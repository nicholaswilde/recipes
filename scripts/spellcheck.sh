#!/bin/bash
set -e
set -o pipefail
shopt -s globstar
shopt -s dotglob nullglob

a=$(git rev-parse --show-toplevel)
cd "${a}"
spellchecker -d dictionary.txt -f {"./cook/**/*.cook","./docs/**/*.md"}
