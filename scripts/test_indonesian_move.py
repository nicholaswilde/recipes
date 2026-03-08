import os
import sys

def check_move():
    recipes = ["Indonesian Satay", "Lemper", "Lumpia", "Nasi Goreng", "Wontons"]
    md_files = ["indonesian-satay.md", "lemper.md", "lumpia.md", "nasi-goreng.md", "wontons.md"]
    
    missing = []
    
    # Check cook files
    for r in recipes:
        cook_path = f"cook/asian/{r}.cook"
        img_path = f"cook/asian/{r}.jpg"
        if not os.path.exists(cook_path):
            missing.append(f"Missing cook file: {cook_path}")
        if not os.path.exists(img_path):
            missing.append(f"Missing image file: {img_path}")
            
    # Check doc files and tags
    for md in md_files:
        doc_path = f"docs/asian/{md}"
        if not os.path.exists(doc_path):
            missing.append(f"Missing doc file: {doc_path}")
        else:
            with open(doc_path, 'r') as f:
                content = f.read()
                if "  - indonesian" not in content:
                    missing.append(f"Missing indonesian tag in: {doc_path}")
                    
    # Check that old directory is gone or empty
    if os.path.exists("cook/indonesian") and os.listdir("cook/indonesian"):
        missing.append("Old cook/indonesian directory is not empty")
    if os.path.exists("docs/indonesian") and os.listdir("docs/indonesian"):
        missing.append("Old docs/indonesian directory is not empty")
        
    return missing

if __name__ == "__main__":
    errors = check_move()
    if errors:
        for e in errors:
            print(e)
        sys.exit(1)
    else:
        print("Indonesian move verified successfully.")
        sys.exit(0)
