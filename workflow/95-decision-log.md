# 95 — Decision Log and Local Closure

Record tracked revision state. Diagnostic-only sessions without a task file do
not create a decision log merely because the conversation ended.

## Modes

- `closure`: close the task, write the final session entry, and generate derived
  exports after the user confirms local closure.
- `handoff`: write a checkpoint session entry and sync without closing the task;
  used only for explicit `/r-handoff`.
- `auto-closure`: write the final automatic session, run strict sync, and close
  the task after PASS.

Carry `GIT_AUTHORIZED=true|false` separately from the mode.

## Record

Read the active article, task, plan or auto manifest, proposal/audit artifacts,
freeze ledger, and prior decision-log index. Create the next `session-NNN.md`
with context, machine proposal, human or automatic decision provenance, actual
edits, deferred items, freeze snapshot, and local/Git publication state. Update
the decision-log index.

Never label simulated or automatically integrated feedback as external journal
review or human approval.

## Sync

Call `96-sync-current.md` using the same closure mode. It updates
`articles/current.docx` directly from the active version and regenerates
`bibliography/bibliography.docx`. It never creates a Markdown pointer copy.
Interactive closure may report unavailable DOCX tooling; auto-closure requires
the configured strict checks.

Close the task only after the required local sync succeeds. On failure, keep it
partial/in-progress and report the failed artifact.

## Optional Git checkpoint

- If `GIT_AUTHORIZED=true`, call `07-git-checkpoint.md` with the appropriate
  authorized mode and require remote verification.
- If false, complete the local closure and report `Git: non pubblicato`. Ask
  separately whether the user wants a scoped commit and push.

Local closure and Git publication are distinct outcomes. Never call a local
closure incomplete solely because Git was not authorized.
