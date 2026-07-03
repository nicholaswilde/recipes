################################################################################
#
# fix_broken_links.py
# ----------------
# Fix broken links in recipe documentation
#
# @author nιcнolaѕ wιlde, 0x08b7d7a3
# @date 08 Mar 2026
# @version 0.1.0
#
################################################################################

import os
import re

def build_file_maps(docs_dir):
    docs_map = {}
    images_map = {}
    
    for root, dirs, files in os.walk(docs_dir):
        for file in files:
            path = os.path.abspath(os.path.join(root, file))
            if file.endswith(".md"):
                docs_map[file] = path
            elif file.endswith((".jpg", ".png", ".jpeg", ".gif", ".webp")):
                images_map[file] = path
                
    return docs_map, images_map

def fix_all_links(docs_dir):
    docs_map, images_map = build_file_maps(docs_dir)
    print(f"Loaded {len(docs_map)} markdown files and {len(images_map)} image files in map.")
    
    # Matches markdown reference links: [1]: <path> or [1]: path
    ref_pattern = re.compile(r'^(\s*\[[^\]]+\]:\s*<?)([^>\s)]+)(>?.*)$', re.MULTILINE)
    
    # Matches inline links: [text](path) or ![text](path)
    inline_pattern = re.compile(r'(\[[^\]]+\]\()([^)]+)(\))')

    fixed_count = 0
    
    for root, dirs, files in os.walk(docs_dir):
        for file in files:
            if not file.endswith(".md"):
                continue
                
            filepath = os.path.abspath(os.path.join(root, file))
            current_dir = os.path.dirname(filepath)
            
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                
            original_content = content
            
            def resolve_and_fix(target):
                # Separate anchor if present
                anchor = ""
                if "#" in target:
                    target_parts = target.split("#", 1)
                    target = target_parts[0]
                    anchor = "#" + target_parts[1]
                
                # If target is empty, web URL, or anchor only, return as is
                if not target or target.startswith(("http://", "https://", "mailto:", "ftp:")):
                    return None
                
                # Clean up wrapping quotes or angle brackets if any
                target_clean = target.strip("<>")
                
                # Resolve relative to current_dir
                resolved_path = os.path.abspath(os.path.join(current_dir, target_clean))
                
                # If path exists, it's correct!
                if os.path.exists(resolved_path):
                    return None
                    
                # Path doesn't exist, let's fix it!
                basename = os.path.basename(target_clean)
                actual_path = None
                
                if basename.endswith(".md"):
                    actual_path = docs_map.get(basename)
                elif basename.endswith((".jpg", ".png", ".jpeg", ".gif", ".webp")):
                    # Try exact match first
                    actual_path = images_map.get(basename)
                    
                    # Try fallback extensions
                    if not actual_path:
                        name_without_ext, _ = os.path.splitext(basename)
                        for ext in [".jpg", ".png", ".jpeg", ".webp", ".gif"]:
                            fallback_name = name_without_ext + ext
                            if fallback_name in images_map:
                                actual_path = images_map[fallback_name]
                                break
                                
                    # Try prefix match in the images map
                    if not actual_path:
                        name_without_ext, _ = os.path.splitext(basename)
                        for img_name, img_path in images_map.items():
                            if img_name.startswith(name_without_ext):
                                actual_path = img_path
                                break
                    
                if actual_path:
                    # Calculate relative path from current_dir to actual_path
                    rel_path = os.path.relpath(actual_path, current_dir)
                    # Re-attach anchor
                    new_target = rel_path + anchor
                    print(f"  Fixing link in {file}: '{target_clean}' -> '{rel_path}'")
                    return new_target
                else:
                    # File not found in our maps
                    if len(basename) > 4 and '.' in basename:
                        print(f"  Warning: target file '{basename}' (from '{target}') in {file} not found in repository.")
                    return None

            # 1. Fix reference links
            def ref_replacer(match):
                prefix = match.group(1)
                target = match.group(2)
                suffix = match.group(3)
                
                new_target = resolve_and_fix(target)
                if new_target is not None:
                    return f"{prefix}{new_target}{suffix}"
                return match.group(0)
                
            content = ref_pattern.sub(ref_replacer, content)
            
            # 2. Fix inline links
            def inline_replacer(match):
                prefix = match.group(1)
                target = match.group(2)
                suffix = match.group(3)
                
                new_target = resolve_and_fix(target)
                if new_target is not None:
                    return f"{prefix}{new_target}{suffix}"
                return match.group(0)
                
            content = inline_pattern.sub(inline_replacer, content)
            
            if content != original_content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                fixed_count += 1
                
    print(f"Successfully fixed links in {fixed_count} files.")

if __name__ == "__main__":
    docs_directory = os.path.abspath("docs")
    fix_all_links(docs_directory)
