# Repository defaults

This baseline manages repository settings supported for private repositories on GitHub Free. It does not require Pro, install workflows, or manage branch protection.

- [repository.json](repository.json): fields for the repository settings API.
- [../scripts/repository-settings.py](../scripts/repository-settings.py): check/apply helper using Python 3 and an authenticated GitHub CLI. It only accepts `ninegene/REPOSITORY` on github.com, verifies the returned repository identity to reject rename/transfer redirects, and excludes forks and archived repos.

## Baseline

| Setting | Value |
| --- | --- |
| Default branch | `main` |
| Allowed PR merge method | Squash only; merge commits and rebase merges disabled |
| Squash commit title/body defaults | PR title and PR description |
| Delete head branches after merge | Enabled |
| Auto-merge / always offer update-branch | Disabled |

The squash title/body settings **prefill defaults**; GitHub still lets the merger edit the message. They do not validate Conventional Commits or force exact title/body equality. Follow the workspace PR-writing guidance when merging.

The helper does not read or modify rulesets, required approvals, code-owner approvals, status checks, or classic branch protections. Existing protections remain unchanged. For private repositories on GitHub Free, this baseline does not enforce PR-only changes, review-thread resolution, or force-push/deletion protection. Use PRs and follow AGENTS.md's Codex review procedure, including checking unresolved findings before merging. Do not claim these process requirements are server-enforced.

## What enforces this?

A JSON file in `.github` is not automatically applied to other repositories. For this personal account, enforcement is a required creation procedure in AGENTS.md plus API application and read-back verification. Running the helper without `--apply` detects drift and exits nonzero. It can be used in a separately authorized periodic audit; no scheduler or workflow is installed here.

Set **GitHub user Settings → Repositories → Repository default branch** to `main` as a second line of defense for web-created repos. This account-level setting is manual. Always use `git init -b main` for local creation, regardless of global Git configuration.

## Create a new repository

Follow the user-authorized visibility and commit/push scope. These commands assume the shell is at the workspace root. Replace `example-repo` before running them.

1. Initialize with `git init -b main example-repo`, add its own README and AGENTS.md, and link CLAUDE.md to AGENTS.md.
2. With explicit commit authorization, create the initial commit on `main`. If commit/push permission is missing, prepare the files and report the remaining bootstrap steps; do not invent a commit exception.
3. With repository creation/push authorization, create the remote from the local source, for example `gh repo create ninegene/example-repo --private --source ./example-repo --remote origin --push`. Choose `--public` only when authorized. Remote `main` must exist before applying the default-branch setting. Avoid server-side auto-initialization that may create a different branch.
4. Inspect, apply, and verify:

   ```bash
   python3 .github/scripts/repository-settings.py ninegene/example-repo
   python3 .github/scripts/repository-settings.py ninegene/example-repo --apply
   python3 .github/scripts/repository-settings.py ninegene/example-repo
   ```

   Exit 0 means managed settings match; exit 1 means drift with no writes; exit 2 means setup/access/verification failed. The first check normally reports drift. `--apply` is an explicit GitHub write: use it only within authorization. It patches only fields in the JSON and reads them back; unrelated settings are preserved. If verification fails after a write, report setup as incomplete and inspect again.
5. Verify local upstream and `origin/HEAD` point to `main`, connect the repo to Codex, and enable its review setup if needed. Use feature branches and PRs after bootstrap. The baseline itself neither installs Codex nor requires a Codex review to run or finish.

An existing `master` repository needs a separately authorized rename/migration first. The helper does not rename branches, reset local refs, or create a missing `main`. Do not automatically run it over all existing repos.

## Permissions and verification

The authenticated `gh` user needs repository administration permission for settings writes. Never embed tokens in these files. No ruleset endpoint is called, so lack of private-repository ruleset support does not block these settings.

```bash
python3 -B -m unittest discover -s .github/tests -p 'test_*.py'
```

Tests mock GitHub and never write to a remote. Verify live application only on an authorized target. No test repo is created automatically.

## References

- [Repository settings API](https://docs.github.com/en/rest/repos/repos#update-a-repository)
- [Managing the default branch name](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/managing-repository-settings/managing-the-default-branch-name-for-your-repositories)
- [Ruleset plan availability](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets)
