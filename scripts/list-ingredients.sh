#!/bin/bash
################################################################################
#
# boilerplate-bash
# ----------------
# Copy cook shopping-list command to clipboard to list all ingredients in all
# cook recipes.
#
# @author Nicholas Wilde, 0x08b7d7a3
# @date 24 Jun 2022
# @version 0.0.1
#
################################################################################
set -e
shopt -s globstar
shopt -s dotglob nullglob

dirs=( ../**/*.cook )          # glob the names

# Convert array to string and add double quotes around each file path to handle spaces
printf -v dirs_d ' \"%s\"' "${dirs[@]}"
dirs_d=${dirs_d:1}                  # remove the leading space

# Copy the command to the clipboard to avoid file name too long error
# Chromebook copy
# https://chromium.googlesource.com/apps/libapps/+/master/hterm/etc/osc52.sh
echo "cook shopping-list ${dirs_d}" | copy
