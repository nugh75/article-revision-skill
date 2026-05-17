---
name: article-revision
description: |
  Coordinate iterative revision of a scientific article in markdown. Trigger
  when the user asks to apply reviewer feedback ("revise article",
  "apply reviewer X comments", "let's process the reviewer comments"),
  to bump the article to a new version, or invokes `/article-revision`
  explicitly. Skill assumes a project layout with `articles/`, `bibliography/
  reference.bib`, `editorial-norms/`, `revisions/`, and an `.env` file.
  For each reviewer point: shows original text + proposed change in chat,
  asks Accept / Reject / Modify, and applies on Accept without committing.
  Auto-detects article language (it/en) and adapts
  the proposal style accordingly. Out of scope: writing the article from
  scratch (use the journal-specific style skill, e.g. `praxis-article-style`),
  managing the `.bib` directly (use `praxis-bibliography-citations` or its
  equivalent).
---

# Article Revision Skill

Operational layer that orchestrates the existing article-style and
bibliography skills around a structured revision workflow.

## Slash Commands

| Command | Action |
|---|---|
| `/article-revision` | Full revision workflow from reviewer feedback |
| `/r-pp` | **Revisione Paragrafo per Paragrafo** — walk every paragraph sequentially; for each, ask diagnostic questions, then propose modifications |
| `/r-pp-a` | **Revisione Paragrafo per Paragrafo Approfondita** — as `/r-pp` but with deep diagnostic questions (content, structure, style, citations, norms) before proposing |
| `/r-pr-2` | **Revisione Due Peer Reviewer** — simulate two independent peer reviewers; generate Standalone reviewer documents in `revisions/<article-slug>/` without interactive A/R/M; the documents feed subsequent revision passes |
| `/r-conn` | **Revisione Connettori** — analyse and polish logical connectors, transitions, and signposting between paragraphs and sections |
| `/r-global` | **Revisione Globale** — high-level, non-granular revision: overall structure, argument coherence, section proportionality, redundancy, terminology consistency |
| `/r-bump` | Bump article version (hand off to `workflow/60-bump-version.md`) |
| `/r-sheet` | Generate final revision sheet (hand off to `workflow/70-final-sheet.md`) |

### Paragraph-by-Paragraph Modes (`/r-pp`, `/r-pp-a`)

These modes perform a **proactive** revision walk over the entire article, paragraph by paragraph. Unlike the standard reviewer-feedback flow, the LLM actively diagnoses each paragraph before proposing changes.

#### `/r-pp` — Standard Paragraph-by-Paragraph

For each paragraph in sequence:

1. **Show** the paragraph with context (preceding paragraph + current paragraph).
2. **Ask** three standard diagnostic questions (adapted to `ARTICLE_LANG`):

   | # | IT | EN |
   |---|---|---|
   | Q1 | L'argomento è chiaro e completo? | Is the argument clear and complete? |
   | Q2 | Il paragrafo si collega bene al precedente? | Does it connect well to the previous paragraph? |
   | Q3 | Ci sono problemi di stile, registro o citazioni? | Any issues with style, register, or citations? |

3. **Wait** for user answers.
4. **Propose** modifications based on user answers, using the standard A/R/M pattern.
5. After decision on each proposal, ask: *"Ci sono altri cambiamenti in questo paragrafo?"* before advancing.
6. **Advance** only on explicit command (`prossimo`, `next`, `passa al prossimo`).

The user can pause with `pause` and resume later from the current paragraph.

#### `/r-pp-a` — Deep Paragraph-by-Paragraph

As `/r-pp`, but with an **extended diagnostic interview** before proposing. For each paragraph, the skill asks these five layered questions:

| # | IT | EN |
|---|---|---|
| Q1 | L'argomento è logicamente completo? Mancano passaggi? | Is the argument logically complete? Any missing steps? |
| Q2 | La struttura interna funziona? (topic sentence, sviluppo, chiusura) | Does the internal structure work? (topic sentence, development, closure) |
| Q3 | Il tono e il registro sono appropriati alla rivista? | Is the tone and register appropriate for the journal? |
| Q4 | Ogni affermazione è supportata da una citazione? Le citazioni sono formattate correttamente? | Is every claim backed by a citation? Are citations correctly formatted? |
| Q5 | Il paragrafo rispetta le norme editoriali? (limiti, stile, terminologia) | Does the paragraph respect the editorial norms? (limits, style, terminology) |

After collecting answers, the skill synthesises them into a unified proposal block, numbering each modification by diagnostic category. The user may accept/reject by category (e.g. `A struttura` or `R citazioni`).

### `/r-pr-2` — Standalone Dual Peer Review (Document Generation)

This mode simulates two independent peer reviewers with distinct personas and writes their reports as standalone Markdown documents in `revisions/<article-slug>/`. It does **not** run an interactive A/R/M loop — the documents become input for subsequent revision passes (`/r-pp-a`, `/r-pp`, `/r-global`, `/r-conn`).

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

**No interactive A/R/M.** The synthesis document lists modifications with tags but does NOT apply them. The user triggers application later via `/r-pp-a`, `/r-pp`, `/r-global`, or `/r-conn`, referencing the synthesis document.

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

1. **Parse** the article into paragraphs and sections.
2. **Extract** every paragraph boundary (last sentence of P<N> + first sentence of P<N+1>) into a list.
3. **Extract** every section boundary (last paragraph of §<N> + first paragraph of §<N+1>).
4. **Diagnose** each boundary: is the logical relationship explicit? Is the connector appropriate?
5. **Present** findings as a diagnostic table, not one by one — the user gets a bird's-eye view:

   ```
   ## Connector Diagnostic — <article>

   ### Inter-paragraph transitions

   | Transition | Logical relation | Current connector | Issue | Proposal |
   |---|---|---|---|---|
   | P3→P4 | Contrast | *ma* | Weak at paragraph start | *Tuttavia* |
   | P7→P8 | Cause/effect | (missing) | Implicit → needs connector | *Di conseguenza* |
   | P12→P13 | Addition | *inoltre* | OK | — |

   ### Inter-section transitions

   | Transition | Logical relation | Current state | Issue | Proposal |
   |---|---|---|---|---|
   | §2→§3 | Sequence | (missing) | Abrupt topic shift | Add signposting line |
   | §4→§5 | Summary + preview | OK | — | — |

   ### Overused connectors

   | Connector | Count | In paragraphs | Recommendation |
   |---|---|---|---|
   | *tuttavia* | 7 | P2, P4, P5, P9, P11, P14, P18 | Reduce to max 3; rephrase 4 |
   ```

6. **Ask** the user to select which transitions to fix: *"Quali transizioni vuoi sistemare? (es. 'P3→P4, P7→P8, §2→§3' oppure 'tutte')"*
7. **Propose** modifications for the selected items using the standard A/R/M pattern (one point per transition group).
8. **Apply** on Accept, advance on command.

Each `[Overused]` item becomes a separate proposal asking to rephrase *N* occurrences. The user can specify which occurrences to keep and which to replace.

### `/r-global` — Global / Holistic Revision

A **non-granular, high-level** revision that examines the article as a whole organism. This mode does not descend into sentence-level edits — it operates at the structural, argumentative, and narrative level.

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
   - **Paragrafi quasi-duplicati:** P12 ~ P28 (both define the dependent variable)
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
   Quali vuoi affrontare? (es. "tutte le proporzioni + terminologia" oppure "solo la mappa argomentativa")
   ```

3. **Wait** for the user to select which lenses to act on.
4. For each selected lens, generate one or more revision points using the A/R/M pattern. Each point addresses a specific structural issue (e.g. "Cut §2 from 8200 to 5000 chars", "Rename 'emotional work' → 'emotional labour' globally").
5. **Apply** on Accept. For structural changes (reordering, cutting), the skill edits the article with surgical precision. For global renaming, use `replaceAll`.
6. **Advance** on explicit command.

This mode is designed to be run **before** granular revision (`/r-pp`, standard reviewer feedback) — fix the architecture first, then the bricks.

## Authority

Editorial rules in priority order:

1. The journal's editorial norms file referenced by `EDITORIAL_NORMS_PATH`
   in `.env` (binding for the article).
2. The journal-specific style skill installed in the project (e.g.
   `praxis-article-style`), if any.
3. This skill — operational orchestration only.

When norms and user preference conflict, **norms win**. Surface the
conflict explicitly in chat.

## Project layout (required)

```
<project-root>/
├── .env
├── articles/                         # or any directory; auto-detected
│   └── article-vN-YYYY-MM-DD[-anonymous].md
├── bibliography/
│   └── reference.bib
├── editorial-norms/
│   └── <journal-norms>.md
├── data/                             # optional, for sample stats
└── revisions/
    └── <reviewer-name>/
        ├── revision-plan-vN.md
        └── final-sheet-vN.md
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

1. `workflow/00-bootstrap.md` — set up the revision environment if missing
   (venv with Python deps, `.bib` file, `.env` with editorial parameters
   and Zotero credentials, editorial norms file). Idempotent: skips
   anything already in place.
2. `workflow/10-setup.md` — load `.env`, norms, bib, current article version,
   detect article language.
3. `workflow/20-plan-revision.md` — accept reviewer feedback, generate
   `revisions/<reviewer>/revision-plan-vN.md` from the template, with
   each point in `To decide` state.
4. `workflow/30-iterate-points.md` — for each point, propose, ask
   `Accept / Reject / Modify`, apply on Accept. **Never commit
   automatically** — the user controls git.
4a. `workflow/31-paragraph-by-paragraph.md` — triggered by `/r-pp` or
   `/r-pp-a`. Walk every paragraph sequentially with diagnostic questions
   before proposing. Deep mode (`/r-pp-a`) uses five-layer diagnostics.
4b. `workflow/32-peer-review-simulation.md` — triggered by `/r-pr-2`.
   Generate two standalone reviewer documents in `revisions/<article-slug>/`
   (method-focused, theory-focused) plus a synthesis document. No interactive
   A/R/M — the documents feed subsequent revision passes.
4c. `workflow/33-connector-revision.md` — triggered by `/r-conn`.
   Analyse and polish logical connectors, transitions, and signposting
   between paragraphs and sections. Does not rewrite content.
4d. `workflow/34-global-revision.md` — triggered by `/r-global`.
   High-level, non-granular revision across seven lenses: thesis clarity,
   argument architecture, section proportionality, narrative arc,
   redundancy, terminology consistency, norm alignment.
5. `workflow/40-bibliography-check.md` — when a citation is touched or new
   keys are introduced.
6. `workflow/50-sample-description.md` — when the methodology asks for a
   sample-description update from raw data.
7. `workflow/60-bump-version.md` — when the user signals end of revision
   round, or when accepted modifications since the last version exceed
   `AUTO_BUMP_THRESHOLD` (default 5); the skill **proposes** a bump,
   never forces it. New filename: `article-v(N+1)-YYYY-MM-DD-HHMM.md`
   (date + 24h time, so multiple bumps in the same day stay distinct).
8. `workflow/70-final-sheet.md` — produce `revisions/<reviewer>/
   final-sheet-vN.md` with the post-revision status.

Skipping is allowed if a step is not applicable; never silently skip a
step that *should* run.

## Interaction pattern (binding)

For every revision point, output exactly this shape in chat:

```
## Point N — <short title> · scope: <fragment|paragraph|whole article>

**Original** (`<file>:<line-range>`)
> <verbatim text>

**Proposta**
> <proposed full text>

**Modifiche:**
1. `<old>` → `<new>` [(motivazione)]
2. `<old>` → `<new>` [(motivazione)]
...

**Δ**: chars +X / words +Y · risk: <low|medium|high>

**A/R/M?** (indicare i numeri delle modifiche, es. "A 2,4" oppure "M 3: sostituire X con Y")
```

Then **wait** for the user. Do not pre-emptively apply.

Each modification within a paragraph is numbered, so the user can accept or reject individual changes with precision:
- `A 1,3` → accept modifications 1 and 3 only.
- `R 2` → reject modification 2.
- `M 4: <direzione>` → modify modification 4 as specified.

If the user responds with `A` without numbers, all modifications are accepted.
If the user responds with `R` without numbers, the entire point is rejected.

### After applying changes

Once modifications are applied, **do not advance** to the next point automatically. Instead, output:

```
Applicate modifiche <numeri>. [Restano in sospeso le modifiche <numeri>.] Ci sono altri cambiamenti da fare in questo paragrafo?
```

And **wait** for an explicit command from the user (e.g. "A 1,3", "M 5: ...", "no, prossimo paragrafo", "passa al prossimo").

### Handling responses

- `Accept` (with selected numbers) → apply via Edit only the numbered modifications. Mark applied modifications as `Accepted` in the project file. Increment the *accepted-since-last-bump* counter. **Do not commit.** When the counter reaches `AUTO_BUMP_THRESHOLD`, suggest a version bump (see step 7). Ask for further changes on the same paragraph.
- `Reject` (with selected numbers) → annotate those modifications as `Rejected` + reason. No file edits for them. Ask for further changes on the same paragraph.
- `Reject` (entire point) → annotate entire point `Rejected` + reason. Advance to next point.
- `Modify <N>: <direzione>` → regenerate modification N according to the user's direction. Re-present the updated modification with the same numbering. Repeat until accepted or rejected.
- Silent advance to the next point only when the user gives an explicit command (e.g. "no, prossimo", "passa al prossimo paragrafo", "next").

If the proposal involves multiple separate edits (e.g. an inline citation + a bibliography entry), still present them as numbered modifications within a single coherent block, allowing the user to accept each independently.

## Language auto-detection

In `00-setup.md`:

1. Skip frontmatter (lines between leading `---`).
2. Read up to 1.000 chars of body text.
3. Score language by function words for the candidate languages.
4. Highest score wins; ties → fallback to `langdetect` if installed, else ask the user.
5. Persist to memory for the session as `ARTICLE_LANG`.

Override via `.env` `ARTICLE_LANG=...` always wins over auto-detection.

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
  ask `Accept / Reject / Modify` before applying.

## Git contract

- **The user controls all git operations.** The skill never commits, never
  stages, never pushes. Modifications to the article, the `.bib`, the
  project file, the final sheet, are written to disk and remain there until
  the user decides to commit them.
- After each accepted change, the skill briefly notes that there are
  pending changes — without performing any git action.
- Suggested commit message format (when the user asks): `revision(<reviewer-slug>): <point-id> — <summary>`. The skill can supply the message text in chat for the user to paste.
- If the user explicitly asks the skill to commit on their behalf, do so
  with `git commit` (no `--no-verify`, no `git push`).

## Revision scope (granularity)

The skill can operate on three levels. The user picks the scope at any
point in the workflow:

| Scope | Trigger phrases | Behaviour |
|---|---|---|
| **Fragment** (sentence-level / inline) | *"fix this sentence"*, *"adjust this quotation"*, *"replace X with Y"* | Smallest possible diff. Touches a single sentence, citation, term, formatting fix. Goes through the same `Original / Proposal / Decision` pattern with surgical context. |
| **Paragraph** (default during reviewer revision) | *"revise this paragraph"*, *"section 3 discussion"* | Operates on a coherent block (one paragraph or one numbered subsection). Standard mode for processing reviewer points. |
| **Whole article** (full pass) | *"revise the whole article"*, *"check coherence from start to finish"* | Sequential walk through every section, point by point. Each candidate change is still presented individually for `Accept / Reject / Modify` — the user is not asked to approve a single mass-replacement. |
| **Paragraph-by-paragraph** (`/r-pp`) | `/r-pp` | Walk every paragraph sequentially. For each: ask three diagnostic questions (clarity, connection, style/citations), collect answers, propose modifications. A/R/M per modification. |
| **Deep paragraph-by-paragraph** (`/r-pp-a`) | `/r-pp-a` | As `/r-pp` but with five-layer diagnostic interview (logic, structure, tone, citations, norms). Proposals numbered by category; user can accept/reject by category. |
| **Dual peer review** (`/r-pr-2`) | `/r-pr-2` | Generate two standalone reviewer reports (method-focused + theory-focused) + synthesis document in `revisions/<article-slug>/`. No interactive A/R/M — output files feed subsequent revision commands (`/r-pp-a`, `/r-global`, etc.). |
| **Connector revision** (`/r-conn`) | `/r-conn` | Non-content pass: examine logical connectors, inter-paragraph transitions, inter-section transitions, signposting. Diagnostic table + selective fix with A/R/M. |
| **Global revision** (`/r-global`) | `/r-global` | High-level, non-granular pass through seven lenses (thesis, architecture, proportionality, narrative, redundancy, terminology, norms). Diagnostic report → user selects lenses → structural A/R/M points. |

For paragraph and whole-article scopes, break into more granular points
when the change touches separate concerns (e.g. a citation correction
plus a phrasing change in the same paragraph → two points, two
decisions, two micro-changes).

Never collapse multiple semantic changes into a single proposal just to
save chat tokens — the user must be able to accept one and reject the
other.

## Mandatory Bump at Session Start

**Every new revision session MUST start with a version bump.** This is non-negotiable. The skill does not wait for the user to accumulate edits before bumping — the bump is the first action after setup, before any revision work begins.

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

## Skill is **not** for

- Writing an article from scratch — defer to the journal-specific style skill.
- Editing `.bib` independently — defer to the bibliography skill (e.g.
  `praxis-bibliography-citations`).
- Anonymisation (XXX placeholders) — handle in a dedicated pass.
- Committing, pushing to remote, opening PRs, sending email.
