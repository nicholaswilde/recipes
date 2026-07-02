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

def load_measuring_table(filepath):
    table = {}
    inside_table = False
    
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if stripped.startswith("| Ingredient"):
                inside_table = True
                continue
            if inside_table:
                if not stripped.startswith("|"):
                    if stripped == "":
                        continue
                    if stripped.startswith("#"):
                        inside_table = False
                        continue
                parts = [p.strip() for p in stripped.split("|")]
                if len(parts) >= 5:
                    name = parts[1].strip()
                    name = re.sub(r'\[([^\]]+)\](?:\([^)]+\)|\[[^\]]*\])?', r'\1', name)
                    volume = parts[2].strip()
                    grams = parts[3].strip()
                    
                    if name.startswith("-") or name == "Ingredient":
                        continue
                          
                    try:
                        if grams and grams != "-":
                            grams_val = float(re.findall(r'\d+', grams)[0])
                            table[name.lower()] = { "volume": volume, "grams": grams_val }
                    except Exception:
                        pass
    return table

def find_best_match(name, mappings):
    name_lower = name.lower().strip()
    if name_lower in mappings:
        return mappings[name_lower]
        
    if name_lower.endswith('s') and name_lower[:-1] in mappings:
        return mappings[name_lower[:-1]]
    if (name_lower + 's') in mappings:
        return mappings[name_lower + 's']
        
    def tokenize(s):
        s = re.sub(r'[\(\),\-#]', ' ', s.lower())
        return set(w for w in s.split() if w not in ["and", "or", "with", "of", "in", "for", "chopped", "pitted", "sliced", "slivered", "packed", "extra", "topping", "some"])
        
    name_tokens = tokenize(name_lower)
    if not name_tokens:
        return None
        
    best_key = None
    best_intersection_len = 0
    
    for key in mappings.keys():
        key_tokens = tokenize(key)
        intersection = name_tokens.intersection(key_tokens)
        if len(intersection) > best_intersection_len:
            best_intersection_len = len(intersection)
            best_key = key
        elif len(intersection) == best_intersection_len and best_intersection_len > 0:
            if best_key is None or abs(len(key) - len(name_lower)) < abs(len(best_key) - len(name_lower)):
                best_key = key
                
    if best_key:
        return mappings[best_key]
    return None

def find_best_key(name, table):
    name_lower = name.lower().strip()
    if name_lower in table:
        return name_lower
        
    if name_lower.endswith('s') and name_lower[:-1] in table:
        return name_lower[:-1]
    if (name_lower + 's') in table:
        return name_lower + 's'
        
    def tokenize(s):
        s = re.sub(r'[\(\),\-#]', ' ', s.lower())
        return set(w for w in s.split() if w not in ["and", "or", "with", "of", "in", "for", "chopped", "pitted", "sliced", "slivered", "packed", "extra", "topping", "some"])
        
    name_tokens = tokenize(name_lower)
    if not name_tokens:
        return None
        
    best_key = None
    best_intersection_len = 0
    
    for key in table.keys():
        key_tokens = tokenize(key)
        intersection = name_tokens.intersection(key_tokens)
        if len(intersection) > best_intersection_len:
            best_intersection_len = len(intersection)
            best_key = key
        elif len(intersection) == best_intersection_len and best_intersection_len > 0:
            if best_key is None or abs(len(key) - len(name_lower)) < abs(len(best_key) - len(name_lower)):
                best_key = key
                
    return best_key

def parse_quantity(qty_str):
    qty_str = qty_str.strip()
    parts = qty_str.split()
    total = 0.0
    for part in parts:
        if '/' in part:
            p = part.split('/')
            try:
                total += float(p[0]) / float(p[1])
            except ValueError:
                pass
        else:
            try:
                total += float(part)
            except ValueError:
                pass
    return total

def get_volume_in_cups(qty, unit):
    unit_lower = unit.lower().strip()
    if unit_lower in ["cup", "cups", "c"]:
        return qty
    elif unit_lower in ["tbsp", "tablespoon", "tablespoons"]:
        return qty / 16.0
    elif unit_lower in ["tsp", "teaspoon", "teaspoons"]:
        return qty / 48.0
    elif unit_lower in ["oz", "fl. oz", "fluid oz", "ounces"]:
        return qty / 8.0
    elif unit_lower in ["ml", "milliliter", "milliliters"]:
        return qty / 236.588
    return None

def convert_ingredient(qty_str, unit, name, measuring_table):
    qty = parse_quantity(qty_str)
    if qty == 0.0:
        return None
        
    best_key = find_best_key(name, measuring_table)
    if not best_key:
        return None
        
    conv = measuring_table[best_key]
    m_vol = re.match(r'^(\d+(?:\.\d+)?(?:/\d+)?)\s*(\w+)?', conv["volume"])
    if not m_vol:
        return None
        
    conv_qty = parse_quantity(m_vol.group(1))
    conv_unit = m_vol.group(2) if m_vol.group(2) else "cup"
    
    conv_cups = get_volume_in_cups(conv_qty, conv_unit)
    if not conv_cups or conv_cups == 0.0:
        return None
        
    grams_per_cup = conv["grams"] / conv_cups
    
    current_cups = get_volume_in_cups(qty, unit)
    if not current_cups:
        return None
        
    grams_result = current_cups * grams_per_cup
    return int(round(grams_result))

def main():
    if len(sys.argv) < 2:
        print("Usage: convert_recipe_units.py <recipe.md>")
        sys.exit(1)
        
    md_path = sys.argv[1]
    if not os.path.exists(md_path):
        print(f"Error: {md_path} not found")
        sys.exit(1)
        
    emoji_path = "includes/emoji.yaml"
    measuring_path = "docs/reference/measuring.md"
    
    if not os.path.exists(emoji_path):
        print(f"Error: {emoji_path} not found")
        sys.exit(1)
    if not os.path.exists(measuring_path):
        print(f"Error: {measuring_path} not found")
        sys.exit(1)
        
    emoji_mappings = load_emoji_mappings(emoji_path)
    measuring_table = load_measuring_table(measuring_path)
    
    with open(md_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    updated_lines = []
    inside_ingredients = False
    
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("## :salt: Ingredients") or stripped.startswith("## Ingredients"):
            inside_ingredients = True
            updated_lines.append(line)
            continue
        elif inside_ingredients and stripped.startswith("##"):
            inside_ingredients = False
            
        if inside_ingredients and stripped.startswith("-"):
            clean_line = stripped
            clean_line = re.sub(r'^-\s*:\w+:\s*', '- ', clean_line)
            clean_line = re.sub(r'\s*\(\d+\s*g\)', '', clean_line)
            
            m = re.match(r'^-\s*(?:(\d+(?:\.\d+)?(?:/\d+)?)\s+(\w+)\s+(.+)|(\d+(?:\.\d+)?(?:/\d+)?)\s+(.+)|(.+))$', clean_line)
            if m:
                qty_str, unit, name = None, None, None
                if m.group(1):
                    qty_str, unit, name = m.group(1), m.group(2), m.group(3)
                elif m.group(4):
                    qty_str, unit, name = m.group(4), "", m.group(5)
                else:
                    name = m.group(6)
                    
                name_clean = re.sub(r'^some\s+', '', name).strip()
                emoji = find_best_match(name_clean, emoji_mappings["ingredients"])
                grams = None
                
                if qty_str and unit:
                    grams = convert_ingredient(qty_str, unit, name_clean, measuring_table)
                    
                emoji_str = f":{emoji}: " if emoji else ""
                
                if grams:
                    new_line = f"- {emoji_str}{qty_str} {unit} ({grams} g) {name}\n"
                elif qty_str:
                    unit_str = f" {unit}" if unit else ""
                    new_line = f"- {emoji_str}{qty_str}{unit_str} {name}\n"
                else:
                    new_line = f"- {emoji_str}{name}\n"
                    
                indent = re.match(r'^(\s*)', line).group(1)
                updated_lines.append(indent + new_line)
            else:
                updated_lines.append(line)
        else:
            updated_lines.append(line)
            
    with open(md_path, "w", encoding="utf-8") as f:
        f.writelines(updated_lines)
        
    print(f"Successfully converted and updated ingredients in {md_path}")

if __name__ == "__main__":
    main()
