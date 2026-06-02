#!/usr/bin/env python3
import os
import re
import json
import subprocess
import urllib.parse

def fetch_discussions():
    query = """
    query($owner: String!, $name: String!, $cursor: String) {
      repository(owner: $owner, name: $name) {
        discussions(first: 100, after: $cursor) {
          pageInfo {
            hasNextPage
            endCursor
          }
          nodes {
            title
            url
            category {
              name
            }
          }
        }
      }
    }
    """
    
    discussions = []
    has_next_page = True
    cursor = None
    
    while has_next_page:
        cursor_arg = f"-F cursor={cursor}" if cursor else "-F cursor=null"
        cmd = [
            "gh", "api", "graphql",
            "-F", "owner=nicholaswilde",
            "-F", "name=recipes",
            cursor_arg,
            "-f", f"query={query}"
        ]
        
        # Disable pager for gh command using env var
        env = os.environ.copy()
        env["GH_NOPAGER"] = "1"
        
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)
        if result.returncode != 0:
            print("Error running gh api:", result.stderr)
            break
            
        try:
            data = json.loads(result.stdout)
            repo = data.get("data", {}).get("repository", {})
            disc_data = repo.get("discussions", {})
            nodes = disc_data.get("nodes", [])
            discussions.extend(nodes)
            
            page_info = disc_data.get("pageInfo", {})
            has_next_page = page_info.get("hasNextPage", False)
            cursor = page_info.get("endCursor", None)
        except Exception as e:
            print("Failed to parse response:", e)
            print("Raw response:", result.stdout)
            break
            
    return discussions

def clean_pathname(title):
    # Decode URL percent-encoding (e.g. %C3%A9 -> é)
    title_decoded = urllib.parse.unquote(title)
    
    # Strip leading/trailing whitespaces/slashes
    clean = title_decoded.strip("/")
    
    # Strip leading recipes/
    if clean.startswith("recipes/"):
        clean = clean[len("recipes/"):]
    elif clean.startswith("recipes"):
        clean = clean[len("recipes"):]
        
    clean = clean.strip("/")
    return clean

def add_comments_to_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    lines = content.splitlines()
    
    # Check if file has front-matter
    has_front_matter = False
    front_matter_end_idx = -1
    
    if len(lines) > 0 and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                has_front_matter = True
                front_matter_end_idx = i
                break
                
    if has_front_matter:
        # Check if comments: true is already in front-matter
        front_matter_lines = lines[1:front_matter_end_idx]
        has_comments = False
        for line in front_matter_lines:
            # Match comments: true or comments: "true" or comments: 'true' (case-insensitive)
            if re.match(r'^\s*comments\s*:\s*[\'"]?true[\'"]?\s*$', line, re.IGNORECASE):
                has_comments = True
                break
                
        if has_comments:
            return False # already has comments enabled
            
        # Insert comments: true right before the closing ---
        lines.insert(front_matter_end_idx, "comments: true")
        new_content = "\n".join(lines) + ("\n" if content.endswith("\n") else "")
    else:
        # Prepend new front-matter
        new_content = "---\ncomments: true\n---\n" + content
        
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
        
    return True

def build_docs_file_map(docs_dir):
    file_map = {}
    for root, dirs, files in os.walk(docs_dir):
        for file in files:
            if file.endswith(".md"):
                basename_no_ext = os.path.splitext(file)[0].lower()
                path = os.path.join(root, file)
                # Map the lowercase name to the path
                file_map[basename_no_ext] = path
    return file_map

def main():
    print("Fetching discussions from GitHub...")
    discussions = fetch_discussions()
    print(f"Fetched {len(discussions)} discussions total.")
    
    comments_discussions = [d for d in discussions if d.get("category", {}).get("name") == "Comments"]
    print(f"Found {len(comments_discussions)} discussions in the 'Comments' category.")
    
    # Build a map of all markdown files in docs/ by their basename (lowercase, no extension)
    docs_file_map = build_docs_file_map("docs")
    print(f"Indexed {len(docs_file_map)} markdown files in docs/ directory.")
    
    modified_files = []
    missing_files = []
    
    for d in comments_discussions:
        title = d.get("title", "")
        url = d.get("url", "")
        
        # Clean pathname
        rel_path = clean_pathname(title)
        if not rel_path:
            continue
            
        # 1. Try exact path match first
        candidates = [
            os.path.join("docs", rel_path + ".md"),
            os.path.join("docs", rel_path, "index.md")
        ]
        
        found_path = None
        for candidate in candidates:
            if os.path.exists(candidate):
                found_path = candidate
                break
                
        # 2. Try matching by basename if exact match failed (e.g. file was moved/refactored)
        if not found_path:
            # Get the last component of the rel_path
            basename_comp = os.path.basename(rel_path.strip("/")).lower()
            if basename_comp in docs_file_map:
                found_path = docs_file_map[basename_comp]
                
        if found_path:
            modified = add_comments_to_file(found_path)
            if modified:
                modified_files.append(found_path)
        else:
            missing_files.append((title, url))
            
    print(f"\n--- Sync Complete ---")
    if modified_files:
        print(f"Modified {len(modified_files)} files to enable comments:")
        for f in modified_files:
            print(f"  - {f}")
    else:
        print("All matching files already had comments enabled (or no files modified).")
        
    if missing_files:
        print(f"\nCould not find matching local markdown files for {len(missing_files)} discussions:")
        for title, url in missing_files:
            print(f"  - Title: {title} ({url})")

if __name__ == "__main__":
    main()
