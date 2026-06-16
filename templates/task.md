---
command: {{COMMAND}}
article: {{ARTICLE_PATH}}
version: {{ARTICLE_VERSION}}
bumped-version: {{BUMPED_VERSION}}
lane: {{REVIEWER_LANE}}
started: {{TIMESTAMP}}
status: in-progress
---

# Task — {{COMMAND}} · {{ARTICLE_SLUG}}

- **Articolo**: `{{ARTICLE_PATH}}`
- **Versione originale**: `{{ARTICLE_VERSION}}`
- **Versione di lavoro**: `{{BUMPED_VERSION}}`
- **Comando**: `{{COMMAND}}`
- **Lane**: `{{REVIEWER_LANE}}`
- **Avvio sessione**: `{{TIMESTAMP}}`
- **Stato**: `in-progress`

## Passi

| # | Passo | Stato | Note |
|---|---|---|---|
| 1 | Bootstrap & Setup | `done` | |
| 2 | Version bump | `done` | {{ARTICLE_VERSION}} → {{BUMPED_VERSION}} |
{{STEPS_ROWS}}

## Riepilogo

- **Accettati**: —
- **Rifiutati**: —
- **Modificati**: —
- **Rinviati**: —

## Stato articolo alla chiusura

- **Versione finale**: —
- **Caratteri**: — / — limite
- **Decision log**: —
