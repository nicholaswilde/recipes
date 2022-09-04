#!/bin/bash

################################################################################
#
# commit
# ----------------
# Commit recipes to the remote repo
#
# @author Nicholas Wilde, 0x08b7d7a3
# @date 02 Sep 2022
# @version 0.1.0
#
################################################################################

set -e
set -o pipefail

# https://stackoverflow.com/a/246128/1061279
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
SCRIPT_NAME=$(basename "${0}")
SCRIPT_VERSION="$(grep "# @version" "${0}" | sed 's/\# \@version //'|\head -n1)"
SCRIPT_DESC="Commit recipes to the remote repo"
DEBUG=false
COMMIT_MSG="feat: add"

readonly DIR
readonly SCRIPT_NAME
readonly SCRIPT_VERSION
readonly SCRIPT_DESC
readonly DEBUG

# shellcheck source=/dev/null
source "${DIR}/lib/libbash"

function file_status(){
  git diff --quiet "${1}"
}

function issue_exists(){
  gh issue view "${1}" > /dev/null 2>&1
}

function create_commit(){
  recipe_name=$(get_recipe_name "${1}")
  msg="${COMMIT_MSG} ${recipe_name}"
  if command_exists gh; then
    first=${recipe_name%% *}
    gh issue list -S "${first}"
    read -rp 'Enter the issue number that corresponds to the commit: ' issue_number
    if ! is_null "${issue_number}"; then
      if issue_exists "${issue_number}"; then
        [ "${DEBUG}" = true ] && printf "issue_number: %s\n" "${issue_number}"
        msg="${msg}. Fixes #${issue_number}."
      fi
    fi
  fi
  git commit -m "${msg}"
}

function add_files(){
  # Check if file exists
  recipe_path="${1}"
  test -f "${1}" || (printf "File does not exist, %s\n" "${1}" && exit 1)

  recipe_path=$(get_recipe_path "${recipe_path}")

  image_path=$(get_image_path "${recipe_path}")

  new_image_path=$(get_new_image_path "${recipe_path}")

  new_markdown_path=$(get_new_markdown_path "${recipe_path}")

  mkdocs_path="${ROOT_DIR}/mkdocs.yml"

  git add "${recipe_path}" "${image_path}" "${new_image_path}" "${new_markdown_path}" "${mkdocs_path}"
}

function main(){
  [ "${DEBUG}" = true ] && git status
  for path in "${@}"; do
    [ "${DEBUG}" = true ] && debug_print "${path}"
    add_files "${path}"
    if ! git diff --quiet; then
      create_commit "${path}"
    fi
  done
  [ "${DEBUG}" = true ] && git status
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
