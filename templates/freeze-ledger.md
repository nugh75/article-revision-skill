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

**Ancoraggio:** ogni unità è identificata da sezione + numero di paragrafo +
*incipit* (primi ~40 caratteri verbatim del paragrafo), **non** dal numero di
riga: gli incipit sopravvivono a modifiche e bump. Le righe sono indicative.

---

## Mappa stato

| Unità | Sezione | Incipit (ancora) | Stato | Ultima modifica | Commenti / intenzioni |
|---|---|---|---|---|---|
<!-- una riga per unità tracciata, es.:
| P4 | §3 Metodo | «Il campione è composto da 124…» | 🟢 frozen | 2026-06-18 1530 | — |
| P5 | §3 Metodo | «Le risposte sono state codificate…» | 🟡 open | 2026-06-18 1532 | Verificare denominatore della percentuale; citazione mancante per il codebook |
-->

---

## Note per unità aperte

<!--
Per ogni unità 🟡 open con un'intenzione articolata, un blocco di dettaglio.
Tieni qui ciò che durante l'iterazione si è deciso di cambiare ma non ancora
applicato, così è sempre sotto mano.

### P5 — §3 Metodo
- **Intenzione:** ricalcolare la percentuale di adesione (denominatore = rispondenti effettivi, non invitati).
- **Origine:** commento sessione 2026-06-18, punto Reviewer A-3.
- **Bloccato da:** `51-data-verification.md` (dato da ri-derivare).
-->

---

## Storico freeze / thaw

| Data | Azione | Unità | Da → A | Origine |
|---|---|---|---|---|
<!-- una riga per ogni freeze/thaw, es.:
| 2026-06-18 1530 | freeze | P4 §3 | open → frozen | auto-offer fine paragrafo |
| 2026-06-18 1601 | thaw | P4 §3 | frozen → open | richiesta utente /r-thaw |
-->
