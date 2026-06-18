# OPENCODE.md — article-revision

This file activates the **article-revision** workflow for opencode and other agents that read `OPENCODE.md`. It mirrors `AGENTS.md`, the Claude Code skill defined in `SKILL.md`, and the workflow files in `workflow/`.

The two files (`AGENTS.md` and `OPENCODE.md`) carry the same workflow. Edit one and propagate to the other to avoid drift.

## Slash Commands

| Command | Description |
|---|---|
| `/article-revision` | Full revision workflow from reviewer feedback |
| `/r-pp` | Revisione Paragrafo per Paragrafo — optional global trace + unitary concept + 4 diagnostic questions per paragraph; recap at chapter/section boundaries |
| `/r-pp-a` | Revisione Paragrafo per Paragrafo Approfondita — optional global trace + 6-layer deep diagnostic, including unitary-concept control |
| `/r-pr-2` | Dual Peer Reviewer — generate standalone reports + synthesis in `revisions/` (no interactive decision loop) |
| `/r-conn` | Connector revision: transitions, signposting, overused connectors |
| `/r-global` | Global revision: 7-lens structural review; can save a trace for `/r-pp` |
| `/r-freeze` | Freeze a concluded part in the per-article freeze ledger (advisory) |
| `/r-thaw` | Reopen a frozen part so it can be revised without the warning |
| `/r-status` | Print the frozen (🟢) vs open (🟡) snapshot from the freeze ledger |
| `/r-handoff` | Write a resumable checkpoint without closing the revision round |
| `/r-resume` | Resume from a paused task file without a new version bump |
| `/r-bump` | Bump article version (vN → vN+1) |
| `/r-sheet` | Generate final revision sheet |
| `/r-help` | Reference card of every command + decision shortcuts (read-only, no bump) |

Revision commands enforce the mandatory session-start bump (`10-setup.md` step 5).
The read-only commands `/r-help` and `/r-status`, the ledger-only commands
`/r-freeze` / `/r-thaw`, and `/r-resume` from a paused task do **not** trigger a bump.
`pause`, `stop`, `sospendi`, and `/r-handoff` write a checkpoint; they do not
run the closure sequence or sync current files.
The freeze ledger (`workflow/15-freeze-ledger.md`) is checked before every
proposal: a frozen part triggers a warning + explicit confirmation before editing.

Commands are registered in the project's `opencode.json` under `"command"`.

For the complete workflow, see `AGENTS.md` in this repository. The same rules apply in opencode, including:

- user-controlled git operations;
- per-point `Accetta / Modifica / Rivedi completamente / Tieni in considerazione` decisions;
- resumable handoff checkpoints via `workflow/06-handoff.md`;
- English workflow prompts and templates;
- multilingual article proposals via `ARTICLE_LANG`;
- explicit Python interpreter selection via `PYTHON_BIN`;
- Word document formatting rules for `.docx` sources and exports.
