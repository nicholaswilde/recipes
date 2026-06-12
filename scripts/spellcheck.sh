#!/bin/bash

################################################################################
#
# spellcheck
# ----------------
# Re-generate typos configuration and run spellcheck
#
# @author nιcнolaѕ wιlde, 0x08b7d7a3
# @date 02 Jun 2026
# @version 0.1.0
#
################################################################################

set -e
set -o pipefail

if ! command -v uv &> /dev/null; then
  echo "Error: 'uv' is not installed. Please install it to run Python scripts." >&2
  exit 1
fi

a=$(git rev-parse --show-toplevel)
cd "${a}"
uv run scripts/generate_typos_config.py
typos
