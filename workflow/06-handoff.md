# 06 — Local Handoff / Resume

Preserve enough local state to resume an unfinished tracked revision. Handoff
does not imply Git publication.

## Invocation modes

- Natural `pause`, `stop`, `sospendi`, or `interrompi`: pause locally.
- `/r-handoff`: write the local checkpoint, decision-log checkpoint, and derived
  exports when a tracked task exists.
- `/r-handoff --git` or an explicit `commit e push`: do the same local work,
  then call `07-git-checkpoint.md` with authorized flush mode.

## No tracked round

If `TASK_FILE_PATH` is absent, do not create a file merely because the user
paused. Return a chat summary containing scope, last proposal, pending decisions,
and the exact next action. No bump, sync, decision log, commit, or push occurs.

## Write the checkpoint

For an existing task file, set `status: paused`, keep the current workflow step
`in-progress`, and fill `## Handoff / Ripresa` with:

- timestamp, command, article and version;
- current phase and exact paragraph/section locator;
- last proposal and decisions already made;
- pending decisions and sources to reload;
- active-session files changed so far;
- risks, frozen units, and the exact next action.

Record deferred intentions in the freeze ledger only when that ledger already
belongs to the tracked round. Do not create a new sidecar during handoff.

For explicit `/r-handoff`, run `95-decision-log.md mode=handoff` and
`96-sync-current.md SYNC_MODE=handoff`. A natural pause may stop after the task
checkpoint unless the user also requested a full handoff.

## Optional Git publication

Set `GIT_AUTHORIZED=true` only for `/r-handoff --git` or an explicit request to
commit and push. Then call `07-git-checkpoint.md mode=flush-authorized` with an
explicit active-session manifest. Without that authorization, report:

```text
Handoff locale scritto. Nessun commit o push eseguito.
```

## Resume

On `/r-resume`, `riprendi`, or `continua`:

1. Find the newest matching task with `status: paused` or `in-progress`.
2. Load its handoff section and referenced sources.
3. Restore its article path, command, counters, and exact next action.
4. Set the task to `in-progress` and continue without another bump.
5. If a prior explicitly authorized commit succeeded but its push failed, ask
   whether to retry that push before publishing any new checkpoint. Local prose
   work may continue when doing so is safe.

Never discard a pending proposal or include unrelated paths in a later Git
manifest.
