# 50 — Sample Description

Triggered when a methodology revision point asks to describe the sample with sociodemographic statistics and raw data is available in `data/`.

## 1. Identify Data Sources

Ask the user, or detect from `data/`:

- Which files contain the data (`*.xlsx`, `*.csv`)?
- Which sheets, if Excel?
- Which column holds the cohort indicator?
- Which columns hold age, gender, and any cohort-specific variable (school order, program area, etc.)?

## 2. Build YAML Mapping

Write `data/sample-mapping.yaml` or similar, following the schema in `scripts/sample_stats.py` docstring. Example:

```yaml
sources:
  - file: "Teachers - Questionnaire.xlsx"
    sheet: "Form responses 1"
    cohort_column: 3
    cohorts:
      "in-service":
        match: "I am currently teaching."
        label: "In-service teachers"
      "pre-service":
        match: "teacher education program"
        label: "Pre-service teachers"
    variables:
      age: 4
      gender: 5
      order: 7
```

Show the mapping to the user before running:

```text
Mapping built (`data/sample-mapping.yaml`):
- 2 sources
- 4 total cohorts
- variables: age, gender, school order

Proceed with the calculation? (yes / modify mapping)
```

## 3. Compute Stats

```bash
scripts/sample_stats.py data/sample-mapping.yaml --output revisions/<slug>/sample-stats.md
```

Open the output and present a one-shot summary in chat as a table.

## 4. Generate Methodology Paragraph

Convert the stats into prose suitable for the article, in `ARTICLE_LANG`. Use this skeleton for English:

```text
**<cohort>** (n=<N>; mean age <M> years, range <min>–<max>; F <F>%, M <M>%, other/nd <X>%) <qualitative description>. <internal distribution if relevant>.
```

For Italian articles, translate the prose to formal academic Italian while keeping the workflow labels in English.

## 5. Present As Normal Revision Point

Hand the proposal back to `30-iterate-points.md` in the standard `Original / Proposal / Decision` shape. The user accepts, rejects, or modifies as usual.

## 6. Notes

- Variables collected but not used as analytical variables in a qualitative design must be flagged in `ARTICLE_LANG`, for example: `Sociodemographic variables were not used as analytical variables in the qualitative design, but they support interpretation in the discussion.`
- Never invent statistics. If `n < 30` or `response rate < 90%` for a variable, make this explicit.
- If the user asks for a table instead of prose, use the format in `templates/sample-stats.md` directly.
