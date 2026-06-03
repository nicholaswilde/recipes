#!/usr/bin/env python3
import os
import re
import sys
import subprocess

def run_command(cmd):
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr

def fix_unresolved_reference(line, col):
    idx = col - 1  # 0-indexed column
    
    # 1. Look for [text][number] pattern in the line
    for match in re.finditer(r'\[(?P<text>[^\]]+)\]\[(?P<ref>\d+)\]', line):
        start, end = match.span()
        # Find where [ref] starts
        ref_start = line.find(f"[{match.group('ref')}]", start)
        ref_end = ref_start + len(match.group('ref')) + 2
        # If the index is within the entire match or specifically within [ref]
        if ref_start <= idx <= ref_end or start <= idx <= end:
            text = match.group('text')
            return line[:start] + text + line[end:]
            
    # 2. Look for [text] (standalone bracket)
    for match in re.finditer(r'\[(?P<text>[^\]]+)\]', line):
        start, end = match.span()
        if start <= idx <= end:
            text = match.group('text')
            if text in ["TAGS"]:
                return line
            # Escape if not already escaped
            if start > 0 and line[start-1] == '\\':
                return line
            return line[:start] + '\\[' + text + '\\]' + line[end:]
            
    return line

def main():
    # 1. Run task validate
    code, stdout, stderr = run_command(["task", "validate"])
    if code != 0:
        print("Error: task validate failed.")
        print(stdout)
        print(stderr)
        sys.exit(code)
    print("Configuration validation passed.")

    # 2. Run zensical build and capture output
    # Since zensical build prints to stdout/stderr, we combine them
    code, stdout, stderr = run_command(["zensical", "build", "--clean"])
    output = stdout + "\n" + stderr
    # Strip ANSI escape sequences
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    output = ansi_escape.sub('', output)

    # Pattern to match warning blocks:
    # Warning: <type>
    #      ╭─[ <file>:<line>:<col> ]
    warning_pattern = re.compile(
        r"Warning:\s*(?P<type>[^\n]+)\n\s*╭─\[\s*(?P<file>[^:]+):(?P<line>\d+):(?P<col>\d+)\s*\]",
        re.MULTILINE
    )

    matches = list(warning_pattern.finditer(output))
    if not matches:
        print("No build warnings found. Everything is clean!")
        sys.exit(0)

    print(f"Found {len(matches)} warnings. Attempting to fix...")

    # Group warnings by file to minimize file reads/writes
    files_to_fix = {}
    for match in matches:
        w_type = match.group("type").strip()
        rel_path = match.group("file").strip()
        line_num = int(match.group("line"))
        col_num = int(match.group("col"))

        # Resolve path
        full_path = rel_path
        if not os.path.exists(full_path):
            full_path = os.path.join("docs", rel_path)
        
        if not os.path.exists(full_path):
            print(f"Warning: File {rel_path} not found.")
            continue

        files_to_fix.setdefault(full_path, []).append((w_type, line_num, col_num))

    for filepath, warnings in files_to_fix.items():
        print(f"Fixing issues in {filepath}...")
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.read().splitlines()

        # Sort warnings by line number in descending order to handle any line alterations cleanly,
        # although our substitutions don't shift line counts.
        warnings.sort(key=lambda x: x[1], reverse=True)

        modified = False
        for w_type, line_num, col_num in warnings:
            idx = line_num - 1
            if idx < 0 or idx >= len(lines):
                continue
            
            line = lines[idx]

            if "unused link definition" in w_type:
                # Remove/empty the line
                print(f"  Line {line_num}: Removing unused link definition: {line}")
                lines[idx] = ""
                modified = True
            elif "unresolved link reference" in w_type:
                new_line = fix_unresolved_reference(line, col_num)
                if new_line != line:
                    print(f"  Line {line_num}: Fixing unresolved link reference:\n    Old: {line}\n    New: {new_line}")
                    lines[idx] = new_line
                    modified = True

        if modified:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write("\n".join(lines) + "\n")

    print("Fixes applied. Re-running zensical build to verify...")
    code, stdout, stderr = run_command(["zensical", "build", "--clean"])
    if code == 0:
        print("Success! Zensical build completed successfully after fixes.")
    else:
        print("Zensical build finished with remaining issues.")
        print(stdout)
        print(stderr)

if __name__ == "__main__":
    main()
