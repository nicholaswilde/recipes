#!/usr/bin/env python3
import sys
import re
import os

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

def main():
    if len(sys.argv) < 2:
        print("Usage: check-recipe-emojis.py <recipe.cook>")
        sys.exit(1)
        
    cook_path = sys.argv[1]
    if not os.path.exists(cook_path):
        print(f"Error: {cook_path} not found")
        sys.exit(1)
        
    with open(cook_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    raw_ingredients = re.findall(r'@(?:([^{]+)\{[^}]*\}|(\w+))', content)
    ingredients = set()
    for item in raw_ingredients:
        name = item[0] if item[0] else item[1]
        if name:
            ingredients.add(name.strip())
            
    raw_cookware = re.findall(r'#(?:([^{]+)\{[^}]*\}|(\w+))', content)
    cookware = set()
    for item in raw_cookware:
        name = item[0] if item[0] else item[1]
        if name:
            cookware.add(name.strip())
            
    emoji_yaml_path = "includes/emoji.yaml"
    if not os.path.exists(emoji_yaml_path):
        print(f"Error: {emoji_yaml_path} not found")
        sys.exit(1)
        
    mappings = load_emoji_mappings(emoji_yaml_path)
    
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
