# OPENCODE.md — article-revision

This file activates the **article-revision** workflow for opencode and other agents that read `OPENCODE.md`. It mirrors `AGENTS.md`, the Claude Code skill defined in `SKILL.md`, and the workflow files in `workflow/`.

The two files (`AGENTS.md` and `OPENCODE.md`) carry the same workflow. Edit one and propagate to the other to avoid drift.

## Slash Commands

| Command | Description |
|---|---|
| `/article-revision` | Full revision workflow from reviewer feedback |
| `/r-pp` | Revisione Paragrafo per Paragrafo — 3 diagnostic questions per paragraph |
| `/r-pp-a` | Revisione Paragrafo per Paragrafo Approfondita — 5-layer deep diagnostic |
| `/r-pr-2` | Dual Peer Reviewer — generate standalone reports + synthesis in `revisions/` (no interactive A/R/M) |
| `/r-conn` | Connector revision: transitions, signposting, overused connectors |
| `/r-global` | Global revision: 7-lens structural review (non-granular) |
| `/r-freeze` | Freeze a concluded part in the per-article freeze ledger (advisory) |
| `/r-thaw` | Reopen a frozen part so it can be revised without the warning |
| `/r-status` | Print the frozen (🟢) vs open (🟡) snapshot from the freeze ledger |
| `/r-bump` | Bump article version (vN → vN+1) |
| `/r-sheet` | Generate final revision sheet |
| `/r-help` | Reference card of every command + A/R/M shortcuts (read-only, no bump) |

Revision commands enforce the mandatory session-start bump (`10-setup.md` step 5).
The read-only commands `/r-help` and `/r-status`, and the ledger-only commands
`/r-freeze` / `/r-thaw`, do **not** trigger a bump.
The freeze ledger (`workflow/15-freeze-ledger.md`) is checked before every
proposal: a frozen part triggers a warning + explicit confirmation before editing.

Commands are registered in the project's `opencode.json` under `"command"`.

For the complete workflow, see `AGENTS.md` in this repository. The same rules apply in opencode, including:

- user-controlled git operations;
- per-point `Accept / Reject / Modify` decisions;
- English workflow prompts and templates;
- multilingual article proposals via `ARTICLE_LANG`;
- explicit Python interpreter selection via `PYTHON_BIN`;
- Word document formatting rules for `.docx` sources and exports.
