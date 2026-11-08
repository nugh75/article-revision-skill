# 39 — Part Revision As A Markdown File

Triggered by `/r-parte [<§N | titolo | P<x>-P<y>>]`, by the `--md` flag on a
diagnostic or revision command, or by phrases like *"revisione del capitolo 3 su
file"*, *"scrivimi la revisione della parte in markdown"*.

The mode produces one Markdown file per part of the manuscript. The file holds
the complete revised text of that part followed by its modification and decision
record, so the part can be read, corrected, or circulated outside chat and later
reintegrated into the manuscript.

Two distinct operations, never merged:

| Operation | Command | Persistent effects |
|---|---|---|
| Produce the part file | `/r-parte <scope>`, or `<command> --md` | Writes only the sidecar under `revisions/`, after confirmation |
| Reintegrate it | `/r-parte --apply <file>` | Tracked round: version, task, ledger, manuscript edit |

Producing the file never edits the manuscript, never bumps, never creates a task,
never updates the ledger, and never syncs exports. Reintegration replaces a whole
part and recomputes paragraph locators, so it always runs as `tracked-round` —
never `direct-apply`, never `auto`. Git stays separately authorized in both
operations.

---

## A. Produce the part file

### A1. Setup

Run `00-bootstrap.md` only if infrastructure is missing and its creation was
separately approved, then `10-setup.md` read-only. Record `ARTICLE_PATH`,
`ARTICLE_VERSION`, `ARTICLE_LANG`, `EDITORIAL_LIMIT_CHARS`, and the freeze
snapshot. Do not select a write transition here.

### A2. Select the part

Accept from the command: `Capitolo N`, `§N`, a heading text substring, or a
paragraph range `P<x>-P<y>`. If nothing is given, list the candidate parts with
line ranges and char shares as in `36-chapter-revision.md` §2, then ask:

> Quale parte devo revisionare su file? (Capitolo N, §N, titolo, o intervallo P12-P18)

Wait for the answer.

A part is contiguous. A non-contiguous selection is refused: ask the user to
choose one part or to run the command once per part.

### A3. Anchor the part

1. Read the full manuscript (skip YAML frontmatter).
2. Build the paragraph locator list for the part:
   `Capitolo <C> — <chapter-title>; Paragrafo P<N> — <ARTICLE_PATH>:<L1-L2>`.
3. Record `LINE_RANGE`, `PART_CHARS`, `PARAGRAPH_RANGE` and the exact
   first and last lines for review. Select prose below any version banner
   or YAML metadata. Capture the SHA-256 of the whole source span with line\n   endings normalized to LF.

   ```bash
   "$PYTHON_BIN" "<skill-root>/scripts/part_source.py" capture "$ARTICLE_PATH" "$LINE_RANGE"
   ```

   Pass the inclusive range as `START:END` and save the result as
   `impronta_fonte`.
4. Check the freeze ledger for each paragraph. Keep every unchanged or frozen
   paragraph intact in `Testo revisionato`. Mark frozen paragraphs in `Note`.

### A4. Diagnose

Run the diagnosis the invoked route prescribes, read-only:

- `/r-parte` alone: the six dimensions of `36-chapter-revision.md` §4, reported
  in condensed form (one line per dimension unless a dimension has findings).
- `<command> --md`: the diagnosis of that command —
  `12-audit.md`, `31-paragraph-by-paragraph.md`, `33-connector-revision.md`,
  `34-global-revision.md`, `36-chapter-revision.md`, `38-redundancy-audit.md`,
  or `13-content-structure.md`.

Show the diagnosis in chat before writing anything. A claim about the Italian
itself goes through the `treccani` skill on the isolated construction, as
`SKILL.md` requires; an unverified claim is worded as a stylistic preference and
marked as such in `TRECCANI_NOTES`.

### A5. Draft the revised part

Apply the preservation rules in `SKILL.md` § "Preservation and verification" to
the whole part: claims, evidence, citations, causal strength, examples, headings,
and section order are preserved unless the user explicitly approves changing
them. Numeric claims run through `51-data-verification.md`; touched citations run
through `40-bibliography-check.md`.

Splits, merges, cuts, moves, and paragraph reordering inside the part are
structural: inventory the affected units per `13-content-structure.md` and keep
each one as a separate numbered decision in the file, defaulting to `pending`.
The part file may propose them; only reintegration can apply them.

### A6. Confirm and write

Show in chat:

```
Parte: <PART_TITLE>  (<ARTICLE_PATH>:<LINE_RANGE>, <PART_CHARS> chars, <PARAGRAPH_RANGE>)
Modifiche proposte: <N>  ·  rischio max: <low|medium|high>
Δ parte: chars <±N> / words <±N>  (limite articolo: <EDITORIAL_LIMIT_CHARS>)
File: revisions/<article-slug>/parti/<part-slug>-<ARTICLE_VERSION>-YYYY-MM-DD-HHMM.md

Scrivo il file? (sì / mostra prima in chat / annulla)
```

Wait. On `sì`, create `revisions/<article-slug>/parti/` if missing and write the
file from `templates/part-revision.md` with `stato: proposto`. Nothing else is
written: no bump, no task, no ledger update, no sync, no Git.

Then report the path and:

> File scritto. Correggilo a mano se serve, poi `/r-parte --apply <file>` per reintegrarlo nell'articolo.

### A7. Update an existing part file

If a part file for the same part and source version already exists, ask whether
to overwrite it or to write a new timestamped file. Never overwrite a file whose
`stato` is `applicato`.

---

## B. Reintegrate the part file

Triggered by `/r-parte --apply <file>`. If no file is given, list the part files
under `revisions/<article-slug>/parti/` with `parte`, `versione`, and `stato`,
then ask which one.

### B1. Drift preflight

Stop if `stato` is `applicato`. Resolve the active article and read
`versione`, `righe` and `impronta_fonte`. For a legacy file without a
fingerprint, regenerate against the active version and carry its decisions
forward as notes for reconfirmation.

```bash
"$PYTHON_BIN" "<skill-root>/scripts/part_source.py" locate "$ARTICLE_PATH" "$LINE_RANGE" "$SOURCE_SHA256"
```

Proceed only with one exact span. Use the returned range when the part moved
and announce the new location. If the version changed, confirm use of the
identical span on the active version. If the span changed or is ambiguous,
show the drift and keep the proposal for review.

### B2. Freeze and decision check

1. Re-run the freeze check on every paragraph the part covers. A 🟢 `frozen`
   paragraph needs an explicit `sì, procedi`.
2. Read `Decisioni`. If all points are pending, present them for acceptance.
   Rebuild the candidate from the verified source span with the exact changes
   of accepted points. The full proposed text is for review. Preserve pending
   or rejected points and frozen paragraphs. Resolve overlapping or dependent
   points explicitly before applying an affected change.
3. For `rivisto-a-mano`, show the exact diff against the verified source and
   ask once to confirm those manual changes. Check the same freeze and
   preservation constraints.

### B3. Preservation verification

Before the edit, compare the original part with the text to be applied for
entities and numbers, polarity and negation, modality, causal strength, scope,
conditions, limitations, and citation function. Report every difference that is
not covered by an accepted decision and stop until the user resolves it.

Structural decisions accepted in the file complete the affected-unit map and
preservation manifest of `13-content-structure.md` before application; cuts,
merges, and new claims stay separately decidable.

### B4. Tracked application

On confirmation, run the candidate checks from `workflow/14-verify-edit.md`
before opening the round. Pass the full active article SHA-256 as
`ARTICLE_REVISION_EXPECTED_SOURCE_SHA256` to the first-edit bump.

1. Run `60-bump-version.md mode=first-edit` and announce the working path.
2. Locate the source span again in the working version using its recorded
   part fingerprint and verify the candidate at the returned range.
3. Create the tracked task and ensure the ledger is reconciled to the working
   version. Apply through `workflow/14-verify-edit.md`.
4. Recompute paragraph locators and check `EDITORIAL_LIMIT_CHARS`.
5. Set the part file to `stato: applicato` with the applied version, new range
   and resolved decisions only after verification succeeds.

If citations or numeric claims were touched, run `40-bibliography-check.md` and
`51-data-verification.md` before closure.

### B5. Closure

```
Reintegro completato.
Parte: <PART_TITLE>  |  Punti applicati: A  |  Esclusi: R
Versione articolo attiva: <path>:<new-line-range>
Bilancio caratteri: +Δ (limite: EDITORIAL_LIMIT_CHARS)

Procedo con la chiusura?
  1. Final sheet (/r-sheet)  — facoltativo
  2. Decision log            — obbligatorio
  3. Sync derived exports    — obbligatorio
(sì / sì senza final sheet / annulla)
```

On confirmation run `95-decision-log.md` with `type: revision-part` and
`96-sync-current.md`, then ask separately whether to publish a Git checkpoint via
`07-git-checkpoint.md`. Offer to freeze the reintegrated part
(`15-freeze-ledger.md` §7); never freeze it automatically.

---

## C. The `--md` flag

`--md` changes where a command's outcome lands, never what the command is allowed
to do. Appended to `/r-audit`, `/r-pp`, `/r-pp-a`, `/r-chapter`, `/r-conn`,
`/r-redundancy`, or `/r-structure`, it keeps that command's diagnosis and
decision loop and writes the result as a part file per §A6, one file per part
covered.

- A command whose scope spans several parts asks which part to write, or writes
  one file per part on `tutte`.
- A diagnostic command with no proposed text writes the file with an empty
  `Testo revisionato` and the diagnosis only; say so when reporting the path.
- `--md` does not authorize a manuscript edit, a bump, a task, a ledger update,
  a sync, or Git. Reintegration stays `/r-parte --apply`.
- `--md` is refused on `/r-auto`: automatic mode applies its own bounded edits
  and has its own reports (`37-scoped-auto-revision.md`).

## D. Edge cases

- **Part with no headings.** Use the paragraph range as `parte` and note that the
  locator is provisional.
- **Part longer than a chapter.** Warn about the char share and ask whether to
  split the file per section before writing.
- **Pause.** `pause`, `stop`, `sospendi`, `interrompi`, `/r-handoff` → call
  `06-handoff.md` recording the selected part, whether the file was written, its
  path, and the exact next action. A written part file is itself a resumable
  checkpoint; no closure, no sync.
- **File edited by hand.** Ask the user to set `stato: rivisto-a-mano` so §B2
  treats the text as approved wording. If `stato` is still `proposto` but the
  text no longer matches the recorded modifications, say so and ask which one
  governs.
- **Deleted source version.** Reintegration against a missing `fonte` stops with
  the drift message in §B1.
