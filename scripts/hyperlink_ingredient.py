#!/usr/bin/env python3
import os
import re
import sys
import argparse

def slugify(text):
    # Convert to lowercase, replace spaces/special chars with hyphens
    text = text.lower()
    text = re.sub(r'[\s_\-]+', '-', text)
    text = re.sub(r'[^\w\-]', '', text)
    return text.strip('-')

def find_ingredient_file(ingredient_name, docs_dir):
    # Try finding by H1 title first
    slug = slugify(ingredient_name)
    best_match = None
    
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
                    # Match H1 title e.g. "# :egg: Sambal Oelek"
                    h1_match = re.match(r'^#\s*(?:\:[a-z_]+\:\s*)?(.+)$', line.strip())
                    if h1_match:
                        title = h1_match.group(1).strip()
                        if title.lower() == ingredient_name.lower():
                            return filepath
            except Exception:
                continue
                
    return None

def add_hyperlink(target_path, ingredient_name, ingredient_file):
    # Calculate relative path
    target_dir = os.path.dirname(os.path.abspath(target_path))
    ing_abs_path = os.path.abspath(ingredient_file)
    rel_path = os.path.relpath(ing_abs_path, target_dir)
    
    # Read target content
    with open(target_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Regex to find ingredient name NOT inside markdown link syntax
    # We want to match 'ingredient_name' but NOT if preceded by '[' or followed by ']'
    # Using negative lookbehind/lookahead is tricky for multi-word, so we can use a simpler pattern
    # Let's match: [something](link) OR [something] OR (ingredient)
    # Actually, we can use a regex replacement function that skips matches inside markdown links.
    # The pattern matches markdown links: \[([^\]]+)\]\([^\)]+\) OR \[([^\]]+)\]
    # And we also match our raw ingredient name.
    
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
        print(f"Successfully hyperlinked '{ingredient_name}' to {rel_path} ({replacements_made} occurrences replaced).")
        return True
    else:
        print(f"No unlinked occurrences of '{ingredient_name}' found in {target_path}.")
        return False

def main():
    parser = argparse.ArgumentParser(description="Hyperlink an ingredient in a recipe markdown file.")
    parser.add_argument("--target", required=True, help="Path to the recipe file to modify")
    parser.add_argument("--ingredient", required=True, help="Name of the ingredient to hyperlink")
    args = parser.parse_args()
    
    docs_dir = "/home/nicholas/git/nicholaswilde/recipes/docs"
    
    if not os.path.exists(args.target):
        print(f"Error: Target file not found: {args.target}", file=sys.stderr)
        sys.exit(1)
        
    ing_file = find_ingredient_file(args.ingredient, docs_dir)
    if not ing_file:
        print(f"Error: Could not find ingredient file for '{args.ingredient}' in {docs_dir}", file=sys.stderr)
        sys.exit(1)
        
    success = add_hyperlink(args.target, args.ingredient, ing_file)
    if not success:
        sys.exit(2)
        
if __name__ == "__main__":
    main()
