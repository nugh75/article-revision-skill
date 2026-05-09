#!/usr/bin/env bash
# Word-level diff between two article versions, summarized by section.
#
# Usage:
#     diff_versions.sh path/to/article-vN.md path/to/article-v(N+1).md
#     diff_versions.sh --auto path/to/article-v(N+1).md   # picks vN automatically

set -euo pipefail

AUTO=0

while [[ $# -gt 0 ]]; do
    case "$1" in
        --auto) AUTO=1; shift ;;
        --) shift; break ;;
        *) break ;;
    esac
done

if [[ $AUTO -eq 1 ]]; then
    NEW="${1:-}"
    [[ -z "$NEW" ]] && { echo "ERROR: pass new version path with --auto" >&2; exit 2; }
    BASENAME=$(basename "$NEW")
    if [[ "$BASENAME" =~ ^(.+)-v([0-9]+)- ]]; then
        PREFIX=${BASH_REMATCH[1]}
        N=${BASH_REMATCH[2]}
    else
        echo "ERROR: cannot parse version from $BASENAME" >&2; exit 2
    fi
    PREV_N=$((N - 1))
    DIR=$(dirname "$NEW")
    OLD=$(find "$DIR" -maxdepth 1 -name "${PREFIX}-v${PREV_N}-*.md" | head -1)
    [[ -z "$OLD" ]] && { echo "ERROR: previous version v${PREV_N} not found in $DIR" >&2; exit 2; }
else
    OLD="${1:-}"; NEW="${2:-}"
    [[ -z "$OLD" || -z "$NEW" ]] && { echo "ERROR: usage: diff_versions.sh OLD NEW" >&2; exit 2; }
fi

[[ -f "$OLD" ]] || { echo "ERROR: not found: $OLD" >&2; exit 2; }
[[ -f "$NEW" ]] || { echo "ERROR: not found: $NEW" >&2; exit 2; }

echo "# Diff: $(basename "$OLD") → $(basename "$NEW")"
echo ""

# Use git diff if available for word-level
if command -v git >/dev/null; then
    git diff --no-index --word-diff=plain --word-diff-regex='[A-Za-zÀ-ſ0-9]+|[^[:space:]]' "$OLD" "$NEW" | head -200 || true
else
    diff -u "$OLD" "$NEW" || true
fi

echo ""
echo "## Char counts"
OLD_C=$(wc -c < "$OLD")
NEW_C=$(wc -c < "$NEW")
DELTA=$((NEW_C - OLD_C))
SIGN=$([[ $DELTA -ge 0 ]] && echo "+" || echo "")
echo "  old: $OLD_C"
echo "  new: $NEW_C"
echo "  delta: ${SIGN}${DELTA}"
