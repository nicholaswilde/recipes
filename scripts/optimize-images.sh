#!/usr/bin/env bash

# Exit immediately if a command exits with a non-zero status
set -euo pipefail

# 1. Dependency check
check_dependencies() {
  local missing=()
  if ! command -v cwebp &>/dev/null; then
    missing+=("cwebp")
  fi
  if ! command -v oxipng &>/dev/null; then
    missing+=("oxipng")
  fi

  if [ ${#missing[@]} -ne 0 ]; then
    echo "Error: Missing required dependencies: ${missing[*]}"
    echo "Please install them before running this script."
    echo "On macOS: brew install webp oxipng"
    echo "On Ubuntu/Debian: sudo apt-get install -y webp oxipng"
    exit 1
  fi
}

check_dependencies

# Directories
IMAGES_DIR="docs/assets/images"
DOCS_DIR="docs"

# 2. Parse category argument
CATEGORY="${1:-}"

# Verify category directory if specified
if [ -n "$CATEGORY" ]; then
  if [ ! -d "$DOCS_DIR/$CATEGORY" ]; then
    echo "Error: Category directory '$DOCS_DIR/$CATEGORY' does not exist."
    exit 1
  fi
fi

# Function to get images belonging to a category
get_category_images() {
  local cat="$1"
  for f in "$DOCS_DIR/$cat"/*.md; do
    [ -f "$f" ] || continue
    local base
    base=$(basename "$f" .md)

    # Match by recipe base name
    if [ -f "$IMAGES_DIR/$base.jpg" ]; then
      echo "$IMAGES_DIR/$base.jpg"
    fi
    if [ -f "$IMAGES_DIR/$base.png" ]; then
      echo "$IMAGES_DIR/$base.png"
    fi

    # Parse explicit assets/images references in the file
    grep -o 'assets/images/[^)]*' "$f" | while read -r ref; do
      local filename
      filename=$(basename "$ref" | tr -d ' >' | cut -d'?' -f1)
      if [ -f "$IMAGES_DIR/$filename" ]; then
        echo "$IMAGES_DIR/$filename"
      fi
    done
  done | sort -u
}

# 3. Collect list of files to process
declare -a FILES_TO_PROCESS=()

if [ -n "$CATEGORY" ]; then
  echo "Scanning for images in category: $CATEGORY..."
  while read -r img; do
    if [ -n "$img" ]; then
      FILES_TO_PROCESS+=("$img")
    fi
  done < <(get_category_images "$CATEGORY")
else
  echo "Scanning all images in $IMAGES_DIR..."
  while read -r img; do
    if [ -n "$img" ]; then
      FILES_TO_PROCESS+=("$img")
    fi
  done < <(find "$IMAGES_DIR" -type f \( -name "*.jpg" -o -name "*.png" \) 2>/dev/null)
fi

TOTAL_FILES=${#FILES_TO_PROCESS[@]}
echo "Found $TOTAL_FILES images to process."

if [ "$TOTAL_FILES" -eq 0 ]; then
  echo "No images found to process. Exiting."
  exit 0
fi

# Variables for size statistics
TOTAL_ORIG_SIZE=0
TOTAL_NEW_SIZE=0

# Process files
for file in "${FILES_TO_PROCESS[@]}"; do
  [ -f "$file" ] || continue
  ext="${file##*.}"
  filename=$(basename "$file")

  orig_size=$(wc -c < "$file")
  TOTAL_ORIG_SIZE=$((TOTAL_ORIG_SIZE + orig_size))

  if [ "$ext" = "jpg" ]; then
    base_no_ext="${file%.*}"
    output_webp="$base_no_ext.webp"

    echo "Converting $filename to WebP..."
    if ! cwebp -q 80 -metadata all "$file" -o "$output_webp" 2>/dev/null; then
      echo "  cwebp failed. Attempting fallback conversion using Python Pillow..."
      if ! uv run python -c "from PIL import Image, ImageFile; ImageFile.LOAD_TRUNCATED_IMAGES = True; im = Image.open('$file'); im.save('$output_webp', 'WEBP', quality=80)" 2>/dev/null; then
        echo "  Warning: $filename is not a valid image or is completely corrupted. Skipping."
        # Keep original size and skip deletion
        TOTAL_NEW_SIZE=$((TOTAL_NEW_SIZE + orig_size))
        continue
      fi
    fi
    
    new_size=$(wc -c < "$output_webp")
    TOTAL_NEW_SIZE=$((TOTAL_NEW_SIZE + new_size))
    
    # Delete original JPEG
    rm "$file"

  elif [ "$ext" = "png" ]; then
    echo "Optimizing PNG: $filename..."
    if ! oxipng -o 4 --strip safe "$file" 2>/dev/null; then
      echo "  Warning: oxipng failed to optimize $filename. Skipping."
      TOTAL_NEW_SIZE=$((TOTAL_NEW_SIZE + orig_size))
      continue
    fi
    
    new_size=$(wc -c < "$file")
    TOTAL_NEW_SIZE=$((TOTAL_NEW_SIZE + new_size))
  fi
done

# 4. Update Markdown references
echo "Updating Markdown image references..."
if [ -n "$CATEGORY" ]; then
  # Only scan and update in target category folder
  find "$DOCS_DIR/$CATEGORY" -type f -name "*.md" -print0 | xargs -0 sed -i 's/\.jpg/\.webp/g'
else
  # Scan and update all Markdown files under docs/
  find "$DOCS_DIR" -type f -name "*.md" -print0 | xargs -0 sed -i 's/\.jpg/\.webp/g'
fi

# 5. Report savings
SAVINGS_BYTES=$((TOTAL_ORIG_SIZE - TOTAL_NEW_SIZE))
SAVINGS_PCT=$(awk -v orig="$TOTAL_ORIG_SIZE" -v sav="$SAVINGS_BYTES" 'BEGIN { printf "%.2f", (orig > 0 ? (sav * 100 / orig) : 0) }')

echo "----------------------------------------"
echo "Image Optimization Complete!"
echo "Original Size: $TOTAL_ORIG_SIZE bytes"
echo "Optimized Size: $TOTAL_NEW_SIZE bytes"
echo "Total Savings: $SAVINGS_BYTES bytes ($SAVINGS_PCT%)"
echo "----------------------------------------"
