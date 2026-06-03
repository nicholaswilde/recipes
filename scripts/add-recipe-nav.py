#!/usr/bin/env python3
import sys
import re
import os

def main():
    if len(sys.argv) < 3:
        print("Usage: add-recipe-nav.py <recipe_name> <relative_path>")
        sys.exit(1)
        
    recipe_name = sys.argv[1]
    rel_path = sys.argv[2]
    
    # Extract category from relative path, e.g. "cookies-and-bars/date-brownies.md" -> "cookies-and-bars"
    category = rel_path.split('/')[0]
    
    zensical_path = "zensical.toml"
    if not os.path.exists(zensical_path):
        print(f"Error: {zensical_path} not found")
        sys.exit(1)
        
    with open(zensical_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    sections = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if "[[project.nav]]" in line:
            # Look ahead for a key definition: Name = [
            j = i + 1
            while j < len(lines) and "[[project.nav]]" not in lines[j] and not re.match(r'^\s*[^=]+=\s*\[', lines[j]):
                j += 1
            if j < len(lines) and re.match(r'^\s*[^=]+=\s*\[', lines[j]):
                key_line_idx = j
                match = re.match(r'^\s*("[^"]+"|\w+)\s*=\s*\[', lines[j])
                section_name = match.group(1).strip('"')
                
                k = j + 1
                list_lines = []
                while k < len(lines) and "]" not in lines[k]:
                    list_lines.append((k, lines[k]))
                    k += 1
                if k < len(lines) and "]" in lines[k]:
                    sections.append({
                        "name": section_name,
                        "start_idx": key_line_idx,
                        "end_idx": k,
                        "items": list_lines
                    })
                i = k
            else:
                i = j
        else:
            i += 1
            
    target_section = None
    for sec in sections:
        for idx, item_line in sec["items"]:
            m = re.search(r'=\s*"([^"]+)"', item_line)
            if m:
                item_path = m.group(1)
                if item_path.startswith(category + "/"):
                    target_section = sec
                    break
        if target_section:
            break
            
    if not target_section:
        print(f"Error: Could not find nav section for category '{category}' in {zensical_path}")
        sys.exit(1)
        
    entries = []
    new_entry = { "name": recipe_name, "line": f'  {{ "{recipe_name}" = "{rel_path}" }},\n' }
    
    for idx, item_line in target_section["items"]:
        m = re.match(r'^\s*\{\s*"([^"]+)"\s*=\s*"([^"]+)"\s*\},?\s*$', item_line)
        if m:
            entries.append({ "name": m.group(1), "line": item_line })
            
    exists = False
    for entry in entries:
        if entry["name"].lower() == recipe_name.lower():
            entry["line"] = new_entry["line"]
            exists = True
            break
            
    if not exists:
        entries.append(new_entry)
        
    entries.sort(key=lambda x: x["name"].lower())
    
    new_list_lines = [entry["line"] for entry in entries]
    
    updated_lines = lines[:target_section["start_idx"]+1] + new_list_lines + lines[target_section["end_idx"]:]
    
    with open(zensical_path, "w", encoding="utf-8") as f:
        f.writelines(updated_lines)
        
    print(f"Successfully added '{recipe_name}' to zensical.toml section '{target_section['name']}'")

if __name__ == "__main__":
    main()
