# Revision Final Sheet {{REVIEWER}} — v{{VERSION}} Status

- **Article**: `{{ARTICLE_PATH}}`
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

## Outstanding Tasks Before Submission

- [ ] {{TASK_1}}
- [ ] {{TASK_2}}

---

## Change History

<!-- summary generated from `revision(...)` commits or from the revision plan -->
