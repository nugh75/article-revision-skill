# 31 — Paragraph-by-Paragraph Revision

Triggered by `/r-pp` (standard) or `/r-pp-a` (deep). Performs a proactive diagnostic walk over every paragraph of the article, asking the user structured questions before proposing modifications. Every paragraph must be checked for a single governing concept and identified by chapter plus Markdown line range; at the end of each chapter, run a recap on clarity, coherence, organization, and paragraph progression before advancing.

## 0. Determine Mode

| Command | Mode | Diagnostic depth |
|---|---|---|
| `/r-pp` | Standard | 4 questions per paragraph |
| `/r-pp-a` | Deep (`--approfondita`) | 6 questions per paragraph |

If the user invokes by phrase (e.g. "revisione paragrafo per paragrafo") without a slash command, ask which mode they want.

## 1. Bootstrap & Setup

If not already done, run `00-bootstrap.md` and `10-setup.md` to load `.env`, norms, bibliography, active article, and detect `ARTICLE_LANG`. **Note:** `10-setup.md` step 5 enforces a mandatory version bump before any revision work begins — do not skip it.

## 1a. Load Optional Global Trace

Before parsing paragraphs, look for global trace files produced by
`workflow/34-global-revision.md`:

```
revisions/<article-slug>/sources/global-trace-*.md
```

If one or more files exist:

1. Prefer the newest trace whose frontmatter has `status: active`.
2. If no active trace is marked, prefer the newest `global-trace-*.md`.
3. Load the trace as **diagnostic context only**. It must not force edits and
   never bypasses the decision loop.
4. If the trace was created for an older article version, warn:

   ```
   ⚠ Traccia globale da versione precedente: <trace-version>. La uso come orientamento, non come vincolo rigido.
   ```

5. Announce:

   ```
   Traccia globale caricata: <path>
   Uso la traccia per mantenere visione d'insieme durante la revisione paragrafo per paragrafo.
   ```

If multiple traces are equally plausible, ask the user to choose one or continue
without trace. If the user says `senza traccia`, continue normally and record
`GLOBAL_TRACE_PATH=none` for the session.

When a trace is loaded, use it to check whether each paragraph supports the
global function of its section, respects the priorities identified by
`/r-global`, and avoids global issues already flagged there (e.g. redundancy,
logical gaps, terminology drift, proportional imbalance). Summarize only the
relevant trace point for the current paragraph; do not paste the full trace into
every diagnostic block.

## 2. Parse Article Into Paragraphs

1. Read the full article (skip YAML frontmatter).
2. Split into semantic paragraphs:
   - A paragraph is a block of text delimited by blank lines.
   - **Skip** headings (lines starting with `#`), blockquotes, code blocks, tables.
   - **Do not** split numbered list items — treat each item as a paragraph.
3. Number paragraphs sequentially: `P1`, `P2`, ..., `PN`.
4. Record the inclusive Markdown line range for each paragraph:
   `P<N> — <ARTICLE_PATH>:<L1-L2>`.
5. Map each paragraph to a chapter and, separately, to its nearest section:
   - A chapter is a numbered heading with a number and a title. Use the first
     numeric component of the heading text: `1`, `1.1`, and `1.2.3` all belong
     to `Capitolo 1`; `2` starts `Capitolo 2`.
   - When the first number changes, the chapter changes.
   - Use the first heading encountered for that first number as the chapter
     title; keep the nearest full heading path as section/subsection context.
   - If headings are unnumbered or inconsistent, warn and use the nearest
     heading as provisional context; still include line ranges.
   - If the article has no headings, treat the whole article as one provisional
     chapter and run the recap only before closure.
6. For every paragraph, carry this locator in memory and in task/handoff/ledger
   entries:
   `Capitolo <C> — <chapter-title>; Paragrafo P<N> — <ARTICLE_PATH>:<L1-L2>`.
7. Announce in chat:

   ```
   Articolo: <article-path>
   Paragrafi individuati: N
   Capitoli individuati: C
   Sezioni/sottosezioni individuate: S
   Traccia globale: <none|GLOBAL_TRACE_PATH>
   Modalità: <standard|approfondita>
   Lingua rilevata: <ARTICLE_LANG>

   Inizio da P1 (<ARTICLE_PATH>:<L1-L2>, Capitolo <C>)? (sì / scegli paragrafo / annulla)
   ```

   Wait for the user.

## 3. Diagnostic Interview Per Paragraph

Before presenting each paragraph, run the freeze check (`15-freeze-ledger.md`
§4). If the paragraph is 🟢 `frozen`, prepend the advisory note and ask whether
to revisit it before running diagnostics:

```
Capitolo <C> — <chapter-title>; P<N> (<ARTICLE_PATH>:<L1-L2>) è CONGELATO (frozen il <data>) — considerato concluso.
Lo rivediamo lo stesso? (sì, procedi / lascia congelato e prossimo)
```

`lascia congelato` → skip to the next paragraph. `sì, procedi` → set 🔵 `wip` and
continue. If the row carries an intention (🟡 `open`), fold it into the diagnosis.

For each paragraph, present it in context and ask the diagnostic questions. **Wait for answers before proposing.**

### Paragraph Unity Requirement

Before asking diagnostic questions, identify the paragraph's **concetto unitario** in one sentence.

A paragraph is unitary when it expresses one governing idea or concept, even if that idea is then developed in two or more coordinated parts (e.g. definition + consequence, claim + evidence, premise + implication). It is not unitary when it contains two or more autonomous ideas that could stand as separate paragraphs.

If no unitary concept can be identified, flag the paragraph as structurally weak and propose one of these remedies:

- split the paragraph into two or more paragraphs;
- move one autonomous idea to a better section;
- narrow the paragraph so all sentences serve the same governing concept.

### Output Format (Standard — `/r-pp`)

```
## Capitolo <C> — <chapter-title> · Paragrafo P<N> · <ARTICLE_PATH>:<L1-L2>

**Sezione/sottosezione:** §<section-path>

**Contesto** (paragrafo precedente):
> <preceding paragraph, truncated to 200 chars if long>

**Traccia globale rilevante:**
> <section-level or article-level guidance from GLOBAL_TRACE_PATH, or "Nessuna traccia globale caricata">

**Paragrafo corrente:**
> <current paragraph verbatim>

**Ipotesi di concetto unitario:**
> <one governing idea/concept that the paragraph should express>

**Domande:**
1. Il paragrafo esprime un concetto unitario, cioè un'unica idea declinata in parti coerenti, o contiene più idee autonome?
2. L'argomento è chiaro e completo?
3. Il paragrafo si collega bene al precedente?
4. Ci sono problemi di stile, registro o citazioni?

Rispondi punto per punto (es. "1. sì, ma il concetto va formulato meglio; 2. sì; 3. no: il collegamento è forzato; 4. citazione mancante in riga X").
```

Adapt to English if `ARTICLE_LANG=en`:

```
**Questions:**
1. Does the paragraph express one governing concept, developed in coherent parts, or does it contain multiple autonomous ideas?
2. Is the argument clear and complete?
3. Does it connect well to the previous paragraph?
4. Any issues with style, register, or citations?
```

### Output Format (Deep — `/r-pp-a`)

```
## Capitolo <C> — <chapter-title> · Paragrafo P<N> · <ARTICLE_PATH>:<L1-L2>

**Sezione/sottosezione:** §<section-path>

**Contesto** (paragrafo precedente):
> <preceding paragraph, truncated to 200 chars if long>

**Traccia globale rilevante:**
> <section-level or article-level guidance from GLOBAL_TRACE_PATH, or "Nessuna traccia globale caricata">

**Paragrafo corrente:**
> <current paragraph verbatim>

**Ipotesi di concetto unitario:**
> <one governing idea/concept that the paragraph should express>

**Domande approfondite:**
1. [Unità] Il paragrafo ha un solo concetto guida, anche se articolato in più parti, o fonde idee autonome?
2. [Logica] L'argomento è logicamente completo? Mancano passaggi intermedi?
3. [Struttura] La struttura interna funziona? (topic sentence, sviluppo, chiusura)
4. [Tono] Il tono e il registro sono appropriati alla rivista?
5. [Citazioni] Ogni affermazione è supportata? Le citazioni sono formattate correttamente?
6. [Norme] Il paragrafo rispetta le norme editoriali? (limiti, stile, terminologia)

Rispondi per categoria (es. "unità: due idee da separare; logica: manca un passaggio tra X e Y; struttura: ok; tono: troppo informale in riga 3; citazioni: ok; norme: ok").
```

## 4. Propose Modifications

Based on the user's diagnostic answers, generate a proposal using the standard decision pattern from `30-iterate-points.md`, section 3:

```
## Point <N> — P<N> revision · scope: paragraph · mode: <standard|deep>

**Unità**: Capitolo <C> — <chapter-title>; Paragrafo P<N> — <ARTICLE_PATH>:<L1-L2>

**Original** (`<article>:<line-range>`)
> <verbatim text>

**Concetto unitario:**
> <the governing concept after diagnosis, or "non unitario" if the proposal splits/reorganizes it>

**Vincolo dalla traccia globale:**
> <relevant global orientation, or "nessuno">

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

**Decisione sulla proposta?**
- `Accetta` — applica la proposta così com'è.
- `Modifica <N>: <direzione>` — mantieni l'idea, ma cambia la modifica indicata.
- `Rivedi completamente: <direzione>` — rigenera la proposta da capo.
- `Tieni in considerazione: <nota>` — non applicare ora; registra come promemoria/traccia.

Puoi indicare numeri specifici, es. `Accetta 2,4` oppure `Modifica 3: sostituire X con Y`.
```

If a proposal requires splitting a paragraph, show the exact resulting paragraphs under `**Proposta**`, mark `risk: medium` or `high` depending on content movement, and keep each split/move as a separate numbered modification.

### Deep mode numbering (`/r-pp-a`)

In deep mode, prefix each modification with its diagnostic category:

```
**Modifiche:**
1. [unità] <old> → <new> [(motivazione)]
2. [logica] <old> → <new> [(motivazione)]
3. [struttura] <old> → <new> [(motivazione)]
4. [tono] <old> → <new> [(motivazione)]
...
```

The user may decide by category: `Accetta logica`, `Modifica tono: <direzione>`,
`Tieni in considerazione citazioni: <nota>`, etc. Shortcuts remain optional:
`A = Accetta`, `M = Modifica`, `R = Rivedi completamente`, `T = Tieni in considerazione`.

## 5. Handle Responses

Follow the standard response handling from `30-iterate-points.md`, section 4:

- **Accetta** → edit file, increment counter, ask "Ci sono altri cambiamenti in questo paragrafo?".
- **Modifica** → regenerate modification N per direction.
- **Rivedi completamente** → regenerate the full proposal from the original paragraph.
- **Tieni in considerazione** → record the note as deferred/context; no file edits.

**Do not advance automatically.** Wait for explicit command: `prossimo`, `next`, `passa al prossimo paragrafo`.

**On the advance command, run the freeze auto-offer** (`15-freeze-ledger.md` §7)
before moving to the next paragraph: offer to freeze the just-finished paragraph
(`Congelo P<N> (<ARTICLE_PATH>:<L1-L2>, Capitolo <C>) come concluso? (sì / no / più tardi)`). If the user declines but
named something still to do, record it via `log-comment` so the paragraph stays
🟡 `open` with its intention in the ledger.

If the next paragraph belongs to a new chapter, run the chapter recap
(section 6) before moving on.

## 6. Chapter Recap

Run this step after the last paragraph of each chapter has been handled
and before presenting the first paragraph of the next chapter. Also run
it for the final chapter before the revision closure summary.

The recap is diagnostic first: do not edit automatically. If the recap identifies
fixes, propose them as normal decision points, split by issue type (e.g. one point
for a transition, one point for a paragraph split, one point for section order).

### Output Format

```
## Recap capitolo — Capitolo <C> — <chapter-title>

**Paragrafi coperti:** P<X> (<ARTICLE_PATH>:<Lx1-Lx2>) – P<Y> (<ARTICLE_PATH>:<Ly1-Ly2>)

**Mappa dei concetti unitari:**
- P<X> (<Lx1-Lx2>): <concept>
- P<Y> (<Ly1-Ly2>): <concept>

**Confronto con traccia globale:**
- <how this chapter aligns or conflicts with the loaded global trace>

**Chiarezza e coerenza:**
- Tesi/funzione del capitolo: <clear|partly clear|unclear> — <reason>
- Progressione tra paragrafi: <linear|has gaps|has redundancies> — <reason>
- Transizioni interne: <adequate|weak|missing> — <reason>
- Ridondanze o salti logici: <none|list>

**Esito:**
- <chapter is organized clearly and coherently | issues to address before moving on>

**Prossimo passo:** procedo al prossimo capitolo? (sì / rivedi P<N> / proponi correzione / congela capitolo / chiudi)
```

Criteria:

- The chapter should have a clear internal function in the article.
- Paragraphs should progress in a recognizable order, not merely accumulate.
- Each paragraph's unitary concept should be distinct from adjacent paragraphs.
- If two adjacent paragraphs share the same concept, propose merging or sharpening
  their functions.
- If one paragraph carries two autonomous concepts, return to that paragraph and
  propose a split before advancing.
- If the user names a deferred issue but does not apply it immediately, record it
  in the freeze ledger with `log-comment` for the relevant paragraph or chapter.

## 7. Edge Cases

- **Skip paragraph.** If the user says `salta` or `skip`, mark the paragraph as `Skipped` and advance.
- **Handoff / pause.** If the user says `pause`, `stop`, `sospendi`,
  `interrompi`, or `/r-handoff`, call `workflow/06-handoff.md`: record the
  current paragraph with full chapter + line-range locator, chapter recap
  status, active global trace, pending proposal, and exact next action. Do not
  run closure or sync.
- **Go back.** `torna a P<N>` — jump to a specific paragraph and re-run diagnostics.
- **Empty paragraph.** If a paragraph is truly empty or contains only whitespace, skip it silently (do not number it).
- **Very long paragraph.** If a paragraph exceeds ~2000 chars, warn: *"Questo paragrafo è molto lungo (X caratteri). Vuoi trattarlo come unico o suddividerlo?"*
- **Bibliography check.** If citations are touched, run `40-bibliography-check.md` before applying.
- **Character budget.** After each accepted change, check against `EDITORIAL_LIMIT_CHARS`. If over, warn immediately (see `30-iterate-points.md`, edge case "Character overshoot").

## 8. Revision Closure

**Trigger — either of:**

1. **Perimetro naturale esaurito**: l'ultimo paragrafo dell'articolo è stato processato.
2. **Chiusura esplicita**: l'utente invia una frase di chiusura —
   IT: `chiudi`, `fine`, `ho finito`, `concludi`, `basta così`, `chiudiamo` /
   EN: `close`, `done`, `finish`, `end`, `I'm done`.

**Sequenza obbligatoria:**

1. Presentare il riepilogo:

   ```
   Revisione paragrafo per paragrafo completata.
   Paragrafi processati: N  |  Accettati: A  |  Rivisti: R  |  Da considerare: T  |  Saltati: S
   Capitoli/sezioni riepilogati: C
   Bilancio caratteri: +Δ (limite: EDITORIAL_LIMIT_CHARS)
   Versione articolo attiva: <path>
   ```

2. Chiedere conferma:

   ```
   Procedo con la chiusura?
     1. Final sheet (/r-sheet)  — facoltativo
     2. Decision log            — obbligatorio
     3. Sync current files      — obbligatorio
   (sì / sì senza final sheet / annulla)
   ```

3. Su conferma:
   - Se richiesto: `workflow/70-final-sheet.md`
   - `workflow/95-decision-log.md`  ← chiude il task file e sincronizza i file correnti
