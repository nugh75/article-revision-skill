# OPENCODE.md — article-revision

This file activates the **article-revision** workflow for [opencode](https://github.com/sst/opencode) and other agents that read `OPENCODE.md`. It is kept in sync with `AGENTS.md` (the cross-tool standard) and mirrors the Claude Code skill defined in `SKILL.md` plus the workflow files in `workflow/`.

The two files (`AGENTS.md` and `OPENCODE.md`) carry identical content: edit one and propagate to the other to avoid drift.

---

## When this workflow activates

Trigger phrases (Italian or English):

- *"revisiona l'articolo"*, *"applichiamo i commenti di X"*, *"rivediamo il paragrafo 3"*
- *"let's process the reviewer comments"*, *"revise this paragraph"*
- explicit invocation if the host tool supports it (Claude Code: `/article-revision`)
- any request that mentions a Markdown article and a reviewer/co-author feedback to apply

If the user is doing something else (writing the article from scratch, generating new content, refactoring code), do NOT activate this workflow.

---

## Hard rules

1. **The user controls all git operations.** This skill never runs `git add`, `git commit`, `git push`, `git stage`. It only writes files. After each accepted change, briefly note that there are pending changes — and stop. If the user explicitly asks the skill to commit, do so without `--no-verify` and without `git push`.

2. **Per-point granularity.** Every revision proposal goes through the user as one atomic decision: `Accetta / Rifiuta / Modifica`. Never collapse multiple unrelated changes into one proposal.

3. **Always ask before creating.** Bootstrap, version bump, new files — every write step that creates something requires explicit confirmation. Idempotent steps (re-checks of already-existing artifacts) need no confirmation.

4. **No silent behaviour.** Whenever the skill takes a non-trivial action, output a one-line acknowledgement in chat.

5. **Surgical edits.** Touch only what the current point requires. No cleanup of adjacent prose, formatting, or unrelated bibliography.

6. **Chapter revision shows full text.** When operating in chapter-by-chapter mode, after applying all changes to a chapter the skill **must** display the full changed chapter text and wait for explicit user acceptance (`Si / Ancora modifiche`) before moving to the next chapter.

7. **Backup before edit.** Before modifying the article file in any revision pass (granular or chapter), the skill **must** create a timestamped backup copy. Use the versioning convention: copy the file to `<prefix>-v<CURRENT>-<YYYY-MM-DD-HHMM>[-anonima].bak.md` in the same directory, or use `scripts/new_version.sh` to create a proper version bump. This ensures the old version is never lost and the user can always revert.

---

## Layout the workflow expects

```
<project-root>/
├── .env                              # editorial parameters and credentials
├── articoli/                         # or another path; auto-detected
│   └── articolo-vN-YYYY-MM-DD[-anonima].md
├── bibliografia/
│   └── reference.bib
├── norme-redazionali/
│   └── norme-<journal>.md
├── dati/                             # optional, for sample-stats from raw data
└── revisioni/
    └── <reviewer-slug>/
        ├── progetto-revisione-vN.md
        └── scheda-revisione-vN.md
```

If anything is missing, run the bootstrap (`workflow/00-bootstrap.md`) — it walks the user through creating each piece without writing anything silently.

---

## `.env` keys

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

## Workflow steps (run in order)

| Step | File | When |
|---|---|---|
| 1 | `workflow/00-bootstrap.md` | first invocation in a new project, or whenever an artifact is missing |
| 2 | `workflow/10-setup.md` | after bootstrap; loads `.env`, norms, bib, active article, detects language |
| 3 | `workflow/20-plan-revision.md` | when user provides reviewer feedback |
| 4 | `workflow/30-iterate-points.md` | core loop — propose, ask, apply (no commit) |
| — | `workflow/35-chapter-revision.md` | *alternative to step 4* — top-down chapter-by-chapter revision (connectors, logical flow). Each chapter shown in full for acceptance after changes |
| 5 | `workflow/40-bibliography-check.md` | when a citation is touched or a reviewer flags one |
| 6 | `workflow/50-sample-description.md` | when methodology asks for sample stats from raw data |
| 7 | `workflow/60-bump-version.md` | end of round, or after `AUTO_BUMP_THRESHOLD` accepted changes |
| 8 | `workflow/70-final-sheet.md` | end of round |

Each workflow file contains the full step-by-step instructions. **Read the relevant workflow file before acting.**

---

## Revision scope (granularity)

The user can pick one of three scopes:

| Scope | Trigger phrases | Behaviour |
|---|---|---|
| **frammento** | *"correggi questa frase"*, *"questa virgolettatura"*, *"sostituisci X con Y"* | smallest possible diff |
| **paragrafo** (default for reviewer points) | *"rivedi questo paragrafo"*, *"il §3"* | one paragraph or numbered subsection |
| **capitolo** | *"rivediamo capitolo per capitolo"*, *"revisione dall'alto"*, *"passiamo al §2"* | chapter-by-chapter top-down pass: connectors, paragraph ordering, logical flow. Changes batched per chapter, full text shown for acceptance after each |
| **articolo intero** | *"rivedi tutto l'articolo"* | sequential walk; every change still individually approved |

Never collapse heterogeneous changes (citation + phrasing + structure) into one proposal — split them into separate decisions.

---

## Interaction pattern (binding format)

For every revision proposal, output exactly this structure:

```
## Punto N — <short title> · scope: <frammento|paragrafo|articolo>

**Originale** (`<articolo>:<line-range>`)
> <verbatim text>

**Proposta**
> <proposed text>

**Δ**: chars <signed> / words <signed> · bibliografia: <signed> voci · rischio: <basso|medio|alto>

**Norme rispettate**: <list>
**Eventuali deroghe**: <list, with reason>

**Decisione?** Accetta / Rifiuta / Modifica
```

Then **wait** for the user. Never apply pre-emptively.

On `Accetta`: edit the file(s), update the project file, increment the *accepted-since-last-bump* counter (HTML comment in the project file). **Do not commit.** Acknowledge briefly. If the counter reached `AUTO_BUMP_THRESHOLD`, propose a version bump.

On `Rifiuta`: annotate `Scartato` + reason in the project file. No file edits.

On `Modifica`: ask for direction, regenerate the proposal, repeat. After the eventual `Accetta`, label the point `Modificato` (not `Accettato`).

---

## Chapter revision (top-down)

Alongside granular point-by-point revision, the skill offers a
chapter-by-chapter mode for macro-level refinement.

### Focus areas

- **Connectors**: weak or missing transitions → appropriate connectives
  (see `reference/connettori-italiani.md` for Italian, `reference/english-connectors.md`
  for English articles).
- **Paragraph ordering**: reorder so argument flows logically
  (context → problem → evidence → implication).
- **Logical flow**: each paragraph picks up from the previous and hands off
  to the next.
- **Active voice**: prefer active constructions where they improve readability.
- **Structural consistency**: chapter opening hooks into preceding section;
  closing leads into the next.

### Triggers

*"rivediamo l'introduzione"*, *"passiamo alla metodologia"*, *"facciamo una
revisione dall'alto"*, or explicit section-by-section walk.

### Interaction pattern

```
## Capitolo N — <title> · revisione strutturale

**Analisi**
> <brief diagnosis>

**Interventi proposti**
1. <change — rationale>
2. <change — rationale>

**Applica?** Si / Rivediamo / Salta
```

- `Si` → apply all changes, then **show the full changed chapter text**
  and ask `**Accetti il capitolo così modificato?** Si / Ancora modifiche`.
- `Rivediamo` → iterate the proposal.
- `Salta` → next chapter, no changes.

The full-text review at the end of each chapter is **mandatory**: the user
must see the complete changed text before approving.

### After acceptance

Move to the next chapter, repeat. Changes are tracked in the project file
under a `Revisione strutturale` batch heading.

### Limits

- Does **not** verify bibliography (use `workflow/40-bibliography-check.md`).
- Does **not** handle sample-description updates (use `workflow/50-sample-description.md`).
- For single-sentence fixes, switch back to **frammento** scope.

---

## Language auto-detection

In `workflow/10-setup.md`:

1. Skip frontmatter and headings.
2. Read up to 1.000 chars of body text.
3. Score language by function words: `il, la, di, e, è, che, in, per` (it) vs `the, and, of, is, to, in, that, for` (en).
4. Highest score wins. Ties → ask the user. `.env` `ARTICLE_LANG` always wins.

If `ARTICLE_LANG=it`, anglicisms in proposals must come from `templates/anglicismi-accettati-it.md`. Surface any new anglicism in the proposal block under "Eventuali deroghe".

---

## Versioning convention

`<prefix>-vN-YYYY-MM-DD-HHMM[-anonima].md`

Multiple bumps in the same day stay distinct because of the time. The bump script (`scripts/new_version.sh`) accepts both legacy `vN-YYYY-MM-DD` and new `vN-YYYY-MM-DD-HHMM` source filenames.

---

## Word document handling

When the project contains Word files (`.docx`) or the revised Markdown article
must be rendered back to Word, preserve content first and enforce a clean
editorial layout:

- Headings must remain explicit headings, not body paragraphs styled manually.
- Body text must be black.
- Headings must be black unless the journal norms explicitly require another color.
- Body paragraphs must not have blank-line spacing between consecutive paragraphs; use paragraph spacing values instead of inserting empty paragraphs.
- Keep visible spacing between headings and the following body text through heading style spacing before/after, not through manual blank lines.
- Do not introduce extra paragraph breaks while converting `.docx` to Markdown or Markdown back to `.docx`.
- If a Word formatting change is proposed, present it as a revision point and ask `Accetta / Rifiuta / Modifica` before applying.

---

## Scripts

Run Python scripts with the project's Python venv. The bootstrap asks before
creating `.venv/`; if the user refuses, ask before using system Python and
remember the selected interpreter as `PYTHON_BIN`. Never fall back to `python3`
silently.

| Script | Purpose |
|---|---|
| `scripts/char_count.py` | char/word counter with budget check |
| `scripts/bib_check.py` | static cross-check between citations and `.bib` |
| `scripts/bib_verify_online.py` | Crossref + OpenAlex similarity scoring |
| `scripts/sample_stats.py` | per-cohort stats from `.xlsx`/`.csv` via YAML mapping |
| `scripts/new_version.sh` | bump filename to `<prefix>-v(N+1)-YYYY-MM-DD-HHMM` |
| `scripts/diff_versions.sh` | word-level diff between two versions |

---

## Out of scope

- Writing an article from scratch.
- Editing `.bib` independently of a revision flow.
- Anonymisation pass (handle separately).
- Committing, pushing to remote, opening PRs, sending email.

For these, defer to the appropriate companion skill or to the user.

---

## Hooking this file into opencode

This file lives inside the skill repo (`.claude/skills/article-revision/OPENCODE.md`). opencode looks for `AGENTS.md` and `OPENCODE.md` at the project root. To activate the skill in a consuming project, link or merge it:

```bash
# from the consuming project root — symlink approach (recommended)
ln -s .claude/skills/article-revision/OPENCODE.md OPENCODE.md
ln -s .claude/skills/article-revision/AGENTS.md   AGENTS.md

# or merge into an existing OPENCODE.md / AGENTS.md:
cat >> OPENCODE.md <<'EOF'

## article-revision
See .claude/skills/article-revision/OPENCODE.md for the full workflow.
EOF
```

Both files describe the same workflow. opencode and codex will pick up either one; Claude Code will pick up the SKILL.md natively. No further configuration is needed.
