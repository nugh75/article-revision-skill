# 10 — Read-Only Setup

Load revision context without creating a version or task file. Run after
bootstrap only when required infrastructure already exists or its creation has
been separately approved.

## Load context

1. Locate `.env` from the current directory upward. Read the configured article
   language, editorial limits, norms path, bibliography path, data-verification
   pointers, and checkpoint thresholds.
2. Read the applicable editorial norms and bibliography metadata.
3. Identify the active Markdown manuscript by the highest `vN`, including an
   `articles/versions/` directory. Treat `-drive` as provenance, not part of a
   future canonical filename.
4. Detect the body language unless `ARTICLE_LANG` overrides it.
5. Read an existing freeze ledger without updating it. If absent, report that
   units are currently untracked; do not create the ledger during diagnosis.

If a paused task exists and the user asked to resume, call
`06-handoff.md#resume`. If a paused task exists but the request is clearly a new
read-only audit, leave it untouched.

## Setup summary

Report article path/version, language, norms, length budget, bibliography, and
freeze snapshot. For diagnosis or proposals, continue read-only: no bump, task
file, sidecar, ledger update, sync, commit, or push.

## Select the write transition

If the user explicitly named a target file/version and requested one bounded
application without versioning or session tracking, set
`EXECUTION_MODE=direct-apply` and call `11-direct-apply.md`. Do not enter the
tracked transition below.

For reviewer rounds, iterative revision, accepted structural changes, requested
versioning, ledger/task work, or explicit tracking, set
`EXECUTION_MODE=tracked-round`. A named target does not make a structural move,
reordering, split, merge, or cut eligible for direct application; route it
through `13-content-structure.md`.

## Transition to a tracked edit

When the user first accepts a file edit in `tracked-round` mode:

1. Revalidate the source and freeze state.
2. Call `60-bump-version.md mode=first-edit`.
3. Call `05-task.md action=create` with the new version.
4. Call `15-freeze-ledger.md action=ensure` and reconcile it to that version.
5. Apply the accepted edit.

A complete `/r-auto <task> --scope "<scope>"` is prior authorization for this
first-edit transition. It still does not authorize Git unless `--git` is present.

Before an authorized Git action, perform the branch/upstream preflight from
`07-git-checkpoint.md`; Git state does not block read-only diagnosis.
