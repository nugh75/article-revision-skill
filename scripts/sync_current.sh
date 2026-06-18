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

find_first_csl() {
  local norms_dir="$PROJECT_ROOT/editorial-norms"
  [[ -d "$norms_dir" ]] || return 0
  find "$norms_dir" -name "*.csl" -print -quit 2>/dev/null || true
}

docx_body_has_text() {
  local docx="$1"
  local text body

  [[ -s "$docx" ]] || return 1
  command -v unzip &>/dev/null || return 0

  text="$(unzip -p "$docx" word/document.xml 2>/dev/null \
    | sed -E 's/<[^>]+>/ /g' \
    | tr -s '[:space:]' ' ' || true)"
  body="${text//Bibliography/}"
  body="${body//References/}"
  body="${body//Bibliografia/}"
  [[ "$body" =~ [[:alnum:]] ]]
}

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
    --citeproc
    --bibliography "$BIB"
  )

  # journal reference.docx for formatting
  REF_DOCX="$PROJECT_ROOT/editorial-norms/reference.docx"
  [[ -f "$REF_DOCX" ]] && PANDOC_OPTS+=(--reference-doc "$REF_DOCX")

  # CSL citation style
  CSL_FILE="$(find_first_csl)"
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
  BIB_ENTRY_COUNT=$(grep -Eic '^[[:space:]]*@[A-Za-z]+[[:space:]]*[{(]' "$BIB" || true)
  if [[ "$BIB_ENTRY_COUNT" -eq 0 ]]; then
    echo "⚠ $BIB non contiene entry BibTeX — bibliography.docx non generato"
    exit 0
  fi

  # Build a minimal markdown wrapper that pandoc can render as a reference list
  TMPMD=$(mktemp /tmp/bib_XXXXXX.md)
  trap 'rm -f "$TMPMD"' EXIT

  cat > "$TMPMD" <<'MDEOF'
---
nocite: |
  @*
---

# Bibliography

::: {#refs}
:::
MDEOF

  BIB_PANDOC_OPTS=(
    --from markdown
    --to docx
    --standalone
    --citeproc
    --bibliography "$BIB"
  )

  CSL_FILE="$(find_first_csl)"
  [[ -n "$CSL_FILE" ]] && BIB_PANDOC_OPTS+=(--csl "$CSL_FILE")

  REF_DOCX="$PROJECT_ROOT/editorial-norms/reference.docx"
  [[ -f "$REF_DOCX" ]] && BIB_PANDOC_OPTS+=(--reference-doc "$REF_DOCX")

  pandoc "${BIB_PANDOC_OPTS[@]}" -o "$BIB_DOCX" "$TMPMD"
  if docx_body_has_text "$BIB_DOCX"; then
    echo "✓ bibliography.docx → $BIB_DOCX ($BIB_ENTRY_COUNT entries)"
  else
    echo "⚠ bibliography.docx generato ma sembra vuoto — controlla $BIB e lo stile CSL"
  fi
fi
