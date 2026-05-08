# 50 — Sample description

Triggered when a revision point in the methodology asks to describe the sample with sociodemographic statistics, and raw data is available in `dati/`.

## 1. Identify data sources

Ask the user (or detect from `dati/`):

- Which files contain the data? (`*.xlsx`, `*.csv`)
- Which sheets, if Excel.
- Which column holds the cohort indicator.
- Which columns hold age, gender, and any cohort-specific variable (school order, program area, …).

## 2. Build the YAML mapping

Write `dati/sample-mapping.yaml` (or similar) following the schema in `scripts/sample_stats.py` docstring. Example:

```yaml
sources:
  - file: "Insegnati - Questionario.xlsx"
    sheet: "Risposte del modulo 1"
    cohort_column: 3
    cohorts:
      "in-service":
        match: "Attualmente insegno."
        label: "Insegnanti in servizio"
      "pre-service":
        match: "PEF"
        label: "Insegnanti in formazione"
    variables:
      age: 4
      gender: 5
      order: 7
```

Show the mapping to the user before running:

```
Mapping costruito (`dati/sample-mapping.yaml`):
- 2 sorgenti
- 4 coorti totali
- variabili: età, genere, ordine

Procedo con il calcolo? (sì / modifica mapping)
```

## 3. Compute stats

```
scripts/sample_stats.py dati/sample-mapping.yaml --output revisioni/<slug>/stat-campione.md
```

Open the output and present a one-shot summary in chat (table view).

## 4. Generate the methodology paragraph

Convert the stats into prose suitable for the article, in `ARTICLE_LANG`. Use this skeleton (it):

```
Gli **<coorte>** (n=<N>; età media <M> anni, range <min>–<max>; F <F>%, M <M>%, altro/nd <X>%) <descrizione qualitativa coorte>. <distribuzione interna se rilevante>.
```

Or (en):

```
**<cohort>** (n=<N>; mean age <M> years, range <min>–<max>; F <F>%, M <M>%, other/nd <X>%) <qualitative description>. <internal distribution if relevant>.
```

## 5. Present as a normal revision point

Hand the proposal back to `30-iterate-points.md` in the standard `Originale / Proposta / Decisione` shape. The user accepts, rejects or modifies as usual.

## 6. Notes

- Variables collected but not used as analytical variables in a qualitative design must be flagged: *"Le variabili socio-demografiche non sono state usate come variabili di analisi nel disegno qualitativo, ma orientano l'interpretazione in sede di discussione."* (it) — adjust phrasing in en.
- Never invent statistics. If `n < 30` or `response rate < 90%` for a variable, make this explicit.
- If the user asks for a table instead of prose, use the format in `templates/stat-campione.md` directly.
