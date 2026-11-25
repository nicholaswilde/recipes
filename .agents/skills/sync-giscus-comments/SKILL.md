---
name: sync-giscus-comments
description: >-
  Sync Giscus GitHub Discussions comments with recipe pages (`comments: true` frontmatter) and
  triage new cooking notes using `scripts/sync_giscus_comments.py`. Trigger: /sync-giscus-comments,
  'sync giscus comments', 'triage giscus comments', 'sync giscus'.
---

# Sync Giscus Comments

Sync GitHub Discussions in the `Comments` category with local recipe Markdown/Cooklang files and
triage actionable cooking notes using `scripts/sync_giscus_comments.py`.

## Prerequisites

- `mdfm` CLI installed (`brew install nicholaswilde/homebrew-tap/mdfm`) — used for `comments: true` and `must-try` -> `favorite` frontmatter mutations.
- Authenticated GitHub CLI (`gh auth status`) with access to `discussions: read` (and
  `issues: write` / `pull-requests: write` / `contents: write` when triaging).
- Clean working tree on `main` (or target `--base-branch`) before running `--triage` in `auto`
  or `pr` mode, as the script creates and checks out `giscus-triage/discussion-<N>` branches.

## Protocol

### 1. Sync `comments: true` Frontmatter (Default Mode)

Run without `--triage` or `--seed-state` to match `Comments` discussions to `docs/**/*.md` and
insert `comments: true` into YAML frontmatter where missing:

```bash
rtk uv run scripts/sync_giscus_comments.py
```

Review any reported `modified_files` and unmatched discussion titles.

### 2. Preview Cooking Note Triage (`--dry-run`)

Before mutating files, creating branches, or opening PRs/issues, preview detected cooking notes:

```bash
rtk uv run scripts/sync_giscus_comments.py --triage --dry-run
```

The script filters out bots and trivial chat (e.g., `"thanks"`, `"looks great"`), treats owner
comments and comments with cooking signals (measurements, times, temperatures, technique verbs)
as actionable notes, and skips IDs already recorded in `.github/giscus_triage_state.json` or
embedded in existing issue/PR `<!-- giscus-comment-id: ... -->` markers.

### 3. Run Cooking Note Triage (`--triage`)

Choose the triage mode (`auto` is default):

- **`auto` (PR with issue fallback):** Stages `comments: true`, promotes `must-try` to `favorite`
  when an owner note is present, appends `[-- Giscus cooking note (@author, date, id): ... --]`
  to the matching `.cook` file, validates Cooklang syntax, updates
  `.github/giscus_triage_state.json`, pushes `giscus-triage/discussion-<N>`, and opens a PR
  (falls back to an `enhancement` issue if no file edits were produced or PR creation fails):

  ```bash
  rtk uv run scripts/sync_giscus_comments.py --triage --mode auto
  ```

- **`pr`:** Opens triage PRs only when file changes are produced:

  ```bash
  rtk uv run scripts/sync_giscus_comments.py --triage --mode pr
  ```

- **`issue`:** Opens `[Giscus]: Fold cooking notes into <Recipe>` issues without modifying local
  files or creating branches:

  ```bash
  rtk uv run scripts/sync_giscus_comments.py --triage --mode issue
  ```

Optional flags:

- `--base-branch <branch>`: Base branch for triage PRs (default: `main`).
- `--state-file <path>`: Processed-comment JSON state file (default: `.github/giscus_triage_state.json`).
- `--owner <owner>` / `--repo <repo>`: Override GitHub owner/repo (defaults to `$GITHUB_REPOSITORY` or `nicholaswilde/recipes`).

### 4. Seed State Only (`--seed-state`)

To record all existing `Comments` discussion comment/reply IDs in `.github/giscus_triage_state.json`
without opening PRs or issues:

```bash
rtk uv run scripts/sync_giscus_comments.py --seed-state
```

### 5. Verify & Follow Up

- If frontmatter was modified locally in Step 1:

  ```bash
  task lint-changed
  task validate
  ```

- When folding staged `[-- Giscus cooking note ... --]` comments from a triage PR/issue into
  inline Cooklang steps:

  ```bash
  task validate-cook FILE="<path/to/recipe.cook>"
  FILES="<path/to/recipe.cook>" task move
  ```

- Automated CI runs daily at `09:00 UTC` and on manual dispatch via
  `.github/workflows/giscus-triage.yaml`.
