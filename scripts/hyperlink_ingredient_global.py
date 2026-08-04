#!/usr/bin/env python3

################################################################################
#
# hyperlink_ingredient_global.py
# ----------------
# Globally hyperlink an ingredient in all recipes
#
# @author nιcнolaѕ wιlde, 0x08b7d7a3
# @date 12 Jun 2026
# @version 0.1.0
#
################################################################################

import os
import re
import sys
import argparse

def slugify(text):
    text = text.lower()
    text = re.sub(r'[\s_\-]+', '-', text)
    text = re.sub(r'[^\w\-]', '', text)
    return text.strip('-')

def find_ingredient_file(ingredient_name, docs_dir):
    slug = slugify(ingredient_name)
    for root, dirs, files in os.walk(docs_dir):
        for file in files:
            if not file.endswith(".md"):
                continue
            filepath = os.path.join(root, file)
            
            # Check filename slug match
            file_slug = slugify(os.path.splitext(file)[0])
            if file_slug == slug:
                return filepath
                
            # Fallback: parse H1 title
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    first_lines = [f.readline() for _ in range(20)]
                for line in first_lines:
                    h1_match = re.match(r'^#\s*(?:\:[a-z_]+\:\s*)?(.+)$', line.strip())
                    if h1_match:
                        title = h1_match.group(1).strip()
                        if title.lower() == ingredient_name.lower():
                            return filepath
            except Exception:
                continue
    return None

def add_hyperlink(target_path, ingredient_name, ingredient_file):
    target_dir = os.path.dirname(os.path.abspath(target_path))
    ing_abs_path = os.path.abspath(ingredient_file)
    rel_path = os.path.relpath(ing_abs_path, target_dir)
    
    with open(target_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Match skip targets:
    # 1. Reference definition: ^\[[^\]]+\]:\s*.*$
    # 2. Angle bracket links: <[^>]+>
    # 3. Standard Markdown link: \[[^\]]+\]\([^\)]+\)
    # 4. Reference link: \[[^\]]+\]\[[^\]]*\]
    skip_def = r'(^\[[^\]]+\]:\s*.*$)'
    skip_angle = r'(<[^>]+>)'
    skip_link = r'(\[[^\]]+\]\([^\)]+\))'
    skip_ref = r'(\[[^\]]+\]\[[^\]]*\])'
    ing_pattern = r'\b(' + re.escape(ingredient_name) + r')\b'
    
    combined_pattern = f'{skip_def}|{skip_angle}|{skip_link}|{skip_ref}|{ing_pattern}'
    
    replacements_made = 0
    
    def replace_fn(match):
        nonlocal replacements_made
        # Check if any skip group matched
        if match.group(1) or match.group(2) or match.group(3) or match.group(4):
            return match.group(0)
        else:
            replacements_made += 1
            return f'[{ingredient_name}]({rel_path})'
            
    new_content = re.sub(combined_pattern, replace_fn, content, flags=re.IGNORECASE | re.MULTILINE)
    
    if replacements_made > 0:
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        return replacements_made
    return 0

def main():
    parser = argparse.ArgumentParser(description="Hyperlink an ingredient globally in all recipes that use it.")
    parser.add_argument("--ingredient", required=True, help="Name of the ingredient to hyperlink globally")
    args = parser.parse_args()
    
    docs_dir = "/home/nicholas/git/nicholaswilde/recipes/docs"
    
    ing_file = find_ingredient_file(args.ingredient, docs_dir)
    if not ing_file:
        print(f"Error: Could not find ingredient file for '{args.ingredient}' in {docs_dir}", file=sys.stderr)
        sys.exit(1)
        
    print(f"Found ingredient file: {ing_file}")
    print(f"Scanning all recipes under {docs_dir} for '{args.ingredient}'...")
    
    updated_recipes = []
    
    for root, dirs, files in os.walk(docs_dir):
        # Skip reference guides
        if "reference" in root.split(os.sep):
            continue
            
        for file in files:
            if not file.endswith(".md"):
                continue
                
            filepath = os.path.join(root, file)
            # Skip the ingredient file itself!
            if os.path.abspath(filepath) == os.path.abspath(ing_file):
                continue
                
            # Quick check if ingredient name is in the content before doing heavy regex
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                if args.ingredient.lower() not in content.lower():
                    continue
            except Exception:
                continue
                
            replacements = add_hyperlink(filepath, args.ingredient, ing_file)
            if replacements > 0:
                rel_recipe = os.path.relpath(filepath, docs_dir)
                updated_recipes.append((rel_recipe, replacements))
                print(f"  Updated: {rel_recipe} ({replacements} occurrences)")
                
    print(f"\nDone! Updated {len(updated_recipes)} recipes.")

if __name__ == "__main__":
    main()
