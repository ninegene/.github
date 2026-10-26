#!/usr/bin/env python3
"""Check repository defaults; write only with --apply. Requires gh and Python 3."""

import argparse
import json
from pathlib import Path
import re
import subprocess
import sys


TEMPLATES = Path(__file__).resolve().parents[1] / "repo-settings"


def api(method, endpoint, payload=None):
    command = [
        "gh", "api", "--hostname", "github.com", "--method", method,
        "-H", "Accept: application/vnd.github+json",
        "-H", "X-GitHub-Api-Version: 2026-03-10", endpoint,
    ]
    if payload is not None:
        command += ["--input", "-"]
    result = subprocess.run(
        command, input=json.dumps(payload) if payload is not None else None,
        text=True, capture_output=True, check=False,
    )
    if result.returncode:
        raise RuntimeError(
            f"{method} {endpoint} failed: {result.stderr.strip()}\n"
            "Check access, administration permissions, and plan support. "
            "Do not treat an unavailable ruleset as enforced."
        )
    return json.loads(result.stdout)


def differences(expected, actual, prefix=""):
    """Compare managed fields; tolerate extra API response metadata."""
    changes = []
    for key, value in expected.items():
        path = f"{prefix}.{key}" if prefix else key
        other = actual.get(key)
        if isinstance(value, dict) and isinstance(other, dict):
            changes.extend(differences(value, other, path))
        elif key == "rules" and isinstance(other, list):
            by_type = {rule["type"]: rule for rule in other}
            for rule in value:
                changes.extend(differences(rule, by_type.get(rule["type"], {}), path))
            extra = set(by_type) - {rule["type"] for rule in value}
            if extra:
                changes.append(f"{path}: additional rules {sorted(extra)}")
        elif value != other:
            changes.append(f"{path}: expected {value!r}, got {other!r}")
    return changes


def managed_ruleset(repo, name):
    matches = []
    page = 1
    while True:
        rulesets = api("GET", f"repos/{repo}/rulesets?per_page=100&page={page}")
        matches.extend(
            item for item in rulesets
            if item["name"] == name and item.get("source_type") == "Repository"
            and item.get("source", "").lower() == repo.lower()
        )
        if len(rulesets) < 100:
            break
        page += 1
    if len(matches) > 1:
        raise RuntimeError("Multiple matching rulesets; reconcile duplicates manually first.")
    if matches:
        return api("GET", f"repos/{repo}/rulesets/{matches[0]['id']}")
    return None


def configure(repo, apply=False):
    settings = json.loads((TEMPLATES / "repository.json").read_text())
    rules = json.loads((TEMPLATES / "default-branch.ruleset.json").read_text())
    endpoint = f"repos/{repo}"
    current = api("GET", endpoint)
    if current.get("fork") or current.get("archived"):
        raise RuntimeError("Forks and archived repositories are excluded from this baseline.")
    # Verify the initialized branch and access to rulesets before any mutation.
    api("GET", f"{endpoint}/branches/{settings['default_branch']}")
    existing = managed_ruleset(repo, rules["name"])
    setting_changes = differences(settings, current)
    rule_changes = differences(rules, existing or {})
    for change in setting_changes + rule_changes:
        print(change)
    if not apply:
        if setting_changes or rule_changes:
            print("Drift found. No changes made. Use --apply only for an authorized target.")
            return 1
    else:
        # This manages only these settings and this named ruleset. Preserve all others.
        # API writes are not transactional: on failure, stop and report partial setup.
        if setting_changes:
            api("PATCH", endpoint, settings)
        if rule_changes:
            if existing:
                api("PUT", f"{endpoint}/rulesets/{existing['id']}", rules)
            else:
                api("POST", f"{endpoint}/rulesets", rules)
        saved = api("GET", endpoint)
        saved_rules = managed_ruleset(repo, rules["name"])
        remaining = differences(settings, saved) + differences(rules, saved_rules or {})
        if remaining:
            raise RuntimeError("Read-back verification failed:\n" + "\n".join(remaining))
    print(f"{repo}: repository settings and default-branch ruleset match the templates.")
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repository", help="ninegene/REPOSITORY on github.com")
    parser.add_argument("--apply", action="store_true", help="Apply defaults, then verify by reading back")
    args = parser.parse_args()
    if (
        not re.fullmatch(r"ninegene/[A-Za-z0-9_.-]+", args.repository)
        or args.repository.rsplit("/", 1)[-1] in {".", ".."}
    ):
        parser.error("target must be a ninegene repository, not a URL or another owner")
    try:
        return configure(args.repository, args.apply)
    except (RuntimeError, OSError, ValueError) as error:
        print(f"Setup incomplete: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
