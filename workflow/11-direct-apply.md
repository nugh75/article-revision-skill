# 11 — Direct Apply

Apply approved wording to an explicitly named manuscript file or version without
opening a tracked revision round.

## Entry conditions

Use this mode only when all are true:

- the user explicitly names the target path or unambiguous version;
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
   warn and require confirmation before editing.
4. Apply only the approved wording to the named target.
5. Re-read the changed unit, search for leftover fragments or accidental
   duplicates, and run `git diff --check` for the owning repository.
6. Report the target path and verification result.

## Boundary

Direct apply does not create a version, task, plan, sidecar, ledger entry,
decision log, final sheet, DOCX export, or `current.*` synchronization. It does
not stage, commit, or push. A later request for any of those actions is a new,
separately authorized operation.
