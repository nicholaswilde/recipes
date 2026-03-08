import os
import sys

def check_move():
    missing = []
    
    # Check cook files
    cook_path = "cook/sides/Kroket.cook"
    img_path = "cook/sides/Kroket.jpg"
    if not os.path.exists(cook_path):
        missing.append(f"Missing cook file: {cook_path}")
    if not os.path.exists(img_path):
        missing.append(f"Missing image file: {img_path}")
            
    # Check doc files and tags
    doc_path = "docs/sides/kroket.md"
    if not os.path.exists(doc_path):
        missing.append(f"Missing doc file: {doc_path}")
    else:
        with open(doc_path, 'r') as f:
            content = f.read()
            if "  - dutch" not in content:
                missing.append(f"Missing dutch tag in: {doc_path}")
                    
    # Check that old directory is gone or empty
    if os.path.exists("cook/dutch") and os.listdir("cook/dutch"):
        missing.append("Old cook/dutch directory is not empty")
    if os.path.exists("docs/dutch") and os.listdir("docs/dutch"):
        missing.append("Old docs/dutch directory is not empty")
        
    return missing

if __name__ == "__main__":
    errors = check_move()
    if errors:
        for e in errors:
            print(e)
        sys.exit(1)
    else:
        print("Dutch move verified successfully.")
        sys.exit(0)
