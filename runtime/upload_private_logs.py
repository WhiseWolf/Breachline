#!/usr/bin/env python3
"""Snapshot ALL logs and runs into the fixed private breachline-logs-only repo.

Python stdlib + git. Does not stop Jarvis or modify original logs/checkouts.
Text is copied in full with recognizable credentials masked; no tail limits.
Snapshots are live, not atomic. Files created after inventory await next upload.
"""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import urllib.error
import urllib.request

NAME = "WhiseWolf/breachline-logs-only"
HTTPS = "https://github.com/" + NAME + ".git"
SSH = "git@github.com:" + NAME + ".git"
MAX_FILE = 95 * 1024 * 1024
SECRET_KEY = re.compile(r"(?i)(?:access[_-]?token|refresh[_-]?token|api[_-]?key|client[_-]?secret|password|passwd|authorization|private[_-]?key|encryption[_-]?key|encrypted[_-]?key)")


def mask(text, known=()):
    for secret in sorted(known, key=len, reverse=True):
        text = text.replace(secret, "[REDACTED]")
    text = re.sub(r"-----BEGIN (?:[A-Z ]*PRIVATE KEY)-----.*?-----END (?:[A-Z ]*PRIVATE KEY)-----", "[REDACTED PRIVATE KEY]", text, flags=re.S)
    text = re.sub(r"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|EA[A-Za-z0-9]{40,}|sk-[A-Za-z0-9_-]{20,}|eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+)\b", "[REDACTED TOKEN]", text)
    text = re.sub(r"(?i)(Bearer\s+|Basic\s+)[A-Za-z0-9+/_.=-]+", r"\1[REDACTED]", text)
    text = re.sub(r"(?i)(https?://)[^\s/@]+:[^\s/@]+@", r"\1[REDACTED]@", text)
    text = re.sub(r'''(?ix)(["']?(?:access[_-]?token|refresh[_-]?token|api[_-]?key|client[_-]?secret|password|passwd|authorization|private[_-]?key|encryption[_-]?key|encrypted[_-]?key)["']?\s*[:=]\s*)(?:"[^"\n]*"|'[^'\n]*'|[^\s,;&}\]\n]+)''', r'\1"[REDACTED]"', text)
    return text


def known_secrets():
    secrets = set()
    def collect(obj):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if SECRET_KEY.search(str(key)) and isinstance(value, str) and len(value) >= 8:
                    secrets.add(value)
                collect(value)
        elif isinstance(obj, list):
            for value in obj:
                collect(value)
    try:
        import tomllib
        collect(tomllib.loads((Path.home() / ".openjarvis/config.toml").read_text()))
    except (ImportError, OSError, ValueError):
        pass
    for key, value in os.environ.items():
        if SECRET_KEY.search(key) or key in {"GH_TOKEN", "GITHUB_TOKEN"}:
            if len(value) >= 8:
                secrets.add(value)
    return secrets


def redact_json(obj, known):
    if isinstance(obj, dict):
        return {key: "[REDACTED]" if SECRET_KEY.search(key) else redact_json(value, known) for key, value in obj.items()}
    if isinstance(obj, list):
        return [redact_json(value, known) for value in obj]
    return mask(obj, known) if isinstance(obj, str) else obj


def copy_logs(source, target):
    known = known_secrets()
    inventory = []
    # No silent exclusions: refuse symlinks/special files rather than omit them.
    for directory, dirs, names in os.walk(source, followlinks=False):
        # git init in logs/ creates administration data, not agent log files.
        dirs[:] = [name for name in dirs if name != ".git"]
        names = [name for name in names if name != ".git"]
        for name in dirs + names:
            path = Path(directory) / name
            if path.is_symlink():
                raise SystemExit("Upload abgebrochen: Symlink im logs-Ordner. Originale unverändert.")
        for name in names:
            path = Path(directory) / name
            if not path.is_file():
                raise SystemExit("Upload abgebrochen: Spezialdatei im logs-Ordner.")
            inventory.append(path)
    manifest = []
    for path in sorted(inventory):
        relative = path.relative_to(source)
        destination = target / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        before = path.stat()
        if before.st_size > MAX_FILE:
            raise SystemExit("Upload abgebrochen: Einzeldatei über 95 MiB; nichts gekürzt oder hochgeladen.")
        with path.open("rb") as stream:
            raw = stream.read(MAX_FILE + 1)
        if len(raw) > MAX_FILE:
            raise SystemExit("Upload abgebrochen: Datei während Kopie über 95 MiB gewachsen.")
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            raise SystemExit("Upload abgebrochen: Nicht-UTF-8-Datei in logs; sichere Maskierung nicht möglich. Nichts hochgeladen.")
        if path.suffix == ".json":
            try:
                cleaned = json.dumps(redact_json(json.loads(text), known), ensure_ascii=False, indent=2) + "\n"
            except ValueError:
                cleaned = mask(text, known)
        else:
            cleaned = mask(text, known)
        encoded = cleaned.encode("utf-8")
        if len(encoded) > MAX_FILE:
            raise SystemExit("Upload abgebrochen: Aufbereitete Datei über 95 MiB.")
        destination.write_bytes(encoded)
        after = path.stat()
        manifest.append({"path": str(relative), "source_bytes_read": len(raw), "uploaded_bytes": len(encoded),
                         "source_mtime_utc": datetime.fromtimestamp(before.st_mtime, timezone.utc).isoformat(),
                         "changed_during_copy": (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns),
                         "credential_masking_changed_content": cleaned != text})
    if not manifest:
        raise SystemExit("Keine Log-Dateien gefunden; nichts hochgeladen.")
    return manifest


def ensure_not_public():
    # The repo was verified private when provisioning. Recheck anonymously:
    # public repos return 200, private/nonexistent repos return 404. A missing
    # repo cannot pass the subsequent authenticated git push.
    request = urllib.request.Request("https://api.github.com/repos/" + NAME,
                                     headers={"User-Agent": "Breachline-Log-Snapshot", "Accept": "application/vnd.github+json"})
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            data = json.load(response)
        if data.get("private") is not True:
            raise SystemExit("Upload abgebrochen: Ziel-Repository ist öffentlich.")
    except urllib.error.HTTPError as error:
        if error.code != 404:
            raise SystemExit("Upload abgebrochen: Repository-Sichtbarkeit konnte nicht geprüft werden.")
    except (OSError, ValueError):
        raise SystemExit("Upload abgebrochen: Repository-Sichtbarkeit konnte nicht geprüft werden.")


def run_git(args, cwd):
    try:
        result = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, timeout=300)
    except (OSError, subprocess.TimeoutExpired):
        raise SystemExit("Git-Schritt nicht abgeschlossen: " + args[0] + ". Lokale Kopie bleibt erhalten.")
    if result.returncode:
        raise SystemExit("Git-Schritt fehlgeschlagen: " + args[0] + ". GitHub-Zugang prüfen. Lokale Kopie bleibt erhalten.")
    return result.stdout.strip()


def transport(root):
    # Reuse the working SSH transport of the existing game checkout, but always
    # substitute our fixed private destination, never an arbitrary origin.
    allowed = {"git@github.com:WhiseWolf/Breachline.git", "ssh://git@github.com/WhiseWolf/Breachline.git", SSH}
    for checkout in (root / "repo", root):
        try:
            result = subprocess.run(["git", "remote", "get-url", "origin"], cwd=checkout,
                                    capture_output=True, text=True, timeout=10)
            if result.returncode == 0 and result.stdout.strip() in allowed:
                return SSH
        except (OSError, subprocess.TimeoutExpired):
            pass
    return HTTPS


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, default=Path.home() / "breachline-agent")
    parser.add_argument("--push", action="store_true", help="Upload all prepared logs to the fixed private repository")
    args = parser.parse_args()
    root = args.workspace.expanduser().resolve()
    source = root / "logs"
    if not source.is_dir() or source.is_symlink():
        parser.error("Projekt braucht einen echten logs-Ordner.")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + os.urandom(3).hex()
    output = root / "diagnostics" / ("full-logs-" + stamp)
    output.mkdir(parents=True, mode=0o700)
    files = copy_logs(source, output / "logs")
    metadata = {"created_utc": datetime.now(timezone.utc).isoformat(), "files": files,
                "scope": "All regular UTF-8 files inventoried under logs, recursively including ALL runs. No truncation, no run limit.",
                "limitations": "Live non-atomic snapshot. Automatic credential masking cannot detect every arbitrary secret. Original local logs unchanged."}
    (output / "SNAPSHOT.json").write_text(json.dumps(metadata, indent=2) + "\n")
    size = sum(f["uploaded_bytes"] for f in files)
    (output / "README.md").write_text("# Vollständiger Jarvis Log-Snapshot\n\n" + metadata["scope"] + "\n\n" + metadata["limitations"] + f"\n\nDateien: {len(files)}; Bytes: {size}. Details: SNAPSHOT.json.\n")
    print(f"Vorbereitet: {len(files)} Dateien, {size / 1024 / 1024:.1f} MiB. Kein Run-Limit, keine Kürzung.")
    print("Lokale Kopie: " + str(output))
    if not args.push:
        print("Für Upload erneut mit --push ausführen.")
        return
    ensure_not_public()
    branch = "snapshots/" + stamp
    with tempfile.TemporaryDirectory(prefix="private-jarvis-logs-") as tmp:
        work = Path(tmp)
        run_git(["init", "-q"], work)
        run_git(["checkout", "-q", "-b", branch], work)
        run_git(["remote", "add", "origin", transport(root)], work)
        shutil.copytree(output, work, dirs_exist_ok=True)
        run_git(["add", "--", "logs", "README.md", "SNAPSHOT.json"], work)
        run_git(["-c", "user.name=Jarvis Log Snapshot", "-c", "user.email=logs@localhost", "-c", "commit.gpgsign=false", "commit", "-q", "-m", "Upload complete masked Jarvis logs and runs"], work)
        # Recheck directly before push; no force push and no main modifications.
        ensure_not_public()
        run_git(["push", "origin", "HEAD:refs/heads/" + branch], work)
    print("Hochgeladen: https://github.com/" + NAME + "/tree/" + branch + "/logs")
    print("Snapshot-Branch: " + branch)


if __name__ == "__main__":
    main()
