# Chapter revision — top-down structural pass

Use this workflow as an alternative to `30-iterate-points.md` when the
user asks for a chapter-by-chapter revision focused on connectors,
paragraph ordering, and logical flow rather than granular point-by-point
fixes.

## When to activate

- User says *"rivediamo l'articolo capitolo per capitolo"*, *"revisione
  dall'alto"*, *"connettori e filo logico"*, *"rivediamo l'introduzione"*,
  *"passiamo al §2"*, or similar.
- The project has been set up (`00-bootstrap.md` and `10-setup.md`
  are complete).

## Prerequisites

- `.env` loaded, article file identified.
- Article language detected (`ARTICLE_LANG`).
- Connector reference available:
  - `reference/connettori-italiani.md` (if `ARTICLE_LANG=it`)
  - `reference/english-connectors.md` (if `ARTICLE_LANG=en`)

## Step-by-step

### 1. Identify chapters

Parse the article for `*N – Title*` or `## N. Title` headings. Present
the chapter list to the user:

```
**Capitoli identificati:**
1. Introduzione (§1)
2. Metodologia (§2)
3. Risultati (§3)
4. Discussione (§4)
5. Conclusioni (§5)

**Da dove iniziamo?**
```

Wait for the user to pick the first chapter.

### 2. Analyse the chapter

Read the chapter in full. Diagnose:

- **Connectors**: are transitions between paragraphs explicit? Are
  there abrupt jumps without a connective? (See the connector reference
  file for appropriate replacements.)
- **Paragraph ordering**: does the argument follow a logical
  progression? Should any paragraph move?
- **Logical flow**: does each paragraph open by picking up the thread
  from the previous one? Does it close by handing off to the next?
- **Active vs passive**: are there passive constructions that would
  read better in the active voice?
- **Structural consistency**: does the first sentence anchor the
  chapter to the preceding section? Does the last sentence lead into
  the next chapter?

### 3. Propose changes

Output the proposal block:

```
## Capitolo N — <title> · revisione strutturale

**Analisi**
> <brief diagnosis>

**Interventi proposti**
1. <change — rationale>
2. <change — rationale>

**Applica?** Si / Rivediamo / Salta
```

- Each intervention must be specific and actionable.
- When a connector replacement is proposed, cite the original and the
  replacement (e.g. *"Inoltre" → "A questo scopo"* for a tighter
  purpose link).
- When a paragraph is reordered, show the new order explicitly.
- When a sentence is rewritten (active → passive), show both versions.

### 4. User decision

- `Si` → apply all proposed edits to the article file. Then **read the
  full changed chapter** and display it in chat, followed by:
  `**Accetti il capitolo così modificato?** Si / Ancora modifiche`.
- `Rivediamo` → ask the user what to adjust. Regenerate the proposal.
  Repeat until `Si` or `Salta`.
- `Salta` → skip this chapter with no changes.

If the user selects `Ancora modifiche`, go back to step 3 with a
refined proposal based on their direction.

### 5. After acceptance

1. Add a note to the project file under a `Revisione strutturale`
   batch heading (create the heading if it does not exist):

   ```markdown
   ## Revisione strutturale — <date>

   - §N <title>: <summary of changes>
   ```

2. Increment the *accepted-since-last-bump* counter.

3. Ask: **"Prossimo capitolo?"** and list the remaining chapters.
   Return to step 2 with the chosen chapter.

4. When no chapters remain, or when the user says *"fermiamo qui"*,
   stop and summarise:

   ```
   **Revisione strutturale completata.**
   Capitoli revisionati: <list>
   Capitoli saltati: <list>
   Modifiche totali: <count>
   ```

## Edge cases

- **Single-chapter article**: treat the whole article as one chapter.
- **No changes needed**: if the chapter reads well, say so and move on.
- **User wants granular fix within chapter**: switch to `Frammento`
  scope for that sentence, then return to chapter mode.

## Relationship to other workflow steps

| Step | Relationship |
|---|---|
| `30-iterate-points.md` | Exclusive alternative — use one or the other per session. |
| `40-bibliography-check.md` | Run after this pass if citations were touched. |
| `60-bump-version.md` | Run after completion if `AUTO_BUMP_THRESHOLD` is reached. |
| `70-final-sheet.md` | Run at the end of the full revision round. |
