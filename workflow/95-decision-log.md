# 95 — Decision Log Closure

Mandatory end-of-round closure step. Record the revision round in the project's
`revisions/decision-log/` structure, compatible with the `decision-log` skill.

## 1. Inputs

Read:

- the current article path and version;
- the active project file (`revision-plan-vN.md`);
- the final sheet, if already generated;
- any `proposal-revision-YYYY-MM-DD-HHMM.md` files created during the round;
- the latest `revisions/decision-log/index.md` and most recent session file.

## 2. Determine Session Metadata

Create one new session in `revisions/decision-log/` with the next sequential
identifier `session-NNN.md`.

Frontmatter rules:

- `tool: codex`
- `type`: choose the dominant round type:
  - `revision-content`
  - `revision-structure`
  - `revision-style`
  - `revision-global`
  - `revision-connector`
  - `version-bump`
- `decision`:
  - `accepted` if all logged points were accepted
  - `partial` if mixed outcomes occurred
  - `rejected` if all points were rejected
  - `modified` if the round mainly accepted user-modified proposals
  - `deferred` if nothing was applied and work was postponed
- `suggestion`: one-line summary of the round
- `rationale`: concise explanation of the human decision direction

## 3. Session Body

Write these sections:

```markdown
## Contesto
<round scope, article version, reviewer lane, and whether the work was partial/full>

## Proposta macchina
<brief synthesis of the proposals made this round; if multi-mod files exist, cite them by filename>

## Decisione umana
<A/R/M outcomes and explicit rationale>

## Modifiche applicate
<flat bullet list of actual edits written to the article, or "Nessuna modifica applicata">

## Note
<open items, deferred issues, next step>
```

## 4. Update Index

Prepend the new session row to `revisions/decision-log/index.md`:

| Sessione | Data | Tool | Tipo | Decisione | Oggetto |

Use the new session number, today's date, `codex`, the chosen type, the chosen
decision, and the short suggestion text.

## 5. Binding Rule

This workflow is mandatory at the end of every revision round. The round is not
considered closed until the decision log session and the index are both
updated.
