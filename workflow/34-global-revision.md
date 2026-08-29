# 34 — Global / Holistic Revision

Triggered by `/r-global`. A **non-granular, high-level** revision that examines the article as a whole organism through seven diagnostic lenses. This mode does not descend into sentence-level edits — it operates at the structural, argumentative, and narrative level. After the diagnostic report, the user can either proceed with global decision proposals or save the report as a persistent trace for `/r-pp` / `/r-pp-a`.

## 0. Entry Point

Invoked by `/r-global` or phrases like:
- *"revisione globale"*
- *"revisione complessiva"*
- *"analisi strutturale dell'articolo"*
- *"holistic review"*
- *"check the overall structure"*

## 1. Bootstrap & Setup

Run `00-bootstrap.md` only if required and separately approved, then
`10-setup.md` read-only. The seven-lens diagnosis does not bump. Saving a trace
requires confirmation but still does not create a manuscript version; the first
accepted manuscript edit enters the tracked lifecycle.
Any task-update instruction in this workflow is conditional on
`TASK_FILE_PATH` already existing; before the first accepted edit, keep progress
only in working memory.

## 2. Read Full Article

1. Read the entire article into context (skip YAML frontmatter).
2. Parse the section structure: identify all `#`, `##`, `###` headings and their hierarchy.
3. Build the chapter map using the first numeric component of numbered headings
   (`1`, `1.1`, `1.2.3` = Capitolo 1; `2` = Capitolo 2), and keep
   section/subsection paths separate.
4. Build the paragraph map with full locators:
   `Capitolo <C> — <chapter title>; P<N> — <ARTICLE_PATH>:<L1-L2>`.
5. Count characters per section.
6. Extract the first sentence of each section (for narrative arc analysis).
7. Extract key terminology (defined terms, recurring concepts) for consistency check.

## 3. Apply the Seven Lenses

Generate a structured diagnostic report. Present all seven lenses as a single, complete document — the user reviews the whole picture before any edits.

### Lens 1 — Thesis Clarity

1. Locate the thesis/contribution statement. Typically in the introduction (last paragraph) or in a dedicated subsection.
2. Evaluate:
   - **Is it explicit?** Does a single sentence state what the article contributes?
   - **Is it answerable or contestable?** Is it precise enough for the article's
     theoretical, empirical, interpretive, or design contribution? Require
     falsifiability only for claims that the study actually presents as
     testable hypotheses.
   - **Is it positioned?** Does it reference the gap it fills?
3. If missing or weak, flag with a specific recommendation.

### Lens 2 — Argument and Content Architecture

1. Map every section to its actual primary role: governing claim, supporting
   claim, definition, evidence, example, bridge, implication, or limitation.
   Do not infer an IMRaD role solely from section number.
2. Identify each section's main claim, required support, and relation to the
   preceding and following sections.
3. Identify logical leaps (A → C without B), orphaned ideas, duplicate
   functions, overloaded units, and missing steps.
4. Flag contradictions between sections (e.g. §2 defines X one way, §5 uses X
   differently).

### Lens 3 — Section Proportionality

1. Calculate the character count and percentage of total for each section.
2. Compare against explicit journal limits or project norms first. When those
   are absent, the following article-type proportions may be reported only as
   orientation, not as pass/fail thresholds:
   - **Empirical (IMRaD):** Intro 10-15%, Literature/Hypotheses 15-20%, Method 15-20%, Results 20-25%, Discussion 20-25%, Conclusion 5-10%.
   - **Theoretical:** Intro 10-15%, Body (split by argument steps) 65-75%, Conclusion 10-15%.
   - **Review:** Intro 5-10%, Thematic sections (balanced) 75-85%, Conclusion 10-15%.
3. Flag a section only when its size impairs its argumentative function or
   violates an explicit norm. A numerical deviation alone is not a defect.

### Lens 4 — Argumentative Progression

1. Evaluate the article's argumentative progression:
   - **Orientation:** Does the opening establish the problem, scope, and reader
     expectations appropriate to the genre? Do not require a rhetorical hook.
   - **Problem or gap:** Is the reason for the inquiry explicit and supported?
   - **Response:** Do theory, method, evidence, or analysis address that reason
     in a traceable sequence?
   - **Implication:** Does the conclusion state what follows without exceeding
     the evidence and reconnect to the governing question?
2. Flag transitions that lack a real logical relation. Do not add storytelling
   formulas where the genre calls for a different progression.

### Lens 5 — Redundancy

1. Treat this as a coarse whole-manuscript scan. Use the candidate-generation
   mechanics in `workflow/38-redundancy-audit.md` to surface representative
   close rewrites and distant paraphrases without treating scores as verdicts.
2. Distinguish preliminary examples of true duplication, new evidence,
   necessary reprise, recurring terminology, contradiction, and false
   positives. Do not recommend a cut from similarity alone.
3. Report the sections and proposition clusters that merit a focused
   `/r-redundancy` audit. Build the full reverse outline only if the user selects
   this lens for follow-up.

### Lens 6 — Terminology Consistency

1. Extract all key terms and their definitions.
2. Check if the same concept is called by the same name throughout.
3. Flag inconsistencies (e.g. *emotional labour* in §2 becomes *emotional work* in §4).
4. Flag terms used before they are defined.

### Lens 7 — Norm Alignment

1. Compare the article's structure against the editorial norms loaded in setup.
2. Check:
   - Section heading conventions (numbered vs unnumbered, title case vs sentence case).
   - Expected section order (IMRaD vs alternative).
   - Citation style (in-text format, bibliography format).
   - Abstract requirements (structured vs unstructured, word limit).
   - Any journal-specific structural requirements.

## 4. Present Diagnostic Report

Output the complete report as a single block:

```
## Revisione Globale — <article>

### 1. Chiarezza della tesi
- **Dov'è la tesi?** §1, riga X: «<quote>»
- **È esplicita?** Sì / Parzialmente / No
- **È valutabile nel genere adottato?** Sì / Parzialmente / No — <motivazione>
- **Raccomandazione:** <indicazione concreta>

### 2. Architettura argomentativa
- **Mappa:**
  §1: <ruolo nell'argomentazione>
  §2: <ruolo>
  → §3: <eventuale salto logico>
  §4: <ruolo>
  §5: <ruolo>
  §6: <ruolo>
- **Salti logici:** <elenco>
- **Passaggi mancanti:** <elenco>
- **Contraddizioni:** <elenco>

### 3. Proporzionalità delle sezioni
| Sezione | Caratteri | % del totale | Norma o riferimento | Valutazione funzionale |
|---|---|---|---|---|
| §1 Intro | 3200 | 12% | nessuna norma esplicita | adeguata allo scopo |
| §2 Letteratura | 8200 | 31% | orientamento 15-20%, non vincolante | verificare due funzioni duplicate |
| §3 Metodo | 4100 | 16% | norma rivista: max 5000 caratteri | conforme |

### 4. Progressione argomentativa
- **Orientamento:** <problema, scopo e aspettative del lettore>
- **Problema o gap:** <è esplicito e sostenuto?>
- **Risposta:** <la sequenza di teoria, metodo, evidenza o analisi è tracciabile?>
- **Implicazione:** <la conclusione segue dalle evidenze e torna alla domanda?>
- **Raccomandazione:** <indicazione>

### 5. Ridondanza
- **Cluster candidati:** P12 (Capitolo 3, <ARTICLE_PATH>:145-153) ~ P28 (Capitolo 5, <ARTICLE_PATH>:310-318) — <proposizione condivisa>
- **Differenze da preservare:** <evidenza, funzione, condizioni o nessuna>
- **Classificazione preliminare:** <tipo o da verificare>
- **Raccomandazione:** <scope per /r-redundancy oppure nessun approfondimento>

### 6. Coerenza terminologica
| Termine | Definito in | Usato anche come | Problema |
|---|---|---|---|
| *emotional labour* | §2, riga 45 | *emotional work* in §4, riga 12 | Inconsistente |
| *self-efficacy* | §2, riga 78 | — | OK |

### 7. Allineamento alle norme
- **Struttura attesa:** IMRaD
- **Struttura effettiva:** Intro → Letteratura → Ipotesi → Metodo → Risultati → Discussione → Conclusione
- **Scostamenti:** <elenco>
- **Raccomandazione:** <indicazione>

---
**Azioni suggerite:** N interventi strutturali, M interventi di superficie.
Come vuoi usare questo report?
- "tutte" — elaboro proposte per ogni lente
- "proporzioni + terminologia" — solo lenti specifiche
- "solo architettura" — una singola lente
- "traccia per /r-pp" — salvo il report come guida globale per la revisione paragrafo per paragrafo, senza modificare l'articolo
- "nessuna" — prendo atto del report, nessuna modifica
```

Adapt to English if `ARTICLE_LANG=en`.

## 5. Save as Global Trace for `/r-pp`

If the user chooses `traccia per /r-pp`, `salva traccia`, `usa come traccia`,
or equivalent:

1. Do **not** modify the article.
2. Prepare a standalone trace file at:

   ```
   revisions/<article-slug>/sources/global-trace-<source-version-or-date>.md
   ```

3. Before creating the file, show the exact path and ask:

   ```
   Creo la traccia globale per la revisione paragrafo per paragrafo?
   File: revisions/<article-slug>/sources/global-trace-<source-version-or-date>.md
   (sì / no)
   ```

4. On confirmation, create `revisions/<article-slug>/sources/` if missing and
   write the trace file. The trace is a revision source, not an accepted change.
   It must not be included in response-to-reviewers material unless the user
   later applies concrete changes derived from it.
5. If a tracked task exists, update it. A trace-only diagnostic does not create
   a task file merely to record completion.
6. Ask whether to close the round or continue with selected global fixes:

   ```
   Traccia globale salvata. Vuoi chiudere la revisione globale o proporre anche modifiche globali? (chiudi / proponi modifiche)
   ```

### Trace File Format

```
---
source: global
status: active
article: <article-path>
article_version: <source article version, or unversioned>
created: <YYYY-MM-DD>
use_as_trace_for:
  - /r-pp
  - /r-pp-a
---

# Traccia revisione globale — <article>

## Sintesi globale
- Tesi/funzione dell'articolo: <one-line synthesis>
- Problema principale da tenere presente: <priority issue>
- Direzione editoriale: <what the paragraph pass should preserve or improve>

## Priorità per la revisione paragrafo per paragrafo
1. <priority from the seven-lens report>
2. <priority>
3. <priority>

## Mappa per sezione
| Sezione | Funzione nell'argomento | Rischi globali | Cosa controllare in `/r-pp` |
|---|---|---|---|
| §1 | <role> | <risk> | <paragraph-level checks> |

## Indicazioni per i paragrafi
- Verificare che ogni paragrafo serva la funzione della sua sezione.
- Segnalare scarti rispetto alla tesi, salti logici, ridondanze e squilibri.
- Usare queste indicazioni come contesto diagnostico: ogni modifica resta soggetta alla decisione esplicita dell'utente.

## Report globale completo
<paste the seven-lens diagnostic report>
```

If an active trace already exists for the same article, ask whether to overwrite
it, keep both, or mark the older trace as superseded. Do not delete older traces
silently.

## 6. Generate Proposals by Lens

A proposal at this altitude is normally structural. When one nonetheless rests on
a judgement about Italian — terminology that is claimed to be improper, a
recurring construction called bureaucratic — verify it with the `treccani` skill
on the isolated term and cite the entry, or present it as a stylistic
preference.

Run the freeze check (`15-freeze-ledger.md` §4) on each unit a structural change
would touch; if a unit is 🟢 `frozen`, apply the advisory warning flow (§5)
before proposing. A global rename that sweeps frozen units must list them and ask
confirmation once for the whole sweep.

For each lens the user selects:

### Structural proposals (Lenses 1, 2, 4)

For architectural changes, run the read-only inventory and mapping phase of
`13-content-structure.md`. Present the current and proposed architecture plus a
preservation manifest before individual decision points. Examples:
- **Restructure:** "Move the hypotheses from §2.3 into §1 (introduction) to establish the thesis earlier."
- **Reorder:** "Swap §4 and §5: present discussion before detailed results tables."
- **Add:** "Insert a transition paragraph between §2 and §3 explaining how the literature gap motivates the method."

### Proportionality proposals (Lens 3)

For size adjustments:
- Present the target char count per section.
- Show which paragraphs to cut, consolidate, or expand, always with chapter and
  line range.
- Use the standard decision labels: user can accept the cut of specific paragraphs, request modifications, ask for a full rewrite, or keep the issue as context.

```
## Point <N> — Proporzioni: ridurre §2 · scope: global

**Diagnosi:** §2 è al 31% (atteso 15-20%). Eccesso di ~3000 caratteri.

**Modifiche:**
1. [Capitolo 2 — Letteratura; P8 — <ARTICLE_PATH>:98-106] Rimuovere la digressione su Author (2018) — 800 chars [(non essenziale per l'argomento)]
2. [Capitolo 2 — Letteratura; P12-P14 — <ARTICLE_PATH>:145-176] Consolidare i tre paragrafi sulla definizione di X in uno solo — 1200 chars [(ridondante)]
3. [§2.4] Spostare la tabella comparativa in appendice — 1000 chars [(materiale supplementare)]

**Δ**: chars -3000 / words -450 · risk: medium

**Decisione sulla proposta?** (`Accetta` / `Modifica` / `Rivedi completamente` / `Tieni in considerazione`)
```

### Terminology proposals (Lens 6)

For global renames:
- Use `replaceAll` on the article file.
- Present as a single decision point.

```
## Point <N> — Terminologia: "emotional work" → "emotional labour" · scope: global

**Diagnosi:** Il termine è definito come *emotional labour* in §2 ma usato come *emotional work* in §4, §5.

**Modifiche:**
1. [global] «emotional work» → «emotional labour» [(5 occorrenze: §4 riga 12, §4 riga 45, §5 riga 8, §5 riga 22, §5 riga 67)]

**Δ**: chars +5 / words 0 · risk: low

**Decisione sulla proposta?** (`Accetta` / `Modifica` / `Rivedi completamente` / `Tieni in considerazione`)
```

### Redundancy proposals (Lens 5)

Run the focused read-only workflow in `workflow/38-redundancy-audit.md` on the
selected sections. Its reverse outline, classification table, canonical home,
unique-information accounting, and decision packets replace a simple
side-by-side similarity judgement. Any accepted merge, move, cut, deepening, or
cross-reference enters that workflow's tracked application phase.

## 7. Handle Responses

Follow standard `30-iterate-points.md`, section 4, with one addition:

- For global modifications (e.g. `replaceAll` renames), after `Accetta`, verify the change with a grep to confirm all occurrences were updated.
- Structural acceptances always enter the tracked application phase of
  `13-content-structure.md`; do not pass them through direct apply or automatic
  mode. After application, re-read the article and confirm no broken
  cross-references (e.g. "as discussed in §4" now points to the wrong section).

## 8. Edge Cases

- **Single-section article.** Still run the seven lenses. Scope adapts naturally.
- **No structural issues found.** Announce: *"L'architettura dell'articolo è solida. Tutte e sette le lenti non rilevano problemi strutturali."* Offer to proceed to `/r-pp` for granular revision.
- **Trace-only round.** If the user saves the diagnostic as a trace and applies
  no manuscript modifications, report the saved path and close without task,
  decision log, current-file sync, or Git.
- **Massive restructuring needed.** If the proposal touches multiple sections
  or creates interdependent decisions, recommend approving one coherent
  structural cluster at a time and verify the preservation manifest after each
  cluster.
- **Contradiction with reviewer feedback.** If reviewer feedback was previously processed via `/article-revision` and the global revision identifies a contradictory recommendation, surface the conflict explicitly: *"⚠️ Il Reviewer A ha chiesto di espandere §2, ma la lente 3 (proporzionalità) suggerisce di ridurlo. Quale direzione preferisci?"*
- **Character budget.** Structural changes (cuts, moves, adds) have large character impact. Track the cumulative Δ after each accept and compare against `EDITORIAL_LIMIT_CHARS`.
- **Handoff / pause.** If the user says `pause`, `stop`, `sospendi`,
  `interrompi`, or `/r-handoff`, call `workflow/06-handoff.md` with the current
  lens, whether the global trace has been saved, pending structural proposals,
  and exact next action. Do not run closure or sync.

## 9. Revision Closure

**Trigger — either of:**

1. **Perimetro naturale esaurito**: tutte le lenti selezionate dall'utente hanno prodotto le loro proposte e ricevuto una decisione esplicita.
2. **Chiusura esplicita**: l'utente invia una frase di chiusura —
   IT: `chiudi`, `fine`, `ho finito`, `concludi`, `basta così`, `chiudiamo` /
   EN: `close`, `done`, `finish`, `end`, `I'm done`.

**Sequenza obbligatoria:**

1. Presentare il riepilogo:

   ```
   Revisione globale completata.
   Lenti analizzate: 7  |  Lenti con modifiche: N
   Traccia per /r-pp: <none|path>
   Strutturali: X  |  Terminologiche: Y  |  Proporzione: Z  |  Rifiutate: R
   Bilancio caratteri: +Δ (limite: EDITORIAL_LIMIT_CHARS)
   Versione articolo attiva: <path>
   ```

2. Chiedere conferma:

   ```
   Procedo con la chiusura?
     1. Final sheet (/r-sheet)  — facoltativo
     2. Decision log            — obbligatorio
     3. Sync derived exports    — obbligatorio
   (sì / sì senza final sheet / annulla)
   ```

3. Su conferma, solo se esiste un round tracciato (`TASK_FILE_PATH`):
   - Se richiesto: `workflow/70-final-sheet.md`
   - `workflow/95-decision-log.md`  ← chiude localmente il task e sincronizza
   - chiedere separatamente se pubblicare con Git

Una diagnosi globale o una traccia senza modifiche al manoscritto non richiede
task, decision log, sync o Git.
