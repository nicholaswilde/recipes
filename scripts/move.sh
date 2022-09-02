#!/bin/bash

################################################################################
#
# move
# ----------------
# Move recipes to their intended locations
#
# @author Nicholas Wilde, 0x08b7d7a3
# @date 15 Aug 2022
# @version 0.1.0
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
SCRIPT_VERSION="0.1.0"
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
  for path in "${@}"; do
    s=$(realpath --relative-to="${ROOT_DIR}" "${path}")
    arr+=("${s}")
  done
  cd "${ROOT_DIR}"
  npx spellchecker -d "${ROOT_DIR}/dictionary.txt" -f "${arr[@]}"
}

function links_check() {
  docker run --rm -v /:/tmp:ro -i -w /tmp ghcr.io/tcort/markdown-link-check:stable "/tmp${1}" -c "/tmp${ROOT_DIR}/mlc_config.json"
}

function move_files(){
  # Check if file exists
  recipe_path="${1}"
  [ "${DEBUG}" = true ] && printf "recipe_path: %s\n" "${recipe_path}"
  test -f "${1}" || (printf "File does not exist, %s\n" "${1}" && exit 1)
  # Get category
  recipe_path=$(readlink -f "${recipe_path}")
  category=$(get_category "${recipe_path}")
  is_null "${category}" && printf "Could not get \`category\`\n" && exit 1
  [ "${DEBUG}" = true ] && printf "category: %s\n" "${category}"
  recipe_filename=$(get_filename "${recipe_path}")
  is_null "${recipe_filename}" && printf "Could not get \`recipe_filename\`\n" && exit 1
  [ "${DEBUG}" = true ] && printf "recipe_filename: %s\n" "${recipe_filename}"
  recipe_name=$(remove_extension "${recipe_filename}")
  [ "${DEBUG}" = true ] && printf "recipe_name: %s\n" "${recipe_name}"
  recipe_extension=$(get_extension "${recipe_filename}")
  [ "${DEBUG}" = true ] && printf "recipe_extension: %s\n" "${recipe_extension}"
  lower=$(to_lower "${recipe_name}")
  [ "${DEBUG}" = true ] && printf "lower: %s\n" "${lower}"
  markdown_path=$(readlink -f "${COOK_PATH}/${category}/${lower}.md")
  [ "${DEBUG}" = true ] && printf "markdown_path: %s\n" "${markdown_path}"
  if [ ! -f "${markdown_path}" ]; then
    cook-docs -c "${COOK_PATH}/${category}"
  fi
  test -f "${markdown_path}" || (printf "File does not exist, %s\n" "${markdown_path}" && exit 1)
  image_path=$(get_image "${COOK_PATH}/${category}/${recipe_name}")
  [ "${DEBUG}" = true ] && printf "image_path: %s\n" "${image_path}"
  image_extension=$(get_extension "${image_path}")
  [ "${DEBUG}" = true ] && printf "image_extension: %s\n" "${image_extension}"
  new_image_path="${IMAGES_PATH}/${lower}.${image_extension}"
  [ "${DEBUG}" = true ] && printf "new_image_path: %s\n" "${new_image_path}"
  new_markdown_path="${DOCS_PATH}/${category}/${lower}.md"
  test -d "${DOCS_PATH}/${category}" || (printf "Folder does not exist, %s\n" "${DOCS_PATH}/${category}" && exit 1)
  [ "${DEBUG}" = true ] && printf "new_markdown_path: %s\n" "${new_markdown_path}"
  if [ -f "${image_path}" ]; then
    cp "${image_path}" "${new_image_path}"
  fi
  mv "${markdown_path}" "${new_markdown_path}"
  spell_check "${new_markdown_path}" "${recipe_path}"
  links_check "${new_markdown_path}"
}

function main(){
  move_files "${@}"
}

if [ $# -ne 1 ]; then usage_error "${SCRIPT_NAME}"; fi

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
