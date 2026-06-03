#!/bin/bash
set -e
set -o pipefail
readonly DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )/../" >/dev/null 2>&1 && pwd )
cd "${DIR}"
find . -not -path '*.github*' -not -path '*cook*' -not -path '*.venv*' -not -path '*.cache*' -name "*.md" -exec lychee {} +
