#!/bin/bash

################################################################################
#
# move
# ----------------
# Compile and move recipes to their intended locations using cook-docs
#
# @author nιcнolaѕ wιlde, 0x08b7d7a3
# @date 02 Sep 2022
# @version 0.4.0
#
################################################################################

set -e
set -o pipefail

if ! command -v uv &> /dev/null; then
  echo "Error: 'uv' is not installed. Please install it to run Python scripts." >&2
  exit 1
fi

if ! command -v cook-docs &> /dev/null; then
  echo "Error: 'cook-docs' is not installed." >&2
  exit 1
fi

# https://stackoverflow.com/a/246128/1061279
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
SCRIPT_NAME=$(basename "${0}")
SCRIPT_VERSION="$(grep "# @version" "${0}" | sed 's/\# \@version //' | head -n1)"
SCRIPT_DESC="Compile and move recipes to their intended locations"
DEBUG=false
FORCE=false

readonly DIR
readonly SCRIPT_NAME
readonly SCRIPT_VERSION
readonly SCRIPT_DESC
readonly DEBUG

# shuck:disable=C003
source "${DIR}/lib/libbash"

function copy_names() {
  if command_exists copy; then
    lb_infoln "Copying names"
    arr=()
    for path in "${@}"; do
      s=$(get_recipe_name "${path}")
      s=$(to_lower "${s}")
      c=$(get_category "${path}")
      n=$(get_recipe_name "${path}")
      arr+=("{ \"${n}\" = \"${c}/${s}.md\" },")
    done
    printf "%s" "${arr[@]}" | copy
  fi
}

function spell_check() {
  lb_infoln "Checking spelling"
  arr=()
  for path in "${@}"; do
    arr+=("${path}")
    s=$(get_new_markdown_path "${path}")
    s=$(realpath --relative-to="${ROOT_DIR}" "${s}")
    arr+=("${s}")
  done
  cd "${ROOT_DIR}"
  if command_exists typos; then
    uv run scripts/generate_typos_config.py || true
    for p in "${arr[@]}"; do
      typos "${p}" || true
    done
  elif command_exists npx; then
    npx -y spellchecker-cli -d "${ROOT_DIR}/dictionary.txt" -f "${arr[@]}" || true
  fi
}

function links_check() {
  lb_infoln "Checking links"
  if command_exists lychee; then
    for path in "${@}"; do
      s=$(get_new_markdown_path "${path}")
      s=$(realpath --relative-to="${ROOT_DIR}" "${s}")
      (cd "${ROOT_DIR}" && lychee "${s}") || true
    done
  else
    lb_infoln "lychee not found, skipping links check"
  fi
}

function optimize_copied_image() {
  local img_path="${1}"
  local md_path="${2}"
  [ -f "${img_path}" ] || return 0

  local filename
  filename=$(basename "${img_path}")
  local ext="${filename##*.}"
  local base="${filename%.*}"

  if [[ "${ext,,}" == "jpg" || "${ext,,}" == "jpeg" ]]; then
    local webp_path="${img_path%.*}.webp"
    if command_exists cwebp && cwebp -q 80 -metadata all "${img_path}" -o "${webp_path}" &>/dev/null; then
      lb_infoln "Converted image to WebP"
      rm -f "${img_path}"
    elif uv run python3 -c "import sys; from PIL import Image, ImageFile; ImageFile.LOAD_TRUNCATED_IMAGES = True; Image.open(sys.argv[1]).convert('RGB').save(sys.argv[2], 'WEBP', quality=80)" "${img_path}" "${webp_path}" &>/dev/null; then
      lb_infoln "Converted image to WebP (Pillow fallback)"
      rm -f "${img_path}"
    else
      lb_infoln "Warning: Failed to convert image to WebP; keeping ${filename}"
      local escaped_name="${filename//&/\\&}"
      sed -i "s|assets/images/${base}\.webp|assets/images/${escaped_name}|g" "${md_path}"
    fi
  elif [[ "${ext,,}" == "png" ]]; then
    if command_exists oxipng; then
      lb_infoln "Optimizing PNG image"
      if ! oxipng -o 4 --strip safe "${img_path}" &>/dev/null; then
        lb_infoln "Warning: Failed to optimize PNG image using oxipng"
      fi
    else
      lb_infoln "Warning: oxipng not found, skipping PNG optimization"
    fi
  fi
}

function move_files(){
  recipe_path="${1}"
  test -f "${recipe_path}" || { printf "File does not exist, %s\n" "${recipe_path}"; exit 1; }
  lb_infoln "Compiling recipe with cook-docs"
  recipe_path=$(get_recipe_path "${recipe_path}")

  category=$(get_category "${recipe_path}")
  is_null "${category}" && printf "Could not get \`category\`\n" && exit 1

  new_markdown_path=$(get_new_markdown_path "${recipe_path}")
  test -d "${DOCS_PATH}/${category}" || mkdir -p "${DOCS_PATH}/${category}"

  local image_path
  image_path=$(get_image_path "${recipe_path}")
  local cook_docs_args=()
  if [ "${FORCE}" = true ]; then
    cook_docs_args+=("--force")
  fi

  local copied_image_path=""
  if [ -n "${image_path}" ] && [ -f "${image_path}" ]; then
    copied_image_path=$(get_new_image_path "${recipe_path}")
    local src_ext="${image_path##*.}"
    if [[ "${src_ext,,}" == "jpg" || "${src_ext,,}" == "jpeg" ]]; then
      cook_docs_args+=("--image-ext" "webp")
    fi
  fi

  cd "${ROOT_DIR}"

  # Single-pass compile: frontmatter, emojis, gram weights, cross-links,
  # companion asset copy, and non-destructive merge (configured in .cookdocs.toml)
  cook-docs "${cook_docs_args[@]}" "${recipe_path}"
  test -f "${new_markdown_path}" || { printf "File does not exist, %s\n" "${new_markdown_path}"; exit 1; }

  if [ -n "${copied_image_path}" ]; then
    optimize_copied_image "${copied_image_path}" "${new_markdown_path}"
  fi

  # Ensure H1 header has a valid emoji shortcode when .cook lacks title metadata
  uv run scripts/check_header_emojis.py --fix "${new_markdown_path}" || true

  if command_exists rumdl; then
    rumdl fmt "${new_markdown_path}" &>/dev/null || true
  fi

  recipe_name=$(get_recipe_name "${recipe_path}")
  relative_markdown_path=$(realpath --relative-to="${DOCS_PATH}" "${new_markdown_path}")
  uv run "${DIR}/add_recipe_nav.py" "${recipe_name}" "${relative_markdown_path}"
}

function main(){
  for path in "${@}"; do
    [ "${DEBUG}" = true ] && debug_print "${path}"
    do_checks "${path}"
    move_files "${path}"
  done
  spell_check "${@}"
  links_check "${@}"
  copy_names "${@}"
}

if [ $# -eq 0 ]; then usage_error "${SCRIPT_NAME}"; fi

# https://www.jamescoyle.net/how-to/1774-bash-getops-example
# https://opensource.com/article/19/12/help-bash-program
while getopts ":fhv-" o; do
  # support long options: https://stackoverflow.com/a/28466267/519360
  if [ "${o}" = "-" ]; then
    o="${OPTARG%%=*}"
    OPTARG="${OPTARG#"$o"}"
    OPTARG="${OPTARG#=}"
  fi
  # shuck:disable=C135
  case "${o}" in
    f|force)   FORCE=true;;
    h|help)    show_help "${SCRIPT_NAME}" "${SCRIPT_DESC}";;
    v|version) show_version "${SCRIPT_NAME}" "${SCRIPT_VERSION}";;
    ??*)       usage_error "${SCRIPT_NAME}";;
    ?)         usage_error "${SCRIPT_NAME}";;
  esac
done
shift $((OPTIND-1))

main "$@"
