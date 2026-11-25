#!/usr/bin/env python3

################################################################################
#
# check_recipe_emojis.py
# ----------------
# Check and auto-fix recipe ingredient and cookware emojis
#
# @author nιcнolaѕ wιlde, 0x08b7d7a3
# @date 02 Jun 2026
# @version 0.3.0
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


def _split_doctor_items(raw_list, known_names):
    """Split a comma-separated doctor item list while preserving commas inside names."""
    remaining = raw_list.strip()
    if not remaining:
        return []
    candidates = sorted(
        {name.strip() for name in known_names if name and name.strip()},
        key=len,
        reverse=True,
    )
    parsed = []
    while remaining:
        matched = None
        rem_lower = remaining.lower()
        for name in candidates:
            name_lower = name.lower()
            if rem_lower == name_lower or rem_lower.startswith(name_lower + ", "):
                matched = remaining[: len(name)]
                remaining = remaining[len(name) :].lstrip()
                if remaining.startswith(","):
                    remaining = remaining[1:].lstrip()
                break
        if matched is not None:
            parsed.append(matched)
        else:
            head, sep, tail = remaining.partition(", ")
            parsed.append(head.strip())
            remaining = tail.strip() if sep else ""
    return parsed


def extract_recipe_items(cook_path):
    """Extract ingredients and cookware via cook-docs --jsonify (Cooklang AST)."""
    parent = str(Path(cook_path).resolve().parent)
    res = subprocess.run(
        ["cook-docs", "-c", parent, "--jsonify", cook_path],
        capture_output=True,
        text=True,
        check=True,
    )
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


def find_unmapped_with_doctor(cook_path, emoji_path, known_ingredients, known_cookware):
    """Query cook-docs doctor --only emojis --json for unmapped items."""
    parent = str(Path(cook_path).resolve().parent)
    res = subprocess.run(
        [
            "cook-docs",
            "-c",
            parent,
            "--emoji-file",
            emoji_path,
            "doctor",
            "--only",
            "emojis",
            "--json",
            cook_path,
        ],
        capture_output=True,
        text=True,
    )
    if not res.stdout.strip():
        raise RuntimeError(res.stderr.strip() or "cook-docs doctor returned empty output")
    report = json.loads(res.stdout)
    missing_ingredients = []
    missing_cookware = []
    for check in report.get("checks", []):
        if check.get("category") != "recipe_emojis" or check.get("severity") == "ok":
            continue
        msg = check.get("message", "")
        m = re.search(r"'\s+\((.+)\)\s*$", msg)
        if not m:
            continue
        for part in m.group(1).split("; "):
            if part.startswith("ingredients: "):
                missing_ingredients.extend(
                    _split_doctor_items(part[len("ingredients: ") :], known_ingredients)
                )
            elif part.startswith("cookware: "):
                missing_cookware.extend(
                    _split_doctor_items(part[len("cookware: ") :], known_cookware)
                )
    return missing_ingredients, missing_cookware


def load_invalid_gemoji_terms(yaml_data, valid_gemoji):
    """Return {category: {term_lower: shortcode}} for entries using invalid gemoji shortcodes."""
    invalid = {"ingredients": {}, "cookware": {}}
    if not valid_gemoji:
        return invalid
    emoji_data = yaml_data.get("emoji", {})
    for category in ("ingredients", "cookware"):
        for group in emoji_data.get(category, []):
            for emoji_name, terms in group.items():
                if emoji_name not in valid_gemoji:
                    for term in terms or []:
                        invalid[category][str(term).strip().lower()] = emoji_name
    return invalid


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

    if not shutil.which("cook-docs"):
        print("Error: 'cook-docs' is not installed.", file=sys.stderr)
        sys.exit(1)

    emoji_path = globals().get("EMOJI_YAML_PATH", EMOJI_YAML_PATH)
    if not os.path.exists(emoji_path):
        print(f"Error: {emoji_path} not found")
        sys.exit(1)

    ingredients, cookware = extract_recipe_items(cook_path)
    missing_ingredients, missing_cookware = find_unmapped_with_doctor(
        cook_path, emoji_path, ingredients, cookware
    )

    with open(emoji_path, "r", encoding="utf-8") as f:
        yaml_data = yaml.safe_load(f) or {}

    invalid_gemoji = load_invalid_gemoji_terms(yaml_data, get_valid_gemoji())

    print("Checking recipe ingredients and cookware emojis via cook-docs doctor...")
    print("-" * 50)

    for label, items, cat_key, missing_list in (
        ("Ingredients", ingredients, "ingredients", missing_ingredients),
        ("Cookware", cookware, "cookware", missing_cookware),
    ):
        missing_lower = {m.lower() for m in missing_list}
        print(f"\n{label}:")
        for item in sorted(items):
            bad_code = invalid_gemoji[cat_key].get(item.lower())
            if item.lower() in missing_lower:
                print(f"  \u274c {item:<30} -> MISSING EMOJI")
            elif bad_code:
                print(f"  \u274c {item:<30} -> :{bad_code}: (INVALID GEMOJI SHORTCODE)")
                missing_list.append(item)
            else:
                print(f"  \u2705 {item:<30} -> mapped")

    print("-" * 50)

    if args.fix and (missing_ingredients or missing_cookware):
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
