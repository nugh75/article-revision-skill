# Progetto revisione {{REVIEWER}} — v{{VERSION}}

## Stato sintetico

- **Articolo di riferimento**: `{{ARTICLE_PATH}}`
- **Reviewer**: {{REVIEWER}}
- **Vincolo editoriale**: max {{EDITORIAL_LIMIT}} {{LIMIT_UNIT}}
- **Conteggio iniziale articolo**: {{INITIAL_COUNT}} {{LIMIT_UNIT}}
- **Lingua articolo (auto)**: {{ARTICLE_LANG}}
- **Norme redazionali**: `{{NORMS_PATH}}`
- **Stato del documento**: progetto di revisione, **non** applicazione delle modifiche

## Metodo di lavoro

Ogni rilievo del reviewer è valutato separatamente. Per ciascun punto:

1. La skill `article-revision` mostra in chat il testo originale e la proposta di modifica.
2. L'utente decide: `Accetta` / `Rifiuta` / `Modifica`.
3. Su `Accetta`: la modifica è applicata al file articolo e committata in git.
4. Su `Rifiuta`: il punto resta nel progetto con motivazione, nessun commit.
5. Su `Modifica`: la skill rigenera la proposta secondo l'indicazione dell'utente e ripete dal passo 1.

Stati decisionali ammessi:

- `Da decidere`
- `Accettato`
- `Modificato` (proposta riformulata e poi accettata)
- `Scartato`
- `Rimandato` (richiede dato esterno o decisione successiva)

## Revisione punto per punto

<!--
  Per ogni rilievo del reviewer, la skill aggiunge una sottosezione qui.
  Schema:

### {{N}}. {{TITOLO_PUNTO}} — {{SEZIONE_ARTICOLO}}

**Osservazione del reviewer**

> {{CITAZIONE_FEDELE}}

**Stato in v{{VERSION}}**

[Già coperto | Parzialmente coperto | Da integrare | Da verificare]

**Valutazione**

{{ANALISI_SINTETICA}}

**Proposta**

Originale (`{{FILE}}:{{LINEE}}`):
> {{TESTO_ORIGINALE}}

Modificato:
> {{TESTO_PROPOSTO}}

**Δ**: chars {{DELTA_CHARS}} · bibliografia {{DELTA_BIB}} · rischio {{RISCHIO}}

**Decisione**

[Da decidere | Accettato | Modificato | Scartato | Rimandato]

**Note**

{{CONTESTO_E_DIPENDENZE}}

---
-->

## Checklist decisionale

| # | Punto | Sezione | Stato in v{{VERSION}} | Priorità | Decisione |
|---|---|---|---|---|---|
<!-- una riga per punto, aggiornata a ogni decisione -->

## Verifiche prima di applicare le modifiche

- Conteggio caratteri/parole sotto il limite editoriale (`scripts/char_count.py`).
- Tono coerente con la skill di stile della rivista.
- Bibliografia: ogni nuova citazione esiste e ha *match* online (`scripts/bib_verify_online.py`).
- Le proposte testuali non introducono dati o inferenze quantitative non presenti nello studio.
- Anglicismi (se `ARTICLE_LANG=it`): ammessi solo quelli in `templates/anglicismi-accettati-it.md`.
