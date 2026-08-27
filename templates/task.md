---
command: {{COMMAND}}
article: {{ARTICLE_PATH}}
version: {{ARTICLE_VERSION}}
bumped-version: {{BUMPED_VERSION}}
lane: {{REVIEWER_LANE}}
started: {{TIMESTAMP}}
status: in-progress
git-checkpoint-threshold: {{AUTO_GIT_CHECKPOINT_THRESHOLD}}
changes-since-git-checkpoint: 0
git-checkpoint-last-prompt-count: 0
git-checkpoint-sequence: 0
---

# Task — {{COMMAND}} · {{ARTICLE_SLUG}}

- **Articolo**: `{{ARTICLE_PATH}}`
- **Versione originale**: `{{ARTICLE_VERSION}}`
- **Versione di lavoro**: `{{BUMPED_VERSION}}`
- **Comando**: `{{COMMAND}}`
- **Lane**: `{{REVIEWER_LANE}}`
- **Avvio sessione**: `{{TIMESTAMP}}`
- **Stato**: `in-progress`
- **Avviso checkpoint Git**: ogni `{{AUTO_GIT_CHECKPOINT_THRESHOLD}}` modifiche applicate; commit e push richiedono autorizzazione Git separata

## Passi

| # | Passo | Stato | Note |
|---|---|---|---|
| 1 | Bootstrap & Setup | `done` | |
| 2 | Version bump | `done` | {{ARTICLE_VERSION}} → {{BUMPED_VERSION}} |
{{STEPS_ROWS}}

## Riepilogo

- **Accettati**: —
- **Da considerare**: —
- **Modificati**: —
- **Rinviati**: —
- **Checkpoint Git pubblicati**: —

## Handoff / Ripresa

- **Ultimo aggiornamento**: —
- **Stato**: in-progress
- **Comando**: `{{COMMAND}}`
- **Articolo di lavoro**: `{{ARTICLE_PATH}}`
- **Versione di lavoro**: `{{BUMPED_VERSION}}`
- **Fase corrente**: —
- **Unità corrente**: — <!-- if paragraph: Capitolo C — title; P<N> — ARTICLE_PATH:L1-L2 -->
- **Ultima proposta mostrata**: —
- **Decisioni già prese**: —
- **Decisioni pendenti**: —
- **Tracce/fonti da ricaricare**: —
- **File modificati finora**: —
- **Prossima azione esatta**: —
- **Avvertenze**: —

## Stato articolo alla chiusura

- **Versione finale**: —
- **Caratteri**: — / — limite
- **Decision log**: —
