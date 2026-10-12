#!/usr/bin/env python3
"""Read-only Jarvis snapshot; optional isolated upload of metadata, never raw logs.

python3 jarvis_diagnostics.py --push
Requires only Python stdlib; git and existing GitHub credentials for --push.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile

REPOSITORY = "https://github.com/WhiseWolf/Breachline.git"
MAX_READ = 4 * 1024 * 1024
TOOLS = set("file_read file_write apply_patch shell_exec git_status git_diff git_log git_commit web_search web_fetch http_request think calculator code_interpreter code_interpreter_docker docker_shell_exec memory_search memory_store".split())
LABELS = set("STARTING RUNNING FAILED INTERRUPTED WAITING NO_PROGRESS CYCLE_RETURNED SUCCEEDED PENDING NOT_EXECUTED RETURNED TOOL_CALL_START TOOL_CALL_END tool_call_start tool_call_end CHECKPOINT_SAVED CONTEXT_ROLL CONTEXT_GROW INFERENCE_RETRY".split())
SKIP = {".git", ".venv", "venv", "node_modules", "__pycache__", "archive", "diagnostics"}


def scalar(key, value):
    if isinstance(value, (bool, int, float)) or value is None:
        return value
    if not isinstance(value, str):
        return None
    if key in {"time", "start", "end"}:
        return value if re.fullmatch(r"[0-9T:.+Z -]{10,40}", value) else None
    if key in {"tool", "tool_name"}:
        return value if value in TOOLS else "OTHER_TOOL"
    return value if value in LABELS else "OTHER"


def select(obj, keys):
    return {k: scalar(k, obj[k]) for k in keys if k in obj}


def text_tail(path):
    # Read from EOF so a large live log cannot consume unlimited memory.
    with path.open("rb") as stream:
        stream.seek(max(0, path.stat().st_size - MAX_READ))
        return stream.read(MAX_READ).decode("utf-8", errors="replace")


def objects(path):
    try:
        data = text_tail(path)
        if path.suffix == ".jsonl":
            rows = []
            for line in data.splitlines():
                try:
                    row = json.loads(line)
                    if isinstance(row, dict):
                        rows.append(row)
                except ValueError:
                    pass  # A live writer can leave an incomplete final line.
            return rows
        obj = json.loads(data)
        return obj if isinstance(obj, list) else [obj] if isinstance(obj, dict) else []
    except (OSError, ValueError):
        return []


def metadata(path, root):
    st = path.stat()
    return {"path": str(path.relative_to(root)), "bytes": st.st_size,
            "mtime_utc": datetime.fromtimestamp(st.st_mtime, timezone.utc).isoformat()}


def inventory(root):
    items = []
    for directory, dirs, names in os.walk(root, followlinks=False):
        dirs[:] = [d for d in dirs if d not in SKIP and not (Path(directory) / d).is_symlink()]
        for name in names:
            p = Path(directory) / name
            if p.is_symlink() or p.suffix.lower() not in {".html", ".js", ".ts", ".css", ".py", ".md"}:
                continue
            if "logs" in p.relative_to(root).parts or name.startswith("."):
                continue
            try:
                items.append(metadata(p, root))
            except OSError:
                continue
        if len(items) > 10000:
            break
    return sorted(items, key=lambda v: v["mtime_utc"], reverse=True)[:200]


def snapshot(root, limit):
    report = {"created_utc": datetime.now(timezone.utc).isoformat(),
              "scope": "Metadata snapshot; not proof of completed game work. No raw log contents, prompts, tool arguments/results, credentials, config or environment copied.",
              "limits": "Live files may change during reading; JSONL summaries cover at most the last 4 MiB. Missing or incomplete JSON is skipped.",
              "active_log_files": [], "recent_project_files": inventory(root), "runs": []}
    logs = root / "logs"
    if not logs.is_dir():
        raise SystemExit("Kein logs-Ordner im angegebenen Projekt gefunden.")
    for p in sorted(logs.iterdir()):
        if p.is_symlink() or not p.is_file() or p.suffix not in {".md", ".log"}:
            continue
        try:
            item = metadata(p, root)
            raw = text_tail(p)
            item["scheduler_checkpoint_mentions_in_tail"] = raw.count("SCHEDULER CHECKPOINT")
            item["empty_status_marker_in_tail"] = "Status: EMPTY" in raw
            report["active_log_files"].append(item)
        except OSError:
            pass
    runs = logs / "runs"
    folders = []
    if runs.is_dir():
        for p in runs.iterdir():
            if p.is_dir() and not p.is_symlink():
                try:
                    folders.append((p.stat().st_mtime, p))
                except OSError:
                    pass
    for _, folder in sorted(folders, reverse=True)[:limit]:
        item = {"run": folder.name, "files": [], "manifest": {}}
        for p in sorted(folder.iterdir()):
            if p.is_symlink() or not p.is_file():
                continue
            try:
                item["files"].append(metadata(p, root))
            except OSError:
                pass
        for obj in objects(folder / "manifest.json"):
            item["manifest"] = select(obj, ("status", "start", "end", "turns", "model_calls", "num_ctx", "successful_tools", "evidence_tools", "current_work_changed", "inference_retries"))
        events = objects(folder / "events.jsonl")
        item["event_counts_in_tail"] = dict(Counter(str(scalar("event", o.get("event"))) for o in events))
        item["recent_events"] = [select(o, ("time", "event", "tool_name", "success", "duration_seconds", "returncode")) for o in events[-40:]]
        item["recent_model_calls"] = [select(o, ("time", "call", "status", "attempt", "estimated_tokens", "num_ctx", "outputs_compacted")) for o in objects(folder / "model_calls.jsonl")[-20:]]
        item["recent_recovery"] = [select(o, ("time", "action", "num_ctx", "estimate", "retained_messages", "attempt", "delay_seconds")) for o in objects(folder / "recovery.jsonl")[-20:]]
        receipts = objects(folder / "action_receipts.json")
        item["action_status_counts"] = dict(Counter(str(scalar("status", o.get("status"))) for o in receipts if isinstance(o, dict)))
        item["recent_actions"] = [select(o, ("tool", "status", "potential_write")) for o in receipts[-40:] if isinstance(o, dict)]
        # Classify error types locally without exporting any free-form error text.
        categories = Counter()
        for p in folder.iterdir():
            if p.is_symlink() or not p.is_file() or p.suffix not in {".json", ".jsonl", ".txt", ".md"}:
                continue
            try:
                raw = text_tail(p)
                for marker in ("FileNotFoundError", "PermissionError", "ContextBudgetError", "UnsafeRecoveryError", "context overflow", "ConnectionError", "docker not available"):
                    count = raw.count(marker)
                    if count:
                        categories[marker] += count
            except OSError:
                pass
        item["error_marker_occurrences_not_unique_failures"] = dict(categories)
        report["runs"].append(item)
    return report


def summary(report):
    lines = ["# Jarvis Diagnose", "", "Zeit: " + report["created_utc"], "", report["scope"], "", report["limits"], "", "## Aktive Log-Dateien", ""]
    for o in report["active_log_files"]:
        lines.append(f'- {o["path"]}: {o["mtime_utc"]}, {o["bytes"]} Bytes, EMPTY={o["empty_status_marker_in_tail"]}, Checkpoint-Erwähnungen={o["scheduler_checkpoint_mentions_in_tail"]}')
    for run in report["runs"]:
        lines += ["", "## Lauf " + run["run"], "", "Manifest: " + json.dumps(run["manifest"]), "", "Aktionsstatus: " + json.dumps(run["action_status_counts"]), "", "Fehlermarker: " + json.dumps(run["error_marker_occurrences_not_unique_failures"])]
        calls = run["recent_model_calls"]
        if calls:
            lines += ["", "Letzter Modell-Eintrag: " + json.dumps(calls[-1])]
        lines += ["", "Letzte Tool-Ereignisse:", "", "```json", json.dumps(run["recent_events"][-10:], indent=2), "```"]
    lines += ["", "## Zuletzt geänderte Projektdateien", ""]
    for o in report["recent_project_files"][:40]:
        lines.append(f'- {o["mtime_utc"]} {o["path"]} ({o["bytes"]} Bytes)')
    return "\n".join(lines) + "\n"


def git(args, cwd):
    result = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, timeout=120)
    if result.returncode:
        # Git error output can include credential-bearing URLs; never echo it.
        raise SystemExit("Git-Schritt fehlgeschlagen: " + args[0] + ". Bestehenden GitHub-Zugang prüfen; lokaler Bericht bleibt erhalten.")
    return result.stdout.strip()


def upload(output, stamp, repository=REPOSITORY):
    branch = "diagnostics/jarvis-" + stamp
    with tempfile.TemporaryDirectory(prefix="jarvis-diagnostic-upload-") as tmp:
        work = Path(tmp)
        git(["init", "-q"], work)
        git(["checkout", "-q", "-b", branch], work)
        git(["remote", "add", "origin", repository], work)
        for name in ("report.json", "SUMMARY.md"):
            (work / name).write_bytes((output / name).read_bytes())
        git(["add", "--", "report.json", "SUMMARY.md"], work)
        git(["-c", "user.name=Jarvis Diagnostics", "-c", "user.email=diagnostics@localhost", "-c", "commit.gpgsign=false", "commit", "-q", "-m", "Add metadata-only Jarvis diagnostic snapshot"], work)
        git(["push", "origin", "HEAD:refs/heads/" + branch], work)
    print("Hochgeladen: https://github.com/WhiseWolf/Breachline/blob/" + branch + "/SUMMARY.md")
    print("Diagnose-Branch: " + branch)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, default=Path.home() / "breachline-agent")
    parser.add_argument("--runs", type=int, default=5)
    parser.add_argument("--push", action="store_true", help="Upload ONLY generated metadata report on a new isolated GitHub branch")
    args = parser.parse_args()
    root = args.workspace.expanduser().resolve()
    if not root.is_dir() or not 1 <= args.runs <= 20:
        parser.error("Workspace muss existieren; --runs muss zwischen 1 und 20 liegen.")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + os.urandom(3).hex()
    output = root / "diagnostics" / stamp
    report = snapshot(root, args.runs)
    output.mkdir(parents=True, mode=0o700)
    (output / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    (output / "SUMMARY.md").write_text(summary(report))
    print(summary(report))
    print("Lokaler Bericht: " + str(output / "SUMMARY.md"))
    if args.push:
        repository = REPOSITORY
        # Reuse an existing SSH remote only when it is exactly this repository.
        for checkout in (root / "repo", root):
            try:
                remote = subprocess.run(["git", "remote", "get-url", "origin"], cwd=checkout, capture_output=True, text=True, timeout=10)
                if remote.returncode == 0 and remote.stdout.strip() in {
                    REPOSITORY, "git@github.com:WhiseWolf/Breachline.git",
                    "ssh://git@github.com/WhiseWolf/Breachline.git"}:
                    repository = remote.stdout.strip()
                    break
            except (OSError, subprocess.TimeoutExpired):
                pass
        upload(output, stamp, repository)


if __name__ == "__main__":
    main()
