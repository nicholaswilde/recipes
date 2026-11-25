#!/usr/bin/env python3

################################################################################
#
# check_recipe_emojis.py
# ----------------
# Check and auto-fix recipe ingredient and cookware emojis
#
# @author nιcнolaѕ wιlde, 0x08b7d7a3
# @date 02 Jun 2026
# @version 0.2.0
#
################################################################################

import argparse
import difflib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import markdown
import yaml

try:
    import pymdownx.emoji
except ImportError:
    pymdownx = None

EMOJI_YAML_PATH = "includes/emoji.yaml"


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


def load_emoji_mappings(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    emoji_data = data.get("emoji", {})
    mappings = {"ingredients": {}, "cookware": {}}
    for category in ("ingredients", "cookware"):
        for group in emoji_data.get(category, []):
            for emoji_name, terms in group.items():
                for term in terms or []:
                    mappings[category][str(term).strip().lower()] = emoji_name
    return mappings


def extract_recipe_items(cook_path):
    """Extract ingredients and cookware via cook-docs --jsonify (Cooklang AST)."""
    if shutil.which("cook-docs"):
        parent = str(Path(cook_path).resolve().parent)
        res = subprocess.run(
            ["cook-docs", "-c", parent, "--jsonify", cook_path],
            capture_output=True,
            text=True,
        )
        if res.returncode == 0 and res.stdout.strip():
            try:
                parsed = json.loads(res.stdout)
                if isinstance(parsed, list):
                    parsed = parsed[0] if parsed else {}
                ingredients = {
                    item["Name"].strip()
                    for item in parsed.get("Ingredients", [])
                    if item.get("Name")
                }
                cookware = {
                    item["Name"].strip()
                    for item in parsed.get("Cookware", [])
                    if item.get("Name")
                }
                return ingredients, cookware
            except (json.JSONDecodeError, KeyError, IndexError):
                pass

    # Fallback regex parser when cook-docs is unavailable
    with open(cook_path, "r", encoding="utf-8") as f:
        content = f.read()
    ingredients = {
        (m[0] or m[1]).strip()
        for m in re.findall(r"@(?:([^\n@#{}]+)\{[^}]*\}|(\w+))", content)
        if m[0] or m[1]
    }
    cookware = {
        (m[0] or m[1]).strip()
        for m in re.findall(r"#(?:([^\n@#{}]+)\{[^}]*\}|(\w+))", content)
        if m[0] or m[1]
    }
    return ingredients, cookware


def find_match(name, category_mappings):
    name_lower = name.lower().strip()
    if name_lower in category_mappings:
        return category_mappings[name_lower]
    if name_lower.endswith("s") and name_lower[:-1] in category_mappings:
        return category_mappings[name_lower[:-1]]
    if (name_lower + "s") in category_mappings:
        return category_mappings[name_lower + "s"]
    return None


def get_heuristic_emoji_group(missing_term, category):
    missing_lower = missing_term.lower().strip()
    if category == "ingredients":
        if "cheese" in missing_lower:
            return "cheese_wedge"
        if any(kw in missing_lower for kw in ["pepper", "chili", "chille", "jalapeño", "serrano", "poblano"]):
            return "hot_pepper"
        if any(kw in missing_lower for kw in ["onion", "scallion", "shallot", "leek"]):
            return "tea"
        if "tomato" in missing_lower or "pico de gallo" in missing_lower or "salsa" in missing_lower:
            return "tomato"
        if any(kw in missing_lower for kw in ["sauce", "dressing", "vinegar", "aminos", "tamari", "miso"]):
            return "takeout_box"
        if "garlic" in missing_lower:
            return "garlic"
        if any(kw in missing_lower for kw in ["chicken", "turkey", "breast"]):
            return "stew"
        if any(kw in missing_lower for kw in ["vegetable", "veggie"]):
            return "carrot"
        if any(kw in missing_lower for kw in ["cream", "milk", "yogurt", "butter"]):
            return "glass_of_milk"
    elif category == "cookware":
        if any(kw in missing_lower for kw in ["pan", "skillet", "pot", "saucepan", "grill", "spoon", "whisk", "knife", "fork"]):
            return "bowl_with_spoon"
    return None


def find_best_emoji_group(missing_term, emoji_category_data):
    best_score = 0.0
    best_emoji = None

    missing_lower = missing_term.lower().strip()
    missing_words = set(re.findall(r"\w+", missing_lower))

    for group in emoji_category_data:
        for emoji_name, terms in group.items():
            for term in terms:
                term_lower = str(term).lower().strip()
                if term_lower == missing_lower:
                    return emoji_name, 1.0

                term_words = set(re.findall(r"\w+", term_lower))
                has_overlap = any(
                    len(w1) > 3 and len(w2) > 3 and (w1 in w2 or w2 in w1)
                    for w1 in missing_words
                    for w2 in term_words
                )
                if has_overlap and 0.8 > best_score:
                    best_score = 0.8
                    best_emoji = emoji_name

                seq_score = difflib.SequenceMatcher(None, missing_lower, term_lower).ratio()
                if seq_score > best_score:
                    best_score = seq_score
                    best_emoji = emoji_name

    if best_score >= 0.6:
        return best_emoji, best_score
    return None, 0.0


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


def main():
    parser = argparse.ArgumentParser(description="Check and optionally fix recipe emojis in includes/emoji.yaml")
    parser.add_argument("recipe_path", help="Path to the recipe .cook file")
    parser.add_argument("--fix", action="store_true", help="Automatically map missing emojis in includes/emoji.yaml")
    args = parser.parse_args()

    cook_path = args.recipe_path
    if not os.path.exists(cook_path):
        print(f"Error: {cook_path} not found")
        sys.exit(1)

    ingredients, cookware = extract_recipe_items(cook_path)

    emoji_path = globals().get("EMOJI_YAML_PATH", EMOJI_YAML_PATH)
    if not os.path.exists(emoji_path):
        print(f"Error: {emoji_path} not found")
        sys.exit(1)

    mappings = load_emoji_mappings(emoji_path)
    valid_gemoji = get_valid_gemoji()

    missing_ingredients = []
    missing_cookware = []

    print("Checking recipe ingredients and cookware emojis...")
    print("-" * 50)

    for label, items, cat_key, missing_list in (
        ("Ingredients", ingredients, "ingredients", missing_ingredients),
        ("Cookware", cookware, "cookware", missing_cookware),
    ):
        print(f"\n{label}:")
        for item in sorted(items):
            match = find_match(item, mappings[cat_key])
            if match:
                if valid_gemoji and match not in valid_gemoji:
                    print(f"  \u274c {item:<30} -> :{match}: (INVALID GEMOJI SHORTCODE)")
                    missing_list.append(item)
                else:
                    print(f"  \u2705 {item:<30} -> :{match}:")
            else:
                print(f"  \u274c {item:<30} -> MISSING EMOJI")
                missing_list.append(item)

    print("-" * 50)

    if args.fix and (missing_ingredients or missing_cookware):
        with open(emoji_path, "r", encoding="utf-8") as f:
            yaml_data = yaml.safe_load(f) or {}

        print("Auto-fixing missing emoji mappings...")
        fixed_count = 0

        for cat_key, missing_list, fallback_group in (
            ("ingredients", missing_ingredients, "takeout_box"),
            ("cookware", missing_cookware, "bowl_with_spoon"),
        ):
            if not missing_list:
                continue
            cat_data = yaml_data.get("emoji", {}).get(cat_key, [])
            for item in missing_list:
                best_group = get_heuristic_emoji_group(item, cat_key)
                if best_group:
                    print(f"  Heuristic mapped {cat_key[:-1] if cat_key.endswith('s') else cat_key} '{item}' to group '{best_group}'")
                else:
                    best_group, score = find_best_emoji_group(item, cat_data)
                    if best_group:
                        print(f"  Mapping {cat_key[:-1] if cat_key.endswith('s') else cat_key} '{item}' to group '{best_group}' (confidence: {score:.2f})")
                    else:
                        best_group = fallback_group
                        print(f"  No similar group found for '{item}'. Mapping to fallback group '{best_group}'")
                insert_emoji_mapping(emoji_path, cat_key, best_group, item)
                fixed_count += 1

        if fixed_count > 0:
            try:
                subprocess.run(["task", "emoji-sort"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception:
                pass
            print(f"Successfully auto-mapped {fixed_count} missing emojis in {emoji_path}!")
            sys.exit(0)

    if missing_ingredients or missing_cookware:
        print("Warning: Missing emoji mappings found.")
        if missing_ingredients:
            print(f"Missing/Invalid ingredients in includes/emoji.yaml: {', '.join(missing_ingredients)}")
        if missing_cookware:
            print(f"Missing/Invalid cookware in includes/emoji.yaml: {', '.join(missing_cookware)}")
        sys.exit(1)
    else:
        print("All ingredients and cookware are successfully mapped to emojis!")
        sys.exit(0)


if __name__ == "__main__":
    main()
