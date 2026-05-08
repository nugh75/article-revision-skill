# Scheda revisione {{REVIEWER}} — stato v{{VERSION}}

- **Articolo**: `{{ARTICLE_PATH}}`
- **Conteggio attuale**: {{CURRENT_COUNT}} {{LIMIT_UNIT}} (limite {{EDITORIAL_LIMIT}} → **sforamento {{OVERSHOOT}}**)
- **Data scheda**: {{DATE}}
- **Versione precedente**: v{{PREV_VERSION}} ({{PREV_COUNT}} {{LIMIT_UNIT}})

---

## Sintesi

| # | Punto reviewer | Sezione | Stato | Decisione |
|---|---|---|---|---|
<!-- una riga per punto -->

**Esito complessivo**: {{ESITO_GLOBALE}}

---

## Dettaglio per punto

<!--
Per ogni punto, una sezione:

### {{N}} — {{TITOLO}}

**Osservazione del reviewer**: {{CITAZIONE}}

**Stato attuale (v{{VERSION}}, riga {{LINEA}})**:

> {{TESTO_ATTUALE}}

**Verdetto**: {{ESITO_PUNTUALE}}

**Modifica applicata** (commit `{{COMMIT_HASH}}`):
- {{DESCRIZIONE_BREVE_DELLA_MODIFICA}}

---
-->

## Vincolo caratteri/parole — recuperi pendenti

| # | Sezione | Cosa togliere | Recupero stimato |
|---|---|---|---|
<!-- candidati da `scripts/char_count.py --suggest-cuts` -->

---

## Punti residui prima del *submit*

- [ ] {{TASK_1}}
- [ ] {{TASK_2}}

---

## Cronologia interventi

<!-- riassunto generato dai commit `revision(...)` -->
