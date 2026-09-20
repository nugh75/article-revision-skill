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
| `ensure` | `workflow/10-setup.md` — after the first-edit working version is created; create if missing, else load and reconcile |
| `check` | `30-iterate-points.md`, `31-paragraph-by-paragraph.md`, `33`, `34`, `36` — **before** proposing on a unit |
| `freeze` | `/r-freeze`, or the auto-offer when a unit's work concludes |
| `thaw` | `/r-thaw` |
| `status` | `/r-status` |
| `log-comment` | after a tracked round exists, or when the user explicitly asks to save an intention |
| `carry-forward` | `60-bump-version.md` — re-anchor and copy the ledger into the new version |
| `verify` | after every applied edit, on `/r-status`, and on bump — run `scripts/freeze_check.py` (§14) |

## 1. Unit model & anchoring

The ledger tracks two tiers, and a unit belongs to exactly one of them:

| Tier | Key | Anchor | Force |
|---|---|---|---|
| section | `§2.2`, `Parte III`, `P4` | incipit, ~40 chars | **advisory** — warn and ask (§5) |
| passage | `F<n>` | full verbatim text + sha256 | **binding** — no edit without `/r-thaw` (§13) |

The section tier is the coarse map of what is concluded. The passage tier locks
a single span of continuous text — half a sentence, one sentence, three — that
must not change at all. A passage wins over the section that contains it: a 🔒
passage inside a 🟡 `open` section stays untouchable and the section's revision
routes around it; inside a 🟢 `frozen` section it is the core that survives even
when the user reopens the section.

A **section-tier unit** is the smallest reviewable block the user freezes at that
tier — normally a paragraph, but it may be a numbered subsection or a fragment.

Identify every unit by, in order:

1. `Capitolo <C> — <title>` — chapter from the first numeric component of the
   numbered heading.
2. `§<section>` — nearest full heading path, if any.
3. `P<n>` — paragraph index within the article (same numbering as `/r-pp`).
4. `<ARTICLE_PATH>:<L1-L2>` — current advisory line range.
5. **Anchor incipit** — the first ~40 verbatim characters of the paragraph.

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
- 🔒 `frozen` — a **passage** (§13), binding. Only `/r-thaw F<n>` releases it.
  Thawing sets the passage to 🟡 `open`; passages never take 🟢 or 🔵.

## 3. ensure (called by setup)

1. Compute `<article-slug>` (article filename prefix before `-vN`).
2. If `revisions/<article-slug>/freeze-ledger.md` does not exist, create it from
   `templates/freeze-ledger.md`, filling `{{ARTICLE_PATH}}`, `{{ARTICLE_SLUG}}`,
   `{{BUMPED_VERSION}}`, `{{TIMESTAMP}}`. Leave the tables empty.
3. If it exists, read it and update the `article` pointer to the active version.
   Advance `reconciled-version` only after checking all row anchors against that
   version; it must not imply that unchecked rows were reconciled. On integrated
   projects the coordinator performs that check and marks missing or ambiguous
   matches `⚠ stale`, preserving every state, note and approval decision.
4. Store `FREEZE_LEDGER_PATH` in working memory.
5. Confirm in chat (one line):
   ```
   Freeze ledger: revisions/<article-slug>/freeze-ledger.md (🟢 X frozen · 🟡 Y open)
   ```

## 4. check (called before every proposal)

Before generating a proposal for unit U:

0. Read the *Passaggi congelati* table (§13). If any 🔒 passage falls inside U,
   the proposal must leave that text byte-identical; say so explicitly in the
   diagnosis and shape the proposal around it. A proposal that would rewrite a
   🔒 passage is not offered at all — offer `/r-thaw F<n>` instead.
1. Read the ledger row whose anchor matches U.
2. Branch on state:
   - 🟢 `frozen` → apply the **advisory warning** flow (§5).
   - 🟡 `open` → proceed normally; if the row carries an intention, fold it into
     the diagnosis so the proposal addresses it.
   - 🔵 `wip` / untracked → proceed normally. Mark `wip` only when a tracked
     edit round exists; a diagnostic check is read-only.

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

- If the user confirms (`sì, procedi`) → run the normal decision loop. During a
  diagnostic-only phase, retain that confirmation in working memory and leave
  the ledger unchanged. Immediately before the first accepted file edit starts
  the tracked round, set the unit to 🔵 `wip` and log a `thaw` in the storico
  (frozen → wip) so the history is honest.
- If the user declines (`lascia congelato`) → skip the unit, leave it 🟢, and
  advance.

Never apply an edit to a frozen unit without an explicit confirmation in the
same turn.

## 6. freeze

Triggered by `/r-freeze [unit]` or accepted from the auto-offer (§7).

1. Resolve the target unit(s). `/r-freeze` with no argument targets the unit
   just worked on; `/r-freeze P4` or `/r-freeze §3` targets explicitly;
   `/r-freeze §3 tutto` freezes every paragraph in a section. A **quoted
   argument** — `/r-freeze "la fiducia precede l'affidamento"` — freezes a
   passage instead; follow §13.3.
2. Set state 🟢 `frozen`, update *Ultima modifica*, clear the *Commenti /
   intenzioni* cell (or move any leftover intention to the storico as resolved).
3. Append a storico row: `<data> | freeze | <unit> | <prev> → frozen | <origin>`.
4. Confirm in chat (one line): `🟢 Congelato <unit> (Capitolo <C>, righe <L1-L2>).`

## 7. Auto-offer on conclusion

After a tracked edit round exists, when a unit's interactive work concludes —
all its modifications decided **and** the user signals no further changes on it
(e.g. "no, prossimo paragrafo", "next") — offer to freeze it **before**
advancing. Do not run the auto-offer for a diagnostic-only unit.

```
Lavoro su <unit> (Capitolo <C>, righe <L1-L2>) concluso: <X> accettate, <Y> tenute in considerazione.
Congelo questa parte come conclusa? (sì / no / più tardi)
```

- `sì` → run `freeze` (§6), origin `auto-offer fine lavoro`, then advance.
- `no` → leave the unit 🟡 `open`; if the user named anything still to do, run
  `log-comment` (§9) before advancing.
- `più tardi` → leave the unit 🔵 `wip`; advance without changing state.

The auto-offer fires **once per unit per session**. Do not nag.

## 8. thaw

Triggered by `/r-thaw [unit]`.

1. Resolve the target unit(s) (same rules as freeze). `/r-thaw F7` thaws a
   passage: follow §13.5 instead of the steps below.
2. Set state 🟡 `open` (or 🔵 `wip` if the user is about to work on it now).
3. Append a storico row: `<data> | thaw | <unit> | frozen → <new> | richiesta utente`.
4. Confirm: `🟡 Scongelato <unit> — ora modificabile senza avviso.`

## 9. log-comment (keep intentions on hand)

When a tracked round exists, or when the user explicitly asks to save a note,
an intention that is **not** applied this turn (deferred, blocked on data,
"let's do this later") may be recorded so it is not lost. Otherwise keep it in
the read-only chat audit and do not create or update the ledger.

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

Run `verify` (§14) first and report its result; `/r-status` is the routine
occasion on which passage drift surfaces.

For projects with `TASKS.md`, also read the live pending-work report using
`workflow/08-revision-archive.md` (`status`, not `refresh`).

```
## Stato revisione — <article-slug>  (reconciled <bumped-version>)

🟢 Frozen (X):   P4 Capitolo 3 <ARTICLE_PATH>:145-153; P9 Capitolo 4 <ARTICLE_PATH>:210-218; …
🟡 Open (Y):     P5 Capitolo 3 <ARTICLE_PATH>:154-162 — ricalcolare %; P7 Capitolo 3 <ARTICLE_PATH>:180-188 — citazione mancante; …
🔵 WIP (Z):      P12 Capitolo 5 <ARTICLE_PATH>:260-268
🔒 Passaggi (W): W verificati · S stale · A ambigui
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
4. Re-run `verify` (§14) against the new version. A passage reported `stale`
   after a bump means the bump itself altered locked text: stop and report it
   before anything else.
5. Update frontmatter `reconciled-version` and `updated`.

## 12. Relationship to other artifacts

- **Task file (`05-task.md`)** — per session, ephemeral step tracker. The ledger
  is per article, persistent. They are complementary; do not merge them.
- **Revision plan (`20-plan-revision.md`)** — per reviewer round, point-level
  decisions. A frozen unit can still receive a new reviewer point later; the
  advisory flow (§5) governs whether it gets touched.
- **Decision log (`95-decision-log.md`)** — at round close, include the frozen /
  open counts in the session `## Note`, and list units frozen this round.

## 13. Passages (fine grain)

### 13.1 Format

The ledger's `## Passaggi congelati` section holds two coupled artifacts per
passage. The table carries state and metadata; the block below carries the
**verbatim text**, byte for byte, inside a `text` fence:

````
| ID | Sezione | Righe | Incipit | sha256 | Stato | Data |
|---|---|---|---|---|---|---|
| F7 | §2.2.4 | <ARTICLE_PATH>:224-224 | «La teoria della diffusione…» | a91f3c7d4e21 | 🔒 frozen | 2026-09-20 |

### F7 — §2.2.4 — 🔒 frozen — 2026-09-20
- **Motivo:** dato verificato con l'autore; formulazione concordata.

```text
La teoria della diffusione delle innovazioni colloca l'adozione su cinque categorie.
```
````

Neither half stands alone: a table row without its block, or a block without its
row, is an error that `verify` (§14) reports. Do not paraphrase or re-indent the
fenced text, and never add ellipses to it — it is the comparison key.

`Righe` and `Incipit` are conveniences for reading; the fenced text and its
digest are the anchor.

### 13.2 Anchoring and normalisation

Comparison is normalised: Unicode NFC, every run of whitespace (newlines
included) collapsed to a single space, ends trimmed. The digest is the first 12
hex characters of the sha256 of that normalised text.

Consequences, and they are the point of the design:

- A passage survives re-wrapped lines, re-indentation and a version bump.
- It survives moving to another chapter — the passage is found wherever it is.
- It becomes `stale` exactly when the words change. That is the signal wanted.
- Markdown inside the span (`*corsivo*`, `[@rossi2024]`) is part of the text:
  changing the markup counts as changing the passage.

### 13.3 freeze a passage

Triggered by `/r-freeze "<testo esatto>"`, or by the user pointing at a span in
chat and asking to lock it.

1. Take the span exactly as it appears in the article. Do not trim it to a
   sentence boundary if the user marked less, and do not extend it silently.
2. Normalise (§13.2) and count occurrences in the active article:
   - **0** → the quoted text does not exist. Report it and stop; do not guess a
     near match.
   - **>1** → refuse and ask the user to extend the span until it is unique:
     `⚠ «<incipit>» compare N volte. Allarga il passaggio per renderlo univoco.`
   - **1** → proceed.
3. Allocate the next free `F<n>`, compute the digest, add the table row with
   state 🔒 `frozen` and add the verbatim block with the user's `Motivo` when
   given.
4. Append a storico row:
   `<data> | freeze-passaggio | F<n> <sezione> | — → 🔒 frozen | <origine>`.
5. Run `verify` (§14) and confirm in one line:
   `🔒 Congelato F<n> (§<sezione>, riga <L>): «<incipit>…»`

Freezing a passage does not change the state of the section containing it.

### 13.4 check a passage (precedence)

Passages are read **before** the section row, in §4 step 0. When a proposal's
range contains a 🔒 passage:

- Leave the passage byte-identical and say so in the diagnosis:
  `F7 è congelato: la proposta lo aggira.`
- If the editorial problem lies *inside* the passage, do not propose a rewrite.
  Report the conflict and offer the choice:
  `Il rilievo cade dentro F7, congelato il <data> (<motivo>). Per intervenire serve /r-thaw F7.`
- Never apply an edit that alters a 🔒 passage, with or without confirmation in
  the same turn. `/r-thaw` is the only door. This is where the passage tier
  differs from the advisory section tier.

### 13.5 thaw a passage

Triggered by `/r-thaw F<n>`.

1. Set the row state to 🟡 `open`, keep the row and the verbatim block — the
   text stays on record as what the passage used to say.
2. Append a storico row:
   `<data> | thaw-passaggio | F<n> | 🔒 frozen → 🟡 open | richiesta utente`.
3. Confirm: `🟡 Scongelato F<n> — ora modificabile.`

A 🟡 passage is no longer enforced by `verify`; it is reported as
`non verificato`. Drop the row entirely only when the user asks.

### 13.6 carry-forward across bumps

Passages need no re-anchoring: the digest and the text travel with the ledger and
the search runs against whatever version is active. On bump, run `verify` (§14)
and report any `stale` before anything else — a passage that went stale during a
bump means the bump altered locked text.

## 14. verify (`scripts/freeze_check.py`)

Deterministic gate. Model discipline decides what to propose; this script decides
whether locked text actually survived.

```
python3 scripts/freeze_check.py <ARTICLE_PATH> [--ledger <freeze-ledger.md>]
```

Without `--ledger` it resolves `revisions/*/freeze-ledger.md` from the working
directory and refuses to guess when that glob is not unique.

One line per passage, then a summary:

```
F3 §1.1 riga 41 — ok
F7 §2.2.4 — ⚠ stale (testo non trovato)
F9 §2.6 — ⚠ ambiguo (2 occorrenze: righe 488, 502)
2 passaggi 🔒 verificati · 2 da sanare
```

Exit `0` when every 🔒 passage is present exactly once; exit `1` on any `stale`,
`ambiguo`, `hash incoerente`, `blocco mancante` or `riga di tabella mancante`.

Run it:

- **after every applied edit round** that wrote to the article, before declaring
  the round closed. Exit 1 means the edit violated a lock: restore the exact text
  and report which passage, do not renegotiate it after the fact.
- on `/r-status` (§10).
- on bump, after carry-forward (§11, §13.6).

A non-zero exit is never reported as a pass, and it is never silenced by editing
the ledger to match the article. The article gets restored; the ledger changes
only through `/r-thaw`.
