# 30 — Iterate points

Core loop. Apply to a single point, a paragraph, or the whole article — the user picks the scope.

## 0. Determine scope

If the user's instruction mentions a specific scope, use it:

- *"correggi questa frase"* → **frammento**
- *"rivedi questo paragrafo"* / reviewer point → **paragrafo**
- *"rivedi tutto l'articolo"* → **articolo intero** (sequential walk)

If unspecified, default to **paragrafo** when processing a reviewer point, **frammento** otherwise. Always confirm in the proposal block which scope is being used.

## 1. Load context

Read the relevant section(s) of the article. Identify the exact lines that the change touches:

- **frammento**: the single sentence or inline element (citation, formatting, term).
- **paragrafo**: the smallest coherent block (one paragraph or one numbered subsection).
- **articolo intero**: walk every section, generating proposals one at a time. Never produce a single mass-replacement.

If the change involves a citation, run `40-bibliography-check.md` for the relevant key first.

If the change requires sample-description data, run `50-sample-description.md` first.

## 2. Generate the proposal

Apply:

- the editorial norms loaded in setup;
- the journal-specific style skill, if available (e.g. `praxis-article-style`);
- `templates/anglicismi-accettati-it.md` if `ARTICLE_LANG=it`;
- the principle of *minimum surgical change*: alter only what the point requires.

Never collapse multiple separate concerns into a single proposal. If the same paragraph needs both a citation correction and a phrasing change, present two consecutive proposals, each with its own decision.

## 3. Present in chat (binding format)

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

Wait for the user. Do **not** apply pre-emptively.

## 4. Handle the response

### Accetta

1. Apply via Edit on the article (and `.bib` or other files if relevant).
2. Update the project file: `Decisione` = `Accettato`.
3. Increment the *accepted-since-last-bump* counter (stored as an HTML comment in the project file: `<!-- accepted_since_bump: N -->`).
4. Run `scripts/char_count.py --limit-from-env` and report the new count + delta.
5. **Do not commit.** Just acknowledge:

   ```
   ✅ Applicato. Modifiche pendenti (non committate): N file.
   Conteggio: M chars (over/under di X). Punti accettati dal bump: <K>/<AUTO_BUMP_THRESHOLD>.
   ```

6. If the counter has reached `AUTO_BUMP_THRESHOLD`, propose a bump:

   ```
   Hai accettato <AUTO_BUMP_THRESHOLD> modifiche dall'ultimo bump.
   Vuoi creare una nuova versione del file ora? (sì / continuiamo)
   ```

   On `sì`, hand off to `60-bump-version.md`.
7. Move to the next point.

### Rifiuta

1. Update the project file: `Decisione` = `Scartato`, with the reason supplied by the user (or "scelta dell'autore" if none).
2. No file modifications.
3. Move on.

### Modifica

1. Ask the user: *"In che direzione devo modificare la proposta?"*
2. Regenerate the proposal in light of the new direction.
3. Return to step 3 of this workflow. After eventual `Accetta`, label the point as `Modificato` (not `Accettato`) — useful for the final scheda.

## 5. Edge cases

- **Multiple decisions in one user message** (e.g. *"Accetta tutti tranne il punto 3"*). Process them sequentially, applying the per-point logic above. Still no auto-commit.
- **Char overshoot after Accept.** Report and ask: *"Lo sforamento è ora +X. Preferisci procedere e gestirlo nello sweep finale, oppure cercare il taglio compensativo subito?"*
- **Bibliography conflict.** If the user wants a key that doesn't exist or has dubious metadata, defer to `40-bibliography-check.md` and don't apply until cleared.
- **Anglicismo non in whitelist** (`ARTICLE_LANG=it` only). Surface in the proposal block under "Eventuali deroghe" — the user decides whether to add to whitelist or rephrase.
- **Articolo intero scope.** The skill walks the article section by section; the user can pause at any moment with `pausa` or `stop`, and resume later from the same point.

## 6. State persistence

The accepted-since-bump counter and the per-point decision state live entirely inside the `progetto-revisione-vN.md` file. On every Accept/Reject/Modify, rewrite the relevant section of that file. This way, an interrupted session resumes cleanly: when the skill is re-invoked, it reads the project file and continues from the first point still in `Da decidere` state.
