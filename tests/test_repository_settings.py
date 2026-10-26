"""Exercise repository-setting writes and failures without network access."""

from contextlib import ExitStack, redirect_stdout, redirect_stderr
from copy import deepcopy
import importlib.util
import io
import json
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "repository_settings", ROOT / "scripts/repository-settings.py"
)
settings = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(settings)
REPO = "ninegene/example-repo"
ENDPOINT = f"repos/{REPO}"


class GitHub:
    def __init__(self):
        self.repository = {
            "full_name": REPO, "default_branch": "main", "fork": False,
            "archived": False, "description": "Preserve unrelated metadata",
        }
        self.calls = []
        self.writes = []
        self.fail = None

    def api(self, method, endpoint, payload=None):
        self.calls.append((method, endpoint))
        if self.fail == (method, endpoint):
            raise RuntimeError("GitHub refused the operation")
        if method == "PATCH" and endpoint == ENDPOINT:
            self.writes.append(deepcopy(payload))
            self.repository.update(payload)
        elif method != "GET":
            raise AssertionError(f"Unexpected mutation: {method} {endpoint}")
        if endpoint == ENDPOINT:
            return deepcopy(self.repository)
        if endpoint == ENDPOINT + "/branches/main":
            return {"name": "main"}
        raise AssertionError(f"Unexpected endpoint: {endpoint}")


class RepositorySettingsTests(unittest.TestCase):
    def setUp(self):
        self.github = GitHub()
        self.output = io.StringIO()
        contexts = ExitStack()
        self.addCleanup(contexts.close)
        contexts.enter_context(redirect_stdout(self.output))
        contexts.enter_context(patch.object(settings, "api", side_effect=self.github.api))

    def test_default_check_is_read_only_and_reports_drift(self):
        self.assertEqual(settings.configure(REPO), 1)
        self.assertEqual(self.github.writes, [])
        self.assertIn("No changes made", self.output.getvalue())

    def test_apply_preserves_unrelated_settings_and_is_idempotent(self):
        self.assertEqual(settings.configure(REPO, apply=True), 0)
        self.assertEqual(len(self.github.writes), 1)
        self.assertFalse(self.github.writes[0]["allow_merge_commit"])
        self.assertEqual(self.github.repository["description"], "Preserve unrelated metadata")
        self.github.writes.clear()
        self.assertEqual(settings.configure(REPO, apply=True), 0)
        self.assertEqual(settings.configure(REPO), 0)
        self.assertEqual(self.github.writes, [])

    def test_only_free_repository_setting_endpoints_are_used(self):
        settings.configure(REPO, apply=True)
        self.assertTrue(all(
            endpoint in {ENDPOINT, ENDPOINT + "/branches/main"}
            for _, endpoint in self.github.calls
        ))
        self.assertFalse(any("ruleset" in endpoint or "protection" in endpoint
                             for _, endpoint in self.github.calls))

    def test_missing_main_prevents_writes(self):
        self.github.fail = ("GET", ENDPOINT + "/branches/main")
        with self.assertRaises(RuntimeError):
            settings.configure(REPO, apply=True)
        self.assertEqual(self.github.writes, [])

    def test_patch_failure_is_not_reported_as_success(self):
        self.github.fail = ("PATCH", ENDPOINT)
        with self.assertRaises(RuntimeError):
            settings.configure(REPO, apply=True)
        self.assertNotIn("match the template", self.output.getvalue())

    def test_rejected_readback_fails_verification(self):
        original = self.github.api

        def ignore_write(method, endpoint, payload=None):
            result = original(method, endpoint, payload)
            if method == "PATCH":
                self.github.repository["allow_merge_commit"] = True
            return result

        with patch.object(settings, "api", side_effect=ignore_write):
            with self.assertRaisesRegex(RuntimeError, "Read-back verification failed"):
                settings.configure(REPO, apply=True)

    def test_forks_and_archives_are_not_modified(self):
        for field in ["fork", "archived"]:
            self.github.repository = {"full_name": REPO, field: True}
            with self.assertRaisesRegex(RuntimeError, "excluded"):
                settings.configure(REPO, apply=True)
        self.assertEqual(self.github.writes, [])

    def test_repository_redirects_cannot_change_the_write_target(self):
        for name in ["another-owner/example-repo", "ninegene/renamed-repo", ""]:
            self.github.repository["full_name"] = name
            with self.assertRaisesRegex(RuntimeError, "identity changed"):
                settings.configure(REPO, apply=True)
        self.assertEqual(self.github.writes, [])

    def test_cli_rejects_other_owners_without_api_calls(self):
        for target in ["other/example", "ninegene/..", "ninegene/."]:
            with patch("sys.argv", ["repository-settings.py", target, "--apply"]):
                with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
                    settings.main()
            self.assertEqual(error.exception.code, 2)
        settings.api.assert_not_called()


class TransportTests(unittest.TestCase):
    def test_json_preserves_false_and_uses_github_hostname(self):
        with patch.object(settings.subprocess, "run", return_value=SimpleNamespace(
            returncode=0, stdout='{"ok":true}', stderr=""
        )) as run:
            settings.api("PATCH", ENDPOINT, {"allow_merge_commit": False})
            self.assertEqual(json.loads(run.call_args.kwargs["input"]), {"allow_merge_commit": False})
            self.assertIn("--hostname", run.call_args.args[0])
            self.assertIn("github.com", run.call_args.args[0])


if __name__ == "__main__":
    unittest.main()
