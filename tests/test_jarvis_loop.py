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

    def test_repeated_rolls_keep_rules_and_archive_settled_tool_history(self):
        engine = SimpleNamespace(generate=Mock(return_value={"content": "ok"}))
        run = self.root / "logs/runs/rolling"
        run.mkdir(parents=True)
        recorder = loop.RecordingEngine(engine, run, 4000, 256)
        rules = SimpleNamespace(role="system", content="IMMUTABLE RULES")
        task = SimpleNamespace(role="user", content="ACTIVE TASK")
        messages = [rules, task]
        recorder.generate(messages)
        for i in range(24):
            messages.append(SimpleNamespace(role="assistant", content="Inspect actual result " + str(i),
                                            tool_calls=[{"id": str(i), "name": "file_read"}]))
            messages.append(SimpleNamespace(role="tool", content="DATA " * 700,
                                            tool_call_id=str(i)))
            recorder.generate(messages)
        self.assertEqual(engine.generate.call_count, 25)
        self.assertIs(messages[0], rules)
        self.assertIs(messages[1], task)
        self.assertLess(len(messages), 16)
        self.assertIn("SCHEDULER_CHECKPOINT", (self.root / "logs/CURRENT_WORK.md").read_text())
        archives = list(run.glob("checkpoint-*.json"))
        self.assertGreater(len(archives), 3)
        self.assertIn("DATA", " ".join(p.read_text() for p in archives))

    def test_roll_never_drops_new_user_instructions_or_pending_protocol(self):
        engine = SimpleNamespace(generate=Mock(return_value={"content": "ok"}))
        recorder = loop.RecordingEngine(engine, self.root, 32768, 2048)
        messages = [SimpleNamespace(role="user", content="RULES")]
        recorder.generate(messages)
        instruction = SimpleNamespace(role="user", content="NEW USER CONSTRAINT")
        messages.extend([instruction, SimpleNamespace(role="assistant", content="Plan",
                         tool_calls=[{"id": "pending"}])])
        self.assertFalse(recorder.roll_history(messages, "test"))
        self.assertEqual(recorder.checkpoints, 0)
        messages.append(SimpleNamespace(role="tool", content="done", tool_call_id="pending"))
        self.assertTrue(recorder.roll_history(messages, "test"))
        self.assertIs(messages[1], instruction)
        self.assertIsNone(messages[-1].tool_calls)

    def test_periodic_checkpoint_does_not_require_model_file_write(self):
        run = self.root / "logs/runs/periodic"
        run.mkdir(parents=True)
        recorder = loop.RecordingEngine(SimpleNamespace(generate=lambda *a, **k: {"content": "ok"}),
                                        run, 32768, 2048)
        messages = [SimpleNamespace(role="user", content="RULES")]
        for i in range(5):
            recorder.generate(messages)
        self.assertEqual(recorder.checkpoints, 1)
        text = (self.root / "logs/CURRENT_WORK.md").read_text()
        self.assertIn("NOT_STARTED", text)
        self.assertIn("periodic", text)
        recorder.checkpoint(messages, "next")
        self.assertEqual((self.root / "logs/CURRENT_WORK.md").read_text().count("<!-- SCHEDULER_CHECKPOINT -->"), 1)


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

    def test_host_file_work_never_advertises_disposable_docker_tools(self):
        names, _, _ = loop.select_tools("code_interpreter_docker,file_write",
                                       "docker_shell_exec,file_read", self.registry())
        self.assertEqual(names, ["file_write", "file_read", "shell_exec"])

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

    def path_error(self):
        return ('Traceback (most recent call last):\n'
                '  File "<string>", line 138, in <module>\n'
                "FileNotFoundError: [Errno 2] No such file or directory: '/home/pagi/breachline-agent/repo/quickpuzzle/index.html'\n")

    def test_completed_audited_isolated_failure_allows_corrected_next_inference(self):
        ledger = loop.ActionLedger(self.root)
        ledger.docker_proof = {"source_ast_sha256": loop.DOCKER_SOURCE_AST_SHA256}
        ledger.record("tool_call_start", {"tool": "code_interpreter_docker"})
        ledger.record("tool_call_end", {"tool": "code_interpreter_docker",
                                      "success": False, "result": self.path_error()})
        engine = SimpleNamespace(generate=Mock(return_value={"content": "inspect host, then use file_write"}))
        recorder = loop.RecordingEngine(engine, self.root, 32768, 2048, ledger=ledger)
        messages = self.messages + [SimpleNamespace(role="tool", content=self.path_error())]
        recorder.generate(messages)
        engine.generate.assert_called_once()
        self.assertEqual(len(ledger.actions), 1)
        self.assertEqual(ledger.actions[0]["status"], "FAILED_ISOLATED")
        self.assertIs(engine.generate.call_args.args[0], messages)

    def test_path_error_alone_never_proves_host_isolation(self):
        for name, result, proof in (
                ("code_interpreter_docker", self.path_error(), None),
                ("shell_exec", self.path_error(), {"verified": True}),
                ("code_interpreter_docker", "Execution timed out after 30 seconds.", {"verified": True}),
                ("code_interpreter_docker", self.path_error() + "... (output truncated)", {"verified": True})):
            self.assertFalse(loop.isolated_path_failure(name, result, proof))

    def isolated_old_run(self, result=None):
        run = self.root / "runs/20261011-failed"
        run.mkdir(parents=True)
        ledger = loop.ActionLedger(run)
        ledger.record("tool_call_start", {"tool": "code_interpreter_docker"})
        ledger.record("tool_call_end", {"tool": "code_interpreter_docker", "success": False})
        loop.save_json(run / "manifest.json", {"status": "FAILED", "mission_id": "fresh"})
        (run / "error.txt").write_text(result or self.path_error())
        events = [{"event": "tool_call_start", "tool_name": "code_interpreter_docker"},
                  {"event": "tool_call_end", "tool_name": "code_interpreter_docker",
                   "success": False, "result_path": str(run / "error.txt")}]
        (run / "events.jsonl").write_text("\n".join(json.dumps(e) for e in events))
        return run, ledger

    def test_old_screenshot_failure_resumes_preserving_all_original_evidence(self):
        run, ledger = self.isolated_old_run()
        originals = {p.name: p.read_bytes() for p in run.iterdir()}
        with patch.object(loop, "isolated_docker_proof", return_value={"verified": True}):
            loop.check_previous_run(self.root)
            loop.check_previous_run(self.root)
        for name, raw in originals.items():
            self.assertEqual((run / name).read_bytes(), raw)
        review = json.loads((run / "isolated_action_review.json").read_text())
        self.assertEqual(review["actions"][0]["status"], "FAILED_ISOLATED")
        self.assertEqual(ledger.actions[0]["status"], "FAILED")
        notice = loop.previous_run_notice(self.root, "fresh")
        self.assertIn("FAILED", notice)

    def test_unknown_implementation_missing_result_and_unpaired_events_stay_blocked(self):
        run, _ = self.isolated_old_run()
        with patch.object(loop, "isolated_docker_proof", return_value=None):
            with self.assertRaises(loop.UnsafeRecoveryError):
                loop.check_previous_run(self.root)
        with patch.object(loop, "isolated_docker_proof", return_value={"verified": True}):
            (run / "error.txt").unlink()
            with self.assertRaises(loop.UnsafeRecoveryError):
                loop.check_previous_run(self.root)
            (run / "error.txt").write_text(self.path_error())
            (run / "events.jsonl").write_text(json.dumps({"event": "tool_call_end",
                "tool_name": "code_interpreter_docker", "success": False,
                "result_path": str(run / "error.txt")}))
            with self.assertRaises(loop.UnsafeRecoveryError):
                loop.check_previous_run(self.root)

    def test_result_outside_run_and_other_failed_write_do_not_get_reconciled(self):
        run, ledger = self.isolated_old_run()
        outside = self.root / "outside.txt"
        outside.write_text(self.path_error())
        events = [json.loads(l) for l in (run / "events.jsonl").read_text().splitlines()]
        events[-1]["result_path"] = str(outside)
        (run / "events.jsonl").write_text("\n".join(json.dumps(e) for e in events))
        with patch.object(loop, "isolated_docker_proof", return_value={"verified": True}):
            with self.assertRaises(loop.UnsafeRecoveryError):
                loop.check_previous_run(self.root)
        events[-1]["result_path"] = str(run / "error.txt")
        events += [{"event": "tool_call_start", "tool_name": "shell_exec"},
                   {"event": "tool_call_end", "tool_name": "shell_exec", "success": False}]
        (run / "events.jsonl").write_text("\n".join(json.dumps(e) for e in events))
        ledger.record("tool_call_start", {"tool": "shell_exec"})
        ledger.record("tool_call_end", {"tool": "shell_exec", "success": False})
        with patch.object(loop, "isolated_docker_proof", return_value={"verified": True}):
            with self.assertRaises(loop.UnsafeRecoveryError):
                loop.check_previous_run(self.root)

    def test_interrupted_docker_action_never_becomes_completed_isolated_failure(self):
        ledger = loop.ActionLedger(self.root)
        ledger.docker_proof = {"verified": True}
        ledger.record("tool_call_start", {"tool": "code_interpreter_docker"})
        with self.assertRaises(loop.UnsafeRecoveryError):
            ledger.check()

    def test_runtime_proof_requires_both_exact_tool_and_default_factory(self):
        import ast
        cls = type("DockerCodeInterpreterTool", (), {})
        source = "class DockerCodeInterpreterTool:\n    pass\n"
        factory = "def _build_tools():\n    return tool_cls()\n"
        source_path = self.root / "tool.py"
        source_path.write_text(source)
        source_hash = loop.digest(ast.dump(ast.parse(source), include_attributes=False).encode())
        factory_hash = loop.digest(ast.dump(ast.parse(factory).body[0], include_attributes=False).encode())
        modules = {"openjarvis": SimpleNamespace(tools=SimpleNamespace()),
                   "openjarvis.tools": SimpleNamespace(),
                   "openjarvis.core.registry": SimpleNamespace(ToolRegistry=SimpleNamespace(get=lambda name: cls)),
                   "openjarvis.tools.code_interpreter_docker": SimpleNamespace(DockerCodeInterpreterTool=cls),
                   "openjarvis.cli.ask": SimpleNamespace(_build_tools=Mock())}
        with patch.dict(sys.modules, modules), \
             patch.object(loop.inspect, "getfile", return_value=str(source_path)), \
             patch.object(loop.inspect, "getsource", return_value=factory), \
             patch.object(loop, "DOCKER_SOURCE_AST_SHA256", source_hash), \
             patch.object(loop, "TOOL_FACTORY_AST_SHA256", factory_hash):
            self.assertEqual(loop.isolated_docker_proof()["source_ast_sha256"], source_hash)
            with patch.object(loop, "TOOL_FACTORY_AST_SHA256", "changed"):
                self.assertIsNone(loop.isolated_docker_proof())
            with patch.object(loop, "DOCKER_SOURCE_AST_SHA256", "changed"):
                self.assertIsNone(loop.isolated_docker_proof())
            modules["openjarvis.core.registry"].ToolRegistry.get = lambda name: type("CustomDocker", (), {})
            self.assertIsNone(loop.isolated_docker_proof())


class CycleIntegrationTests(unittest.TestCase):
    setUp = ContextTests.setUp
    write_contract = ContextTests.write_contract

    def test_main_continues_after_three_consecutive_context_handoffs(self):
        with patch.object(sys, "argv", ["jarvis_loop", "--workspace", str(self.root)]), \
             patch.object(loop, "check_previous_run"), \
             patch.object(loop, "run_cycle", side_effect=["CONTEXT_HANDOFF"] * 4 + [KeyboardInterrupt()]) as cycle, \
             patch.object(loop.time, "sleep") as sleep, \
             patch.object(loop.os, "chdir"), patch.object(loop.signal, "signal"):
            loop.main()
        self.assertEqual(cycle.call_count, 5)
        # StopRequest uses interruptible one-second waits (60 per cycle).
        self.assertEqual(sleep.call_count, 240)

    def test_two_cycles_reload_handoff_and_retry_model_without_replaying_actions(self):
        self.exercise_cycles()

    def test_context_overflow_reloads_checkpoint_without_replaying_write(self):
        self.exercise_cycles(overflow=True)

    def test_context_overflow_without_checkpoint_stops(self):
        self.exercise_cycles(overflow=True, checkpoint=False)

    def test_context_overflow_with_uncertain_write_stops(self):
        self.exercise_cycles(overflow=True, uncertain=True)

    def test_returned_failure_without_event_is_not_hidden_by_earlier_success(self):
        self.exercise_cycles(unreported_failure=True)

    def exercise_cycles(self, overflow=False, checkpoint=True, uncertain=False, unreported_failure=False):
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
            if checkpoint:
                (self.root / "logs/CURRENT_WORK.md").write_text(handoff)
            writes.append(handoff)
            bus.emit("tool_call_end", tool="file_write", success=True, result="saved")
            if overflow and len(observed) == 1:
                if uncertain:
                    bus.emit("tool_call_start", tool="shell_exec")
                # Protected user context cannot be compacted to fit the ceiling.
                messages.append(SimpleNamespace(role="user", content="x" * 110000))
            kwargs["engine"].generate(messages)
            results = [
                SimpleNamespace(tool_name="web_search", success=True, content="mock source"),
                SimpleNamespace(tool_name="file_write", success=True, content="saved")]
            if unreported_failure:
                results.append(SimpleNamespace(tool_name="file_write", success=False, content="Write error: disk full"))
            return SimpleNamespace(content="done", turns=2, metadata={}, tool_results=results)

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
            if unreported_failure:
                with self.assertRaises(loop.UnsafeRecoveryError):
                    loop.run_cycle(self.root, config, self.prompt, policy.num_ctx, policy)
                run = next((self.root / "logs/runs").iterdir())
                self.assertEqual([a["status"] for a in json.loads((run / "action_receipts.json").read_text())],
                                 ["SUCCEEDED", "SUCCEEDED", "FAILED"])
                self.assertEqual(len(json.loads((run / "tool_results.json").read_text())), 3)
                self.assertEqual((run / "answer.md").read_text(), "done")
                self.assertTrue((run / "failure_snapshot.json").exists())
                return
            if overflow and (not checkpoint or uncertain):
                with self.assertRaises(loop.UnsafeRecoveryError if uncertain else loop.ContextBudgetError):
                    loop.run_cycle(self.root, config, self.prompt, policy.num_ctx, policy)
                manifest = json.loads(next((self.root / "logs/runs").glob("*/manifest.json")).read_text())
                self.assertEqual(manifest["status"], "FAILED")
                self.assertIn("failure_snapshot", manifest)
                snapshot = json.loads(Path(manifest["failure_snapshot"]).read_text())
                self.assertIn("messages", snapshot)
                self.assertIn("actions", snapshot)
                return
            first = loop.run_cycle(self.root, config, self.prompt, policy.num_ctx, policy)
            second = loop.run_cycle(self.root, config, self.prompt, policy.num_ctx, policy)
        self.assertEqual((first, second), ("CONTEXT_HANDOFF" if overflow else "CYCLE_RETURNED", "CYCLE_RETURNED"))
        if overflow:
            self.assertIn("CONTEXT_HANDOFF", observed[1])
            self.assertEqual(len(list((self.root / "logs/runs").glob("*/context_overflow.json"))), 1)
        self.assertEqual(writes, ["CONTINUE 1", "CONTINUE 2"])
        self.assertIn("CONTINUE 1", observed[1])
        self.assertNotIn("NOT_STARTED\n===== END FILE", observed[1])
        self.assertEqual(engine.generate.call_count, 4 if overflow else 5)
        self.assertEqual(config.read_text(), "existing configuration")


if __name__ == "__main__":
    unittest.main()

