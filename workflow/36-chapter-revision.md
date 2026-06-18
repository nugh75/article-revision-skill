# 36 — Chapter / Section Revision

Triggered by `/r-chapter`. Revises a single section of the article in full
awareness of the rest of the text: terminology, cross-references, argument
thread, redundancy, section interfaces, and norms compliance.

This mode differs from `/r-global` (no sentence-level edits; operates on the
whole article) and from `/r-pp` (paragraph-level edits with no cross-article
context): it operates at paragraph depth **on one section** while holding the
entire article as reference.

## 0. Entry Point

Invoked by `/r-chapter [§N | section-name]` or phrases like:
- *"revisione capitolo X"*
- *"rivedi la sezione metodologia in relazione al resto"*
- *"revise chapter 3 in context"*
- *"chapter revision"*

If a section identifier is provided in the command (e.g. `/r-chapter §3` or
`/r-chapter introduction`), use it directly. Otherwise show the section list
(step 2) and ask.

## 1. Bootstrap & Setup

If not already done, run `00-bootstrap.md` and `10-setup.md` to load `.env`,
norms, bibliography, active article, detect `ARTICLE_LANG`, complete the
mandatory bump, and create the task file (`workflow/05-task.md` — action
`create` with `COMMAND=/r-chapter`).

`05-task.md#update-step`: `Select section` → `in-progress`.

## 2. Select Target Section

If not already specified:

1. Parse the article. List all `#` and `##` headings with char counts:

   ```
   §1 — Introduction (820 chars, 4%)
   §2 — Literature Review (3 120 chars, 15%)
   §3 — Methodology (2 040 chars, 10%)
   §4 — Results (4 800 chars, 23%)
   §5 — Discussion (5 100 chars, 25%)
   §6 — Conclusion (1 200 chars, 6%)
   ```

2. Ask:

   > Quale sezione vuoi revisionare in relazione al resto dell'articolo?
   > (Indica §N, il titolo, o il numero d'ordine.)

3. Wait. Accept `§N`, a heading text substring, or a number.

`05-task.md#update-step`: `Select section` → `done`.

## 3. Load Article

1. Read the full article into context (skip YAML frontmatter).
2. Assign:
   - `TARGET` = the selected section (all paragraphs between its heading and the next same-level heading).
   - `CONTEXT` = everything else.
3. Compute: `TARGET_CHARS` and `TARGET_PCT` (% of total article chars).
4. Extract from CONTEXT:
   - **Defined terms**: bold (`**term**`), italics (`*term*`), or explicit "X is defined as" patterns.
   - **Forward/backward cross-references to TARGET**: `§N`, `see section`, `as discussed in`, `as we will show`, etc.
   - **Repeated-content candidates**: paragraphs in CONTEXT with > 40% word overlap with any paragraph in TARGET.
   - **Section seams**: closing paragraph of §(N-1) + opening paragraph of §(N+1).

`05-task.md#update-step`: `Load article` → `done`.

## 4. Cross-Article Diagnostic

Analyse TARGET across six dimensions using CONTEXT. Generate a single
structured report — the user reviews the complete picture before any edit.

### Dimension 1 — Terminology consistency

For each defined term in CONTEXT that appears in TARGET:
- Is it used with the same meaning?
- Is it spelled and capitalised the same way?

For each term first introduced in TARGET:
- Is it used consistently in subsequent sections of CONTEXT?

```markdown
| Termine | Definito in | Uso in TARGET | Coerente? | Nota |
|---|---|---|---|---|
| *self-efficacy* | §2 r.45 | corretto | ✓ | — |
| *emotional labour* | §2 r.78 | "emotional work" | ✗ | →align to §2 |
```

### Dimension 2 — Cross-references

For each cross-reference in TARGET:
- Does it point to an existing heading?
- Is the referenced content actually where the article claims?

For each reference in CONTEXT that promises content in TARGET:
- Is that content present?

```markdown
| Tipo | Testo nel documento | Destinazione | Status | Nota |
|---|---|---|---|---|
| forward | "as shown in §5" | §5 Results | ✓ | — |
| backward | "discussed in §2" | §2 Literature | ✗ | §2 does not discuss X |
| incoming | "§3 explains Y" (in §5) | TARGET §3 | ✗ | Y not in §3 |
```

### Dimension 3 — Section interface

Examine the seam between TARGET and its neighbours:

- **§(N-1) → TARGET**: does the closing sentence of §(N-1) lead logically into TARGET's opening? Is there a bridging sentence?
- **TARGET → §(N+1)**: does TARGET's closing sentence set up §(N+1)'s opening?

Rate each interface: `smooth` | `abrupt` | `redundant` | `missing bridge`.
For `abrupt` or `missing bridge`, draft a candidate transition sentence.

### Dimension 4 — Redundancy

List TARGET paragraphs that substantially repeat content in CONTEXT (>40%
conceptual overlap).

```markdown
| Paragrafo TARGET | Sovrapposizione con | Tipo | Azione consigliata |
|---|---|---|---|
| P12 (sample size) | §6 r.210 | identical | consolidate → §3 only |
| P7 (framework) | §2 r.88 | partial | shorten P7 |
```

If no significant redundancy: "Nessuna ridondanza significativa."

### Dimension 5 — Argument thread

Map TARGET's role in the macro-argument (use the article's introduction and
conclusion as anchor):

- **Promise**: what does the introduction say TARGET will do?
- **Delivery**: what does TARGET actually deliver?
- **Gap**: discrepancy, or "nessun gap rilevato".

### Dimension 6 — Norms compliance (section-level)

Compute TARGET's share of the article and compare with the journal's expected
structure (from `EDITORIAL_NORMS_PATH`):

| Sezione | Attuale | Attesa (norme) | Status |
|---|---|---|---|
| §3 Methodology | 10% (2 040 ch) | 15-20% | ⚠️ underweight |

---

Present the complete diagnostic in chat:

```
## Revisione Capitolo — §N <title>

Sezione target: <path>:<line-range>  (<N> chars, <X>% of article)

### Dim 1 — Terminologia
<table>

### Dim 2 — Cross-riferimenti
<table>

### Dim 3 — Interfacce di sezione
Precedente → TARGET: <smooth|abrupt|missing bridge> — <candidate bridge if needed>
TARGET → Successiva: <smooth|abrupt|missing bridge> — <candidate bridge if needed>

### Dim 4 — Ridondanze
<table or "Nessuna ridondanza significativa">

### Dim 5 — Filo argomentativo
- Promise: <text>
- Delivery: <text>
- Gap: <text or "nessun gap">

### Dim 6 — Proporzione
<table>

---
Quali dimensioni vuoi sistemare? ("tutte" / "1,3,5" / specifici)
```

Wait for user selection.

`05-task.md#update-step`: `Cross-article analysis` → `done`.

## 5. Iterate Fixes

Run the freeze check (`15-freeze-ledger.md` §4) on each paragraph a point would
touch; if a paragraph is 🟢 `frozen`, apply the advisory warning flow (§5) before
proposing.

For each selected dimension, generate revision points following the standard
decision interaction pattern from `SKILL.md` § "Interaction pattern (binding)".

Each point must:
- Identify the specific paragraph(s) in TARGET to change.
- Reference the cross-article evidence that motivates the change
  (e.g. «termine "X" definito come Y in §2, usato come Z qui»).
- Apply changes using `Edit` (surgical) or `replace_all` for global renames.

Handle `Accetta`, `Modifica`, `Rivedi completamente`, and
`Tieni in considerazione` responses as in `workflow/30-iterate-points.md`.

`05-task.md#update-step`: `Fix selected` → `in-progress` (at start).
`05-task.md#update-step`: `Fix selected` → `done` (when user signals all done or all dimensions exhausted).

## 6. Post-revision checks

- If any citation was touched → hand off to `workflow/40-bibliography-check.md`.
- If any numeric claim was touched → hand off to `workflow/51-data-verification.md`.

## 7. Revision Closure

**Trigger — either of:**

1. **Perimetro naturale esaurito**: tutte le dimensioni selezionate dall'utente hanno ricevuto una decisione esplicita.
2. **Chiusura esplicita**: l'utente invia una frase di chiusura —
   IT: `chiudi`, `fine`, `ho finito`, `concludi`, `stop`, `basta così`, `chiudiamo` /
   EN: `close`, `done`, `finish`, `end`, `I'm done`.

**Sequenza obbligatoria:**

1. Presentare il riepilogo:

   ```
   Revisione capitolo §N completata.
   Dimensioni analizzate: D  |  Modifiche accettate: A  |  Rifiutate: R
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
   - `workflow/95-decision-log.md` con `type: revision-chapter` ← chiude il task file e sincronizza i file correnti

`05-task.md#update-step`: `Decision log` → `done` once `95-decision-log.md` completes.
