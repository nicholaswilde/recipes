#!/bin/bash

################################################################################
#
# optimize-images
# ----------------
# Convert JPEG to WebP, optimize PNG, and update markdown references.
#
# @author nιcнolaѕ wιlde
# @date 12 Jun 2026
# @version 0.1.0
#
################################################################################

set -e
set -o pipefail

# Check dependencies
if ! command -v cwebp &>/dev/null; then
  echo "Error: 'cwebp' is not installed. Please install it (e.g. 'apt-get install webp' or 'brew install webp')." >&2
  exit 1
fi

if ! command -v oxipng &>/dev/null; then
  echo "Error: 'oxipng' is not installed. Please install it (e.g. 'cargo install oxipng' or 'brew install oxipng')." >&2
  exit 1
fi

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
readonly DIR

# shuck:disable=C003
source "${DIR}/lib/libbash"

CATEGORY="${1:-}"

TOTAL_ORIG_SIZE=0
TOTAL_COMP_SIZE=0
FILES_PROCESSED=0

# Helper to update markdown references to the new WebP filename
update_references() {
  local orig_name="$1"
  local new_name="$2"
  local search_dir="$3"
  
  # Use grep -rl to find files referencing the old image, then update them
  grep -rl "assets/images/${orig_name}" "$search_dir" 2>/dev/null | while read -r file; do
    sed -i "s|assets/images/${orig_name}|assets/images/${new_name}|g" "$file"
  done
}

process_image() {
  local img_path="$1"
  local filename
  filename=$(basename "$img_path")
  local ext="${filename##*.}"
  local base="${filename%.*}"
  
  local search_dir
  if [ -n "$CATEGORY" ]; then
    search_dir="${DOCS_PATH}/${CATEGORY}"
  else
    search_dir="${DOCS_PATH}"
  fi

  if [ ! -f "$img_path" ]; then
    return
  fi

  local mime
  mime=$(get_mime_type "$img_path" 2>/dev/null || echo "")

  local orig_size
  orig_size=$(wc -c < "$img_path")
  
  # Determine action based on mime type or file extension
  if [[ "$mime" == "image/jpeg" || "${ext,,}" == "jpg" || "${ext,,}" == "jpeg" ]]; then
    local webp_path="${img_path%.*}.webp"
    
    # Run cwebp and handle failure gracefully
    if cwebp -q 80 -metadata all "$img_path" -o "$webp_path" &>/dev/null; then
      local new_size
      new_size=$(wc -c < "$webp_path")
      
      rm -f "$img_path"
      
      # Update markdown references
      update_references "$filename" "${base}.webp" "$search_dir"
      
      TOTAL_ORIG_SIZE=$((TOTAL_ORIG_SIZE + orig_size))
      TOTAL_COMP_SIZE=$((TOTAL_COMP_SIZE + new_size))
      FILES_PROCESSED=$((FILES_PROCESSED + 1))
    else
      echo "Warning: Failed to convert $img_path to WebP format." >&2
    fi
    
  elif [[ "$mime" == "image/png" || "${ext,,}" == "png" ]]; then
    # Optimize PNG in place and handle failure gracefully
    if oxipng -o 4 --strip safe "$img_path" &>/dev/null; then
      local new_size
      new_size=$(wc -c < "$img_path")
      
      TOTAL_ORIG_SIZE=$((TOTAL_ORIG_SIZE + orig_size))
      TOTAL_COMP_SIZE=$((TOTAL_COMP_SIZE + new_size))
      FILES_PROCESSED=$((FILES_PROCESSED + 1))
    else
      echo "Warning: Failed to optimize PNG $img_path with oxipng." >&2
    fi
  fi
}

if [ -n "$CATEGORY" ]; then
  # Category specified: only process images referenced in docs/category/*.md
  if [ ! -d "${DOCS_PATH}/${CATEGORY}" ]; then
    echo "Error: Category directory '${DOCS_PATH}/${CATEGORY}' does not exist." >&2
    exit 1
  fi
  
  # Find all markdown files in category
  mapfile -t md_files < <(find "${DOCS_PATH}/${CATEGORY}" -name "*.md" -type f 2>/dev/null)
  
  if [ ${#md_files[@]} -eq 0 ]; then
    echo "No markdown files found in category '${CATEGORY}'."
    exit 0
  fi
  
  # Extract image names referenced in these markdown files
  # Match assets/images/filename.ext
  mapfile -t referenced_images < <(grep -o -h -E "assets/images/[a-zA-Z0-9_.-]+\.(jpg|jpeg|png|JPG|JPEG|PNG)" "${md_files[@]}" 2>/dev/null | sed 's|assets/images/||' | sort -u)
  
  for img in "${referenced_images[@]}"; do
    process_image "${IMAGES_PATH}/${img}"
  done

else
  # No category specified: process all images in docs/assets/images
  if [ -d "$IMAGES_PATH" ]; then
    while IFS= read -r -d '' file; do
      process_image "$file"
    done < <(find "$IMAGES_PATH" -type f \( -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" \) -print0)
  fi
fi

# Report space savings
if [ "$FILES_PROCESSED" -gt 0 ]; then
  SAVED=$((TOTAL_ORIG_SIZE - TOTAL_COMP_SIZE))
  if [ "$TOTAL_ORIG_SIZE" -gt 0 ]; then
    PCT=$(( SAVED * 100 / TOTAL_ORIG_SIZE ))
  else
    PCT=0
  fi
  echo "Processed $FILES_PROCESSED files."
  echo "Original Size: $TOTAL_ORIG_SIZE bytes"
  echo "Compressed Size: $TOTAL_COMP_SIZE bytes"
  echo "Saved: $SAVED bytes ($PCT% savings)"
else
  echo "No images processed."
fi
