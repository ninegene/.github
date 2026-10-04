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
- **Visibility:** choose per repo. Anything with credentials, personal data, or private notes is **private**. Never commit secrets. Use env vars or local config files listed in `.gitignore`.
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
