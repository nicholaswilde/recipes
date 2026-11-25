#!/usr/bin/env python3

################################################################################
#
# lint_changed.py
# ----------------
# Lint changed recipe files
#
# @author nιcнolaѕ wιlde, 0x08b7d7a3
# @date 12 Jun 2026
# @version 0.1.0
#
################################################################################

import subprocess
import sys
import os

def get_changed_files():
    # Get staged, unstaged, and untracked files
    try:
        # Run git status --porcelain
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Error running git status: {e}", file=sys.stderr)
        return []

    files = []
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        # Status codes: M = modified, A = added, ?? = untracked, R = renamed
        # Format is typically "XY path" or "XY path -> new_path"
        status = line[:2]
        path = line[3:].strip()
        if "->" in path:
            path = path.split("->")[1].strip()
        
        # Strip quotes if git quoted the path
        if path.startswith('"') and path.endswith('"'):
            path = path[1:-1]
            # Resolve git octal escapes (e.g. \303\242) if any
            path = path.encode().decode('unicode-escape').encode('latin1').decode('utf-8', errors='ignore')

        files.append((status, path))
    return files

def main():
    changed_files = get_changed_files()
    if not changed_files:
        print("No changed files detected.")
        sys.exit(0)

    md_files = []
    frontmatter_files = []
    yaml_files = []
    ignored_docs = {
        "docs/README.md",
        "docs/index.md",
        "docs/reference/charts.md",
    }

    for status, path in changed_files:
        if not os.path.exists(path):
            continue
        norm_path = path.replace("\\", "/")
        if path.endswith(".md"):
            md_files.append(path)
            if norm_path.startswith("docs/") and norm_path not in ignored_docs:
                frontmatter_files.append(path)
        elif path.endswith(".cook") and norm_path.startswith("cook/"):
            frontmatter_files.append(path)
        elif path.endswith((".yaml", ".yml")):
            if not norm_path.startswith(".github/"):
                yaml_files.append(path)

    has_errors = False

    # Lint Markdown files
    if md_files:
        print(f"Linting {len(md_files)} changed Markdown files with rumdl...")
        # Run rumdl check
        result = subprocess.run(["rumdl", "check"] + md_files)
        if result.returncode != 0:
            has_errors = True
    else:
        print("No changed Markdown files to lint.")

    # Validate frontmatter in docs/ and cook/ via per-glob [[schemas]]
    if frontmatter_files:
        print(
            f"\nValidating frontmatter in {len(frontmatter_files)} changed"
            " file(s) with mdfm..."
        )
        result = subprocess.run(
            ["mdfm", "check", "--errors-only"] + frontmatter_files
        )
        if result.returncode != 0:
            has_errors = True

        print(
            f"\nChecking frontmatter formatting in {len(frontmatter_files)}"
            " changed file(s) with mdfm..."
        )
        result = subprocess.run(
            ["mdfm", "fmt", "--check", "--files-only"] + frontmatter_files
        )
        if result.returncode != 0:
            has_errors = True

    # Lint YAML files
    if yaml_files:
        print(f"\nLinting {len(yaml_files)} changed YAML files with yamllint-rs...")
        result = subprocess.run(["yamllint-rs"] + yaml_files)
        if result.returncode != 0:
            has_errors = True
    else:
        print("No changed YAML files to lint.")

    if has_errors:
        sys.exit(1)
    else:
        print("\nAll changed files passed linting successfully!")
        sys.exit(0)

if __name__ == "__main__":
    main()
