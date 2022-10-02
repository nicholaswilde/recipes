#!/bin/bash
set -e
set -o pipefail
readonly DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )/../" >/dev/null 2>&1 && pwd )
for f in $(find "${DIR}" -not -path '*.github*' -not -path '*cook*' -not -path '*libbash*' -not -name '*index.md' -not -name '*README.md' -name \*.md); do
  s=$(head -n 1 "${f}")
  if [[ "${s}" != "---" ]]; then
    printf "%s: %s\n"  "${f}" "${s}"
    # sed -i '1i ---\ncomments: true\n---' "${f}"
  fi
done
