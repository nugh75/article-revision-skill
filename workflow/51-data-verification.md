# 51 — Data Verification

Triggered whenever a revision proposal **adds, changes, or relies on a quantitative claim**: a percentage, a count, a mean, an index value, a correlation, a rank ("the highest/lowest dimension"), or any figure presented as an empirical result.

Rationale: numeric claims propagate silently across versions. A figure introduced in v1 can survive untouched to v9 even when it is an artefact (wrong filter, substring match, mislabeled denominator). Reviewers — simulated or real — rarely recompute; they trust the number. This step makes the number, not its inheritance, the source of truth.

**Binding rule:** never inherit a numeric claim from the previous article version, from a reviewer's letter, or from an earlier revision document. Re-derive it from the project's authoritative data source, or mark it `Deferred`.

## 1. Detect a Numeric Claim

A point requires verification if the original text or the proposed text contains any of:

- a percentage or proportion (`24,4%`, `one in six`);
- an absolute count presented as a finding (`82 activities`, `2.095 PTOF`);
- a mean, median, standard deviation, or index value;
- a correlation / effect size / p-value;
- a superlative or rank over data (`the most frequent`, `the lowest-scoring dimension`);
- a derived qualitative claim that only holds if a figure holds (`dominated by X`, `marginal`, `underrepresented`).

If none is present, skip this file and return to `30-iterate-points.md`.

## 2. Locate the Authoritative Source

In order of precedence:

1. `.env` keys `DATA_VERIFY_PATH` (root of the authoritative dataset/platform) and `DATA_VERIFY_NOTES` (free-text pointer: master file, key column, formula location).
2. A "data source" section in the project's `AGENTS.md` (or `CLAUDE.md`), if it documents where figures come from.
3. Otherwise, ask the user:

   > This point carries a numeric claim (`<quote the figure>`). Where is the authoritative data — a file, a script, a dashboard export? I will not inherit the number from the previous version.

Never substitute a plausible value, a value copied from a reviewer comment, or a value from an older revision document. Those are not sources.

## 3. Re-derive the Figure

- Read the raw data and recompute the statistic with an **explicit, stated criterion** (which column, which filter, which denominator, which population subset).
- Prefer structured fields over free-text keyword matching. If keyword matching is unavoidable, use word boundaries — a substring match silently inflates counts (e.g. `stem` inside `sistema`, `IA` inside `studoIA`). State the regex used.
- State the denominator explicitly and whether categories are mutually exclusive. "% of schools mentioning X" ≠ "% of mentions".
- If the figure is an automatic categorization built for this check (e.g. bucketing a noisy free-text field), label it as such — reproducible ≠ validated. It must be declared in the article's Method, not presented as a clean structured measure.

## 4. Compare and Classify

| Outcome | Meaning | Action |
|---|---|---|
| **Confirmed** | Re-derived value matches the claim (within rounding) | Proceed with the proposal unchanged. Record the source + criterion in the point's `Notes`. |
| **Corrected** | Re-derived value differs | Update the proposal to the true value. Flag in chat with old → new and the cause. |
| **Unreproducible** | No source can produce the claimed value | Do **not** invent a replacement. Either re-derive with a defensible criterion (and rewrite the claim around it) or mark the point `Deferred` with the reason. |
| **Inconsistent** | The claim contradicts itself (e.g. `82 of 42.381 = 0,5%` when it is 0,19%) | Treat as Corrected; fix the internal arithmetic, not just one side. |

For **Corrected / Unreproducible / Inconsistent**, surface before applying:

```text
## Data check — Point N

**Claim**: <verbatim figure from text>
**Source**: <file / script / query used>
**Criterion**: <column, filter, denominator, regex>
**Re-derived**: <true value> (<n>, denominator <D>)
**Verdict**: Confirmed | Corrected | Unreproducible | Inconsistent
**Cause** (if not Confirmed): <e.g. substring `stem`⊂`sistema`; wrong denominator>
```

Then continue the standard decision proposal in `30-iterate-points.md`, carrying the corrected value.

## 5. Provenance Interaction

If a corrected/unreproducible figure also appears in **prior published or submitted versions**, note it in the point's `Notes` and in the final sheet (`70-final-sheet.md`). When the feedback source is `journal` (a real reviewer round), the response letter must state explicitly what changed and why — a number silently altered between v(N) and v(N+1) is something an attentive reviewer detects by diffing. Simulated rounds need only an internal changelog line.

## 6. Notes

- This step is **not optional** when a numeric claim is in scope. Skipping it silently is a binding violation, same severity as auto-committing.
- The check applies symmetrically: verify a figure you are *removing* too, in case the removal is based on a wrong premise.
- Cache nothing across versions. Re-derive every round; the data source may have changed.
