#!/usr/bin/env python3

import os

def dedupe_zensical(filepath="zensical.toml"):
    if not os.path.exists(filepath):
        print(f"Error: {filepath} not found.")
        return

    with open(filepath, "r") as f:
        lines = f.readlines()

    new_lines = []
    seen_in_section = set()
    in_array = False
    removed_count = 0
    
    for line in lines:
        # Detect the start of an array section (e.g., `Sides = [`)
        if "=" in line and "[" in line and "]" not in line:
            in_array = True
            seen_in_section = set()
            new_lines.append(line)
            continue
        elif "]" in line and in_array:
            in_array = False
            new_lines.append(line)
            continue
            
        if in_array and "{" in line and "}" in line:
            trimmed = line.strip()
            if trimmed in seen_in_section:
                removed_count += 1
                continue
            seen_in_section.add(trimmed)
            
        new_lines.append(line)
        
    if removed_count > 0:
        with open(filepath, "w") as f:
            f.writelines(new_lines)
        print(f"Successfully removed {removed_count} duplicate entries from {filepath}.")
    else:
        print(f"No duplicate entries found in {filepath}.")

if __name__ == "__main__":
    dedupe_zensical()
