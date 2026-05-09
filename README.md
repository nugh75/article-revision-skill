# article-revision

A Claude Code skill that coordinates **iterative peer-revision rounds on scientific articles** written in Markdown.

It orchestrates the recurring tasks of academic revision — collecting reviewer feedback, proposing surgical edits, verifying citations, computing sample statistics, tracking the editorial budget, bumping versions — into a structured, file-based, idempotent workflow.

The user keeps full control over git: the skill never commits, never pushes.

---

## What it does

For each reviewer point (or arbitrary revision request) the skill:

1. Loads the relevant section of the article, the bibliography, and the journal's editorial norms.
2. Generates a **proposal** that respects the norms and the article's style.
3. Shows in chat a fixed block: *Original + Proposal + Δ chars/words + Norms respected + Decision*.
4. Waits for `Accept / Reject / Modify`.
5. On accept: applies the diff, updates the *project file* (the persistent revision plan), bumps a counter.
6. After N accepted changes, **proposes** (never forces) a versioned snapshot of the article: `<prefix>-v(N+1)-YYYY-MM-DD-HHMM[-anonymous].md`.

It also handles:

- **Bibliography verification** against Crossref + OpenAlex (catching fictitious or wrong references).
- **Sample-description statistics** generated from `.xlsx`/`.csv` data sources.
- **Granularity**: revisions can target a single sentence, a paragraph, or the whole article.
- **Auto language detection** (it/en) — adapts the proposal style accordingly. Workflow docs stay in English; article proposals are written in the article language.

---

## Installation

This is a Claude Code skill: it lives at `.claude/skills/article-revision/` inside a project.

```bash
# from your project root
mkdir -p .claude/skills
cd .claude/skills
git clone https://github.com/nugh75/article-revision.git
```

Then create the project Python virtual environment for the scripts, or let the skill ask to create it on first run:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r .claude/skills/article-revision/requirements.txt
```

If `.venv/` is missing, the bootstrap asks whether to create it. If you refuse,
the skill asks before using system Python and stores the selected interpreter in
session memory as `PYTHON_BIN`. It never falls back to `python3` silently.

---

## Project layout the skill expects

```
<project-root>/
├── .env                              # editorial limits, paths, Zotero, etc.
├── .claude/skills/article-revision/  # this skill
├── articles/                         # or another path; auto-detected
│   └── article-vN-YYYY-MM-DD[-anonymous].md
├── bibliography/
│   └── reference.bib
├── editorial-norms/
│   └── norms-<journal>.md
├── data/                             # optional: sample-description sources
└── revisions/
    └── <reviewer-slug>/
        ├── revision-plan-vN.md
        └── final-sheet-vN.md
```

If anything is missing the skill's bootstrap step (`workflow/00-bootstrap.md`) walks the user through creating it. Nothing is created silently.

---

## `.env` keys

See `.env.example` for the full list. Required:

- `EDITORIAL_LIMIT_CHARS` (or `EDITORIAL_LIMIT_WORDS`)
- `EDITORIAL_NORMS_PATH`
- `BIBLIOGRAPHY_BIB_PATH`

Recommended:

- `CROSSREF_USER_AGENT`, `OPENALEX_USER_AGENT` — for the bibliography online verification scripts.
- `ZOTERO_USER_ID`, `ZOTERO_API_KEY`, `ZOTERO_GROUP_ID` — for Zotero sync.
- `ARTICLE_LANG` — force language detection (default: auto).
- `PYTHON_BIN` — Python interpreter for skill scripts (default: `.venv/bin/python`).
- `AUTO_BUMP_THRESHOLD` — how many accepted changes before the skill proposes a version bump (default: 5).

---

## Usage

In Claude Code, invoke the skill explicitly or let it auto-trigger:

```
/article-revision
```

Or implicitly:

> *"Apply Elisa's comments to the article."*
> *"Revise paragraph 3."*
> *"Create version 10 of the file."*

The first call walks through bootstrap; subsequent calls jump straight to the relevant workflow step.

---

## Multi-tool support

The skill works natively with **Claude Code** through `SKILL.md` (auto-discovered in `.claude/skills/`).

For other agents, two equivalent entry-point files describe the same workflow:

- `AGENTS.md` — cross-tool standard, read by Claude Code, opencode, OpenAI Codex CLI, Aider, Cline, and most agentic tools.
- `OPENCODE.md` — opencode-specific (legacy convention), kept in sync with `AGENTS.md`.

To activate the skill in a project that uses opencode or codex, symlink (or copy) the relevant file to the project root:

```bash
# from the consuming project root
ln -s .claude/skills/article-revision/AGENTS.md   AGENTS.md
ln -s .claude/skills/article-revision/OPENCODE.md OPENCODE.md
```

If the project already has an `AGENTS.md` / `OPENCODE.md`, merge by appending a single line that delegates to the skill:

```markdown
## article-revision
See .claude/skills/article-revision/AGENTS.md for the full workflow.
```

Both files reference the same `workflow/` and `scripts/`; the experience is identical across agents.

---

## Companion skills

`article-revision` is the **orchestration layer**. Two existing companion skills cover deeper concerns:

- a *journal-style skill* enforcing editorial norms (e.g. `praxis-article-style` for QTimes);
- a *bibliography skill* managing the `.bib` (e.g. `praxis-bibliography-citations`).

Both are optional. Without them, the skill falls back on the journal-norms file and the static `bib_check.py` / `bib_verify_online.py` scripts.

---

## Workflow files

The skill is driven by the markdown files in `workflow/`, executed in order:

| File | Purpose |
|---|---|
| `00-bootstrap.md` | Create venv, `.bib`, `.env`, norms file if missing |
| `10-setup.md` | Load configuration and active article |
| `20-plan-revision.md` | Parse reviewer feedback into a project file |
| `30-iterate-points.md` | The core loop: propose, ask, apply, log |
| `40-bibliography-check.md` | Static + online citation verification |
| `50-sample-description.md` | Compute sociodemographic statistics from raw data |
| `60-bump-version.md` | Snapshot to `vN+1` with timestamp |
| `70-final-sheet.md` | Produce the round's status sheet |

---

## Scripts

| File | What it does |
|---|---|
| `scripts/char_count.py` | Char/word count with section-exclusion and budget check |
| `scripts/bib_check.py` | Static cross-check between citations and `.bib` |
| `scripts/bib_verify_online.py` | Crossref + OpenAlex similarity scoring (cache included) |
| `scripts/sample_stats.py` | Per-cohort stats from `.xlsx`/`.csv` via YAML mapping |
| `scripts/new_version.sh` | Bump filename to `<prefix>-v(N+1)-YYYY-MM-DD-HHMM` |
| `scripts/diff_versions.sh` | Word-level diff between two versions |

---

## Word documents

The skill is Markdown-first, but projects may contain `.docx` sources or need a
Word export at the end of a revision round. In that case, preserve the article
content and enforce these layout rules:

- Use real Word heading styles for titles and section headings.
- Keep all body text black.
- Keep headings black unless journal norms specify otherwise.
- Do not add blank paragraphs between body paragraphs.
- Use style spacing before/after headings to create margins between headings and body text.
- Avoid manual blank lines during `.docx` ↔ Markdown conversion.
- Treat formatting changes as revision points that still require `Accept / Reject / Modify`.

---

## Templates

| File | Used for |
|---|---|
| `templates/revision-plan.md` | Per-reviewer planning document |
| `templates/final-sheet.md` | End-of-round status sheet |
| `templates/bibliography-audit.md` | Bibliography online-verification report |
| `templates/sample-stats.md` | Sample-description output |
| `templates/accepted-anglicisms-it.md` | Whitelist of accepted English terms in Italian prose |

---

## Design principles

- **User controls git.** The skill never commits, never stages, never pushes. It writes files; you commit.
- **Always ask before creating.** Bootstrap, version bump, file generation — every write step asks for confirmation when ambiguous.
- **Per-point granularity.** No mass replacements, no batched approvals. Every individual change goes through *Accept / Reject / Modify*.
- **State lives in markdown.** The project file and final sheet are the source of truth; sessions resume cleanly after interruption.
- **Surgical edits only.** Touch what the reviewer's point requires, nothing more.

---

## License

MIT. See [LICENSE](LICENSE).

---

## Contributing

Open issues and PRs are welcome. The skill is intentionally simple — most extensions belong in companion skills (journal-specific style, advanced bibliography flows). Try not to inflate `article-revision` itself.
