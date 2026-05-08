# 40 — Bibliography check

Triggered when:

- a revision point introduces, replaces or removes a citation;
- the reviewer flags a specific reference;
- the user runs an explicit bibliography audit before submission.

## 1. Identify the keys to verify

If the trigger is a single point: just the keys involved. If it is a full audit: all entries in `BIBLIOGRAPHY_BIB_PATH`, but **incrementally** (use the cache in `.cache/bib-verify/`).

## 2. Run static check

```
scripts/bib_check.py <article> <bib>
```

Report any:

- pandoc keys cited but absent in `.bib` → block: must be fixed before continuing;
- bib entries with missing required fields → flag, ask user to enrich;
- bib entries never cited → informational only.

## 3. Run online verification (if requested or if score-flag)

```
scripts/bib_verify_online.py <bib> --keys <comma-separated> --threshold 0.6 --output revisioni/audit-bibliografia-vN.md
```

The script writes a markdown audit listing the entries with similarity score below threshold, including the best Crossref / OpenAlex match for each. Open the audit file and present the flagged entries in chat using the same `Originale / Proposta / Decisione` shape:

```
## Voce sospetta — <bib_key>

**Metadata `.bib` attuale**
> <author> — *<title>* (<year>) — <publisher/journal>

**Probabile riferimento corretto** (Crossref/OpenAlex, similarity X.YZ)
> <matched-author> — *<matched-title>* (<matched-year>) — <DOI>

**Decisione?** Accetta correzione / Rifiuta / Modifica metadata / Mantieni inalterato (con commento)
```

If the user accepts, modify `.bib` (with `praxis-bibliography-citations` if available, or a direct Edit) and any inline occurrences in the article. Suggested commit message (the user decides whether to commit):

```
revision(<slug>): bib check — <bib_key> corrected
```

## 4. Legacy compatibility

If a flagged key is referenced elsewhere in the project (other articles, drafts), do not delete the key. Either:

- update the metadata in place (key remains, content corrected, even if the key name no longer matches);
- or add a comment in the `.bib` documenting the remap;
- or rename + add a stub entry — only if the user explicitly authorizes a wider refactor.

The default is conservative: **fix metadata, keep the key**, document the remap with a `% Nota:` comment in the `.bib`.

## 5. Wrap

After all flagged entries are decided, update the audit file with the final decisions. Suggested commit message:

```
revision(<slug>): bib audit — N entries reviewed
```

Return to the calling workflow (`30-iterate-points.md` if it triggered the check, or `70-final-sheet.md` otherwise).
