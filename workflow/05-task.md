# 05 — Task File

Manages the per-session task file at
`revisions/<article-slug>/task-<command-slug>-<bumped-version>.md`.
Every revision session has exactly one task file; it tracks steps in real time
and provides the input summary for `95-decision-log.md`.

## When to invoke

| Action | Called by |
|---|---|
| `create` | `workflow/10-setup.md` — immediately after the mandatory bump |
| `update-step` | Any workflow file when a named step reaches a new status |
| `close` | `workflow/95-decision-log.md` — before writing the session entry |

---

## 1. create

**Inputs** (from working memory after `10-setup.md`):

- `COMMAND` — slash command that triggered the session (e.g. `/r-pp`, `/r-chapter`).
- `ARTICLE_PATH` — path to the active article file.
- `ARTICLE_SLUG` — article filename prefix before `-vN` (e.g. `article`).
- `ARTICLE_VERSION` — original version identifier (e.g. `v3`).
- `BUMPED_VERSION` — new version identifier after the mandatory bump (e.g. `v4-2026-06-16-1430`).
- `REVIEWER_LANE` — reviewer slug, simulated label, or `self` for proactive modes (`/r-pp`, `/r-global`, `/r-chapter`, `/r-conn`).

**Step list** (rows 3..N of the `## Passi` table) by command:

| Command | Steps (in order) |
|---|---|
| `/article-revision` | Plan revision · Iterate points · Bibliography check · Final sheet · Decision log |
| `/r-pp` | Parse paragraphs · Walk P1..PN · Bibliography check · Final sheet · Decision log |
| `/r-pp-a` | Parse paragraphs · Walk P1..PN (deep) · Bibliography check · Final sheet · Decision log |
| `/r-pr-2` | Generate Reviewer A · Generate Reviewer B · Synthesize · Decision log |
| `/r-conn` | Parse transitions · Diagnose · Fix selected · Decision log |
| `/r-global` | Read article · Seven lenses · Fix selected · Decision log |
| `/r-chapter` | Select section · Load article · Cross-article analysis · Fix selected · Decision log |
| `/r-redline` | Generate redline · Response letter · Decision log |
| `/r-approve` | Load approvals · Apply outcomes · Decision log |

All initial step statuses: `pending`. Steps 1 and 2 are pre-filled as `done`.

**File path**:
`revisions/<article-slug>/task-<command-slug>-<bumped-version>.md`

Where `<command-slug>` strips the leading `/` (e.g. `r-pp`, `r-chapter`,
`article-revision`).

**Template**: use `templates/task.md`. Fill all `{{...}}` placeholders.
`{{STEPS_ROWS}}` = one table row per step listed above, all with status `pending`.

Confirm in chat (one line):
```
Task file: revisions/<article-slug>/task-<command-slug>-<bumped-version>.md
```

Store `TASK_FILE_PATH` in working memory for the session.

---

## 2. update-step

**Called with**: step name (must match the exact string in column "Passo") +
new status + optional note.

**Status values**: `pending` → `in-progress` → `done` | `skipped` | `failed`

**Procedure**:

1. Read `TASK_FILE_PATH`.
2. Find the row whose "Passo" cell matches the step name exactly.
3. Replace the "Stato" cell with the new status (wrapped in backticks).
4. If a note is provided, append it to the "Note" cell.
5. Write back with the Edit tool (surgical replace of that row only).

Do not output this update in chat unless the new status is `failed`.
If `failed`: output one line `⚠ Step "<name>" failed — <note>` and wait for user.

---

## 3. close

**Called by `95-decision-log.md`** before writing the session entry.

**Procedure**:

1. Read `TASK_FILE_PATH`.
2. Set any `pending` or `in-progress` step to:
   - `skipped` — if the session ended normally but that step was not applicable.
   - `failed` — only for the step that was active when an abnormal end occurred.
3. Fill in `## Riepilogo`:
   - **Accettati**: total accepted modifications this session (from working memory counter).
   - **Rifiutati**: total rejected.
   - **Modificati**: total accepted-after-modify.
   - **Rinviati**: total deferred.
4. Fill in `## Stato articolo alla chiusura`:
   - **Versione finale**: path to the active article file at session end.
   - **Caratteri**: current char count + " / " + limit from `.env`.
   - **Decision log**: the session identifier that `95-decision-log.md` will write (e.g. `session-042`).
5. Change frontmatter `status`:
   - `completed` — all core steps reached `done`.
   - `partial` — some core steps were `skipped`.
   - `abandoned` — session cut short (one step `failed`).
6. Write back.

Return the `## Riepilogo` and `## Stato articolo alla chiusura` content to
`95-decision-log.md` for inclusion in the "Note" section of the session body.
