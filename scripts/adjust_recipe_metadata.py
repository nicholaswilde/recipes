#!/usr/bin/env python3
import sys
import os
import argparse
import yaml

def parse_args():
    parser = argparse.ArgumentParser(description="Adjust recipe metadata, tags, and frontmatter.")
    parser.add_argument("file", help="Path to the recipe markdown file.")
    parser.add_argument("--add-tags", help="Comma-separated list of tags to add.")
    parser.add_argument("--remove-tags", help="Comma-separated list of tags to remove.")
    parser.add_argument("--set-metadata", help="Comma-separated key=value pairs to set in frontmatter (e.g., comments=true,hero=path/to/image.webp).")
    return parser.parse_args()

def parse_metadata_value(val_str):
    val_str_lower = val_str.strip().lower()
    if val_str_lower == "true":
        return True
    if val_str_lower == "false":
        return False
    try:
        if "." in val_str:
            return float(val_str)
        return int(val_str)
    except ValueError:
        return val_str.strip()

def main():
    args = parse_args()
    
    if not os.path.exists(args.file):
        print(f"Error: File '{args.file}' not found.")
        sys.exit(1)
        
    with open(args.file, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Split frontmatter and markdown body
    # Frontmatter is defined between the first two '---' lines
    parts = content.split("---", 2)
    if len(parts) < 3:
        # No frontmatter found, let's initialize empty frontmatter
        frontmatter = {}
        body = content
    else:
        frontmatter_str = parts[1]
        body = parts[2]
        try:
            frontmatter = yaml.safe_load(frontmatter_str) or {}
        except yaml.YAMLError as e:
            print(f"Error parsing YAML frontmatter: {e}")
            sys.exit(1)
            
    # Process Tags
    tags = frontmatter.get("tags") or []
    if not isinstance(tags, list):
        tags = [tags] if tags else []
    # Convert all current tags to strings
    tags = [str(t).strip() for t in tags]
    
    # Add tags
    if args.add_tags:
        new_tags = [t.strip() for t in args.add_tags.split(",") if t.strip()]
        for tag in new_tags:
            if tag not in tags:
                tags.append(tag)
                
    # Remove tags
    if args.remove_tags:
        tags_to_remove = [t.strip() for t in args.remove_tags.split(",") if t.strip()]
        tags = [t for t in tags if t not in tags_to_remove]
        
    # Update frontmatter tags (remove the key entirely if tags list is empty, or set it)
    if tags:
        frontmatter["tags"] = tags
    elif "tags" in frontmatter:
        # Keep empty tags list or remove it?
        # Zensical standard usually includes empty tags or removes it. Let's set it to None or remove it.
        frontmatter["tags"] = None
        
    # Process other metadata
    if args.set_metadata:
        pairs = args.set_metadata.split(",")
        for pair in pairs:
            if "=" in pair:
                key, val = pair.split("=", 1)
                key = key.strip()
                frontmatter[key] = parse_metadata_value(val)
                
    # Dump frontmatter back
    try:
        # Dump with default_flow_style=False to keep it human-readable
        new_frontmatter_str = yaml.safe_dump(frontmatter, default_flow_style=False, sort_keys=False)
    except yaml.YAMLError as e:
        print(f"Error generating YAML frontmatter: {e}")
        sys.exit(1)
        
    # Reassemble the file
    new_content = f"---\n{new_frontmatter_str}---\n{body.lstrip()}"
    
    with open(args.file, "w", encoding="utf-8") as f:
        f.write(new_content)
        
    print(f"Successfully adjusted metadata for '{args.file}'.")

if __name__ == "__main__":
    main()
