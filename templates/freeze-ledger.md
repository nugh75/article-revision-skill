---
article: {{ARTICLE_PATH}}
reconciled-version: {{BUMPED_VERSION}}
updated: {{TIMESTAMP}}
---

# Freeze Ledger — {{ARTICLE_SLUG}}

Persistent, article-level map of which parts are **concluded** (frozen) and
which still **need work** (open). It survives version bumps and sessions —
unlike the per-session task file. One row per tracked unit.

**Legenda stato:**

- 🟢 `frozen` — concluso e approvato. La skill avvisa prima di toccarlo e chiede conferma (advisory). Per modificarlo liberamente: `/r-thaw`.
- 🟡 `open` — richiede intervento. La colonna *Commenti / intenzioni* dice cosa si intende cambiare.
- 🔵 `wip` — in lavorazione in questa sessione.
- ⚪ unità non elencata = mai esaminata (untracked).
- 🔒 `frozen` (passaggio) — vincolante, non advisory: il testo esatto elencato in
  *Passaggi congelati* non si tocca. Per modificarlo serve `/r-thaw F<n>`.
  Un passaggio 🔒 dentro una sezione 🟡 `open` resta intoccabile: la revisione
  della sezione lo aggira.

**Ancoraggio:** ogni unità è identificata da capitolo + sezione + numero di
paragrafo + righe correnti + *incipit* (primi ~40 caratteri verbatim del
paragrafo), **non** dal numero di riga da solo: gli incipit sopravvivono a
modifiche e bump. Le righe sono obbligatorie ma indicative.

---

## Mappa stato

| Unità | Capitolo | Sezione | Righe | Incipit (ancora) | Stato | Ultima modifica | Commenti / intenzioni |
|---|---|---|---|---|---|---|---|
<!-- una riga per unità tracciata, es.:
| P4 | Capitolo 3 — Metodo | §3.1 Campione | <ARTICLE_PATH>:145-153 | «Il campione è composto da 124…» | 🟢 frozen | 2026-06-18 1530 | — |
| P5 | Capitolo 3 — Metodo | §3.1 Campione | <ARTICLE_PATH>:154-162 | «Le risposte sono state codificate…» | 🟡 open | 2026-06-18 1532 | Verificare denominatore della percentuale; citazione mancante per il codebook |
-->

---

## Passaggi congelati

Grana fine: uno *span* di testo continuo di qualunque lunghezza — mezza frase,
una frase, tre frasi — che non deve cambiare. La tabella tiene stato e metadati;
il blocco sotto tiene il **testo verbatim**, byte per byte, in un fence `text`.
`scripts/freeze_check.py <articolo>` verifica che ogni passaggio 🔒 esista
ancora identico e riporta righe aggiornate, `stale` e `ambiguo`.

Il confronto è normalizzato (NFC, whitespace collassato): un passaggio
sopravvive a riavvolgimento delle righe e a un bump di versione, e risulta
`stale` solo se le parole cambiano.

| ID | Sezione | Righe | Incipit | sha256 | Stato | Data |
|---|---|---|---|---|---|---|
<!-- una riga per passaggio, es.:
| F7 | §2.2.4 | <ARTICLE_PATH>:224-224 | «La teoria della diffusione…» | a91f3c7d4e21 | 🔒 frozen | 2026-06-18 1530 |
-->

<!-- un blocco per passaggio, con il testo esatto; es.:

### F7 — §2.2.4 — 🔒 frozen — 2026-06-18
- **Motivo:** dato verificato con l'autore; formulazione concordata.

```text
La teoria della diffusione delle innovazioni colloca l'adozione su cinque categorie.
```
-->

---

## Note per unità aperte

<!--
Per ogni unità 🟡 open con un'intenzione articolata, un blocco di dettaglio.
Tieni qui ciò che durante l'iterazione si è deciso di cambiare ma non ancora
applicato, così è sempre sotto mano.

### P5 — Capitolo 3 — Metodo — <ARTICLE_PATH>:154-162
- **Intenzione:** ricalcolare la percentuale di adesione (denominatore = rispondenti effettivi, non invitati).
- **Origine:** commento sessione 2026-06-18, punto Reviewer A-3.
- **Bloccato da:** `51-data-verification.md` (dato da ri-derivare).
-->

---

## Storico freeze / thaw

| Data | Azione | Unità | Da → A | Origine |
|---|---|---|---|---|
<!-- una riga per ogni freeze/thaw, es.:
| 2026-06-18 1530 | freeze | P4 Capitolo 3 <ARTICLE_PATH>:145-153 | open → frozen | auto-offer fine paragrafo |
| 2026-06-18 1601 | thaw | P4 Capitolo 3 <ARTICLE_PATH>:145-153 | frozen → open | richiesta utente /r-thaw |
-->
