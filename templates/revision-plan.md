# Revision Plan {{REVIEWER}} — v{{VERSION}}

## Summary Status

- **Reference article**: `{{ARTICLE_PATH}}`
- **Reviewer**: {{REVIEWER}}
- **Editorial limit**: max {{EDITORIAL_LIMIT}} {{LIMIT_UNIT}}
- **Initial article count**: {{INITIAL_COUNT}} {{LIMIT_UNIT}}
- **Article language (auto)**: {{ARTICLE_LANG}}
- **Editorial norms**: `{{NORMS_PATH}}`
- **Document status**: revision plan, **not** applied changes

## Working Method

Each reviewer point is evaluated separately. For each point:

1. The `article-revision` skill shows the original text and the proposed change in chat.
2. The user decides: `Accept` / `Reject` / `Modify`.
3. On `Accept`: the change is applied to the article file. The skill does not commit.
4. On `Reject`: the point remains in the project file with a reason. No file edit is made.
5. On `Modify`: the skill regenerates the proposal according to the user's direction and repeats from step 1.

Allowed decision states:

- `To decide`
- `Accepted`
- `Modified` (proposal reformulated and then accepted)
- `Rejected`
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

Original (`{{FILE}}:{{LINES}}`):
> {{ORIGINAL_TEXT}}

Modified:
> {{PROPOSED_TEXT}}

**Δ**: chars {{DELTA_CHARS}} · bibliography {{DELTA_BIB}} · risk {{RISK}}

**Decision**

[To decide | Accepted | Modified | Rejected | Deferred]

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
- Anglicisms (if `ARTICLE_LANG=it`): allowed only when present in `templates/accepted-anglicisms-it.md`.
