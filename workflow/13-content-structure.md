# 13 — Content Structure

Triggered by `/r-structure [scope]`. Map the ideas and argumentative functions
of existing manuscript content, then propose a preservation-first architecture.
The command is read-only until the user explicitly accepts a structural change.

## Read-only diagnosis

1. Load the active manuscript, relevant project notes, and freeze ledger through
   `10-setup.md` without creating revision state.
2. State the scope, communicative purpose, intended reader, and governing claim.
   Mark uncertainty instead of supplying a missing purpose or claim.
3. Inventory every heading, paragraph, list, figure callout, and other content
   block in scope. Give each unit a stable working identifier plus its current
   locator, incipit, or content hash.
4. Use `wayfinder` to assign each unit a primary function: governing claim,
   supporting claim, definition, evidence, example, bridge, implication, or
   limitation.
5. Map dependencies and logical relations: prerequisite, elaboration, evidence,
   example, contrast, chronology, cause, consequence, concession, or synthesis.
6. Diagnose orphaned ideas, unsupported claims, duplicate functions, missing
   bridges, premature concepts, overloaded units, and sequencing mismatches.
7. Choose an organizational pattern that serves the mapped relations. Do not
   force a conventional template when it does not match the content's purpose.

## Required proposal

Show both maps in chat:

```text
## Current architecture
| Current order | Unit ID | Locator | Function | Main idea/claim | Support | Dependency | Issue |

## Proposed architecture
| New order | Unit ID | Intended function | Relation to previous | Action | Reason |
```

`Action` is one of `keep`, `move`, `split-proposal`, `merge-proposal`,
`cut-proposal`, or `new-content-proposal`. A proposal does not authorize any
action.

Then report:

- the governing hierarchy and transition logic;
- missing claims, support, definitions, or bridges;
- each merge, cut, split, or addition as a separate decision;
- a preservation manifest accounting for every source unit exactly once.

Do not write a sidecar, bump a version, create a task, change the ledger, or
edit the manuscript during this phase.

## Applying an accepted structure

Structural application always uses `tracked-round`; never `direct-apply` or
`auto`. Before the first move:

1. Revalidate the inventory and the exact decisions the user accepted.
2. Check the freeze ledger and obtain confirmation for any frozen unit.
3. Create the new working version and task through the first-edit lifecycle in
   `SKILL.md`.
4. Record a move manifest containing each source unit's old locator, new
   locator, action, and approval. Preserve unit text during a pure move.
5. Apply only approved moves and separately approved splits, merges, cuts, or
   additions. Never infer one operation from acceptance of another.
6. Verify that every original unit is present exactly once unless an explicit
   approved manifest entry explains the difference.
7. Recompute locators, re-anchor affected ledger entries, run
   `git diff --check`, and present the structural diff before closure.

Git publication remains a separate authorization under
`07-git-checkpoint.md`.
