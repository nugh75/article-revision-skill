# 10 — Setup

Run after `00-bootstrap.md`. Loads the configuration into the session and identifies the active article. Do **not** repeat it on subsequent calls in the same session unless the user changes project or article.

## 1. Locate `.env`

Walk up from the current working directory until a `.env` file is found, or the filesystem root is reached. If none, ask the user:

> Non trovo un `.env` nella radice del progetto. Vuoi che ne crei uno con i valori di default? (limite caratteri, percorso `.bib`, percorso norme)

Required keys:

- `EDITORIAL_LIMIT_CHARS` (or `EDITORIAL_LIMIT_WORDS`)
- `BIBLIOGRAPHY_BIB_PATH`
- `EDITORIAL_NORMS_PATH`

Optional: `ARTICLE_LANG`, `ARTICLE_STYLE_NOTES`, `CROSSREF_USER_AGENT`, `OPENALEX_USER_AGENT`, Zotero keys.

## 2. Read the editorial norms

Open the file at `EDITORIAL_NORMS_PATH`. Identify:

- length cap (chars or words);
- citation style (APA author-year, Pandoc keys, IEEE numeric, …);
- quotation marks (`"…"`, `«…»`, English curly);
- italics rules;
- section structure expected;
- bibliography format.

Hold this in working memory for the session.

## 3. Identify the active article

Look for `articoli/articolo-v*-*.md`. If multiple versions, pick the one with the highest `vN`.

If `articoli/` doesn't exist, search the project root and likely directories (`revisioni-articolo/`, `docs/`, …) for files matching `articolo-v*-*.md`. Report the candidate to the user before continuing.

## 4. Detect article language

Read up to 1.000 chars of body text (skipping frontmatter and first headings). Score language:

- it: presence of `il, la, di, e, è, che, in, per, su`
- en: presence of `the, and, of, is, to, in, that, for, on`

Pick the higher score. Tie-breaker: ask the user. The result is `ARTICLE_LANG`. If `.env` declares `ARTICLE_LANG`, that always wins.

## 5. Confirm setup with the user

Output a one-shot summary:

```
✅ Setup completato

- Articolo: <path>
- Versione: vN-YYYY-MM-DD
- Lingua: <it|en> (auto)
- Norme: <path>
- Limite: <N> {chars|words}
- Conteggio attuale: <M> ({over|under} di X)
- Bibliografia: <path> (Y voci)

Pronto. Procediamo?
```

After confirmation, wait for the next instruction (typically: receive reviewer feedback → run `20-plan-revision.md`).
