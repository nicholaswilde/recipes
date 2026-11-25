#!/usr/bin/env python3

################################################################################
#
# check_header_emojis.py
# ----------------
# Check if recipe H1 headers have valid emoji shortcodes
#
# @author nιcнolaѕ wιlde, 0x08b7d7a3
# @date 26 Jun 2026
# @version 0.2.0
#
################################################################################

import argparse
import os
import re
import subprocess
import sys
import tomllib
from pathlib import Path

import markdown
import yaml

try:
    import pymdownx.emoji
except ImportError:
    pymdownx = None

EMOJI_YAML_PATH = "includes/emoji.yaml"
COOKDOCS_CONFIG_PATH = ".cookdocs.toml"

EMOJI_REPLACEMENTS = {
    "avodado": "avocado",
    "muffin": "cupcake",
    "peanut": "peanuts",
    "salad_bowl": "green_salad",
}


def get_valid_gemoji():
    if not pymdownx:
        return None
    try:
        md = markdown.Markdown()
        valid = set()
        for index_fn in (pymdownx.emoji.gemoji, pymdownx.emoji.twemoji):
            res = index_fn(options={}, md=md)
            valid.update(k.strip(":") for k in res.get("emoji", {}).keys())
            valid.update(k.strip(":") for k in res.get("aliases", {}).keys())
        return valid
    except Exception:
        return None


def load_cookdocs_emoji_rules(config_path=COOKDOCS_CONFIG_PATH):
    """Load [emoji.categories] and [emoji.titles] from .cookdocs.toml."""
    categories = {}
    heuristics = {}
    path = Path(config_path)
    if not path.is_file():
        return categories, heuristics
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
        emoji_cfg = data.get("emoji", {})
        for cat, sc in emoji_cfg.get("categories", {}).items():
            categories[str(cat).strip().lower()] = str(sc).strip().strip(":")
        for sc, terms in emoji_cfg.get("titles", {}).items():
            clean_sc = str(sc).strip().strip(":")
            for term in terms:
                heuristics[str(term).strip().lower()] = clean_sc
    except Exception as e:
        print(f"Warning: could not load {config_path}: {e}")
    return categories, heuristics


CATEGORY_EMOJIS, HEURISTIC_EMOJIS = load_cookdocs_emoji_rules()


def load_emoji_mappings(filepath):
    try:
        if not os.path.exists(filepath):
            return {}, set()
        with open(filepath, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        emoji_data = data.get("emoji", {})

        mappings = {}
        allowed_emojis = set()
        for section in ("cookware", "ingredients"):
            for item in emoji_data.get(section, []):
                for emoji_name, terms in item.items():
                    allowed_emojis.add(emoji_name)
                    for term in terms or []:
                        mappings[str(term).lower().strip()] = emoji_name
        return mappings, allowed_emojis
    except Exception as e:
        print(f"Warning: could not load emoji mappings: {e}")
        return {}, set()


def check_file(file_path):
    """Checks if a markdown file's H1 header has an emoji shortcode.

    Returns (is_valid, emoji_shortcode_or_none, h1_title or error_message).
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("# "):
                    h1_title = line[2:].strip()
                    m = re.match(r"^:([a-zA-Z0-9_+-]+):", h1_title)
                    if m:
                        return True, m.group(1), h1_title
                    return False, None, h1_title
            return False, None, "No H1 header found"
    except Exception as e:
        return False, None, f"Error reading file: {e}"


def suggest_emoji(file_path, mappings):
    title = ""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("# "):
                    title = line[2:].strip()
                    break
    except Exception:
        pass

    if not title:
        title = os.path.splitext(os.path.basename(file_path))[0].replace("-", " ")

    title_clean = re.sub(r":[a-zA-Z0-9_+-]+:", "", title)
    title_words = [w.lower() for w in re.findall(r"\w+", title_clean)]

    # 1. Match title words against .cookdocs.toml [emoji.titles]
    for word in title_words:
        if word in HEURISTIC_EMOJIS:
            return HEURISTIC_EMOJIS[word]

    # 2. Match title words against includes/emoji.yaml
    for word in title_words:
        if word in mappings:
            return mappings[word]

    # 3. Match first emoji or keyword in the Ingredients section
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        ingredients_section = False
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("## ") and "ingredients" in stripped.lower():
                ingredients_section = True
                continue
            if ingredients_section and stripped.startswith("## "):
                ingredients_section = False

            if ingredients_section and stripped.startswith("- "):
                emoji_match = re.match(r"^-\s+:([a-zA-Z0-9_+-]+):", stripped)
                if emoji_match:
                    return emoji_match.group(1)

                ing_line_lower = re.sub(r"^-\s*", "", stripped).lower()
                for kw, emoji_name in HEURISTIC_EMOJIS.items():
                    if kw in ing_line_lower:
                        return emoji_name

                matches = [
                    (term, emoji_name)
                    for term, emoji_name in mappings.items()
                    if len(term) > 3
                    and term not in {"fresh", "chopped", "ground", "dried", "water", "salt", "pepper", "oil", "butter"}
                    and term in ing_line_lower
                ]
                if matches:
                    matches.sort(key=lambda x: len(x[0]), reverse=True)
                    return matches[0][1]
    except Exception:
        pass

    # 4. Longest-prefix fallback against .cookdocs.toml [emoji.categories]
    rel_parts = list(Path(file_path).parts)
    if rel_parts and rel_parts[0] == "docs":
        rel_parts = rel_parts[1:]
    cat_parts = [p.lower() for p in rel_parts[:-1]]
    for end in range(len(cat_parts), 0, -1):
        key = "/".join(cat_parts[:end])
        if key in CATEGORY_EMOJIS:
            return CATEGORY_EMOJIS[key]
    return "shallow_pan_of_food"


def insert_emoji_mapping(filepath, category, emoji_key, new_term):
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    category_found = False
    inserted = False

    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped == f"{category}:":
            category_found = True
            continue
        if category_found and stripped in {"ingredients:", "cookware:"} and line.startswith("  "):
            break

        if category_found and line.rstrip().endswith(f"- {emoji_key}:"):
            indent = "        "
            if i + 1 < len(lines):
                m_indent = re.match(r"^(\s+)-", lines[i + 1])
                if m_indent:
                    indent = m_indent.group(1)
            lines.insert(i + 1, f"{indent}- {new_term}\n")
            inserted = True
            break

    if not inserted:
        category_index = -1
        next_category_index = -1
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped == f"{category}:":
                category_index = i
            elif category_index != -1 and stripped in {"ingredients:", "cookware:"} and line.startswith("  "):
                next_category_index = i
                break

        insert_pos = next_category_index if next_category_index != -1 else len(lines)
        for offset, gl in enumerate((f"    - {emoji_key}:\n", f"        - {new_term}\n")):
            lines.insert(insert_pos + offset, gl)

    with open(filepath, "w", encoding="utf-8") as f:
        f.writelines(lines)


def fix_file(file_path, suggested_emoji):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.read().splitlines()

        for idx, line in enumerate(lines):
            if line.startswith("# "):
                title_clean = re.sub(r"^:[a-zA-Z0-9_+-]+:\s*", "", line[2:].strip())
                lines[idx] = f"# :{suggested_emoji}: {title_clean}"
                break

        with open(file_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        return True
    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Check and optionally fix emoji shortcodes in recipe H1 headers")
    parser.add_argument("files", nargs="*", help="Optional specific markdown file(s) to check")
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Automatically insert suggested H1 emoji if missing and register in includes/emoji.yaml",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Show all checked files with their emojis")
    args = parser.parse_args()

    docs_dir = "docs"
    exclude_files = {"index.md", "tags.md", "README.md"}
    exclude_dirs = {"reference", "assets"}

    if args.files:
        files_to_check = args.files
    else:
        files_to_check = []
        for root, dirs, files in os.walk(docs_dir):
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            for file in files:
                if file.endswith(".md") and file not in exclude_files:
                    files_to_check.append(os.path.join(root, file))

    emoji_mappings, allowed_emojis = load_emoji_mappings(EMOJI_YAML_PATH)
    valid_gemoji = get_valid_gemoji()

    missing_emoji_files = []
    unregistered_emoji_files = []
    invalid_emoji_files = []
    fixed_count = 0
    emoji_yaml_modified = False

    for file_path in sorted(files_to_check):
        is_valid, emoji, title = check_file(file_path)

        if is_valid:
            if emoji in EMOJI_REPLACEMENTS:
                replacement = EMOJI_REPLACEMENTS[emoji]
                if args.fix:
                    print(f"  \u274c {file_path}: Invalid emoji :{emoji}:. Replacing with :{replacement}: ... ", end="")
                    if fix_file(file_path, replacement):
                        print("Fixed!")
                        fixed_count += 1
                        clean_title = re.sub(r":[a-zA-Z0-9_+-]+:", "", title).strip()
                        if replacement not in allowed_emojis:
                            insert_emoji_mapping(EMOJI_YAML_PATH, "ingredients", replacement, clean_title.lower())
                            allowed_emojis.add(replacement)
                            emoji_yaml_modified = True
                    else:
                        print("Failed to fix.")
                else:
                    invalid_emoji_files.append((file_path, title, emoji))
            elif valid_gemoji and emoji not in valid_gemoji:
                print(f"  \u274c {file_path}: :{emoji}: (INVALID GEMOJI SHORTCODE)")
                invalid_emoji_files.append((file_path, title, emoji))
            elif emoji in allowed_emojis:
                if args.verbose:
                    print(f"  \u2705 {file_path}: :{emoji}: (Mapped in emoji.yaml)")
            else:
                if args.fix:
                    print(f"  \u274c {file_path}: H1 emoji :{emoji}: not registered in emoji.yaml. Registering ... ", end="")
                    clean_title = re.sub(r":[a-zA-Z0-9_+-]+:", "", title).strip()
                    insert_emoji_mapping(EMOJI_YAML_PATH, "ingredients", emoji, clean_title.lower())
                    allowed_emojis.add(emoji)
                    print("Registered!")
                    fixed_count += 1
                    emoji_yaml_modified = True
                else:
                    unregistered_emoji_files.append((file_path, title, emoji))
        else:
            suggestion = suggest_emoji(file_path, emoji_mappings)
            if args.fix:
                print(f"  \u274c {file_path}: Missing emoji. Suggesting :{suggestion}: ... ", end="")
                if fix_file(file_path, suggestion):
                    print("Fixed! ", end="")
                    if suggestion not in allowed_emojis:
                        print(f"Registering :{suggestion}: in emoji.yaml ... ", end="")
                        clean_title = re.sub(r":[a-zA-Z0-9_+-]+:", "", title).strip()
                        insert_emoji_mapping(EMOJI_YAML_PATH, "ingredients", suggestion, clean_title.lower())
                        allowed_emojis.add(suggestion)
                        emoji_yaml_modified = True
                    print("Done!")
                    fixed_count += 1
                else:
                    print("Failed to fix.")
            else:
                missing_emoji_files.append((file_path, title, suggestion))

    if emoji_yaml_modified:
        try:
            subprocess.run(["task", "emoji-sort"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass

    print(f"\nChecked {len(files_to_check)} markdown file(s).")

    if args.fix:
        print(f"Successfully fixed/registered H1 emojis in {fixed_count} recipe files!")
        sys.exit(0)

    has_errors = False
    if invalid_emoji_files:
        print(f"\nFound {len(invalid_emoji_files)} file(s) with INVALID emoji shortcodes:")
        for path, title, emoji in invalid_emoji_files:
            print(f"- {path}: '{title}' (Emoji :{emoji}: does not exist in gemoji)")
        has_errors = True
    if missing_emoji_files:
        print(f"\nFound {len(missing_emoji_files)} file(s) missing an emoji shortcode in H1 header:")
        for path, title, suggestion in missing_emoji_files:
            print(f"- {path}: '{title}' (Suggested: :{suggestion}:)")
        has_errors = True
    if unregistered_emoji_files:
        print(f"\nFound {len(unregistered_emoji_files)} file(s) with H1 emoji not registered in {EMOJI_YAML_PATH}:")
        for path, title, emoji in unregistered_emoji_files:
            print(f"- {path}: '{title}' (Emoji :{emoji}: is unregistered)")
        has_errors = True

    if has_errors:
        sys.exit(1)
    print("All checked recipes contain a registered H1 header emoji!")
    sys.exit(0)


if __name__ == "__main__":
    main()
