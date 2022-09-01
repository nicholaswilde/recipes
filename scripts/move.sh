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

# DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
ROOT_DIR="$(git rev-parse --show-toplevel)"
DOCS_PATH="${ROOT_DIR}/docs"
IMAGES_PATH="${DOCS_PATH}/assets/images"
SCRIPT_NAME=$(basename "${0}")
SCRIPT_VERSION="0.1.0"
SCRIPT_DESC="Move recipes to their intended locations"
DEBUG=false

# readonly DIR
readonly SCRIPT_NAME
readonly SCRIPT_VERSION
readonly ROOT_DIR
readonly DOCS_PATH
readonly DEBUG
readonly IMAGES_PATH

# Check is variable is null
function is_null {
  [ -z "${1}" ]
}

# printf usage_error if something isn't right.
function usage_error() {
  show_usage "${1}"
  printf "\nTry %s -h for more options.\n" "${1}" >&2
  exit 1
}

function show_usage(){
  printf "Usage: %s [OPTIONS] FILENAME\n" "${1}"
}

function show_version(){
  printf "%s version %s\n" "${1}" "${2}"; exit 0
}

function script_desc(){
  printf "%s\n\n" "${1}"
}

# Show the help
function show_help(){
  show_usage "${1}"
  script_desc "${2}"
  printf "Mandatory arguments:\n"
  printf "  FILENAME            The cook filename to move\n\n"
  printf "Options:\n"
  printf "  -h, --help          Print this Help.\n"
  printf "  -v, --version       Print script version and exit.\n"
  exit 0
}

function get_category(){
  basename "$(dirname "${1}")"
}

function show_error(){
  printf "Could not get \`%s\`\n" "${1}"
  exit 1
}

function get_extension() {
  printf '%s\n' "${1#*.}"
}

function to_lower() {
  s="${1// /-}"
  printf '%s\n' "${s,,}"
}

function remove_extension() {
  printf '%s\n' "${1%%.*}"
}

function get_filename() {
  basename "${1}"
}

function get_image() {
  s="${1}"
  if [ -f "${s}.jpg" ]; then
    readlink -f "${s}.jpg"
  elif [ -f "${s}.png" ]; then
    readlink -f "${s}.png"
  fi
}

function spell_check() {
  npx spellchecker -d "${ROOT_DIR}"/dictionary.txt -f "${@}"
}

function check_links() {
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
  markdown_path=$(readlink -f "cook/${category}/${lower}.md")
  [ "${DEBUG}" = true ] && printf "markdown_path: %s\n" "${markdown_path}"
  if [ ! -f "${markdown_path}" ]; then
    cook-docs -c "${ROOT_DIR}/cook/${category}"
  fi
  test -f "${markdown_path}" || (printf "File does not exist, %s\n" "${markdown_path}" && exit 1)
  image_path=$(get_image "cook/${category}/${recipe_name}")
  [ "${DEBUG}" = true ] && printf "image_path: %s\n" "${image_path}"
  image_extension=$(get_extension "${image_path}")
  [ "${DEBUG}" = true ] && printf "image_extension: %s\n" "${image_extension}"
  new_image_path="${IMAGES_PATH}/${lower}.${image_extension}"
  [ "${DEBUG}" = true ] && printf "new_image_path: %s\n" "${new_image_path}"
  new_markdown_path="${DOCS_PATH}/${category}/${lower}.md"
  test -d "${DOCS_PATH}/${category}" || (printf "Folder does not exist, %s\n" "${DOCS_PATH}/${category}" && exit 1)
  [ "${DEBUG}" = true ] && printf "new_markdown_path: %s\n" "${new_markdown_path}"
  cp "${image_path}" "${new_image_path}"
  mv "${markdown_path}" "${new_markdown_path}"
  spell_check "${new_markdown_path}" "${recipe_path}"
  check_links "${new_markdown_path}"
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
