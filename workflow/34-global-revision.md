# 34 — Global / Holistic Revision

Triggered by `/r-global`. A **non-granular, high-level** revision that examines the article as a whole organism through seven diagnostic lenses. This mode does not descend into sentence-level edits — it operates at the structural, argumentative, and narrative level.

## 0. Entry Point

Invoked by `/r-global` or phrases like:
- *"revisione globale"*
- *"revisione complessiva"*
- *"analisi strutturale dell'articolo"*
- *"holistic review"*
- *"check the overall structure"*

## 1. Bootstrap & Setup

If not already done, run `00-bootstrap.md` and `10-setup.md` to load `.env`, norms, bibliography, active article, and detect `ARTICLE_LANG`. **Note:** `10-setup.md` step 5 enforces a mandatory version bump — do not skip it.

## 2. Read Full Article

1. Read the entire article into context (skip YAML frontmatter).
2. Parse the section structure: identify all `#`, `##`, `###` headings and their hierarchy.
3. Count characters per section.
4. Extract the first sentence of each section (for narrative arc analysis).
5. Extract key terminology (defined terms, recurring concepts) for consistency check.

## 3. Apply the Seven Lenses

Generate a structured diagnostic report. Present all seven lenses as a single, complete document — the user reviews the whole picture before any edits.

### Lens 1 — Thesis Clarity

1. Locate the thesis/contribution statement. Typically in the introduction (last paragraph) or in a dedicated subsection.
2. Evaluate:
   - **Is it explicit?** Does a single sentence state what the article contributes?
   - **Is it falsifiable?** Could it be wrong? Or is it too vague to test?
   - **Is it positioned?** Does it reference the gap it fills?
3. If missing or weak, flag with a specific recommendation.

### Lens 2 — Argument Architecture

1. Map each section to its role in the overall argument:
   - §1: What does the introduction establish?
   - §2: What theoretical ground does the literature review lay?
   - §3: What does the method section set up?
   - §4: What do the results show?
   - §5: How does the discussion interpret the results?
   - §6: How does the conclusion close the loop?
2. Identify logical leaps (A → C without B) and missing steps.
3. Flag contradictions between sections (e.g. §2 defines X one way, §5 uses X differently).

### Lens 3 — Section Proportionality

1. Calculate the character count and percentage of total for each section.
2. Compare against expected proportions for the article type:
   - **Empirical (IMRaD):** Intro 10-15%, Literature/Hypotheses 15-20%, Method 15-20%, Results 20-25%, Discussion 20-25%, Conclusion 5-10%.
   - **Theoretical:** Intro 10-15%, Body (split by argument steps) 65-75%, Conclusion 10-15%.
   - **Review:** Intro 5-10%, Thematic sections (balanced) 75-85%, Conclusion 10-15%.
3. Flag sections that are >5% over or under the expected range.

### Lens 4 — Narrative Arc

1. Evaluate the article's storytelling structure:
   - **Apertura (Opening):** Does the first paragraph hook the reader? Is the research question clear?
   - **Tensione (Tension):** Does the gap/problem create genuine intellectual tension?
   - **Climax (Climax):** Do the findings deliver on the promise? Is the key result prominent?
   - **Risoluzione (Resolution):** Does the conclusion close the loop? Does it return to the opening question?
2. Flag weak transitions in the narrative (e.g. findings section reads like a list, not a story).

### Lens 5 — Redundancy

1. Scan for near-duplicate content:
   - Paragraphs that make the same point with different wording.
   - Arguments repeated across sections (e.g. the same limitation mentioned in §3, §5, and §6).
   - Redundant definitions (same term defined in multiple places).
2. Highlight consolidation opportunities.

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
- **È falsificabile?** Sì / No — <motivazione>
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
| Sezione | Caratteri | % del totale | Atteso | Stato |
|---|---|---|---|---|
| §1 Intro | 3200 | 12% | 10-15% | OK |
| §2 Letteratura | 8200 | 31% | 15-20% | ⚠️ Sovradimensionata |
| §3 Metodo | 4100 | 16% | 15-20% | OK |
| §4 Risultati | 5200 | 20% | 20-25% | ⚠️ Leggermente sotto |
| §5 Discussione | 4100 | 16% | 20-25% | ⚠️ Sotto |
| §6 Conclusione | 1400 | 5% | 5-10% | OK |

### 4. Arco narrativo
- **Apertura:** <valutazione>
- **Tensione:** <valutazione — il gap motiva lo studio?>
- **Climax:** <valutazione — i risultati mantengono la promessa?>
- **Risoluzione:** <valutazione — la conclusione chiude il cerchio?>
- **Raccomandazione:** <indicazione>

### 5. Ridondanza
- **Paragrafi quasi-duplicati:** P12 ~ P28 (entrambi definiscono la variabile dipendente)
- **Argomenti ripetuti:** Il limite del campione appare in §3, §5 e §6
- **Raccomandazione:** <quali consolidare>

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
Quali lenti vuoi affrontare?
- "tutte" — elaboro proposte per ogni lente
- "proporzioni + terminologia" — solo lenti specifiche
- "solo architettura" — una singola lente
- "nessuna" — prendo atto del report, nessuna modifica
```

Adapt to English if `ARTICLE_LANG=en`.

## 5. Generate Proposals by Lens

For each lens the user selects:

### Structural proposals (Lenses 1, 2, 4)

For architectural changes, present as A/R/M points. Examples:
- **Restructure:** "Move the hypotheses from §2.3 into §1 (introduction) to establish the thesis earlier."
- **Reorder:** "Swap §4 and §5: present discussion before detailed results tables."
- **Add:** "Insert a transition paragraph between §2 and §3 explaining how the literature gap motivates the method."

### Proportionality proposals (Lens 3)

For size adjustments:
- Present the target char count per section.
- Show which paragraphs to cut, consolidate, or expand.
- Use A/R/M: user can accept the cut of specific paragraphs.

```
## Point <N> — Proporzioni: ridurre §2 · scope: global

**Diagnosi:** §2 è al 31% (atteso 15-20%). Eccesso di ~3000 caratteri.

**Modifiche:**
1. [§2.1] Rimuovere la digressione su Author (2018) — 800 chars [(non essenziale per l'argomento)]
2. [§2.3] Consolidare i tre paragrafi sulla definizione di X in uno solo — 1200 chars [(ridondante)]
3. [§2.4] Spostare la tabella comparativa in appendice — 1000 chars [(materiale supplementare)]

**Δ**: chars -3000 / words -450 · risk: medium

**A/R/M?**
```

### Terminology proposals (Lens 6)

For global renames:
- Use `replaceAll` on the article file.
- Present as a single A/R/M point.

```
## Point <N> — Terminologia: "emotional work" → "emotional labour" · scope: global

**Diagnosi:** Il termine è definito come *emotional labour* in §2 ma usato come *emotional work* in §4, §5.

**Modifiche:**
1. [global] «emotional work» → «emotional labour» [(5 occorrenze: §4 riga 12, §4 riga 45, §5 riga 8, §5 riga 22, §5 riga 67)]

**Δ**: chars +5 / words 0 · risk: low

**A/R/M?**
```

### Redundancy proposals (Lens 5)

For deduplication:
- Show the near-duplicate paragraphs side by side.
- Propose which to keep and which to cut.
- Allow the user to choose the keepers.

## 6. Handle Responses

Follow standard `30-iterate-points.md`, section 4, with one addition:

- For global modifications (e.g. `replaceAll` renames), after Accept, verify the change with a grep to confirm all occurrences were updated.
- After applying structural changes (section reordering), re-read the article and confirm no broken cross-references (e.g. "as discussed in §4" now points to the wrong section).

## 7. Edge Cases

- **Single-section article.** Still run the seven lenses. Scope adapts naturally.
- **No structural issues found.** Announce: *"L'architettura dell'articolo è solida. Tutte e sette le lenti non rilevano problemi strutturali."* Offer to proceed to `/r-pp` for granular revision.
- **Massive restructuring needed.** If the diagnostic identifies >5 structural issues, warn: *"Questa revisione comporta cambiamenti strutturali significativi. Consiglio di procedere una lente alla volta per non perdere il controllo."*
- **Contradiction with reviewer feedback.** If reviewer feedback was previously processed via `/article-revision` and the global revision identifies a contradictory recommendation, surface the conflict explicitly: *"⚠️ Il Reviewer A ha chiesto di espandere §2, ma la lente 3 (proporzionalità) suggerisce di ridurlo. Quale direzione preferisci?"*
- **Character budget.** Structural changes (cuts, moves, adds) have large character impact. Track the cumulative Δ after each accept and compare against `EDITORIAL_LIMIT_CHARS`.

## 8. Completion

```
Revisione globale completata.
Lenti analizzate: 7
Lenti con modifiche: N
Modifiche strutturali accettate: X
Modifiche terminologiche accettate: Y
Modifiche di proporzione accettate: Z
Modifiche respinte: R
Bilancio caratteri: +Δ (limite: EDITORIAL_LIMIT_CHARS)

L'architettura è ora solida. Vuoi procedere con la revisione granulare?
- /r-pp per revisione paragrafo per paragrafo
- /r-pp-a per revisione approfondita
- /r-conn per la revisione dei connettori
- /r-bump per il bump di versione
```
