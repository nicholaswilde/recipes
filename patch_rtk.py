import os
import re

directory = '.agents/skills'
for filename in os.listdir(directory):
    if filename.endswith('.md'):
        filepath = os.path.join(directory, filename)
        with open(filepath, 'r') as f:
            content = f.read()

        # Add rtk to git commands
        content = re.sub(r'(?<!rtk )(?<!\w)(git )(add|commit|push|pull|status|diff|checkout|branch|log|merge|rebase)', r'rtk git \2', content)
        
        # Add rtk to gh commands
        content = re.sub(r'(?<!rtk )(?<!\w)(gh )(issue|pr|run|repo)', r'rtk gh \2', content)
        
        # Ensure 'rtk gh ...' commands in code blocks end with '| cat' if they don't already
        def add_pipe_cat(match):
            line = match.group(0)
            if '| cat' not in line:
                return line + ' | cat'
            return line
            
        content = re.sub(r'^(rtk gh .*?)(?:\s*\| cat)?$', add_pipe_cat, content, flags=re.MULTILINE)

        with open(filepath, 'w') as f:
            f.write(content)
print("Applied rtk prefix to skills")
