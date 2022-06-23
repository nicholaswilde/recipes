#!/bin/bash
shopt -s globstar
shopt -s dotglob nullglob

dirs=( ../**/*.cook )          # glob the names

printf -v dirs_d ' \"%s\"' "${dirs[@]}"
dirs_d=${dirs_d:1}                  # remove the leading space

# printf '%s\n' "${dirs_d}"

"cook shopping-list ${dirs_d}"
