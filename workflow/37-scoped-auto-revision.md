# 37 — Scoped Automatic Revision

Run only when the user explicitly requests `/r-auto` or clearly authorizes an
automatic revision with both a task and a bounded scope. The workflow may
revise argumentation, but it must preserve the article's claims, evidence,
citations, examples, epistemic strength, and section order.

## 1. Parse and authorize

Accept:

```text
/r-auto <task[,task...]> --scope "<scope>" [--agents N]
```

Supported tasks: `chiarezza`, `stile`, `connettori`, `terminologia`,
`citazioni`, `argomentazione`. Reject or ask once if task or scope is missing
or ambiguous. `--agents` counts proposal workers, not the coordinator or later
auditor. Default to the available worker slots, maximum 3. If no subagent can
be started, stop; do not silently convert this into single-agent automatic work.

A fully specified invocation authorizes:

- the mandatory session-start bump;
- the task file, worker reports, audit report, final sheet, decision log, and
  current exports;
- automatic application of eligible edits inside scope;
- technical closure after a passing audit;
- threshold-based scoped Git checkpoints and their automatic pushes.

It does not authorize Drive writes, redlines, colleague approval, bibliography
enrichment outside the selected task, force-pushes, or unrelated Git paths.

## 2. Setup and immutable scope manifest

Run `00-bootstrap.md` if required and `10-setup.md`. For `/r-auto`, do not ask
again for the mandatory bump: the complete command is confirmation. Create the
task file with `COMMAND=/r-auto` and `REVIEWER_LANE=self`.

Resolve the scope against the newly bumped article. Supported forms:

- one paragraph or exact paragraph range (`P12`, `P12-P40`);
- heading-bounded section, chapter, or Part;
- `intero articolo` / `whole article`.

First build a provisional candidate manifest and check every candidate against
the freeze ledger. Ask about all frozen candidates before finalization. Then
create the immutable manifest, marking each candidate `included` or
`excluded-frozen`; later confirmation requires a new manifest and audit baseline,
not mutation of the existing manifest.

Before edits, create
`revisions/<article-slug>/auto-scope-<bumped-version>.md` containing:

- selected tasks and worker count;
- article path/version and SHA-256 of the pre-edit article;
- exact start/end headings and line bounds;
- ordered paragraph manifest with paragraph ID, chapter, nearest heading,
  line range, and incipit;
- frozen/open ledger state;
- explicit invariants for material outside scope.

Recount the manifest with a second method. If counts differ, stop before
delegating. Frozen units require explicit user confirmation and are excluded
until confirmed; auto-mode never overrides the freeze ledger.

## 3. Partition and delegate proposals

Partition the manifest into contiguous, non-overlapping ranges. Balance by
characters while preserving paragraph boundaries. Give each worker:

- the article as a read-only source;
- its exact manifest range plus the preceding and following paragraph as
  read-only context;
- selected tasks, editorial norms, language, and relevant global trace;
- the invariants and stop conditions below;
- a unique report path:
  `revisions/<article-slug>/auto-worker-<bumped-version>-<range>.md`.

Workers must not edit any shared file. Each returns report content with one row
per manifest paragraph: `unchanged`, `proposed`, or `deferred`; exact original;
full replacement; task/category; rationale; risk; citations/numbers touched;
and cross-boundary dependencies. The coordinator writes the returned content to
the unique report path with `apply_patch`. Reports are proposals, never edits.

Run workers concurrently when independent slots are available. A worker must
defer rather than decide if two substantively valid interpretations remain.

## 4. Stop conditions

Stop and ask the user before applying the affected item when any proposal:

- is `risk: high`;
- adds, removes, strengthens, narrows, or reverses a claim;
- adds evidence or a citation not already supplied and verified;
- changes a number without passing `51-data-verification.md`;
- deletes a theoretically relevant example or more than incidental wording;
- splits, merges, moves, renumbers, or reorders paragraphs/sections;
- touches a frozen unit without explicit confirmation;
- crosses the manifest boundary;
- chooses between two defensible interpretations;
- conflicts with another worker or the editorial norms.

Record stopped items in the task file and ask the user. For a non-frozen unit,
also record the unresolved intention in the freeze ledger as open. For a frozen
unit, leave it frozen and put the note in the task file; do not thaw it merely
to record a proposal. Do not apply stopped items implicitly. An unanswered stop
condition blocks audit and closure. If it prevents safe integration of dependent
edits, pause via `06-handoff.md`.

## 5. Coordinator integration

The coordinator reads every worker report and is the only actor allowed to
edit the article. Revalidate each proposal against the current source, then
apply eligible replacements in manifest/source order. Do not apply a patch if
its original no longer matches exactly; rebase it from the current paragraph or
defer it.

Eligible argumentative edits may make premises, inference links, paragraph
function, limitations, or transitions more explicit. They must not change the
argument's commitments. Preserve citations, placeholders, years, URLs, numeric
tokens, headings, blank-line/paragraph structure, and theoretically relevant
examples unless the selected task explicitly and safely requires a local change.

Maintain counts for checked, changed, unchanged, deferred, and stopped units.
Increment `changes-since-git-checkpoint` once per integrated changed manifest
unit. Integrate in threshold-sized batches; before each mid-run checkpoint, run
the bounded batch audit required by `07-git-checkpoint.md`, then commit and push
automatically. Do not trigger mid-session bump proposals while `/r-auto` is
running; the session-start version remains the integration target.

## 6. Independent audit

After integration, start a fresh audit subagent that did not author worker
proposals. Give it the pre-edit snapshot, integrated article, immutable scope
manifest, selected tasks, norms, and worker reports. Do not give it the
coordinator's conclusions.

Require checks for:

- every manifest unit accounted for exactly once;
- byte/semantic identity outside scope;
- unchanged headings, order, and paragraph/blank-line map unless explicitly
  authorized;
- preservation of claims, causal strength, agents/subjects, theoretical
  referents, comparisons, limitations, examples, and epistemic caution;
- citations/placeholders, years, URLs, and numbers preserved or verified;
- no invented evidence or bibliography keys;
- editorial limit, bibliography static check when relevant, and
  `git diff --check`.

The coordinator writes the auditor's result to
`revisions/<article-slug>/auto-audit-<bumped-version>.md` with `PASS` or `FAIL`,
evidence, and exact paragraph locators. On `FAIL`, repair only unambiguous
low/medium-risk defects and rerun a fresh audit. Otherwise stop; never close
automatically on a failing audit.

## 7. Automatic technical closure

When the audit passes, all manifest units are accounted for, and no stop
condition awaits a user decision,
the user's initial `/r-auto` authorization is sufficient. Do not ask again.

1. Print the run summary: scope, tasks, workers, checked/changed/unchanged/
   deferred/stopped counts, character delta, audit result, active version.
2. Always run `70-final-sheet.md`.
3. Run `95-decision-log.md` in `auto-closure` mode. It writes the log, calls
   strict `96-sync-current.md`, and closes the task file only after sync passes.
4. Verify `articles/current.md` matches the active version byte-for-byte and
   inspect extracted text from both generated DOCX files. File size alone is
   not sufficient.
5. Require `95-decision-log.md` auto-closure to return the final checkpoint
   hash, upstream, and successful remote verification. Its flush includes final
   sheet, decision log, task file, current exports, manifest, reports, audit,
   article, and other active-session files.
6. Report technical closure successful only if decision log, task close,
   Markdown sync, required DOCX exports, content checks, commit, push, and
   remote verification pass.

If audit, closure, or export verification fails before the flush, mark the
relevant task step `failed` or leave the session `partial`, report the exact
artifact, and do not create the closure checkpoint. If commit or push fails,
preserve any local commit and stop under `07-git-checkpoint.md` recovery rules.
