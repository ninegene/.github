"""Exercise GitHub mutations and failure handling without network access."""

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
        self.repository = {"full_name": REPO, "default_branch": "main", "fork": False, "archived": False}
        self.rulesets = {}
        self.writes = []
        self.fail = None

    def api(self, method, endpoint, payload=None):
        if self.fail == (method, endpoint):
            raise RuntimeError("GitHub refused the operation")
        if method != "GET":
            self.writes.append((method, endpoint, deepcopy(payload)))
        if endpoint == ENDPOINT:
            if method == "PATCH":
                self.repository.update(payload)
            return deepcopy(self.repository)
        if endpoint == ENDPOINT + "/branches/main":
            return {"name": "main"}
        if "/rulesets?" in endpoint:
            return [
                {"id": key, "name": value["name"], "source_type": "Repository", "source": REPO}
                for key, value in self.rulesets.items()
            ]
        if method == "POST" and endpoint.endswith("/rulesets"):
            key = max(self.rulesets, default=0) + 1
            self.rulesets[key] = dict(deepcopy(payload), id=key)
            return self.rulesets[key]
        key = int(endpoint.rsplit("/", 1)[1])
        if method == "PUT":
            self.rulesets[key] = dict(deepcopy(payload), id=key)
        return deepcopy(self.rulesets[key])


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

    def test_apply_and_reapply_are_idempotent(self):
        self.assertEqual(settings.configure(REPO, apply=True), 0)
        self.assertEqual([method for method, _, _ in self.github.writes], ["PATCH", "POST"])
        self.github.writes.clear()
        self.assertEqual(settings.configure(REPO, apply=True), 0)
        self.assertEqual(settings.configure(REPO), 0)
        self.assertEqual(self.github.writes, [])

    def test_update_existing_ruleset_preserves_unrelated_ruleset(self):
        settings.configure(REPO, apply=True)
        self.github.rulesets[1]["enforcement"] = "disabled"
        self.github.rulesets[9] = {"id": 9, "name": "project-ci", "rules": []}
        self.github.writes.clear()
        settings.configure(REPO, apply=True)
        self.assertEqual(self.github.writes[0][:2], ("PUT", ENDPOINT + "/rulesets/1"))
        self.assertEqual(self.github.rulesets[9], {"id": 9, "name": "project-ci", "rules": []})

    def test_missing_main_or_unavailable_rulesets_prevents_writes(self):
        for endpoint in [ENDPOINT + "/branches/main", ENDPOINT + "/rulesets?per_page=100&page=1"]:
            self.github.fail = ("GET", endpoint)
            with self.assertRaises(RuntimeError):
                settings.configure(REPO, apply=True)
            self.assertEqual(self.github.writes, [])

    def test_duplicate_managed_rulesets_prevent_writes(self):
        settings.configure(REPO, apply=True)
        self.github.rulesets[2] = deepcopy(self.github.rulesets[1])
        self.github.writes.clear()
        with self.assertRaisesRegex(RuntimeError, "Multiple matching"):
            settings.configure(REPO, apply=True)
        self.assertEqual(self.github.writes, [])

    def test_partial_failure_is_not_reported_as_success(self):
        self.github.fail = ("POST", ENDPOINT + "/rulesets")
        with self.assertRaises(RuntimeError):
            settings.configure(REPO, apply=True)
        self.assertEqual(self.github.writes[0][0], "PATCH")
        self.assertNotIn("match the templates", self.output.getvalue())

    def test_rejected_readback_fails_verification(self):
        original = self.github.api

        def ignore_write(method, endpoint, payload=None):
            if method == "POST":
                payload = dict(payload, enforcement="disabled")
            return original(method, endpoint, payload)

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

    def test_rule_order_is_ignored_but_missing_protection_is_not(self):
        settings.configure(REPO, apply=True)
        self.github.rulesets[1]["rules"].reverse()
        self.assertEqual(settings.configure(REPO), 0)
        self.github.rulesets[1]["rules"] = []
        self.assertEqual(settings.configure(REPO), 1)

    def test_pagination_finds_owned_ruleset_not_inherited_namesake(self):
        name = "ninegene-default-branch"
        pages = {
            ENDPOINT + "/rulesets?per_page=100&page=1": [
                {"id": 99, "name": name, "source_type": "Organization", "source": "other"}
            ] * 100,
            ENDPOINT + "/rulesets?per_page=100&page=2": [
                {"id": 1, "name": name, "source_type": "Repository", "source": REPO}
            ],
            ENDPOINT + "/rulesets/1": {"id": 1, "name": name},
        }
        with patch.object(settings, "api", side_effect=lambda method, endpoint: pages[endpoint]):
            self.assertEqual(settings.managed_ruleset(REPO, name)["id"], 1)

    def test_cli_rejects_other_owners_without_api_calls(self):
        for target in ["other/example", "ninegene/..", "ninegene/."]:
            with patch("sys.argv", ["repository-settings.py", target, "--apply"]):
                with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
                    settings.main()
            self.assertEqual(error.exception.code, 2)
        settings.api.assert_not_called()


class TransportTests(unittest.TestCase):
    def test_json_preserves_false_and_zero_and_uses_github_hostname(self):
        with patch.object(settings.subprocess, "run", return_value=SimpleNamespace(
            returncode=0, stdout='{"ok":true}', stderr=""
        )) as run:
            settings.api("PATCH", ENDPOINT, {"enabled": False, "approvals": 0})
            self.assertEqual(json.loads(run.call_args.kwargs["input"]), {"enabled": False, "approvals": 0})
            self.assertIn("--hostname", run.call_args.args[0])
            self.assertIn("github.com", run.call_args.args[0])


if __name__ == "__main__":
    unittest.main()
