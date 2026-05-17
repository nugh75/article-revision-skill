# 32 — Standalone Dual Peer Review (Document Generation)

Triggered by `/r-pr-2`. Simulates two independent peer reviewers with distinct personas and writes their reports as standalone Markdown documents. **No interactive A/R/M loop** — the documents feed subsequent revision passes (`/r-pp-a`, `/r-pp`, `/r-global`, `/r-conn`).

## 0. Entry Point

Invoked by `/r-pr-2` or phrases like:
- *"simula una revisione di due peer reviewer"*
- *"fai finta che due reviewer leggano l'articolo"*
- *"dual peer review simulation"*
- *"genera i report dei reviewer"*

If the user says "simula tre reviewer", adapt — add a third persona on the fly (e.g. Reviewer C: language/style specialist). The pattern scales.

## 1. Bootstrap & Setup

If not already done, run `00-bootstrap.md` and `10-setup.md` to load `.env`, norms, bibliography, active article, and detect `ARTICLE_LANG`. **Note:** `10-setup.md` step 5 enforces a mandatory version bump before any revision work begins — do not skip it.

## 2. Confirm Output Directory

Verify that `revisions/<article-slug>/` exists. If not, create it:

```bash
mkdir -p revisions/<article-slug>
```

Where `<article-slug>` is derived from the article filename without extension (e.g. `article-v5-2026-05-14-1427` → `article-v5`).

## 3. Define Reviewer Personas

Use these personas unless the user overrides:

### Reviewer A — Il Metodologo / The Methodologist

- **Focus:** Research design, sampling, data quality, internal/external validity, statistical choices, replicability
- **Tone:** Rigorous, precise, sometimes sceptical
- **Typical comments:** "The sample size is insufficient for the claimed effect", "Confound X is not controlled for", "The measurement instrument for Y has known reliability issues"
- **Likes:** Preregistration, power analysis, sensitivity checks, transparent limitations
- **Dislikes:** Overclaiming, p-hacking, convenience samples presented as representative

### Reviewer B — Il Teorico / The Theoretician

- **Focus:** Literature positioning, argument coherence, contribution novelty, theoretical grounding, writing quality, narrative arc
- **Tone:** Broad, synthetic, sometimes demanding
- **Typical comments:** "The theoretical gap is overstated — see Author (2020) for a similar argument", "The contribution is unclear: what does this add beyond the existing literature?", "Section 3 and Section 5 contradict each other on the definition of X"
- **Likes:** Clear contribution statements, honest engagement with prior work, elegant argument structure
- **Dislikes:** Strawman arguments, citation padding, vague research questions

Announce the personas and confirm:

```
## Simulazione Dual Peer Review — Generazione Documenti

**Reviewer A — Il Metodologo**: disegno di ricerca, campionamento, qualità dei dati, validità, scelte statistiche.
**Reviewer B — Il Teorico**: posizionamento nella letteratura, coerenza argomentativa, novità del contributo, qualità della scrittura.

**Articolo**: <article-path>
**Versione**: v<N>
**Lingua**: <ARTICLE_LANG>

Output:
- `revisions/<article-slug>/reviewer-a-vN.md`
- `revisions/<article-slug>/reviewer-b-vN.md`
- `revisions/<article-slug>/peer-review-synthesis-vN.md`

Procedo con la generazione? (sì / annulla)
```

## 4. Parse Article Into Sections

1. Read the full article (skip YAML frontmatter, abstract lines, keywords).
2. Split by headings (`#`, `##`, `###`). A section is the heading line + all body paragraphs before the next heading of equal or higher level.
3. Number sections: `§1`, `§2`, ..., `§N`.
4. Exclude the bibliography block (identified by repeated citation lines with `-` prefix or the `---` separator before it) and the biographic note. These are checked separately.

## 5. Generate Reviewer A Report

Write `revisions/<article-slug>/reviewer-a-vN.md` with this structure:

```markdown
---
reviewer: "A — Il Metodologo"
article: <article-path>
version: v<N>
created: YYYY-MM-DD
persona: "Rigorous, method-focused. Focus: research design, sampling, data quality, validity, statistics, replicability."
---

# Reviewer A Report — Il Metodologo

## Overall Assessment
<2–3 paragraphs summarising strengths, weaknesses, and overall methodological soundness. Include a verdict: Accept with minor/major revisions, Reject, etc.>

---

## §1 — <section title>
### Comments
1. <numbered comment with line reference>
2. <numbered comment with line reference>
...

### Flagged Issues
- [Reproducibility] <issue>
- [Validity] <issue>
- [Statistical] <issue>

---

## §2 — <section title>
...

---

## Bibliography Check
<Check that all in-text citations map to .bib entries. Flag missing keys, mismatched years, formatting issues.>

---

## Priority Ranking
1. **Critical** — <issue> (§<section>)
2. **High** — <issue> (§<section>)
3. **Medium** — <issue> (§<section>)
...
```

**Generation rules:**
- Apply the Methodologist persona rigorously.
- Every comment must reference a specific section and, where possible, a line or passage.
- Flagged issues use categories: Reproducibility, Validity, Statistical, Sampling, Measurement, Overclaiming.
- The Priority Ranking must be ordered by severity, not by section order.
- Language: match `ARTICLE_LANG` (Italian for `it`, English for `en`).

## 6. Generate Reviewer B Report

Write `revisions/<article-slug>/reviewer-b-vN.md` with this structure:

```markdown
---
reviewer: "B — Il Teorico"
article: <article-path>
version: v<N>
created: YYYY-MM-DD
persona: "Broad-view, theory-focused. Focus: literature positioning, argument coherence, contribution clarity, writing quality."
---

# Reviewer B Report — Il Teorico

## Overall Assessment
<2–3 paragraphs summarising narrative quality, argument coherence, contribution novelty, and overall writing. Include a verdict.>

---

## §1 — <section title>
### Comments
1. <numbered comment with line reference>
2. <numbered comment with line reference>
...

### Flagged Issues
- [Literature] <issue>
- [Argument] <issue>
- [Clarity] <issue>

---

## §2 — <section title>
...

---

## Narrative Arc Assessment
<Evaluate the article's story: opening → gap → method → findings → discussion → conclusion. Flag missing beats, weak transitions, unresolved threads.>

---

## Bibliography Check
<Check completeness, relevance, over/under-citation of specific sources. Flag strawman arguments.>

---

## Priority Ranking
1. **Critical** — <issue> (§<section>)
2. **High** — <issue> (§<section>)
3. **Medium** — <issue> (§<section>)
...
```

**Generation rules:**
- Apply the Theoretician persona rigorously.
- Every comment must reference a specific section and, where possible, a line or passage.
- Flagged issues use categories: Literature, Argument, Clarity, Contribution, Narrative, Terminology.
- The Priority Ranking must be ordered by severity.
- Language: match `ARTICLE_LANG`.

## 7. Generate Synthesis Document

Write `revisions/<article-slug>/peer-review-synthesis-vN.md` with this structure:

```markdown
---
reviewers: "A (Metodologo) + B (Teorico)"
article: <article-path>
version: v<N>
created: YYYY-MM-DD
total_comments_a: <N>
total_comments_b: <N>
convergent: <N>
divergent: <N>
independent_a: <N>
independent_b: <N>
---

# Peer Review Synthesis

## Summary Statistics

| Metric | Count |
|---|---|
| Reviewer A comments | <N> |
| Reviewer B comments | <N> |
| Convergent (C) — both agree | <N> |
| Divergent (D) — they disagree | <N> |
| Independent-A (I) — A only | <N> |
| Independent-B (I) — B only | <N> |

---

## §1 — <section title>

### Convergence Matrix

| # | Topic | Reviewer A | Reviewer B | Status |
|---|---|---|---|---|
| 1 | <topic> | <summary> | <summary> | C |
| 2 | <topic> | <summary> | — | I |
| 3 | <topic> | — | <summary> | I |

### Convergent Points (C)
<Explain what both agree on. These have the highest priority for revision.>

### Divergent Points (D)
<Explain the disagreement. The user must decide which direction to take.>

### Unified Proposal
> <proposed text integrating feedback from both reviewers, if a concrete text change is needed>

### Modifications
1. [A] `<old>` → `<new>` (motivation)
2. [B] `<old>` → `<new>` (motivation)
3. [A+B] `<old>` → `<new>` (motivation — convergent)

---

## §2 — <section title>
...

---

## Global Priority-Ordered Action List

1. **[A+B] Critical** — <action> (§<section>)
2. **[A] Critical** — <action> (§<section>)
3. **[B] High** — <action> (§<section>)
4. **[A] Medium** — <action> (§<section>)
...

---

## Suggested Revision Strategy

<Recommend which command to run next based on the nature of the feedback:
- `/r-global` if structural/thematic issues dominate
- `/r-pp-a` if granular sentence-level changes dominate
- `/r-conn` if transition/connector issues dominate
- Or a combination with a suggested order>
```

### Modification Tag Convention

| Tag | Meaning |
|---|---|
| `[A]` | Modification from Reviewer A only |
| `[B]` | Modification from Reviewer B only |
| `[A+B]` | Convergent modification (both reviewers agree) |

### Convergence Classification Rules

| Label | Meaning |
|---|---|
| **Convergent (C)** | Both reviewers identify the same issue independently |
| **Divergent (D)** | The reviewers disagree or prioritise differently |
| **Independent (I)** | Only one reviewer raised this point; the other is silent |

For divergent points (D), the synthesis must explain the disagreement and present both sides. Never choose one side automatically.

## 8. One-Page Summary in Chat

After all three files are written, output a summary:

```
## Simulazione Dual Peer Review — Completata

**Articolo**: <article-path> (v<N>)
**Sezioni processate**: N

### Statistiche
| | # |
|---|---|
| Commenti Reviewer A | Na |
| Commenti Reviewer B | Nb |
| Convergenti (C) | Nc |
| Divergenti (D) | Nd |
| Indipendenti-A | Nia |
| Indipendenti-B | Nib |

### Top Priority [A+B] — Convergenti
1. <issue> (§<section>)
2. <issue> (§<section>)
3. ...

### File generati
- `revisions/<article-slug>/reviewer-a-vN.md`
- `revisions/<article-slug>/reviewer-b-vN.md`
- `revisions/<article-slug>/peer-review-synthesis-vN.md`

### Revisione suggerita
<Recommendation based on feedback type>

Comando suggerito: `/r-pp-a` | `/r-global` | `/r-conn`

Procedo?
```

Wait for the user.

## 9. Edge Cases

- **Single-section article.** Still generate all three files. The synthesis is simpler but follows the same structure.
- **Reviewer silence on a section.** Mark as "No comments" in that section's block. Do not fabricate issues.
- **Both reviewers agree a section should be removed.** Flag as convergent (C) with high priority. Present the removal proposal in the synthesis.
- **Bibliography conflicts.** If either reviewer flags a citation issue, note it in the synthesis and suggest `/r-bib` or manual check.
- **No convergent points.** Still generate the synthesis. Flag that the reviews are fully independent and recommend which persona's feedback to prioritise.
- **Character budget.** Warn in the summary if accepted modifications from the global action list are likely to overshoot `EDITORIAL_LIMIT_CHARS`.

## 10. What Happens Next

The user reviews the three documents and then invokes a revision command to apply changes:

- **`/r-global`** — if structural/thematic issues dominate (proportionality, redundancy, narrative arc)
- **`/r-pp-a`** — if granular paragraph-level changes are needed (logic, structure, tone, citations, norms per paragraph)
- **`/r-pp`** — if light paragraph-level changes are sufficient
- **`/r-conn`** — if transition/connector issues dominate

The revision command reads the synthesis document (`peer-review-synthesis-vN.md`) and uses the priority-ordered action list and modification tags to guide the interactive A/R/M workflow. Each modification is presented with the standard `Point N` interaction pattern.

The user can also choose to process reviewer comments selectively (e.g. "applica solo i punti [A+B] convergenti della §3" or "parti dai punti critici di Reviewer A").
