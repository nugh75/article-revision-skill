# Colleague Approvals — <article short title>

Structured fallback for colleague sign-off (used when Google Doc inline
suggestions cannot be read programmatically).

**How to fill:** one row per revision point. Set **Verdict** to exactly one
of `approve`, `changes`, `reject`. Add your name and a short note. Leave a
row untouched if you have no opinion (it stays `pending`).

| Point | Short title | Verdict | Colleague | Note |
|---|---|---|---|---|
| P1 | <title> | pending | <name> | <note> |
| P2 | <title> | pending | <name> | <note> |
| P3 | <title> | pending | <name> | <note> |

Legend:
- `approve` — change is good as applied.
- `changes` — keep the intent but adjust; describe how in **Note**.
- `reject` — do not make this change; say why in **Note** (final call stays
  with the corresponding author).
- `pending` — not yet reviewed.

Do not edit the article text here; this file only records verdicts. The
skill ingests it via `/r-gdrive sync` and acts on it via `/r-approve`.
