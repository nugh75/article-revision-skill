# 06 — Handoff / Resume

Creates a resumable checkpoint for an unfinished revision session. This is not
revision closure: it does not run `95-decision-log.md`, does not sync current
files, and does not mark the round complete.

## When to invoke

Invoke this workflow whenever:

- the user says `pause`, `stop`, `sospendi`, `interrompi`, `riprendiamo dopo`,
  `handoff`, or `/r-handoff`;
- the agent is about to stop while a revision point, paragraph, section, lens,
  or approval pass is still open;
- a long-running pass reaches a natural waiting point and state has changed
  since the last checkpoint.

Every revision workflow may call this step at any time. The user should be able
to resume from the checkpoint without relying on chat history.

## 1. Write Handoff Checkpoint

Use the existing `TASK_FILE_PATH`. Do not create a separate handoff file unless
there is no task file; if `TASK_FILE_PATH` is missing, ask before creating a
minimal checkpoint under `revisions/<article-slug>/handoff-<YYYY-MM-DD-HHMM>.md`.

Update the task file:

1. Frontmatter `status`: set to `paused`.
2. In `## Passi`, leave the current step as `in-progress`; do not mark it
   `skipped`, `failed`, or `done` unless that is already true.
3. Fill or replace the `## Handoff / Ripresa` section with:

   ```markdown
   ## Handoff / Ripresa

   - **Ultimo aggiornamento**: <YYYY-MM-DD HH:MM>
   - **Stato**: paused
   - **Comando**: <COMMAND>
   - **Articolo di lavoro**: <ARTICLE_PATH>
   - **Versione di lavoro**: <BUMPED_VERSION>
   - **Fase corrente**: <workflow step name>
   - **Unità corrente**: <point id | P<N> | §N | lens | transition group>
   - **Ultima proposta mostrata**: <none|sidecar path|short title>
   - **Decisioni già prese**: <brief counts and statuses>
   - **Decisioni pendenti**: <exact item numbers/categories still open>
   - **Tracce/fonti da ricaricare**: <freeze ledger, global trace, reviewer plan, approval file, data source>
   - **File modificati finora**: <article/bib/task/proposal files>
   - **Prossima azione esatta**: <one concrete instruction for the next agent>
   - **Avvertenze**: <risks, frozen units, unresolved data/citation checks>
   ```

4. If there is a sidecar proposal file (`proposal-revision-*.md`), append the
   same checkpoint to its `Decision Trail`.
5. If a deferred intention appears in the handoff, also record it in the freeze
   ledger via `15-freeze-ledger.md#log-comment`; never leave deferred intentions
   only in the task file.

## 2. Chat Output

Output a concise handoff block:

```text
Handoff scritto.
- Task file: <TASK_FILE_PATH>
- Stato: paused
- Ripresa: <Prossima azione esatta>
```

If pending user decisions remain, list them explicitly:

```text
Decisioni pendenti: <items>
```

## 3. Resume From Handoff

When the user asks to resume (`riprendi`, `resume`, `continua`, `/r-resume`, or
re-invokes the same command in a project with a paused task file):

1. Search `revisions/<article-slug>/task-*-*.md` for frontmatter
   `status: paused` or `status: in-progress`.
2. Prefer the newest task whose `article` path exists. If several match, show the
   candidates and ask which one to resume.
3. Load `## Handoff / Ripresa` and the files listed under
   `Tracce/fonti da ricaricare`.
4. Treat resume as continuation of the existing revision session:
   - do **not** run a new mandatory bump;
   - do **not** create a new task file;
   - set `TASK_FILE_PATH`, `ARTICLE_PATH`, `BUMPED_VERSION`, and command-specific
     state from the task file;
   - set frontmatter `status: in-progress`;
   - update `Ultimo aggiornamento` and `Stato`.
5. In chat, confirm:

   ```text
   Ripresa da handoff.
   - Task file: <TASK_FILE_PATH>
   - Articolo: <ARTICLE_PATH>
   - Prossima azione: <Prossima azione esatta>
   ```

6. Continue exactly from the recorded next action. If the checkpoint is
   ambiguous, ask one clarifying question and keep the task paused until the user
   answers.

## 4. Hard Rules

- Handoff never replaces the mandatory closure sequence. When the user later
  closes the round, still run `95-decision-log.md` and `96-sync-current.md`.
- Handoff never commits, stages, pushes, or syncs current files.
- Handoff never silently discards a pending proposal. Record pending item numbers,
  categories, and the exact next action.
- A resumed session is not a new revision session and must not trigger a new
  version bump unless the user explicitly starts a new session.
