---
name: github-wiki
description: Create or update GitHub Wiki pages in the ninegene/.github.wiki clone, maintain page metadata and category navigation, and resolve wiki page URLs. Use for this wiki's pages or navigation, not ordinary repository Markdown or ChatGPT Pages.
---

# GitHub Wiki

Maintain the public wiki at <https://github.com/ninegene/.github/wiki> through the separate `.github.wiki` Git clone under the workspace root.

## Repository and synchronization

- Read the workspace `.github/AGENTS.md` and any existing wiki-specific instructions before editing. If the clone is missing, clone `ninegene/.github.wiki` into the workspace root. Do not put pages in the main `.github` repository.
- Inspect status, remote, branch, existing pages, and navigation. The known default branch is `master`; verify it with the remote before publication rather than assuming `main`.
- Browser edits create wiki commits. Fetch to check for them; on a clean default-branch checkout, use a fast-forward-only pull before editing. With local changes or divergence, preserve the work and reconcile changes without resetting or overwriting it.
- Wiki Markdown files become pages. Do not create `AGENTS.md`, `CLAUDE.md`, or a skill file in the wiki just to supply agent instructions.
- Keep public content generic; exclude secrets, personal details, and private repository details. Prepare local edits unless the user requests publication. Commit only when explicitly requested in the current request; browser Save Page also commits and publishes. Follow workspace restrictions for SSH and destructive operations.

## Page format

Use root-level `.md` files and GitHub Flavored Markdown. Prefer clear, portable names such as `GitHub-Wiki-Guide.md`; avoid `\ / : * ? " < > |`, reserved navigation names, and punctuation-heavy new names. Preserve existing filenames and links unless a rename is requested.

Start each content page, including `Home.md`, with this YAML schema:

```yaml
---
date_created: '2026-10-04'
last_updated: '2026-10-04'
category: Documentation
tags: [github, wiki]
---
```

- Use the user's current local date in `yyyy-MM-dd` format; example dates above are illustrative. Set both dates on initial creation. On every page edit, refresh `last_updated` and preserve `date_created`.
- When adding metadata to an existing page, recover its creation date from the earliest Git history for that page (including prior names when relevant). If unavailable, ask for the missing date instead of inventing it.
- Use one meaningful `category` and a YAML list of concise `tags`. Reassess both against the resulting content on each edit; reuse suitable existing names rather than creating synonymous categories.
- Follow the frontmatter with a title, a short summary, and an explicit `## Table of contents` containing Markdown links to the page's sections. Keep links synchronized with headings, including GitHub's suffixes for repeated headings. Do not use MediaWiki `__TOC__` or assume frontmatter creates navigation automatically.
- Frontmatter is a local metadata convention, not a wiki taxonomy engine. Keep the actual navigation in Markdown.

## Category navigation

After creating a page or changing its title, summary, or category, reconcile both navigation files against all actual content pages:

- `Home.md`: a complete directory with category headings and one linked entry plus a short, content-based description for every content page. Home can link to itself under Overview. Exclude `_Sidebar.md`, `_Footer.md`, assets, and agent instruction files from ordinary page listings.
- `_Sidebar.md`: a Home link first, then the same category headings with compact page links. Include every other content page once under its current category; order categories and titles consistently. Avoid empty categories.
- Keep sidebar/footer content compact; they are layout fragments, exempt from page frontmatter and table-of-contents requirements. Create `_Footer.md` only when requested or already needed by the wiki.
- Preserve unrelated content and existing custom navigation. Refresh Home's metadata and TOC when editing its directory.

## Links and page URLs

Use descriptive Markdown links to the actual GitHub repository, file, code lines, or commit whenever those resources are referenced. Resolve remotes and refs before linking; do not invent a branch or SHA. Use `/blob/<ref>/<path>#L<n>` for files/lines and `/commit/<sha>` for commits; prefer a full commit SHA for version-specific evidence. Local filesystem paths belong in agent reports, not as substitutes for GitHub links in wiki prose.

For wiki links or a request for a page URL, read [references/github-wiki.md](references/github-wiki.md). The helper `scripts/wiki_url.py` constructs a candidate from a filename or encodes a verified slug. It does not discover GitHub's canonical URL. For unusual existing names, copy the actual link from GitHub's wiki page list or browser and confirm it resolves to the intended page. Distinguish an unpublished page's expected URL from a verified live URL.

## Verification and handoff

Check the edited pages' metadata, creation dates, TOC anchors, and GitHub links. Compare Home and sidebar entries with the content-page inventory so no page is missing, duplicated, or filed under an outdated category. Review diffs independently in each affected repository. Report the local changes and publication state accurately; do not claim pages are live before authorized publication succeeds.
