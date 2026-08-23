#!/usr/bin/env python3

################################################################################
#
# auto_hyperlink_recipe.py
# ----------------
# Auto-hyperlink all ingredients within a single recipe markdown file that have
# corresponding ingredient/sauce pages in the repository.
#
# @author nιcнolaѕ wιlde, 0x08b7d7a3
# @date 23 Aug 2026
# @version 0.1.0
#
################################################################################

import os
import re
import sys
import argparse
import subprocess

def slugify(text):
    text = text.lower()
    text = re.sub(r'[\s_\-]+', '-', text)
    text = re.sub(r'[^\w\-]', '', text)
    return text.strip('-')

def build_ingredient_dict(docs_dir):
    """
    Builds a dictionary of all potential ingredient/sauce files.
    Maps normalized name -> absolute file path.
    Only scans specific directories that act as ingredients.
    """
    ingredient_dirs = [
        "ingredients",
        "sauces-and-dressings",
        "breads"
    ]
    
    ing_map = {}
    
    for idir in ingredient_dirs:
        dir_path = os.path.join(docs_dir, idir)
        if not os.path.exists(dir_path):
            continue
            
        for root, dirs, files in os.walk(dir_path):
            for file in files:
                if not file.endswith(".md"):
                    continue
                filepath = os.path.join(root, file)
                
                # Check filename slug match
                base_name = os.path.splitext(file)[0]
                
                # Fallback: parse H1 title
                title = base_name.replace('-', ' ')
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        for i in range(20):
                            line = f.readline()
                            if not line:
                                break
                            h1_match = re.match(r'^#\s*(?:\:[a-z_]+\:\s*)?(.+)$', line.strip())
                            if h1_match:
                                title = h1_match.group(1).strip()
                                break
                except Exception:
                    pass
                
                # Register both title and base_name
                ing_map[title.lower()] = filepath
                ing_map[base_name.lower()] = filepath
                
    return ing_map

def add_hyperlinks(target_path, ing_map):
    # Read target content
    with open(target_path, "r", encoding="utf-8") as f:
        content = f.read()

    target_dir = os.path.dirname(os.path.abspath(target_path))
    
    # We want to find which ingredients are present in this file.
    # We sort keys by length descending to match longest phrases first
    sorted_keys = sorted(ing_map.keys(), key=len, reverse=True)
    
    # Exclude the current file's own title/basename
    current_basename = os.path.splitext(os.path.basename(target_path))[0].lower()
    
    # Regex to extract ingredient list to know what to search for (optional, but let's just search the whole text)
    skip_def = r'(^\[[^\]]+\]:\s*.*$)'
    skip_angle = r'(<[^>]+>)'
    skip_link = r'(\[[^\]]+\]\([^\)]+\))'
    skip_ref = r'(\[[^\]]+\]\[[^\]]*\])'

    replacements_made = 0
    new_content = content
    
    for ing_name in sorted_keys:
        if ing_name == current_basename or len(ing_name) <= 2:
            continue
            
        # Check if the ingredient name exists in the content (case insensitive)
        if not re.search(r'\b' + re.escape(ing_name) + r'\b', new_content, re.IGNORECASE):
            continue
            
        ing_abs_path = os.path.abspath(ing_map[ing_name])
        if os.path.abspath(target_path) == ing_abs_path:
            continue
            
        rel_path = os.path.relpath(ing_abs_path, target_dir)
        
        # Determine the display name (title case or matching case)
        ing_pattern = r'\b(' + re.escape(ing_name) + r')\b'
        combined_pattern = f'{skip_def}|{skip_angle}|{skip_link}|{skip_ref}|{ing_pattern}'
        
        def replace_fn(match):
            nonlocal replacements_made
            if match.group(1) or match.group(2) or match.group(3) or match.group(4):
                return match.group(0)
            else:
                replacements_made += 1
                matched_text = match.group(5)
                # Keep the original capitalization of the matched text
                return f'[{matched_text}]({rel_path})'
                
        new_content = re.sub(combined_pattern, replace_fn, new_content, flags=re.IGNORECASE | re.MULTILINE)
    
    if replacements_made > 0:
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"Successfully auto-hyperlinked ingredients in {target_path} ({replacements_made} replacements).")
        return True
    else:
        print(f"No ingredients to auto-hyperlink found in {target_path}.")
        return False

def format_with_rumdl(target_path):
    try:
        subprocess.run(["rumdl", "fmt", target_path], check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        print(f"Warning: rumdl fmt failed for {target_path}", file=sys.stderr)

def main():
    parser = argparse.ArgumentParser(description="Auto-hyperlink ingredients in a recipe markdown file.")
    parser.add_argument("target", help="Path to the recipe file to modify")
    args = parser.parse_args()
    
    if not os.path.exists(args.target):
        print(f"Error: Target file not found: {args.target}", file=sys.stderr)
        sys.exit(1)
        
    # Assume script is run from project root
    docs_dir = os.path.abspath("docs")
    
    ing_map = build_ingredient_dict(docs_dir)
    success = add_hyperlinks(args.target, ing_map)
    
    if success:
        format_with_rumdl(args.target)
        
if __name__ == "__main__":
    main()
