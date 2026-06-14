# 70 — Final Sheet

Generates `revisions/<slug>/final-sheet-vN.md`, summarizing the round's outcome.

## 1. Source Material

Read:

- the project file (`revision-plan-vN.md`) to extract decisions per point;
- `git log` filtered to commits matching `revision(<slug>):` since the start of the round, if commits exist;
- `bibliography-audit-vN.md` if any bibliography check happened;
- the current char/word count.

## 1a. Read Feedback Provenance

Read `{{FEEDBACK_SOURCE}}` from the project file's *Summary Status* (`journal` or `simulated`). It governs how the sheet is split:

- `journal` — these points are answerable to the journal. The sheet's *Response-letter material* section is populated and is the basis for the reply to reviewers.
- `simulated` — internal QA. The *Response-letter material* section stays empty with the note `Internal simulation — not for the journal.` Simulated points must never appear in a response letter.

If the round mixed sources (some points journal, some simulated — possible when a self-review was layered on a real round), separate them: only `journal`-tagged points go into response-letter material; `simulated` ones are listed under *Internal QA carried this round*.

Carry forward any data-verification verdicts (`51-data-verification.md` §5): for `journal` feedback, every **Corrected / Unreproducible / Inconsistent** figure that also existed in a prior submitted version is listed in *Outstanding tasks* as a disclosure the response letter must make explicit.

## 2. Fill Template

Use `templates/final-sheet.md` and substitute placeholders. The summary table at the top should report, per point:

| Status | Meaning |
|---|---|
| Accepted | Proposal applied |
| Modified | Proposal reformulated and then applied |
| Rejected | No text modification |
| Deferred | Requires external data or a later decision |

## 3. Recovery Suggestions

If the article is over the editorial limit, populate the *Pending recoveries* section with concrete suggestions, such as duplicate prose or redundant section openings. Run:

```bash
scripts/char_count.py <article> --limit-from-env
```

Then propose 3–5 candidate cuts with estimated savings.

## 4. Outstanding Tasks

In the *Outstanding tasks before submission* checklist, list:

- `Deferred` entries from the project file;
- bibliography entries still flagged from the audit;
- character overshoot to recover;
- anonymisation pass, if `-anonymous` suffix is present and there are remaining placeholders the user wants resolved before submission;
- any external check the user mentioned.

## 5. Change History

Pull from `git log` if commits exist:

```bash
git log --oneline --grep "revision(<slug>):" --since "<date round started>"
```

Format as a bulleted list under the *Change history* heading.

## 6. Suggested Commit

The skill writes the final sheet but **does not commit**. Suggested commit message for the user:

```text
revision(<slug>): final sheet — round closed
```

## 7. Hand Off

After writing the final sheet, the workflow must always hand off to
`workflow/95-decision-log.md`. This handoff is mandatory even when:

- the round produced no accepted changes;
- the user stopped after a partial pass;
- the outcome is rejected or deferred;
- no git commit exists.

Final chat message:

```text
Final sheet: revisions/<slug>/final-sheet-vN.md

Round closed. Summary:
- <X> accepted, <Y> modified, <Z> rejected, <W> deferred
- count: <M> {chars|words} (<over|under> by <N>)
- bibliography: <status>
- outstanding tasks: <short list>
```

The skill ends here. The next round starts a new project file with version vN+1, or the same N+1 if the user prefers continuing.
