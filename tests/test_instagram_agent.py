import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import HTTPError, URLError

SPEC = importlib.util.spec_from_file_location("instagram_agent", Path(__file__).resolve().parents[1] / "runtime/instagram_agent.py")
ig = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ig)


class FakeClient:
    def __init__(self, fail=None, status="FINISHED"):
        self.calls = []
        self.fail = fail
        self.status = status

    def identity(self):
        return {"username": ig.ACCOUNT, "user_id": ig.USER_ID}

    def clean(self, data):
        return data

    def api(self, method, path, params=None):
        self.calls.append((method, path))
        if path == self.fail:
            raise ig.AdapterError("simulated timeout")
        if path.endswith("/media"):
            return {"id": "111"}
        if path.endswith("/media_publish"):
            return {"id": "222"}
        if path == "111":
            return {"status_code": self.status}
        return {"id": "222", "permalink": "https://www.instagram.com/p/example/"}


class AdapterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.state = self.root / "state"
        self.job = {"kind": "IMAGE", "asset_url": "https://whisewolf.github.io/Breachline/assets/shot.jpg",
                    "caption": "Try the prototype", "test_url": "https://whisewolf.github.io/Breachline/games/test/",
                    "game_version": "abc123", "purpose": "Test controls", "gameplay_evidence": "test.txt",
                    "asset_rights": "own gameplay recording"}
        (self.root / "test.txt").write_text("Actual local test notes")
        self.job_path = self.root / "job.json"
        self.job_path.write_text(json.dumps(self.job))

    def tearDown(self):
        self.temp.cleanup()

    def test_dry_run_has_no_network_or_receipt(self):
        client = FakeClient()
        result = ig.publish(client, ig.job_data(self.job_path), self.state)
        self.assertEqual(result["status"], "PREVIEW_ONLY")
        self.assertEqual(client.calls, [])
        self.assertFalse(self.state.exists())

    def test_success_is_durable_and_duplicate_not_republished(self):
        client = FakeClient()
        with patch.object(ig, "reachable"):
            result = ig.publish(client, self.job, self.state, True)
            calls = len(client.calls)
            again = ig.publish(client, self.job, self.state, True)
        self.assertEqual(result["media_id"], "222")
        self.assertEqual(again["status"], "PUBLISHED")
        self.assertEqual(len(client.calls), calls)
        receipt = self.state / (ig.fingerprint(self.job) + ".json")
        self.assertEqual(receipt.stat().st_mode & 0o777, 0o600)
        self.assertEqual(self.state.stat().st_mode & 0o777, 0o700)

    def test_unknown_creation_and_publish_are_never_replayed(self):
        for endpoint, expected in [(ig.USER_ID + "/media", "CREATING"), (ig.USER_ID + "/media_publish", "PUBLISHING")]:
            state = self.root / expected
            client = FakeClient(fail=endpoint)
            with patch.object(ig, "reachable"):
                with self.assertRaises(ig.AdapterError):
                    ig.publish(client, self.job, state, True)
                calls = len(client.calls)
                with self.assertRaises(ig.AdapterError):
                    ig.publish(client, self.job, state, True)
            self.assertEqual(len(client.calls), calls)
            self.assertEqual(json.loads(next(state.glob("*.json")).read_text())["status"], expected)

    def test_pending_processing_reuses_same_container(self):
        client = FakeClient(status="IN_PROGRESS")
        with patch.object(ig, "reachable"):
            self.assertEqual(ig.publish(client, self.job, self.state, True)["status"], "NOT_READY")
            client.status = "FINISHED"
            self.assertEqual(ig.publish(client, self.job, self.state, True)["status"], "PUBLISHED")
        self.assertEqual(client.calls.count(("POST", ig.USER_ID + "/media")), 1)

    def test_permalink_failure_does_not_lose_publication(self):
        client = FakeClient(fail="222")
        with patch.object(ig, "reachable"):
            result = ig.publish(client, self.job, self.state, True)
        self.assertEqual(result["status"], "PUBLISHED")
        self.assertEqual(json.loads(next(self.state.glob("*.json")).read_text())["media_id"], "222")

    def client(self):
        path = self.root / "instagram.json"
        path.write_text(json.dumps({"access_token": "secret-test-token"}))
        return ig.Client(path)

    def test_wrong_account_is_blocked(self):
        client = self.client()
        with patch.object(client, "api", return_value={"user_id": "42", "username": "wrong"}):
            with self.assertRaises(ig.AdapterError):
                client.identity()

    def test_job_rejects_unrelated_urls_and_missing_evidence(self):
        ig.job_data(self.job_path)
        for key, value in [("test_url", "https://example.com/game/"), ("asset_url", "https://whisewolf.github.io/Breachline/a.jpg?token=secret"), ("gameplay_evidence", "missing.txt")]:
            job = dict(self.job, **{key: value})
            self.job_path.write_text(json.dumps(job))
            with self.assertRaises(ig.AdapterError):
                ig.job_data(self.job_path)

    def test_api_error_does_not_expose_token(self):
        client = self.client()
        error = HTTPError("https://graph.instagram.com", 400, "bad", {}, io.BytesIO(b'{"error":{"message":"secret-test-token"}}'))
        with patch.object(ig, "build_opener") as opener:
            opener.return_value.open.side_effect = error
            with self.assertRaises(ig.AdapterError) as caught:
                client.api("GET", "me")
        self.assertNotIn(client.token, str(caught.exception))

    def test_failed_refresh_preserves_credentials(self):
        client = self.client()
        before = client.path.read_bytes()
        with patch.object(client, "identity"), patch.object(client, "api", return_value={}):
            with self.assertRaises(ig.AdapterError):
                ig.refresh(client)
        self.assertEqual(client.path.read_bytes(), before)

    def test_paging_urls_are_not_exposed(self):
        client = self.client()
        with patch.object(client, "api", return_value={"data": [], "paging": {"next": "https://graph.instagram.com/?access_token=secret-test-token", "cursors": {"after": "abc"}}}):
            data = client.collection(ig.USER_ID + "/media")
        self.assertEqual(data["after"], "abc")
        self.assertNotIn("secret-test-token", json.dumps(data))


if __name__ == "__main__":
    unittest.main()
