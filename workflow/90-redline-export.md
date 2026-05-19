# 90 — Redline Export (for the journal reviewer)

Triggered by `/r-redline`. Produces the **marked-up** old-vs-new manuscript
the reviewer asked for, plus the point-by-point response letter.

The clean revised manuscript remains the submission file. This redline is a
**separate** deliverable. Many journals (ECPS included) forbid revision marks
in the final Word file, so never submit the redline as the manuscript.

## 1. Pick the two versions

- `OLD` = the version the reviewer last saw (usually the submitted vN, or the
  version recorded as `submitted` in the project file).
- `NEW` = the current revised version (highest vN after the revision pass).

Confirm both paths with the user if ambiguous. Accept `.md` or `.docx`.

## 2. Generate the colored redline

```bash
$PYTHON_BIN .../scripts/make_redline.py <OLD> <NEW> \
    --out-prefix revisions/<slug>/redline-vOLD-to-vNEW \
    --title "<article short title> — redline vOLD→vNEW"
```

Outputs in `revisions/<slug>/`:

| File | Use |
|---|---|
| `redline-…​.html` | Browser/print view, colors via CSS |
| `redline-…​.docx` | Word file with **real OOXML color runs**: inserted = green + underline, deleted = red + strikethrough |
| `redline-…​.redline.md` | Intermediate (raw OOXML); can be deleted |

Report the insertion/deletion counts printed by the script.

## 3. Generate the response-to-reviewers letter

Copy `templates/response-to-reviewers.md` to
`revisions/<slug>/response-to-reviewers-vNEW.md` and fill one row per
reviewer point:

- the reviewer's request (verbatim or paraphrased),
- what was changed,
- where (section / line / paragraph in NEW),
- a one-line rationale.

Pull the mapping from the project file's accepted points and from any
`reviewer-feedback.md` already in `revisions/<slug>/`.

## 4. Notify

```text
Redline ready:
- revisions/<slug>/redline-vOLD-to-vNEW.docx  (+I ins / D del-or-edit)
- revisions/<slug>/redline-vOLD-to-vNEW.html
- revisions/<slug>/response-to-reviewers-vNEW.md  (M points, K unfilled)

Submission set for the journal:
  1. clean revised .docx (no marks)        — produced by the Word export step
  2. redline .docx (this file)             — for the reviewer
  3. response-to-reviewers letter          — point-by-point

The skill does not email or upload. Use `/r-gdrive` to place these in the
shared Drive folder, or hand them to the user.
```

Never commit automatically — the user controls git.
