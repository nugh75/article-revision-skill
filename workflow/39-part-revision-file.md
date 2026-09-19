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
3. Record `LINE_RANGE` (inclusive), `PART_CHARS`, `PARAGRAPH_RANGE`, and the
   verbatim first and last line of the part as `ANCHOR_FIRST_LINE` and
   `ANCHOR_LAST_LINE`. These anchors are what makes reintegration verifiable;
   never paraphrase them.
4. Run the freeze check (`15-freeze-ledger.md` §4) on every paragraph in the
   part. A 🟢 `frozen` paragraph requires the advisory flow (§5) before it is
   revised, even on file. If the user leaves it frozen, exclude it from the
   revised text and say so in the file's `Note`.

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

Read the file's frontmatter and compare it with the current manuscript:

1. `fonte` and `versione` against the active `ARTICLE_PATH` / `ARTICLE_VERSION`.
2. `ancora_inizio` and `ancora_fine` against the lines at `righe`. If they do not
   match there, search the manuscript for both anchors.

Outcomes:

- Anchors found at `righe` in the recorded version → proceed.
- Anchors found at a different line range, content unchanged → adopt the new
  range, announce it, and proceed.
- Recorded version is older than the active one but anchors and part content are
  unchanged → warn and ask for confirmation before proceeding.
- Anchors missing, or the part content changed since the file was written → stop:

  ```
  ⚠ Drift: la parte è cambiata dopo la scrittura di <file>.
  Atteso: <ancora_inizio> … <ancora_fine> in <fonte>:<righe> (<versione>)
  Trovato: <what is there now>
  Non reintegro. Vuoi rigenerare il file sulla versione attiva (/r-parte <scope>) o rivedere il diff?
  ```

  Never overwrite a drifted part.

`stato: applicato` stops reintegration: report that the file was already applied
and ask whether to regenerate it instead.

### B2. Freeze and decision check

1. Re-run the freeze check on every paragraph the part covers. A 🟢 `frozen`
   paragraph needs an explicit `sì, procedi`.
2. Read the `Decisioni` section. Only `accepted` points are applied.
   - Every point `pending` → present the list and ask which to accept
     (`tutti` / numbers / `annulla`).
   - Mixed states → apply the accepted ones; report which points are left out
     and keep the revised text consistent with that subset, regenerating the
     part text when a rejected point is entangled with an accepted one.
   - `stato: rivisto-a-mano` → the file's `Testo revisionato` is treated as the
     user's own approved wording. Still confirm once:
     > Il file è marcato `rivisto-a-mano`: applico il testo così com'è? (sì / annulla)

### B3. Preservation verification

Before the edit, compare the original part with the text to be applied for
entities and numbers, polarity and negation, modality, causal strength, scope,
conditions, limitations, and citation function. Report every difference that is
not covered by an accepted decision and stop until the user resolves it.

Structural decisions accepted in the file complete the affected-unit map and
preservation manifest of `13-content-structure.md` before application; cuts,
merges, and new claims stay separately decidable.

### B4. Tracked application

On confirmation, run the tracked first-edit transition from `10-setup.md`:

1. `60-bump-version.md mode=first-edit`, and announce the new path.
2. `05-task.md action=create` with `COMMAND=/r-parte --apply`.
3. `15-freeze-ledger.md action=ensure`, reconciled to the new version.
4. Replace `righe` in the new version with the applied part text.
5. Verify the result, recompute the paragraph locators of the part and of every
   paragraph after it, and report the new ranges.
6. Check the article total against `EDITORIAL_LIMIT_CHARS` and warn if over.
7. Rewrite the part file: `stato: applicato`, applied version and new line range
   in the frontmatter, decisions resolved.

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
