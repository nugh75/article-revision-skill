# article-revision

An auditable Markdown workflow for revising scientific articles and theses.
The runtime contract is `SKILL.md`; operational details live in `workflow/`.

## Core behavior

- Diagnosis and proposals are read-only. They do not create a version, task,
  ledger entry, export, commit, or push.
- Idea organization and content-architecture maps are read-only by default.
  Applying a structural reorganization always uses a tracked round and accounts
  for every source unit.
- A bounded edit to an explicitly named file/version can run in direct-apply
  mode: edit and verify that target only, with no bump, task, ledger, or sync.
- A tracked reviewer or iterative round creates the working version, task file,
  and freeze ledger before its first edit.
- `Accetta` authorizes the stated text edit only.
- Interactive Git checkpoints always require a dedicated confirmation.
- Plain `/r-auto` performs bounded local edits and verification. Only
  `/r-auto ... --git`, `/r-handoff --git`, or an explicit `commit e push`
  authorizes publication.
- Pause and ordinary `/r-handoff` remain local and resumable.

## Main commands

| Command | Purpose |
|---|---|
| `/r-audit [scope]` | Read-only conceptual, prose, citation, or data audit |
| `/r-structure [scope]` | Read-only content map and preservation-first structural proposal |
| `/r-global` | Seven-lens whole-manuscript diagnosis |
| `/r-pp`, `/r-pp-a` | Paragraph-by-paragraph diagnosis and approved edits |
| `/r-conn` | Connector and transition review |
| `/r-chapter` | Chapter or section revision in whole-text context |
| `/r-pr-2` | Standalone simulated peer-review reports |
| `/r-auto <task> --scope "<scope>" [--agents N] [--git]` | Bounded automatic revision |
| `/r-handoff [--git]`, `/r-resume` | Pause or resume a tracked round |
| `/r-guide`, `/r-help` | Read-only guidance and command reference |

The full list is in `workflow/99-help.md`.

## Expected project inputs

```text
<project-root>/
├── .env
├── articles/
├── bibliography/reference.bib
├── editorial-norms/
└── revisions/
```

Bootstrap (`workflow/00-bootstrap.md`) runs only when an operation needs missing
infrastructure. It asks before creating files, directories, or a virtual
environment. Read-only audits use the material already available.

See `.env.example` for configuration. Use the project virtual environment for
Python scripts; the workflow never silently falls back to system Python.

## Companion skills

- `wayfinder` audits definitions, idea roles, construct boundaries, relations,
  and content architecture.
- `scrittura` organizes source material and drafts prose without implicit file
  changes.
- `tone-of-voice` performs the final academic-style and paragraph-readability
  pass without changing established terminology, structure, or evidence.

`article-revision` owns tracked application, versioning, closure, and optional
Git publication.

## Installation

Place the repository in `.claude/skills/article-revision/` for Claude Code or
in an agent skill directory supported by the host. Codex can follow symlinked
skill directories, so keep one visible copy per skill name in each discovery
scope to avoid duplicate menu entries.

## License

MIT. See `LICENSE`.
