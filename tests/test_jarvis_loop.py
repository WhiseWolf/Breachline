import importlib.util
import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

spec = importlib.util.spec_from_file_location("jarvis_loop", Path(__file__).parents[1] / "runtime/jarvis_loop.py")
loop = importlib.util.module_from_spec(spec)
spec.loader.exec_module(loop)


class ContextTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "briefing").mkdir()
        (self.root / "logs").mkdir()
        self.prompt = self.root / "start.md"
        self.prompt.write_text("EXECUTE")
        self.contract = {"required_context_files": ["00_CONSTITUTION.md"],
                         "start_context_order": ["MASTER_SYSTEM_PROMPT.md", "00_CONSTITUTION.md", "AGENT_BRIEFING_FULL.md"],
                         "active_log_files": ["../logs/CURRENT_WORK.md"], "mission_id": "fresh"}
        for name in self.contract["start_context_order"]:
            (self.root / "briefing" / name).write_text("RULE " + name)
        (self.root / "logs/CURRENT_WORK.md").write_text("NOT_STARTED")
        self.write_contract()

    def write_contract(self):
        (self.root / "briefing/agent_config.json").write_text(json.dumps(self.contract))

    def test_second_cycle_reloads_handoff_and_briefing(self):
        first, records, _ = loop.load_context(self.root, self.prompt)
        (self.root / "logs/CURRENT_WORK.md").write_text("CONTINUE: inspect actual evidence")
        (self.root / "briefing/MASTER_SYSTEM_PROMPT.md").write_text("UPDATED ENTRY")
        second, records2, _ = loop.load_context(self.root, self.prompt)
        self.assertIn("NOT_STARTED", first)
        self.assertNotIn("NOT_STARTED", second)
        self.assertIn("CONTINUE: inspect actual evidence", second)
        self.assertIn("UPDATED ENTRY", second)
        self.assertNotEqual(records[0]["sha256"], records2[0]["sha256"])

    def test_no_archive_or_repo_log_in_context(self):
        (self.root / "logs/archive").mkdir()
        (self.root / "logs/archive/old.md").write_text("OLD MISSION")
        (self.root / "repo/logs").mkdir(parents=True)
        (self.root / "repo/logs/CURRENT_WORK.md").write_text("OLD TASK")
        body, _, _ = loop.load_context(self.root, self.prompt)
        self.assertNotIn("OLD MISSION", body)
        self.assertNotIn("OLD TASK", body)
        for bad in ("../logs/archive/old.md", "../repo/logs/CURRENT_WORK.md"):
            self.contract["active_log_files"].append(bad)
            self.write_contract()
            with self.assertRaises(ValueError):
                loop.load_context(self.root, self.prompt)
            self.contract["active_log_files"].pop()

    def test_missing_required_rule_fails_before_inference(self):
        (self.root / "briefing/00_CONSTITUTION.md").unlink()
        with self.assertRaises(FileNotFoundError):
            loop.load_context(self.root, self.prompt)

    def test_symlink_escape_is_rejected(self):
        outside = self.root / "outside.md"
        outside.write_text("WRONG CONTEXT")
        target = self.root / "briefing/00_CONSTITUTION.md"
        target.unlink()
        target.symlink_to(outside)
        with self.assertRaises(ValueError):
            loop.load_context(self.root, self.prompt)

    def test_incomplete_order_is_rejected(self):
        self.contract["start_context_order"].remove("00_CONSTITUTION.md")
        self.write_contract()
        with self.assertRaises(ValueError):
            loop.load_context(self.root, self.prompt)

    def test_exact_engine_input_is_forwarded_and_hashed(self):
        received = []
        engine = SimpleNamespace(generate=lambda messages, **kwargs: received.append((messages, kwargs)) or {"content": "ok"})
        recorder = loop.RecordingEngine(engine, self.root, 32768, 2048)
        messages = [SimpleNamespace(role="user", content="Real current task")]
        recorder.generate(messages, model="local")
        self.assertIs(received[0][0], messages)
        self.assertEqual(received[0][1]["num_ctx"], 32768)
        self.assertEqual(recorder.calls, 1)
        self.assertIn("messages_sha256", (self.root / "model_calls.jsonl").read_text())

    def test_oversized_context_never_reaches_engine(self):
        engine = SimpleNamespace(generate=lambda *a, **k: self.fail("Oversized context sent"))
        recorder = loop.RecordingEngine(engine, self.root, 1024, 256)
        with self.assertRaises(RuntimeError):
            recorder.generate([SimpleNamespace(role="user", content="X" * 6000)])
        self.assertEqual(recorder.calls, 0)

    def test_long_tool_output_is_archived_without_losing_rules_or_protocol(self):
        received = []
        engine = SimpleNamespace(generate=lambda messages, **kwargs: received.append(messages) or {"content": "ok"})
        recorder = loop.RecordingEngine(engine, self.root, 4000, 256)
        rules = SimpleNamespace(role="system", content="IMMUTABLE RULES")
        task = SimpleNamespace(role="user", content="ACTIVE TASK")
        tool = SimpleNamespace(role="tool", content="START " + "X" * 20000 + " END", tool_call_id="call_42")
        recorder.generate([rules, task, tool], model="local")
        result = received[0]
        self.assertIs(result[0], rules)
        self.assertIs(result[1], task)
        self.assertEqual(result[2].tool_call_id, "call_42")
        self.assertIn("CONTEXT COMPACTED", result[2].content)
        self.assertEqual(len(tool.content), 20010)
        artifacts = list(self.root.glob("message-*.txt"))
        self.assertEqual(artifacts[0].read_text(), tool.content)

    def test_initial_briefing_is_not_compacted_even_if_long(self):
        recorder = loop.RecordingEngine(SimpleNamespace(), self.root, 32768, 2048)
        rules = SimpleNamespace(role="system", content="C" * 5000)
        task = SimpleNamespace(role="user", content="BRIEFING " * 1000)
        self.assertIs(recorder.compact_outputs([rules, task], 128)[0], rules)
        self.assertEqual(recorder.compact_outputs([rules, task], 128)[1].content, task.content)


class ToolSelectionTests(unittest.TestCase):
    def registry(self, *extra):
        available = {"file_read", "file_write", "shell_exec", *extra}
        return SimpleNamespace(contains=lambda name: name in available)

    def test_missing_configured_shell_is_added_and_lists_are_merged(self):
        names, _, added = loop.select_tools("file_read,apply_patch", "file_write,git_diff", self.registry("apply_patch", "git_diff"))
        self.assertEqual(set(names), {"file_read", "file_write", "shell_exec", "apply_patch", "git_diff"})
        self.assertIn("shell_exec", added)
        self.assertEqual(len(names), len(set(names)))

    def test_empty_config_still_wires_execution_baseline(self):
        names, _, _ = loop.select_tools("", "", self.registry())
        self.assertEqual(names, ["file_read", "file_write", "shell_exec"])

    def test_unknown_implementation_fails_explicitly(self):
        with self.assertRaisesRegex(ValueError, "not registered"):
            loop.select_tools("imaginary_tool", "", self.registry())
        with self.assertRaisesRegex(ValueError, "implementations unavailable"):
            loop.select_tools("", "", SimpleNamespace(contains=lambda n: n != "shell_exec"))

    def test_history_tools_are_excluded_and_optional_tools_checked(self):
        names, excluded, _ = loop.select_tools("memory_search,file_read", "file_read", self.registry("web_search"))
        self.assertNotIn("memory_search", names)
        self.assertIn("memory_search", excluded)
        self.assertIn("web_search", names)
        self.assertNotIn("web_fetch", names)


class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.messages = [SimpleNamespace(role="user", content="Protected rules and active handoff")]

    def test_transient_inference_retry_preserves_history_and_does_not_repeat_write(self):
        ledger = loop.ActionLedger(self.root)
        ledger.record("tool_call_start", {"tool": "file_write"})
        ledger.record("tool_call_end", {"tool": "file_write", "success": True})
        original_receipts = ledger.path.read_text()
        engine = SimpleNamespace(generate=Mock(side_effect=[TimeoutError("slow"), {"content": "continue"}]))
        sleep = Mock()
        policy = loop.RecoveryPolicy(32768, retries=2, sleep=sleep)
        recorder = loop.RecordingEngine(engine, self.root, 32768, 2048, policy, ledger)
        self.assertEqual(recorder.generate(self.messages)["content"], "continue")
        self.assertEqual(engine.generate.call_count, 2)
        self.assertIs(engine.generate.call_args_list[0].args[0], self.messages)
        self.assertIs(engine.generate.call_args_list[1].args[0], self.messages)
        self.assertEqual(ledger.path.read_text(), original_receipts)
        sleep.assert_called_once_with(10)

    def test_retry_budget_and_unknown_failures_stop(self):
        engine = SimpleNamespace(generate=Mock(side_effect=TimeoutError("offline")))
        sleep = Mock()
        policy = loop.RecoveryPolicy(32768, retries=2, sleep=sleep)
        recorder = loop.RecordingEngine(engine, self.root, 32768, 2048, policy)
        with self.assertRaises(TimeoutError):
            recorder.generate(self.messages)
        self.assertEqual(engine.generate.call_count, 3)
        self.assertEqual([c.args[0] for c in sleep.call_args_list], [10, 30])
        engine.generate = Mock(side_effect=PermissionError("policy denied"))
        with self.assertRaises(PermissionError):
            recorder.generate(self.messages)
        self.assertEqual(engine.generate.call_count, 1)
        self.assertFalse(loop.transient_error(RuntimeError("Ollama returned 400: bad config")))
        self.assertTrue(loop.transient_error(RuntimeError("Ollama returned 503: busy")))

    def test_cycle_retry_budget_is_bounded_even_across_model_calls(self):
        policy = loop.RecoveryPolicy(32768, retries=2, sleep=Mock())
        policy.retries_used = 6
        engine = SimpleNamespace(generate=Mock(side_effect=TimeoutError("offline")))
        recorder = loop.RecordingEngine(engine, self.root, 32768, 2048, policy)
        with self.assertRaises(TimeoutError):
            recorder.generate(self.messages)
        self.assertEqual(engine.generate.call_count, 1)

    def test_context_grows_in_place_to_ceiling_and_keeps_all_rules(self):
        engine = SimpleNamespace(generate=Mock(return_value={"content": "ok"}))
        policy = loop.RecoveryPolicy(32768, 49152, sleep=Mock())
        recorder = loop.RecordingEngine(engine, self.root, 32768, 2048, policy)
        messages = [SimpleNamespace(role="user", content="RULE" * 17000)]
        recorder.generate(messages)
        self.assertEqual(policy.num_ctx, 40960)
        self.assertIs(engine.generate.call_args.args[0], messages)
        self.assertEqual(engine.generate.call_args.kwargs["num_ctx"], 40960)
        recorder.generate([SimpleNamespace(role="user", content="RULE" * 21000)])
        self.assertEqual(policy.num_ctx, 49152)
        calls = engine.generate.call_count
        with self.assertRaises(loop.ContextBudgetError):
            recorder.generate([SimpleNamespace(role="user", content="RULE" * 30000)])
        self.assertEqual(engine.generate.call_count, calls)

    def test_pending_or_failed_write_blocks_inference_and_restart(self):
        run_dir = self.root / "runs/20261011-run"
        run_dir.mkdir(parents=True)
        ledger = loop.ActionLedger(run_dir)
        engine = SimpleNamespace(generate=Mock())
        recorder = loop.RecordingEngine(engine, run_dir, 32768, 2048, ledger=ledger)
        ledger.record("tool_call_start", {"tool": "shell_exec"})
        loop.save_json(run_dir / "manifest.json", {"status": "RUNNING"})
        with self.assertRaises(loop.UnsafeRecoveryError):
            recorder.generate(self.messages)
        with self.assertRaises(loop.UnsafeRecoveryError):
            loop.check_previous_run(self.root)
        ledger.record("tool_call_end", {"tool": "shell_exec", "success": False})
        with self.assertRaises(loop.UnsafeRecoveryError):
            recorder.generate(self.messages)
        engine.generate.assert_not_called()

    def test_failed_read_does_not_block_alternative_research(self):
        ledger = loop.ActionLedger(self.root)
        ledger.record("tool_call_start", {"tool": "web_search"})
        ledger.record("tool_call_end", {"tool": "web_search", "success": False})
        ledger.check()
        ledger.record("tool_call_start", {"tool": "http_request", "arguments": {"method": "GET"}})
        ledger.record("tool_call_end", {"tool": "http_request", "success": False})
        ledger.check()
        self.assertTrue(loop.potential_write("http_request", {"arguments": {"method": "POST"}}))
        self.assertTrue(loop.potential_write("http_request", {"arguments": "broken JSON"}))

    def test_completed_writes_are_not_replayed_on_restart(self):
        run_dir = self.root / "runs/20261011-run"
        run_dir.mkdir(parents=True)
        ledger = loop.ActionLedger(run_dir)
        ledger.record("tool_call_start", {"tool": "git_commit"})
        ledger.record("tool_call_end", {"tool": "git_commit", "success": True})
        loop.save_json(run_dir / "manifest.json", {"status": "FAILED"})
        loop.check_previous_run(self.root)
        self.assertEqual(len(ledger.actions), 1)

    def test_keyboard_interrupt_never_retries(self):
        policy = loop.RecoveryPolicy(32768, sleep=Mock())
        engine = SimpleNamespace(generate=Mock(side_effect=KeyboardInterrupt))
        recorder = loop.RecordingEngine(engine, self.root, 32768, 2048, policy)
        with self.assertRaises(KeyboardInterrupt):
            recorder.generate(self.messages)
        policy.sleep.assert_not_called()

    def test_continuity_notice_uses_only_same_mission_runtime_evidence(self):
        run_dir = self.root / "runs/20261011-run"
        run_dir.mkdir(parents=True)
        loop.save_json(run_dir / "manifest.json", {"status": "FAILED", "mission_id": "fresh"})
        notice = loop.previous_run_notice(self.root, "fresh")
        self.assertIn("verify its actual outcome", notice)
        self.assertIn(str(run_dir), notice)
        self.assertEqual(loop.previous_run_notice(self.root, "other"), "")

    def legacy_run(self, docker_result, shell_result=True, shell_end=True):
        run = self.root / "runs/20261011-legacy"
        run.mkdir(parents=True)
        loop.save_json(run / "manifest.json", {"status": "INTERRUPTED"})
        (run / "docker.txt").write_text(docker_result)
        (run / "shell.txt").write_text("Exit code: 0\nstdout: 2026-10-11T07:34:36+00:00")
        events = [
            {"event": "tool_call_start", "tool_name": "code_interpreter_docker"},
            {"event": "tool_call_end", "tool_name": "code_interpreter_docker", "success": False, "result_path": str(run / "docker.txt")},
            {"event": "tool_call_start", "tool_name": "shell_exec"}]
        if shell_end:
            events.append({"event": "tool_call_end", "tool_name": "shell_exec", "success": shell_result, "result_path": str(run / "shell.txt")})
        (run / "events.jsonl").write_text("\n".join(json.dumps(e) for e in events))
        return run

    def test_legacy_completed_shell_and_proven_preexecution_docker_failure_resume(self):
        error = "Docker execution error (DockerException): Error while fetching server API version: ('Connection aborted.', FileNotFoundError(2, 'No such file or directory'))"
        run = self.legacy_run(error)
        loop.check_previous_run(self.root)
        review = json.loads((run / "legacy_action_review.json").read_text())
        self.assertEqual([a["status"] for a in review["actions"]], ["NOT_EXECUTED", "SUCCEEDED"])
        self.assertEqual(json.loads((run / "manifest.json").read_text())["status"], "INTERRUPTED")

    def test_legacy_pending_shell_and_ambiguous_docker_failure_still_block(self):
        self.legacy_run("Execution timed out after 30 seconds.", shell_end=False)
        with self.assertRaises(loop.UnsafeRecoveryError):
            loop.check_previous_run(self.root)

    def test_live_preexecution_docker_failure_allows_free_alternative(self):
        ledger = loop.ActionLedger(self.root)
        ledger.record("tool_call_start", {"tool": "code_interpreter_docker"})
        ledger.record("tool_call_end", {"tool": "code_interpreter_docker", "success": False,
                                      "result": "Docker execution error (DockerException): Error while fetching server API version: FileNotFoundError(2, 'No such file or directory')"})
        ledger.check()
        self.assertEqual(ledger.actions[-1]["status"], "NOT_EXECUTED")
        self.assertFalse(loop.failed_before_execution("shell_exec", "FileNotFoundError(2, 'No such file or directory')"))


class CycleIntegrationTests(unittest.TestCase):
    setUp = ContextTests.setUp
    write_contract = ContextTests.write_contract

    def test_two_cycles_reload_handoff_and_retry_model_without_replaying_actions(self):
        config = self.root / "config.toml"
        config.write_text("existing configuration")
        cfg = SimpleNamespace(agent=SimpleNamespace(max_turns=60),
                              intelligence=SimpleNamespace(max_tokens=2048, temperature=0.3))
        outputs = [{"content": "first"}, TimeoutError("temporary"), {"content": "done"},
                   {"content": "second"}, {"content": "done"}]
        engine = SimpleNamespace(generate=Mock(side_effect=outputs), close=Mock())
        observed = []
        writes = []

        class Bus:
            def __init__(self):
                self.callbacks = {}

            def subscribe(self, kind, callback):
                self.callbacks[kind.value] = callback

            def emit(self, kind, **data):
                self.callbacks[kind](SimpleNamespace(event_type=SimpleNamespace(value=kind), data=data))

        def agent(**kwargs):
            observed.append(kwargs["query_text"])
            messages = [SimpleNamespace(role="user", content=kwargs["query_text"])]
            kwargs["engine"].generate(messages)
            bus = kwargs["bus"]
            bus.emit("tool_call_start", tool="web_search")
            bus.emit("tool_call_end", tool="web_search", success=True, result="mock source")
            bus.emit("tool_call_start", tool="file_write")
            handoff = "CONTINUE " + str(len(observed))
            (self.root / "logs/CURRENT_WORK.md").write_text(handoff)
            writes.append(handoff)
            bus.emit("tool_call_end", tool="file_write", success=True, result="saved")
            kwargs["engine"].generate(messages)
            return SimpleNamespace(content="done", turns=2, metadata={}, tool_results=[
                SimpleNamespace(tool_name="web_search", success=True, content="mock source"),
                SimpleNamespace(tool_name="file_write", success=True, content="saved")])

        modules = {
            "openjarvis.core.events": SimpleNamespace(EventBus=Bus, EventType=SimpleNamespace(
                TOOL_CALL_START=SimpleNamespace(value="tool_call_start"),
                TOOL_CALL_END=SimpleNamespace(value="tool_call_end"))),
            "openjarvis.engine": SimpleNamespace(get_engine=lambda *a: ("ollama", engine)),
            "openjarvis.security": SimpleNamespace(setup_security=lambda *a: SimpleNamespace(engine=engine)),
            "openjarvis.cli.ask": SimpleNamespace(_run_agent=agent),
        }
        policy = loop.RecoveryPolicy(32768, sleep=Mock())
        with patch.dict(sys.modules, modules), patch.object(loop, "prepare_runtime", return_value=(
                cfg, "operative", "local", ["file_read", "file_write", "web_search"], [])):
            first = loop.run_cycle(self.root, config, self.prompt, policy.num_ctx, policy)
            second = loop.run_cycle(self.root, config, self.prompt, policy.num_ctx, policy)
        self.assertEqual((first, second), ("CYCLE_RETURNED", "CYCLE_RETURNED"))
        self.assertEqual(writes, ["CONTINUE 1", "CONTINUE 2"])
        self.assertIn("CONTINUE 1", observed[1])
        self.assertNotIn("NOT_STARTED\n===== END FILE", observed[1])
        self.assertEqual(engine.generate.call_count, 5)
        self.assertEqual(config.read_text(), "existing configuration")


if __name__ == "__main__":
    unittest.main()
