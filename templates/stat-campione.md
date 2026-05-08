# Statistiche campione — {{ARTICLE_PATH}}

- **Sorgenti dati**: {{DATA_SOURCES}}
- **Coorti**: {{COHORTS}}
- **Variabili raccolte**: {{VARIABLES}}
- **Generato da**: `scripts/sample_stats.py` con mappatura `{{MAPPING_FILE}}`

---

## Tabella riassuntiva

| Coorte | n | Età: media (range) | Genere F / M / altro-nd | Distribuzione interna |
|---|---|---|---|---|
<!-- una riga per coorte -->

---

## Per coorte

<!--
Per ogni coorte:

### {{COORTE}} (n={{N}})

- **Età**: media {{MEAN}} anni · range {{RANGE}} · mediana {{MEDIAN}}
- **Genere**: F {{F}}% · M {{M}}% · altro/nd {{ALTRO}}%
- **{{VARIABILE_TIPICA}}**: {{DETTAGLIO}}

-->

---

## Note metodologiche

- I conteggi e le percentuali si riferiscono ai rispondenti effettivi della coorte; quando la *response rate* di una variabile è < 90%, è segnalata in nota.
- Le variabili socio-demografiche non sono usate come variabili di analisi nel disegno qualitativo, ma orientano l'interpretazione in sede di discussione.
