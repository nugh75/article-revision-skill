# 95 — Decision Log

Mandatory decision-log step. Record either a revision-round closure or a
handoff checkpoint in the project's `revisions/decision-log/` structure,
compatible with the `decision-log` skill.

## Modes

| Mode | Called by | Effect |
|---|---|---|
| `closure` | explicit/natural revision closure | close the task file, write a final session entry, then sync current files |
| `handoff` | `workflow/06-handoff.md` | write a checkpoint session entry, then sync current files without closing the task |

Default to `closure` unless the caller explicitly says `mode=handoff`.

## 0. Close Task File

In `closure` mode, before reading any inputs, call `workflow/05-task.md` —
action `close`.

This fills in the task file's `## Riepilogo` and `## Stato articolo alla chiusura`
sections. The returned summary is used in step 3 (§ Note) of the session body below.

If `TASK_FILE_PATH` is not set in working memory (e.g. the session predates the
task file feature), skip this step silently.

In `handoff` mode, do **not** call `workflow/05-task.md#close` and do not mark
the round complete. Read the current `## Handoff / Ripresa` section from
`TASK_FILE_PATH` and use it as the checkpoint summary.

## 1. Inputs

Read:

- the current article path and version;
- the active project file (`revision-plan-vN.md`);
- the final sheet, if already generated;
- any `proposal-revision-YYYY-MM-DD-HHMM.md` files created during the round;
- in `handoff` mode: the current `## Handoff / Ripresa` checkpoint;
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
  - `revision-chapter`
  - `version-bump`
  - `handoff-checkpoint` (only in `handoff` mode)
- `decision`:
  - `accepted` if all logged points were accepted
  - `partial` if mixed outcomes occurred
  - `modified` if the round mainly accepted user-modified proposals
  - `deferred` if nothing was applied and work was postponed
  - `paused` if this is a handoff checkpoint
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
<Accetta / Modifica / Rivedi completamente / Tieni in considerazione outcomes and explicit rationale>

## Modifiche applicate
<flat bullet list of actual edits written to the article, or "Nessuna modifica applicata">

## Note
<open items, deferred issues, next step>
<if a task file was closed in step 0: include its Riepilogo and Stato articolo alla chiusura here>
<if mode=handoff: include Handoff / Ripresa fields, pending decisions, and exact next action>
<freeze ledger snapshot: 🟢 X frozen · 🟡 Y open; list units frozen this round and any 🟡 open intentions still pending (read from revisions/<article-slug>/freeze-ledger.md)>
```

## 4. Update Index

Prepend the new session row to `revisions/decision-log/index.md`:

| Sessione | Data | Tool | Tipo | Decisione | Oggetto |

Use the new session number, today's date, `codex`, the chosen type, the chosen
decision, and the short suggestion text.

## 5. Binding Rule

This workflow is mandatory:

- at the end of every revision round (`closure` mode);
- at every handoff (`handoff` mode).

In `closure` mode, the round is not considered closed until the decision log
session, the index, and the current files (step 6) are all updated.

In `handoff` mode, the round remains paused/resumable after the decision-log
entry and sync; the handoff is not complete until both are done.

## 6. Sync Current Files (mandatory)

Immediately after writing the session entry and updating `index.md`, run
`workflow/96-sync-current.md` with the same mode (`closure` or `handoff`).

This step is **not optional** in either mode. It overwrites:
- `articles/current.md` — copy of the active article version
- `articles/current.docx` — pandoc conversion of `current.md`
- `bibliography/bibliography.docx` — formatted reference list from `reference.bib`

If pandoc is not available, `96-sync-current.md` warns and skips `.docx`
generation without aborting the closure.

In `closure` mode, add the sync result to the task file step `Sync current
files` via `workflow/05-task.md#update-step`.

In `handoff` mode, add the sync result to the task file step `Handoff
checkpoint` as a note; leave `Sync current files` available for final closure.
