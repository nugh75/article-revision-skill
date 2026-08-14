# 07 — Automatic Git Checkpoint

Create and push a scoped Git checkpoint after a configured number of applied
changes, and flush any remaining session state at handoff or closure. The user
has authorized these routine commit/push operations by using this skill; do not
ask again for each checkpoint.

## Configuration and state

- `AUTO_GIT_CHECKPOINT_THRESHOLD` is a positive integer; default `5`.
- One **change** is one numbered modification applied in an interactive flow.
  In `/r-auto`, one integrated changed manifest unit counts as one change.
- Store these fields in `TASK_FILE_PATH` frontmatter:
  `changes-since-git-checkpoint`, `git-checkpoint-sequence`, and
  `git-checkpoint-threshold`.
- Keep this counter independent from `accepted_since_bump` and
  `AUTO_BUMP_THRESHOLD`.

## When to invoke

Invoke with `mode=threshold` immediately after the article and all associated
session records for an applied change have been updated, whenever the counter
reaches the configured threshold.

Invoke with `mode=flush` after handoff sync or successful closure sync, even
when the counter is below the threshold. Do not create an empty commit.

For `/r-auto`, integrate at most the remaining number of units before the next
threshold. Before each mid-run checkpoint, run a bounded audit on that batch
using the scope, preservation, citation/number, and `git diff --check`
invariants from `37-scoped-auto-revision.md`. Push only after that audit passes.
The final independent whole-run audit remains mandatory.

## Session file manifest

Build an explicit path list. Include only files created or changed by the
active revision session:

- `TASK_FILE_PATH` and `ARTICLE_PATH`;
- the active revision plan/project file;
- freeze ledger and proposal sidecars changed by this session;
- bibliography/data audits or bibliography files changed by this session;
- `/r-auto` manifest, worker reports, and audit reports;
- decision-log files, final sheet, and synchronized current exports only after
  the workflow that creates them has completed.

Never include `.env`, repository-wide globs, or unrelated user files. Never use
`git add -A`, `git add .`, or an unresolved wildcard.

## Preflight and execution

1. Confirm `TASK_FILE_PATH` exists and the threshold is a positive integer.
2. Confirm the current branch has one unambiguous upstream. Do not infer a new
   remote or branch and do not create one automatically.
3. If unrelated paths are already staged, stop before changing the index.
4. For `mode=threshold`, increment `git-checkpoint-sequence` and reset
   `changes-since-git-checkpoint` to `0` in the task file before committing.
   For `mode=flush`, increment the sequence only if session files actually
   differ from `HEAD`; reset a non-zero counter before committing. If the task
   already has a filled `## Riepilogo`, update `Checkpoint Git pubblicati` to
   the new sequence before committing.
5. Run the deterministic helper from the project root:

   ```bash
   /absolute/path/to/article-revision/scripts/git_checkpoint.sh \
     --repo <project-root> \
     --message "revision(<article-slug>): checkpoint <sequence> — <N> changes" \
     -- <explicit-session-file>...
   ```

   Use `revision(<article-slug>): handoff — <unit>` for a handoff flush and
   `revision(<article-slug>): close <version>` for a closure flush.

6. Parse the helper output. On `status=pushed`, report the short hash and
   `<remote>/<branch>` in one line and continue without asking permission.
7. On `status=noop`, restore any counter/sequence changed solely for this
   attempt and continue.
8. If the commit succeeds but push or remote verification fails, preserve the
   local commit, stop the revision workflow, and report the hash plus exact
   failure. On resume, retry that push before accepting new changes.
9. On any preflight, hook, staging, fetch, or commit failure, restore the task
   counter if it was not committed, leave all content intact, and stop. Never
   pull, merge, rebase, amend, reset, force-push, or bypass hooks automatically.

## Hard rules

- Scope safety outranks checkpoint frequency: never absorb unrelated work.
- A successful push must be verified by comparing `HEAD` with `git ls-remote`.
- Automatic checkpoints do not authorize PRs, tags, releases, Drive writes,
  or changes outside the revision session.
- Routine checkpoints are pre-authorized; ambiguous or unsafe Git state is a
  stop condition, not a reason to ask for routine commit/push permission.
