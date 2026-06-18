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
| `/r-freeze` | **Congela** una parte conclusa nel freeze ledger; in seguito la skill avvisa prima di toccarla (`workflow/15-freeze-ledger.md`) |
| `/r-thaw` | **Scongela** una parte: torna modificabile senza avviso (`workflow/15-freeze-ledger.md`) |
| `/r-status` | **Stato revisione** — mappa frozen (🟢) vs open (🟡) dal freeze ledger (`workflow/15-freeze-ledger.md`) |
| `/r-bump` | Bump article version (hand off to `workflow/60-bump-version.md`) |
| `/r-sheet` | Generate final revision sheet (hand off to `workflow/70-final-sheet.md`) |
| `/r-chapter` | **Revisione Capitolo** — paragraph-depth revision of one section in cross-article context: terminology, cross-references, interfaces, redundancy, argument thread, norms compliance (`workflow/36-chapter-revision.md`) |
| `/r-gdrive` | **Google Drive Collaboration** — create/sync a shared Drive folder; pull colleague feedback as a revision source (`workflow/80-gdrive-collab.md`) |
| `/r-approve` | **Colleague Approval** — gate accepted modifications behind colleague sign-off before they count as final (`workflow/35-colleague-approval.md`) |
| `/r-redline` | **Redline Export** — colored old-vs-new manuscript for the reviewer + response-to-reviewers letter (`workflow/90-redline-export.md`) |

See `SKILL.md` for the full description of each mode.

If the user is doing something else (writing the article from scratch, generating new content, refactoring code), do **not** activate this workflow.

---

## Hard rules

1. **The user controls all git operations.** This skill never runs `git add`, `git commit`, `git push`, or `git stage` on its own initiative. It only writes files unless the user gives an explicit git instruction. After each accepted change, briefly note that there are pending changes and stop. If the user explicitly asks the skill to commit, do so without `--no-verify`. If the user explicitly authorizes a push, the skill may run `git push` after confirming the target branch/remote.
2. **Per-point granularity.** Every revision proposal goes through the user as one atomic decision: `Accept / Reject / Modify`. Never collapse multiple unrelated changes into one proposal.
3. **Always ask before creating.** Bootstrap, version bump, new files: every write step that creates something requires explicit confirmation. Idempotent re-checks of already-existing artifacts need no confirmation.
4. **No silent behavior.** Whenever the skill takes a non-trivial action, output a one-line acknowledgement in chat.
5. **Surgical edits.** Touch only what the current point requires. Do not clean up adjacent prose, formatting, or unrelated bibliography.
6. **Mandatory bump at session start.** Every new revision session MUST start with a version bump (vN → vN+1) before any edits. The bump is enforced by `10-setup.md` step 5. Never skip it. The `AUTO_BUMP_THRESHOLD` handles additional mid-session bumps separately.
7. **Task file per session.** Immediately after the bump, create `revisions/<article-slug>/task-<command-slug>-<bumped-version>.md` via `workflow/05-task.md`. Update it at each major step. Close it via `95-decision-log.md` at the end of the round. Never skip task file creation.
8. **Sync current files.** At the end of every revision round, `workflow/95-decision-log.md` must call `workflow/96-sync-current.md`, which overwrites `articles/current.md`, `articles/current.docx`, and `bibliography/bibliography.docx`. This step is mandatory and runs even when no changes were accepted. Never close a round without it.
9. **Revision closure triggers.** A round closes either when its natural perimeter is exhausted (last paragraph, last lens, last dimension, all reviewer points decided) OR when the user sends an explicit closure phrase (`chiudi`, `fine`, `ho finito`, `stop` / `close`, `done`, `finish`, `end`). In both cases, present a summary, ask for confirmation, then run the mandatory closure sequence.
10. **Freeze ledger.** Keep one persistent ledger per article at `revisions/<article-slug>/freeze-ledger.md` (`workflow/15-freeze-ledger.md`). Check it before every proposal: a 🟢 frozen part is *advisory* — warn (`⚠ congelata`) and require explicit `sì, procedi` before applying. When the user states a change but does not apply it this turn, record it in the ledger (🟡 open + intention) — never leave deferred intentions only in chat. Offer to freeze a unit when its work concludes.

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
    ├── <article-slug>/
    │   └── freeze-ledger.md          # persistent: frozen vs open parts + intentions
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
- `ARTICLE_STYLE_NOTES` (extra style notes loaded at setup)
- `PYTHON_BIN` (Python interpreter for skill scripts; default `.venv/bin/python`)
- `AUTO_BUMP_THRESHOLD` (default 5)
- `DATA_VERIFY_PATH` (root of the authoritative dataset/platform for empirical figures; enables `workflow/51-data-verification.md`)
- `DATA_VERIFY_NOTES` (free-text pointer to master file, key column, and formula location within `DATA_VERIFY_PATH`)
- `GDRIVE_REVIEW_FOLDER_ID` (shared Drive folder id for `/r-gdrive`; written back after `create`, reused to avoid duplicates)
- `RCLONE_REMOTE`, `GDRIVE_PATH` (rclone fallback for `/r-gdrive` when the MCP Drive connector is unavailable)

See `.env.example` for the complete template.

---

## Workflow Steps

| Step | File | When |
|---|---|---|
| 0 | `workflow/05-task.md` | Called by `10-setup.md` (create) and `95-decision-log.md` (close); tracks steps and produces session summary |
| 1 | `workflow/00-bootstrap.md` | First invocation in a new project, or whenever an artifact is missing |
| 2 | `workflow/10-setup.md` | After bootstrap; loads `.env`, norms, bibliography, active article, detects language, creates task file, ensures freeze ledger |
| 2a | `workflow/15-freeze-ledger.md` | Per-article freeze ledger: `ensure` (setup), advisory `check` before every proposal, `freeze`/`thaw`/`status`, `log-comment`, `carry-forward` (bump) |
| 3 | `workflow/20-plan-revision.md` | When user provides reviewer feedback |
| 4 | `workflow/30-iterate-points.md` | Core loop: propose, ask, apply (no commit) |
| 4a | `workflow/31-paragraph-by-paragraph.md` | Triggered by `/r-pp` or `/r-pp-a`. Per-paragraph diagnostic walk. |
| 4b | `workflow/32-peer-review-simulation.md` | Triggered by `/r-pr-2`. Generates three standalone documents in `revisions/<article-slug>/`. No interactive A/R/M. |
| 4c | `workflow/33-connector-revision.md` | Triggered by `/r-conn`. Connector and transition polish. |
| 4d | `workflow/34-global-revision.md` | Triggered by `/r-global`. Seven-lens structural review. |
| 4e | `workflow/36-chapter-revision.md` | Triggered by `/r-chapter`. Paragraph-depth revision of one section with full cross-article context across six dimensions. |
| 5 | `workflow/40-bibliography-check.md` | When a citation is touched or a reviewer flags one |
| 6 | `workflow/50-sample-description.md` | When methodology asks for sample stats from raw data |
| 7 | `workflow/60-bump-version.md` | Mandatory session-start bump + end of round, or after `AUTO_BUMP_THRESHOLD` accepted changes |
| 8 | `workflow/70-final-sheet.md` | End of round (optional) |
| 9 | `workflow/95-decision-log.md` + `96-sync-current.md` | Mandatory closure: decision log, task file close, sync current files |

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
| **Chapter revision** (`/r-chapter`) | `/r-chapter [§N]` | Paragraph-depth revision of one section with full cross-article context: terminology, cross-references, section interfaces, redundancy, argument thread, norms compliance |
| **Drive collaboration** (`/r-gdrive`) | `/r-gdrive [create\|push\|sync]` | Create/sync a shared Drive folder; pull colleague feedback into `revisions/<slug>/sources/`. No A/R/M — output is a source for later passes. User shares the folder. |
| **Colleague approval** (`/r-approve`) | `/r-approve` | Gate `Accepted` points behind colleague sign-off (Doc suggestions or `approvals.md`). `approve` → mark approved; `changes` → re-propose via A/R/M; `reject` → ask user (no auto-revert). |
| **Redline export** (`/r-redline`) | `/r-redline` | Colored old-vs-new `.docx`/`.html` for the reviewer + response-to-reviewers letter. Separate from the clean submission file. No A/R/M. |
| **Freeze / Thaw / Status** (`/r-freeze`, `/r-thaw`, `/r-status`) | `/r-freeze [unit]`, `/r-thaw [unit]`, `/r-status` | Mark a concluded part 🟢 frozen (advisory) / reopen it 🟡 / print the frozen-vs-open snapshot. Ledger-only, no article edit. |

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

## Feedback provenance

Every revision round carries a `Feedback source`, set in `20-plan-revision.md` and stored in the project file and final sheet:

- `journal` — a real reviewer/editor round. Its points feed the response letter; corrected figures must be disclosed there.
- `simulated` — produced internally (`/r-pr-2`, self-review). Internal QA only. `/r-pr-2` documents carry `source: simulated` in frontmatter and are read, not re-asked. Never present simulated feedback to the journal as external review. `70-final-sheet.md` keeps it out of the response letter.

Mixed rounds (a self-review layered on a real round) are split by tag: only `journal` points become response-letter material.

---

## Data verification (binding)

A numeric claim is never inherited. Whenever a proposal adds, changes, or relies on a percentage, count, mean, index, correlation, rank, or a qualitative claim contingent on a figure, `workflow/51-data-verification.md` must run **before** proposing: re-derive the figure from the authoritative source (`DATA_VERIFY_PATH` / `DATA_VERIFY_NOTES`, or a data-source section in the project's `AGENTS.md`), with an explicit criterion (column, filter, denominator, regex with word boundaries). If no source reproduces the value, the point is `Deferred` — never replaced with a plausible number. Skipping this when a figure is in scope is a binding violation, same severity as auto-committing.

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
- Opening PRs or sending email. Committing and pushing are allowed only on explicit user instruction, following the Git contract.

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
