#!/bin/bash

################################################################################
#
# move
# ----------------
# Move recipes to their intended locations
#
# @author Nicholas Wilde, 0x08b7d7a3
# @date 02 Sep 2022
# @version 0.3.0
#
################################################################################

set -e
set -o pipefail

# https://stackoverflow.com/a/246128/1061279
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
SCRIPT_NAME=$(basename "${0}")
SCRIPT_VERSION="$(grep "# @version" "${0}" | sed 's/\# \@version //'|\head -n1)"
SCRIPT_DESC="Move recipes to their intended locations"
DEBUG=false

readonly DIR
readonly SCRIPT_NAME
readonly SCRIPT_VERSION
readonly SCRIPT_DESC
readonly DEBUG

# shellcheck source=/dev/null
source "${DIR}/lib/libbash"

# shellcheck source=/dev/null
source "${DIR}/libbash/init"
# shellcheck source=/dev/null
source "${LIBBASH_DIR}/all"

function cleanup(){
  if command_exists task; then
   lb_infoln "Cleaning up"
    cd "${ROOT_DIR}"
    task clean
  fi
}

function copy_names() {
  if command_exists copy; then
   lb_infoln "Copying names"
    arr=()
    for path in "${@}"; do
      s=$(get_recipe_name "${path}")
      s=$(to_lower "${s}")
      c=$(get_category "${path}")
      n=$(get_recipe_name "${path}")
      arr+=("- ${n}: ${c}/${s}.md")
    done
    printf "%s" "${arr[@]}" | copy
  fi
}

function spell_check() {
 lb_infoln  "Checking spelling"
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
 lb_infoln "Checking links"
  arr=()
  for path in "${@}"; do
    s=$(get_new_markdown_path "${path}")
    docker run --rm -v /:/tmp:ro -i -w /tmp ghcr.io/tcort/markdown-link-check:stable "/tmp${s}" -c "/tmp${ROOT_DIR}/mlc_config.json"
  done
}

function move_files(){
  # Check if file exists
  recipe_path="${1}"
  test -f "${1}" || (printf "File does not exist, %s\n" "${1}" && exit 1)
 lb_infoln "Moving files"
  recipe_path=$(get_recipe_path "${recipe_path}")

  category=$(get_category "${recipe_path}")
  is_null "${category}" && printf "Could not get \`category\`\n" && exit 1

  recipe_filename=$(get_filename "${recipe_path}")
  is_null "${recipe_filename}" && printf "Could not get \`recipe_filename\`\n" && exit 1

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

function main(){
  for path in "${@}"; do
    [ "${DEBUG}" = true ] && debug_print "${path}"
    do_checks "${path}"
    move_files "${path}"
  done
  spell_check "${@}"
  links_check "${@}"
  copy_names "${@}"
  cleanup
}

if [ $# -eq 0 ]; then usage_error "${SCRIPT_NAME}"; fi

# https://www.jamescoyle.net/how-to/1774-bash-getops-example
# https://opensource.com/article/19/12/help-bash-program
# Get the options
# while getopts ":hv" o; do
while getopts ":hv-" o; do
  # support long options: https://stackoverflow.com/a/28466267/519360
  if [ "${o}" = "-" ]; then   # long option: reformulate o and OPTARG
    OPTARG=
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
