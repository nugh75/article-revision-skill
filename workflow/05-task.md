# 05 — Task File

Manages the per-session task file at
`revisions/<article-slug>/task-<command-slug>-<bumped-version>.md`.
Every tracked edit round has exactly one task file; diagnostic-only sessions
have none. The file tracks applied work and provides the input summary for
`95-decision-log.md`.

## When to invoke

| Action | Called by |
|---|---|
| `create` | `workflow/10-setup.md` — after the first-edit working version is created |
| `update-step` | Any workflow file when a named step reaches a new status |
| `handoff` | `workflow/06-handoff.md` — whenever work is paused or may be interrupted |
| `resume` | `workflow/06-handoff.md` — when continuing from a paused task file |
| `close` | `workflow/95-decision-log.md` — before writing the session entry |

---

## 1. create

**Inputs** (from working memory after `10-setup.md`):

- `COMMAND` — slash command that triggered the session (e.g. `/r-pp`, `/r-chapter`).
- `ARTICLE_PATH` — path to the active article file.
- `ARTICLE_SLUG` — article filename prefix before `-vN` (e.g. `article`).
- `ARTICLE_VERSION` — original version identifier (e.g. `v3`).
- `BUMPED_VERSION` — working version created before the first accepted edit (e.g. `v4-2026-06-16-1430`).
- `REVIEWER_LANE` — reviewer slug, simulated label, or `self` for proactive modes (`/r-pp`, `/r-global`, `/r-chapter`, `/r-conn`).
- `AUTO_GIT_CHECKPOINT_THRESHOLD` — positive integer loaded by setup; default
  `5`. It is the dedicated prompt threshold in interactive chat. It is automatic
  only for `/r-auto ... --git`.

**Step list** (rows 3..N of the `## Passi` table) by command:

| Command | Steps (in order) |
|---|---|
| `/article-revision` | Plan revision · Iterate points · Bibliography check · Handoff checkpoint · Final sheet · Decision log · Sync derived exports |
| `/r-pp` | Parse paragraphs · Walk P1..PN · Bibliography check · Handoff checkpoint · Final sheet · Decision log · Sync derived exports |
| `/r-pp-a` | Parse paragraphs · Walk P1..PN (deep) · Bibliography check · Handoff checkpoint · Final sheet · Decision log · Sync derived exports |
| `/r-pr-2` | Generate Reviewer A · Generate Reviewer B · Synthesize · Handoff checkpoint · Decision log · Sync derived exports |
| `/r-conn` | Parse transitions · Diagnose · Fix selected · Handoff checkpoint · Decision log · Sync derived exports |
| `/r-structure` | Inventory units · Map current/proposed architecture · Apply accepted structure · Preservation audit · Handoff checkpoint · Decision log · Sync derived exports |
| `/r-redundancy` | Build proposition map · Classify clusters · Apply accepted decisions · Preservation audit · Handoff checkpoint · Decision log · Sync derived exports |
| `/r-global` | Read article · Seven lenses · Save trace or fix selected · Handoff checkpoint · Decision log · Sync derived exports |
| `/r-chapter` | Select section · Load article · Cross-article analysis · Fix selected · Handoff checkpoint · Decision log · Sync derived exports |
| `/r-auto` | Resolve scope manifest · Delegate proposals · Integrate patches · Independent audit · Bibliography check · Final sheet · Decision log · Sync derived exports |
| `/r-redline` | Generate redline · Response letter · Handoff checkpoint · Decision log · Sync derived exports |
| `/r-approve` | Load approvals · Apply outcomes · Handoff checkpoint · Decision log · Sync derived exports |

All command-specific rows in `{{STEPS_ROWS}}` start as `pending`. The fixed
template rows `Bootstrap & Setup` and `Version bump` are pre-filled as `done`
because task creation occurs only after that first-edit boundary.

**File path**:
`revisions/<article-slug>/task-<command-slug>-<bumped-version>.md`

Where `<command-slug>` strips the leading `/` (e.g. `r-pp`, `r-chapter`,
`article-revision`).

**Template**: use `templates/task.md`. Fill all `{{...}}` placeholders.
`{{STEPS_ROWS}}` = one table row per step listed above, all with status `pending`.
Set the Git checkpoint frontmatter fields to the configured threshold, counter
`0`, last-prompt count `0`, and sequence `0`.

Confirm in chat (one line):
```
Task file: revisions/<article-slug>/task-<command-slug>-<bumped-version>.md
```

Store `TASK_FILE_PATH` in working memory for the session.

---

## 2. update-step

**Called with**: step name (must match the exact string in column "Passo") +
new status + optional note.

**Status values**: `pending` → `in-progress` → `done` | `skipped` | `failed` | `paused`

**Procedure**:

1. Read `TASK_FILE_PATH`.
2. Find the row whose "Passo" cell matches the step name exactly.
3. Replace the "Stato" cell with the new status (wrapped in backticks).
4. If a note is provided, append it to the "Note" cell.
5. Write back with the Edit tool (surgical replace of that row only).

Do not output this update in chat unless the new status is `failed`.
If `failed`: output one line `⚠ Step "<name>" failed — <note>` and wait for user.

---

## 3. handoff

Called by `workflow/06-handoff.md`.

**Procedure**:

1. Read `TASK_FILE_PATH`.
2. Set frontmatter `status: paused`.
3. Set the `Handoff checkpoint` row to `paused` or `done`:
   - `paused` if the round is being interrupted now;
   - `done` if the checkpoint is a routine save but the agent continues.
4. Replace the `## Handoff / Ripresa` section using the fields defined in
   `workflow/06-handoff.md`.
5. Write back. Do not close the task file.
6. `workflow/06-handoff.md` then calls `95-decision-log.md` in `handoff` mode
   and `96-sync-current.md` in `handoff` mode. Record those results as notes on
   the `Handoff checkpoint` row; leave final `Decision log` and `Sync current
   files` rows available for closure.

## 4. resume

Called by `workflow/06-handoff.md`.

**Procedure**:

1. Read the selected paused task file.
2. Set frontmatter `status: in-progress`.
3. Set `Handoff checkpoint` row to `in-progress`.
4. Update `## Handoff / Ripresa`:
   - `Stato`: `resumed`
   - `Ultimo aggiornamento`: current timestamp
   - keep `Prossima azione esatta` unless the user changes it.
5. Restore working memory from the task file fields.
6. Restore the Git checkpoint threshold, counter, last-prompt count, and
   sequence. For legacy task files without `git-checkpoint-last-prompt-count`,
   default it to `0`. If a previously authorized commit did not push, report it
   and ask before retrying; do not reinterpret resume as Git authorization.

## 5. close

**Called by `95-decision-log.md`** before writing the session entry.

**Procedure**:

1. Read `TASK_FILE_PATH`.
2. Set any `pending` or `in-progress` step to:
   - `skipped` — if the session ended normally but that step was not applicable.
   - `failed` — only for the step that was active when an abnormal end occurred.
3. Fill in `## Riepilogo`:
   - **Accettati**: total accepted modifications this session (from working memory counter).
   - **Da considerare**: total items kept as deferred/context.
   - **Modificati**: total accepted-after-modify.
   - **Rinviati**: total deferred for external data or later decision.
   - **Checkpoint Git pubblicati**: count from `git-checkpoint-sequence`.
4. Fill in `## Stato articolo alla chiusura`:
   - **Versione finale**: path to the active article file at session end.
   - **Caratteri**: current char count + " / " + limit from `.env`.
   - **Decision log**: the session identifier that `95-decision-log.md` will write (e.g. `session-042`).
5. Change frontmatter `status`:
   - `completed` — all core steps reached `done`.
   - `partial` — some core steps were `skipped`.
   - `paused` — only if the user requested handoff and closure was cancelled.
   - `abandoned` — session cut short (one step `failed`).
6. Write back.

Return the `## Riepilogo` and `## Stato articolo alla chiusura` content to
`95-decision-log.md` for inclusion in the "Note" section of the session body.
