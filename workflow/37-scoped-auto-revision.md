# 37 — Scoped Automatic Revision

Run only for `/r-auto <task[,task...]> --scope "<scope>" [--agents N] [--git]`.
Task and scope are mandatory; auto-mode is never inferred.

Supported tasks are `chiarezza`, `stile`, `connettori`, `terminologia`,
`citazioni`, and `argomentazione`. Use at most three proposal workers.

Read the selected profiles in `references/auto-tasks.md`. Copy their acceptance
criteria and stop conditions into the manifest so combined tasks cannot silently
broaden one another.

## Authorization

A complete command authorizes a working version when the first eligible change
is ready, its task and audit records, scoped edits, and local derived exports.

Only `--git` authorizes threshold and final commits and push. Record
`GIT_AUTHORIZED=true|false`. For this mode set `ARTICLE_REVISION_LOCAL_ONLY=1`
on the version hook and use `auto-closure` for export. Cloud transfer is a
separate operation. Keep redline, colleague approval and unrelated paths
outside this mode.

## Read-only setup

Resolve the scope to exact paragraph or heading bounds in the active article.
Record its SHA-256 and the current ledger, selected tasks, ordered locators
and out-of-scope invariants. Keep the manifest in memory through eligibility
checks. Exclude frozen units from automatic application. List every 🔒
passage in scope as an invariant and keep its text intact.

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

Revalidate the article fingerprint, ledger and exact originals. Assemble the
eligible changes into one candidate in source order and verify it with the
pre-write checks in `workflow/14-verify-edit.md`. Preserve citations, numbers,
placeholders, headings, examples, epistemic strength and paragraph order.

If no change is eligible, report the findings and stop in read-only mode.
Once a verified change is ready, pass `ARTICLE_REVISION_LOCAL_ONLY=1` and the
recorded SHA-256 as `ARTICLE_REVISION_EXPECTED_SOURCE_SHA256` to
`workflow/60-bump-version.md`. Create the task and write
`auto-scope-<version>.md` with the source and working-version locators.
Revalidate the exact source spans on the working version and apply the
candidate through `workflow/14-verify-edit.md`. If the source drifted, stop
and report it. If the version was already created, keep it for recovery.

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
mode=auto-closure` with `GIT_AUTHORIZED` unchanged. Require local export generation and DOCX text checks.

- With `--git`, closure also requires an authorized final checkpoint and remote
  verification.
- Without `--git`, closure succeeds locally and reports the changed files as
  unpublished. Do not describe missing Git publication as a failure.
