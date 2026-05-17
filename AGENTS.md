# AGENTS.md — article-revision

This file activates the **article-revision** workflow for any AI coding agent that reads `AGENTS.md` (Claude Code, opencode, OpenAI Codex CLI, Aider, Cline, and similar tools). It mirrors the Claude Code skill defined in `SKILL.md` and the workflow files in `workflow/`.

If your tool also reads `OPENCODE.md`, that file contains the same workflow.

---

## When this workflow activates

Trigger phrases:

- *"revise the article"*, *"apply reviewer X comments"*, *"revise paragraph 3"*
- *"let's process the reviewer comments"*, *"revise this paragraph"*
- explicit invocation if the host tool supports it (Claude Code: `/article-revision`)
- any request that mentions a Markdown article and reviewer/co-author feedback to apply

### Slash Commands

| Command | Action |
|---|---|
| `/article-revision` | Full revision workflow from reviewer feedback |
| `/r-pp` | **Revisione Paragrafo per Paragrafo** — sequential walk with diagnostic questions per paragraph |
| `/r-pp-a` | **Revisione Paragrafo per Paragrafo Approfondita** — deep five-layer diagnostic per paragraph |
| `/r-pr-2` | **Revisione Due Peer Reviewer** — generate two standalone reviewer reports + synthesis in `revisions/<article-slug>/` (no interactive A/R/M) |
| `/r-conn` | **Revisione Connettori** — analyse and polish logical connectors, transitions, and signposting |
| `/r-global` | **Revisione Globale** — high-level, non-granular revision across seven structural lenses |
| `/r-bump` | Bump article version (hand off to `workflow/60-bump-version.md`) |
| `/r-sheet` | Generate final revision sheet (hand off to `workflow/70-final-sheet.md`) |

See `SKILL.md` for the full description of each mode.

If the user is doing something else (writing the article from scratch, generating new content, refactoring code), do **not** activate this workflow.

---

## Hard rules

1. **The user controls all git operations.** This skill never runs `git add`, `git commit`, `git push`, or `git stage`. It only writes files. After each accepted change, briefly note that there are pending changes and stop. If the user explicitly asks the skill to commit, do so without `--no-verify` and without `git push`.
2. **Per-point granularity.** Every revision proposal goes through the user as one atomic decision: `Accept / Reject / Modify`. Never collapse multiple unrelated changes into one proposal.
3. **Always ask before creating.** Bootstrap, version bump, new files: every write step that creates something requires explicit confirmation. Idempotent re-checks of already-existing artifacts need no confirmation.
4. **No silent behavior.** Whenever the skill takes a non-trivial action, output a one-line acknowledgement in chat.
5. **Surgical edits.** Touch only what the current point requires. Do not clean up adjacent prose, formatting, or unrelated bibliography.
6. **Mandatory bump at session start.** Every new revision session MUST start with a version bump (vN → vN+1) before any edits. The bump is enforced by `10-setup.md` step 5. Never skip it. The `AUTO_BUMP_THRESHOLD` handles additional mid-session bumps separately.

---

## Expected Layout

```
<project-root>/
├── .env                              # editorial parameters and credentials
├── articles/                         # or another path; auto-detected
│   └── article-vN-YYYY-MM-DD[-anonymous].md
├── bibliography/
│   └── reference.bib
├── editorial-norms/
│   └── norms-<journal>.md
├── data/                             # optional, for sample stats from raw data
└── revisions/
    └── <reviewer-slug>/
        ├── revision-plan-vN.md
        └── final-sheet-vN.md
```

If anything is missing, run the bootstrap (`workflow/00-bootstrap.md`). It walks the user through creating each piece without writing anything silently.

---

## `.env` Keys

Required:

- `EDITORIAL_LIMIT_CHARS` (or `EDITORIAL_LIMIT_WORDS`)
- `EDITORIAL_NORMS_PATH`
- `BIBLIOGRAPHY_BIB_PATH`

Recommended:

- `CROSSREF_USER_AGENT`, `OPENALEX_USER_AGENT` (bibliography online verification)
- `ZOTERO_USER_ID`, `ZOTERO_API_KEY`, `ZOTERO_GROUP_ID` (Zotero sync)
- `ARTICLE_LANG` (force language detection)
- `PYTHON_BIN` (Python interpreter for skill scripts; default `.venv/bin/python`)
- `AUTO_BUMP_THRESHOLD` (default 5)

See `.env.example` for the complete template.

---

## Workflow Steps

| Step | File | When |
|---|---|---|
| 1 | `workflow/00-bootstrap.md` | First invocation in a new project, or whenever an artifact is missing |
| 2 | `workflow/10-setup.md` | After bootstrap; loads `.env`, norms, bibliography, active article, detects language |
| 3 | `workflow/20-plan-revision.md` | When user provides reviewer feedback |
| 4 | `workflow/30-iterate-points.md` | Core loop: propose, ask, apply (no commit) |
| 4a | `workflow/31-paragraph-by-paragraph.md` | Triggered by `/r-pp` or `/r-pp-a`. Per-paragraph diagnostic walk. |
| 4b | `workflow/32-peer-review-simulation.md` | Triggered by `/r-pr-2`. Generates three standalone documents in `revisions/<article-slug>/`. No interactive A/R/M. |
| 4c | `workflow/33-connector-revision.md` | Triggered by `/r-conn`. Connector and transition polish. |
| 4d | `workflow/34-global-revision.md` | Triggered by `/r-global`. Seven-lens structural review. |
| 5 | `workflow/40-bibliography-check.md` | When a citation is touched or a reviewer flags one |
| 6 | `workflow/50-sample-description.md` | When methodology asks for sample stats from raw data |
| 7 | `workflow/60-bump-version.md` | Mandatory session-start bump + end of round, or after `AUTO_BUMP_THRESHOLD` accepted changes |
| 8 | `workflow/70-final-sheet.md` | End of round |

Each workflow file contains the full step-by-step instructions. **Read the relevant workflow file before acting.**

---

## Revision Scope

The user can pick one of three scopes:

| Scope | Trigger phrases | Behavior |
|---|---|---|
| **Fragment** | *"fix this sentence"*, *"adjust this quotation"*, *"replace X with Y"* | Smallest possible diff |
| **Paragraph** (default for reviewer points) | *"revise this paragraph"*, *"section 3"* | One paragraph or numbered subsection |
| **Whole article** | *"revise the whole article"* | Sequential walk; every change still individually approved |
| **Paragraph-by-paragraph** (`/r-pp`) | `/r-pp` | Walk every paragraph; three diagnostic questions per paragraph before proposing |
| **Deep paragraph-by-paragraph** (`/r-pp-a`) | `/r-pp-a` | Five-layer diagnostic (logic, structure, tone, citations, norms) per paragraph; proposals numbered by category |
| **Dual peer review** (`/r-pr-2`) | `/r-pr-2` | Generate two standalone reviewer reports (method + theory) + synthesis in `revisions/`. No interactive A/R/M. |
| **Connector revision** (`/r-conn`) | `/r-conn` | Non-content pass: logical connectors, transitions, signposting. Diagnostic table + selective fix with A/R/M |
| **Global revision** (`/r-global`) | `/r-global` | High-level, non-granular: seven lenses (thesis, architecture, proportionality, narrative, redundancy, terminology, norms) |

Never collapse heterogeneous changes (citation + phrasing + structure) into one proposal. Split them into separate decisions.

---

## Interaction Pattern

For every revision proposal, output exactly this structure:

```text
## Point N — <short title> · scope: <fragment|paragraph|whole article>

**Original** (`<article>:<line-range>`)
> <verbatim text>

**Proposta**
> <proposed full text>

**Modifiche:**
1. `<old>` → `<new>` [(motivazione)]
2. `<old>` → `<new>` [(motivazione)]
...

**Δ**: chars <signed> / words <signed> · risk: <low|medium|high>

**Norms respected**: <list>
**Possible exceptions**: <list, with reason>

**A/R/M?** (indicare i numeri delle modifiche, es. "A 2,4" oppure "M 3: sostituire X con Y")
```

Then **wait** for the user. Never apply pre-emptively.

Each modification within a paragraph is numbered. The user can accept/reject individual changes:
- `A 1,3` → accept modifications 1 and 3 only.
- `R 2` → reject modification 2.
- `M 4: <direction>` → modify modification 4 as specified.
- `A` (no numbers) → accept all.
- `R` (no numbers) → reject entire point.

### After applying changes

Once modifications are applied, **do not advance** automatically. Output:

```
Applicate modifiche <numbers>. [Restano in sospeso le modifiche <numbers>.] Ci sono altri cambiamenti da fare in questo paragrafo?
```

And **wait** for an explicit command (e.g. "no, prossimo paragrafo", "next", "passa al prossimo").

On `Accept` (selected numbers): edit the file(s), update the project file, increment the *accepted-since-last-bump* counter. **Do not commit.** Ask for further changes on the same paragraph.

On `Reject` (selected numbers): annotate rejected + reason. No file edits. Ask for further changes.

On `Reject` (entire point): annotate rejected + reason. Advance to next point.

On `Modify <N>: <direction>`: regenerate modification N per user direction. Re-present it.

Silent advance only on explicit user command ("prossimo", "next", etc.).

---

## Language Handling

In `workflow/10-setup.md`:

1. Skip frontmatter and headings.
2. Read up to 1,000 chars of body text.
3. Score language by function words for the candidate languages.
4. Highest score wins. Ties require asking the user. `.env` `ARTICLE_LANG` always wins.

Workflow documentation, prompts, and templates stay in English. Article proposals are written in `ARTICLE_LANG`.

If `ARTICLE_LANG=it`, anglicisms in proposals must come from `templates/accepted-anglicisms-it.md`. Surface any new anglicism in the proposal block under "Possible exceptions".

---

## Versioning Convention

`<prefix>-vN-YYYY-MM-DD-HHMM[-anonymous].md`

Multiple bumps in the same day stay distinct because of the time. The bump script (`scripts/new_version.sh`) accepts both legacy `vN-YYYY-MM-DD` and new `vN-YYYY-MM-DD-HHMM` source filenames.

---

## Word Document Handling

When the project contains Word files (`.docx`) or the revised Markdown article must be rendered back to Word, preserve content first and enforce a clean editorial layout:

- Headings must remain explicit headings, not body paragraphs styled manually.
- Body text must be black.
- Headings must be black unless the journal norms explicitly require another color.
- Body paragraphs must not have blank-line spacing between consecutive paragraphs; use paragraph spacing values instead of inserting empty paragraphs.
- Keep visible spacing between headings and the following body text through heading style spacing before/after, not through manual blank lines.
- Do not introduce extra paragraph breaks while converting `.docx` to Markdown or Markdown back to `.docx`.
- If a Word formatting change is proposed, present it as a revision point and ask `Accept / Reject / Modify` before applying.

---

## Scripts

Run Python scripts with the project's Python venv. The bootstrap asks before creating `.venv/`; if the user refuses, ask before using system Python and remember the selected interpreter as `PYTHON_BIN`. Never fall back to `python3` silently.

| Script | Purpose |
|---|---|
| `scripts/char_count.py` | Char/word counter with budget check |
| `scripts/bib_check.py` | Static cross-check between citations and `.bib` |
| `scripts/bib_verify_online.py` | Crossref + OpenAlex similarity scoring |
| `scripts/sample_stats.py` | Per-cohort stats from `.xlsx`/`.csv` via YAML mapping |
| `scripts/new_version.sh` | Bump filename to `<prefix>-v(N+1)-YYYY-MM-DD-HHMM` |
| `scripts/diff_versions.sh` | Word-level diff between two versions |

---

## Out of Scope

- Writing an article from scratch.
- Editing `.bib` independently of a revision flow.
- Anonymisation pass (handle separately).
- Committing, pushing to remote, opening PRs, sending email.

For these, defer to the appropriate companion skill or to the user.

---

## Hooking This File Into Your Tool

This file lives inside the skill repo (`.claude/skills/article-revision/AGENTS.md`). To make your AI agent aware of it from a consuming project, link or copy it to the project root, or merge its contents into the project's existing `AGENTS.md`:

```bash
# from the consuming project root
ln -s .claude/skills/article-revision/AGENTS.md AGENTS.md
# or, if you already have an AGENTS.md, append a section pointing to the skill:
cat >> AGENTS.md <<'EOF'

## article-revision
See .claude/skills/article-revision/AGENTS.md for the full workflow.
EOF
```
