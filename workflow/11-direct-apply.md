# 11 — Direct Apply

Apply approved wording to the explicitly named active article version or
standalone draft without opening a tracked revision round.

## Entry conditions

Use this mode only when all are true:

- the user explicitly names a standalone draft or the active article version;
- the replacement is bounded and its wording or direction is approved;
- the replacement does not move, reorder, split, merge, or cut content units;
- the user did not request a reviewer round, new version, task, ledger, current
  export synchronization, or other tracked lifecycle artifact.

Otherwise use `tracked-round` through `10-setup.md`. Structural operations use
`13-content-structure.md` even when their target is explicitly named.

## Apply

1. Set `EXECUTION_MODE=direct-apply` and resolve the exact target.
2. Confirm the source text still matches the approved proposal. If it drifted,
   stop and show the difference.
3. Read any existing freeze ledger without updating it. If the target is frozen,
   warn and require confirmation before editing. If a 🔒 passage
   (`15-freeze-ledger.md` §13) falls inside the target, stop: a direct apply never
   alters locked text, not even with confirmation.
4. Run `workflow/14-verify-edit.md` to verify and apply the approved candidate.
5. Run `git diff --check` in the owning repository and report the target and
   the verification result.

## Boundary

Direct apply does not create a version, task, plan, sidecar, ledger entry,
decision log, final sheet, DOCX export, or `current.*` synchronization. It does
not stage, commit, or push. A later request for any of those actions is a new,
separately authorized operation.
