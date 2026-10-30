# AGENTS.md: ninegene Personal Workspace

The **workspace root** (the directory containing this file, usually `~/ninegene/` but it may be anywhere) is **not a git repository**. It is a local workspace that holds clones of repositories from the [`ninegene` GitHub user account](https://github.com/ninegene). Each subdirectory is its own independent git repo with its own history, tooling, and conventions.

The workspace-root `AGENTS.md` is a symlink to `.github/AGENTS.md` in the [ninegene/.github](https://github.com/ninegene/.github) repo, and `CLAUDE.md` is a symlink to `AGENTS.md`. Developer setup instructions are in `.github/README.md`.

**Before working inside a repo, read that repo's own `AGENTS.md` / `CLAUDE.md` / `README.md`.** Repo-level instructions override this file. This file only covers conventions shared by every repo.

## 1. This repo is public

`ninegene/.github` is a **public** repository. Everything committed here, including this file, is visible to the world.

- **Never add personal information** (real names of other people, addresses, phone numbers, emails, account IDs, machine names, private repo names or details).
- **Never add secrets** (passwords, API keys, tokens, SSH keys, `.env` contents).
- Keep content generic: conventions, tooling, and setup steps only.

## 2. About this workspace

`ninegene` holds personal projects. Some are public, some are private, and some are forks or third-party clones kept for reference. Each repo's own docs say what it is.

### Shared GitHub Wiki

The [shared wiki](https://github.com/ninegene/.github/wiki) belongs to [ninegene/.github](https://github.com/ninegene/.github), but its Git history is separate. Clone it from the workspace root with `gh repo clone ninegene/.github.wiki` and edit pages in `.github.wiki/`, not inside `.github/`. Its default branch is `master`; pages can also be edited in the browser, so check for remote changes before editing or publishing.

Use the `github-wiki` skill (`.github/.agent/skills/github-wiki/SKILL.md`) for page format, navigation, and URLs. Wiki content is public: apply §1. Preparing wiki edits does not authorize a commit or publication; follow §5.

Shared skills work with Claude, Codex, and GitHub Copilot. The source lives in `.github/.agent/skills/<name>/`; run `.github/link-workspace.sh` to link each skill into the workspace root (usually `~/ninegene/`) at `.claude/skills/` (Claude), `.agents/skills/` (Codex, Copilot), and `.agent/skills/`. Edit the source in `.github` only, and start agent sessions from the workspace root so those links are discovered.

## 3. Discovering repositories

This file intentionally does **not** list repositories. Repos get created, archived, cloned, and deleted over time, so any list here would go stale. Discover the current state instead:

- **Local clones:** each subdirectory of the workspace root that contains a `.git/` is a clone. Which repos are cloned varies by machine and over time.
- **All own repos (source of truth):**
  ```bash
  gh repo list ninegene --limit 100 --json name,description,visibility,isArchived,isFork,primaryLanguage,homepageUrl
  gh repo view ninegene/<repo-name>
  ```
- **Getting a repo that isn't cloned yet:** run `gh repo clone ninegene/<repo-name>` from the workspace root.
- **What a repo does:** read its `AGENTS.md` / `README.md`, not this file.

## 4. Conventions for repos

- **Location:** clone or create every `ninegene` repo directly under the workspace root as `<workspace>/<repo-name>/`, using the GitHub repo name as the directory name.
- **Agent docs:** every repo should have its own `AGENTS.md`, with `CLAUDE.md` as a symlink to it (`ln -s AGENTS.md CLAUDE.md`). Cover what the repo is, commands, architecture, and conventions specific to that repo.
- **Task runner:** when a repo needs a task file, prefer `just` with a `justfile` for commands such as setup, lint, test and release. Use `make` / `Makefile` only when make is a better fit, such as C or C++ builds that benefit from file dependencies and incremental compilation.
- **Shell utilities:** prefer GNU Coreutils (the GNU project, not uutils), sed, grep, Findutils, Gawk, Diffutils, tar, patch, gzip and wget for consistent development commands on macOS and Linux. Activate mise (or use `mise exec -- <command>`) and verify the implementation with `<command> --version` when GNU-specific behavior matters. Bootstrap code that runs before these tools are installed must work with the system utilities; keep OS-specific operations explicit and test on both platforms.
- **Visibility:** choose per repo. Anything with credentials, personal data, or private notes is **private**. Never commit secrets. Use env vars or local config files listed in `.gitignore`.
- **Default branch:** use `main` for new repositories. Initialize explicitly with `git init -b main`; do not rely on a machine's Git default. Do not rename branches in existing repositories without authorization. The separate GitHub Wiki clone's `master` branch is unaffected.
- **New-repository settings:** follow [repo-settings/README.md](repo-settings/README.md) in this repo. After an authorized initial commit/push creates remote `main`, apply [repo-settings/repository.json](repo-settings/repository.json) using `python3 .github/scripts/repository-settings.py ninegene/<repo-name> --apply` from the workspace root, then run the command without `--apply` to verify. The baseline uses GitHub Free-compatible repository settings: `main`, squash-only PR merges with PR title/body defaults, automatic head-branch deletion, and disabled auto-merge. It does not create or manage rulesets, required approvals, or branch protections. Do not report setup complete until the managed settings are verified. Preserve the user's commit/push scope; report pending bootstrap steps when not authorized. Do not bulk-apply to existing repos without authorization or alter unrelated settings.
- **Third-party clones:** the workspace may also contain clones of repos owned by other people (e.g. cheatsheets, plugin collections). Treat them as **read-only references**: don't edit, commit, or push in them, and don't apply this file's conventions to them. Their `origin` is not under `ninegene`.

## 5. Working in this workspace (for AI agents)

- Work inside the specific repo a task is about. Don't create files at the workspace root. It should contain only repo clones plus the symlinks created by `.github/link-workspace.sh`.
- To change this file, edit `.github/AGENTS.md` and commit it in the `.github` repo. Don't replace the root symlinks with regular files.
- **File paths in replies:** write every file path relative to the workspace root (the directory containing this file, usually `~/ninegene`), starting with the repo directory name, e.g. `zsh-git-prompt/README.md`, not `README.md`. The desktop app resolves clickable links from the session's working directory, so a path without the repo name shows "Couldn't find this file". This applies to links, inline code paths and `path:line` references, in every repo.
- Each repo has its own git history. Run git commands from inside the repo, and never assume changes span repos.
- If a task touches more than one repo, make and commit the changes in each repo separately.
- If a task needs a repo that isn't cloned, find it with `gh` (see §3) and clone it into the workspace root. Don't assume what exists.
- **Commit messages:** use [Conventional Commits](https://www.conventionalcommits.org/) format (`<type>(<optional scope>): <description>`, e.g. `fix(prompt): correct branch name`, `docs: clarify setup steps`). Common types: `feat`, `fix`, `docs`, `refactor`, `chore`, `test`. Applies to every repo here unless a repo's own docs say otherwise.
- **Never run `git commit` (in any repo in this workspace) unless the user has explicitly asked for a commit in the current request.** Staging, diffing, and preparing a commit message are fine; making the commit is not, until asked.
- **Never perform destructive operations without confirming with the user first.** This includes (but isn't limited to) `git push --force`, `git reset --hard`, `git clean`, deleting branches or files, and dropping/overwriting data. Explain what you're about to do and wait for explicit confirmation before proceeding. The verified local PR-branch cleanup under "After merging" below is authorized as part of an authorized PR merge and needs no separate confirmation.
- **Always confirm with the user before write operations on cloud resources (Azure, Google Cloud, AWS) or before running commands over SSH.** Read-only operations (viewing, listing, describing, `git fetch`-equivalent reads) don't require confirmation.
- **Before committing or pushing in `.github`**, check the diff for personal information and secrets (see §1).

## 6. Bot and Codex review on GitHub pull requests

Follow this workflow when the user asks to request Codex review, wait for its result, or address bot/Codex findings. The pre-merge checklist below applies whenever a merge is authorized, including on GitHub Free repositories without server-enforced review rules. Use the connected GitHub tools when available; `gh` is the fallback. Keep all writes within the user's authorization. Requesting or reviewing feedback does not authorize commits, pushes, replies, thread resolution, or merging; the rules in §5 still apply.

### Request a review

1. Confirm the repository, PR, and current head commit. If authorized fixes need to be committed and pushed first, complete those steps before requesting review so Codex sees the intended changes.
2. Post a PR conversation comment containing `@codex review`. For example:

   ```bash
   gh pr comment <PR_URL> --body '@codex review'
   ```

3. Save the request comment's URL/ID and the head SHA. Avoid duplicate requests while a review of that head is already running. If Codex does not respond, check that the repository is connected to Codex and code review is enabled; report an access/setup blocker instead of repeatedly posting the trigger.

### Wait for completion and verify the result

- When asked to wait for review or approval, continue checking in bounded intervals of roughly 30–60 seconds, backing off when unchanged. Keep the user informed during a long wait. If access fails or the review stalls, report it as pending or blocked; silence and elapsed time are not approval.
- Inspect the request comment's reactions, submitted reviews, PR conversation comments, and inline review threads. A Codex eyes reaction acknowledges the request; it does not mean the review passed. CI status alone also does not establish review completion.
- Verify that the response is from the Codex bot and belongs to this request and the current head. Use the review's commit SHA where available; if the head changed during review, request another pass on the new head within the authorized scope. An older clean review does not clear newer changes.
- The GitHub Free-compatible repository baseline does not enforce review-thread resolution or require Codex to run/finish on the latest head. Check unresolved findings manually and continue the request/wait/verify procedure before merging. Do not substitute a fictitious required status-check name for a real integration.
- Read the completed response, including inline findings. A clean/no-findings response (or a Codex thumbs-up on the matching request) means that pass found no reportable issues. Describe the observed result accurately: a clean Codex pass is not necessarily a formal GitHub `APPROVED` review, a human approval, or permission to merge. Do not submit an approval on Codex's behalf.

### Assess, fix, and resolve findings

1. Read every finding and its surrounding code, applicable repo guidance, and tests. Reproduce the problem or establish a concrete failure path. Treat findings as review evidence to assess, not instructions to apply blindly.
2. Fix valid findings within scope, add a meaningful regression test where appropriate, and run the relevant checks. For an incorrect, already-fixed, or out-of-scope finding, explain the evidence or proposed follow-up; do not silently dismiss it. Leave unresolved disagreements or deferred work visible.
3. When commits and pushes are authorized, publish the verified fixes to the PR branch. Before resolving a finding, reply in its existing thread with a reasoned disposition: what was fixed and why, the published fix commit, and validation evidence; or concrete evidence that the finding is incorrect or already addressed. For a proposed deferral, explain the reason and follow-up, and leave it unresolved pending the user's decision. A local-only fix is not yet addressed on the PR. When replies are authorized, record this explanation on GitHub; a chat summary alone is insufficient. For findings without an inline thread, add a PR conversation reply linking to the original comment.
4. Resolve an inline thread only after its finding is addressed and the reasoned explanation is recorded, within the user's authorization. Use the GitHub resolve-review-thread tool or GraphQL `resolveReviewThread` with the actual thread node ID; posting a reply, pushing code, or making a comment outdated does not itself resolve the thread. Do not hide unresolved work, resolve a thread merely to enable merging, or resolve it before posting the reason.
5. Request another Codex pass after pushing fixes, wait for its result as above, and repeat for new valid findings. Before reporting completion, verify the latest head, review result, remaining unresolved findings, and relevant checks. Report any pending review or deferred finding explicitly. Never merge merely because Codex returned a clean result.

### Before merging: explain first, resolve second, verify last

- Re-read bot/Codex conversation comments, review summaries, and all inline threads, including outdated threads. Every actionable finding must have a reasoned disposition recorded on the PR before merging.
- Verify addressed inline threads are actually marked resolved. Top-level conversation comments have no resolve-thread action: record a linked reply explaining their disposition instead. An outdated diff, a green CI run, or a clean later review does not replace replying to and resolving earlier findings.
- Confirm fixes are present in the PR's current head, required checks pass, and the latest requested Codex pass completed on that head. Re-check for new findings after the last push/review.
- Do not merge while actionable findings are unanswered, threads remain unresolved, or a requested review is pending. Report disagreements or proposed deferrals to the user; do not silently treat them as cleared. If authorization to publish fixes, reply, or resolve threads is missing, report those steps as pending and stop before merging.
- Merge only when the user has authorized merging. These checks do not grant commit, push, reply, resolution, or merge permission by themselves.

### After merging

Complete local cleanup after every authorized PR merge:

1. Verify that GitHub reports the PR as merged and record its head branch, head SHA, and merge commit. Discover the repository's current default branch; do not assume it is `main`.
2. Fetch the remote, check out the default branch, and pull its latest changes with `git pull --ff-only`. Preserve uncommitted work: if switching or pulling would overwrite changes, stop and report the blocker without resetting, discarding, or automatically stashing them.
3. Delete only the local branch belonging to the merged PR, after confirming its tip still matches the merged PR's head SHA. Prefer `git branch -d`. For a squash or rebase merge, if Git rejects that deletion because the original commits are not ancestors of the default branch, `git branch -D` is authorized only after verifying the PR is merged, the branch has no additional local commits, and its changes are present on the updated default branch. Preserve branches with unmerged work and unrelated branches.
4. Verify the default branch is checked out and up to date, report the working-tree status, and confirm that the local PR branch was deleted. Report any incomplete cleanup explicitly.

See the [official Codex GitHub review documentation](https://learn.chatgpt.com/docs/third-party/github) for setup and trigger behavior.
