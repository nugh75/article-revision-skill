# 10 — Setup

Run after `00-bootstrap.md`. It loads configuration into the session and identifies the active article. Do **not** repeat it in the same session unless the user changes project or article.

## 1. Locate `.env`

Walk up from the current working directory until a `.env` file is found, or the filesystem root is reached. If none is found, ask:

> I cannot find a `.env` in the project root. Do you want me to create one with default values? (character limit, `.bib` path, norms path)

Required keys:

- `EDITORIAL_LIMIT_CHARS` (or `EDITORIAL_LIMIT_WORDS`)
- `BIBLIOGRAPHY_BIB_PATH`
- `EDITORIAL_NORMS_PATH`

Optional: `ARTICLE_LANG`, `ARTICLE_STYLE_NOTES`, `CROSSREF_USER_AGENT`, `OPENALEX_USER_AGENT`, Zotero keys, `PYTHON_BIN`, `DATA_VERIFY_PATH`, `DATA_VERIFY_NOTES`.

If `DATA_VERIFY_PATH` is set (root of the authoritative dataset/platform for the article's empirical figures), hold it and `DATA_VERIFY_NOTES` in working memory: `workflow/51-data-verification.md` uses them to re-derive any numeric claim instead of inheriting it.

## 2. Read Editorial Norms

Open the file at `EDITORIAL_NORMS_PATH`. Identify:

- length cap (chars or words);
- citation style (APA author-year, Pandoc keys, IEEE numeric, etc.);
- quotation marks;
- italics rules;
- expected section structure;
- bibliography format.

Hold this in working memory for the session.

## 3. Identify Active Article

Look for `articles/article-v*-*.md`. If multiple versions exist, pick the one with the highest `vN`.

If the chosen filename contains `-drive`, treat that marker as provenance only: it means the file was downloaded from Google Drive. Keep the file as the active source, but do not propagate `-drive` when creating the bumped version.

If `articles/` does not exist, search the project root and likely directories (`docs/`, `drafts/`, `revisions/`) for files matching `article-v*-*.md`. Report the candidate to the user before continuing.

## 4. Detect Article Language

Read up to 1,000 chars of body text, skipping frontmatter and first headings. Score language using function words for candidate languages.

Pick the higher score. Tie-breaker: ask the user. The result is `ARTICLE_LANG`. If `.env` declares `ARTICLE_LANG`, that always wins.

## 5. Mandatory Session Bump

**Every new revision session MUST start with a version bump.** After setup confirms the active article:

First check whether this is a resume, not a new session:

1. Search `revisions/<article-slug>/task-*-*.md` for frontmatter
   `status: paused` or `status: in-progress`.
2. If one exists and the user asked to resume (`riprendi`, `continua`,
   `/r-resume`, same command after interruption), call
   `workflow/06-handoff.md#resume-from-handoff`.
3. On resume, do **not** run a new bump, do **not** create a new task file, and
   continue from the task file's `## Handoff / Ripresa`.
4. If a paused/in-progress task exists but the user did not clearly ask for a
   new session, show the newest candidate and ask whether to resume it or start
   a new session. Do not bump until that choice is clear.

If this is a new session:

1. Call `60-bump-version.md` to create v(N+1) from the current vN.
2. Do **not** proceed to any revision workflow until the bump is confirmed and completed.
3. If the session already created a bump earlier (detectable via `accepted_since_bump: 0` + today's date entry in project file), skip — do not double-bump.

In chat, after the setup summary, immediately ask:

```text
Setup complete.

Bump obbligatorio: vN → v(N+1) prima di iniziare la revisione.
Procedo con il bump? (sì / salta e usa vN / annulla)
```

Only if the user says `sì`, run the bump via `60-bump-version.md`. If they say `salta e usa vN`, warn that this breaks the mandatory bump rule and ask them to confirm again. Never skip the bump silently.

## 6. Confirm Setup

Output a one-shot summary after the bump:

```text
Setup complete

- Article: <path>
- Version: vN-YYYY-MM-DD → v(N+1)-YYYY-MM-DD-HHMM (bump effettuato)
- Language: <it|en|...> (<auto|env>)
- Norms: <path>
- Limit: <N> {chars|words}
- Current count: <M> ({over|under} by X)
- Bibliography: <path> (Y entries)

Ready. Proceed?
```

## 7. Create Task File

Immediately after the bump is confirmed, call `workflow/05-task.md` — action
`create` — passing:

- `COMMAND` from the slash command or trigger phrase used this session.
- `ARTICLE_PATH`, `ARTICLE_SLUG`, `ARTICLE_VERSION`, `BUMPED_VERSION` from working memory.
- `REVIEWER_LANE` from the revision plan or `self` for proactive modes.

The task file path is stored as `TASK_FILE_PATH` in working memory.

## 8. Ensure Freeze Ledger

Call `workflow/15-freeze-ledger.md` — action `ensure`. This creates
`revisions/<article-slug>/freeze-ledger.md` from `templates/freeze-ledger.md` if
absent, otherwise loads it and updates `reconciled-version`/`updated` to the
bumped version. Store `FREEZE_LEDGER_PATH` in working memory.

From here on, the ledger governs the advisory check before every proposal
(`15-freeze-ledger.md` §4–5) and records frozen/open units and their intentions.
Confirm in chat (one line):

```text
Freeze ledger: revisions/<article-slug>/freeze-ledger.md (🟢 X frozen · 🟡 Y open)
```

After creation, wait for the next instruction (reviewer feedback, `/r-pp`, `/r-pr-2`, `/r-conn`, `/r-global`, `/r-chapter`, `/r-status`).
