import os
import re

def find_multi_serving_recipes(directory):
    """
    Scans a directory for Markdown files with multiple "Ingredients" headers.
    Returns a list of relative paths.
    """
    multi_serving_files = []
    # Pattern to match the header: ## followed by any character (the emoji part) and then Ingredients
    pattern = re.compile(r'^##\s+.*Ingredients', re.IGNORECASE)

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".md"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        count = 0
                        for line in f:
                            if pattern.match(line):
                                count += 1
                        if count > 1:
                            multi_serving_files.append(os.path.relpath(file_path, directory))
                except (IOError, UnicodeDecodeError):
                    # Skip files we can't read
                    continue
    return sorted(multi_serving_files)

if __name__ == "__main__":
    import sys
    search_dir = sys.argv[1] if len(sys.argv) > 1 else 'docs'
    results = find_multi_serving_recipes(search_dir)
    for res in results:
        print(res)
