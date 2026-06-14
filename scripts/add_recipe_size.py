#!/usr/bin/env python3
import sys
import os
import re

def parse_qty_val(qty_str):
    qty_str = qty_str.strip()
    # Mixed fraction "1 1/2"
    m_mixed = re.match(r'^(\d+)\s+(\d+)/(\d+)$', qty_str)
    if m_mixed:
        return float(m_mixed.group(1)) + float(m_mixed.group(2)) / float(m_mixed.group(3))
    # Simple fraction "1/2"
    m_frac = re.match(r'^(\d+)/(\d+)$', qty_str)
    if m_frac:
        return float(m_frac.group(1)) / float(m_frac.group(2))
    # Decimal or integer
    try:
        return float(qty_str)
    except ValueError:
        return None

def format_qty(val):
    if val == 0:
        return ""
    if val.is_integer():
        return str(int(val))
    # Check common fractions
    fracs = {0.25: "1/4", 0.5: "1/2", 0.75: "3/4", 0.33: "1/3", 0.333: "1/3", 0.66: "2/3", 0.667: "2/3", 0.125: "1/8", 0.375: "3/8", 0.625: "5/8", 0.875: "7/8"}
    rem = val - int(val)
    for f_val, f_str in fracs.items():
        if abs(rem - f_val) < 0.01:
            if int(val) > 0:
                return f"{int(val)} {f_str}"
            else:
                return f_str
    # Otherwise format as decimal, rounding to 2 decimal places
    return f"{val:.2f}".rstrip('0').rstrip('.')

def scale_ingredient_line(line, factor):
    # Keep the leading indentation, the dash, and the optional emoji
    m_prefix = re.match(r'^(\s*-\s*)(:\w+:\s*)?', line)
    if not m_prefix:
        return line # Not a standard ingredient bullet point
    
    prefix = m_prefix.group(0)
    rest = line[len(prefix):]
    
    # 1. Scale the weight in parentheses if present, e.g. "(113 g)" or "(113g)"
    def scale_weight(match):
        num_str = match.group(1)
        val = parse_qty_val(num_str)
        if val is not None:
            scaled_val = val * factor
            # round to integer for grams
            return f"({int(round(scaled_val))} g)"
        return match.group(0)
        
    rest = re.sub(r'\((\d+(?:\.\d+)?)\s*g\)', scale_weight, rest)
    
    # 2. Scale the quantity at the start of the rest of the text
    # mixed fraction, simple fraction, decimal, or integer
    m_qty = re.match(r'^(\d+\s+\d+/\d+|\d+/\d+|\d+\.\d+|\d+)\b', rest)
    if m_qty:
        qty_str = m_qty.group(1)
        val = parse_qty_val(qty_str)
        if val is not None:
            scaled_val = val * factor
            scaled_str = format_qty(scaled_val)
            rest = scaled_str + rest[len(qty_str):]
            
    return prefix + rest

def extract_and_remove_serves(content):
    lines = content.splitlines()
    table_start = -1
    table_end = -1
    for i in range(min(30, len(lines))):
        if lines[i].strip().startswith("|") and ":" in lines[i]:
            if i > 0 and lines[i-1].strip().startswith("|") and "Total Time" in lines[i-1]:
                table_start = i-1
                j = i
                while j < len(lines) and lines[j].strip().startswith("|"):
                    j += 1
                table_end = j
                break
    
    original_serves = None
    if table_start != -1:
        table_lines = lines[table_start:table_end]
        headers = [h.strip() for h in table_lines[0].split("|")[1:-1]]
        alignments = [a.strip() for a in table_lines[1].split("|")[1:-1]]
        values = [v.strip() for v in table_lines[2].split("|")[1:-1]]
        
        serves_idx = -1
        for idx, h in enumerate(headers):
            if "Serves" in h or "fork_and_knife_with_plate" in h:
                serves_idx = idx
                break
        
        if serves_idx != -1:
            original_serves = values[serves_idx]
            new_headers = [headers[idx] for idx in range(len(headers)) if idx != serves_idx]
            new_alignments = [alignments[idx] for idx in range(len(alignments)) if idx != serves_idx]
            new_values = [values[idx] for idx in range(len(values)) if idx != serves_idx]
            
            new_table_lines = [
                "| " + " | ".join(new_headers) + " |",
                "| " + " | ".join(new_alignments) + " |",
                "| " + " | ".join(new_values) + " |"
            ]
            lines[table_start:table_end] = new_table_lines
            content = "\n".join(lines)
            
    return content, original_serves

def find_ingredients_range(lines):
    start_idx = -1
    end_idx = -1
    for idx, line in enumerate(lines):
        if re.match(r'^##\s+.*Ingredients', line, re.IGNORECASE):
            start_idx = idx
            for j in range(idx + 1, len(lines)):
                if lines[j].startswith("##"):
                    end_idx = j
                    break
            if end_idx == -1:
                end_idx = len(lines)
            break
    return start_idx, end_idx

def add_size_to_existing_tabs(ing_lines, factor, new_tab_name):
    first_tab_lines = []
    inside_first_tab = False
    
    for line in ing_lines:
        if line.strip().startswith('=== "'):
            if not first_tab_lines:
                inside_first_tab = True
                continue
            else:
                break
        if inside_first_tab:
            if line.strip() == "" or line.startswith("    "):
                first_tab_lines.append(line)
            else:
                break
                
    # Strip leading and trailing blank lines
    while first_tab_lines and first_tab_lines[0].strip() == "":
        first_tab_lines.pop(0)
    while first_tab_lines and first_tab_lines[-1].strip() == "":
        first_tab_lines.pop()
        
    scaled_lines = []
    for line in first_tab_lines:
        if line.startswith("    -"):
            clean_line = line[4:]
            scaled_clean = scale_ingredient_line(clean_line, factor)
            scaled_lines.append("    " + scaled_clean)
        else:
            scaled_lines.append(line)
            
    last_idx = len(ing_lines) - 1
    while last_idx >= 0 and ing_lines[last_idx].strip() == "":
        last_idx -= 1
        
    new_tab_block = [
        f'=== "{new_tab_name}"\n',
        "\n"
    ] + [line + "\n" if not line.endswith("\n") else line for line in scaled_lines]
    
    result = ing_lines[:last_idx + 1] + ["\n"] + new_tab_block + ing_lines[last_idx + 1:]
    return result

def convert_plain_list_to_tabs(ing_lines, factor, new_tab_name, original_serves):
    original_list_lines = []
    header_lines = []
    trailing_lines = []
    inside_list = False
    
    for line in ing_lines:
        if line.strip().startswith("-") or line.strip().startswith("*"):
            inside_list = True
            original_list_lines.append(line)
        else:
            if not inside_list:
                header_lines.append(line)
            else:
                trailing_lines.append(line)
                
    if original_serves:
        if original_serves.isdigit():
            original_tab_name = f"Serves {original_serves}"
        else:
            original_tab_name = original_serves.title()
    else:
        original_tab_name = "Original"
        
    scaled_list_lines = []
    for line in original_list_lines:
        m_indent = re.match(r'^(\s*)', line)
        indent = m_indent.group(1) if m_indent else ""
        clean_line = line[len(indent):]
        scaled_clean = scale_ingredient_line(clean_line, factor)
        scaled_list_lines.append("    " + indent + scaled_clean)
        
    formatted_original_lines = []
    for line in original_list_lines:
        m_indent = re.match(r'^(\s*)', line)
        indent = m_indent.group(1) if m_indent else ""
        clean_line = line[len(indent):]
        formatted_original_lines.append("    " + indent + clean_line)
        
    result = []
    result.extend(header_lines)
    result.append("\n")
    result.append(f'=== "{original_tab_name}"\n')
    result.append("\n")
    result.extend(formatted_original_lines)
    result.append("\n")
    result.append(f'=== "{new_tab_name}"\n')
    result.append("\n")
    result.extend(scaled_list_lines)
    result.extend(trailing_lines)
    
    return result

def main():
    if len(sys.argv) < 4:
        print("Usage: add_recipe_size.py <recipe.md> <scale_factor> <tab_name>")
        sys.exit(1)
        
    md_path = sys.argv[1]
    if not os.path.exists(md_path):
        print(f"Error: {md_path} not found")
        sys.exit(1)
        
    try:
        factor = float(sys.argv[2])
    except ValueError:
        print(f"Error: scale_factor must be a float, got {sys.argv[2]}")
        sys.exit(1)
        
    new_tab_name = sys.argv[3]
    
    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    content, original_serves = extract_and_remove_serves(content)
    lines = content.splitlines(keepends=True)
    
    start_idx, end_idx = find_ingredients_range(lines)
    if start_idx == -1:
        print("Error: Ingredients section not found in file.")
        sys.exit(1)
        
    ing_lines = lines[start_idx:end_idx]
    
    has_tabs = any('=== "' in line for line in ing_lines)
    
    if has_tabs:
        updated_ing_lines = add_size_to_existing_tabs(ing_lines, factor, new_tab_name)
    else:
        updated_ing_lines = convert_plain_list_to_tabs(ing_lines, factor, new_tab_name, original_serves)
        
    lines[start_idx:end_idx] = updated_ing_lines
    
    with open(md_path, "w", encoding="utf-8") as f:
        f.writelines(lines)
        
    print(f"Successfully added size '{new_tab_name}' (factor {factor}) to {md_path}")

if __name__ == "__main__":
    main()
