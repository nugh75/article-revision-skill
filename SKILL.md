---
name: article-revision
description: |
  Coordinate iterative revision of a scientific article in markdown. Trigger
  when the user asks to apply reviewer feedback ("revise article",
  "apply reviewer X comments", "let's process the reviewer comments"),
  to bump the article to a new version, pause/resume an in-progress revision
  via `/r-handoff` or `/r-resume`, asks for the recommended path via
  `/r-guide`, or invokes `/article-revision` explicitly.
  Skill assumes a project layout with `articles/`, `bibliography/
  reference.bib`, `editorial-norms/`, `revisions/`, and an `.env` file.
  For each reviewer point: shows original text + proposed change in chat,
  asks Accetta / Modifica / Rivedi completamente / Tieni in considerazione,
  and applies on Accetta without committing.
  Auto-detects article language (it/en) and adapts
  the proposal style accordingly. Out of scope: writing the article from
  scratch (use the journal-specific style skill, e.g. `praxis-article-style`),
  managing the `.bib` directly (use `praxis-bibliography-citations` or its
  equivalent).
---

# Article Revision Skill `artr`

Operational layer that orchestrates the existing article-style and
bibliography skills around a structured revision workflow.

## Slash Commands

| Command | Action |
|---|---|
| `/article-revision` | Full revision workflow from reviewer feedback |
| `/r-pp` | **Revisione Paragrafo per Paragrafo** — walk every paragraph sequentially; for each, the AI checks paragraph unity, clarity, connection, style/citations, then proposes modifications; at chapter boundaries it recaps coherence and organization |
| `/r-pp-a` | **Revisione Paragrafo per Paragrafo Approfondita** — as `/r-pp` but with deep AI analysis (unitary concept, logic, structure, style, citations, norms) before proposing |
| `/r-pr-2` | **Revisione Due Peer Reviewer** — simulate two independent peer reviewers; generate Standalone reviewer documents in `revisions/<article-slug>/` without interactive decision loop; the documents feed subsequent revision passes |
| `/r-conn` | **Revisione Connettori** — analyse and polish logical connectors, transitions, and signposting between paragraphs and sections |
| `/r-global` | **Revisione Globale** — high-level, non-granular revision: overall structure, argument coherence, section proportionality, redundancy, terminology consistency; can also save a global trace for `/r-pp` |
| `/r-freeze` | **Congela** una parte conclusa (paragrafo/sezione/frammento) nel freeze ledger; in seguito la skill avvisa prima di toccarla (`workflow/15-freeze-ledger.md`) |
| `/r-thaw` | **Scongela** una parte congelata: torna modificabile senza avviso (`workflow/15-freeze-ledger.md`) |
| `/r-status` | **Stato revisione** — mappa di cosa è concluso (🟢 frozen) e cosa richiede intervento (🟡 open), dal freeze ledger (`workflow/15-freeze-ledger.md`) |
| `/r-handoff` | **Handoff** — scrive checkpoint, decision log, sync current files e commit scoped senza chiudere la revisione (`workflow/06-handoff.md`) |
| `/r-resume` | **Resume** — riprende da un task file sospeso senza nuovo bump (`workflow/06-handoff.md`) |
| `/r-bump` | Bump article version (call `workflow/60-bump-version.md`) |
| `/r-sheet` | Generate final revision sheet (call `workflow/70-final-sheet.md`) |
| `/r-chapter` | **Revisione Capitolo** — revisiona una singola sezione in relazione al resto dell'articolo: terminologia, cross-riferimenti, filo argomentativo, ridondanze, interfacce di sezione (`workflow/36-chapter-revision.md`) |
| `/r-gdrive` | **Google Drive Collaboration** — create/sync a shared Drive folder for colleagues; pull their feedback back as a revision source (`workflow/80-gdrive-collab.md`) |
| `/r-approve` | **Colleague Approval** — gate accepted modifications behind colleague sign-off (Google Doc suggestions or `approvals.md`) before they count as final (`workflow/35-colleague-approval.md`) |
| `/r-redline` | **Redline Export** — colored old-vs-new manuscript for the journal reviewer (insert = green/underline, delete = red/strikethrough) + response-to-reviewers letter (`workflow/90-redline-export.md`) |
| `/r-guide` | **Recommended Guide** — read-only recommended full revision path: TOV, global analysis, paragraph pass, chapter handoffs, simulated reviewers (`workflow/98-guide.md`) |
| `/r-help` | **Aiuto** — scheda di riferimento con tutti i comandi e le scorciatoie decisionali; read-only, nessun setup o bump (`workflow/99-help.md`) |

### Paragraph-by-Paragraph Modes (`/r-pp`, `/r-pp-a`)

These modes perform a **proactive** revision walk over the entire article, paragraph by paragraph. The AI actively analyzes each paragraph using multiple diagnostic dimensions before proposing changes. Unlike the standard reviewer-feedback flow, this is not reactive to external feedback — it's an autonomous diagnostic process. At the end of each chapter, the AI must recap whether the paragraphs are organized clearly and coherently before advancing.

#### `/r-pp` — Standard Paragraph-by-Paragraph

For each paragraph in sequence:

1. **Show** the paragraph with context (preceding paragraph + current paragraph).
2. **Analyze** the paragraph using four standard diagnostic dimensions (adapted to `ARTICLE_LANG`):

    | # | IT | EN |
    |---|---|---|
    | Q1 | Il paragrafo esprime un concetto unitario, cioè un'idea declinata in parti coerenti, o contiene più idee autonome? | Does the paragraph express one governing concept, developed in coherent parts, or multiple autonomous ideas? |
    | Q2 | L'argomento è chiaro e completo? | Is the argument clear and complete? |
    | Q3 | Il paragrafo si collega bene al precedente? | Does it connect well to the previous paragraph? |
    | Q4 | Ci sono problemi di stile, registro o citazioni? | Any issues with style, register, or citations? |

3. **Propose** modifications based on the AI's analysis, using the standard decision pattern.
4. After decision on each proposal, ask: *"Ci sono altri cambiamenti in questo paragrafo?"* before advancing.
5. At the end of each chapter, recap the chapter's unitary-concept map, paragraph progression, transitions, redundancies, and overall coherence before moving on.
6. **Advance** only on explicit command (`prossimo`, `next`, `passa al prossimo`).

The user can pause with `pause`, `stop`, or `/r-handoff`; the skill records the
current paragraph via `workflow/06-handoff.md` and later resumes with
`/r-resume` without a new bump.

#### `/r-pp-a` — Deep Paragraph-by-Paragraph

As `/r-pp`, but with an **extended AI analysis** before proposing. For each paragraph, the AI analyzes six layered dimensions:

| # | IT | EN |
|---|---|---|
| Q1 | Il paragrafo ha un solo concetto guida, anche se articolato in più parti, o fonde idee autonome? | Does the paragraph have one governing concept, even if developed in several parts, or does it merge autonomous ideas? |
| Q2 | L'argomento è logicamente completo? Mancano passaggi? | Is the argument logically complete? Any missing steps? |
| Q3 | La struttura interna funziona? (topic sentence, sviluppo, chiusura) | Does the internal structure work? (topic sentence, development, closure) |
| Q4 | Il tono e il registro sono appropriati alla rivista? | Is the tone and register appropriate for the journal? |
| Q5 | Ogni affermazione è supportata da una citazione? Le citazioni sono formattate correttamente? | Is every claim backed by a citation? Are citations correctly formatted? |
| Q6 | Il paragrafo rispetta le norme editoriali? (limiti, stile, terminologia) | Does the paragraph respect the editorial norms? (limits, style, terminology) |

After the AI completes its analysis, it synthesises the findings into a unified proposal block, numbering each modification by diagnostic category. The user may decide by category (e.g. `Accetta struttura`, `Modifica citazioni: <direzione>`, `Tieni in considerazione tono: <nota>`).

### `/r-pr-2` — Standalone Dual Peer Review (Document Generation)

This mode simulates two independent peer reviewers with distinct personas and writes their reports as standalone Markdown documents in `revisions/<article-slug>/`. It does **not** run an interactive decision loop — the documents become input for subsequent revision passes (`/r-pp-a`, `/r-pp`, `/r-global`, `/r-conn`).

| Reviewer | Persona | Focus |
|---|---|---|
| **Reviewer A** | Rigorous, method-focused | Methodology, data, internal validity, statistics |
| **Reviewer B** | Broad-view, theory-focused | Literature positioning, argument coherence, contribution clarity, writing quality |

**Output files** (written to `revisions/<article-slug>/`):

| File | Content |
|---|---|
| `reviewer-a-vN.md` | Full Reviewer A report: per-section comments, flagged issues, overall assessment |
| `reviewer-b-vN.md` | Full Reviewer B report: per-section comments, flagged issues, overall assessment |
| `peer-review-synthesis-vN.md` | Convergence/divergence analysis, unified proposal with [A]/[B]/[A+B] tags |

**Workflow:**

1. **Setup** — Run `10-setup.md` (including mandatory bump). Load the full article.
2. **Parse** — Split article into sections by heading level (`§1`, `§2`, ...).
3. **Generate Reviewer A** — Section by section, apply the Methodologist persona. Write `reviewer-a-vN.md` with: per-section numbered comments, flagged issues (reproducibility, validity, statistical concerns), and an overall assessment with priority ranking.
4. **Generate Reviewer B** — Section by section, apply the Theoretician persona. Write `reviewer-b-vN.md` with: per-section numbered comments, flagged issues (literature positioning, argument coherence, contribution clarity), and an overall assessment with priority ranking.
5. **Synthesise** — Compare both reports. Classify each observation as Convergent (C: both agree), Divergent (D: they disagree), or Independent (I: one reviewer only). Write `peer-review-synthesis-vN.md` with: convergence matrix per section, unified proposal with modifications tagged [A], [B], or [A+B], and a priority-ordered action list.
6. **Notify** — Output a one-page summary in chat: section count, convergent/divergent/independent counts, top-priority [A+B] items, file paths. The user then decides which revision command to run next.

**No interactive decision loop.** The synthesis document lists modifications with tags but does NOT apply them. The user triggers application later via `/r-pp-a`, `/r-pp`, `/r-global`, or `/r-conn`, referencing the synthesis document.

### `/r-conn` — Connector Revision

A focused pass that examines the article's **logical scaffolding**: connectors, transition phrases, and signposting language. This mode does **not** rewrite content — it only adjusts the connective tissue between paragraphs and sections.

**Scope:**
- Inter-paragraph transitions (last sentence of P<N> → first sentence of P<N+1>)
- Inter-section transitions (closing paragraph of §<N> → opening paragraph of §<N+1>)
- Logical connectors within paragraphs (`therefore`, `however`, `moreover`, `in contrast`, `consequently`, `first`/`second`/`finally`)
- Signposting language (`as discussed above`, `as we will see in §3`, `to summarise`)
- Missing connectors where the logical relationship is implicit but should be explicit
- Overused connectors (e.g. five `however` in one page)

**IT connector reference table** (used when `ARTICLE_LANG=it`):

| Logical relation | Preferred connectors | Avoid (weak/ambiguous) |
|---|---|---|
| Causa/effetto | *pertanto*, *di conseguenza*, *ne deriva che* | *quindi* (overused), *dunque* (informal) |
| Contrasto | *tuttavia*, *ciononostante*, *al contrario* | *ma* (paratactic, weak at paragraph start) |
| Aggiunta | *inoltre*, *per di più*, *si aggiunga che* | *e* (paratactic), *anche* (ambiguous scope) |
| Esemplificazione | *per esempio*, *si consideri*, *è il caso di* | *tipo*, *come* (colloquial) |
| Riformulazione | *in altri termini*, *vale a dire*, *ossia* | *cioè* (acceptable but informal) |
| Concessione | *sebbene*, *benché*, *per quanto* | *anche se* (acceptable in some journals) |
| Ordine/sequenza | *in primo luogo*, *in secondo luogo*, *infine* | *prima... poi...* (narrative, not academic) |
| Riepilogo | *in sintesi*, *complessivamente*, *in definitiva* | *per farla breve* (colloquial) |
| Rinvio interno | *come discusso in §X*, *si veda supra*, *come vedremo* | *come detto prima/dopo* (vague) |

**EN connector reference table** (used when `ARTICLE_LANG=en`):

| Logical relation | Preferred connectors | Avoid |
|---|---|---|
| Cause/effect | *therefore*, *consequently*, *as a result*, *thus* | *so* (informal), *hence* (archaic in some fields) |
| Contrast | *however*, *nevertheless*, *in contrast*, *conversely* | *but* (weak at sentence start) |
| Addition | *moreover*, *furthermore*, *in addition* | *and* (paratactic), *also* (vague) |
| Exemplification | *for example*, *for instance*, *consider* | *like* (colloquial) |
| Reformulation | *in other words*, *that is*, *namely* | *i.e.* (acceptable, prefer full form) |
| Concession | *although*, *even though*, *while* | *despite* (needs noun phrase) |
| Sequencing | *first*, *second*, *finally* | *firstly*, *secondly* (debated; follow journal norms) |
| Summary | *in summary*, *overall*, *to conclude* | *to wrap up* (colloquial) |
| Internal reference | *as discussed in §X*, *see above*, *as we will show* | *as said before* (vague) |

**Workflow:**

1. **Parse** the article into paragraphs, chapters, and sections; every paragraph gets the locator `Capitolo <C> — <title>; P<N> — <file>:<L1-L2>`.
2. **Extract** every paragraph boundary (last sentence of `P<N> — <file>:<L1-L2>` + first sentence of `P<N+1> — <file>:<L3-L4>`) into a list, preserving both paragraph line ranges.
3. **Extract** every section boundary (last paragraph of §<N> + first paragraph of §<N+1>).
4. **Diagnose** each boundary: is the logical relationship explicit? Is the connector appropriate?
5. **Present** findings as a diagnostic table, not one by one — the user gets a bird's-eye view:

   ```
   ## Connector Diagnostic — <article>

   ### Inter-paragraph transitions

   | Transition | Logical relation | Current connector | Issue | Proposal |
   |---|---|---|---|---|
   | P3 (cap. 1, righe 42-48) → P4 (cap. 1, righe 50-56) | Contrast | *ma* | Weak at paragraph start | *Tuttavia* |
   | P7 (cap. 2, righe 88-96) → P8 (cap. 2, righe 98-105) | Cause/effect | (missing) | Implicit → needs connector | *Di conseguenza* |
   | P12 (cap. 3, righe 145-153) → P13 (cap. 3, righe 155-162) | Addition | *inoltre* | OK | — |

   ### Inter-section transitions

   | Transition | Logical relation | Current state | Issue | Proposal |
   |---|---|---|---|---|
   | §2→§3 | Sequence | (missing) | Abrupt topic shift | Add signposting line |
   | §4→§5 | Summary + preview | OK | — | — |

   ### Overused connectors

   | Connector | Count | In paragraphs | Recommendation |
   |---|---|---|---|
   | *tuttavia* | 7 | P2 (20-25), P4 (50-56), P5 (58-64), P9 (110-116), P11 (132-139), P14 (170-176), P18 (220-228) | Reduce to max 3; rephrase 4 |
   ```

6. **Ask** the user to select which transitions to fix: *"Quali transizioni vuoi sistemare? (es. 'P3 righe 42-48 → P4 righe 50-56', 'P7 righe 88-96 → P8 righe 98-105', '§2→§3' oppure 'tutte')"*
7. **Propose** modifications for the selected items using the standard decision pattern (one point per transition group).
8. **Apply** on `Accetta`, advance on command.

Each `[Overused]` item becomes a separate proposal asking to rephrase *N* occurrences. The user can specify which occurrences to keep and which to replace.

### `/r-global` — Global / Holistic Revision

A **non-granular, high-level** revision that examines the article as a whole organism. This mode does not descend into sentence-level edits — it operates at the structural, argumentative, and narrative level. After the diagnostic report, the user can either request structural decision proposals or save the report as a persistent trace for `/r-pp` / `/r-pp-a`.

**The seven lenses of global revision:**

| # | Lens | Key question |
|---|---|---|
| 1 | **Thesis clarity** | Is the contribution/tesi stated explicitly and early? Is it falsifiable? |
| 2 | **Argument architecture** | Does the sequence of sections build a coherent argument? Are there logical leaps or missing steps? |
| 3 | **Section proportionality** | Are some sections bloated and others skeletal? Does the weight match the importance? |
| 4 | **Narrative arc** | Does the article tell a compelling story? Intro → gap → method → findings → implications → conclusion? |
| 5 | **Redundancy** | Are the same points made in multiple sections? Are there near-duplicate paragraphs? |
| 6 | **Terminology consistency** | Is the same concept called by the same name throughout? Are key terms defined once and used consistently? |
| 7 | **Norm alignment** | At the macro level, does the article structure match journal expectations? (e.g. IMRaD, theoretical→empirical→discussion) |

**Workflow:**

1. **Read** the full article into context.
2. **Generate** a structured diagnostic report applying all seven lenses. This is presented as a single document — the user reviews the whole picture before any edits:

   ```
   ## Revisione Globale — <article>

   ### 1. Thesis clarity
   - **Dov'è la tesi?** §1, riga X: «<quote>»
   - **È esplicita?** Sì / Parzialmente / No
   - **È falsificabile?** Sì / No — <perché>
   - **Raccomandazione:** <what to adjust>

   ### 2. Argument architecture
   - **Mappa argomentativa:**
     §1: <role in argument>
     §2: <role in argument>
     §3: <role in argument>
     → §4: <gap: missing transition between method and findings>
     §5: <role in argument>
     §6: <role in argument>
   - **Salti logici:** <list>
   - **Passaggi mancanti:** <list>

   ### 3. Section proportionality
   | Section | Chars | % of total | Recommended | Status |
   |---|---|---|---|---|
   | §1 Intro | 3200 | 12% | 10-15% | OK |
   | §2 Literature | 8200 | 31% | 15-20% | ⚠️ Overweight |
   | §3 Method | 4100 | 16% | 15-20% | OK |
   | §4 Results | 5200 | 20% | 20-25% | ⚠️ Slightly under |
   | §5 Discussion | 4100 | 16% | 20-25% | ⚠️ Under |
   | §6 Conclusion | 1400 | 5% | 5-10% | OK |

   ### 4. Narrative arc
   - **Apertura:** <evaluation>
   - **Tensione:** <evaluation — does the gap motivate the study?>
   - **Climax:** <evaluation — do the findings deliver?>
   - **Risoluzione:** <evaluation — does the conclusion close the loop?>
   - **Raccomandazione:** <high-level direction>

   ### 5. Redundancy
   - **Paragrafi quasi-duplicati:** P12 (Capitolo 3, articles/current.md:145-153) ~ P28 (Capitolo 5, articles/current.md:310-318) (both define the dependent variable)
   - **Argomenti ripetuti:** The limitation about sample size appears in §3, §5, and §6
   - **Raccomandazione:** <which to consolidate>

   ### 6. Terminology consistency
   | Termine | Definizione in | Usato anche come | Issue |
   |---|---|---|---|
   | *emotional labour* | §2, riga 45 | *emotional work* in §4, riga 12 | Inconsistente |
   | *self-efficacy* | §2, riga 78 | — | OK |

   ### 7. Norm alignment
   - **Struttura attesa:** IMRaD
   - **Struttura effettiva:** Intro → Literature → Hypotheses → Method → Results → Discussion → Conclusion
   - **Scostamenti:** Literature section longer than journal norm; hypothese section is a separate heading (journal expects them embedded in intro)
   - **Raccomandazione:** <what to adjust>

   ---
   **Azioni suggerite:** N interventi strutturali, M interventi di superficie.
   Come vuoi usare questo report?
   - "tutte" / "solo architettura" / "proporzioni + terminologia" → genero proposte decisionali
   - "traccia per /r-pp" → salvo il report come guida globale per la revisione paragrafo per paragrafo
   - "nessuna" → nessuna modifica
   ```

3. **Wait** for the user to choose how to use the report.
4. If the user chooses `traccia per /r-pp`, ask before creating
   `revisions/<article-slug>/sources/global-trace-<bumped-version>.md`, then
   save the seven-lens report with a section/priority map. This does not modify
   the article; it becomes diagnostic context for later `/r-pp` and `/r-pp-a`.
5. If the user selects lenses to act on, generate one or more revision points
   using the standard decision pattern. Each point addresses a specific structural issue
   (e.g. "Cut §2 from 8200 to 5000 chars", "Rename 'emotional work' →
   'emotional labour' globally").
6. **Apply** on `Accetta`. For structural changes (reordering, cutting), the skill edits the article with surgical precision. For global renaming, use `replaceAll`.
7. **Advance** on explicit command.

This mode is designed to be run **before** granular revision (`/r-pp`, standard reviewer feedback): either fix the architecture first, or save the architecture diagnosis as a trace so paragraph-level revision keeps the global argument in view.

## Authority

Editorial rules in priority order:

1. The journal's editorial norms file referenced by `EDITORIAL_NORMS_PATH`
   in `.env` (binding for the article).
2. The journal-specific style skill installed in the project (e.g.
   `praxis-article-style`), if any.
3. This skill — operational orchestration only.

When norms and user preference conflict, **norms win**. Surface the
conflict explicitly in chat.

## Feedback provenance

Every revision round carries a `Feedback source`, set in `20-plan-revision.md`
and stored in the project file and final sheet:

- `journal` — a real reviewer/editor round. Its points feed the response
  letter; corrected figures must be disclosed there.
- `simulated` — produced internally (`/r-pr-2`, self-review). Internal QA
  only. `/r-pr-2` documents carry `source: simulated` in frontmatter and are
  read, not re-asked. Never present simulated feedback to the journal as
  external review. `70-final-sheet.md` keeps it out of the response letter.

Mixed rounds (a self-review layered on a real round) are split by tag: only
`journal` points become response-letter material.

## Data verification (binding)

A numeric claim is never inherited. Whenever a proposal adds, changes, or
relies on a percentage, count, mean, index, correlation, rank, or a
qualitative claim that holds only if a figure holds, `30-iterate-points.md`
must run `51-data-verification.md` **before** proposing: re-derive the figure
from the authoritative source (`DATA_VERIFY_PATH` / `DATA_VERIFY_NOTES`, or a
data-source section in the project's `AGENTS.md`), with an explicit criterion
(column, filter, denominator, regex with word boundaries). If no source
reproduces the value, the point is `Deferred` — never replaced with a
plausible number. Skipping this when a figure is in scope is a binding
violation, same severity as an unauthorized auto-commit.

## Freeze ledger (advisory, persistent)

The skill keeps one **freeze ledger** per article at
`revisions/<article-slug>/freeze-ledger.md` — the single artifact that always
answers: *which parts are concluded and good (🟢 frozen), which still need work
(🟡 open), and what we intend to change about them.* It persists across version
bumps and sessions; see `workflow/15-freeze-ledger.md`.

Binding rules:

- **Check before proposing.** Every interactive revision workflow
  (`30`, `31`, `33`, `34`, `36`) reads the ledger before touching a unit.
- **Frozen is advisory, not silent-skip.** A proposal may still touch a 🟢 frozen
  unit, but the skill must first warn (`⚠ questa parte è congelata`) and get an
  explicit confirmation (`sì, procedi`) in the same turn before applying. Without
  confirmation, leave it frozen and advance.
- **Track intentions, don't lose them.** Whenever the user states something to
  change but the change is not applied this turn, record it in the ledger
  (`log-comment`): the unit becomes 🟡 open with the intention written down. Chat
  is not memory — the ledger is.
- **Offer to freeze on conclusion.** When a unit's work concludes and the user
  signals no further changes on it, the skill offers to freeze it before
  advancing (once per unit per session). `/r-freeze` freezes on demand.
- **Carry forward on bump.** `60-bump-version.md` re-anchors the ledger to the
  new version by incipit; a unit whose anchor no longer matches is flagged
  `⚠ stale`, never dropped silently.

Freezing is a project-record convenience, not a git operation. It changes the
ledger only — never the article and never the repository state.

## Project layout (required)

```
<project-root>/
├── .env
├── articles/                         # or any directory; auto-detected
│   ├── article-vN-YYYY-MM-DD[-anonymous].md
│   ├── current.md                    # always the active version (synced by 96-sync-current)
│   └── current.docx                  # Word export of current.md
├── bibliography/
│   ├── reference.bib
│   └── bibliography.docx             # formatted reference list (synced by 96-sync-current)
├── editorial-norms/
│   ├── <journal-norms>.md
│   ├── reference.docx                # optional: pandoc reference doc for journal layout
│   └── <style>.csl                   # optional: CSL file for citation formatting
├── data/                             # optional, for sample stats
└── revisions/
    ├── <article-slug>/
    │   └── freeze-ledger.md          # persistent: frozen vs open parts + intentions
    ├── <reviewer-name>/
    │   ├── revision-plan-vN.md
    │   ├── proposal-revision-YYYY-MM-DD-HHMM.md
    │   ├── final-sheet-vN.md
    │   └── task-<cmd>-<version>.md   # per-session task file
    └── decision-log/
        ├── index.md
        └── session-NNN.md
```

If any of these is missing, the skill asks the user to confirm an
alternative path or to create it. Never invent paths silently.

## `.env` contract

Required:

- `EDITORIAL_LIMIT_CHARS` — hard char cap (e.g. `40000`).
- `EDITORIAL_NORMS_PATH` — relative path to the norms file.
- `BIBLIOGRAPHY_BIB_PATH` — relative path to `reference.bib`.

Optional:

- `EDITORIAL_LIMIT_WORDS` — alternative to chars, if the journal uses words.
- `ARTICLE_LANG` — forces language detection (`it`, `en`, …).
- `ARTICLE_STYLE_NOTES` — extra style notes to load.
- `PYTHON_BIN` — Python interpreter for skill scripts. Defaults to
  `<project-root>/.venv/bin/python` after bootstrap. If no venv exists, ask the
  user before creating one or falling back to system Python.
- `CROSSREF_USER_AGENT` — for `bib_verify_online.py`.
- `OPENALEX_USER_AGENT` — same.
- `ZOTERO_USER_ID`, `ZOTERO_API_KEY`, `ZOTERO_GROUP_ID` — Zotero integration.
- `DATA_VERIFY_PATH` — root of the authoritative dataset/platform for the
  article's empirical figures. Enables `workflow/51-data-verification.md` to
  re-derive numeric claims instead of inheriting them.
- `DATA_VERIFY_NOTES` — free-text pointer to the master file, key column, and
  formula location within `DATA_VERIFY_PATH`.
- `GDRIVE_REVIEW_FOLDER_ID` — shared Drive folder id for `/r-gdrive`
  (written back after `create`; reused to avoid duplicate folders).
- `RCLONE_REMOTE`, `GDRIVE_PATH` — only for the rclone fallback of
  `/r-gdrive` when the MCP Drive connector is unavailable.
- `AUTO_BUMP_THRESHOLD` — number of accepted changes that triggers a mid-session
  bump proposal. Default: `5`.

## Python execution contract

- All Python scripts must run through the project virtual environment:
  `<project-root>/.venv/bin/python`.
- On first invocation, if `.venv/` is missing, ask whether to create it and
  install `.claude/skills/article-revision/requirements.txt`.
- If the user refuses venv creation, ask whether system Python may be used for
  this session. Never fall back to `python3` silently.
- Remember the selected interpreter as `PYTHON_BIN` for the session; append it
  to `.env` only with explicit user confirmation.
- Shell scripts may run directly, but any Python they invoke must use
  `PYTHON_BIN` or the venv interpreter.

## Workflow files (must be followed in order on first invocation)

0. `workflow/05-task.md` — per-session task file lifecycle (create, update-step,
   handoff, resume, close). Called by setup, handoff/resume, and closure.
   Stores the running step list and produces the session summary for the
   decision log.
0a. `workflow/06-handoff.md` — resumable checkpoint and resume workflow. Called
   by `pause`, `stop`, `/r-handoff`, `/r-resume`, or whenever the agent may be
   interrupted before natural closure. A handoff writes a checkpoint, decision
   log entry, current-file sync, and scoped commit without closing the round.
1. `workflow/00-bootstrap.md` — set up the revision environment if missing
   (venv with Python deps, `.bib` file, `.env` with editorial parameters
   and Zotero credentials, editorial norms file). Idempotent: skips
   anything already in place.
2. `workflow/10-setup.md` — load `.env`, norms, bib, current article version,
   detect article language.
2a. `workflow/15-freeze-ledger.md` — ensure the per-article freeze ledger exists
   and is reconciled to the bumped version (`ensure`). Thereafter it governs the
   advisory check before every proposal and records frozen/open units and their
   intentions. Also drives `/r-freeze`, `/r-thaw`, `/r-status`.
3. `workflow/20-plan-revision.md` — accept reviewer feedback, generate
   `revisions/<reviewer>/revision-plan-vN.md` from the template, with
   each point in `To decide` state.
4. `workflow/30-iterate-points.md` — for each point, propose, ask
   `Accetta / Modifica / Rivedi completamente / Tieni in considerazione`, apply on `Accetta`. **Never commit
   automatically** — the user controls git.
4a. `workflow/31-paragraph-by-paragraph.md` — triggered by `/r-pp` or
    `/r-pp-a`. Walk every paragraph sequentially with AI diagnostic analysis
    before proposing; each paragraph must carry chapter and line-range
    locators, each paragraph must have one governing concept, and each chapter
    gets a coherence recap before advancing. Deep mode (`/r-pp-a`) uses
    six-layer diagnostics.
4b. `workflow/32-peer-review-simulation.md` — triggered by `/r-pr-2`.
   Generate two standalone reviewer documents in `revisions/<article-slug>/`
   (method-focused, theory-focused) plus a synthesis document. No interactive
   decision loop — the documents feed subsequent revision passes.
4c. `workflow/33-connector-revision.md` — triggered by `/r-conn`.
   Analyse and polish logical connectors, transitions, and signposting
   between paragraphs and sections. Does not rewrite content.
4d. `workflow/34-global-revision.md` — triggered by `/r-global`.
   High-level, non-granular revision across seven lenses: thesis clarity,
   argument architecture, section proportionality, narrative arc,
   redundancy, terminology consistency, norm alignment. Can save the report as
   `revisions/<slug>/sources/global-trace-*.md` for later `/r-pp` / `/r-pp-a`.
4e. `workflow/36-chapter-revision.md` — triggered by `/r-chapter`. Revises a
   single section at paragraph depth while checking it against the rest of the
   article across six cross-article dimensions: terminology, cross-references,
   section interfaces, redundancy, argument thread, norms compliance.
5. `workflow/40-bibliography-check.md` — when a citation is touched or new
   keys are introduced.
6. `workflow/50-sample-description.md` — when the methodology asks for a
   sample-description update from raw data.
6a. `workflow/51-data-verification.md` — when a proposal adds, changes, or
   relies on a numeric claim (percentage, count, mean, index, correlation,
   rank, or a qualitative claim contingent on a figure). Re-derive from the
   authoritative source; never inherit from a prior version or a reviewer's
   wording. Binding, not optional.
7. `workflow/60-bump-version.md` — when the user signals end of revision
   round, or when accepted modifications since the last version exceed
   `AUTO_BUMP_THRESHOLD` (default 5); the skill **proposes** a bump,
   never forces it. New filename: `article-v(N+1)-YYYY-MM-DD-HHMM.md`
   (date + 24h time, so multiple bumps in the same day stay distinct).
8. `workflow/70-final-sheet.md` — produce `revisions/<reviewer>/
   final-sheet-vN.md` with the post-revision status.
9. `workflow/95-decision-log.md` — mandatory decision-log step. Record the round in
   `revisions/decision-log/` and update `index.md`, close the task file, then
   call `96-sync-current.md`. Also supports `mode=handoff`, where it records a
   checkpoint without closing the task. The round is not closed until all three
   closure-mode steps complete.
10. `workflow/96-sync-current.md` — mandatory sync step (called by 95). Overwrites
   `articles/current.md`, `articles/current.docx`, and
   `bibliography/bibliography.docx`. Requires pandoc; uses `--citeproc` and
   `nocite: @*` for the bibliography export, then warns if the generated
   bibliography docx is missing or appears empty. Skips `.docx` exports only if
   pandoc is absent.

Collaboration / delivery steps (run on demand, not in fixed order):

- `workflow/35-colleague-approval.md` — triggered by `/r-approve`. Gates
  `Accepted` points behind colleague sign-off (Google Doc suggestions or
  structured `approvals.md`) before they count as final.
- `workflow/80-gdrive-collab.md` — triggered by `/r-gdrive`. Create/sync a
  shared Drive folder (MCP connector, rclone fallback); pull colleague
  feedback into `revisions/<slug>/sources/` as a revision source. The skill
  never adds collaborators — the user shares the folder in the Drive UI.
- `workflow/90-redline-export.md` — triggered by `/r-redline`. Colored
  old-vs-new manuscript for the reviewer (`scripts/make_redline.py`) plus
  the point-by-point response letter. The redline is a **separate**
  deliverable; the clean submission file carries no revision marks.
- `workflow/98-guide.md` — triggered by `/r-guide`. Prints the recommended
  full revision path. Standalone and read-only: no bootstrap, no setup, no bump,
  no file I/O.
- `workflow/99-help.md` — triggered by `/r-help`. Prints the command reference
  card. Standalone and read-only: no bootstrap, no setup, no bump, no file I/O.

Skipping is allowed if a step is not applicable; never silently skip a
step that *should* run.

## Filename provenance rule

When the active article filename contains `-drive` before `.md`, that token
marks a file downloaded from Google Drive. It is provenance metadata, not part
of the canonical version name. The revision workflow may use that file as the
source, but any version bump must remove `-drive` and generate the canonical
filename `article-v(N+1)-YYYY-MM-DD-HHMM[-anonymous].md`.

## Paragraph and Chapter Locators (binding)

Every time the skill identifies, discusses, stores, freezes, resumes, or
proposes an edit for a paragraph, it must include a full locator:

`Capitolo <C> — <chapter title>; Paragrafo P<N> — <ARTICLE_PATH>:<L1-L2>`

- **Paragraph**: a semantic body block delimited by blank lines, excluding
  headings, blockquotes, code blocks, and tables unless a workflow explicitly
  says otherwise. `L1-L2` is the inclusive line range in the current Markdown
  article file.
- **Chapter**: a numbered Markdown heading with a number and a title. Determine
  the chapter from the first numeric component of the heading text: `1`,
  `1.1`, and `1.2.3` all belong to `Capitolo 1`; `2` or `2.1` starts
  `Capitolo 2`. When the first number changes, the chapter changes.
- **Section/subsection**: the nearest full heading path may still be shown as
  `§...`, but it must not be confused with the chapter. A subsection `1.2`
  remains inside `Capitolo 1`.
- If headings are unnumbered or numbering is inconsistent, warn and use the
  nearest heading as provisional context; still include paragraph line ranges.
- Recompute paragraph line ranges after edits and version bumps before writing
  handoff, freeze-ledger, task, proposal, or summary entries.

## Interaction pattern (binding)

For every revision point, output exactly this shape in chat:

```
## Point N — <short title> · scope: <fragment|paragraph|whole article>

**Unità**: <Capitolo C — title; Paragrafo P<N> — article:line-range> <!-- required when a paragraph is referenced -->

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

Then **wait** for the user. Do not pre-emptively apply.

If a single point contains **more than one numbered modification**, the skill
must also write a companion file to disk before waiting for the user:

`revisions/<reviewer>/proposal-revision-YYYY-MM-DD-HHMM.md`

The file mirrors the exact proposal shown in chat and acts as the proposal to
follow during the subsequent decision loop. It must include:

- the reference article path and current version;
- timestamp;
- point title and scope;
- original text;
- full proposed text;
- numbered modifications;
- current status: `proposed`.

Each modification within a paragraph is numbered, so the user can decide individual changes with precision:
- `Accetta 1,3` → apply modifications 1 and 3 only.
- `Modifica 4: <direzione>` → regenerate modification 4 as specified.
- `Rivedi completamente: <direzione>` → regenerate the whole proposal.
- `Tieni in considerazione 2: <nota>` → do not apply modification 2 now; record it as deferred/context.

Optional shortcuts remain accepted for speed:
`A = Accetta`, `M = Modifica`, `R = Rivedi completamente`, `T = Tieni in considerazione`.

### Auto-mode

Auto-mode must be **explicitly requested** by the user (e.g. "attiva auto-mode", "automatico", "continua senza chiedere"). It is **never** the default.

When auto-mode is active:

1. The skill runs the same diagnostic and proposal cycle for each paragraph.
2. Each modification is **presented in chat** using the standard format above.
3. After presenting, the skill **automatically applies** the modification (implicit `Accetta`) and advances to the next.
4. The skill **never waits** for user input between paragraphs.
5. Only the following cases require pausing and asking the user:
   - Ambiguous or conflicting information that cannot be resolved from context
   - A modification with `risk: high` (structural change, potential loss of content)
   - A modification that requires a decision between two valid alternatives
   - End of chapter or end of article (report summary, then ask whether to
     continue or write a handoff checkpoint)
6. At the end of each chapter, output the chapter recap from
   `workflow/31-paragraph-by-paragraph.md`: unitary-concept map, organization,
   coherence, transitions, redundancies, and any issue to address before
   advancing. Include the auto-mode counts in that recap:

```
[Auto-mode] §<N> completato: X modifiche applicate, Y saltate. Recap: <clear|issues>.
```

7. At the end of the full revision, output a final summary:

```
[Auto-mode] Revisione completata: N sezioni, M modifiche applicate, K saltate.
```

To **deactivate** auto-mode without suspending the round, the user says
"manual", "manuale", or "ferma auto-mode". The skill resumes the standard
interactive decision pattern from the current paragraph. If the user simply says
`stop`, `pause`, or `sospendi`, treat it as `workflow/06-handoff.md`.

### After applying changes

Once modifications are applied, **do not advance** to the next point automatically. Instead, output:

```
Applicate modifiche <numeri>. [Restano in sospeso le modifiche <numeri>.] Ci sono altri cambiamenti da fare in questo paragrafo?
```

And **wait** for an explicit command from the user (e.g. "Accetta 1,3", "Modifica 5: ...", "no, prossimo paragrafo", "passa al prossimo").

When the user signals no further changes on the unit and asks to advance, run
the freeze auto-offer (`15-freeze-ledger.md` §7) **before** moving on: offer to
freeze the concluded unit, or — if the user named something still to do — record
the intention in the ledger (`log-comment`). Then advance.

### Handling responses

- `Accetta` (with selected numbers) → apply via Edit only the numbered modifications. Mark applied modifications as `Accepted` in the project file. Increment the *accepted-since-last-bump* counter. **Do not commit.** When the counter reaches `AUTO_BUMP_THRESHOLD`, suggest a version bump (see step 7). Ask for further changes on the same paragraph.
- Every decision interaction must be compatible with the project's
  `decision-log` skill. At the end of the revision round, `95-decision-log.md`
  is mandatory: the round must always be logged, even if the final outcome is
  partial or deferred.
- `Modifica <N>: <direzione>` → regenerate modification N according to the user's direction. Re-present the updated modification with the same numbering. Repeat until accepted or deferred.
- `Rivedi completamente: <direzione>` → regenerate the whole proposal from the original text. Do not edit the article until the user later chooses `Accetta`.
- `Tieni in considerazione <N>: <nota>` → annotate those modifications as `Deferred` + note. No file edits for them. Record the note in the freeze ledger if it names a future intention.
- Silent advance to the next point only when the user gives an explicit command (e.g. "no, prossimo", "passa al prossimo paragrafo", "next").

If the proposal involves multiple separate edits (e.g. an inline citation + a bibliography entry), still present them as numbered modifications within a single coherent block, allowing the user to accept each independently.

## Language auto-detection

In `workflow/10-setup.md`:

1. Skip frontmatter (lines between leading `---`).
2. Read up to 1,000 chars of body text.
3. Score language by function words for the candidate languages.
4. Highest score wins; ties → fallback to `langdetect` if installed, else ask the user.
5. Persist to memory for the session as `ARTICLE_LANG`.

Override via `.env` `ARTICLE_LANG=...` always wins over auto-detection.

If `ARTICLE_LANG=it`, anglicisms in proposals must come from `templates/accepted-anglicisms-it.md`. Surface any new anglicism in the proposal block under "Possible exceptions".

## Style of generated proposals

| `ARTICLE_LANG` | Proposal language | Notes |
|---|---|---|
| `it` | Italian, formal academic register | Anglicisms only when established convention; see `templates/accepted-anglicisms-it.md` |
| `en` | English, formal academic register | — |

Workflow files and skill chat scaffolding stay in English regardless of
`ARTICLE_LANG`.

## Word document handling

When the project contains Word files (`.docx`) or the revised Markdown article
must be rendered back to Word, preserve content first and enforce a clean
editorial layout:

- Headings must remain explicit headings, not body paragraphs styled manually.
- Body text must be black.
- Headings must be black unless the journal norms explicitly require another
  color.
- Body paragraphs must not have blank-line spacing between consecutive
  paragraphs; use paragraph spacing values instead of inserting empty
  paragraphs.
- Keep visible spacing between headings and the following body text through
  heading style spacing before/after, not through manual blank lines.
- Do not introduce extra paragraph breaks while converting `.docx` to Markdown
  or Markdown back to `.docx`.
- If a Word formatting change is proposed, present it as a revision point and
  ask `Accetta / Modifica / Rivedi completamente / Tieni in considerazione` before applying.

## Git contract

- **The user controls normal git operations.** The skill never commits, stages,
  or pushes on proposal acceptance. Modifications to the article, the `.bib`,
  the project file, and the final sheet are written to disk and remain there
  until the user gives an explicit git instruction.
- **Handoff is the only automatic git exception.** `workflow/06-handoff.md`
  writes a checkpoint, records a decision-log checkpoint, syncs current files,
  stages only active-session files, and creates a commit with a clear message.
  It never pushes and never includes unrelated user changes.
- After each accepted change, the skill briefly notes that there are
  pending changes — without performing any git action unless explicitly asked.
- Suggested commit message format (when the user asks): `revision(<reviewer-slug>): <point-id> — <summary>`. The skill can supply the message text in chat for the user to paste.
- If the user explicitly asks the skill to commit on their behalf, do so
  with `git commit` and without `--no-verify`.
- If the user explicitly authorizes a push, confirm the target remote/branch
  when ambiguous, then run `git push`.

## Revision closure triggers

A revision session closes in **two cases**. A pause/handoff is different from
closure and uses `workflow/06-handoff.md`.

1. **Perimetro naturale esaurito** — all items in the revision scope have been processed:
   - `/article-revision`, `/r-pp`, `/r-pp-a`: last reviewer point or last paragraph reached.
   - `/r-conn`: all selected transitions and overused connectors fixed.
   - `/r-global`: all selected lenses have produced and received explicit decisions, or the user saved the seven-lens report as a trace for `/r-pp`.
   - `/r-chapter`: all selected cross-article dimensions fixed.

2. **Chiusura esplicita** — user sends a closure phrase:
   - IT: `chiudi`, `fine`, `ho finito`, `concludi`, `basta così`, `chiudiamo`
   - EN: `close`, `done`, `finish`, `end`, `I'm done`

**Mandatory closure sequence (always the same):**

1. Present session summary (items processed, accepted/modified/fully revised/deferred, Δ chars, active version).
2. Ask: *"Procedo con la chiusura? (sì / sì senza final sheet / annulla)"*
3. On confirm:
   - `workflow/70-final-sheet.md` — if user requests it
   - `workflow/95-decision-log.md` — mandatory (closes task file + calls `96-sync-current.md`)

Never advance to the closure sequence without user confirmation. Never skip
`95-decision-log.md` or `96-sync-current.md` once closure is confirmed.

## Handoff and Resume

If the user says `pause`, `stop`, `sospendi`, `interrompi`, `/r-handoff`, or
similar while the round is not complete, run `workflow/06-handoff.md` instead of
the closure sequence. Handoff writes a checkpoint in the task file, marks the
session `paused`, records the current unit/proposal/pending decisions, and
creates a decision-log checkpoint, syncs current files, and creates a scoped git
commit with a clear message before printing the exact next action for a future
agent.

If the user says `riprendi`, `continua`, `/r-resume`, or re-invokes a command
after interruption, run `workflow/06-handoff.md#resume-from-handoff` during
setup. Resuming an existing paused task is not a new revision session: do not
run a new mandatory bump and do not create a new task file.

## Revision scope (granularity)

The skill can operate on three levels. The user picks the scope at any
point in the workflow:

| Scope | Trigger phrases | Behaviour |
|---|---|---|
| **Fragment** (sentence-level / inline) | *"fix this sentence"*, *"adjust this quotation"*, *"replace X with Y"* | Smallest possible diff. Touches a single sentence, citation, term, formatting fix. Goes through the same `Original / Proposal / Decision` pattern with surgical context. |
| **Paragraph** (default during reviewer revision) | *"revise this paragraph"*, *"section 3 discussion"* | Operates on a coherent block (one paragraph or one numbered subsection). Standard mode for processing reviewer points. |
| **Whole article** (full pass) | *"revise the whole article"*, *"check coherence from start to finish"* | Sequential walk through every section, point by point. Each candidate change is still presented individually for `Accetta / Modifica / Rivedi completamente / Tieni in considerazione` — the user is not asked to approve a single mass-replacement. |
| **Paragraph-by-paragraph** (`/r-pp`) | `/r-pp` | Walk every paragraph sequentially. If a global trace exists, load it as diagnostic context. For each paragraph: check unitary concept, clarity, connection, style/citations, and propose modifications. At chapter boundaries recap organization and coherence. Explicit decision per modification. |
| **Deep paragraph-by-paragraph** (`/r-pp-a`) | `/r-pp-a` | As `/r-pp` but with six-layer AI analysis (unitary concept, logic, structure, tone, citations, norms). Uses any active global trace as context; proposals numbered by category. |
| **Dual peer review** (`/r-pr-2`) | `/r-pr-2` | Generate two standalone reviewer reports (method-focused + theory-focused) + synthesis document in `revisions/<article-slug>/`. No interactive decision loop — output files feed subsequent revision commands (`/r-pp-a`, `/r-global`, etc.). |
| **Connector revision** (`/r-conn`) | `/r-conn` | Non-content pass: examine logical connectors, inter-paragraph transitions, inter-section transitions, signposting. Diagnostic table + selective fix with explicit decisions. |
| **Global revision** (`/r-global`) | `/r-global` | High-level, non-granular pass through seven lenses (thesis, architecture, proportionality, narrative, redundancy, terminology, norms). Diagnostic report → user either selects lenses for structural decisions or saves a trace for `/r-pp`. |
| **Chapter revision** (`/r-chapter`) | `/r-chapter [§N]` | Paragraph-depth revision of a single section in full cross-article context. Six diagnostic dimensions: terminology, cross-references, section interfaces, redundancy, argument thread, norms compliance. Explicit decision per point. |
| **Drive collaboration** (`/r-gdrive`) | `/r-gdrive [create\|push\|sync]` | Create/sync a shared Drive folder; push the revised article + redline; pull colleague feedback into `revisions/<slug>/sources/`. No interactive decision loop — output is a source for later passes. User shares the folder. |
| **Colleague approval** (`/r-approve`) | `/r-approve` | Gate `Accepted` points behind colleague sign-off (Doc suggestions or `approvals.md`). `approve` → mark approved; `changes` → re-propose via the decision loop; `reject` → ask user (no auto-revert). |
| **Redline export** (`/r-redline`) | `/r-redline` | Colored old-vs-new `.docx`/`.html` for the reviewer + response-to-reviewers letter. Separate from the clean submission file. No interactive decision loop. |
| **Guide** (`/r-guide`) | `/r-guide` | Print the recommended full revision path: TOV + `/r-global` + `/r-pp-a` with chapter handoffs + closure + `/r-pr-2` QA + mini-round. Read-only, no bump. |
| **Handoff / Resume** (`/r-handoff`, `/r-resume`) | `/r-handoff`, `/r-resume`, `pause`, `stop`, `sospendi`, `riprendi`, `continua` | Save a resumable checkpoint in the current task file, write decision log, sync current files, and commit the handoff state without closing the round; later resume that same task without a new mandatory bump. |
| **Freeze** (`/r-freeze`) | `/r-freeze [unit]` | Mark a concluded part 🟢 frozen in the ledger. No-arg = last unit worked on; `P4` / `§3` / `§3 tutto` target explicitly. Ledger-only, no article edit. |
| **Thaw** (`/r-thaw`) | `/r-thaw [unit]` | Mark a frozen part 🟡 open again so it can be revised without the advisory warning. |
| **Status** (`/r-status`) | `/r-status` | Print the frozen/open/wip snapshot from the ledger + the next suggested intervention. Read-only. |

For paragraph and whole-article scopes, break into more granular points
when the change touches separate concerns (e.g. a citation correction
plus a phrasing change in the same paragraph → two points, two
decisions, two micro-changes).

Never collapse multiple semantic changes into a single proposal just to
save chat tokens — the user must be able to accept one and keep the other as a
deferred consideration.

## Revision session task file

Every revision session creates one task file at:
`revisions/<article-slug>/task-<command-slug>-<bumped-version>.md`

The task file is:
- **Created** by `workflow/05-task.md` immediately after the mandatory bump (`10-setup.md` step 7).
- **Updated** step by step as each workflow phase completes (`05-task.md#update-step`).
- **Checkpointed** by `workflow/06-handoff.md` whenever the session is paused.
- **Resumed** by `workflow/06-handoff.md` without a new bump when the user continues.
- **Closed** by `workflow/95-decision-log.md` before writing the session entry (`05-task.md#close`).

The closed task file contains:
- The article path, version, command, and reviewer lane.
- A step-by-step status table (`done` / `skipped` / `failed`).
- The latest `## Handoff / Ripresa` checkpoint, if the session was paused.
- Accepted / modified / fully revised / deferred counts.
- Final article char count vs limit.
- The decision-log session identifier.

Never skip task file creation. If `TASK_FILE_PATH` is not set when `95-decision-log.md` runs, it means setup was incomplete — warn the user.

## Mandatory Bump at Session Start

**Every new revision session MUST start with a version bump.** This is non-negotiable. The skill does not wait for the user to accumulate edits before bumping — the bump is the first action after setup, before any revision work begins. Resuming a paused task via `workflow/06-handoff.md` is not a new session and must not create another bump.

**Rule:**
- After `10-setup.md` completes and the active article is identified, immediately propose a version bump via `60-bump-version.md`.
- If the bump is using the existing vN filename (i.e. no changes have been made yet to vN), the bump copies vN → v(N+1) with a fresh timestamp. All subsequent edits go into v(N+1).
- Only after the bump is confirmed and completed does the skill proceed to the revision workflow (reviewer feedback, `/r-pp`, `/r-pr-2`, `/r-conn`, `/r-global`, etc.).

**Exception:** If the setup detects that the article has *already* been bumped during this same session (i.e. `accepted_since_bump: 0` and a bump entry exists in the project file with today's date), skip the bump — do not double-bump.

**The `AUTO_BUMP_THRESHOLD` still applies** for mid-session bumps: after N accepted changes, the skill proposes an additional bump. This is separate from the mandatory session-start bump.

**Suggested commit message for the session-start bump:**
```
bump: vN → v(N+1) (start revision session)
```

## Versioning convention

`<prefix>-vN-YYYY-MM-DD-HHMM[-anonymous].md`

Multiple bumps in the same day stay distinct because of the time component. The bump script (`scripts/new_version.sh`) accepts both legacy `vN-YYYY-MM-DD` and new `vN-YYYY-MM-DD-HHMM` source filenames.

## Scripts

Run Python scripts with the project's Python venv (`PYTHON_BIN`). Bootstrap asks before creating `.venv/`; if the user refuses, ask before using system Python and remember the selection. Never fall back to `python3` silently.

| Script | Purpose |
|---|---|
| `scripts/char_count.py` | Char/word counter with budget check |
| `scripts/bib_check.py` | Static cross-check between citations and `.bib` |
| `scripts/bib_verify_online.py` | Crossref + OpenAlex similarity scoring |
| `scripts/sample_stats.py` | Per-cohort stats from `.xlsx`/`.csv` via YAML mapping |
| `scripts/new_version.sh` | Bump filename to `<prefix>-v(N+1)-YYYY-MM-DD-HHMM` |
| `scripts/diff_versions.sh` | Word-level diff between two versions |
| `scripts/sync_current.sh` | Sync `current.md`, `current.docx`, and a non-empty citeproc-rendered `bibliography.docx` after each revision round |

## Skill is **not** for

- Writing an article from scratch — defer to the journal-specific style skill.
- Editing `.bib` independently — defer to the bibliography skill (e.g.
  `praxis-bibliography-citations`).
- Anonymisation (XXX placeholders) — handle in a dedicated pass.
- Opening PRs or sending email. Committing is allowed only on explicit user instruction or the mandatory handoff commit; pushing is allowed only on explicit user instruction, following the Git contract.
