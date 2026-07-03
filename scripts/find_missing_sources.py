#!/usr/bin/env python3

################################################################################
#
# find_missing_sources.py
# ----------------
# Find recipes with missing source URLs
#
# @author nιcнolaѕ wιlde, 0x08b7d7a3
# @date 14 Jun 2026
# @version 0.1.0
#
################################################################################

import os
import re

def main():
    docs_dir = "docs"
    exclude_files = {"index.md", "tags.md"}
    exclude_dirs = {"reference", "assets"}
    
    # Regex to match Source or Sources with optional emoji prefix
    # Matches: ## :link: Source, ## Source, ## :link: Sources, ## Sources
    source_pattern = re.compile(r'^##\s+(?::[a-zA-Z0-9_-]+:\s+)?Sources?(?:\s+|$)', re.IGNORECASE)
    
    missing_files = []
    total_checked = 0
    
    for root, dirs, files in os.walk(docs_dir):
        # Exclude specific directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for file in files:
            if not file.endswith(".md") or file in exclude_files:
                continue
                
            file_path = os.path.join(root, file)
            total_checked += 1
            
            has_source = False
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    for line in f:
                        if source_pattern.match(line.strip()):
                            has_source = True
                            break
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
                continue
                
            if not has_source:
                missing_files.append(file_path)
                
    print(f"Checked {total_checked} markdown files.")
    if missing_files:
        print(f"Found {len(missing_files)} file(s) missing a Source section:")
        for path in sorted(missing_files):
            print(f"- [ ] {path}")
    else:
        print("All recipes contain a Source section!")

if __name__ == "__main__":
    main()
