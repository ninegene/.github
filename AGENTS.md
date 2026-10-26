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
- **New-repository settings:** follow [repo-settings/README.md](repo-settings/README.md) in this repo. After an authorized initial commit/push creates remote `main`, apply [repo-settings/repository.json](repo-settings/repository.json) and [repo-settings/default-branch.ruleset.json](repo-settings/default-branch.ruleset.json) using `python3 .github/scripts/repository-settings.py ninegene/<repo-name> --apply` from the workspace root, then run the command without `--apply` to verify. This requires squash-only PR merges with PR title/body defaults, zero approvals and no code-owner approval, resolved code-review threads, and default-branch force-push/deletion protection with no bypass actors. Do not report setup complete until the settings and active ruleset are verified. Preserve the user's commit/push scope; report pending bootstrap steps when not authorized. Report access/plan blockers rather than silently skipping protections or changing visibility. Do not bulk-apply to existing repos or alter unrelated rulesets.
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
- **Never perform destructive operations without confirming with the user first.** This includes (but isn't limited to) `git push --force`, `git reset --hard`, `git clean`, deleting branches or files, and dropping/overwriting data. Explain what you're about to do and wait for explicit confirmation before proceeding.
- **Always confirm with the user before write operations on cloud resources (Azure, Google Cloud, AWS) or before running commands over SSH.** Read-only operations (viewing, listing, describing, `git fetch`-equivalent reads) don't require confirmation.
- **Before committing or pushing in `.github`**, check the diff for personal information and secrets (see §1).

## 6. Codex review on GitHub pull requests

Follow this workflow when the user asks to request Codex review, wait for its result, or address its findings. Use the connected GitHub tools when available; `gh` is the fallback. Keep all writes within the user's authorization. Requesting review does not authorize commits, pushes, or merging; the rules in §5 still apply.

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
- The new-repository ruleset blocks unresolved inline review threads, including Codex findings. It does not block ordinary PR conversation comments or require Codex to run/finish on the latest head; continue the request/wait/verify procedure. Do not substitute a fictitious required status-check name for a real integration.
- Read the completed response, including inline findings. A clean/no-findings response (or a Codex thumbs-up on the matching request) means that pass found no reportable issues. Describe the observed result accurately: a clean Codex pass is not necessarily a formal GitHub `APPROVED` review, a human approval, or permission to merge. Do not submit an approval on Codex's behalf.

### Assess, fix, and resolve findings

1. Read every finding and its surrounding code, applicable repo guidance, and tests. Reproduce the problem or establish a concrete failure path. Treat findings as review evidence to assess, not instructions to apply blindly.
2. Fix valid findings within scope, add a meaningful regression test where appropriate, and run the relevant checks. For an incorrect, already-fixed, or out-of-scope finding, explain the evidence or proposed follow-up; do not silently dismiss it. Leave unresolved disagreements or deferred work visible.
3. When commits and pushes are authorized, publish the verified fixes to the PR branch. When replies are authorized, reply in each finding's existing thread with the disposition, fix commit, and validation evidence. A PR conversation reply is appropriate for findings without an inline thread.
4. Resolve an inline thread only after its finding is addressed and the explanation is recorded, within the user's authorization. Use the GitHub resolve-review-thread tool or GraphQL `resolveReviewThread` with the actual thread node ID; posting a reply, pushing code, or making a comment outdated does not itself resolve the thread. Do not hide unresolved work by resolving it prematurely.
5. Request another Codex pass after pushing fixes, wait for its result as above, and repeat for new valid findings. Before reporting completion, verify the latest head, review result, remaining unresolved findings, and relevant checks. Report any pending review or deferred finding explicitly. Never merge merely because Codex returned a clean result.

See the [official Codex GitHub review documentation](https://learn.chatgpt.com/docs/third-party/github) for setup and trigger behavior.
