# Audit bibliografia — v{{VERSION}}

- **Bibliografia**: `{{BIB_PATH}}`
- **Articolo**: `{{ARTICLE_PATH}}`
- **Data audit**: {{DATE}}
- **Strumenti**: Crossref, OpenAlex (vedi `.env` per user-agent)

---

## Sintesi

| Esito | N. voci |
|---|---|
| ✅ Verificate | {{COUNT_OK}} |
| ⚠️ Match parziale (rivedere) | {{COUNT_PARTIAL}} |
| ❌ Non trovate (rischio voce inesistente) | {{COUNT_MISSING}} |
| 🔍 Non controllate (skip) | {{COUNT_SKIPPED}} |

---

## Voci sospette

<!--
Per ciascuna voce con esito ⚠️ o ❌:

### {{BIB_KEY}}

- **Citata in**: `{{ARTICLE}}:{{LINE}}`
- **Metadata `.bib`**: {{TITLE}} — {{AUTHORS}} ({{YEAR}}) — {{PUBLISHER_OR_JOURNAL}}
- **Esito Crossref**: {{CROSSREF_RESULT}}
- **Esito OpenAlex**: {{OPENALEX_RESULT}}
- **Best match online**: {{BEST_MATCH}} (similarity: {{SCORE}})
- **Azione consigliata**: {{ACTION}}

---
-->

## Voci citate ma non presenti nel `.bib`

<!-- elenco generato da `scripts/bib_check.py` -->

## Voci nel `.bib` mai citate

<!-- elenco — informativo, non blocca -->

---

## Decisioni

<!--
Per ogni voce sospetta, decidi:
- mantieni invariata
- correggi metadata (vedi proposta)
- sostituisci con altra voce
- rimuovi voce e citazione

Le decisioni vengono applicate dal workflow `30-bibliography-check.md`.
-->
