#!/usr/bin/env python3
"""Sequential local OpenJarvis scheduler; keeps the existing config.toml."""
from __future__ import annotations

import argparse
import fcntl
import hashlib
import inspect
import json
import os
from pathlib import Path
import signal
import time
from datetime import datetime
from uuid import uuid4


def now():
    return datetime.now().astimezone().isoformat(timespec="seconds")


def digest(data):
    return hashlib.sha256(data).hexdigest()


def save_json(path, value):
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2, default=str) + "\n")
    temp.replace(path)


def load_context(workspace, start_prompt):
    briefing = workspace / "briefing"
    contract_path = briefing / "agent_config.json"
    contract_bytes = contract_path.read_bytes()
    contract = json.loads(contract_bytes)
    parts = [start_prompt.read_text()]
    records = []

    def include(path, scope):
        path = path.resolve()
        if not path.is_relative_to(scope.resolve()):
            raise ValueError(f"Context path outside active directory: {path}")
        if "archive" in path.parts:
            raise ValueError(f"Archive excluded from start context: {path}")
        raw = path.read_bytes()
        if not raw.strip():
            raise ValueError(f"Required context file is empty: {path}")
        records.append({"path": str(path), "sha256": digest(raw), "bytes": len(raw)})
        parts.append(f"\n===== ACTIVE FILE: {path} =====\n{raw.decode('utf-8')}\n===== END FILE =====")

    order = contract["start_context_order"]
    required = set(contract["required_context_files"]) | {
        "MASTER_SYSTEM_PROMPT.md", "00_CONSTITUTION.md", "AGENT_BRIEFING_FULL.md"}
    if not required.issubset(order) or len(order) != len(set(order)):
        raise ValueError("Incomplete or duplicate briefing loading order")
    for name in order:
        include(briefing / name, briefing)
    parts.append("\n===== ACTIVE agent_config.json =====\n" + contract_bytes.decode())
    records.append({"path": str(contract_path), "sha256": digest(contract_bytes), "bytes": len(contract_bytes)})
    log_paths = [(briefing / name).resolve() for name in contract["active_log_files"]]
    if (workspace / "logs/CURRENT_WORK.md").resolve() not in log_paths:
        raise ValueError("CURRENT_WORK missing from active log contract")
    for path in log_paths:
        include(path, workspace / "logs")
    return "\n".join(parts), records, contract


def select_tools(agent_tools, enabled_tools, registry):
    """Merge configured tools and explicitly wire the local execution baseline."""
    excluded = {"retrieval", "memory_store", "memory_search", "memory_index", "memory_retrieve"}
    names = []
    for configured in (agent_tools, enabled_tools):
        values = configured.split(",") if isinstance(configured, str) else (configured or [])
        names.extend(name.strip() for name in values if name.strip() and name.strip() not in excluded)
    names = list(dict.fromkeys(names))
    missing = [name for name in names if not registry.contains(name)]
    if missing:
        raise ValueError(f"Configured tools not registered: {missing}. No tools silently dropped.")
    required = ["file_read", "file_write", "shell_exec"]
    unavailable = [name for name in required if not registry.contains(name)]
    if unavailable:
        raise ValueError(f"Required local tool implementations unavailable: {unavailable}")
    added = []
    for name in required + ["apply_patch", "git_status", "git_diff", "web_search", "web_fetch"]:
        if registry.contains(name) and name not in names:
            names.append(name)
            added.append(name)
    return names, sorted(excluded), added


def prepare_runtime(config_path):
    import openjarvis.agents
    import openjarvis.tools
    from openjarvis.core.config import load_config
    from openjarvis.core.registry import AgentRegistry, ToolRegistry
    cfg = load_config(config_path)
    agent_name = cfg.agent.default_agent
    agent_cls = AgentRegistry.get(agent_name)
    if not getattr(agent_cls, "accepts_tools", False):
        raise ValueError(f"Configured agent {agent_name!r} cannot execute tools")
    model = cfg.intelligence.default_model
    if not model or "cloud" in model.lower():
        raise ValueError("An explicit local model is required in config.toml")
    names, excluded, added = select_tools(cfg.agent.tools, cfg.tools.enabled, ToolRegistry)
    if "web_search" in names:
        # No API-key based auto-selection of a potentially paid search provider.
        os.environ["OPENJARVIS_WEB_SEARCH_ENGINE"] = "duckduckgo"
    print("Werkzeuge: " + ", ".join(names), flush=True)
    print("Vom Scheduler ergänzt: " + (", ".join(added) or "keine"), flush=True)
    cfg.agent.context_from_memory = False
    if hasattr(cfg, "memory_files"):
        cfg.memory_files.soul_path = ""
        cfg.memory_files.memory_path = ""
        cfg.memory_files.user_path = ""
        cfg.memory_files.persona_name = ""
    return cfg, agent_name, model, names, excluded


class RecordingEngine:
    """Record the hash of each actual engine input; never silently truncate it."""
    def __init__(self, engine, run_dir, num_ctx, max_tokens):
        self.engine = engine
        self.run_dir = run_dir
        self.num_ctx = num_ctx
        self.max_tokens = max_tokens
        self.calls = 0

    def __getattr__(self, name):
        return getattr(self.engine, name)

    def generate(self, messages, **kwargs):
        serialized = json.dumps([{"role": str(m.role), "content": m.content} for m in messages], ensure_ascii=False)
        tools = json.dumps(kwargs.get("tools", []), ensure_ascii=False)
        # Conservative planning estimate, not an exact tokenizer measurement.
        estimated = (len(serialized.encode()) + len(tools.encode())) // 2 + self.max_tokens
        if estimated > self.num_ctx:
            raise RuntimeError(f"Context estimate {estimated} exceeds num_ctx={self.num_ctx}; no content was cut. Compact active logs with source pointers or use --num-ctx.")
        self.calls += 1
        with (self.run_dir / "model_calls.jsonl").open("a") as f:
            f.write(json.dumps({"time": now(), "call": self.calls, "messages_sha256": digest(serialized.encode()), "estimated_tokens": estimated, "num_ctx": self.num_ctx}) + "\n")
        print(f"[{now()}] Modellaufruf {self.calls}", flush=True)
        kwargs["num_ctx"] = self.num_ctx
        return self.engine.generate(messages, **kwargs)


def run_cycle(workspace, config_path, start_prompt, num_ctx):
    run_id = datetime.now().astimezone().strftime("%Y%m%dT%H%M%S%z") + "-" + uuid4().hex[:8]
    run_dir = workspace / "logs/runs" / run_id
    run_dir.mkdir(parents=True)
    manifest_path = run_dir / "manifest.json"
    manifest = {"run_id": run_id, "start": now(), "status": "STARTING", "workspace": str(workspace), "config_path": str(config_path)}
    save_json(manifest_path, manifest)
    engine = None
    try:
        body, files, contract = load_context(workspace, start_prompt)
        cfg, agent, model, tools, excluded = prepare_runtime(config_path)
        # Replace historical task/persona prompts only in this in-memory config.
        # Keep generation, tool selection and runtime security settings unchanged.
        cfg.agent.default_system_prompt = (workspace / "briefing/00_CONSTITUTION.md").read_text()
        if hasattr(cfg.agent, "system_prompt"):
            cfg.agent.system_prompt = cfg.agent.default_system_prompt
        if hasattr(cfg.agent, "system_prompt_path"):
            cfg.agent.system_prompt_path = ""
        if hasattr(cfg, "system_prompt"):
            cfg.system_prompt.prefix = ""
        prompt = f"Run-ID: {run_id}\nSystemzeit: {now()}\nWorkspace: {workspace}\nRun-Verzeichnis: {run_dir}\n\n" + body
        (run_dir / "input.md").write_text(prompt)
        manifest.update({"mission_id": contract["mission_id"], "loaded_files": files,
                         "config_sha256": digest(config_path.read_bytes()), "input_sha256": digest(prompt.encode()),
                         "start_prompt_sha256": digest(start_prompt.read_bytes()),
                         "scheduler_sha256": digest(Path(__file__).read_bytes()),
                         "agent": agent, "model": model, "engine": "ollama", "tools": tools,
                         "max_tokens": cfg.intelligence.max_tokens, "max_turns": cfg.agent.max_turns,
                         "temperature": cfg.intelligence.temperature, "num_ctx": num_ctx,
                         "excluded_memory_tools": excluded, "historical_memory_loaded": False})
        save_json(manifest_path, manifest)
        from openjarvis.core.events import EventBus, EventType
        from openjarvis.engine import get_engine
        from openjarvis.security import setup_security
        from openjarvis.cli.ask import _run_agent
        bus = EventBus()

        def trace(event):
            # Do not dump prompts, credentials or raw command arguments.
            record = {"time": now(), "event": event.event_type.value}
            for key in ("tool_name", "success", "duration_seconds", "returncode"):
                if key in event.data:
                    record[key] = event.data[key]
            with (run_dir / "events.jsonl").open("a") as f:
                f.write(json.dumps(record, default=str) + "\n")
            print(f"[{record['time']}] {record['event']} {record.get('tool_name', '')}", flush=True)

        for kind in (EventType.TOOL_CALL_START, EventType.TOOL_CALL_END):
            bus.subscribe(kind, trace)
        resolved = get_engine(cfg, "ollama")
        if resolved is None:
            raise RuntimeError("Configured local Ollama is unavailable; no cloud fallback")
        _, engine = resolved
        sec = setup_security(cfg, engine, bus)
        recorder = RecordingEngine(sec.engine, run_dir, num_ctx, cfg.intelligence.max_tokens)
        kwargs = dict(agent_name=agent, query_text=prompt, engine=recorder, model_name=model,
                      tool_names=tools, config=cfg, bus=bus,
                      temperature=cfg.intelligence.temperature, max_tokens=cfg.intelligence.max_tokens)
        # Retain the existing runtime security policy, also across API versions.
        for key in ("capability_policy", "rate_limiter"):
            if key in inspect.signature(_run_agent).parameters:
                kwargs[key] = getattr(sec, key, None)
        before = digest((workspace / "logs/CURRENT_WORK.md").read_bytes())
        manifest["status"] = "RUNNING"
        save_json(manifest_path, manifest)
        print(f"[{now()}] START {run_id}: {agent}, {model}, max_turns={cfg.agent.max_turns}, max_tokens={cfg.intelligence.max_tokens}", flush=True)
        result = _run_agent(**kwargs)
        (run_dir / "answer.md").write_text(result.content or "")
        save_json(run_dir / "tool_results.json", [
            {"tool_name": r.tool_name, "success": r.success, "content": r.content,
             "metadata": getattr(r, "metadata", {})} for r in result.tool_results])
        successes = sum(bool(r.success) for r in result.tool_results)
        changed = before != digest((workspace / "logs/CURRENT_WORK.md").read_bytes())
        wait = (result.content or "").strip().splitlines()[-1:] == ["SCHEDULER_WAIT"]
        status = "WAITING" if wait else ("CYCLE_RETURNED" if successes and changed else "NO_PROGRESS")
        manifest.update({"status": status, "turns": result.turns, "tool_results": len(result.tool_results),
                         "successful_tools": successes, "current_work_changed": changed,
                         "model_calls": recorder.calls, "agent_metadata": result.metadata,
                         "note": "Tool success and file change are operational signals, not verified research or player value."})
        return status
    except BaseException as exc:
        manifest.update({"status": "INTERRUPTED" if isinstance(exc, (KeyboardInterrupt, SystemExit)) else "FAILED", "error": str(exc)})
        raise
    finally:
        manifest["end"] = now()
        save_json(manifest_path, manifest)
        if engine is not None and hasattr(engine, "close"):
            engine.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", type=Path, default=Path("/home/pagi/breachline-agent"))
    parser.add_argument("--config", type=Path, default=Path("/home/pagi/.openjarvis/config.toml"))
    parser.add_argument("--interval", type=int, default=60, help="Seconds after each completed cycle")
    parser.add_argument("--num-ctx", type=int, default=int(os.environ.get("JARVIS_NUM_CTX", "32768")))
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()
    workspace = args.workspace.expanduser().resolve()
    if args.interval < 1 or args.num_ctx < 1024:
        parser.error("Invalid interval/context window")
    os.chdir(workspace)
    logs = workspace / "logs"
    logs.mkdir(exist_ok=True)
    with (logs / "new_scheduler.lock").open("a") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise SystemExit("The new scheduler is already running")
        def stop(signum, frame):
            raise KeyboardInterrupt
        signal.signal(signal.SIGTERM, stop)
        prompt_path = Path(__file__).with_name("START_PROMPT.md")
        stalls = 0
        while True:
            try:
                status = run_cycle(workspace, args.config.expanduser().resolve(), prompt_path, args.num_ctx)
            except KeyboardInterrupt:
                print("Scheduler stopped.", flush=True)
                return
            except Exception as exc:
                print(f"[{now()}] FAILED: {exc}", flush=True)
                raise SystemExit(1) from exc
            print(f"[{now()}] {status}", flush=True)
            stalls = stalls + 1 if status == "NO_PROGRESS" else 0
            if status == "WAITING" or stalls >= 3:
                print("Scheduler paused: see latest logs/runs manifest and CURRENT_WORK.", flush=True)
                return
            if args.once:
                return
            try:
                time.sleep(args.interval)
            except KeyboardInterrupt:
                print("Scheduler stopped.", flush=True)
                return


if __name__ == "__main__":
    main()
