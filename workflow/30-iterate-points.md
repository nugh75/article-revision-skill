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

When the target is or includes a paragraph, compute the full locator before
generating the proposal:

`Capitolo <C> — <chapter title>; Paragrafo P<N> — <ARTICLE_PATH>:<L1-L2>`

Use the chapter rule in `SKILL.md#paragraph-and-chapter-locators-binding`: the
first numeric component of the numbered heading determines the chapter. Keep any
nearest subsection as additional context, but do not call it a chapter.

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
- 🔵 `wip` / untracked → proceed. Mark it `wip` only after a tracked round and
  ledger exist; diagnosis alone does not create or update state.

## 2. Generate Proposal

Apply:

- editorial norms loaded in setup;
- journal-specific style skill, if available;
- `templates/accepted-anglicisms-it.md` if `ARTICLE_LANG=it`;
- minimum surgical change: alter only what the point requires.

Never collapse multiple separate concerns into a single proposal. If the same paragraph needs both citation correction and phrasing change, present two consecutive proposals, each with its own decision.

If a single proposal contains more than one numbered modification, keep the
complete proposal in chat. Write a sidecar only when the user explicitly asks
to save it or after the first accepted edit has created a tracked round:

`revisions/<reviewer>/proposal-revision-YYYY-MM-DD-HHMM.md`

Use `templates/proposal-revision.md`. The file mirrors the exact chat proposal
and acts as persisted state only after writing it is authorized.
Each subsequent `Accetta` / `Modifica` / `Rivedi completamente` /
`Tieni in considerazione` updates the same file's
`Decision Trail` and status.

## 3. Present In Chat

```text
## Point N — <short title> · scope: <fragment|paragraph|whole article>

**Unità**: <Capitolo C — title; Paragrafo P<N> — article:line-range> <!-- required for paragraph scope -->

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

1. Select the execution mode if it was not already fixed:
   - `direct-apply` → call `11-direct-apply.md` for the accepted wording, report
     the verified target, and return from this response branch without running
     the tracked-round steps below;
   - `tracked-round` → if `TASK_FILE_PATH` is absent, run the first-edit
     transition in `10-setup.md`, then recompute locators against the new
     working version.
2. In a tracked round, apply via Edit on the working article only the modifications accepted by the
   user. If some modifications were deferred or pending, apply only the
   accepted ones.
3. Update an existing project file, or create the prepared plan now if this is
   a reviewer round: each accepted modification → `Accepted`.
4. If a sidecar proposal file exists for this point, update it: accepted item
   numbers, pending items, and status (`accepted` if all accepted, `partial`
   otherwise).
5. Increment the *accepted-since-last-bump* counter.
6. Increment `changes-since-git-checkpoint` by the number of accepted numbered
   modifications. After the article, project file, sidecar, and ledger state
   are consistent, call `07-git-checkpoint.md` with
   `mode=interactive-prompt` when its prompt conditions are met. Ask before the
   scoped commit and push; continue only on `sì`. On `non ora`, preserve the
   counter and follow the workflow's re-prompt rule.
7. **Do not advance automatically.** Output:

   ```text
   Applicate modifiche <numbers>. [Restano in sospeso le modifiche <numbers>.] Ci sono altri cambiamenti da fare in questo paragrafo?
   ```

   Wait for an explicit command from the user.

8. If the counter reaches `AUTO_BUMP_THRESHOLD`, offer an additional bump after
   the user signals to advance. Do not couple it to Git.

### Tieni in considerazione (selected numbers or all)

1. If `TASK_FILE_PATH` exists, mark the selected modifications as `Deferred` in
   the project file with the user's note/reason. If no numbers are provided,
   mark the whole point `Deferred`. Without a tracked round, retain the decision
   in chat unless the user explicitly asks to save it.
2. If a tracked sidecar proposal file exists for this point, update the deferred item
   numbers and keep status `partial` unless all items were deferred, in which
   case set `deferred`.
3. No file edits for those modifications.
4. If a tracked ledger exists, record an intention for the current unit via
   `log-comment`. Without one, offer to save the note but do not write it
   implicitly.
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

**Before advancing in a tracked round, run the freeze auto-offer**
(`15-freeze-ledger.md` §7). In a diagnostic-only pass, advance without changing
the ledger.

- If the unit's work concluded cleanly, offer to freeze it:
  `Lavoro su <unit> concluso: <X> accettate, <Y> tenute in considerazione. Congelo questa parte come conclusa? (sì / no / più tardi)`.
  `sì` → `freeze`; `più tardi` → leave 🔵 `wip`.
- If the user named something still to do on the unit (or chose `no` with a
  reason), record it via `log-comment` (`15-freeze-ledger.md` §9): the unit
  becomes 🟡 `open` with the intention written into the ledger. Never let a
  deferred intention live only in chat.

Then advance.

## 5. Edge Cases

- **Multiple decisions in one user message** (for example, *"Accetta tutto tranne punto 3: tienilo in considerazione"*). Process them sequentially with the per-point logic above, then show one Git checkpoint prompt if the accumulated counter meets the prompt conditions.
- **Character overshoot after Accetta.** Report and ask: `The overrun is now +X. Do you prefer to proceed and handle it in the final sweep, or look for a compensating cut now?`
- **Bibliography conflict.** If the user wants a key that does not exist or has dubious metadata, defer to `40-bibliography-check.md` and do not apply until cleared.
- **Anglicism not in whitelist** (`ARTICLE_LANG=it` only). Surface in the proposal block under `Possible exceptions`; the user decides whether to add it to the whitelist or rephrase.
- **Handoff / pause.** Natural pause/stop updates only an existing local task
  checkpoint. Explicit `/r-handoff` may also log and sync locally. Neither
  authorizes Git without `--git` or `commit e push`.
- **Whole article scope.** Walk the article section by section. The user can
  pause at any moment via the handoff workflow and resume later from the same
  point.

## 6. State Persistence

After a tracked round starts, the accepted-since-bump counter and per-point
state live in `revision-plan-vN.md`, and Git prompt state lives in
`TASK_FILE_PATH`. Before that boundary, proposals and reformulations remain in
chat unless the user explicitly asks to save them. Only applied edits or
authorized saved artifacts create persistent session state.

## 7. Revision Closure

**Trigger — either of:**

1. **Perimetro naturale esaurito**: tutti i punti del piano di revisione sono in stato `Accepted`, `Modified`, o `Deferred`.
2. **Chiusura esplicita**: l'utente invia una frase di chiusura —
   IT: `chiudi`, `fine`, `ho finito`, `concludi`, `basta così`, `chiudiamo` /
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

3. Su conferma, se `TASK_FILE_PATH` esiste:
   - Se richiesto: `workflow/70-final-sheet.md`
   - `workflow/95-decision-log.md`  ← chiude localmente il task e sincronizza i file correnti
   - chiedere separatamente se pubblicare con commit e push
   Se non esiste un task, distinguere:
   - `direct-apply` → riepilogare file e verifica, senza log, sync o Git state;
   - `chat-only` → terminare con il riepilogo diagnostico senza creare file.
