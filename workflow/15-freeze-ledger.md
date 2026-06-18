# 15 — Freeze Ledger

Persistent, article-level map of what is **concluded** (frozen) and what still
**needs work** (open), plus the comments/intentions gathered while iterating.
It is the single artifact that always answers: *which parts are done and good,
which parts still require intervention, and what we intend to change about them.*

Unlike the per-session task file (`05-task.md`) and the per-reviewer revision
plan, the freeze ledger is **per article** and **carries across version bumps
and sessions**.

**File:** `revisions/<article-slug>/freeze-ledger.md` (one per article).
**Template:** `templates/freeze-ledger.md`.

## When to invoke

| Action | Called by |
|---|---|
| `ensure` | `workflow/10-setup.md` — after the mandatory bump; create if missing, else load and reconcile to the bumped version |
| `check` | `30-iterate-points.md`, `31-paragraph-by-paragraph.md`, `33`, `34`, `36` — **before** proposing on a unit |
| `freeze` | `/r-freeze`, or the auto-offer when a unit's work concludes |
| `thaw` | `/r-thaw` |
| `status` | `/r-status` |
| `log-comment` | whenever the user states an intention to change a part but the change is not applied this turn |
| `carry-forward` | `60-bump-version.md` — re-anchor and copy the ledger into the new version |

## 1. Unit model & anchoring

A **unit** is the smallest reviewable block the user freezes — normally a
paragraph, but it may be a numbered subsection or a fragment.

Identify every unit by, in order:

1. `§<section>` — nearest heading.
2. `P<n>` — paragraph index within the article (same numbering as `/r-pp`).
3. **Anchor incipit** — the first ~40 verbatim characters of the paragraph.

Never key a unit by raw line number alone: line numbers shift on every edit and
bump. The anchor incipit is what makes a frozen unit recognisable after the text
moves. Record the line range too, but treat it as advisory.

If an anchor no longer matches any paragraph (the incipit was edited away),
mark that ledger row `⚠ stale` and ask the user to re-point it; never silently
drop a frozen unit.

## 2. States

- 🟢 `frozen` — concluded and approved. **Advisory**: the skill may still
  propose changes, but it must warn and ask before applying (see §5).
- 🟡 `open` — needs intervention. The *Commenti / intenzioni* cell says what we
  intend to change.
- 🔵 `wip` — being worked on in the current session.
- ⚪ untracked — a unit absent from the ledger has never been examined.

## 3. ensure (called by setup)

1. Compute `<article-slug>` (article filename prefix before `-vN`).
2. If `revisions/<article-slug>/freeze-ledger.md` does not exist, create it from
   `templates/freeze-ledger.md`, filling `{{ARTICLE_PATH}}`, `{{ARTICLE_SLUG}}`,
   `{{BUMPED_VERSION}}`, `{{TIMESTAMP}}`. Leave the tables empty.
3. If it exists, read it and update the frontmatter `reconciled-version` and
   `updated` fields to the current bumped version/timestamp. Do not rewrite the
   rows here — reconciliation of anchors happens lazily in `check` and fully in
   `carry-forward`.
4. Store `FREEZE_LEDGER_PATH` in working memory.
5. Confirm in chat (one line):
   ```
   Freeze ledger: revisions/<article-slug>/freeze-ledger.md (🟢 X frozen · 🟡 Y open)
   ```

## 4. check (called before every proposal)

Before generating a proposal for unit U:

1. Read the ledger row whose anchor matches U.
2. Branch on state:
   - 🟢 `frozen` → apply the **advisory warning** flow (§5).
   - 🟡 `open` → proceed normally; if the row carries an intention, fold it into
     the diagnosis so the proposal addresses it.
   - 🔵 `wip` / untracked → proceed normally; mark `wip` while working.

This check is mandatory in every interactive revision workflow. Skipping it for
a frozen unit defeats the purpose of freezing.

## 5. Advisory warning flow (frozen unit)

When a proposal would touch a 🟢 `frozen` unit, prepend the proposal block with:

```
⚠ Questa parte è CONGELATA (frozen il <data>, motivo: <motivo se presente>).
Era considerata conclusa. Vuoi davvero rivederla?
```

Then show the normal proposal block, but the closing line becomes:

```
**Decisione sulla proposta?** — procedere su una parte congelata richiede conferma esplicita.
Rispondi "sì, procedi" per attivare il ciclo decisionale, oppure "lascia congelato".
```

- If the user confirms (`sì, procedi`) → set the unit to 🔵 `wip` and run the
  normal decision loop. On the first applied change, log a `thaw` in the storico
  (frozen → wip) so the history is honest.
- If the user declines (`lascia congelato`) → skip the unit, leave it 🟢, and
  advance.

Never apply an edit to a frozen unit without an explicit confirmation in the
same turn.

## 6. freeze

Triggered by `/r-freeze [unit]` or accepted from the auto-offer (§7).

1. Resolve the target unit(s). `/r-freeze` with no argument targets the unit
   just worked on; `/r-freeze P4` or `/r-freeze §3` targets explicitly;
   `/r-freeze §3 tutto` freezes every paragraph in a section.
2. Set state 🟢 `frozen`, update *Ultima modifica*, clear the *Commenti /
   intenzioni* cell (or move any leftover intention to the storico as resolved).
3. Append a storico row: `<data> | freeze | <unit> | <prev> → frozen | <origin>`.
4. Confirm in chat (one line): `🟢 Congelato <unit> (<sezione>).`

## 7. Auto-offer on conclusion

When a unit's interactive work concludes — all its modifications decided **and**
the user signals no further changes on it (e.g. "no, prossimo paragrafo",
"next") — offer to freeze it **before** advancing:

```
Lavoro su <unit> (<sezione>) concluso: <X> accettate, <Y> tenute in considerazione.
Congelo questa parte come conclusa? (sì / no / più tardi)
```

- `sì` → run `freeze` (§6), origin `auto-offer fine lavoro`, then advance.
- `no` → leave the unit 🟡 `open`; if the user named anything still to do, run
  `log-comment` (§9) before advancing.
- `più tardi` → leave the unit 🔵 `wip`; advance without changing state.

The auto-offer fires **once per unit per session**. Do not nag.

## 8. thaw

Triggered by `/r-thaw [unit]`.

1. Resolve the target unit(s) (same rules as freeze).
2. Set state 🟡 `open` (or 🔵 `wip` if the user is about to work on it now).
3. Append a storico row: `<data> | thaw | <unit> | frozen → <new> | richiesta utente`.
4. Confirm: `🟡 Scongelato <unit> — ora modificabile senza avviso.`

## 9. log-comment (keep intentions on hand)

Whenever the user voices an intention to change a part but the change is **not**
applied this turn (deferred, blocked on data, "let's do this later"), record it
so it is never lost:

1. Ensure the unit has a 🟡 `open` row (create it if untracked).
2. Append the intention to the *Commenti / intenzioni* cell (concise) and, if
   articulated, add a detail block under `## Note per unità aperte` with:
   - **Intenzione** — what to change.
   - **Origine** — session/date and the point or reviewer that raised it.
   - **Bloccato da** — dependency, if any (e.g. `51-data-verification.md`).
3. Confirm: `📝 Annotato su <unit>: <short intention>.`

This is the mechanism that satisfies *"tenere traccia dei commenti
nell'iterazione delle cose che si intende cambiare"*: every deferred intention
lands in the ledger, not only in chat.

## 10. status (`/r-status`)

Print a compact snapshot from the ledger — do not edit anything:

```
## Stato revisione — <article-slug>  (reconciled <bumped-version>)

🟢 Frozen (X):   P4 §3, P9 §4, …
🟡 Open (Y):     P5 §3 — ricalcolare %; P7 §3 — citazione mancante; …
🔵 WIP (Z):      P12 §5
⚪ Untracked:    ~N paragrafi mai esaminati

Prossimo intervento suggerito: <first open unit + its intention>
```

If `ARTICLE_LANG=en`, render the labels in English (Frozen / Open / WIP /
Untracked).

## 11. carry-forward (called on bump)

When `60-bump-version.md` creates v(N+1):

1. Copy the ledger forward (the file path is stable; only frontmatter changes).
2. Re-anchor every row against the new version's text by matching the anchor
   incipit. Update the advisory line range.
3. Any row whose anchor no longer matches → mark `⚠ stale`, list those in chat,
   and ask the user to re-point or drop them. Never lose a frozen unit silently.
4. Update frontmatter `reconciled-version` and `updated`.

## 12. Relationship to other artifacts

- **Task file (`05-task.md`)** — per session, ephemeral step tracker. The ledger
  is per article, persistent. They are complementary; do not merge them.
- **Revision plan (`20-plan-revision.md`)** — per reviewer round, point-level
  decisions. A frozen unit can still receive a new reviewer point later; the
  advisory flow (§5) governs whether it gets touched.
- **Decision log (`95-decision-log.md`)** — at round close, include the frozen /
  open counts in the session `## Note`, and list units frozen this round.
