#!/bin/bash
set -e
set -o pipefail

a=$(git rev-parse --show-toplevel)
cd "${a}"
python3 scripts/generate_typos_config.py
typos
