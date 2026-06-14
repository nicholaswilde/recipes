#!/usr/bin/env python3
import sys
import re
import os
import argparse
import json
import urllib.request
import urllib.parse
from bs4 import BeautifulSoup
import yaml

COMMON_UNITS = {
    "cup", "cups", "tbsp", "tablespoon", "tablespoons", "tsp", "teaspoon", "teaspoons",
    "g", "gram", "grams", "ml", "milliliter", "milliliters", "oz", "ounce", "ounces",
    "lb", "pound", "pounds", "kg", "kilogram", "kilograms", "can", "cans", "clove",
    "cloves", "pinch", "pinches", "slice", "slices", "package", "packages", "bag",
    "bags", "canister", "canisters", "jar", "jars", "head", "heads", "bunch", "bunches",
    "sprig", "sprigs", "piece", "pieces", "large", "medium", "small", "handful", "handfuls"
}

COMMON_COOKWARE_KEYWORDS = [
    "bowl", "mixing bowl", "pan", "baking pan", "baking sheet", "saucepan", "pot",
    "skillet", "frying pan", "griddle", "oven", "microwave", "blender", "food processor",
    "stand mixer", "hand mixer", "whisk", "spatula", "wooden spoon", "knife", "cutting board",
    "strainer", "colander", "peeler", "grater", "measuring cup", "measuring spoon",
    "casserole dish", "tart pan", "muffin tin", "loaf pan", "cookie scoop", "wire rack"
]

def parse_iso_duration(duration_str):
    if not duration_str:
        return ""
    m = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration_str)
    if not m:
        return duration_str
    hours, minutes, seconds = m.groups()
    parts = []
    if hours:
        h_val = int(hours)
        parts.append(f"{h_val} hour" + ("s" if h_val != 1 else ""))
    if minutes:
        m_val = int(minutes)
        parts.append(f"{m_val} minute" + ("s" if m_val != 1 else ""))
    return " ".join(parts)

def parse_fraction(val_str):
    val_str = val_str.strip()
    unicode_fractions = {
        '½': 0.5, '⅓': 0.33, '⅔': 0.67, '¼': 0.25, '¾': 0.75,
        '⅕': 0.2, '⅖': 0.4, '⅗': 0.6, '⅘': 0.8, '⅙': 0.17, '⅚': 0.83,
        '⅛': 0.125, '⅜': 0.375, '⅝': 0.625, '⅞': 0.875
    }
    for char, float_val in unicode_fractions.items():
        if char in val_str:
            val_str = val_str.replace(char, f" {float_val}")
            
    parts = val_str.split()
    total = 0.0
    for part in parts:
        if '/' in part:
            try:
                num, denom = part.split('/')
                total += float(num) / float(denom)
            except ValueError:
                pass
        else:
            try:
                total += float(part)
            except ValueError:
                pass
    if total > 0.0:
        if total.is_integer():
            return str(int(total))
        return f"{total:.2f}".rstrip('0').rstrip('.')
    return val_str

def parse_ingredient(ing_line):
    ignored_ingredients = []
    try:
        config_path = os.path.join("cook", "config", "ignored_ingredients.yaml")
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                ignored_ingredients = yaml.safe_load(f) or []
    except Exception:
        pass
        
    ing_line_clean = ing_line.strip()
    for ignored in ignored_ingredients:
        if ing_line_clean.lower() == ignored.lower():
            return ing_line_clean
            
    qty_regex = r'^(\d+(?:\s+\d+/\d+|\s+[½⅓⅔¼¾⅕⅖⅗⅘⅙⅚⅛⅜⅝⅞])?|\d+/\d+|\d+\.\d+|[½⅓⅔¼¾⅕⅖⅗⅘⅙⅚⅛⅜⅝⅞])'
    qty_match = re.match(qty_regex, ing_line_clean)
    
    if not qty_match:
        return f"@{ing_line_clean}{{}}"
        
    qty_raw = qty_match.group(1)
    remaining = ing_line_clean[len(qty_raw):].strip()
    qty = parse_fraction(qty_raw)
    
    words = remaining.split()
    if not words:
        return f"@ingredient{{{qty}}}"
        
    first_word = words[0].lower().rstrip(',')
    unit = ""
    ing_name_words = words
    if first_word in COMMON_UNITS:
        unit = first_word
        ing_name_words = words[1:]
        
    if ing_name_words and ing_name_words[0].lower() == "of":
        ing_name_words = ing_name_words[1:]
        
    name = " ".join(ing_name_words).strip()
    
    notes = ""
    m_notes = re.search(r'\(([^)]+)\)$', name)
    if m_notes:
        notes = m_notes.group(1).strip()
        name = name[:m_notes.start()].strip()
        
    name = name.rstrip(',').strip()
    
    for ignored in ignored_ingredients:
        if name.lower() == ignored.lower():
            return ing_line_clean
            
    unit_part = f"%{unit}" if unit else ""
    notes_part = f" ({notes})" if notes else ""
    
    return f"@{name}{{{qty}{unit_part}}}{notes_part}"

def format_time_range(text):
    pattern_range = r'(\d+)\s*(?:-|to)\s*(\d+)\s*(minutes|minute|hours|hour|seconds|second|secs|sec)'
    m_range = re.search(pattern_range, text, re.IGNORECASE)
    if m_range:
        num1, num2, unit = m_range.groups()
        replacement = f"{num1} to ~{{{num2}%{unit}}}"
        return re.sub(pattern_range, replacement, text, flags=re.IGNORECASE)
        
    pattern_single = r'(about|approx|approximately)\s*(\d+)\s*(minutes|minute|hours|hour|seconds|second|secs|sec)'
    m_single = re.search(pattern_single, text, re.IGNORECASE)
    if m_single:
        prefix, num, unit = m_single.groups()
        replacement = f"{prefix} ~{{{num}%{unit}}}"
        return re.sub(pattern_single, replacement, text, flags=re.IGNORECASE)
        
    return text

def resolve_category(category_name):
    if not category_name:
        return "main"
    category_lower = category_name.lower().strip()
    
    if any(kw in category_lower for kw in ["dessert", "sweet", "cake", "cookie", "bar"]):
        if any(kw in category_lower for kw in ["cookie", "bar"]):
            return "cookies-and-bars"
        return "desserts"
    if any(kw in category_lower for kw in ["bread", "bun", "dough", "roll"]):
        return "breads"
    if any(kw in category_lower for kw in ["breakfast", "brunch", "waffle", "pancake"]):
        return "breakfast"
    if any(kw in category_lower for kw in ["drink", "beverage", "cocktail", "smoothie"]):
        return "beverages"
    if any(kw in category_lower for kw in ["sauce", "dressing", "dip", "salsa", "gravy"]):
        return "sauces-and-dressings"
    if any(kw in category_lower for kw in ["soup", "stew", "chowder", "chili"]):
        return "soups-and-stews"
    if any(kw in category_lower for kw in ["salad", "side", "appetizer", "snack"]):
        return "sides"
    if any(kw in category_lower for kw in ["lunch"]):
        return "lunches"
    if any(kw in category_lower for kw in ["mediterranean"]):
        return "mediterranean"
        
    return "main"

def fetch_html(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as response:
        return response.read().decode('utf-8')

def find_recipe_in_json(data):
    if isinstance(data, dict):
        if data.get("@type") == "Recipe" or data.get("@type") == ["Recipe"]:
            return data
        for k, v in data.items():
            if k == "@graph" and isinstance(v, list):
                for item in v:
                    recipe = find_recipe_in_json(item)
                    if recipe:
                        return recipe
            elif isinstance(v, (dict, list)):
                recipe = find_recipe_in_json(v)
                if recipe:
                    return recipe
    elif isinstance(data, list):
        for item in data:
            recipe = find_recipe_in_json(item)
            if recipe:
                return recipe
    return None

def extract_json_ld_recipe(html):
    soup = BeautifulSoup(html, "html.parser")
    scripts = soup.find_all("script", type="application/ld+json")
    for script in scripts:
        try:
            data = json.loads(script.string or "")
            recipe = find_recipe_in_json(data)
            if recipe:
                return recipe
        except Exception:
            continue
    return None

def parse_instructions(instructions_data):
    steps = []
    if isinstance(instructions_data, str):
        steps.append(instructions_data)
    elif isinstance(instructions_data, list):
        for item in instructions_data:
            if isinstance(item, str):
                steps.append(item)
            elif isinstance(item, dict):
                if item.get("@type") == "HowToSection":
                    elements = item.get("itemListElement") or []
                    for elem in elements:
                        if isinstance(elem, dict) and elem.get("@type") == "HowToStep":
                            steps.append(elem.get("text") or elem.get("name") or "")
                elif item.get("@type") == "HowToStep":
                    steps.append(item.get("text") or item.get("name") or "")
                elif "text" in item:
                    steps.append(item.get("text") or "")
    return [s.strip() for s in steps if s.strip()]

def extract_wprm_recipe(html):
    soup = BeautifulSoup(html, "html.parser")
    recipe_container = soup.find(class_="wprm-recipe-container")
    if not recipe_container:
        return None
        
    recipe = {}
    name_el = recipe_container.find(class_="wprm-recipe-name")
    recipe["name"] = name_el.get_text(strip=True) if name_el else "Unknown Recipe"
    
    servings_el = recipe_container.find(class_="wprm-recipe-servings")
    recipe["servings"] = servings_el.get_text(strip=True) if servings_el else ""
    
    prep_el = recipe_container.find(class_="wprm-recipe-prep_time")
    recipe["prep_time"] = prep_el.get_text(strip=True) if prep_el else ""
    cook_el = recipe_container.find(class_="wprm-recipe-cook_time")
    recipe["cook_time"] = cook_el.get_text(strip=True) if cook_el else ""
    total_el = recipe_container.find(class_="wprm-recipe-total_time")
    recipe["total_time"] = total_el.get_text(strip=True) if total_el else ""
    
    image_el = recipe_container.find("img")
    image_url = ""
    if image_el:
        image_url = image_el.get("data-lazy-src") or image_el.get("src") or ""
    recipe["image_url"] = image_url
    
    ingredients = []
    ing_elements = recipe_container.find_all(class_="wprm-recipe-ingredient")
    for ing in ing_elements:
        amount_el = ing.find(class_="wprm-recipe-ingredient-amount")
        unit_el = ing.find(class_="wprm-recipe-ingredient-unit")
        name_el = ing.find(class_="wprm-recipe-ingredient-name")
        notes_el = ing.find(class_="wprm-recipe-ingredient-notes")
        
        amount = amount_el.get_text(strip=True) if amount_el else ""
        unit = unit_el.get_text(strip=True) if unit_el else ""
        name = name_el.get_text(strip=True) if name_el else ""
        notes = notes_el.get_text(strip=True) if notes_el else ""
        
        full_ing = f"{amount} {unit} {name}".replace("  ", " ").strip()
        if notes:
            full_ing += f" ({notes})"
        ingredients.append(full_ing)
    recipe["ingredients"] = ingredients
    
    instructions = []
    inst_elements = recipe_container.find_all(class_="wprm-recipe-instruction")
    for inst in inst_elements:
        text_el = inst.find(class_="wprm-recipe-instruction-text")
        text = text_el.get_text(strip=True) if text_el else inst.get_text(strip=True)
        instructions.append(text)
    recipe["instructions"] = instructions
    
    return recipe

def download_image(url, output_path):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as response:
        with open(output_path, "wb") as f:
            f.write(response.read())

def tag_cookware(step_text):
    keywords = sorted(COMMON_COOKWARE_KEYWORDS, key=len, reverse=True)
    for kw in keywords:
        pattern = rf'(?<![#@])\b{re.escape(kw)}\b'
        step_text = re.sub(pattern, f"#{kw}{{}}", step_text, flags=re.IGNORECASE)
    return step_text

def compile_cooklang(recipe_data, source_url):
    lines = []
    lines.append(f">> source: {source_url}")
    
    servings = recipe_data.get("servings")
    if servings:
        lines.append(f">> serves: {servings}")
        
    prep_time = recipe_data.get("prep_time")
    if prep_time:
        lines.append(f">> prep time: {prep_time}")
    cook_time = recipe_data.get("cook_time")
    if cook_time:
        lines.append(f">> cook time: {cook_time}")
    total_time = recipe_data.get("total_time")
    if total_time:
        lines.append(f">> total time: {total_time}")
        
    lines.append("")
    
    # Declarations of all ingredients at the beginning (commented out)
    parsed_ingredients = []
    raw_ing_names = []
    for ing in recipe_data.get("ingredients", []):
        parsed = parse_ingredient(ing)
        parsed_ingredients.append(parsed)
        # Extract name from @name{...} format to tag in steps
        m_name = re.match(r'^@([^{]+)\{', parsed)
        if m_name:
            raw_ing_names.append(m_name.group(1))
            
    for parsed in parsed_ingredients:
        lines.append(parsed)
        
    lines.append("")
    
    # Instruction steps
    # Sort names by length descending to replace longest names first
    raw_ing_names = sorted(list(set(raw_ing_names)), key=len, reverse=True)
    
    for step in recipe_data.get("instructions", []):
        step_clean = format_time_range(step)
        step_clean = tag_cookware(step_clean)
        
        # Tag ingredients in steps
        for ing_name in raw_ing_names:
            pattern = rf'(?<![#@])\b{re.escape(ing_name)}\b'
            step_clean = re.sub(pattern, f"@{ing_name}", step_clean, flags=re.IGNORECASE)
            
        lines.append(step_clean)
        lines.append("")
        
    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(description="Scrape a recipe from a URL and save as CookLang (.cook) and image.")
    parser.add_argument("url", help="Recipe webpage URL")
    parser.add_argument("-c", "--category", help="Category folder override")
    
    args = parser.parse_args()
    
    print(f"Fetching {args.url}...")
    html = fetch_html(args.url)
    
    # 1. Try JSON-LD Recipe
    recipe_data = None
    recipe_json = extract_json_ld_recipe(html)
    if recipe_json:
        recipe_data = {}
        recipe_data["name"] = recipe_json.get("name") or "Unknown Recipe"
        
        yield_val = recipe_json.get("recipeYield")
        if isinstance(yield_val, list) and yield_val:
            yield_val = yield_val[0]
        servings = ""
        if yield_val:
            m = re.search(r'\d+', str(yield_val))
            if m:
                servings = m.group(0)
        recipe_data["servings"] = servings
        
        recipe_data["prep_time"] = parse_iso_duration(recipe_json.get("prepTime"))
        recipe_data["cook_time"] = parse_iso_duration(recipe_json.get("cookTime"))
        recipe_data["total_time"] = parse_iso_duration(recipe_json.get("totalTime"))
        
        img_data = recipe_json.get("image")
        image_url = ""
        if isinstance(img_data, list) and img_data:
            image_url = img_data[0]
        elif isinstance(img_data, dict):
            image_url = img_data.get("url") or ""
        elif isinstance(img_data, str):
            image_url = img_data
        if image_url:
            recipe_data["image_url"] = urllib.parse.urljoin(args.url, image_url)
        else:
            recipe_data["image_url"] = ""
            
        recipe_data["ingredients"] = recipe_json.get("recipeIngredient") or []
        recipe_data["instructions"] = parse_instructions(recipe_json.get("recipeInstructions"))
        
        category_json = recipe_json.get("recipeCategory")
        if isinstance(category_json, list) and category_json:
            category_json = category_json[0]
        recipe_data["category"] = str(category_json or "")
        print("Successfully parsed recipe via JSON-LD Schema.")
        
    if not recipe_data or not recipe_data.get("ingredients"):
        # 2. Try Fallback WPRM BeautifulSoup
        print("JSON-LD parse did not return a valid recipe. Trying WPRM BeautifulSoup fallback...")
        recipe_data = extract_wprm_recipe(html)
        
    if not recipe_data or not recipe_data.get("ingredients"):
        print("Error: Could not parse recipe from the webpage.")
        sys.exit(1)
        
    # Resolve category
    category = args.category
    if not category:
        category = resolve_category(recipe_data.get("category") or recipe_data.get("name"))
        
    # Format Title/Filename (clean special characters)
    title = recipe_data.get("name")
    filename = "".join(c for c in title if c.isalnum() or c in " -_").strip()
    
    # Directories
    target_dir = os.path.join("cook", category)
    os.makedirs(target_dir, exist_ok=True)
    
    cook_path = os.path.join(target_dir, f"{filename}.cook")
    jpg_path = os.path.join(target_dir, f"{filename}.jpg")
    
    # Save Cooklang file
    cook_content = compile_cooklang(recipe_data, args.url)
    with open(cook_path, "w", encoding="utf-8") as f:
        f.write(cook_content)
    print(f"Saved Cooklang recipe to {cook_path}")
    
    # Save Image
    image_url = recipe_data.get("image_url")
    if image_url:
        try:
            print(f"Downloading recipe image from {image_url}...")
            download_image(image_url, jpg_path)
            print(f"Saved image to {jpg_path}")
        except Exception as e:
            print(f"Warning: Could not download image: {e}")
            
    print("Recipe import complete!")

if __name__ == "__main__":
    main()
