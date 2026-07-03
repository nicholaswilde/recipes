#!/usr/bin/env python3

################################################################################
#
# git_summary.py
# ----------------
# Generate a summary of git changes
#
# @author nιcнolaѕ wιlde, 0x08b7d7a3
# @date 12 Jun 2026
# @version 0.1.0
#
################################################################################

import subprocess
import sys

def main():
    print("=== Git Workspace Summary (Token Saver) ===")
    
    # 1. Show branch info and status overview
    print("\n--- Status ---")
    status = subprocess.run(["git", "status", "-s"], capture_output=True, text=True)
    if not status.stdout.strip():
        print("Working tree clean. No changes.")
    else:
        print(status.stdout.strip())
        
    # 2. Show diff stat
    print("\n--- Diff Stat (Unstaged Changes) ---")
    diff_stat = subprocess.run(["git", "diff", "--stat"], capture_output=True, text=True)
    if diff_stat.stdout.strip():
        print(diff_stat.stdout.strip())
    else:
        print("No unstaged changes.")
        
    # 3. Show cached diff stat
    print("\n--- Diff Stat (Staged Changes) ---")
    diff_cached_stat = subprocess.run(["git", "diff", "--cached", "--stat"], capture_output=True, text=True)
    if diff_cached_stat.stdout.strip():
        print(diff_cached_stat.stdout.strip())
    else:
        print("No staged changes.")

    # 4. Show last commit info (short)
    print("\n--- Last Commit ---")
    last_commit = subprocess.run(["git", "log", "-1", "--oneline"], capture_output=True, text=True)
    print(last_commit.stdout.strip())

if __name__ == "__main__":
    main()
