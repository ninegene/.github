# ninegene/.github

Shared AI-agent context and the **starting point for developer setup** for the repos under the [ninegene](https://github.com/ninegene) GitHub account.

> **This repo is public.** Don't commit personal information or secrets here.

- [AGENTS.md](AGENTS.md): context for AI coding agents about the local workspace (`CLAUDE.md` is a symlink to it)
- [.agent/skills/](.agent/skills/): shared workspace skills, including [GitHub Wiki maintenance](.agent/skills/github-wiki/SKILL.md)
- [link-workspace.sh](link-workspace.sh): sets up the local workspace (symlinks into the workspace root)
- [bootstrap-dev-env.sh](bootstrap-dev-env.sh): installs the shared developer tools (macOS only for now)
- [ninegene.code-workspace](ninegene.code-workspace): shared VS Code workspace settings and tasks
- [.editorconfig](.editorconfig): shared indentation, line-ending and column settings for Markdown and shell scripts
- [.markdownlint.json](.markdownlint.json): shared markdownlint rules (long lines allowed)
- [.vscode/extensions.json](.vscode/extensions.json): VS Code extensions, all installed by `bootstrap-dev-env.sh`

## Languages

The languages I work with most often are **Bash**, **JavaScript/TypeScript** and **Python**. **Go** and **Elixir/Erlang** come up on some projects. I also use **Java, Kotlin and Groovy**, but mostly at work, not in personal projects, so nothing here is set up for them.

I also have experience with **Terraform** for provisioning cloud resources on **AWS, Azure and Google Cloud**, for both work and personal projects.

The shared workspace file configures formatting, linting and type checking for each language:

| Language | Format | Lint / type check |
| --- | --- | --- |
| Bash | shfmt | ShellCheck |
| JavaScript / TypeScript | Prettier (only where a repo has a Prettier config) | ESLint, TypeScript |
| Python (managed with uv) | Ruff | Ruff, Pyright |
| Go | gofmt (golang.go) | gopls with staticcheck |
| Elixir / Erlang | `mix format` (ElixirLS) | ElixirLS with Dialyzer, erlang-ls |
| Terraform | `terraform fmt` (HashiCorp Terraform extension) | Terraform language server, validate on save |

## Developer setup

Do these steps once, in order.

### 1. Install tools

**Required:** [Git](https://git-scm.com/downloads), [GitHub CLI (`gh`)](https://cli.github.com/)
**Recommended:** [Visual Studio Code](https://code.visualstudio.com/download), [Claude desktop app](https://claude.com/download)

### 2. Set up the workspace

All repos are cloned side by side under one **workspace root**, recommended `~/ninegene`. The root itself is not a git repo. It holds this `.github` clone and the other repo clones.

```bash
WORKSPACE=~/ninegene
mkdir -p "$WORKSPACE" && cd "$WORKSPACE"
gh auth login          # if not already logged in
gh repo clone ninegene/.github
./.github/link-workspace.sh
```

`link-workspace.sh` creates these symlinks in the workspace root and is safe to run more than once:

```
<workspace>/
├── .github/                          # this repo
├── .editorconfig -> .github/.editorconfig
├── .markdownlint.json -> .github/.markdownlint.json
├── .vscode/extensions.json -> ../.github/.vscode/extensions.json
├── ninegene.code-workspace -> .github/ninegene.code-workspace
├── AGENTS.md -> .github/AGENTS.md
├── CLAUDE.md -> AGENTS.md
├── .agent/skills/github-wiki -> ../../.github/.agent/skills/github-wiki
├── .agents/skills/github-wiki -> ../../.github/.agent/skills/github-wiki
├── .claude/skills/github-wiki -> ../../.github/.agent/skills/github-wiki
└── <repo-name>/                      # other repos, cloned as needed
```

Skills are maintained once in `.github/.agent/skills/<name>/`. The script creates a per-skill link in the workspace's `.agent/skills/`, plus the discovery locations used by [Codex](https://developers.openai.com/codex/skills), [GitHub Copilot](https://docs.github.com/en/copilot/reference/customization-cheat-sheet) (`.agents/skills/`), and [Claude](https://code.claude.com/docs/en/skills) (`.claude/skills/`). Re-run it after adding a shared skill. Existing conflicting paths are skipped and reported instead of overwritten.

#### Open the workspace in VS Code

Open the link in the **workspace root**, not the copy inside `.github/` (otherwise `.github` becomes the root and the tasks fail):

```bash
code "$WORKSPACE/ninegene.code-workspace"
```

### 3. Clone the repos you need

Always clone from the workspace root:

```bash
cd "$WORKSPACE"
gh repo list ninegene --limit 100          # see what exists
gh repo clone ninegene/<repo-name>         # clone one repo
```

### 4. Install the shared dev tools

Run once per machine, from the workspace root:

```bash
./.github/bootstrap-dev-env.sh
```

Safe to re-run. On **macOS** it installs Xcode Command Line Tools, Homebrew, `git`, `curl`, `gh`, `shellcheck`, `shfmt`, [uv](https://docs.astral.sh/uv/) (Python versions, virtualenvs and dependencies), Go, Elixir (with Erlang), Terraform (from the `hashicorp/tap` tap, since Homebrew core no longer ships it), AWS CLI, Azure CLI, Google Cloud CLI, VS Code, Claude Code, Codex CLI, [Antigravity CLI](https://antigravity.google/docs/cli/) (`brew install --cask antigravity-cli`), **every extension listed in [.vscode/extensions.json](.vscode/extensions.json)** and [nvm](https://github.com/nvm-sh/nvm). To add or drop an extension, edit that file. Tools already on `PATH` are skipped. If a tool fails, the script keeps going and lists failures with a manual fix at the end. Other operating systems are not supported yet. After it finishes, sign in with `gh auth login`, `claude`, `codex`, `agy`, `aws configure sso`, `az login` and `gcloud auth login`.

It does **not** set up any individual repo. Each repo documents its own setup in its `README.md` / `AGENTS.md`.

## Editing AGENTS.md

Edit `.github/AGENTS.md` (the workspace-root `AGENTS.md` is a symlink to it), then commit and push from inside `.github/`. Other machines get the update with `git -C .github pull`.
