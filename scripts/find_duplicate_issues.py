#!/usr/bin/env python3
import os
import sys
import json
import subprocess
import re
import argparse

def get_open_duplicate_issues(limit=100):
    cmd = ["gh", "issue", "list", "--label", "duplicate", "--json", "number,title,body", "--limit", str(limit)]
    env = os.environ.copy()
    env["GH_NOPAGER"] = "1"
    result = subprocess.run(cmd, env=env, capture_output=True, text=True)
    if result.returncode != 0:
        print("Error fetching issues from GitHub CLI:", result.stderr, file=sys.stderr)
        return []
    return json.loads(result.stdout)

def build_recipe_maps():
    recipe_files = {}
    recipe_names = {}
    recipe_urls = {}

    # Walk through docs and index recipes
    for root, dirs, files in os.walk("docs"):
        for file in files:
            if not file.endswith(".md"):
                continue
            path = os.path.join(root, file)
            recipe_files[file.lower()] = path
            
            # Clean name without extension and hyphens
            name_only = os.path.splitext(file)[0].replace("-", " ").lower()
            recipe_names[name_only] = path
            
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                    
                # Search for any markdown URLs in the file
                urls = re.findall(r'https?://[^\s\)\>]+', content)
                for u in urls:
                    clean_url = u.rstrip("/").lower()
                    recipe_urls[clean_url] = path
            except Exception:
                pass
                
    return recipe_files, recipe_names, recipe_urls

def close_issue(number, recipe_path):
    comment = f"Closed as duplicate. Existing recipe: {recipe_path}"
    cmd = ["gh", "issue", "close", str(number), "-c", comment]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"  [+] Successfully closed issue #{number} as duplicate of {recipe_path}")
    else:
        print(f"  [-] Failed to close issue #{number}: {result.stderr}", file=sys.stderr)

def main():
    parser = argparse.ArgumentParser(description="Find open duplicate issues that match existing recipes in the repo.")
    parser.add_argument("--close", action="store_true", help="Automatically close matched duplicate issues.")
    parser.add_argument("--limit", type=int, default=100, help="Maximum number of issues to fetch.")
    args = parser.parse_args()

    print("Fetching open duplicate issues...")
    issues = get_open_duplicate_issues(args.limit)
    if not issues:
        print("No duplicate issues found or failed to retrieve issues.")
        sys.exit(0)
        
    recipe_files, recipe_names, recipe_urls = build_recipe_maps()
    print(f"Loaded {len(issues)} duplicate issues.")
    print(f"Loaded {len(recipe_files)} existing recipe files.")
    print("-" * 60)
    
    exact_matches = []
    close_matches = []
    
    for issue in issues:
        number = issue["number"]
        title = issue["title"]
        body = issue.get("body", "") or ""
        
        # 1. Search by exact source URL match in body
        urls_in_body = re.findall(r'https?://[^\s]+', body)
        url_matched = None
        for u in urls_in_body:
            clean_u = u.rstrip("/").lower()
            if clean_u in recipe_urls:
                url_matched = recipe_urls[clean_u]
                break
                
        if url_matched:
            exact_matches.append({
                "number": number,
                "title": title,
                "path": url_matched
            })
            continue
            
        # 2. Search by title keyword matches
        title_clean = title.lower()
        title_clean = re.sub(r'recipe|ultimate|best|easy|homemade|simple|\bthe\b|\ba\b|with|from|copycat|\b-.*\b|\b\|.*\b', ' ', title_clean)
        words = [w.strip() for w in title_clean.split() if len(w.strip()) > 3]
        
        matched_recipes = []
        if words:
            for name, path in recipe_names.items():
                match_count = sum(1 for w in words if w in name)
                if match_count == len(words):
                    matched_recipes.append(path)
                elif len(words) >= 3 and match_count >= len(words) - 1:
                    matched_recipes.append(path)
                    
        if matched_recipes:
            close_matches.append({
                "number": number,
                "title": title,
                "matches": list(set(matched_recipes))
            })
            
    print(f"\nExact matches found: {len(exact_matches)}")
    for match in exact_matches:
        num = match["number"]
        title = match["title"]
        path = match["path"]
        print(f"  [#{num}] {title} -> {path}")
        if args.close:
            close_issue(num, path)
            
    print(f"\nClose keyword matches found: {len(close_matches)}")
    for match in close_matches:
        print(f"  [#{match['number']}] {match['title']}")
        for m in match["matches"]:
            print(f"    - {m}")
            
if __name__ == "__main__":
    main()
