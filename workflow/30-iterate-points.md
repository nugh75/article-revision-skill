# 30 — Iterate Points

Core loop. Apply to a single point, a paragraph, or the whole article; the user picks the scope.

## 0. Determine Scope

If the user's instruction mentions a specific scope, use it:

- *"fix this sentence"* → **fragment**
- *"revise this paragraph"* / reviewer point → **paragraph**
- *"revise the whole article"* → **whole article** (sequential walk)

If unspecified, default to **paragraph** when processing a reviewer point, **fragment** otherwise. Always confirm in the proposal block which scope is being used.

## 1. Load Context

Read the relevant section(s) of the article. Identify the exact lines that the change touches:

- **fragment**: the single sentence or inline element (citation, formatting, term);
- **paragraph**: the smallest coherent block (one paragraph or one numbered subsection);
- **whole article**: walk every section, generating proposals one at a time. Never produce a single mass-replacement.

If the change involves a citation, run `40-bibliography-check.md` for the relevant key first.

If the change requires sample-description data, run `50-sample-description.md` first.

If the original or proposed text contains a numeric claim — a percentage, count, mean, index, correlation, rank, or a qualitative claim that holds only if a figure holds — run `51-data-verification.md` **before** generating the proposal. Never inherit the figure from the previous version or from the reviewer's wording. This is binding, not optional.

Run the freeze check (`15-freeze-ledger.md` §4) on the target unit **before**
generating the proposal:

- 🟢 `frozen` → apply the advisory warning flow (`15-freeze-ledger.md` §5):
  prepend `⚠ Questa parte è CONGELATA …`, and require an explicit `sì, procedi`
	  before running the decision loop. If the user declines, skip the unit and advance.
- 🟡 `open` → if the row carries an intention, fold it into the diagnosis so the
  proposal addresses what was already noted.
- 🔵 `wip` / untracked → proceed; mark the unit `wip` while working.

## 2. Generate Proposal

Apply:

- editorial norms loaded in setup;
- journal-specific style skill, if available;
- `templates/accepted-anglicisms-it.md` if `ARTICLE_LANG=it`;
- minimum surgical change: alter only what the point requires.

Never collapse multiple separate concerns into a single proposal. If the same paragraph needs both citation correction and phrasing change, present two consecutive proposals, each with its own decision.

If a single proposal still contains **more than one numbered modification**
(for example, several refusi in the same paragraph or multiple tightly related
surface edits), write a sidecar proposal file before presenting it in chat:

`revisions/<reviewer>/proposal-revision-YYYY-MM-DD-HHMM.md`

Use `templates/proposal-revision.md`. The file must mirror the exact chat
proposal and act as the persisted proposal to follow during the decision loop.
Each subsequent `Accetta` / `Modifica` / `Rivedi completamente` /
`Tieni in considerazione` updates the same file's
`Decision Trail` and status.

## 3. Present In Chat

```text
## Point N — <short title> · scope: <fragment|paragraph|whole article>

**Original** (`<article>:<line-range>`)
> <verbatim text>

**Proposta**
> <proposed full text>

**Modifiche:**
1. `<old>` → `<new>` [(motivazione)]
2. `<old>` → `<new>` [(motivazione)]
...

**Δ**: chars <signed> / words <signed> · risk: <low|medium|high>

**Norms respected**: <list>
**Possible exceptions**: <list, with reason>

**Decisione sulla proposta?**
- `Accetta` — applica la proposta così com'è.
- `Modifica <N>: <direzione>` — mantieni l'idea, ma cambia la modifica indicata.
- `Rivedi completamente: <direzione>` — rigenera la proposta da capo.
- `Tieni in considerazione: <nota>` — non applicare ora; registra come promemoria/traccia.

Puoi indicare numeri specifici, es. `Accetta 2,4` oppure `Modifica 3: sostituire X con Y`.
```

Wait for the user. Do **not** apply pre-emptively.

Each modification is numbered. The user responds with:
- `Accetta 1,3` → apply modifications 1 and 3 only.
- `Modifica 4: <direction>` → regenerate modification 4 as directed.
- `Rivedi completamente: <direction>` → regenerate the whole proposal.
- `Tieni in considerazione 2: <note>` → do not apply modification 2 now; record it as deferred/context.
- `Accetta` (no numbers) → apply all modifications.

Optional shortcuts remain accepted for speed:
`A = Accetta`, `M = Modifica`, `R = Rivedi completamente`, `T = Tieni in considerazione`.

## 4. Handle Response

### Accetta (selected numbers or all)

1. Apply via Edit on the article only the modifications accepted by the user. If some modifications were deferred or left pending, apply only the accepted ones.
2. Update the project file: each accepted modification → `Accepted`.
3. If a sidecar proposal file exists for this point, update it: accepted item
   numbers, pending items, and status (`accepted` if all accepted, `partial`
   otherwise).
4. Increment the *accepted-since-last-bump* counter.
5. **Do not commit.**
6. **Do not advance automatically.** Output:

   ```text
   Applicate modifiche <numbers>. [Restano in sospeso le modifiche <numbers>.] Ci sono altri cambiamenti da fare in questo paragrafo?
   ```

   Wait for an explicit command from the user.

7. If the counter has reached `AUTO_BUMP_THRESHOLD`, after the user signals to advance, propose a bump (hand off to `60-bump-version.md`).

### Tieni in considerazione (selected numbers or all)

1. Mark the selected modifications as `Deferred` in the project file with the
   user's note/reason. If no numbers are provided, mark the whole point
   `Deferred`.
2. If a sidecar proposal file exists for this point, update the deferred item
   numbers and keep status `partial` unless all items were deferred, in which
   case set `deferred`.
3. No file edits for those modifications.
4. If the note describes an intention for the current unit, record it in the
   freeze ledger via `log-comment` so the reminder survives outside chat.
5. **Do not advance automatically.** Output:

   ```text
   Modifiche <numbers> tenute in considerazione. [Restano in sospeso le modifiche <numbers>.] Ci sono altri cambiamenti da fare in questo paragrafo?
   ```

### Rivedi completamente

1. Regenerate the entire proposal from the original text and the user's new
   direction, if provided.
2. If a sidecar proposal file exists for this point, mark the previous proposal
   as `superseded`, append the human direction in `Decision Trail`, and write the
   new proposal in the same file.
3. Re-present the full proposal in the standard format.
4. Return to step 3. No file modifications happen until `Accetta`.

### Modifica <N>: <direction>

1. Regenerate modification N according to the user's direction.
2. If a sidecar proposal file exists for this point, overwrite the relevant
   modification entry and append the human direction in `Decision Trail`.
3. Re-present the updated modification in context, keeping the same numbering.
4. Return to step 3. After eventual `Accetta`, label the modification as `Modified` (not merely `Accepted`).

### Advance to next point

Only advance when the user gives an explicit command:
- "no, prossimo paragrafo"
- "passa al prossimo"
- "next"
- "prossimo"

**Before advancing, run the freeze auto-offer** (`15-freeze-ledger.md` §7):

- If the unit's work concluded cleanly, offer to freeze it:
  `Lavoro su <unit> concluso: <X> accettate, <Y> tenute in considerazione. Congelo questa parte come conclusa? (sì / no / più tardi)`.
  `sì` → `freeze`; `più tardi` → leave 🔵 `wip`.
- If the user named something still to do on the unit (or chose `no` with a
  reason), record it via `log-comment` (`15-freeze-ledger.md` §9): the unit
  becomes 🟡 `open` with the intention written into the ledger. Never let a
  deferred intention live only in chat.

Then advance.

## 5. Edge Cases

- **Multiple decisions in one user message** (for example, *"Accetta tutto tranne punto 3: tienilo in considerazione"*). Process them sequentially with the per-point logic above. Still no auto-commit.
- **Character overshoot after Accetta.** Report and ask: `The overrun is now +X. Do you prefer to proceed and handle it in the final sweep, or look for a compensating cut now?`
- **Bibliography conflict.** If the user wants a key that does not exist or has dubious metadata, defer to `40-bibliography-check.md` and do not apply until cleared.
- **Anglicism not in whitelist** (`ARTICLE_LANG=it` only). Surface in the proposal block under `Possible exceptions`; the user decides whether to add it to the whitelist or rephrase.
- **Whole article scope.** Walk the article section by section. The user can pause at any moment with `pause` or `stop`, and resume later from the same point.

## 6. State Persistence

The accepted-since-bump counter and per-point decision state live entirely inside the `revision-plan-vN.md` file. On every `Accetta`, `Modifica`, `Rivedi completamente`, or `Tieni in considerazione`, rewrite the relevant section of that file. This way, an interrupted session resumes cleanly: when the skill is re-invoked, it reads the project file and continues from the first point still in `To decide` state.

## 7. Revision Closure

**Trigger — either of:**

1. **Perimetro naturale esaurito**: tutti i punti del piano di revisione sono in stato `Accepted`, `Modified`, o `Deferred`.
2. **Chiusura esplicita**: l'utente invia una frase di chiusura —
   IT: `chiudi`, `fine`, `ho finito`, `concludi`, `stop`, `basta così`, `chiudiamo` /
   EN: `close`, `done`, `finish`, `end`, `I'm done`.

**Sequenza obbligatoria:**

1. Presentare il riepilogo:

   ```
   Revisione punti completata.
   Punti totali: N  |  Accettati: A  |  Modificati: M  |  Rivisti completamente: R  |  Da considerare: T
   Bilancio caratteri: +Δ (limite: EDITORIAL_LIMIT_CHARS)
   Versione articolo attiva: <path>
   ```

2. Chiedere conferma:

   ```
   Procedo con la chiusura?
     1. Final sheet (/r-sheet)  — facoltativo
     2. Decision log            — obbligatorio
     3. Sync current files      — obbligatorio
   (sì / sì senza final sheet / annulla)
   ```

3. Su conferma:
   - Se richiesto: `workflow/70-final-sheet.md`
   - `workflow/95-decision-log.md`  ← chiude il task file e sincronizza i file correnti
