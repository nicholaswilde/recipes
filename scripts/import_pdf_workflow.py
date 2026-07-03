#!/usr/bin/env python3

################################################################################
#
# import_pdf_workflow.py
# ----------------
# Orchestrate the PDF recipe import workflow
#
# @author nιcнolaѕ wιlde, 0x08b7d7a3
# @date 01 Jul 2026
# @version 0.1.0
#
################################################################################

import sys
import os
import argparse
import urllib.request
import subprocess
import tempfile
import re
from PIL import Image

def download_file(url, dest):
    print(f"Downloading {url} silently...")
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as response, open(dest, 'wb') as out_file:
        out_file.write(response.read())
    print("Download completed successfully.")

def auto_crop_recipe_image(page_image_path, output_image_path):
    print("Attempting to auto-detect and crop hero image from page 1...")
    try:
        img = Image.open(page_image_path).convert("RGB")
        width, height = img.size
        
        # Scan the right half (x > width * 0.45) and top half (100 < y < height * 0.6)
        min_x, min_y, max_x, max_y = width, height, 0, 0
        start_x = int(width * 0.45)
        
        for x in range(start_x, width - 10, 10):
            for y in range(100, int(height * 0.6), 10):
                r, g, b = img.getpixel((x, y))
                # Detect non-white pixels
                if r < 248 or g < 248 or b < 248:
                    if x < min_x: min_x = x
                    if x > max_x: max_x = x
                    if y < min_y: min_y = y
                    if y > max_y: max_y = y
                    
        if max_x > min_x and max_y > min_y:
            pad = 15
            box = (
                max(start_x, min_x - pad),
                max(100, min_y - pad),
                min(width, max_x + pad),
                min(height, max_y + pad)
            )
            cropped = img.crop(box)
            cropped.save(output_image_path, "JPEG")
            print(f"Successfully cropped image using bounding box {box} to {output_image_path}")
            return True
        else:
            print("No high-contrast image region found on the right/top half of page 1.")
    except Exception as e:
        print(f"Warning: Failed to auto-crop image: {e}")
    return False

def find_lit_binary():
    import shutil
    binary = shutil.which("lit")
    if binary:
        return binary
    home = os.path.expanduser("~")
    fallbacks = [
        os.path.join(home, ".local/bin/lit"),
        os.path.join(home, ".npm-global/bin/lit"),
        "/usr/local/bin/lit"
    ]
    for fb in fallbacks:
        if os.path.exists(fb):
            return fb
    return "lit"

def clean_parsed_text(text):
    # Remove lit parse logs and headers
    lines = text.splitlines()
    clean_lines = []
    for line in lines:
        if line.startswith("[liteparse]") or re.match(r"^--- Page \d+ ---$", line):
            continue
        clean_lines.append(line)
    return "\n".join(clean_lines).strip()

def main():
    parser = argparse.ArgumentParser(description="Automated PDF recipe import workflow.")
    parser.add_argument("pdf_source", help="URL or local path to the recipe PDF")
    parser.add_argument("-c", "--category", help="Target recipe category (e.g. breads, sides/vegetables)")
    parser.add_argument("-n", "--issue", help="GitHub issue number to close/link (optional)")
    parser.add_argument("--commit", action="store_true", help="Automatically commit the imported recipe")
    
    args = parser.parse_args()
    
    pdf_source = args.pdf_source
    lit_bin = find_lit_binary()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        pdf_path = os.path.join(temp_dir, "recipe.pdf")
        
        # 1. Download if URL
        if pdf_source.startswith("http://") or pdf_source.startswith("https://"):
            try:
                download_file(pdf_source, pdf_path)
            except Exception as e:
                print(f"Error downloading PDF: {e}")
                sys.exit(1)
        else:
            if not os.path.exists(pdf_source):
                print(f"Error: Local PDF file '{pdf_source}' not found.")
                sys.exit(1)
            pdf_path = os.path.abspath(pdf_source)
            
        # 2. Extract Text with lit parse
        print(f"Extracting text from PDF using {lit_bin}...")
        res = subprocess.run([lit_bin, "parse", pdf_path], capture_output=True, text=True)
        if res.returncode != 0:
            print("Error: lit parse failed.")
            print(res.stderr)
            sys.exit(1)
            
        extracted_text = clean_parsed_text(res.stdout)
        
        # Try to infer recipe name from the first non-empty lines
        recipe_name = "Imported PDF Recipe"
        lines = [l.strip() for l in extracted_text.splitlines() if l.strip()]
        if lines:
            # Clean common headers from name
            candidate = lines[0]
            if not candidate.startswith("http"):
                recipe_name = candidate.replace("/", "-").replace("|", "-").strip()
                
        print(f"Inferred Recipe Name: {recipe_name}")
        
        # Write extracted text to a text file for developer reference
        ref_text_path = os.path.join("cook", f"{recipe_name}_extracted_text.txt")
        # Ensure cook directory exists
        os.makedirs("cook", exist_ok=True)
        with open(ref_text_path, "w", encoding="utf-8") as f:
            f.write(extracted_text)
        print(f"Saved raw extracted text to {ref_text_path} for manual referencing.")
        
        # 3. Render Page 1 and Auto-Crop
        image_cropped = False
        screenshot_dir = os.path.join(temp_dir, "screenshots")
        os.makedirs(screenshot_dir, exist_ok=True)
        
        print("Rendering page 1 for hero image extraction...")
        res_ss = subprocess.run([lit_bin, "screenshot", pdf_path, "--target-pages", "1", "-o", screenshot_dir], capture_output=True, text=True)
        if res_ss.returncode == 0:
            # lit screenshot names the file page_1.png
            page_1_png = os.path.join(screenshot_dir, "page_1.png")
            if os.path.exists(page_1_png):
                temp_image_path = os.path.join(temp_dir, "hero.jpg")
                image_cropped = auto_crop_recipe_image(page_1_png, temp_image_path)
            else:
                print("Warning: page_1.png not found after screenshot generation.")
        else:
            print("Warning: Failed to render page screenshots.")
            print(res_ss.stderr)
            
        # Create a basic cook file draft
        cook_file_path = os.path.join("cook", f"{recipe_name}.cook")
        with open(cook_file_path, "w", encoding="utf-8") as f:
            f.write(f">> source: {pdf_source}\n")
            f.write(">> serves: \n")
            f.write(">> total time: \n\n")
            f.write("// TODO: Format ingredients and steps into CookLang syntax below.\n")
            f.write("// Extracted text reference:\n")
            for line in extracted_text.splitlines():
                f.write(f"// {line}\n")
                
        print(f"\nCreated draft CookLang file at: {cook_file_path}")
        
        # Build manual import command
        manual_cmd = ["uv", "run", "scripts/import_manual_recipe.py", cook_file_path]
        if image_cropped:
            # We copy the cropped image to a non-temp path so the other script can pick it up
            final_temp_image = os.path.join("cook", f"{recipe_name}.jpg")
            import shutil
            shutil.copy2(temp_image_path, final_temp_image)
            manual_cmd += ["-i", final_temp_image]
            
        if args.category:
            manual_cmd += ["-c", args.category]
        if args.issue:
            manual_cmd += ["-n", args.issue]
        if args.commit:
            manual_cmd += ["--commit"]
            
        print("\nWorkflow Setup Complete!")
        print("To complete the import:")
        print(f"1. Open and edit the CookLang recipe file: {cook_file_path}")
        print("2. Run the manual import script to compile and stage it:")
        print(f"   {' '.join(manual_cmd)}")
        
if __name__ == "__main__":
    main()
