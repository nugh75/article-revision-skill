# 40 — Bibliography Check

Triggered when:

- a revision point introduces, replaces, or removes a citation;
- the reviewer flags a specific reference;
- the user runs an explicit bibliography audit before submission.

## 1. Identify Keys To Verify

If the trigger is a single point, check only the keys involved. If it is a full audit, check all entries in `BIBLIOGRAPHY_BIB_PATH`, incrementally, using the cache in `.cache/bib-verify/`.

## 2. Run Static Check

```bash
scripts/bib_check.py <article> <bib>
```

Report any:

- cited keys absent from `.bib` → blocking, must be fixed before continuing;
- `.bib` entries with missing required fields → flag and ask user to enrich;
- `.bib` entries never cited → informational only.

## 3. Run Online Verification

Run this if requested or if a score-based flag is needed:

```bash
scripts/bib_verify_online.py <bib> --keys <comma-separated> --threshold 0.6 --output revisions/bibliography-audit-vN.md
```

The script writes a Markdown audit listing entries below the similarity threshold, including the best Crossref/OpenAlex match for each. Open the audit file and present flagged entries in chat using the same `Original / Proposal / Decision` shape:

```text
## Suspicious Entry — <bib_key>

**Current `.bib` metadata**
> <author> — *<title>* (<year>) — <publisher/journal>

**Likely correct reference** (Crossref/OpenAlex, similarity X.YZ)
> <matched-author> — *<matched-title>* (<matched-year>) — <DOI>

**Decision?** Accept correction / Reject / Modify metadata / Keep unchanged with comment
```

If the user accepts, modify `.bib` and any inline occurrences in the article. Suggested commit message, if the user asks:

```text
revision(<slug>): bib check — <bib_key> corrected
```

## 4. Legacy Compatibility

If a flagged key is referenced elsewhere in the project (other articles, drafts), do not delete the key. Either:

- update metadata in place (key remains, content corrected, even if the key name no longer matches);
- add a comment in `.bib` documenting the remap;
- rename and add a stub entry only if the user explicitly authorizes a wider refactor.

Default is conservative: **fix metadata, keep the key**, and document the remap with a `% Note:` comment in `.bib`.

## 5. Wrap

After all flagged entries are decided, update the audit file with final decisions. Suggested commit message:

```text
revision(<slug>): bib audit — N entries reviewed
```

Return to the calling workflow (`30-iterate-points.md` if it triggered the check, or `70-final-sheet.md` otherwise).
