#!/usr/bin/env bash
# sync_current.sh — align current.md, current.docx, bibliography.docx
# Usage: bash scripts/sync_current.sh <article-path> <bib-path>
# Called by workflow/96-sync-current.md at the end of every revision session.

set -euo pipefail

ARTICLE="${1:?Usage: sync_current.sh <article-path> <bib-path>}"
BIB="${2:?Usage: sync_current.sh <article-path> <bib-path>}"

ARTICLES_DIR="$(dirname "$ARTICLE")"
BIB_DIR="$(dirname "$BIB")"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Resolve paths relative to project root if not absolute
[[ "$ARTICLE" != /* ]] && ARTICLE="$PROJECT_ROOT/$ARTICLE"
[[ "$BIB"     != /* ]] && BIB="$PROJECT_ROOT/$BIB"
ARTICLES_DIR="$(dirname "$ARTICLE")"
BIB_DIR="$(dirname "$BIB")"

CURRENT_MD="$ARTICLES_DIR/current.md"
CURRENT_DOCX="$ARTICLES_DIR/current.docx"
BIB_DOCX="$BIB_DIR/bibliography.docx"

# --- 1. current.md ---
cp "$ARTICLE" "$CURRENT_MD"
echo "✓ current.md  → $CURRENT_MD"

# --- 2. current.docx ---
if ! command -v pandoc &>/dev/null; then
  echo "⚠ pandoc non trovato — current.docx non generato"
  echo "  Installa pandoc e riesegui: bash scripts/sync_current.sh $ARTICLE $BIB"
else
  PANDOC_OPTS=(
    --from markdown
    --to docx
    --standalone
    --bibliography "$BIB"
  )

  # journal reference.docx for formatting
  REF_DOCX="$PROJECT_ROOT/editorial-norms/reference.docx"
  [[ -f "$REF_DOCX" ]] && PANDOC_OPTS+=(--reference-doc "$REF_DOCX")

  # CSL citation style
  CSL_FILE=$(find "$PROJECT_ROOT/editorial-norms" -name "*.csl" 2>/dev/null | head -1)
  [[ -n "$CSL_FILE" ]] && PANDOC_OPTS+=(--csl "$CSL_FILE")

  pandoc "${PANDOC_OPTS[@]}" -o "$CURRENT_DOCX" "$CURRENT_MD"
  echo "✓ current.docx → $CURRENT_DOCX"
fi

# --- 3. bibliography.docx ---
if ! command -v pandoc &>/dev/null; then
  echo "⚠ pandoc non trovato — bibliography.docx non generato"
elif [[ ! -f "$BIB" ]]; then
  echo "⚠ $BIB non trovato — bibliography.docx non generato"
else
  # Build a minimal markdown wrapper that pandoc can render as a reference list
  TMPMD=$(mktemp /tmp/bib_XXXXXX.md)
  trap 'rm -f "$TMPMD"' EXIT

  cat > "$TMPMD" <<'MDEOF'
---
title: "Bibliography"
nocite: "@*"
---
MDEOF

  BIB_PANDOC_OPTS=(
    --from markdown
    --to docx
    --standalone
    --bibliography "$BIB"
  )

  CSL_FILE=$(find "$PROJECT_ROOT/editorial-norms" -name "*.csl" 2>/dev/null | head -1)
  [[ -n "$CSL_FILE" ]] && BIB_PANDOC_OPTS+=(--csl "$CSL_FILE")

  REF_DOCX="$PROJECT_ROOT/editorial-norms/reference.docx"
  [[ -f "$REF_DOCX" ]] && BIB_PANDOC_OPTS+=(--reference-doc "$REF_DOCX")

  pandoc "${BIB_PANDOC_OPTS[@]}" -o "$BIB_DOCX" "$TMPMD"
  echo "✓ bibliography.docx → $BIB_DOCX"
fi
