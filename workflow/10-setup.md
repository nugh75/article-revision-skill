# 10 — Setup

Run after `00-bootstrap.md`. It loads configuration into the session and identifies the active article. Do **not** repeat it in the same session unless the user changes project or article.

## 1. Locate `.env`

Walk up from the current working directory until a `.env` file is found, or the filesystem root is reached. If none is found, ask:

> I cannot find a `.env` in the project root. Do you want me to create one with default values? (character limit, `.bib` path, norms path)

Required keys:

- `EDITORIAL_LIMIT_CHARS` (or `EDITORIAL_LIMIT_WORDS`)
- `BIBLIOGRAPHY_BIB_PATH`
- `EDITORIAL_NORMS_PATH`

Optional: `ARTICLE_LANG`, `ARTICLE_STYLE_NOTES`, `CROSSREF_USER_AGENT`, `OPENALEX_USER_AGENT`, Zotero keys, `PYTHON_BIN`.

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

If `articles/` does not exist, search the project root and likely directories (`docs/`, `drafts/`, `revisions/`) for files matching `article-v*-*.md`. Report the candidate to the user before continuing.

## 4. Detect Article Language

Read up to 1,000 chars of body text, skipping frontmatter and first headings. Score language using function words for candidate languages.

Pick the higher score. Tie-breaker: ask the user. The result is `ARTICLE_LANG`. If `.env` declares `ARTICLE_LANG`, that always wins.

## 5. Confirm Setup

Output a one-shot summary:

```text
Setup complete

- Article: <path>
- Version: vN-YYYY-MM-DD
- Language: <it|en|...> (<auto|env>)
- Norms: <path>
- Limit: <N> {chars|words}
- Current count: <M> ({over|under} by X)
- Bibliography: <path> (Y entries)

Ready. Proceed?
```

After confirmation, wait for the next instruction, typically reviewer feedback for `20-plan-revision.md`.
