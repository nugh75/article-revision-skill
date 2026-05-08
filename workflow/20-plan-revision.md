# 20 — Plan revision

When the user provides reviewer feedback (textual letter, list of comments, or a markdown file with the review), generate the project file.

## 1. Acquire reviewer identity

Ask the user — unless already supplied:

> Come si chiama il/la reviewer? (Userò un *slug* per il filename e i commit, es. `elisa`, `peer-1`, `editor`.)

## 2. Parse the feedback into discrete points

Split the reviewer's letter into atomic points. One point = one actionable observation, even if the reviewer wraps several together. Each point should map to:

- a section of the article (e.g. *"Introduzione"*, *"Metodologia – Campione"*);
- a level of priority (`alta`, `media`, `bassa`);
- a verbatim quote of the reviewer's words.

Number them progressively. If a single sentence from the reviewer covers multiple sections, split into multiple points.

## 3. Generate `revisioni/<reviewer-slug>/progetto-revisione-vN.md`

Use `templates/progetto-revisione.md` and substitute:

- `{{REVIEWER}}` — full name or slug;
- `{{VERSION}}` — the article version (e.g. `9`);
- `{{ARTICLE_PATH}}` — relative path;
- `{{EDITORIAL_LIMIT}}`, `{{LIMIT_UNIT}}` — from `.env`;
- `{{INITIAL_COUNT}}` — output of `scripts/char_count.py --limit-from-env`;
- `{{ARTICLE_LANG}}` — from setup;
- `{{NORMS_PATH}}` — from `.env`.

Then for each point, write a section under `## Revisione punto per punto` with all subfields populated **except** `Decisione` (which stays `Da decidere`) and the actual proposal text (filled later in `20-iterate-points.md`).

Populate the checklist at the bottom:

```
| # | Punto | Sezione | Stato in v<N> | Priorità | Decisione |
```

## 4. Confirm in chat

The skill writes the project file to disk. **The user controls git** — no auto-commit. If asked, the suggested commit message is:

```
revision(<slug>): start — N points planned
```

Then in chat:

```
✅ Progetto revisione creato: <path>

N punti pianificati:
1. <titolo> — <sezione> (priorità <alta|media|bassa>)
2. ...

Iniziamo dal punto 1? (sì / scegli punto N / posticipa)
```

Wait for the user.
