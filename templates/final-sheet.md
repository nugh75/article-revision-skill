# Revision Final Sheet {{REVIEWER}} — v{{VERSION}} Status

- **Article**: `{{ARTICLE_PATH}}`
- **Feedback source**: {{FEEDBACK_SOURCE}} <!-- journal | simulated -->
- **Current count**: {{CURRENT_COUNT}} {{LIMIT_UNIT}} (limit {{EDITORIAL_LIMIT}} → **overshoot {{OVERSHOOT}}**)
- **Sheet date**: {{DATE}}
- **Previous version**: v{{PREV_VERSION}} ({{PREV_COUNT}} {{LIMIT_UNIT}})

---

## Summary

| # | Reviewer point | Section | Status | Decision |
|---|---|---|---|---|
<!-- one row per point -->

**Overall outcome**: {{OVERALL_OUTCOME}}

---

## Point Details

<!--
For each point, one section:

### {{N}} — {{TITLE}}

**Reviewer observation**: {{QUOTE}}

**Current status (v{{VERSION}}, line {{LINE}})**:

> {{CURRENT_TEXT}}

**Verdict**: {{POINT_OUTCOME}}

**Applied change** (commit `{{COMMIT_HASH}}`, if any):
- {{SHORT_CHANGE_DESCRIPTION}}

---
-->

## Character/Word Limit — Pending Recoveries

| # | Section | What to remove | Estimated recovery |
|---|---|---|---|
<!-- candidates from `scripts/char_count.py --suggest-cuts` -->

---

## Response-letter Material

<!--
Populate only when Feedback source = journal. One block per journal point that
needs an answer to the reviewer. When source = simulated, replace this whole
section with the single line: "Internal simulation — not for the journal."

### {{N}} — {{TITLE}}
**Reviewer point**: {{QUOTE}}
**Response**: {{HOW_ADDRESSED}}
**Data disclosure** (if a figure was corrected vs a prior submitted version):
{{OLD_VALUE}} → {{NEW_VALUE}} — {{CAUSE}}
-->

---

## Internal QA Carried This Round

<!--
Simulated / self-review points processed this round (Feedback source = simulated,
or simulated points in a mixed round). Listed for the project record only;
never sent to the journal.
-->

---

## Outstanding Tasks Before Submission

- [ ] {{TASK_1}}
- [ ] {{TASK_2}}
- [ ] Disclose in the response letter every numeric claim corrected vs a prior submitted version (journal rounds only).

---

## Change History

<!-- summary generated from `revision(...)` commits or from the revision plan -->
