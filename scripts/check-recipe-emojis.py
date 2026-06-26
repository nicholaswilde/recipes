#!/usr/bin/env python3
import sys
import re
import os
import argparse
import difflib
import subprocess
import yaml

EMOJI_YAML_PATH = "includes/emoji.yaml"

def load_emoji_mappings(filepath):
    mappings = {
        "ingredients": {},
        "cookware": {}
    }
    
    current_category = None
    current_emoji = None
    
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or stripped == "---":
                continue
                
            if stripped == "ingredients:":
                current_category = "ingredients"
                current_emoji = None
                continue
            elif stripped == "cookware:":
                current_category = "cookware"
                current_emoji = None
                continue
                
            m_emoji = re.match(r'^\s*-\s*([^:]+):', line)
            if m_emoji:
                current_emoji = m_emoji.group(1)
                continue
                
            m_item = re.match(r'^\s*-\s*(.+)$', line)
            if m_item and current_category and current_emoji:
                item_name = m_item.group(1).strip('"\'')
                mappings[current_category][item_name.lower()] = current_emoji
                
    return mappings

def find_match(name, category_mappings):
    name_lower = name.lower().strip()
    if name_lower in category_mappings:
        return category_mappings[name_lower]
        
    if name_lower.endswith('s') and name_lower[:-1] in category_mappings:
        return category_mappings[name_lower[:-1]]
    if (name_lower + 's') in category_mappings:
        return category_mappings[name_lower + 's']
        
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
        if any(kw in missing_lower for kw in ["pan", "skillet", "pot", "saucepan", "grill"]):
            return "bowl_with_spoon"
        if any(kw in missing_lower for kw in ["spoon", "whisk", "knife", "fork"]):
            return "bowl_with_spoon"
    return None

def find_best_emoji_group(missing_term, emoji_category_data):
    best_score = 0.0
    best_emoji = None
    
    missing_lower = missing_term.lower().strip()
    missing_words = set(re.findall(r'\w+', missing_lower))
    
    for group in emoji_category_data:
        for emoji_name, terms in group.items():
            for term in terms:
                term_lower = term.lower().strip()
                if term_lower == missing_lower:
                    return emoji_name, 1.0
                    
                # Substring/word overlap check
                term_words = set(re.findall(r'\w+', term_lower))
                has_overlap = False
                for w1 in missing_words:
                    for w2 in term_words:
                        if len(w1) > 3 and len(w2) > 3 and (w1 in w2 or w2 in w1):
                            has_overlap = True
                            break
                if has_overlap:
                    score = 0.8
                    if score > best_score:
                        best_score = score
                        best_emoji = emoji_name
                
                # SequenceMatcher similarity
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
        if category_found and (stripped == "ingredients:" or stripped == "cookware:") and line.startswith("  "):
            break
            
        if category_found and line.rstrip().endswith(f"- {emoji_key}:"):
            # Check indentation to match
            # If the next line is indented, let's match its indentation, otherwise default to 8 spaces
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
        # End of category or file
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

def main():
    parser = argparse.ArgumentParser(description="Check and optionally fix recipe emojis in includes/emoji.yaml")
    parser.add_argument("recipe_path", help="Path to the recipe .cook file")
    parser.add_argument("--fix", action="store_true", help="Automatically map missing emojis in includes/emoji.yaml")
    
    args = parser.parse_args()
    
    cook_path = args.recipe_path
    if not os.path.exists(cook_path):
        print(f"Error: {cook_path} not found")
        sys.exit(1)
        
    with open(cook_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    raw_ingredients = re.findall(r'@(?:([^\n@#{}]+)\{[^}]*\}|(\w+))', content)
    ingredients = set()
    for item in raw_ingredients:
        name = item[0] if item[0] else item[1]
        if name:
            ingredients.add(name.strip())
            
    raw_cookware = re.findall(r'#(?:([^\n@#{}]+)\{[^}]*\}|(\w+))', content)
    cookware = set()
    for item in raw_cookware:
        name = item[0] if item[0] else item[1]
        if name:
            cookware.add(name.strip())
            
    emoji_path = globals().get("EMOJI_YAML_PATH", EMOJI_YAML_PATH)
    if not os.path.exists(emoji_path):
        print(f"Error: {emoji_path} not found")
        sys.exit(1)
        
    mappings = load_emoji_mappings(emoji_path)
    
    missing_ingredients = []
    missing_cookware = []
    
    print("Checking recipe ingredients and cookware emojis...")
    print("-" * 50)
    
    print("\nIngredients:")
    for ing in sorted(ingredients):
        match = find_match(ing, mappings["ingredients"])
        if match:
            print(f"  \u2705 {ing:<30} -> :{match}:")
        else:
            print(f"  \u274c {ing:<30} -> MISSING EMOJI")
            missing_ingredients.append(ing)
            
    print("\nCookware:")
    for cw in sorted(cookware):
        match = find_match(cw, mappings["cookware"])
        if match:
            print(f"  \u2705 {cw:<30} -> :{match}:")
        else:
            print(f"  \u274c {cw:<30} -> MISSING EMOJI")
            missing_cookware.append(cw)
            
    print("-" * 50)
    
    if args.fix and (missing_ingredients or missing_cookware):
        # We need to load raw YAML data to find close matches or structure
        with open(emoji_path, "r", encoding="utf-8") as f:
            yaml_data = yaml.safe_load(f)
            
        print("Auto-fixing missing emoji mappings...")
        
        fixed_count = 0
        
        if missing_ingredients:
            ingredients_data = yaml_data.get("emoji", {}).get("ingredients", [])
            for ing in missing_ingredients:
                best_group = get_heuristic_emoji_group(ing, "ingredients")
                if best_group:
                    print(f"  Heuristic mapped ingredient '{ing}' to group '{best_group}'")
                else:
                    best_group, score = find_best_emoji_group(ing, ingredients_data)
                    if best_group:
                        print(f"  Mapping ingredient '{ing}' to group '{best_group}' (confidence: {score:.2f})")
                    else:
                        best_group = "takeout_box"
                        print(f"  No similar group found for ingredient '{ing}'. Mapping to fallback group '{best_group}'")
                insert_emoji_mapping(emoji_path, "ingredients", best_group, ing)
                fixed_count += 1
                
        if missing_cookware:
            cookware_data = yaml_data.get("emoji", {}).get("cookware", [])
            for cw in missing_cookware:
                best_group = get_heuristic_emoji_group(cw, "cookware")
                if best_group:
                    print(f"  Heuristic mapped cookware '{cw}' to group '{best_group}'")
                else:
                    best_group, score = find_best_emoji_group(cw, cookware_data)
                    if best_group:
                        print(f"  Mapping cookware '{cw}' to group '{best_group}' (confidence: {score:.2f})")
                    else:
                        best_group = "bowl_with_spoon"
                        print(f"  No similar group found for cookware '{cw}'. Mapping to fallback group '{best_group}'")
                insert_emoji_mapping(emoji_path, "cookware", best_group, cw)
                fixed_count += 1
                
        if fixed_count > 0:
            # Run sorting / formatting
            try:
                subprocess.run(["task", "emoji-sort"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception:
                pass
            print(f"Successfully auto-mapped {fixed_count} missing emojis in {emoji_path}!")
            sys.exit(0)
            
    if missing_ingredients or missing_cookware:
        print("Warning: Missing emoji mappings found.")
        if missing_ingredients:
            print(f"Missing ingredients in includes/emoji.yaml: {', '.join(missing_ingredients)}")
        if missing_cookware:
            print(f"Missing cookware in includes/emoji.yaml: {', '.join(missing_cookware)}")
        sys.exit(1)
    else:
        print("All ingredients and cookware are successfully mapped to emojis!")
        sys.exit(0)

if __name__ == "__main__":
    main()
