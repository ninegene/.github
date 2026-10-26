# Repository defaults

These JSON files define the baseline for new, owned repositories on GitHub. They contain no credentials, repository IDs, app IDs, or private repository details.

- [repository.json](repository.json): fields for the repository settings API.
- [default-branch.ruleset.json](default-branch.ruleset.json): a repository branch ruleset, managed by name as `ninegene-default-branch`.
- [../scripts/repository-settings.py](../scripts/repository-settings.py): check/apply helper using Python 3 and an authenticated GitHub CLI. It only accepts `ninegene/REPOSITORY` on github.com, verifies the returned repository identity to reject rename/transfer redirects, and excludes forks and archived repos.

## Baseline

| Setting | Value |
| --- | --- |
| Default branch | `main` |
| Allowed PR merge method | Squash only; merge commits and rebase merges disabled |
| Squash commit title/body defaults | PR title and PR description |
| Delete head branches after merge | Enabled |
| Auto-merge / always offer update-branch | Disabled |
| Protected branches | The current default branch (`~DEFAULT_BRANCH`) |
| Require a PR | Yes; after the initial repository bootstrap |
| Required approvals / code-owner approval / latest-push approval | Zero / disabled / disabled |
| Unresolved code-review threads | Must be resolved before merge |
| Force pushes / branch deletion | Blocked on the default branch |
| Bypass actors | None, including no administrator or app exemption |
| Required status checks | No generic check names; configure actual CI checks per repo |

The squash title/body settings **prefill defaults**; GitHub still lets the merger edit the message. They do not validate Conventional Commits or force exact title/body equality. Follow the workspace PR-writing guidance when merging.

Use this ruleset instead of adding a duplicate classic branch-protection rule. Other rulesets and classic protections can impose additional restrictions; the helper does not weaken or delete those. When migrating an existing repo, inspect all effective rules before claiming no approvals are required.

## What enforces this?

A JSON file in `.github` is not automatically applied to other repositories. A GitHub template repository is also not a replacement for applying repository settings and rules. For this personal account, enforcement is a required creation procedure in AGENTS.md plus API application and read-back verification. Running the helper without `--apply` detects drift and exits nonzero. It can be used in a separately authorized periodic audit; no scheduler or workflow is installed here.

Set **GitHub user Settings → Repositories → Repository default branch** to `main` as a second line of defense for web-created repos. This account-level setting is manual and was not changed by this work. Always use `git init -b main` for local creation, regardless of global Git configuration.

## Create a new repository

Follow the user-authorized visibility and commit/push scope. The commands below assume the shell is at the workspace root. Replace `example-repo` before running them.

1. Initialize the local repo with `git init -b main example-repo`, add its own README and AGENTS.md, and link CLAUDE.md to AGENTS.md.
2. With explicit commit authorization, create the initial commit on `main`. If commit/push permission is missing, prepare the files and report the remaining bootstrap steps; do not invent a commit exception.
3. With repository creation/push authorization, create the remote from the local source, for example `gh repo create ninegene/example-repo --private --source ./example-repo --remote origin --push`. Choose `--public` only when that visibility is authorized. The initial `main` must exist remotely before applying the default-branch setting. Avoid server-side auto-initialization that may create a different branch.
4. Inspect and apply the baseline:

   ```bash
   python3 .github/scripts/repository-settings.py ninegene/example-repo
   python3 .github/scripts/repository-settings.py ninegene/example-repo --apply
   python3 .github/scripts/repository-settings.py ninegene/example-repo
   ```

   The first check normally reports drift (exit 1). Exit 0 means the managed settings match; exit 2 means setup/access/verification failed. `--apply` is an explicit GitHub write: use it only within the user's authorization. The helper creates the named ruleset once, updates it by ID on subsequent runs, and reads everything back. It controls all fields in the JSON and the contents of that one named ruleset; keep repo-specific checks in a separate ruleset. Unrelated settings/rulesets are preserved. API changes are not transactional: a later failure can leave partial setup, which must be reported and checked again.
5. Verify local upstream and `origin/HEAD` point to `main`, connect the repo to Codex, and enable its review setup if needed. Use feature branches and PRs after the bootstrap; do not directly push further changes to protected `main`.

An existing `master` repository needs a separately authorized rename/migration first. The helper intentionally does not rename branches, reset local refs, or create a missing `main` branch. Do not automatically run it over all existing repos.

## Codex findings and review completion

`required_review_thread_resolution: true` blocks merges while any inline code-review thread is unresolved, including Codex findings. It is not a gate on ordinary PR conversation comments, and resolving a thread does not prove the code is fixed. Assess each finding, record its disposition, and resolve it only after addressing it under the workspace review procedure.

This rule does **not** require a Codex review to run or finish, nor does it enforce that the latest head received a clean review. Continue following AGENTS.md's request/wait/verify procedure. If a hard completion gate is wanted later, add a verified check produced by an actual review integration; do not invent a required `Codex` context that no integration publishes. Codex access/review configuration is separate from these GitHub settings.

## Permissions and plan support

The authenticated `gh` user needs repository administration permissions for settings/ruleset writes. Never embed tokens in these files. Rulesets are available for public repositories on GitHub Free and private repositories on GitHub Pro/Team/Enterprise. Classic protected branches have similar plan restrictions; they are not a Free-private workaround.

If GitHub rejects a ruleset or reports it is not enforced on the current plan, report protection as unavailable/pending. Do not silently skip it, claim the repo is protected, change visibility, or upgrade the account. Confirm support and permissions before using the apply step on a private repo.

## Verify changes to the templates/helper

```bash
python3 -B -m unittest discover -s .github/tests -p 'test_*.py'
```

Tests use mocked GitHub responses and never write to a remote. Live application should be verified on a specifically authorized target; no test repository is created automatically.

## References

- [Repository settings API](https://docs.github.com/en/rest/repos/repos#update-a-repository)
- [Repository rulesets API](https://docs.github.com/en/rest/repos/rules)
- [Available rules, including required PRs and blocked force pushes](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets)
- [Ruleset availability and layered enforcement](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets)
- [Managing the default branch name](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/managing-repository-settings/managing-the-default-branch-name-for-your-repositories)
- [Protected branch availability](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)
