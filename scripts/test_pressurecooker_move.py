import os
import sys

def check_move():
    mapping = {
        "cook/ingredients/Black Beans.cook": "pressure-cooker",
        "cook/ingredients/Brown Rice.cook": "pressure-cooker",
        "cook/ingredients/Chickpeas.cook": "pressure-cooker",
        "cook/sides/Black Eyed Peas and Greens.cook": "pressure-cooker",
        "cook/sides/Refried Black Beans.cook": "pressure-cooker",
    }
    
    doc_mapping = {
        "docs/ingredients/black-beans.md": "pressure-cooker",
        "docs/ingredients/brown-rice.md": "pressure-cooker",
        "docs/ingredients/chickpeas.md": "pressure-cooker",
        "docs/sides/black-eyed-peas-and-greens.md": "pressure-cooker",
        "docs/sides/refried-black-beans.md": "pressure-cooker",
    }
    
    missing = []
    
    for path, tag in mapping.items():
        if not os.path.exists(path):
            missing.append(f"Missing file: {path}")
        else:
            with open(path, 'r') as f:
                content = f.read()
                if f">> tags: {tag}" not in content and f" {tag}" not in content:
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
                    
    if os.path.exists("cook/pressurecooker") and [f for f in os.listdir("cook/pressurecooker") if f != "recipe.md.gotmpl"]:
        missing.append("Old cook/pressurecooker directory is not empty")
    if os.path.exists("docs/pressurecooker") and os.listdir("docs/pressurecooker"):
        missing.append("Old docs/pressurecooker directory is not empty")
        
    return missing

if __name__ == "__main__":
    errors = check_move()
    if errors:
        for e in errors:
            print(e)
        sys.exit(1)
    else:
        print("Pressure cooker move verified successfully.")
        sys.exit(0)
