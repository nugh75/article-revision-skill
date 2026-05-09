# OPENCODE.md — article-revision

This file activates the **article-revision** workflow for opencode and other agents that read `OPENCODE.md`. It mirrors `AGENTS.md`, the Claude Code skill defined in `SKILL.md`, and the workflow files in `workflow/`.

The two files (`AGENTS.md` and `OPENCODE.md`) carry the same workflow. Edit one and propagate to the other to avoid drift.

For the complete workflow, see `AGENTS.md` in this repository. The same rules apply in opencode, including:

- user-controlled git operations;
- per-point `Accept / Reject / Modify` decisions;
- English workflow prompts and templates;
- multilingual article proposals via `ARTICLE_LANG`;
- explicit Python interpreter selection via `PYTHON_BIN`;
- Word document formatting rules for `.docx` sources and exports.
