#!/usr/bin/env python3

################################################################################
#
# import_manual_recipe.py
# ----------------
# Orchestrate the manual recipe import workflow
#
# @author nιcнolaѕ wιlde, 0x08b7d7a3
# @date 25 Jun 2026
# @version 0.1.0
#
################################################################################

import sys
import os
import re
import argparse
import shutil
import subprocess
import glob

def find_categories():
    cook_dir = "cook"
    if not os.path.exists(cook_dir):
        return []
    categories = []
    for root, dirs, files in os.walk(cook_dir):
        # Skip hidden folders or config
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'config']
        for d in dirs:
            rel = os.path.relpath(os.path.join(root, d), cook_dir)
            categories.append(rel)
    return sorted(categories)

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

def run_command(cmd, shell=False):
    print(f"Running command: {' '.join(cmd) if not shell else cmd}")
    result = subprocess.run(cmd, shell=shell, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Command failed with exit code {result.returncode}")
        print(f"Stdout:\n{result.stdout}")
        print(f"Stderr:\n{result.stderr}")
    return result

def main():
    parser = argparse.ArgumentParser(description="Import a manual/image-based recipe (.cook file + optional image) and orchestrate the full processing pipeline.")
    parser.add_argument("cook_file", help="Path to the input .cook file")
    parser.add_argument("-i", "--image", help="Path to the recipe hero image (optional)")
    parser.add_argument("-c", "--category", help="Target category (e.g. breakfast, breads, desserts, etc.)")
    parser.add_argument("-n", "--issue", help="GitHub issue number to close/link (optional)")
    parser.add_argument("--commit", action="store_true", help="Automatically commit the imported recipe")
    
    args = parser.parse_args()
    
    cook_file = args.cook_file
    if not os.path.exists(cook_file):
        print(f"Error: cook file '{cook_file}' not found.")
        sys.exit(1)
        
    recipe_filename = os.path.basename(cook_file)
    recipe_name = os.path.splitext(recipe_filename)[0]
    
    # Infer/prompt category
    category = args.category
    abs_cook_file = os.path.abspath(cook_file)
    abs_repo_root = os.path.abspath(os.getcwd())
    cook_dir = os.path.join(abs_repo_root, "cook")
    
    if not category:
        if abs_cook_file.startswith(cook_dir):
            rel_path = os.path.relpath(abs_cook_file, cook_dir)
            parts = rel_path.split(os.sep)
            if len(parts) > 1:
                category = "/".join(parts[:-1])
                print(f"Inferred category '{category}' from file location.")
                
    if not category:
        categories = find_categories()
        is_interactive = sys.stdin.isatty() and not os.environ.get("CI")
        if is_interactive and categories:
            print("\nAvailable categories:")
            for idx, cat in enumerate(categories, 1):
                print(f"  {idx:2d}. {cat}")
            try:
                ans = input(f"\nSelect a category number (1-{len(categories)}) or type a custom category name: ").strip()
                if ans.isdigit():
                    idx = int(ans) - 1
                    if 0 <= idx < len(categories):
                        category = categories[idx]
                else:
                    if ans:
                        category = ans
            except (KeyboardInterrupt, EOFError):
                print("\nOperation cancelled.")
                sys.exit(1)
                
    if not category:
        print("Error: Category is required. Please specify with --category or run interactively.")
        sys.exit(1)
        
    target_cook_dir = os.path.join("cook", category)
    os.makedirs(target_cook_dir, exist_ok=True)
    target_cook_path = os.path.join(target_cook_dir, recipe_filename)
    
    # Copy/move .cook file if it's not already there
    if os.path.abspath(cook_file) != os.path.abspath(target_cook_path):
        print(f"Copying '{cook_file}' to '{target_cook_path}'")
        shutil.copy2(cook_file, target_cook_path)
        
    # If image is specified, copy it to cook/category/{recipe_name}.jpg or .png
    if args.image:
        img_src = args.image
        if not os.path.exists(img_src):
            print(f"Warning: Image file '{img_src}' not found. Skipping image.")
        else:
            _, img_ext = os.path.splitext(img_src.lower())
            if img_ext in ['.jpeg', '.jpg']:
                img_ext = '.jpg'
            elif img_ext != '.png':
                print(f"Warning: Image extension '{img_ext}' is not .jpg or .png. Using .jpg extension.")
                img_ext = '.jpg'
            target_img_path = os.path.join(target_cook_dir, f"{recipe_name}{img_ext}")
            print(f"Copying image '{img_src}' to '{target_img_path}'")
            shutil.copy2(img_src, target_img_path)
            
    # Step 2: Run move.sh
    print("\n--- Step 2: Running move script to compile and organize ---")
    res = run_command(["bash", "scripts/move.sh", target_cook_path])
    if res.returncode != 0:
        print("move.sh failed.")
        sys.exit(1)
        
    md_path = get_new_markdown_path(cook_path=target_cook_path)
    if not os.path.exists(md_path):
        print(f"Error: Target markdown file was not created at {md_path}")
        sys.exit(1)
    print(f"Target markdown file successfully created at: {md_path}")
    
    # Step 3: Run check_recipe_emojis.py --fix
    print("\n--- Step 3: Verifying and auto-fixing recipe emojis ---")
    emoji_cmd = ["uv", "run", "scripts/check_recipe_emojis.py", "--fix", target_cook_path]
    run_command(emoji_cmd)
    
    # Step 4: Run convert_recipe_units.py
    print("\n--- Step 4: Converting volumetric units to weights ---")
    convert_cmd = ["uv", "run", "scripts/convert_recipe_units.py", md_path]
    run_command(convert_cmd)
    
    # Step 5: Run spellcheck & whitelist
    print("\n--- Step 5: Running spellchecker and auto-whitelisting proper nouns ---")
    run_command(["uv", "run", "scripts/generate_typos_config.py"])
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
                if word[0].isupper() or len(word) <= 2:
                    print(f"Auto-whitelisting detected proper noun/acronym: {word}")
                    words_to_whitelist.append(word)
                else:
                    print(f"Skipping auto-whitelist for lowercase word: {word}")
                    
        if not words_to_whitelist:
            print("No words selected for whitelisting. Spelling check needs manual fixing.")
            break
            
        whitelist_cmd = ["uv", "run", "scripts/whitelist_typos.py"] + words_to_whitelist
        res_wl = subprocess.run(whitelist_cmd, capture_output=True, text=True)
        if res_wl.returncode != 0:
            print("Failed to run whitelist_typos.py:")
            print(res_wl.stderr)
            break
        print(f"Successfully whitelisted: {words_to_whitelist}")

    print("\nImport orchestration complete!")
    
    # Step 6: Git commit options
    should_commit = args.commit
    is_interactive = sys.stdin.isatty() and not os.environ.get("CI")
    if not should_commit and is_interactive:
        try:
            ans = input("Would you like to commit the imported recipe changes now? [y/N]: ").strip().lower()
            if ans in ('y', 'yes'):
                should_commit = True
        except (KeyboardInterrupt, EOFError):
            pass
            
    if should_commit:
        issue_num = args.issue
        if not issue_num and is_interactive:
            gh_available = shutil.which("gh") is not None
            if gh_available:
                first_word = recipe_name.split()[0] if recipe_name else ""
                if first_word:
                    print(f"Searching GitHub issues for '{first_word}'...")
                    subprocess.run(["gh", "issue", "list", "-S", first_word])
            try:
                ans_issue = input("Enter the issue number that corresponds to the commit (leave blank to skip): ").strip()
                if ans_issue:
                    ans_issue = ans_issue.lstrip("#")
                    if ans_issue.isdigit():
                        issue_num = ans_issue
            except (KeyboardInterrupt, EOFError):
                pass
                
        lower_name = recipe_name.replace(" ", "-").lower()
        image_files = glob.glob(f"docs/assets/images/{lower_name}.*")
        
        files_to_add = [
            target_cook_path,
            md_path,
            "zensical.toml",
            "includes/emoji.yaml",
            "dictionary.txt",
            "_typos.toml"
        ]
        
        cook_images = glob.glob(f"{target_cook_dir}/{recipe_name}.*")
        for ci in cook_images:
            if not ci.endswith(".cook"):
                files_to_add.append(ci)
                
        for img in image_files:
            files_to_add.append(img)
            
        add_cmds = ["git", "add"]
        for f in files_to_add:
            if os.path.exists(f):
                add_cmds.append(f)
                
        run_command(add_cmds)
        
        commit_msg = f"feat: add {recipe_name}"
        if issue_num:
            commit_msg += f". Fixes #{issue_num}."
        else:
            commit_msg += "."
            
        print(f"Committing with message: {commit_msg}")
        run_command(["git", "commit", "-m", commit_msg])
        print("Successfully committed!")

if __name__ == "__main__":
    main()
