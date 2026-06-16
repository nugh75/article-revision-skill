# 96 — Sync Current Files

Mandatory post-decision-log step. Aligns the three "current" files so that
collaborators and external tools always see a single stable pointer to the
latest revision state.

This step is called by `95-decision-log.md` immediately after the session
entry is written. It runs even when no changes were accepted this round.

## Files produced / overwritten

| File | Content | Location |
|---|---|---|
| `articles/current.md` | Copy of the active article version | `articles/` |
| `articles/current.docx` | Pandoc conversion of `current.md` | `articles/` |
| `bibliography/bibliography.docx` | Formatted reference list from `reference.bib` | `bibliography/` |

## 1. Identify Sources

From working memory:

- `ARTICLE_PATH` — path to the active (bumped) article file.
- `BIBLIOGRAPHY_BIB_PATH` — from `.env`.
- `PYTHON_BIN` — project Python interpreter.

## 2. Sync `current.md`

```bash
cp "$ARTICLE_PATH" articles/current.md
```

Overwrite unconditionally. Announce in chat:
```
current.md → articles/current.md ✓
```

## 3. Generate `current.docx`

Run `scripts/sync_current.sh` which calls pandoc:

```bash
bash scripts/sync_current.sh "$ARTICLE_PATH" "$BIBLIOGRAPHY_BIB_PATH"
```

If pandoc is not installed, warn and skip (do not abort the closure):
```
⚠ pandoc non trovato — current.docx non generato.
  Installa pandoc e riesegui: bash scripts/sync_current.sh
```

If a `--reference-doc` file exists at `editorial-norms/reference.docx`, pass it
to pandoc for journal-compliant formatting.

## 4. Generate `bibliography.docx`

The same `scripts/sync_current.sh` call handles this. It converts `reference.bib`
to a formatted reference list using:

1. Pandoc + CSL (if a `.csl` file is found in `editorial-norms/`).
2. Fallback: plain numbered list via `scripts/bib_check.py --format=docx`.

Announce in chat:
```
bibliography.docx → bibliography/bibliography.docx ✓
```

## 5. Update Task File

Call `workflow/05-task.md#update-step`: `Sync current files` → `done`.

## 6. Final Confirmation

Output a single summary line in chat:

```
Chiusura completata.
- articles/current.md          ✓
- articles/current.docx        ✓ (or ⚠ pandoc missing)
- bibliography/bibliography.docx ✓ (or ⚠ see above)
- Decision log: session-NNN    ✓
- Task file: <TASK_FILE_PATH>  ✓
```

The revision session is now fully closed.
