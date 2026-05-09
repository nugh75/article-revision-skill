---
name: article-revision
description: |
  Coordinate iterative revision of a scientific article in markdown. Trigger
  when the user asks to apply reviewer feedback ("revise article",
  "apply reviewer X comments", "let's process the reviewer comments"),
  to bump the article to a new version, or invokes `/article-revision`
  explicitly. Skill assumes a project layout with `articles/`, `bibliography/
  reference.bib`, `editorial-norms/`, `revisions/`, and an `.env` file.
  For each reviewer point: shows original text + proposed change in chat,
  asks Accept / Reject / Modify, and applies on Accept without committing.
  Auto-detects article language (it/en) and adapts
  the proposal style accordingly. Out of scope: writing the article from
  scratch (use the journal-specific style skill, e.g. `praxis-article-style`),
  managing the `.bib` directly (use `praxis-bibliography-citations` or its
  equivalent).
---

# Article Revision Skill

Operational layer that orchestrates the existing article-style and
bibliography skills around a structured revision workflow.

## Authority

Editorial rules in priority order:

1. The journal's editorial norms file referenced by `EDITORIAL_NORMS_PATH`
   in `.env` (binding for the article).
2. The journal-specific style skill installed in the project (e.g.
   `praxis-article-style`), if any.
3. This skill — operational orchestration only.

When norms and user preference conflict, **norms win**. Surface the
conflict explicitly in chat.

## Project layout (required)

```
<project-root>/
├── .env
├── articles/                         # or any directory; auto-detected
│   └── article-vN-YYYY-MM-DD[-anonymous].md
├── bibliography/
│   └── reference.bib
├── editorial-norms/
│   └── <journal-norms>.md
├── data/                             # optional, for sample stats
└── revisions/
    └── <reviewer-name>/
        ├── revision-plan-vN.md
        └── final-sheet-vN.md
```

If any of these is missing, the skill asks the user to confirm an
alternative path or to create it. Never invent paths silently.

## `.env` contract

Required:

- `EDITORIAL_LIMIT_CHARS` — hard char cap (e.g. `40000`).
- `EDITORIAL_NORMS_PATH` — relative path to the norms file.
- `BIBLIOGRAPHY_BIB_PATH` — relative path to `reference.bib`.

Optional:

- `EDITORIAL_LIMIT_WORDS` — alternative to chars, if the journal uses words.
- `ARTICLE_LANG` — forces language detection (`it`, `en`, …).
- `ARTICLE_STYLE_NOTES` — extra style notes to load.
- `PYTHON_BIN` — Python interpreter for skill scripts. Defaults to
  `<project-root>/.venv/bin/python` after bootstrap. If no venv exists, ask the
  user before creating one or falling back to system Python.
- `CROSSREF_USER_AGENT` — for `bib_verify_online.py`.
- `OPENALEX_USER_AGENT` — same.
- `ZOTERO_USER_ID`, `ZOTERO_API_KEY`, `ZOTERO_GROUP_ID` — Zotero integration.

## Python execution contract

- All Python scripts must run through the project virtual environment:
  `<project-root>/.venv/bin/python`.
- On first invocation, if `.venv/` is missing, ask whether to create it and
  install `.claude/skills/article-revision/requirements.txt`.
- If the user refuses venv creation, ask whether system Python may be used for
  this session. Never fall back to `python3` silently.
- Remember the selected interpreter as `PYTHON_BIN` for the session; append it
  to `.env` only with explicit user confirmation.
- Shell scripts may run directly, but any Python they invoke must use
  `PYTHON_BIN` or the venv interpreter.

## Workflow files (must be followed in order on first invocation)

1. `workflow/00-bootstrap.md` — set up the revision environment if missing
   (venv with Python deps, `.bib` file, `.env` with editorial parameters
   and Zotero credentials, editorial norms file). Idempotent: skips
   anything already in place.
2. `workflow/10-setup.md` — load `.env`, norms, bib, current article version,
   detect article language.
3. `workflow/20-plan-revision.md` — accept reviewer feedback, generate
   `revisions/<reviewer>/revision-plan-vN.md` from the template, with
   each point in `To decide` state.
4. `workflow/30-iterate-points.md` — for each point, propose, ask
   `Accept / Reject / Modify`, apply on Accept. **Never commit
   automatically** — the user controls git.
5. `workflow/40-bibliography-check.md` — when a citation is touched or new
   keys are introduced.
6. `workflow/50-sample-description.md` — when the methodology asks for a
   sample-description update from raw data.
7. `workflow/60-bump-version.md` — when the user signals end of revision
   round, or when accepted modifications since the last version exceed
   `AUTO_BUMP_THRESHOLD` (default 5); the skill **proposes** a bump,
   never forces it. New filename: `article-v(N+1)-YYYY-MM-DD-HHMM.md`
   (date + 24h time, so multiple bumps in the same day stay distinct).
8. `workflow/70-final-sheet.md` — produce `revisions/<reviewer>/
   final-sheet-vN.md` with the post-revision status.

Skipping is allowed if a step is not applicable; never silently skip a
step that *should* run.

## Interaction pattern (binding)

For every revision point, output exactly this shape in chat:

```
## Point N — <short title>

**Original** (`<file>:<line-range>`)
> <verbatim text>

**Proposal**
> <proposed text>

**Δ**: chars +X / words +Y · bibliography: ±Z entries · risk: <low|medium|high>
**Decision?** Accept / Reject / Modify
```

Then **wait** for the user. Do not pre-emptively apply.

- `Accept` → apply via Edit, mark point as `Accepted` in the project file, increment the *accepted-since-last-bump* counter, advance to next. **Do not commit.** When the counter reaches `AUTO_BUMP_THRESHOLD`, suggest a version bump (see step 7).
- `Reject` → annotate `Rejected` + reason, advance.
- `Modify` → ask the user for direction, regenerate the proposal, repeat.

If the proposal involves multiple separate edits (e.g. an inline citation + a bibliography entry), still present them as a single coherent block, and apply them in one go.

## Language auto-detection

In `00-setup.md`:

1. Skip frontmatter (lines between leading `---`).
2. Read up to 1.000 chars of body text.
3. Score language by function words for the candidate languages.
4. Highest score wins; ties → fallback to `langdetect` if installed, else ask the user.
5. Persist to memory for the session as `ARTICLE_LANG`.

Override via `.env` `ARTICLE_LANG=...` always wins over auto-detection.

## Style of generated proposals

| `ARTICLE_LANG` | Proposal language | Notes |
|---|---|---|
| `it` | Italian, formal academic register | Anglicisms only when established convention; see `templates/accepted-anglicisms-it.md` |
| `en` | English, formal academic register | — |

Workflow files and skill chat scaffolding stay in English regardless of
`ARTICLE_LANG`.

## Word document handling

When the project contains Word files (`.docx`) or the revised Markdown article
must be rendered back to Word, preserve content first and enforce a clean
editorial layout:

- Headings must remain explicit headings, not body paragraphs styled manually.
- Body text must be black.
- Headings must be black unless the journal norms explicitly require another
  color.
- Body paragraphs must not have blank-line spacing between consecutive
  paragraphs; use paragraph spacing values instead of inserting empty
  paragraphs.
- Keep visible spacing between headings and the following body text through
  heading style spacing before/after, not through manual blank lines.
- Do not introduce extra paragraph breaks while converting `.docx` to Markdown
  or Markdown back to `.docx`.
- If a Word formatting change is proposed, present it as a revision point and
  ask `Accept / Reject / Modify` before applying.

## Git contract

- **The user controls all git operations.** The skill never commits, never
  stages, never pushes. Modifications to the article, the `.bib`, the
  project file, the final sheet, are written to disk and remain there until
  the user decides to commit them.
- After each accepted change, the skill briefly notes that there are
  pending changes — without performing any git action.
- Suggested commit message format (when the user asks): `revision(<reviewer-slug>): <point-id> — <summary>`. The skill can supply the message text in chat for the user to paste.
- If the user explicitly asks the skill to commit on their behalf, do so
  with `git commit` (no `--no-verify`, no `git push`).

## Revision scope (granularity)

The skill can operate on three levels. The user picks the scope at any
point in the workflow:

| Scope | Trigger phrases | Behaviour |
|---|---|---|
| **Fragment** (sentence-level / inline) | *"fix this sentence"*, *"adjust this quotation"*, *"replace X with Y"* | Smallest possible diff. Touches a single sentence, citation, term, formatting fix. Goes through the same `Original / Proposal / Decision` pattern with surgical context. |
| **Paragraph** (default during reviewer revision) | *"revise this paragraph"*, *"section 3 discussion"* | Operates on a coherent block (one paragraph or one numbered subsection). Standard mode for processing reviewer points. |
| **Whole article** (full pass) | *"revise the whole article"*, *"check coherence from start to finish"* | Sequential walk through every section, point by point. Each candidate change is still presented individually for `Accept / Reject / Modify` — the user is not asked to approve a single mass-replacement. |

For paragraph and whole-article scopes, break into more granular points
when the change touches separate concerns (e.g. a citation correction
plus a phrasing change in the same paragraph → two points, two
decisions, two micro-changes).

Never collapse multiple semantic changes into a single proposal just to
save chat tokens — the user must be able to accept one and reject the
other.

## Skill is **not** for

- Writing an article from scratch — defer to the journal-specific style skill.
- Editing `.bib` independently — defer to the bibliography skill (e.g.
  `praxis-bibliography-citations`).
- Anonymisation (XXX placeholders) — handle in a dedicated pass.
- Committing, pushing to remote, opening PRs, sending email.
