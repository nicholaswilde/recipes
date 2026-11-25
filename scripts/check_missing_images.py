#!/usr/bin/env python3

################################################################################
#
# check_missing_images.py
# ----------------
# Check for recipes with missing image files
#
# @author nιcнolaѕ wιlde, 0x08b7d7a3
# @date 14 Jun 2026
# @version 0.1.0
#
################################################################################

"""Check recipe markdown files for missing images.

Detects three types of image issues:
1. NO_HERO     - Recipe has no `hero:` field in frontmatter
2. NO_EMBED    - Recipe has no image embed (![...]) in the body
3. HERO_MISSING - The `hero:` field references an image file that doesn't exist
4. HERO_CORRUPT - The `hero:` field contains markdown links (broken by hyperlink scripts)

Usage:
    uv run python scripts/check_missing_images.py [--json] [--category CATEGORY]
"""

import argparse
import json
import os
import subprocess
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS_DIR = os.path.join(REPO_ROOT, "docs")

# Directories and files to skip
SKIP_DIRS = {"css", "javascripts", "stylesheets", "assets", "reference"}
SKIP_FILES = {"index.md", "README.md", "tags.md"}


def is_recipe(filepath):
    """Check if a markdown file is a recipe (has Ingredients or Instructions)."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    return "## :salt: Ingredients" in content or "## :pencil: Instructions" in content


def get_hero_map(paths=None):
    """Query `hero` frontmatter values via `mdfm` keyed by resolved path."""
    targets = [str(p) for p in paths] if paths else [DOCS_DIR]
    result = subprocess.run(
        ["mdfm", "--output", "json", "get", "hero", *targets],
        capture_output=True,
        text=True,
        check=True,
    )
    entries = json.loads(result.stdout) if result.stdout.strip() else []
    return {
        os.path.realpath(entry["file"]): str(entry["value"]).strip()
        for entry in entries
        if entry.get("value") is not None
    }


def has_image_embed(filepath):
    """Check if a markdown file has an image embed ![...]."""
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip().startswith("!["):
                return True
    return False


def resolve_hero_image(filepath, hero_path):
    """Check if the hero image file exists on disk.

    Returns (exists, resolved_path, is_corrupt).
    """
    # Check if hero path contains markdown links (corrupted by hyperlink scripts)
    if "[" in hero_path and "](" in hero_path:
        return False, hero_path, True

    # Try resolving from docs/ root
    from_docs = os.path.join(DOCS_DIR, hero_path)
    if os.path.isfile(from_docs):
        return True, from_docs, False

    # Try resolving relative to the markdown file
    from_file = os.path.join(os.path.dirname(filepath), hero_path)
    if os.path.isfile(from_file):
        return True, from_file, False

    return False, hero_path, False


def find_recipe_files(category=None):
    """Find all recipe markdown files, optionally filtered by category."""
    recipe_files = []
    for root, dirs, files in os.walk(DOCS_DIR):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for fname in files:
            if fname in SKIP_FILES or not fname.endswith(".md"):
                continue

            filepath = os.path.join(root, fname)
            relpath = os.path.relpath(filepath, DOCS_DIR)

            if category:
                top_dir = relpath.split(os.sep)[0]
                if top_dir != category:
                    continue

            if is_recipe(filepath):
                recipe_files.append(filepath)

    return sorted(recipe_files)


def check_images(recipe_files, hero_map=None):
    """Check all recipe files for image issues.

    Returns a list of dicts with issue details.
    """
    if hero_map is None:
        hero_map = get_hero_map(recipe_files) if recipe_files else {}

    issues = []

    for filepath in recipe_files:
        relpath = os.path.relpath(filepath, REPO_ROOT)
        hero = hero_map.get(os.path.realpath(filepath), "")
        embed = has_image_embed(filepath)

        if not hero:
            issues.append({
                "file": relpath,
                "type": "NO_HERO",
                "detail": "No hero image in frontmatter",
            })

        if not embed:
            issues.append({
                "file": relpath,
                "type": "NO_EMBED",
                "detail": "No image embed (![...]) in body",
            })

        if hero:
            exists, resolved, is_corrupt = resolve_hero_image(filepath, hero)
            if is_corrupt:
                issues.append({
                    "file": relpath,
                    "type": "HERO_CORRUPT",
                    "detail": f"Hero path contains markdown links: {hero}",
                })
            elif not exists:
                issues.append({
                    "file": relpath,
                    "type": "HERO_MISSING",
                    "detail": f"Hero image file not found: {hero}",
                })

    return issues


def print_report(issues):
    """Print a human-readable report of image issues."""
    if not issues:
        print("✅ All recipe files have proper images!")
        return

    # Group by type
    by_type = {}
    for issue in issues:
        by_type.setdefault(issue["type"], []).append(issue)

    type_labels = {
        "NO_HERO": "Missing hero frontmatter",
        "NO_EMBED": "Missing image embed",
        "HERO_MISSING": "Hero image file not found",
        "HERO_CORRUPT": "Hero path corrupted (contains markdown links)",
    }

    print(f"Found {len(issues)} image issues across recipe files:\n")

    for issue_type in ["HERO_CORRUPT", "HERO_MISSING", "NO_HERO", "NO_EMBED"]:
        type_issues = by_type.get(issue_type, [])
        if not type_issues:
            continue

        label = type_labels.get(issue_type, issue_type)
        print(f"{'=' * 60}")
        print(f"  {label} ({len(type_issues)} files)")
        print(f"{'=' * 60}")

        for issue in type_issues:
            print(f"  {issue['file']}")
            if issue_type in ("HERO_MISSING", "HERO_CORRUPT"):
                print(f"    → {issue['detail']}")
        print()

    # Summary
    print(f"{'=' * 60}")
    print("Summary:")
    for issue_type, label in type_labels.items():
        count = len(by_type.get(issue_type, []))
        if count > 0:
            print(f"  {label}: {count}")
    print(f"  Total issues: {len(issues)}")


def main():
    parser = argparse.ArgumentParser(
        description="Check recipe markdown files for missing images"
    )
    parser.add_argument(
        "--json", action="store_true", help="Output results as JSON"
    )
    parser.add_argument(
        "--category",
        type=str,
        default=None,
        help="Filter by category directory (e.g., breakfast, desserts)",
    )
    args = parser.parse_args()

    recipe_files = find_recipe_files(category=args.category)
    target_dir = os.path.join(DOCS_DIR, args.category) if args.category else DOCS_DIR
    hero_map = get_hero_map([target_dir]) if os.path.isdir(target_dir) else {}
    issues = check_images(recipe_files, hero_map=hero_map)

    if args.json:
        print(json.dumps(issues, indent=2))
    else:
        print_report(issues)

    sys.exit(1 if issues else 0)


if __name__ == "__main__":
    main()
