import importlib.util
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from types import SimpleNamespace

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


if __name__ == "__main__":
    unittest.main()
