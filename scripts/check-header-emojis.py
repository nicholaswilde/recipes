#!/usr/bin/env python3
import os
import re
import sys
import argparse
import subprocess
import yaml

EMOJI_YAML_PATH = "includes/emoji.yaml"

CATEGORY_EMOJIS = {
    "beverages": "clinking_glasses",
    "cookies-and-bars": "cookie",
    "desserts": "cake",
    "breads": "bread",
    "breakfast": "egg",
    "main": "shallow_pan_of_food",
    "sides": "salad_bowl",
    "sauces-and-dressings": "takeout_box",
    "soups-and-stews": "stew",
    "lunches": "sandwich",
    "salads": "green_salad",
}

HEURISTIC_EMOJIS = {
    "corn": "corn",
    "succotash": "corn",
    "bean": "beans",
    "beans": "beans",
    "onion": "onion",
    "garlic": "garlic",
    "tomato": "tomato",
    "tomatoes": "tomato",
    "pepper": "hot_pepper",
    "chili": "hot_pepper",
    "chilli": "hot_pepper",
    "jalapeño": "hot_pepper",
    "basil": "herb",
    "parsley": "herb",
    "cilantro": "herb",
    "rosemary": "herb",
    "thyme": "herb",
    "oregano": "herb",
    "beef": "meat_on_bone",
    "chicken": "poultry_leg",
    "pork": "pig",
    "bacon": "bacon",
    "cookie": "cookie",
    "cookies": "cookie",
    "cake": "cake",
    "bread": "bread",
    "bun": "bread",
    "buns": "bread",
    "roll": "bread",
    "rolls": "bread",
    "soup": "stew",
    "stew": "stew",
    "salad": "green_salad",
    "curry": "curry",
    "pie": "pie",
    "tart": "pie",
    "mousse": "custard",
    "pudding": "custard",
    "custard": "custard",
    "mustard": "takeout_box",
    "pickle": "cucumber",
    "pickles": "cucumber",
    "pickled": "cucumber",
    "potato": "potato",
    "potatoes": "potato",
    "sweet potato": "sweet_potato",
    "sweet potatoes": "sweet_potato",
    "egg": "egg",
    "eggs": "egg",
    "cheese": "cheese_wedge",
    "cream": "glass_of_milk",
    "milk": "glass_of_milk",
    "butter": "butter",
    "lemon": "lemon",
    "lime": "lemon",
    "orange": "tangerine",
    "apple": "apple",
    "apples": "apple",
    "banana": "banana",
    "bananas": "banana",
    "strawberry": "strawberry",
    "strawberries": "strawberry",
    "blueberry": "blue_circle",
    "blueberries": "blue_circle",
    "chocolate": "chocolate_bar",
    "cocoa": "chocolate_bar",
    "peanut": "peanut",
    "peanuts": "peanut",
    "cashew": "chestnut",
    "cashews": "chestnut",
    "walnut": "chestnut",
    "walnuts": "chestnut",
    "almond": "chestnut",
    "almonds": "chestnut",
    "tofu": "takeout_box",
    "rice": "rice",
    "noodle": "spaghetti",
    "noodles": "spaghetti",
    "pasta": "spaghetti",
}

def load_emoji_mappings(filepath):
    try:
        if not os.path.exists(filepath):
            return {}
        with open(filepath, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        emoji_data = data.get("emoji", {})
        
        mappings = {}
        for item in emoji_data.get("cookware", []):
            for emoji_name, terms in item.items():
                for term in terms:
                    mappings[str(term).lower().strip()] = emoji_name
        for item in emoji_data.get("ingredients", []):
            for emoji_name, terms in item.items():
                for term in terms:
                    mappings[str(term).lower().strip()] = emoji_name
        return mappings
    except Exception as e:
        print(f"Warning: could not load emoji mappings: {e}")
        return {}

def check_file(file_path):
    """
    Checks if a markdown file's H1 header has an emoji shortcode.
    Returns (is_valid, emoji_shortcode_or_none, h1_title or error_message)
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("# "):
                    h1_title = line[2:].strip()
                    m = re.match(r"^:([a-zA-Z0-9_+-]+):", h1_title)
                    if m:
                        return True, m.group(1), h1_title
                    else:
                        return False, None, h1_title
            return False, None, "No H1 header found"
    except Exception as e:
        return False, None, f"Error reading file: {e}"

def suggest_emoji(file_path, mappings):
    # Extract title
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
        
    title_clean = re.sub(r':[a-zA-Z0-9_+-]+:', '', title)
    title_words = [w.lower() for w in re.findall(r'\w+', title_clean)]
    
    # 1. Try to find match in title words against our heuristic list
    for word in title_words:
        if word in HEURISTIC_EMOJIS:
            return HEURISTIC_EMOJIS[word]
            
    # 2. Try to find match in title words against emoji.yaml
    for word in title_words:
        if word in mappings:
            return mappings[word]
            
    # 3. Try to find matching ingredient in the file's ingredient section
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
                
                ing_line = re.sub(r'^-\s*', '', stripped)
                ing_line_lower = ing_line.lower()
                
                # Check against heuristic list
                for kw, emoji_name in HEURISTIC_EMOJIS.items():
                    if kw in ing_line_lower:
                        return emoji_name
                        
                # Check against mappings list, sorting by length descending to get most specific first
                matches = []
                for term, emoji_name in mappings.items():
                    if len(term) <= 3 or term in ["fresh", "chopped", "ground", "dried", "water", "salt", "pepper", "oil", "butter"]:
                        continue
                    if term in ing_line_lower:
                        matches.append((term, emoji_name))
                if matches:
                    matches.sort(key=lambda x: len(x[0]), reverse=True)
                    return matches[0][1]
    except Exception:
        pass
        
    # 4. Fallback to category
    parts = file_path.split(os.sep)
    category = parts[1] if len(parts) > 2 else "main"
    return CATEGORY_EMOJIS.get(category, "shallow_pan_of_food")

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
        if category_found and (stripped == "ingredients:" or stripped == "cookware:") and line.startswith("  "):
            break
            
        if category_found and line.rstrip().endswith(f"- {emoji_key}:"):
            indent = "        "
            if i + 1 < len(lines):
                next_line = lines[i + 1]
                m_indent = re.match(r'^(\s+)-', next_line)
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
            elif category_index != -1 and (stripped == "ingredients:" or stripped == "cookware:") and line.startswith("  "):
                next_category_index = i
                break
                
        insert_pos = next_category_index if next_category_index != -1 else len(lines)
        new_group_lines = [
            f"    - {emoji_key}:\n",
            f"        - {new_term}\n"
        ]
        for offset, gl in enumerate(new_group_lines):
            lines.insert(insert_pos + offset, gl)
            
    with open(filepath, "w", encoding="utf-8") as f:
        f.writelines(lines)

def fix_file(file_path, suggested_emoji):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        lines = content.splitlines()
        for idx, line in enumerate(lines):
            if line.startswith("# "):
                title = line[2:].strip()
                new_line = f"# :{suggested_emoji}: {title}"
                lines[idx] = new_line
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
    parser.add_argument("--fix", action="store_true", help="Automatically insert suggested H1 emoji if missing and register in includes/emoji.yaml")
    parser.add_argument("-v", "--verbose", action="store_true", help="Show all checked files with their emojis")
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

    emoji_mappings = load_emoji_mappings(EMOJI_YAML_PATH)
    # Get all uniquely defined emoji shortcodes in emoji.yaml keys
    try:
        with open(EMOJI_YAML_PATH, "r", encoding="utf-8") as f:
            yaml_data = yaml.safe_load(f)
        emoji_data = yaml_data.get("emoji", {})
        allowed_emojis = set()
        for item in emoji_data.get("cookware", []):
            allowed_emojis.update(item.keys())
        for item in emoji_data.get("ingredients", []):
            allowed_emojis.update(item.keys())
    except Exception:
        allowed_emojis = set()

    missing_emoji_files = []
    unregistered_emoji_files = []
    total_checked = 0
    fixed_count = 0
    emoji_yaml_modified = False

    for file_path in sorted(files_to_check):
        total_checked += 1
        is_valid, emoji, title = check_file(file_path)
        
        if is_valid:
            # Check if the emoji used is present in emoji.yaml
            if emoji in allowed_emojis:
                if args.verbose:
                    print(f"  \u2705 {file_path}: :{emoji}: (Mapped in emoji.yaml)")
            else:
                if args.fix:
                    print(f"  \u274c {file_path}: H1 emoji :{emoji}: not registered in emoji.yaml. Registering ... ", end="")
                    clean_title = re.sub(r':[a-zA-Z0-9_+-]+:', '', title).strip()
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
                    # Register the new emoji mapping if not already in emoji.yaml
                    if suggestion not in allowed_emojis:
                        print(f"Registering :{suggestion}: in emoji.yaml ... ", end="")
                        clean_title = re.sub(r':[a-zA-Z0-9_+-]+:', '', title).strip()
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
        # Run sorting
        try:
            subprocess.run(["task", "emoji-sort"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass

    print(f"\nChecked {total_checked} markdown file(s).")
    
    if args.fix:
        print(f"Successfully fixed/registered H1 emojis in {fixed_count} recipe files!")
        sys.exit(0)
        
    has_errors = False
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
    else:
        print("All checked recipes contain a registered H1 header emoji!")
        sys.exit(0)

if __name__ == "__main__":
    main()
