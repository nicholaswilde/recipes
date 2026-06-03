#!/bin/bash

################################################################################
#
# linkcheck
# ----------------
# Run the lychee link checker on markdown files
#
# @author nιcнolaѕ wιlde, 0x08b7d7a3
# @date 02 Jun 2026
# @version 0.1.0
#
################################################################################

set -e
set -o pipefail
readonly DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )/../" >/dev/null 2>&1 && pwd )
cd "${DIR}"
find . -not -path '*.github*' -not -path '*cook*' -not -path '*.venv*' -not -path '*.cache*' -name "*.md" -exec lychee {} +
