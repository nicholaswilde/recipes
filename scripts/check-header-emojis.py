#!/usr/bin/env python3
import os
import re
import sys
import argparse

def check_file(file_path):
    """
    Checks if a markdown file's H1 header has an emoji shortcode.
    Returns (is_valid, h1_title or error_message)
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("# "):
                    h1_title = line[2:].strip()
                    # Matches emoji shortcode e.g., :egg:
                    if re.match(r"^:[a-zA-Z0-9_+-]+:", h1_title):
                        return True, h1_title
                    else:
                        return False, h1_title
            return False, "No H1 header found"
    except Exception as e:
        return False, f"Error reading file: {e}"

def main():
    parser = argparse.ArgumentParser(description="Check for emoji shortcodes in recipe H1 headers")
    parser.add_argument("files", nargs="*", help="Optional specific markdown file(s) to check")
    args = parser.parse_args()

    docs_dir = "docs"
    exclude_files = {"index.md", "tags.md", "README.md"}
    exclude_dirs = {"reference", "assets"}

    files_to_check = []

    if args.files:
        files_to_check = args.files
    else:
        for root, dirs, files in os.walk(docs_dir):
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            for file in files:
                if file.endswith(".md") and file not in exclude_files:
                    files_to_check.append(os.path.join(root, file))

    missing_files = []
    total_checked = 0

    for file_path in sorted(files_to_check):
        total_checked += 1
        is_valid, title = check_file(file_path)
        if not is_valid:
            missing_files.append((file_path, title))

    print(f"Checked {total_checked} markdown file(s).")
    if missing_files:
        print(f"Found {len(missing_files)} file(s) missing an emoji shortcode in H1 header:")
        for path, title in missing_files:
            print(f"- {path}: {title}")
        sys.exit(1)
    else:
        print("All checked recipes contain an emoji shortcode in their H1 header!")
        sys.exit(0)

if __name__ == "__main__":
    main()
