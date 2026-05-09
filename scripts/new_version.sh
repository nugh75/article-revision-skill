#!/usr/bin/env bash
# Bump article version: copy `article-vN-...md`
# into `article-v(N+1)-YYYY-MM-DD-HHMM[-anonymous].md`.
#
# Accepts source filenames in either of these formats:
#   article-vN-YYYY-MM-DD.md
#   article-vN-YYYY-MM-DD-HHMM.md
# (plus the optional `-anonymous` suffix).
#
# Usage:
#     new_version.sh <path/to/article-vN-...md>
#     new_version.sh                                  # auto-find latest
#     new_version.sh --articles-dir articles/

set -euo pipefail

ARTICLES_DIR="."
VERBOSE=0

while [[ $# -gt 0 ]]; do
    case "$1" in
        --articles-dir) ARTICLES_DIR="$2"; shift 2 ;;
        --verbose|-v) VERBOSE=1; shift ;;
        --) shift; break ;;
        *) break ;;
    esac
done

if [[ $# -ge 1 ]]; then
    SRC="$1"
else
    # find latest *-vN-YYYY-...md by version number, any prefix
    SRC=$(find "$ARTICLES_DIR" -maxdepth 3 -type f -name '*-v[0-9]*-*.md' \
        | sed -E 's/.*-v([0-9]+)-([0-9]+).*/\1\t\2\t&/' \
        | sort -k1,1n -k2,2 \
        | tail -1 \
        | cut -f3-)
    if [[ -z "$SRC" ]]; then
        echo "ERROR: no *-v*.md found under $ARTICLES_DIR" >&2
        exit 2
    fi
fi

if [[ ! -f "$SRC" ]]; then
    echo "ERROR: source file not found: $SRC" >&2
    exit 2
fi

BASENAME=$(basename "$SRC")
DIRNAME=$(dirname "$SRC")

# Extract version number and the static prefix.
# Pattern: <prefix>-vN-YYYY-MM-DD[-HHMM][-anonymous].md
# Examples:
#   article-v9-2026-05-08.md
#   scientific-article-praxis-v9-2026-05-08-anonymous.md
#   draft-v3-2026-05-08-1430.md
if [[ "$BASENAME" =~ ^(.+)-v([0-9]+)-[0-9]{4}-[0-9]{2}-[0-9]{2}(-[0-9]{4})?(-anonymous|-anonima)?\.md$ ]]; then
    PREFIX="${BASH_REMATCH[1]}"
    VERSION="${BASH_REMATCH[2]}"
    SUFFIX="${BASH_REMATCH[4]:-}"
else
    echo "ERROR: filename doesn't match <prefix>-vN-YYYY-MM-DD[-HHMM][-anonymous].md: $BASENAME" >&2
    exit 2
fi

NEW_VERSION=$((VERSION + 1))
TIMESTAMP=$(date +%F-%H%M)
NEW_NAME="${PREFIX}-v${NEW_VERSION}-${TIMESTAMP}${SUFFIX}.md"
DEST="${DIRNAME}/${NEW_NAME}"

if [[ -e "$DEST" ]]; then
    echo "ERROR: destination already exists: $DEST" >&2
    exit 2
fi

cp "$SRC" "$DEST"
[[ $VERBOSE -eq 1 ]] && echo "Copied: $SRC → $DEST" >&2

echo "$DEST"
