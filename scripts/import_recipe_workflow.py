#!/usr/bin/env python3

################################################################################
#
# import_recipe_workflow.py
# ----------------
# Orchestrate the recipe import workflow
#
# @author nιcнolaѕ wιlde, 0x08b7d7a3
# @date 14 Jun 2026
# @version 0.1.0
#
################################################################################

import sys
import os
import re
import argparse
import subprocess
import glob

def find_newest_cook_file(category=None):
    # Find all .cook files under cook/
    pattern = "cook/**/*.cook"
    cook_files = glob.glob(pattern, recursive=True)
    if not cook_files:
        return None
    # Filter by category if specified
    if category:
        cook_files = [f for f in cook_files if f.startswith(f"cook/{category}/")]
    if not cook_files:
        return None
    return max(cook_files, key=os.path.getmtime)

def get_new_markdown_path(cook_path):
    parts = cook_path.split(os.sep)
    try:
        idx = parts.index("cook")
        category_parts = parts[idx+1:-1]
        category = "/".join(category_parts)
    except ValueError:
        category = "main"
    filename = os.path.splitext(parts[-1])[0]
    lower = filename.replace(" ", "-").lower()
    return os.path.join("docs", category, f"{lower}.md")

def extract_recipe_url_from_issue(issue_number):
    try:
        # Run gh issue view
        cmd = ["gh", "issue", "view", str(issue_number), "--json", "title,body"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        import json
        data = json.loads(result.stdout)
        body = data.get("body", "")
        title = data.get("title", "")
        print(f"Fetched issue #{issue_number}: {title}")
        
        # Extract URLs
        urls = re.findall(r'https?://[^\s)\]]+', body)
        for url in urls:
            # Skip GitHub user-attachments and github.com issue pages
            if "github.com/user-attachments" not in url and "github.com/" not in url:
                return url
        return None
    except Exception as e:
        print(f"Error fetching/parsing GitHub issue: {e}")
        return None

def run_command(cmd, shell=False):
    print(f"Running command: {' '.join(cmd) if not shell else cmd}")
    result = subprocess.run(cmd, shell=shell, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Command failed with exit code {result.returncode}")
        print(f"Stdout:\n{result.stdout}")
        print(f"Stderr:\n{result.stderr}")
    return result

def main():
    parser = argparse.ArgumentParser(description="Orchestrate the recipe import workflow in a single execution.")
    parser.add_argument("url_or_issue", help="Target recipe URL or GitHub issue number")
    parser.add_argument("category", nargs="?", default=None, help="Target category (optional)")
    
    args = parser.parse_args()
    
    url = args.url_or_issue
    category = args.category
    
    # Check if URL or issue number
    is_issue = False
    if url.isdigit() or url.startswith("#"):
        is_issue = True
        issue_num = url.lstrip("#")
        print(f"Input is detected as a GitHub issue number: {issue_num}")
        extracted_url = extract_recipe_url_from_issue(issue_num)
        if not extracted_url:
            print(f"Error: No external recipe URL found in the description of issue #{issue_num}.")
            sys.exit(1)
        url = extracted_url
        print(f"Extracted recipe URL from issue: {url}")
        
    # Step 1: Run scrape_to_cook.py
    scrape_cmd = ["uv", "run", "scripts/scrape_to_cook.py", url]
    if category:
        scrape_cmd.extend(["--category", category])
        
    print("\n--- Step 1: Scraping recipe to CookLang ---")
    res = run_command(scrape_cmd)
    if res.returncode != 0:
        print("Scraping failed.")
        sys.exit(1)
        
    # Find the created .cook file
    cook_file = find_newest_cook_file(category)
    if not cook_file:
        print("Error: Could not locate the newly created .cook file.")
        sys.exit(1)
    print(f"Located new .cook file: {cook_file}")
    
    # Step 2: Run task move
    print("\n--- Step 2: Running move script to compile and organize ---")
    res = run_command(["bash", "scripts/move.sh", cook_file])
    
    md_path = get_new_markdown_path(cook_path=cook_file)
    if not os.path.exists(md_path):
        print(f"Error: Target markdown file was not created at {md_path}")
        sys.exit(1)
    print(f"Target markdown file successfully created at: {md_path}")
    
    # Step 3: Run check_recipe_emojis.py --fix
    print("\n--- Step 3: Verifying and auto-fixing recipe emojis ---")
    emoji_cmd = ["uv", "run", "scripts/check_recipe_emojis.py", "--fix", cook_file]
    run_command(emoji_cmd)
    
    # Step 4: Run convert_recipe_units.py
    print("\n--- Step 4: Converting volumetric units to weights ---")
    convert_cmd = ["uv", "run", "scripts/convert_recipe_units.py", md_path]
    run_command(convert_cmd)
    
    # Step 5: Run spellcheck & whitelist
    print("\n--- Step 5: Running spellchecker and auto-whitelisting proper nouns ---")
    
    # Run typos spellchecker to detect errors
    spellcheck_cmd = ["typos", md_path]
    
    max_iterations = 5
    for iteration in range(max_iterations):
        res = subprocess.run(spellcheck_cmd, capture_output=True, text=True)
        if res.returncode == 0:
            print("Spellcheck passed successfully with 0 errors.")
            break
            
        # Parse output for misspelled words
        output = res.stderr + "\n" + res.stdout
        flagged_words = re.findall(r"`([^`]+)` is misspelled", output)
        flagged_words = list(set(flagged_words))
        
        if not flagged_words:
            print("Spellcheck failed, but no specific misspelled words could be parsed from output:")
            print(output)
            break
            
        print(f"Flagged misspelled words: {flagged_words}")
        
        # Decide which words to whitelist
        words_to_whitelist = []
        is_interactive = sys.stdin.isatty() and not os.environ.get("CI")
        
        for word in flagged_words:
            if is_interactive:
                try:
                    ans = input(f"Word '{word}' flagged. Whitelist it? [y/N]: ").strip().lower()
                    if ans in ('y', 'yes'):
                        words_to_whitelist.append(word)
                except (KeyboardInterrupt, EOFError):
                    print("\nInput cancelled.")
                    break
            else:
                # Auto-detect proper nouns (capitalized) or common exceptions
                if word[0].isupper() or len(word) <= 2:
                    print(f"Auto-whitelisting detected proper noun/acronym: {word}")
                    words_to_whitelist.append(word)
                else:
                    print(f"Skipping auto-whitelist for lowercase word: {word}")
                    
        if not words_to_whitelist:
            print("No words selected for whitelisting. Spelling check needs manual fixing.")
            break
            
        # Run whitelist_typos.py
        whitelist_cmd = ["uv", "run", "scripts/whitelist_typos.py"] + words_to_whitelist
        res_wl = subprocess.run(whitelist_cmd, capture_output=True, text=True)
        if res_wl.returncode != 0:
            print("Failed to run whitelist_typos.py:")
            print(res_wl.stderr)
            break
        print(f"Successfully whitelisted: {words_to_whitelist}")
        
    print("\nWorkflow orchestration complete!")

if __name__ == "__main__":
    main()
