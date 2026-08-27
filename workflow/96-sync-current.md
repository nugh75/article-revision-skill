# 96 — Sync Derived Exports

Mandatory post-decision-log step. The active article is already the authoritative
Markdown source: it is the canonical `article-vN-…md` file with the highest
numeric `N` in `articles/versions/`. This step creates only derived exports; it
never creates or updates an `articles/current.md` copy.

Run after both closure and explicit handoff, including rounds with no accepted
text edits. In `auto-closure`, missing, empty, or unverifiable DOCX output is
fatal and returns `FAIL`.

## Outputs

| File | Content |
|---|---|
| `articles/current.docx` | Word export generated directly from the active article |
| `bibliography/bibliography.docx` | Formatted references from `reference.bib` |
| `bibliography/bibliography.md` and `.csv` | Project lists, outside strict auto-closure |

`current.docx` is a disposable export and always lives in `articles/`, never in
`articles/versions/`.

## 1. Identify sources

Load from working memory:

- `ARTICLE_PATH` — canonical path of the active article version;
- `BIBLIOGRAPHY_BIB_PATH` — configured bibliography source;
- `PYTHON_BIN` — project Python interpreter.

Before exporting, require that `ARTICLE_PATH` exists and still resolves to the
highest numeric version. A stale or frozen source returns `FAIL`.

## 2. Generate exports

Run:

```bash
SYNC_MODE="$SYNC_MODE" bash scripts/sync_current.sh "$ARTICLE_PATH" "$BIBLIOGRAPHY_BIB_PATH"
```

The script passes `ARTICLE_PATH` directly to Pandoc. If
`editorial-norms/reference.docx` or a CSL file exists, it applies them.

Interactive `closure` and `handoff` may warn and continue when Pandoc is absent.
`auto-closure` must fail with `pandoc missing`.

For `bibliography.docx`, require rendered body text beyond its heading. In
`auto-closure`, also require non-empty extracted body text from
`articles/current.docx`. Never report an export as synchronized when its check
failed.

## 3. Update the task

- `closure`: set `Sync derived exports` to `done`.
- `handoff`: set `Handoff checkpoint` to `paused` with note
  `decision log + derived exports synchronized`; keep the final
  `Sync derived exports` row open.
- `auto-closure`: return the structured result to `95-decision-log.md`; that
  workflow owns final task status.

## 4. Report

For `closure`:

```text
Chiusura completata.
- active article source             ✓ <ARTICLE_PATH>
- articles/current.docx             ✓ (or ⚠ pandoc missing)
- bibliography/bibliography.docx    ✓ (or ⚠ see above)
- Decision log: session-NNN         ✓
- Task file: <TASK_FILE_PATH>       ✓
```

For `handoff`, use `Handoff sincronizzato`, report the same source and exports,
and mark the task `paused`.

For `auto-closure`, print no completion message. Return:

```text
AUTO_SYNC_RESULT: PASS|FAIL
active_article: PASS|FAIL
current_docx_text: PASS|FAIL
bibliography_docx_text: PASS|FAIL
```
