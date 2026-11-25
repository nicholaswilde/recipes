#!/usr/bin/env python3

################################################################################
#
# sync_giscus_comments.py
# ----------------
# Sync Giscus comments with recipe pages and triage cooking notes
#
# @author nιcнolaѕ wιlde, 0x08b7d7a3
# @date 01 Jun 2026
# @version 0.2.0
#
################################################################################

import argparse
import json
import os
import re
import shutil
import subprocess
import tempfile
import unicodedata
import urllib.parse
from datetime import datetime, timezone

import yaml

DEFAULT_OWNER = "nicholaswilde"
DEFAULT_REPO = "recipes"
DEFAULT_STATE_FILE = ".github/giscus_triage_state.json"
COMMENT_ID_MARKER_RE = re.compile(r"<!--\s*giscus-comment-id:\s*(DC_[^\s>]+)\s*-->")

TRIVIAL_CHAT_RE = re.compile(
    r"^\s*(?:"
    r"thanks?(?:\s+(?:you|so\s+much|a\s+lot|for\s+(?:the\s+)?recip[ey]|for\s+sharing))?"
    r"|no\s+problem"
    r"|you(?:'|’)?re\s+welcome"
    r"|looks\s+(?:great|good|delicious|amazing|yummy)"
    r"|yum+"
    r"|awesome|delicious|great\s+recip[ey]|love\s+(?:this|it)"
    r")[!.\s]*$",
    re.IGNORECASE,
)

COOKING_SIGNAL_RE = re.compile(
    r"(?:"
    r"\b\d+(?:[./]\d+)?\s*(?:cups?|tbsp|tsp|tablespoons?|teaspoons?|grams?|g|kg|oz|ounces?|lbs?|pounds?|ml|l|mins?|minutes?|hours?|hrs?|days?|degrees?|°[fc]|f|c|%)\b"
    r"|^\s*(?:[-*]|\d+\.)\s+"
    r"|\b(?:add|use|try|sub|substitute|replace|swap|omit|reduce|increase|double|halve|bake|roast|cook|simmer|boil|proof|chill|fold|zest|glaze|toast|score|grease|preheat|missing|step|ratio|variation|instead|adjust)\b"
    r")",
    re.IGNORECASE | re.MULTILINE,
)


def get_repo_owner_name(owner=None, repo=None):
    """Resolve GitHub owner and repository name from args or environment."""
    env_repo = os.environ.get("GITHUB_REPOSITORY", "")
    env_owner, env_name = (
        env_repo.split("/", 1) if "/" in env_repo else (DEFAULT_OWNER, DEFAULT_REPO)
    )
    return owner or env_owner, repo or env_name


def _gh_env():
    """Return environment dict with GH_NOPAGER disabled."""
    env = os.environ.copy()
    env["GH_NOPAGER"] = "1"
    return env


def fetch_discussions(owner=DEFAULT_OWNER, repo=DEFAULT_REPO):
    """Fetch GitHub Discussions with comments and replies via GraphQL."""
    query = """
    query($owner: String!, $name: String!, $cursor: String) {
      repository(owner: $owner, name: $name) {
        discussions(first: 50, after: $cursor) {
          pageInfo {
            hasNextPage
            endCursor
          }
          nodes {
            id
            number
            title
            url
            category {
              name
            }
            comments(first: 50) {
              nodes {
                id
                url
                author {
                  login
                }
                body
                createdAt
                updatedAt
                replies(first: 20) {
                  nodes {
                    id
                    url
                    author {
                      login
                    }
                    body
                    createdAt
                    updatedAt
                  }
                }
              }
            }
          }
        }
      }
    }
    """

    discussions = []
    has_next_page = True
    cursor = None

    while has_next_page:
        cmd = [
            "gh",
            "api",
            "graphql",
            "-F",
            f"owner={owner}",
            "-F",
            f"name={repo}",
            "-F",
            f"cursor={cursor}" if cursor else "cursor=null",
            "-f",
            f"query={query}",
        ]

        result = subprocess.run(cmd, env=_gh_env(), capture_output=True, text=True)
        if result.returncode != 0:
            print("Error running gh api:", result.stderr)
            break

        try:
            data = json.loads(result.stdout)
            repository = data.get("data", {}).get("repository", {})
            disc_data = repository.get("discussions", {})
            nodes = disc_data.get("nodes", [])
            discussions.extend(nodes)

            page_info = disc_data.get("pageInfo", {})
            has_next_page = page_info.get("hasNextPage", False)
            cursor = page_info.get("endCursor", None)
        except Exception as exc:
            print("Failed to parse response:", exc)
            print("Raw response:", result.stdout)
            break

    return discussions


def clean_pathname(title):
    """Normalize a Giscus discussion pathname title into a relative doc path."""
    title_decoded = urllib.parse.unquote(title)
    clean = title_decoded.strip("/")

    if clean.startswith("recipes/"):
        clean = clean[len("recipes/") :]
    elif clean.startswith("recipes"):
        clean = clean[len("recipes") :]

    return clean.strip("/")


def normalize_slug(name):
    """Normalize a filename or title into a lowercase hyphenated slug."""
    decoded = urllib.parse.unquote(name)
    ascii_text = (
        unicodedata.normalize("NFKD", decoded)
        .encode("ascii", "ignore")
        .decode("ascii")
    )
    ascii_text = ascii_text.replace("'", "").replace("\u2019", "")
    return re.sub(r"[^a-z0-9]+", "-", ascii_text.lower()).strip("-")


def add_comments_to_file(filepath):
    """Ensure `comments: true` exists in a markdown file's YAML frontmatter."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    lines = content.splitlines()
    has_front_matter = False
    front_matter_end_idx = -1

    if len(lines) > 0 and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                has_front_matter = True
                front_matter_end_idx = i
                break

    if has_front_matter:
        front_matter_lines = lines[1:front_matter_end_idx]
        for line in front_matter_lines:
            if re.match(
                r'^\s*comments\s*:\s*[\'"]?true[\'"]?\s*$', line, re.IGNORECASE
            ):
                return False

        lines.insert(front_matter_end_idx, "comments: true")
        new_content = "\n".join(lines) + ("\n" if content.endswith("\n") else "")
    else:
        new_content = "---\ncomments: true\n---\n" + content

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_content)

    return True


def build_docs_file_map(docs_dir="docs"):
    """Map lowercase markdown basenames (without extension) to file paths."""
    file_map = {}
    if not os.path.isdir(docs_dir):
        return file_map
    for root, _, files in os.walk(docs_dir):
        for file in sorted(files):
            if file.endswith(".md"):
                basename_no_ext = os.path.splitext(file)[0].lower()
                file_map[basename_no_ext] = os.path.join(root, file)
    return file_map


def find_docs_file(rel_path, docs_dir="docs", docs_file_map=None):
    """Resolve a discussion relative path to a local markdown file under docs/."""
    if not rel_path:
        return None

    candidates = [
        os.path.join(docs_dir, rel_path + ".md"),
        os.path.join(docs_dir, rel_path, "index.md"),
    ]
    for candidate in candidates:
        if os.path.exists(candidate):
            return candidate

    if docs_file_map is None:
        docs_file_map = build_docs_file_map(docs_dir)

    basename_comp = os.path.basename(rel_path.strip("/")).lower()
    if basename_comp in docs_file_map:
        return docs_file_map[basename_comp]

    target_slug = normalize_slug(basename_comp)
    for key, path in docs_file_map.items():
        if normalize_slug(key) == target_slug:
            return path
    return None


def build_cook_file_map(cook_dir="cook"):
    """Map normalized recipe slugs to lists of `.cook` file paths."""
    cook_map = {}
    if not os.path.isdir(cook_dir):
        return cook_map
    for root, _, files in os.walk(cook_dir):
        for file in sorted(files):
            if file.endswith(".cook"):
                slug = normalize_slug(os.path.splitext(file)[0])
                cook_map.setdefault(slug, []).append(os.path.join(root, file))
    return cook_map


def find_cook_file(rel_path, md_path=None, cook_dir="cook", cook_file_map=None):
    """Find the source `.cook` file corresponding to a discussion or `.md` file."""
    if cook_file_map is None:
        cook_file_map = build_cook_file_map(cook_dir)

    slug = ""
    if rel_path:
        slug = normalize_slug(os.path.basename(rel_path.strip("/")))
    if not slug and md_path:
        slug = normalize_slug(os.path.splitext(os.path.basename(md_path))[0])
    if not slug:
        return None

    matches = cook_file_map.get(slug, [])
    if not matches and md_path:
        md_slug = normalize_slug(os.path.splitext(os.path.basename(md_path))[0])
        matches = cook_file_map.get(md_slug, [])
    if not matches:
        return None
    if len(matches) == 1:
        return matches[0]

    # Prefer matching top-level category directory when multiple recipes share a slug.
    category = ""
    if rel_path and "/" in rel_path:
        category = rel_path.split("/", 1)[0].lower()
    elif md_path:
        parts = os.path.normpath(md_path).split(os.sep)
        if "docs" in parts:
            idx = parts.index("docs")
            if idx + 1 < len(parts) - 1:
                category = parts[idx + 1].lower()
        elif len(parts) >= 3:
            category = parts[1].lower()

    if category:
        for path in matches:
            rel_cook = os.path.relpath(path, cook_dir)
            parts = rel_cook.split(os.sep)
            if len(parts) >= 2 and parts[0].lower() == category:
                return path

    return matches[0]


def _find_frontmatter_bounds(lines):
    """Return `(start_idx, end_idx)` of YAML frontmatter or `None` if absent."""
    if len(lines) < 2 or lines[0].strip() != "---":
        return None
    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            return (0, idx)
    return None


def _promote_tags_in_frontmatter_lines(
    lines, fm_end_idx, add_favorite_if_missing=False
):
    """Promote `must-try` to `favorite` in YAML frontmatter lines.

    Args:
        lines: Full file split into lines.
        fm_end_idx: Index of closing `---` line.
        add_favorite_if_missing: Add `favorite` tag if `must-try` was absent.

    Returns:
        Tuple of `(updated_lines, changed)`.
    """
    fm_text = "\n".join(lines[1:fm_end_idx])
    try:
        fm_data = yaml.safe_load(fm_text) or {}
    except yaml.YAMLError:
        return lines, False

    if not isinstance(fm_data, dict):
        return lines, False

    tags = fm_data.get("tags")
    if isinstance(tags, str):
        tags_list = [tags]
    elif isinstance(tags, list):
        tags_list = [str(t).strip() for t in tags if t is not None]
    else:
        tags_list = []

    has_must_try = "must-try" in tags_list
    has_favorite = "favorite" in tags_list

    if not has_must_try and not (add_favorite_if_missing and not has_favorite):
        return lines, False

    new_lines = list(lines)

    if has_must_try:
        # Handle inline flow list: `tags: [a, must-try]`
        inline_updated = False
        for i in range(1, fm_end_idx):
            m = re.match(r"^(\s*tags\s*:\s*)\[(.*)\]\s*$", new_lines[i])
            if m:
                items = [
                    x.strip().strip("'\"")
                    for x in m.group(2).split(",")
                    if x.strip()
                ]
                updated_items = []
                for item in items:
                    if item == "must-try":
                        if not has_favorite and "favorite" not in updated_items:
                            updated_items.append("favorite")
                    else:
                        updated_items.append(item)
                new_lines[i] = f"{m.group(1)}[{', '.join(updated_items)}]"
                inline_updated = True
                break

        if not inline_updated:
            # Handle block list items: `  - must-try` or `- must-try`
            out_fm = []
            replaced = False
            for i in range(1, fm_end_idx):
                line = new_lines[i]
                item_match = re.match(
                    r"^(\s*-\s*)['\"]?must-try['\"]?\s*(#.*)?$", line
                )
                if item_match:
                    replaced = True
                    if not has_favorite:
                        comment = f" {item_match.group(2)}" if item_match.group(2) else ""
                        out_fm.append(f"{item_match.group(1)}favorite{comment}")
                    # If favorite already exists, drop the duplicate must-try entry.
                else:
                    out_fm.append(line)
            if not replaced:
                return lines, False
            new_lines = [new_lines[0]] + out_fm + new_lines[fm_end_idx:]
        return new_lines, True

    # add_favorite_if_missing is True and neither tag is present
    tags_key_idx = None
    insert_idx = fm_end_idx
    for i in range(1, fm_end_idx):
        if re.match(r"^\s*tags\s*:", new_lines[i]):
            tags_key_idx = i
            j = i + 1
            while j < fm_end_idx and (
                re.match(r"^\s*-\s+", new_lines[j]) or not new_lines[j].strip()
            ):
                if re.match(r"^\s*-\s+", new_lines[j]):
                    insert_idx = j + 1
                j += 1
            if insert_idx == fm_end_idx and j <= fm_end_idx:
                insert_idx = i + 1
            break

    if tags_key_idx is not None:
        m = re.match(r"^(\s*tags\s*:\s*)\[(.*)\]\s*$", new_lines[tags_key_idx])
        if m:
            existing = [x.strip() for x in m.group(2).split(",") if x.strip()]
            existing.append("favorite")
            new_lines[tags_key_idx] = f"{m.group(1)}[{', '.join(existing)}]"
        else:
            if re.match(r"^\s*tags\s*:\s*\S+", new_lines[tags_key_idx]):
                # Single scalar tag like `tags: breakfast`
                scalar = new_lines[tags_key_idx].split(":", 1)[1].strip()
                new_lines[tags_key_idx : tags_key_idx + 1] = [
                    "tags:",
                    f"  - {scalar}",
                    "  - favorite",
                ]
            else:
                new_lines[tags_key_idx] = "tags:"
                new_lines.insert(insert_idx, "  - favorite")
    else:
        new_lines.insert(fm_end_idx, "  - favorite")
        new_lines.insert(fm_end_idx, "tags:")

    return new_lines, True


def promote_tags_in_markdown(filepath):
    """Promote `must-try` to `favorite` in a markdown file's frontmatter."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    lines = content.splitlines()
    bounds = _find_frontmatter_bounds(lines)
    if bounds is None:
        return False

    new_lines, changed = _promote_tags_in_frontmatter_lines(lines, bounds[1])
    if not changed:
        return False

    new_content = "\n".join(new_lines) + ("\n" if content.endswith("\n") else "")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_content)
    return True


def promote_tags_in_cook_content(content, add_favorite_if_missing=False):
    """Promote `must-try` to `favorite` in `.cook` YAML or `>>` metadata."""
    lines = content.splitlines()
    bounds = _find_frontmatter_bounds(lines)
    trailing_nl = "\n" if content.endswith("\n") else ""

    if bounds is not None:
        new_lines, changed = _promote_tags_in_frontmatter_lines(
            lines, bounds[1], add_favorite_if_missing=add_favorite_if_missing
        )
        if not changed:
            return content, False
        return "\n".join(new_lines) + trailing_nl, True

    # Handle legacy `>> tags:` metadata lines
    tag_line_indices = [
        i for i, line in enumerate(lines) if re.match(r"^\s*>>\s*tags\s*:", line)
    ]

    if tag_line_indices:
        changed = False
        has_favorite = any(
            "favorite"
            in [
                t.strip()
                for t in lines[i].split(":", 1)[1].split(",")
                if t.strip()
            ]
            for i in tag_line_indices
        )
        new_lines = list(lines)
        for idx in tag_line_indices:
            prefix, raw_tags = new_lines[idx].split(":", 1)
            tags = [t.strip() for t in raw_tags.split(",") if t.strip()]
            if "must-try" in tags:
                updated = []
                for t in tags:
                    if t == "must-try":
                        if not has_favorite and "favorite" not in updated:
                            updated.append("favorite")
                            has_favorite = True
                    else:
                        updated.append(t)
                new_lines[idx] = f"{prefix}: {', '.join(updated)}"
                changed = True

        if not changed and add_favorite_if_missing and not has_favorite:
            idx = tag_line_indices[0]
            prefix, raw_tags = new_lines[idx].split(":", 1)
            tags = [t.strip() for t in raw_tags.split(",") if t.strip()]
            tags.append("favorite")
            new_lines[idx] = f"{prefix}: {', '.join(tags)}"
            changed = True

        if not changed:
            return content, False
        return "\n".join(new_lines) + trailing_nl, True

    if not add_favorite_if_missing:
        return content, False

    meta_indices = [
        i for i, line in enumerate(lines) if re.match(r"^\s*>>\s*[^:]+:", line)
    ]
    if meta_indices:
        new_lines = list(lines)
        new_lines.insert(meta_indices[-1] + 1, ">> tags: favorite")
        return "\n".join(new_lines) + trailing_nl, True

    # No metadata header at all: add standard YAML frontmatter
    new_content = "---\ntags:\n  - favorite\n---\n\n" + content.lstrip("\n")
    return new_content, True


def _sanitize_cooklang_comment(text):
    """Prevent accidental termination of `[-- ... --]` Cooklang block comments."""
    return text.replace("[--", "[- -").replace("--]", "- -]").strip()


def append_cooking_notes_to_cook_content(content, notes):
    """Append staged Giscus cooking notes as Cooklang block comments.

    Returns:
        Tuple of `(updated_content, notes_added_count)`.
    """
    blocks = []
    for note in notes:
        note_id = note["id"]
        if note_id in content:
            continue
        author = note.get("author") or "unknown"
        date_str = (note.get("createdAt") or "")[:10] or "unknown-date"
        body = _sanitize_cooklang_comment(note.get("body") or "")
        if not body:
            continue
        if "\n" in body:
            blocks.append(
                f"[-- Giscus cooking note (@{author}, {date_str}, {note_id}):\n{body} --]"
            )
        else:
            blocks.append(
                f"[-- Giscus cooking note (@{author}, {date_str}, {note_id}): {body} --]"
            )

    if not blocks:
        return content, 0

    stripped = content.rstrip()
    joined = "\n\n".join(blocks)
    return f"{stripped}\n\n{joined}\n", len(blocks)


def update_cook_file(cook_path, notes, promote_favorite=False):
    """Update a `.cook` file with promoted tags and staged cooking notes."""
    with open(cook_path, "r", encoding="utf-8") as f:
        original = f.read()

    updated, promoted = promote_tags_in_cook_content(
        original, add_favorite_if_missing=promote_favorite
    )
    updated, notes_added = append_cooking_notes_to_cook_content(updated, notes)

    if updated != original:
        with open(cook_path, "w", encoding="utf-8") as f:
            f.write(updated)

    return {
        "changed": updated != original,
        "promoted": promoted,
        "notes_added": notes_added,
    }


def extract_comments_from_discussion(discussion):
    """Flatten top-level comments and replies from a discussion chronologically."""
    extracted = []
    comments_conn = discussion.get("comments") or {}
    for node in comments_conn.get("nodes") or []:
        if not node:
            continue
        author_obj = node.get("author") or {}
        extracted.append(
            {
                "id": node.get("id", ""),
                "url": node.get("url", ""),
                "author": author_obj.get("login", "") if author_obj else "",
                "body": node.get("body", ""),
                "createdAt": node.get("createdAt", ""),
                "updatedAt": node.get("updatedAt", ""),
                "is_reply": False,
            }
        )
        replies_conn = node.get("replies") or {}
        for reply in replies_conn.get("nodes") or []:
            if not reply:
                continue
            r_author = reply.get("author") or {}
            extracted.append(
                {
                    "id": reply.get("id", ""),
                    "url": reply.get("url", ""),
                    "author": r_author.get("login", "") if r_author else "",
                    "body": reply.get("body", ""),
                    "createdAt": reply.get("createdAt", ""),
                    "updatedAt": reply.get("updatedAt", ""),
                    "is_reply": True,
                }
            )
    extracted.sort(key=lambda item: item.get("createdAt") or "")
    return extracted


def is_cooking_note(comment, owner=DEFAULT_OWNER):
    """Classify whether a Giscus comment is an actionable cooking note.

    Returns:
        Tuple `(is_note, is_owner_note)`.
    """
    body = (comment.get("body") or "").strip()
    author = (comment.get("author") or "").strip()

    if not body or author.lower().endswith("[bot]"):
        return False, False

    if TRIVIAL_CHAT_RE.match(body):
        return False, False

    is_owner = bool(owner and author.lower() == owner.lower())
    if is_owner:
        return True, True

    if COOKING_SIGNAL_RE.search(body):
        return True, False

    return False, False


def load_state(state_file):
    """Load processed Giscus comment IDs from JSON state file."""
    if not state_file or not os.path.exists(state_file):
        return {"processed_comment_ids": [], "last_synced_at": None}
    with open(state_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        return {"processed_comment_ids": [], "last_synced_at": None}
    ids = data.get("processed_comment_ids") or []
    return {
        "processed_comment_ids": sorted(set(str(x) for x in ids)),
        "last_synced_at": data.get("last_synced_at"),
    }


def save_state(state_file, processed_ids, last_synced_at=None):
    """Persist sorted processed Giscus comment IDs to JSON state file."""
    parent = os.path.dirname(state_file)
    if parent:
        os.makedirs(parent, exist_ok=True)
    payload = {
        "processed_comment_ids": sorted(set(processed_ids)),
        "last_synced_at": last_synced_at
        or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    with open(state_file, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
        f.write("\n")


def fetch_existing_triage_comment_ids(owner=DEFAULT_OWNER, repo=DEFAULT_REPO):
    """Collect comment IDs already referenced in existing GitHub issues and PRs."""
    tracked = set()
    repo_slug = f"{owner}/{repo}"
    for kind in ("issue", "pr"):
        cmd = [
            "gh",
            kind,
            "list",
            "--repo",
            repo_slug,
            "--state",
            "all",
            "--limit",
            "200",
            "--json",
            "body",
        ]
        result = subprocess.run(
            cmd, env=_gh_env(), capture_output=True, text=True
        )
        if result.returncode != 0:
            print(f"Warning: could not list existing {kind}s: {result.stderr.strip()}")
            continue
        try:
            items = json.loads(result.stdout) or []
        except json.JSONDecodeError:
            continue
        for item in items:
            body = item.get("body") or ""
            tracked.update(COMMENT_ID_MARKER_RE.findall(body))
    return tracked


def validate_cook_file(cook_path):
    """Validate a single `.cook` file via `cook-docs doctor` (or `cook` fallback)."""
    if shutil.which("cook-docs"):
        result = subprocess.run(
            ["cook-docs", "doctor", "--only", "syntax,ignored", cook_path],
            capture_output=True,
            text=True,
        )
        output = (result.stdout + "\n" + result.stderr).strip()
        return result.returncode == 0, output
    if not shutil.which("cook"):
        return True, "cook-docs/cook CLI not installed; skipped syntax validation"
    with tempfile.TemporaryDirectory() as tmp_dir:
        shutil.copy2(cook_path, tmp_dir)
        result = subprocess.run(
            ["cook", "doctor", "validate", "-b", tmp_dir],
            capture_output=True,
            text=True,
        )
        output = (result.stdout + "\n" + result.stderr).strip()
        return result.returncode == 0, output


def _recipe_display_name(rel_path, md_path, cook_path):
    """Return human-readable recipe name for PR/issue titles."""
    if cook_path:
        return os.path.splitext(os.path.basename(cook_path))[0]
    if md_path:
        slug = os.path.splitext(os.path.basename(md_path))[0]
        return slug.replace("-", " ").title()
    return rel_path or "Recipe"


def format_triage_body(
    discussion,
    notes,
    md_path,
    cook_path,
    md_comments_added,
    md_promoted,
    cook_result,
):
    """Build Markdown body for a Giscus cooking note triage PR or issue."""
    disc_num = discussion.get("number")
    disc_url = discussion.get("url", "")
    disc_title = discussion.get("title", "")

    lines = [
        "## Giscus Cooking Notes Triage",
        "",
        f"- **Discussion:** [#{disc_num}]({disc_url}) (`{disc_title}`)",
        f"- **Source `.cook`:** `{cook_path}`" if cook_path else "- **Source `.cook`:** _Not found (Markdown-only page)_",
        f"- **Target `.md`:** `{md_path}`" if md_path else "- **Target `.md`:** _Not found_",
        "",
        "### Detected Cooking Notes",
        "",
    ]

    for note in notes:
        author = note.get("author") or "unknown"
        date_str = (note.get("createdAt") or "")[:10] or "unknown-date"
        note_url = note.get("url") or disc_url
        kind = "reply" if note.get("is_reply") else "comment"
        lines.append(f"#### @{author} ({date_str}, [{kind}]({note_url}))")
        lines.append("")
        for body_line in (note.get("body") or "").strip().splitlines():
            lines.append(f"> {body_line}")
        lines.append("")

    lines.append("### Automated Updates Applied")
    lines.append("")
    if md_comments_added:
        lines.append(f"- Enabled `comments: true` in `{md_path}`")
    if md_promoted or (cook_result and cook_result.get("promoted")):
        lines.append("- Promoted tag `must-try` -> `favorite`")
    if cook_result and cook_result.get("notes_added"):
        lines.append(
            f"- Staged {cook_result['notes_added']} cooking note(s) as Cooklang block comment(s) in `{cook_path}`"
        )
    if (
        not md_comments_added
        and not md_promoted
        and not (cook_result and cook_result.get("changed"))
    ):
        lines.append("- None (requires manual review / `.cook` folding)")

    lines.extend(
        [
            "",
            "### Next Steps",
            "",
        ]
    )
    if cook_path:
        lines.extend(
            [
                f"- [ ] Fold the cooking note adjustments into inline Cooklang steps in `{cook_path}` and remove the staged `[-- ... --]` comment",
                f"- [ ] Validate Cooklang syntax (`task validate-cook FILE=\"{cook_path}\"`)",
                f"- [ ] Recompile and sync recipe docs (`FILES=\"{cook_path}\" task move`)",
            ]
        )
    else:
        lines.append(
            f"- [ ] Fold the cooking note adjustments into `{md_path or disc_title}`"
        )

    lines.append("")
    for note in notes:
        lines.append(f"<!-- giscus-comment-id: {note['id']} -->")
    return "\n".join(lines) + "\n"


def _run_git(args):
    """Run a git command and return CompletedProcess."""
    return subprocess.run(["git"] + args, capture_output=True, text=True)


def open_triage_issue(title, body, owner=DEFAULT_OWNER, repo=DEFAULT_REPO):
    """Create a GitHub issue for triaging Giscus cooking notes."""
    cmd = [
        "gh",
        "issue",
        "create",
        "--repo",
        f"{owner}/{repo}",
        "--title",
        title,
        "--body",
        body,
        "--label",
        "enhancement",
    ]
    result = subprocess.run(cmd, env=_gh_env(), capture_output=True, text=True)
    if result.returncode != 0:
        print("Error creating issue:", result.stderr.strip())
        return None
    url = result.stdout.strip()
    print(f"Created triage issue: {url}")
    return url


def open_triage_pr(
    branch_name,
    base_branch,
    title,
    body,
    files_to_stage,
    owner=DEFAULT_OWNER,
    repo=DEFAULT_REPO,
):
    """Commit staged triage changes on a branch, push, and open a PR."""
    if not files_to_stage:
        return None

    remote_check = _run_git(["ls-remote", "--heads", "origin", branch_name])
    if remote_check.returncode == 0 and remote_check.stdout.strip():
        print(f"Remote branch '{branch_name}' already exists; skipping duplicate PR.")
        return "EXISTING_BRANCH"

    checkout_res = _run_git(["checkout", "-B", branch_name])
    if checkout_res.returncode != 0:
        print("Error creating branch:", checkout_res.stderr.strip())
        return None

    try:
        stage_res = _run_git(["add", "--"] + files_to_stage)
        if stage_res.returncode != 0:
            print("Error staging files:", stage_res.stderr.strip())
            _run_git(["reset", "--hard", "HEAD"])
            return None

        commit_res = _run_git(["commit", "-m", title])
        if commit_res.returncode != 0:
            print("Error committing changes:", commit_res.stderr.strip())
            _run_git(["reset", "--hard", "HEAD"])
            return None

        push_res = _run_git(["push", "-u", "origin", branch_name])
        if push_res.returncode != 0:
            print("Error pushing branch:", push_res.stderr.strip())
            return None

        pr_cmd = [
            "gh",
            "pr",
            "create",
            "--repo",
            f"{owner}/{repo}",
            "--base",
            base_branch,
            "--head",
            branch_name,
            "--title",
            title,
            "--body",
            body,
        ]
        pr_res = subprocess.run(
            pr_cmd, env=_gh_env(), capture_output=True, text=True
        )
        if pr_res.returncode != 0:
            print("Error creating PR:", pr_res.stderr.strip())
            return None

        url = pr_res.stdout.strip()
        print(f"Created triage PR: {url}")
        return url
    finally:
        _run_git(["checkout", base_branch])
        _run_git(["branch", "-D", branch_name])


def sync_comments_frontmatter(
    discussions, docs_dir="docs", docs_file_map=None
):
    """Sync `comments: true` frontmatter onto matching markdown files."""
    if docs_file_map is None:
        docs_file_map = build_docs_file_map(docs_dir)

    comments_discussions = [
        d
        for d in discussions
        if (d.get("category") or {}).get("name") == "Comments"
    ]
    modified_files = []
    missing_files = []

    for d in comments_discussions:
        title = d.get("title", "")
        url = d.get("url", "")
        rel_path = clean_pathname(title)
        if not rel_path:
            continue

        found_path = find_docs_file(
            rel_path, docs_dir=docs_dir, docs_file_map=docs_file_map
        )
        if found_path:
            if add_comments_to_file(found_path):
                modified_files.append(found_path)
        else:
            missing_files.append((title, url))

    return modified_files, missing_files


def triage_discussions(
    discussions,
    owner=DEFAULT_OWNER,
    repo=DEFAULT_REPO,
    docs_dir="docs",
    cook_dir="cook",
    state_file=DEFAULT_STATE_FILE,
    mode="auto",
    base_branch="main",
    dry_run=False,
):
    """Detect new Giscus cooking notes and open PRs/issues to fold and promote tags."""
    docs_file_map = build_docs_file_map(docs_dir)
    cook_file_map = build_cook_file_map(cook_dir)
    state = load_state(state_file)
    processed_ids = set(state["processed_comment_ids"])
    existing_tracked_ids = (
        set() if dry_run else fetch_existing_triage_comment_ids(owner, repo)
    )

    comments_discussions = [
        d
        for d in discussions
        if (d.get("category") or {}).get("name") == "Comments"
    ]

    results = []
    for d in comments_discussions:
        all_comments = extract_comments_from_discussion(d)
        new_notes = []
        has_owner_note = False

        for c in all_comments:
            cid = c.get("id")
            if not cid or cid in processed_ids or cid in existing_tracked_ids:
                continue
            is_note, is_owner = is_cooking_note(c, owner=owner)
            if is_note:
                new_notes.append(c)
                if is_owner:
                    has_owner_note = True

        if not new_notes:
            continue

        rel_path = clean_pathname(d.get("title", ""))
        md_path = find_docs_file(
            rel_path, docs_dir=docs_dir, docs_file_map=docs_file_map
        )
        cook_path = find_cook_file(
            rel_path,
            md_path=md_path,
            cook_dir=cook_dir,
            cook_file_map=cook_file_map,
        )
        recipe_name = _recipe_display_name(rel_path, md_path, cook_path)

        state_existed = bool(state_file and os.path.exists(state_file))
        md_comments_added = False
        md_promoted = False
        cook_result = {"changed": False, "promoted": False, "notes_added": 0}
        changed_files = []

        if dry_run or mode == "issue":
            # Inspect without mutating local files on dry-run or issue-only mode.
            if md_path:
                with open(md_path, "r", encoding="utf-8") as f:
                    md_text = f.read()
                md_comments_added = not re.search(
                    r"^\s*comments\s*:\s*['\"]?true['\"]?\s*$",
                    md_text,
                    re.IGNORECASE | re.MULTILINE,
                )
                md_bounds = _find_frontmatter_bounds(md_text.splitlines())
                if has_owner_note and md_bounds:
                    _, md_promoted = _promote_tags_in_frontmatter_lines(
                        md_text.splitlines(), md_bounds[1]
                    )
            if cook_path:
                with open(cook_path, "r", encoding="utf-8") as f:
                    cook_text = f.read()
                _, cook_promoted = promote_tags_in_cook_content(
                    cook_text, add_favorite_if_missing=has_owner_note and md_promoted
                )
                _, notes_added = append_cooking_notes_to_cook_content(
                    cook_text, new_notes
                )
                cook_result = {
                    "changed": cook_promoted or notes_added > 0,
                    "promoted": cook_promoted,
                    "notes_added": notes_added,
                }
        else:
            # Ensure clean starting working tree in pr/auto modes before making edits.
            _run_git(["checkout", base_branch])

            if md_path:
                if add_comments_to_file(md_path):
                    md_comments_added = True
                if has_owner_note and promote_tags_in_markdown(md_path):
                    md_promoted = True
                if md_comments_added or md_promoted:
                    changed_files.append(md_path)

            if cook_path:
                cook_result = update_cook_file(
                    cook_path,
                    new_notes,
                    promote_favorite=has_owner_note and md_promoted,
                )
                if cook_result["changed"]:
                    valid, val_msg = validate_cook_file(cook_path)
                    if not valid:
                        print(
                            f"Warning: cook validation failed for {cook_path}: {val_msg}"
                        )
                    changed_files.append(cook_path)

        body = format_triage_body(
            d,
            new_notes,
            md_path,
            cook_path,
            md_comments_added,
            md_promoted,
            cook_result,
        )
        if dry_run:
            results.append(
                {
                    "discussion": d.get("number"),
                    "recipe": recipe_name,
                    "action": "dry-run",
                    "notes": len(new_notes),
                    "md_path": md_path,
                    "cook_path": cook_path,
                    "promoted": md_promoted or cook_result["promoted"],
                    "body": body,
                }
            )
            continue

        pr_title = f"chore(recipes): triage Giscus notes for {recipe_name}"
        issue_title = f"[Giscus]: Fold cooking notes into {recipe_name}"

        action_taken = None
        action_url = None

        if mode in ("auto", "pr") and changed_files:
            updated_ids = processed_ids | {n["id"] for n in new_notes}
            save_state(state_file, updated_ids)
            files_to_stage = list(changed_files) + [state_file]
            branch_name = f"giscus-triage/discussion-{d.get('number')}"
            pr_res = open_triage_pr(
                branch_name=branch_name,
                base_branch=base_branch,
                title=pr_title,
                body=body,
                files_to_stage=files_to_stage,
                owner=owner,
                repo=repo,
            )
            if pr_res == "EXISTING_BRANCH":
                action_taken = "skipped-existing-branch"
            elif pr_res:
                action_taken = "pr"
                action_url = pr_res

            # Restore local edits on base_branch so subsequent discussions branch cleanly.
            _run_git(["checkout", "--"] + changed_files)
            if state_existed:
                save_state(
                    state_file,
                    state["processed_comment_ids"],
                    state.get("last_synced_at"),
                )
            elif os.path.exists(state_file):
                os.remove(state_file)

        if action_taken is None and mode in ("issue", "auto"):
            issue_url = open_triage_issue(
                title=issue_title, body=body, owner=owner, repo=repo
            )
            if issue_url:
                action_taken = "issue"
                action_url = issue_url

        results.append(
            {
                "discussion": d.get("number"),
                "recipe": recipe_name,
                "action": action_taken or "none",
                "url": action_url,
                "notes": len(new_notes),
                "md_path": md_path,
                "cook_path": cook_path,
                "promoted": md_promoted or cook_result["promoted"],
            }
        )

    return results


def seed_state_from_discussions(discussions, state_file):
    """Record all current discussion comment/reply IDs in the state file."""
    state = load_state(state_file)
    processed = set(state["processed_comment_ids"])
    for d in discussions:
        if (d.get("category") or {}).get("name") != "Comments":
            continue
        for c in extract_comments_from_discussion(d):
            if c.get("id"):
                processed.add(c["id"])
    save_state(state_file, processed)
    return len(processed)


def parse_args(argv=None):
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description="Sync Giscus comments and triage new cooking notes."
    )
    parser.add_argument(
        "--triage",
        action="store_true",
        help="Detect new cooking notes and open PRs/issues to fold adjustments and promote tags.",
    )
    parser.add_argument(
        "--mode",
        choices=["auto", "pr", "issue"],
        default="auto",
        help="Triage output mode: 'auto' (PR with issue fallback), 'pr', or 'issue'.",
    )
    parser.add_argument(
        "--state-file",
        default=DEFAULT_STATE_FILE,
        help=f"Path to processed-comment JSON state file (default: {DEFAULT_STATE_FILE}).",
    )
    parser.add_argument(
        "--seed-state",
        action="store_true",
        help="Seed the state file with all existing comment IDs without creating PRs/issues.",
    )
    parser.add_argument(
        "--base-branch",
        default="main",
        help="Base branch for triage PRs (default: main).",
    )
    parser.add_argument(
        "--owner",
        help=f"GitHub repository owner (default: $GITHUB_REPOSITORY or {DEFAULT_OWNER}).",
    )
    parser.add_argument(
        "--repo",
        help=f"GitHub repository name (default: $GITHUB_REPOSITORY or {DEFAULT_REPO}).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned triage actions without modifying files or calling git/gh write commands.",
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    owner, repo = get_repo_owner_name(args.owner, args.repo)

    print(f"Fetching discussions from GitHub ({owner}/{repo})...")
    discussions = fetch_discussions(owner=owner, repo=repo)
    print(f"Fetched {len(discussions)} discussions total.")

    comments_discussions = [
        d
        for d in discussions
        if (d.get("category") or {}).get("name") == "Comments"
    ]
    print(
        f"Found {len(comments_discussions)} discussions in the 'Comments' category."
    )

    if args.seed_state:
        total = seed_state_from_discussions(discussions, args.state_file)
        print(f"Seeded {total} comment IDs into {args.state_file}.")
        return

    if args.triage:
        results = triage_discussions(
            discussions,
            owner=owner,
            repo=repo,
            state_file=args.state_file,
            mode=args.mode,
            base_branch=args.base_branch,
            dry_run=args.dry_run,
        )
        print("\n--- Triage Complete ---")
        if not results:
            print("No new cooking notes detected.")
            return
        for item in results:
            print(
                f"  - Discussion #{item['discussion']} ({item['recipe']}): "
                f"action={item['action']}, notes={item['notes']}, "
                f"promoted={item['promoted']}"
                + (f", url={item['url']}" if item.get("url") else "")
            )
        return

    docs_file_map = build_docs_file_map("docs")
    print(f"Indexed {len(docs_file_map)} markdown files in docs/ directory.")
    modified_files, missing_files = sync_comments_frontmatter(
        discussions, docs_dir="docs", docs_file_map=docs_file_map
    )

    print("\n--- Sync Complete ---")
    if modified_files:
        print(f"Modified {len(modified_files)} files to enable comments:")
        for f in modified_files:
            print(f"  - {f}")
    else:
        print(
            "All matching files already had comments enabled (or no files modified)."
        )

    if missing_files:
        print(
            f"\nCould not find matching local markdown files for {len(missing_files)} discussions:"
        )
        for title, url in missing_files:
            print(f"  - Title: {title} ({url})")


if __name__ == "__main__":
    main()
