import os
import re

directory = '.agents/skills'
for filename in os.listdir(directory):
    if filename.endswith('.md'):
        filepath = os.path.join(directory, filename)
        with open(filepath, 'r') as f:
            content = f.read()

        # Add rtk to ls, tree, grep, find, rg
        # but avoid matching things like `lit parse` or english words.
        # we only match them if they are at the start of a code block line or backticks
        content = re.sub(r'(`|```bash\n|\n\s*)(ls|tree|grep|find|rg)(\s)', r'\1rtk \2\3', content)

        # Let's also do task commands: task lint, task build, task validate
        # content = re.sub(r'(?<!rtk err )(?<!\w)(task )(lint|validate|build|test)', r'rtk err \1\2', content)

        with open(filepath, 'w') as f:
            f.write(content)
print("Applied rtk to rest")
