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
            "Check repository access and administration permissions."
        )
    return json.loads(result.stdout)


def differences(expected, actual):
    """Compare only settings owned by the template."""
    return [
        f"{key}: expected {value!r}, got {actual.get(key)!r}"
        for key, value in expected.items() if actual.get(key) != value
    ]


def configure(repo, apply=False):
    settings = json.loads((TEMPLATES / "repository.json").read_text())
    endpoint = f"repos/{repo}"
    current = api("GET", endpoint)
    # Reject rename/transfer redirects instead of writing to another repository.
    if current.get("full_name", "").lower() != repo.lower():
        raise RuntimeError("Repository identity changed; use its current, authorized name.")
    if current.get("fork") or current.get("archived"):
        raise RuntimeError("Forks and archived repositories are excluded from this baseline.")
    # The desired default branch must already exist; do not create or rename it.
    api("GET", f"{endpoint}/branches/{settings['default_branch']}")
    setting_changes = differences(settings, current)
    for change in setting_changes:
        print(change)
    if not apply:
        if setting_changes:
            print("Drift found. No changes made. Use --apply only for an authorized target.")
            return 1
    else:
        # Patch only managed repository settings; do not read or alter rulesets.
        if setting_changes:
            api("PATCH", endpoint, settings)
        saved = api("GET", endpoint)
        remaining = differences(settings, saved)
        if remaining:
            raise RuntimeError("Read-back verification failed:\n" + "\n".join(remaining))
    print(f"{repo}: repository settings match the template.")
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
