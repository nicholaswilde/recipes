with open("cook/main/Mezza Luna Lasagna.cook", "r") as f:
    lines = f.readlines()

new_lines = [
    "---\n",
    "title: 🌙 Mezza Luna Lasagna\n",
    "source: https://www.traderjoes.com/home/recipes/mezza-luna-lasagna\n",
    "tags:\n",
    "  - pasta\n",
    "  - trader-joes\n",
    "  - dinner\n",
    "  - squash\n",
    "  - lasagna\n",
    "time: 2 hours 15 minutes\n",
    "servings: 6-8\n",
    "---\n\n"
]

for line in lines:
    if not line.startswith(">>"):
        new_lines.append(line)

with open("cook/main/Mezza Luna Lasagna.cook", "w") as f:
    f.writelines(new_lines)
