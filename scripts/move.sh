#!/bin/bash

################################################################################
#
# move
# ----------------
# Move recipes to their intended locations
#
# @author Nicholas Wilde, 0x08b7d7a3
# @date 02 Sep 2022
# @version 0.2.0
#
################################################################################

set -e
set -o pipefail

# https://stackoverflow.com/a/246128/1061279

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
ROOT_DIR="$(git rev-parse --show-toplevel)"
DOCS_PATH="${ROOT_DIR}/docs"
COOK_PATH="${ROOT_DIR}/cook"
IMAGES_PATH="${DOCS_PATH}/assets/images"
SCRIPT_NAME=$(basename "${0}")
SCRIPT_VERSION="$(grep "# @version" "${0}" | sed 's/\# \@version //'|\head -n1)"
SCRIPT_DESC="Move recipes to their intended locations"
DEBUG=true

readonly DIR
readonly SCRIPT_NAME
readonly SCRIPT_VERSION
readonly ROOT_DIR
readonly DOCS_PATH
readonly DEBUG
readonly IMAGES_PATH
readonly COOK_PATH

# shellcheck source=/dev/null
source "${DIR}/lib/libbash"

function spell_check() {
  arr=()
  for path in "${@}"; do
    arr+=("${path}")
    s=$(get_new_markdown_path "${path}")
    s=$(realpath --relative-to="${ROOT_DIR}" "${s}")
    arr+=("${s}")
  done
  cd "${ROOT_DIR}"
  npx spellchecker -d "${ROOT_DIR}/dictionary.txt" -f "${arr[@]}"
}

function links_check() {
  arr=()
  for path in "${@}"; do
    s=$(get_new_markdown_path "${path}")
    docker run --rm -v /:/tmp:ro -i -w /tmp ghcr.io/tcort/markdown-link-check:stable "/tmp${s}" -c "/tmp${ROOT_DIR}/mlc_config.json"
  done
}

function get_recipe_path(){
  s=$(readlink -f "${1}")
  printf '%s\n' "${s}"
}

function get_recipe_filename(){
  get_filename "${1}"
}

function get_recipe_name(){
  recipe_filename=$(get_filename "${1}")
  remove_extension "${recipe_filename}"
}

function get_markdown_path(){
  recipe_name=$(get_recipe_name "${1}")
  category=$(get_category "${1}")
  lower=$(to_lower "${recipe_name}")
  readlink -f "${COOK_PATH}/${category}/${lower}.md"
}

function get_image_path(){
  category=$(get_category "${1}")
  recipe_name=$(get_recipe_name "${1}")
  get_image "${COOK_PATH}/${category}/${recipe_name}"
}

function get_new_image_path(){
  recipe_name=$(get_recipe_name "${1}")
  lower=$(to_lower "${recipe_name}")
  image_path=$(get_image_path "${recipe_path}")
  image_extension=$(get_extension "${image_path}")
  printf "%s/%s.%s" "${IMAGES_PATH}" "${lower}" "${image_extension}"
}

function get_new_markdown_path(){
  recipe_name=$(get_recipe_name "${1}")
  category=$(get_category "${1}")
  lower=$(to_lower "${recipe_name}")
  printf "%s/%s/%s.md" "${DOCS_PATH}" "${category}" "${lower}"
}

function move_files(){
  # Check if file exists
  recipe_path="${1}"
  test -f "${1}" || (printf "File does not exist, %s\n" "${1}" && exit 1)

  recipe_path=$(get_recipe_path "${recipe_path}")

  category=$(get_category "${recipe_path}")
  is_null "${category}" && printf "Could not get \`category\`\n" && exit 1

  recipe_filename=$(get_filename "${recipe_path}")
  is_null "${recipe_filename}" && printf "Could not get \`recipe_filename\`\n" && exit 1

  recipe_name=$(get_recipe_name "${1}")

  markdown_path=$(get_markdown_path "${recipe_path}")

  if [ ! -f "${markdown_path}" ]; then
    cook-docs -c "${COOK_PATH}/${category}"
  fi
  test -f "${markdown_path}" || (printf "File does not exist, %s\n" "${markdown_path}" && exit 1)

  image_path=$(get_image_path "${recipe_path}")

  new_image_path=$(get_new_image_path "${recipe_path}")

  new_markdown_path=$(get_new_markdown_path "${recipe_path}")
  test -d "${DOCS_PATH}/${category}" || (printf "Folder does not exist, %s\n" "${DOCS_PATH}/${category}" && exit 1)

  if [ -f "${image_path}" ]; then
    cp "${image_path}" "${new_image_path}"
  fi

  mv "${markdown_path}" "${new_markdown_path}"
}

function debug_print(){
  recipe_path=$(get_recipe_path "${1}")
  printf "recipe_path: %s\n" "${recipe_path}"
  printf "category: %s\n" "$(get_category "${recipe_path}")"
  printf "recipe_filename: %s\n" "$(get_filename "${recipe_path}")"
  printf "recipe_name: %s\n" "$(get_recipe_name "${recipe_path}")"
  printf "markdown_path: %s\n" "$(get_markdown_path "${recipe_path}")"
  printf "image_path: %s\n" "$(get_image_path "${recipe_path}")"
  printf "new_image_path: %s\n" "$(get_new_image_path "${recipe_path}")"
  printf "new_markdown_path: %s\n" "$(get_new_markdown_path "${recipe_path}")"
}

function main(){
  for path in "${@}"; do
    [ "${DEBUG}" = true ] && debug_print "${path}"
    move_files "${path}"
  done
  spell_check "${@}"
  links_check "${@}"
}

if [ $# -eq 0 ]; then usage_error "${SCRIPT_NAME}"; fi

# https://www.jamescoyle.net/how-to/1774-bash-getops-example
# https://opensource.com/article/19/12/help-bash-program
# Get the options
# while getopts ":hv" o; do
while getopts ":hv-" o; do
  # support long options: https://stackoverflow.com/a/28466267/519360
  if [ "${o}" = "-" ]; then   # long option: reformulate o and OPTARG
    o="${OPTARG%%=*}"       # extract long option name
    OPTARG="${OPTARG#"$o"}"   # extract long option argument (may be empty)
    OPTARG="${OPTARG#=}"      # if long option argument, remove assigning `=`
  fi
  case "${o}" in
    h|help)    show_help "${SCRIPT_NAME}" "${SCRIPT_DESC}";;
    v|version) show_version "${SCRIPT_NAME}" "${SCRIPT_VERSION}";;
    ??*)         usage_error "${SCRIPT_NAME}";;
    ?)           usage_error "${SCRIPT_NAME}";;
  esac
done
shift $((OPTIND-1)) # remove parsed options and args from $@ list

main "$@"
