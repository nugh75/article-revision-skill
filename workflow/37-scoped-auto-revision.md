# 37 — Scoped Automatic Revision

Run only for `/r-auto <task[,task...]> --scope "<scope>" [--agents N] [--git]`.
Task and scope are mandatory; auto-mode is never inferred.

Supported tasks are `chiarezza`, `stile`, `connettori`, `terminologia`,
`citazioni`, and `argomentazione`. Use at most three proposal workers.

Read the selected profiles in `references/auto-tasks.md`. Copy their acceptance
criteria and stop conditions into the manifest so combined tasks cannot silently
broaden one another.

## Authorization

A complete command authorizes the first-edit bump, task/report files, eligible
scoped edits, independent audit, decision log, and local derived exports.

Only `--git` authorizes threshold commits, the final commit, and push. Record
`GIT_AUTHORIZED=true|false` before any work. The command never authorizes Drive,
redline, colleague approval, force-push, or unrelated paths.

## Setup and manifest

Run read-only setup, then create the first-edit version and task file. Resolve
the scope to exact paragraph or heading bounds. Check the freeze ledger before
finalizing an immutable manifest. Frozen candidates remain excluded until the
user explicitly confirms them.

Write `auto-scope-<version>.md` with article hash, selected tasks, ordered unit
locators, line bounds, freeze state, and out-of-scope invariants. Recount the
manifest independently before delegation.

## Proposal workers

Partition the manifest into contiguous, non-overlapping ranges. Workers read the
article and context but edit no shared file. Each returns exact originals, full
replacements, rationale, risk, citations/numbers touched, and cross-boundary
dependencies. The coordinator alone writes reports and applies eligible edits.

A worker whose rationale asserts something about Italian must verify it with the
`treccani` skill on the isolated construction and carry the entry in the
rationale. Without that evidence the edit is not eligible for automatic
application: the coordinator holds it for review as a stylistic preference. This
pass applies edits nobody reads first, so an unverified linguistic claim never
reaches the manuscript.

## Stop conditions

Ask before applying a proposal that changes a claim or causal strength, adds
unverified evidence, alters a number without data verification, removes a
relevant example, changes structure/order, touches frozen or out-of-scope text,
or chooses between defensible interpretations. An unresolved stop condition
blocks automatic closure.

## Integration and checkpoints

Revalidate exact originals and integrate eligible units in source order.
Preserve citations, numbers, placeholders, headings, examples, epistemic
strength, and paragraph order.

Increment the checkpoint counter per changed unit:

- with `--git`, run the bounded audit and call `07-git-checkpoint.md
  mode=auto-authorized` at thresholds;
- without `--git`, keep all work local and continue without Git calls.

## Independent audit

Use a fresh auditor that did not author proposals. Compare the pre-edit snapshot,
integrated manuscript, manifest, norms, and reports. Require complete unit
accounting, identity outside scope, semantic preservation, citation/number
checks, and `git diff --check`. Write a PASS/FAIL audit report. Repair only
unambiguous low/medium-risk defects; otherwise stop.

## Local closure

After PASS, generate the final sheet and call `95-decision-log.md
mode=auto-closure` with `GIT_AUTHORIZED` unchanged. Require strict current-file
sync and DOCX text checks.

- With `--git`, closure also requires an authorized final checkpoint and remote
  verification.
- Without `--git`, closure succeeds locally and reports the changed files as
  unpublished. Do not describe missing Git publication as a failure.
