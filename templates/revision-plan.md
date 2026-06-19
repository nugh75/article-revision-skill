# Revision Plan {{REVIEWER}} — v{{VERSION}}

## Summary Status

- **Reference article**: `{{ARTICLE_PATH}}`
- **Reviewer**: {{REVIEWER}}
- **Feedback source**: {{FEEDBACK_SOURCE}} <!-- journal = feeds response letter; simulated = internal QA only -->
- **Editorial limit**: max {{EDITORIAL_LIMIT}} {{LIMIT_UNIT}}
- **Initial article count**: {{INITIAL_COUNT}} {{LIMIT_UNIT}}
- **Article language (auto)**: {{ARTICLE_LANG}}
- **Editorial norms**: `{{NORMS_PATH}}`
- **Document status**: revision plan, **not** applied changes

## Working Method

Each reviewer point is evaluated separately. For each point:

1. The `article-revision` skill shows the original text and the proposed change in chat.
2. The user decides: `Accetta` / `Modifica` / `Rivedi completamente` / `Tieni in considerazione`.
3. On `Accetta`: the change is applied to the article file. The skill does not commit.
4. On `Modifica`: the skill regenerates the selected modification according to the user's direction and repeats from step 1.
5. On `Rivedi completamente`: the skill regenerates the whole proposal from the original text.
6. On `Tieni in considerazione`: the point remains in the project file as deferred/context. No file edit is made.

Allowed decision states:

- `To decide`
- `Accepted`
- `Modified` (proposal reformulated and then accepted)
- `Deferred` (requires external data or later decision)

## Point-by-Point Revision

<!--
  For each reviewer point, the skill adds a subsection here.
  Schema:

### {{N}}. {{POINT_TITLE}} — {{ARTICLE_SECTION}}

**Reviewer observation**

> {{VERBATIM_QUOTE}}

**Status in v{{VERSION}}**

[Already covered | Partially covered | To integrate | To verify]

**Assessment**

{{BRIEF_ANALYSIS}}

**Proposal**

Unità: {{UNIT_LOCATOR}} <!-- if paragraph: Capitolo C — title; P<N> — FILE:L1-L2 -->

Original (`{{FILE}}:{{LINES}}`):
> {{ORIGINAL_TEXT}}

Modified:
> {{PROPOSED_TEXT}}

**Δ**: chars {{DELTA_CHARS}} · bibliography {{DELTA_BIB}} · risk {{RISK}}

**Decision**

[To decide | Accepted | Modified | Deferred]

**Notes**

{{CONTEXT_AND_DEPENDENCIES}}

---
-->

## Decision Checklist

| # | Point | Section | Status in v{{VERSION}} | Priority | Decision |
|---|---|---|---|---|---|
<!-- one row per point, updated after each decision -->

## Checks Before Applying Changes

- Character/word count remains under the editorial limit (`scripts/char_count.py`).
- Tone is consistent with the journal style skill or editorial norms.
- Bibliography: each new citation exists and has an online match (`scripts/bib_verify_online.py`).
- Text proposals do not introduce data or quantitative inferences absent from the study.
- Every numeric claim added, changed, or relied upon is re-derived from the authoritative source, never inherited from a prior version or a reviewer comment (`workflow/51-data-verification.md`).
- Anglicisms (if `ARTICLE_LANG=it`): allowed only when present in `templates/accepted-anglicisms-it.md`.
