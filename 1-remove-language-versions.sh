#!/usr/bin/env bash
# 1-remove-language-versions.sh
# Removes all .ipynb files that contain a language classifier in their name,
# keeping only the English (untagged) versions.
#
# Language classifiers matched: two-letter ISO 639-1 codes such as
#   _de, _fr, _es, _ja, _ko, _pt, _it, _zh, _nl, _pl, _ru, _sv, _ar, ...
# Pattern: any .ipynb whose basename contains _XX (underscore + exactly two
# lowercase letters) immediately before the .ipynb extension.
# Example:  01_hello_agent_de.ipynb  → removed
#           01_hello_agent.ipynb     → kept

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# Find and remove ipynb files with a language tag (_xx) before the extension
mapfile -t FILES < <(find "$TARGET_DIR" -name '*_[a-z][a-z].ipynb' -type f)

if [[ ${#FILES[@]} -eq 0 ]]; then
    echo "No language-tagged .ipynb files found. Nothing to remove."
    exit 0
fi

echo "Removing ${#FILES[@]} language-tagged .ipynb file(s):"
for f in "${FILES[@]}"; do
    echo "  $(basename "$f")"
    rm "$f"
done

echo "Done. Only English (untagged) notebooks remain."
