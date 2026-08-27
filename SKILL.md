---
name: article-revision
description: Coordinate auditable revision and structural reorganization of a scientific article or thesis in Markdown. Use for reviewer feedback, content architecture, paragraph or chapter revision, approved file edits, versioning, freeze-ledger tracking, bounded `/r-auto`, handoff, or closure. Diagnosis and proposals are read-only; Git publication requires separate explicit authorization.
---

# Article Revision

Orchestrate revision records and approved manuscript edits. This skill owns
file application and versioning; it does not replace conceptual diagnosis or
prose drafting.

## Routing

| Request | Route |
|---|---|
| Definitions, construct boundaries, argumentative function | Run `wayfinder` read-only first |
| Organize raw ideas or create an outline in chat | Run `wayfinder`, then use `scrittura` |
| Drafting, rewriting, lexical or flow work in chat | Use `scrittura`, then `tone-of-voice` |
| Map or reorganize existing manuscript content | `/r-structure [scope]` via `workflow/13-content-structure.md` |
| Read-only manuscript diagnosis | `/r-audit` via `workflow/12-audit.md`, or the diagnostic phase of `/r-global`, `/r-pp`, `/r-pp-a`, `/r-conn`, and `/r-chapter` |
| Apply bounded, non-structural approved text to an explicitly named file/version, without tracking | Direct apply via `workflow/11-direct-apply.md` |
| Reviewer round, versioned revision session, ledger/task workflow | Tracked edit lifecycle below |
| Bounded automatic edits | `/r-auto <task> --scope "<scope>" [--agents N] [--git]` |
| Pause or resume local work | `/r-handoff`, `/r-resume` |
| Publish a checkpoint | explicit `commit e push`, `/r-handoff --git`, or `/r-auto ... --git` |

Other commands remain available through their workflow files: `/r-pr-2`,
`/r-freeze`, `/r-thaw`, `/r-status`, `/r-bump`, `/r-sheet`, `/r-gdrive`,
`/r-approve`, `/r-redline`, `/r-guide`, and `/r-help`.

## Authority

Apply constraints in this order:

1. The user's current explicit instruction and approved wording.
2. Factual accuracy, evidence, citations, data verification, and preservation of
   epistemic strength.
3. The freeze ledger and the explicitly bounded revision scope.
4. Project style notes and applicable editorial norms.
5. `tone-of-voice` preferences.

Surface conflicts before applying text. Editorial norms do not silently
override a deliberate user choice; record an intentional exception.

## Lifecycle and authorization

Select one execution mode before any write:

| Mode | Use when | Persistent effects |
|---|---|---|
| `chat-only` | Diagnose, compare, draft, audit, organize ideas, or propose a content architecture | None unless the user separately asks to save an artifact |
| `direct-apply` | The user explicitly names the target file/version and asks to apply bounded approved wording without opening a revision round | Edit and verify that target only |
| `tracked-round` | Reviewer feedback, iterative revision, accepted structural reorganization, requested versioning, task/ledger state, or explicit tracking | Working version, task, ledger, closure artifacts |
| `auto` | Complete bounded `/r-auto` command | Tracked automatic lifecycle defined below |

If the request names a file but does not make tracking intent clear, prefer
`direct-apply` for one bounded replacement and `tracked-round` for an iterative
or reviewer-driven session. State the selected mode before writing. User intent
overrides the default.

Structural moves, paragraph or section reordering, and accepted merges or cuts
always use `tracked-round`, even when the target file is named. They affect
multiple content units and their locators, so they never use `direct-apply` or
`auto`. Follow `workflow/13-content-structure.md`.

### 1. Diagnose and propose

Reading, analysis, comparison, and proposals are read-only by default.

- Load the active manuscript, relevant norms, bibliography, and existing freeze
  ledger without creating or updating files.
- Do not bump, create a task file, update the ledger, sync exports, stage, commit,
  or push during diagnosis.
- A proposal shown in chat is not an applied edit and is not written to a
  sidecar unless the user explicitly asks to save it.
- Read adjacent manuscript context as needed, but keep proposed changes inside
  the named scope.

### 2. Apply directly to a named target

Use `workflow/11-direct-apply.md` when the user explicitly identifies a file or
version and requests a bounded replacement without asking for a revision round.

- Revalidate the exact target and approved wording.
- Edit that file in place and verify the result.
- Do not bump, create a task, update the ledger, sync `current.*`, or create
  closure artifacts.
- Git still requires separate authorization.

### 3. Apply the first accepted edit in a tracked round

`Accetta`, `applica`, or an equivalent explicit instruction authorizes the
approved manuscript edit, not Git publication.

Before the first file edit of a new tracked round:

1. Revalidate the exact source text and scope.
2. Check the freeze ledger. A frozen unit requires explicit confirmation.
3. Create the new article version through `workflow/60-bump-version.md` and
   announce the resulting path.
4. Create the task file through `workflow/05-task.md` and reconcile the ledger.
5. Apply only the accepted wording to the new version.

Further accepted changes in the same round use that version. A diagnostic-only
session ends without a version, task file, decision log, sync, or Git action.

### 4. Automatic mode

Auto-mode is never inferred. Follow
`workflow/37-scoped-auto-revision.md` only for a request that names both task
and bounded scope.

Read `references/auto-tasks.md` for the selected task profiles and their
acceptance criteria.

Supported tasks: `chiarezza`, `stile`, `connettori`, `terminologia`,
`citazioni`, and `argomentazione`.

- A complete `/r-auto` authorizes the first-edit bump, scoped low/medium-risk
  edits, reports, independent audit, decision log, and local current exports.
- It does not authorize new claims, unverified evidence, substantive cuts,
  paragraph or section moves, frozen material, or choices between defensible
  interpretations.
- It authorizes commit and push only when the command includes `--git` or the
  user separately says `commit e push`.

## Proposal format

Use the smallest format that still supports an informed decision:

```text
## Point N — <title>
Unità: <chapter; paragraph; file:lines>

Originale
> <exact text>

Proposta
> <complete proposed text>

Modifiche
1. <change and reason>

Rischio: <low|medium|high>
Decisione? Accetta / Modifica / Rivedi / Tieni in considerazione
```

- Show full replacement wording for medium/high-risk changes.
- Keep conceptually independent changes separately decidable.
- Include character/word deltas, norms, or exceptions only when material.
- Wait after a proposal. Apply nothing before acceptance.
- After applying, remain on the same unit until the user asks to advance.

## Preservation and verification

- Preserve claims, evidence, citations, causal strength, examples, headings,
  and section order unless the user explicitly approves changing them.
- In structural work, preserve every inventoried source unit by default. A move
  may change order but not content; a merge, cut, split, or new claim requires a
  separate explicit decision and must remain traceable in the move manifest.
- A numeric claim is never inherited. Run `workflow/51-data-verification.md`
  before proposing a changed or newly relied-upon figure.
- When citations change, run `workflow/40-bibliography-check.md`.
- Recompute paragraph locators after edits. Use:
  `Capitolo <C> — <title>; Paragrafo P<N> — <article>:<L1-L2>`.
- Stage only an explicit active-session manifest. Never include `.env`, broad
  globs, or unrelated paths.

## Freeze ledger

The ledger is advisory and persistent.

- Read it before every proposal that may affect a tracked unit.
- Warn and obtain confirmation before editing a frozen unit.
- Record deferred intentions only after a tracked round exists; otherwise keep
  them in the read-only audit response until the user asks to save them.
- Offer to freeze a concluded unit; never freeze automatically.

See `workflow/15-freeze-ledger.md` for mechanics.

## Handoff, closure, and Git

- `pause`, `stop`, `sospendi`, or `interrompi` pause locally. If a task file
  exists, update its checkpoint; otherwise give a chat summary. They never imply
  commit or push.
- `/r-handoff` records a local resumable checkpoint. Add `--git` or explicitly
  request `commit e push` to publish it.
- Closing a tracked round writes the decision log and synchronizes current
  exports after confirmation. Then ask separately whether to create and push a
  scoped Git checkpoint.
- At the configured threshold, interactive work may prompt for a checkpoint;
  `non ora` preserves local work and continues.
- A normal text acceptance, natural-language stop, diagnostic command, or
  closure confirmation is not Git authorization.
- Never pull, merge, rebase, amend, reset, force-push, bypass hooks, open a PR,
  tag, or release automatically.

Follow `workflow/06-handoff.md`, `workflow/07-git-checkpoint.md`,
`workflow/95-decision-log.md`, and `workflow/96-sync-current.md` for the relevant
branch.

## Project contract

Expected project inputs are `.env`, an active Markdown manuscript,
`bibliography/reference.bib`, editorial norms, and `revisions/`. Ask before
creating missing infrastructure. Use the project virtual environment for Python
scripts; never silently fall back to system Python.

The operational details for each mode live in `workflow/`. Read only the
workflow files needed by the selected route.

## Maintenance verification

After changing this skill, regenerate compatibility files and run the contract
checks. When a second installed checkout exists, pass it as `--mirror`:

```bash
python scripts/generate_compat_docs.py
python scripts/check_contract.py [--mirror <installed-copy>]
bash tests/test_git_checkpoint.sh
```
