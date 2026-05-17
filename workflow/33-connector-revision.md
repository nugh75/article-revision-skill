# 33 — Connector Revision

Triggered by `/r-conn`. A focused, non-content pass that examines the article's logical scaffolding: connectors, transition phrases, and signposting language. This mode does **not** rewrite content — it only adjusts the connective tissue.

## 0. Entry Point

Invoked by `/r-conn` or phrases like:
- *"revisione connettori"*
- *"controlla le transizioni"*
- *"check the connectors"*
- *"polish transitions and signposting"*

## 1. Bootstrap & Setup

If not already done, run `00-bootstrap.md` and `10-setup.md` to load `.env`, norms, bibliography, active article, and detect `ARTICLE_LANG`. **Note:** `10-setup.md` step 5 enforces a mandatory version bump — do not skip it.

## 2. Parse Article Into Transitions

### 2a. Extract inter-paragraph transitions

For every consecutive pair of body paragraphs (P<N> → P<N+1>):
- Extract the **last sentence** of P<N>.
- Extract the **first sentence** of P<N+1>.
- Skip heading lines, blockquotes, code blocks, tables.
- Number the transition: `T<P<N>→P<N+1>>`.

### 2b. Extract inter-section transitions

For every consecutive section boundary (§<N> → §<N+1>):
- Extract the **last paragraph** of §<N> (first 200 chars).
- Extract the **first paragraph** of §<N+1> (first 200 chars).

### 2c. Count connector frequency

Scan the full article for the connector word lists (see `SKILL.md` tables). Count occurrences of each connector. Flag any connector with count > 3 as potentially overused.

## 3. Load Connector Reference

Use the connector reference tables from `SKILL.md`:

- If `ARTICLE_LANG=it`: use the IT connector reference table.
- If `ARTICLE_LANG=en`: use the EN connector reference table.
- The tables define: logical relation → preferred connectors → weak/ambiguous forms to avoid.

## 4. Diagnose Each Transition

For each inter-paragraph transition (T<P<N>→P<N+1>>):

1. **Determine the logical relation** between the two paragraphs:
   - Cause/effect, contrast, addition, exemplification, reformulation, concession, sequence, summary, internal reference, or none (same topic continuation).

2. **Check the current connector** (if any) at the boundary:
   - Is a connector present? If not, would one help?
   - If present, is it appropriate for the logical relation?
   - Is it a preferred or weak form per the reference table?

3. **Classify:**

   | Class | Meaning |
   |---|---|
   | `OK` | Connector present and appropriate |
   | `MISSING` | No connector where one would improve clarity |
   | `WEAK` | Connector present but weak/ambiguous form |
   | `WRONG` | Connector present but wrong logical relation |

4. **Skip** transitions classified as `OK`. Only flag `MISSING`, `WEAK`, `WRONG`.

## 5. Diagnose Connector Overuse

For each connector with count > 3:

- List the paragraphs where it appears.
- Determine if replacements are possible without changing meaning.
- If a connector is the standard choice and has few alternatives (e.g. *tuttavia* appears 5 times but is the only natural contrast connector in those contexts), mark as `ACCEPTABLE` despite the count.
- Otherwise, mark as `OVERUSED`.

## 6. Present Diagnostic Table

Present findings as a single structured table — **not** one transition at a time. The user reviews the bird's-eye view before selecting which to fix.

```
## Diagnostic Connettori — <article>

### Transizioni inter-paragrafo

| Transizione | Relazione logica | Stato | Testo attuale | Proposta |
|---|---|---|---|---|
| P3→P4 | Contrasto | WEAK | «Ma d'altra parte...» | «Tuttavia...» |
| P7→P8 | Causa/effetto | MISSING | (nessun connettore) | «Di conseguenza, ...» |
| P12→P13 | Aggiunta | OK | «Inoltre...» | — |

### Transizioni inter-sezione

| Transizione | Relazione logica | Stato | Problema | Proposta |
|---|---|---|---|---|
| §2→§3 | Sequenza | MISSING | Cambio brusco di tema | Aggiungere frase-ponte: «Stabilite le premesse teoriche, passiamo ora al disegno empirico.» |
| §4→§5 | Riepilogo + anteprima | OK | — | — |

### Connettori sovrautilizzati

| Connettore | Occorrenze | Paragrafi | Raccomandazione |
|---|---|---|---|
| *tuttavia* | 7 | P2, P4, P5, P9, P11, P14, P18 | Ridurre a max 3; riformulare 4 |
| *inoltre* | 5 | P3, P7, P10, P15, P20 | Ridurre a max 2; usare *per di più*, *si aggiunga che* |

### Segnaletica interna

| Tipo | Riferimento | Problema | Proposta |
|---|---|---|---|
| Rinvio in avanti | «come vedremo più avanti» in P5 | Vago — quale sezione? | «come vedremo nel §4» |
| Rinvio all'indietro | «come detto sopra» in P22 | Vago | «come discusso nel §2» |
```

If `ARTICLE_LANG=en`, adapt labels: *Transizione* → *Transition*, *Relazione logica* → *Logical relation*, *Stato* → *Status*, etc.

## 7. Collect User Selection

After presenting the diagnostic table:

```
Diagnostica connettori completata.

Transizioni con problemi: N (inter-paragrafo) + M (inter-sezione)
Connettori sovrautilizzati: K
Problemi di segnaletica: J

Quali vuoi sistemare?
- "tutte" — applica tutte le proposte
- "transizioni" — solo le transizioni inter-paragrafo e inter-sezione
- "P3→P4, P7→P8" — transizioni specifiche
- "sovrautilizzati" — solo i connettori sovrautilizzati
- "segnaletica" — solo la segnaletica interna
- "nessuno" — salta questa modalità
```

Wait for the user. Do not apply pre-emptively.

## 8. Propose Modifications

For each selected item group, generate a proposal using the standard A/R/M pattern.

**For transitions** (one point per group of up to 5 transitions that share a type):

```
## Point <N> — Connettori: transizioni inter-paragrafo · scope: connector

**Diagnosi:** <N> transizioni con problemi (MISSING, WEAK, WRONG)

**Modifiche:**
1. [P3→P4] «Ma d'altra parte» → «Tuttavia» [(WEAK → contrasto)]
2. [P7→P8] (nessuno) → «Di conseguenza, » [(MISSING → causa/effetto)]
3. [P14→P15] «Quindi» → «Pertanto, » [(WEAK → causa/effetto)]
...

**Δ**: chars +X / words +Y · risk: low

**A/R/M?**
```

**For overused connectors** (one point per overused connector):

```
## Point <N> — Connettori: sovrautilizzo di "tuttavia" · scope: connector

**Diagnosi:** 7 occorrenze (P2, P4, P5, P9, P11, P14, P18). Si raccomanda di tenerne 3 e riformulare 4.

**Modifiche:**
1. [P4] «Tuttavia...» → «Ciononostante...» [(rimpiazzo)]
2. [P9] «Tuttavia...» → «Al contrario...» [(rimpiazzo)]
3. [P14] «Tuttavia...» → «Nondimeno...» [(rimpiazzo)]
4. [P18] «Tuttavia...» → riformulare la frase senza connettore [(ristrutturazione)]

**Δ**: chars ±X / words ±Y · risk: low

**A/R/M?**
```

## 9. Handle Responses

Follow standard `30-iterate-points.md`, section 4. After applying, ask: *"Ci sono altri connettori da sistemare?"* before advancing.

## 10. Edge Cases

- **Empty transitions.** If a paragraph has only one sentence, treat the entire paragraph as the transition element.
- **No issues found.** If all transitions are classified as `OK`, announce: *"Nessun problema di connettori rilevato. Tutte le transizioni sono appropriate."* and exit.
- **Section headings as connectors.** If a section heading already contains an explicit transition (e.g. «§3: From Theory to Method»), mark the inter-section transition as `OK` regardless of the paragraph content.
- **Bibliography check.** Not applicable — this mode does not touch citations.
- **Character budget.** Connector edits are minor. Warn only if adding signposting sentences causes significant change.

## 11. Completion

```
Revisione connettori completata.
Transizioni sistemate: N
Connettori riformulati: K
Segnaletica aggiornata: J
Modifiche accettate: X
Modifiche respinte: Y

Vuoi procedere con un'altra modalità? (/r-pp, /r-pr-2, /r-global)
Vuoi fare il bump di versione? (/r-bump)
```
