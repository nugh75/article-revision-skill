# 35 — Colleague Approval

Triggered by `/r-approve`. Gates accepted modifications behind colleague
sign-off before they are treated as final for the response letter and the
clean submission. Runs after a revision pass has produced `Accepted`
points and (usually) after `/r-gdrive sync` has pulled colleague input.

## Point state machine (extends the project file)

```
To decide → Proposed → Accepted → Colleague-review → Colleague-approved → Final
                               ↘ Colleague-changes-requested ↘ (re-propose)
                               ↘ Rejected
```

`Accepted` means the author/user accepted it via `Accetta`. `Colleague-approved`
means a colleague signed off. Only `Colleague-approved`/`Final` points are
listed as settled in `response-to-reviewers`; `Accepted`-but-not-approved
points are flagged as pending in the final sheet.

Record per point in the project file:
`<!-- approval: pending|approved|changes|na  by:<name>  date:<YYYY-MM-DD> -->`

## Inputs (both supported)

1. **Google Doc suggestions** — colleagues accept/comment in the shared
   Doc. Pulled by `/r-gdrive sync`. If the connector cannot read inline
   comments, fall back to (2).
2. **Structured `approvals.md`** — table in the Drive folder (template
   `templates/approvals.md`): one row per point id →
   `approve | changes | reject` + note + colleague name.

When both exist, the structured `approvals.md` row wins for that point
(explicit verdict beats inferred-from-comment); note the divergence in chat.

## Procedure

1. Load the project file points and the latest
   `revisions/<slug>/sources/drive-feedback-*.md` / `approvals.md`.
2. Build an approval table and show it — do not change files yet:

   ```
   ## Colleague Approval — <slug>

   | Point | Title | Author state | Colleague | Verdict | Note |
   |---|---|---|---|---|---|
   | P1 | … | Accepted | C. Rossi | approve | — |
   | P3 | … | Accepted | C. Rossi | changes | "soften claim" |
   | P5 | … | Accepted | (none)   | pending | no feedback yet |
   ```

3. For each `approve`: set `approval: approved` in the project file. No
   text change (already applied at `Accetta`).
4. For each `changes`: re-open the point as a new proposal incorporating
   the colleague's note, via the standard decision block in
   `30-iterate-points.md`. Apply on `Accetta`; set `approval: approved` once
   re-accepted.
5. For each `reject`: present to the user — a colleague reject does not
   auto-revert. Ask `keep / revert / modify`. Only revert on explicit user
   instruction (respect the git contract; never commit).
6. Leave `pending` points untouched; list them so the user can chase
   feedback.

## Output

Append an **Approval log** section to the project file:

```markdown
## Approval Log
- P1 — approved — C. Rossi — 2026-05-20
- P3 — changes → re-accepted — C. Rossi — 2026-05-20
```

Then in chat: counts (approved / changes / reject / pending) and the next
suggested step (`/r-redline`, `/r-sheet`, or chase pending). Never commit
automatically.
