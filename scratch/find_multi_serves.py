import os
import re

docs_dir = "docs"
matching_files = []

for root, dirs, files in os.walk(docs_dir):
    for file in files:
        if file.endswith(".md"):
            filepath = os.path.join(root, file)
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Count the occurrences of the Serves icon table header
            # E.g. "| :fork_and_knife_with_plate: Serves |" or "Serves" in table headers
            matches = re.findall(r'\|\s*:fork_and_knife_with_plate:\s*Serves\s*\|', content)
            if len(matches) > 1:
                matching_files.append((filepath, len(matches)))

print("Files with multiple Serves table headers:")
for path, count in sorted(matching_files, key=lambda x: x[1], reverse=True):
    print(f"  - {path} ({count} occurrences)")
