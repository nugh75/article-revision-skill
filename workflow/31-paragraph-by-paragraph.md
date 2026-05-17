# 31 — Paragraph-by-Paragraph Revision

Triggered by `/r-pp` (standard) or `/r-pp-a` (deep). Performs a proactive diagnostic walk over every paragraph of the article, asking the user structured questions before proposing modifications.

## 0. Determine Mode

| Command | Mode | Diagnostic depth |
|---|---|---|
| `/r-pp` | Standard | 3 questions per paragraph |
| `/r-pp-a` | Deep (`--approfondita`) | 5 questions per paragraph |

If the user invokes by phrase (e.g. "revisione paragrafo per paragrafo") without a slash command, ask which mode they want.

## 1. Bootstrap & Setup

If not already done, run `00-bootstrap.md` and `10-setup.md` to load `.env`, norms, bibliography, active article, and detect `ARTICLE_LANG`. **Note:** `10-setup.md` step 5 enforces a mandatory version bump before any revision work begins — do not skip it.

## 2. Parse Article Into Paragraphs

1. Read the full article (skip YAML frontmatter).
2. Split into semantic paragraphs:
   - A paragraph is a block of text delimited by blank lines.
   - **Skip** headings (lines starting with `#`), blockquotes, code blocks, tables.
   - **Do not** split numbered list items — treat each item as a paragraph.
3. Number paragraphs sequentially: `P1`, `P2`, ..., `PN`.
4. Announce in chat:

   ```
   Articolo: <article-path>
   Paragrafi individuati: N
   Modalità: <standard|approfondita>
   Lingua rilevata: <ARTICLE_LANG>

   Inizio da P1? (sì / scegli paragrafo / annulla)
   ```

   Wait for the user.

## 3. Diagnostic Interview Per Paragraph

For each paragraph, present it in context and ask the diagnostic questions. **Wait for answers before proposing.**

### Output Format (Standard — `/r-pp`)

```
## P<N> — §<section-name> · righe <L1-L2>

**Contesto** (paragrafo precedente):
> <preceding paragraph, truncated to 200 chars if long>

**Paragrafo corrente:**
> <current paragraph verbatim>

**Domande:**
1. L'argomento è chiaro e completo?
2. Il paragrafo si collega bene al precedente?
3. Ci sono problemi di stile, registro o citazioni?

Rispondi punto per punto (es. "1. sì, 2. no: il collegamento è forzato, 3. citazione mancante in riga X").
```

Adapt to English if `ARTICLE_LANG=en`:

```
**Questions:**
1. Is the argument clear and complete?
2. Does it connect well to the previous paragraph?
3. Any issues with style, register, or citations?
```

### Output Format (Deep — `/r-pp-a`)

```
## P<N> — §<section-name> · righe <L1-L2>

**Contesto** (paragrafo precedente):
> <preceding paragraph, truncated to 200 chars if long>

**Paragrafo corrente:**
> <current paragraph verbatim>

**Domande approfondite:**
1. [Logica] L'argomento è logicamente completo? Mancano passaggi intermedi?
2. [Struttura] La struttura interna funziona? (topic sentence, sviluppo, chiusura)
3. [Tono] Il tono e il registro sono appropriati alla rivista?
4. [Citazioni] Ogni affermazione è supportata? Le citazioni sono formattate correttamente?
5. [Norme] Il paragrafo rispetta le norme editoriali? (limiti, stile, terminologia)

Rispondi per categoria (es. "logica: manca un passaggio tra X e Y; struttura: ok; tono: troppo informale in riga 3; citazioni: ok; norme: ok").
```

## 4. Propose Modifications

Based on the user's diagnostic answers, generate a proposal using the standard A/R/M pattern from `30-iterate-points.md`, section 3:

```
## Point <N> — P<N> revision · scope: paragraph · mode: <standard|deep>

**Original** (`<article>:<line-range>`)
> <verbatim text>

**Diagnosi:**
- <summary of user's answers>

**Proposta**
> <proposed full text>

**Modifiche:**
1. <old> → <new> [(motivazione)]
2. <old> → <new> [(motivazione)]
...

**Δ**: chars <signed> / words <signed> · risk: <low|medium|high>

**Norms respected**: <list>
**Possible exceptions**: <list, with reason>

**A/R/M?** (indicare i numeri delle modifiche, es. "A 2,4" oppure "M 3: sostituire X con Y")
```

### Deep mode numbering (`/r-pp-a`)

In deep mode, prefix each modification with its diagnostic category:

```
**Modifiche:**
1. [logica] <old> → <new> [(motivazione)]
2. [struttura] <old> → <new> [(motivazione)]
3. [tono] <old> → <new> [(motivazione)]
...
```

The user may accept/reject by category: `A logica`, `R tono`, etc.

## 5. Handle Responses

Follow the standard response handling from `30-iterate-points.md`, section 4:

- **Accept** → edit file, increment counter, ask "Ci sono altri cambiamenti in questo paragrafo?".
- **Reject** → annotate, ask if more changes.
- **Reject entire point** → advance to next paragraph.
- **Modify** → regenerate modification N per direction.

**Do not advance automatically.** Wait for explicit command: `prossimo`, `next`, `passa al prossimo paragrafo`.

## 6. Edge Cases

- **Skip paragraph.** If the user says `salta` or `skip`, mark the paragraph as `Skipped` and advance.
- **Pause.** `pause` — record the current paragraph index. On next invocation, resume from that paragraph.
- **Go back.** `torna a P<N>` — jump to a specific paragraph and re-run diagnostics.
- **Empty paragraph.** If a paragraph is truly empty or contains only whitespace, skip it silently (do not number it).
- **Very long paragraph.** If a paragraph exceeds ~2000 chars, warn: *"Questo paragrafo è molto lungo (X caratteri). Vuoi trattarlo come unico o suddividerlo?"*
- **Bibliography check.** If citations are touched, run `40-bibliography-check.md` before applying.
- **Character budget.** After each accepted change, check against `EDITORIAL_LIMIT_CHARS`. If over, warn immediately (see `30-iterate-points.md`, edge case "Character overshoot").

## 7. Completion

When all paragraphs have been processed, output:

```
Revisione paragrafo per paragrafo completata.
Paragrafi processati: N
Modifiche accettate: X
Modifiche respinte: Y
Paragrafi saltati: Z
Bilancio caratteri: +Δ (limite: EDITORIAL_LIMIT_CHARS)

Vuoi generare il final sheet? (/r-sheet)
Vuoi fare il bump di versione? (/r-bump)
```

Wait for the user. Do not auto-advance.
