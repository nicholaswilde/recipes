import os
import sys

def check_move():
    mapping = {
        "cook/desserts/Crème Bavaroise.cook": "custard",
        "cook/desserts/Crème Brûlée.cook": "custard",
        "cook/desserts/Crème Chiboust.cook": "custard",
        "cook/desserts/Crème Diplomat.cook": "custard",
        "cook/desserts/Brioche Tart.cook": "tart",
        "cook/desserts/Lemon Tart.cook": "tart",
        "cook/main/Caramelized Onion, Spinach, and Sweet Potato Tart.cook": "tart",
        "cook/main/Shallot Onion and Chive Tart.cook": "tart",
    }
    
    doc_mapping = {
        "docs/desserts/crème-bavaroise.md": "custard",
        "docs/desserts/crème-brûlée.md": "custard",
        "docs/desserts/crème-chiboust.md": "custard",
        "docs/desserts/crème-diplomat.md": "custard",
        "docs/desserts/brioche-tart.md": "tart",
        "docs/desserts/lemon-tart.md": "tart",
        "docs/main/caramelized-onion,-spinach,-and-sweet-potato-tart.md": "tart",
        "docs/main/shallot-onion-and-chive-tart.md": "tart",
    }
    
    missing = []
    
    for path, tag in mapping.items():
        if not os.path.exists(path):
            missing.append(f"Missing file: {path}")
        else:
            with open(path, 'r') as f:
                content = f.read()
                if f">> tags: {tag}" not in content and f" {tag}" not in content:
                     # loose check for tag
                     if tag not in content:
                        missing.append(f"Missing {tag} tag in: {path}")

    for path, tag in doc_mapping.items():
        if not os.path.exists(path):
            missing.append(f"Missing doc file: {path}")
        else:
            with open(path, 'r') as f:
                content = f.read()
                if f"  - {tag}" not in content:
                    missing.append(f"Missing {tag} tag in doc: {path}")
                    
    if os.path.exists("cook/custards") and [f for f in os.listdir("cook/custards") if f != "recipe.md.gotmpl"]:
        missing.append("Old cook/custards directory is not empty")
    if os.path.exists("cook/tarts") and [f for f in os.listdir("cook/tarts") if f != "recipe.md.gotmpl"]:
        missing.append("Old cook/tarts directory is not empty")
        
    return missing

if __name__ == "__main__":
    errors = check_move()
    if errors:
        for e in errors:
            print(e)
        sys.exit(1)
    else:
        print("Dessert consolidation verified successfully.")
        sys.exit(0)
