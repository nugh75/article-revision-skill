---
name: article-revision
description: |
  Coordinate iterative revision of a scientific article in markdown.
  Supports two modes: (1) granular point-by-point revision triggered by
  reviewer feedback ("revisiona articolo", "applichiamo i commenti di X",
  "let's process the reviewer comments"), and (2) top-down chapter-by-chapter
  revision focused on connectors and logical flow ("revisione dall'alto",
  "rivediamo capitolo per capitolo", "passiamo al §2"). Also handles version
  bumps. Skill assumes a project layout with `articoli/`, `bibliografia/
  reference.bib`, `norme-redazionali/`, `revisioni/`, and an `.env` file.
  Auto-detects article language (it/en) and adapts the proposal style
  accordingly. Out of scope: writing the article from scratch, editing
  `.bib` independently, anonymisation, git operations.
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
├── articoli/                         # or any directory; auto-detected
│   └── articolo-vN-YYYY-MM-DD[-anonima].md
├── bibliografia/
│   └── reference.bib
├── norme-redazionali/
│   └── <journal-norms>.md
├── dati/                             # optional, for sample stats
└── revisioni/
    └── <reviewer-name>/
        ├── progetto-revisione-vN.md
        └── scheda-revisione-vN.md
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
   `revisioni/<reviewer>/progetto-revisione-vN.md` from the template, with
   each point in `Da decidere` state.
4. `workflow/30-iterate-points.md` — for each point, propose, ask
   `Accetta / Rifiuta / Modifica`, apply on Accept. **Never commit
   automatically** — the user controls git.
4b. `workflow/35-chapter-revision.md` — alternative to step 4 for
   top-down chapter-by-chapter revision. Focus: connectors, paragraph
   ordering, logical flow. Changes are proposed per chapter, applied,
   then the full chapter text is shown for acceptance before moving on.
5. `workflow/40-bibliography-check.md` — when a citation is touched or new
   keys are introduced.
6. `workflow/50-sample-description.md` — when the methodology asks for a
   sample-description update from raw data.
7. `workflow/60-bump-version.md` — when the user signals end of revision
   round, or when accepted modifications since the last version exceed
   `AUTO_BUMP_THRESHOLD` (default 5); the skill **proposes** a bump,
   never forces it. New filename: `articolo-v(N+1)-YYYY-MM-DD-HHMM.md`
   (date + 24h time, so multiple bumps in the same day stay distinct).
8. `workflow/70-final-sheet.md` — produce `revisioni/<reviewer>/
   scheda-revisione-vN.md` with the post-revision status.

Skipping is allowed if a step is not applicable; never silently skip a
step that *should* run.

## Interaction pattern (binding)

For every revision point, output exactly this shape in chat:

```
## Punto N — <short title>

**Originale** (`<file>:<line-range>`)
> <verbatim text>

**Proposta**
> <proposed text>

**Δ**: chars +X / words +Y · bibliografia: ±Z voci · rischio: <basso|medio|alto>
**Decisione?** Accetta / Rifiuta / Modifica
```

Then **wait** for the user. Do not pre-emptively apply.

- `Accetta` → apply via Edit, mark point as `Accettato` in the project file, increment the *accepted-since-last-bump* counter, advance to next. **Do not commit.** When the counter reaches `AUTO_BUMP_THRESHOLD`, suggest a version bump (see step 7).
- `Rifiuta` → annotate `Scartato` + reason, advance.
- `Modifica` → ask the user for direction, regenerate the proposal, repeat.

If the proposal involves multiple separate edits (e.g. an inline citation + a bibliography entry), still present them as a single coherent block, and apply them in one go.

**Evidenziazione visiva**: nella `**Proposta**`, marcate le parole cambiate rispetto all'originale con `<mark>...</mark>` attorno al segmento modificato. L'utente deve vedere a colpo d'occhio cosa cambia senza confrontare manualmente.

## Language auto-detection

In `00-setup.md`:

1. Skip frontmatter (lines between leading `---`).
2. Read up to 1.000 chars of body text.
3. Score language by function words: `il, la, di, e, è, che, in, per` for it; `the, and, of, is, to, in, that, for` for en.
4. Highest score wins; ties → fallback to `langdetect` if installed, else ask the user.
5. Persist to memory for the session as `ARTICLE_LANG`.

Override via `.env` `ARTICLE_LANG=...` always wins over auto-detection.

## Style of generated proposals

| `ARTICLE_LANG` | Proposal language | Notes |
|---|---|---|
| `it` | Italian, formal academic register | Anglicisms only when established convention; see `templates/anglicismi-accettati-it.md` |
| `en` | English, formal academic register | — |

Workflow files and skill chat scaffolding stay in English regardless of
`ARTICLE_LANG`.

- Evitare costruzioni oppositive del tipo "non ... ma ...". Preferire formulazioni positive o coordinate che chiariscano il rapporto logico.

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
  ask `Accetta / Rifiuta / Modifica` before applying.

## Git contract

- **The user controls all git operations.** The skill never commits, never
  stages, never pushes. Modifications to the article, the `.bib`, the
  project file, the scheda, are written to disk and remain there until
  the user decides to commit them.
- **Backup before edit.** Before modifying the article file in any revision
  pass, the skill **must** create a timestamped backup copy in the same
  directory. Use the versioning convention:
  `<prefix>-v<CURRENT>-<YYYY-MM-DD-HHMM>[-anonima].bak.md`. This ensures
  the previous version is never lost.
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
| **Frammento** (sentence-level / inline) | *"correggi questa frase"*, *"questa virgolettatura"*, *"sostituisci X con Y"* | Smallest possible diff. Touches a single sentence, citation, term, formatting fix. Goes through the same `Originale / Proposta / Decisione` pattern with surgical context. |
| **Paragrafo** (default during reviewer revision) | *"rivedi questo paragrafo"*, *"il §3 sulla discussione"* | Operates on a coherent block (one paragraph or one numbered subsection). Standard mode for processing reviewer points. |
| **Capitolo** (chapter-by-chapter pass) | *"rivediamo l'articolo capitolo per capitolo"*, *"revisione dall'alto"*, *"connettori e filo logico"*, *"passiamo al §2"* | Top-down pass through each article section. Focus: paragraph ordering, connectors, logical flow between paragraphs and sections. Changes are proposed as a batch per chapter, applied together, then the full changed chapter is shown for final acceptance before moving on. |
| **Articolo intero** (full pass) | *"rivedi tutto l'articolo"*, *"controlla coerenza dall'inizio alla fine"* | Sequential walk through every section, point by point. Each candidate change is still presented individually for `Accetta / Rifiuta / Modifica` — the user is not asked to approve a single mass-replacement. |

For paragrafo and articolo intero, breakable into more granular points
when the change touches separate concerns (e.g. a citation correction
plus a phrasing change in the same paragraph → two points, two
decisions, two micro-changes).

Never collapse multiple semantic changes into a single proposal just to
save chat tokens — the user must be able to accept one and reject the
other.

## Chapter revision (top-down)

Alongside the granular point-by-point revision, the skill offers a
chapter-by-chapter mode focused on macro-level textual refinement:

- **Connectors**: replace missing or weak transitions with appropriate
  connectives (see `reference/connettori-italiani.md` for Italian or
  `reference/english-connectors.md` for English articles).
- **Paragraph ordering**: reorder paragraphs within a chapter so the
  argument flows logically (e.g. context → problem → evidence → implication).
- **Logical flow**: ensure each paragraph picks up the thread from the
  previous one and hands it off to the next.
- **Active voice**: prefer active constructions over passive where they
  improve readability (applies to the chapter under revision, not globally).
- **Structural consistency**: verify that the chapter opening hooks into
  the preceding section and the closing leads into the next.

This mode works **one chapter at a time** and is triggered by phrases like
"rivediamo l'introduzione", "passiamo alla metodologia", or "facciamo una
revisione dall'alto capitolo per capitolo".

### Interaction pattern for chapter revision

```
## Capitolo N — <title> · revisione strutturale

**Analisi**
> <brief diagnosis: connectors found, ordering issues, logical gaps>

**Interventi proposti**
1. <change 1 — rationale>
2. <change 2 — rationale>
...

**Applica?** Si / Rivediamo / Salta
```

- `Si` → apply all proposed changes, then **show the full changed chapter
  text** and ask `**Accetti il capitolo così modificato?** Si / Ancora modifiche`.
- `Rivediamo` → user requests changes to the proposal; iterate the proposal.
- `Salta` → skip to the next chapter without changes.

The full-text review at the end of each chapter is **mandatory**: the user
must see the complete changed text before approving the chapter.

### After a chapter is accepted

Once a chapter is accepted, the skill moves to the next one and repeats the
same pattern. All changes across the chapter revision pass are tracked in
the project file as a single batch under a `Revisione strutturale` heading.

### Limits

- This mode does **not** verify bibliography entries (use step 5,
  `workflow/40-bibliography-check.md`).
- This mode does **not** handle sample-description updates from raw data
  (use step 6, `workflow/50-sample-description.md`).
- For fine-grained fixes on a single sentence or citation, switch back to
  **Frammento** scope.

## Skill is **not** for

- Writing an article from scratch — defer to the journal-specific style skill.
- Editing `.bib` independently — defer to the bibliography skill (e.g.
  `praxis-bibliography-citations`).
- Anonymisation (XXX placeholders) — handle in a dedicated pass.
- Committing, pushing to remote, opening PRs, sending email.
