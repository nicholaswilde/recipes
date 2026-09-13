#!/usr/bin/env python3
import sys
import os
import yaml

def read_frontmatter_and_body(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            fm_text = parts[1]
            body = parts[2]
            try:
                fm = yaml.safe_load(fm_text) or {}
                return fm, body
            except Exception as e:
                print(f"Error parsing YAML in {filepath}: {e}")
                return {}, content
    return {}, content

def main():
    if len(sys.argv) != 3:
        print("Usage: inject_frontmatter.py <cook_file> <md_file>")
        sys.exit(1)
        
    cook_file = sys.argv[1]
    md_file = sys.argv[2]
    
    if not os.path.exists(cook_file) or not os.path.exists(md_file):
        print(f"File not found. cook: {cook_file}, md: {md_file}")
        sys.exit(0)
        
    cook_fm, _ = read_frontmatter_and_body(cook_file)
    md_fm, md_body = read_frontmatter_and_body(md_file)
    
    if not cook_fm:
        print("No frontmatter found in cook file.")
        return
        
    for k, v in cook_fm.items():
        if k == 'tags':
            existing_tags = md_fm.get('tags', [])
            if not isinstance(existing_tags, list):
                existing_tags = []
            
            new_tags = v if isinstance(v, list) else []
            merged_tags = existing_tags.copy()
            for tag in new_tags:
                if tag not in merged_tags:
                    merged_tags.append(tag)
            md_fm['tags'] = merged_tags
        else:
            # We don't necessarily want to bring 'title', 'category' into md frontmatter 
            # if we don't want them, but it doesn't hurt. 
            # Let's drop 'title' and 'category' to keep it clean like standard recipes.
            if k not in ['title', 'category']:
                md_fm[k] = v
            
    if 'comments' not in md_fm:
        md_fm['comments'] = True
        
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write('---\n')
        yaml.dump(md_fm, f, default_flow_style=False, sort_keys=False)
        f.write('---')
        if not md_body.startswith('\n'):
            f.write('\n')
        f.write(md_body)
    
    print(f"Successfully injected frontmatter from {cook_file} into {md_file}")

if __name__ == "__main__":
    main()
