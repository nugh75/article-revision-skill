# 30 — Iterate Points

Core loop. Apply to a single point, a paragraph, or the whole article; the user picks the scope.

## 0. Determine Scope

If the user's instruction mentions a specific scope, use it:

- *"fix this sentence"* → **fragment**
- *"revise this paragraph"* / reviewer point → **paragraph**
- *"revise the whole article"* → **whole article** (sequential walk)

If unspecified, default to **paragraph** when processing a reviewer point, **fragment** otherwise. Always confirm in the proposal block which scope is being used.

## 1. Load Context

Read the relevant section(s) of the article. Identify the exact lines that the change touches:

- **fragment**: the single sentence or inline element (citation, formatting, term);
- **paragraph**: the smallest coherent block (one paragraph or one numbered subsection);
- **whole article**: walk every section, generating proposals one at a time. Never produce a single mass-replacement.

If the change involves a citation, run `40-bibliography-check.md` for the relevant key first.

If the change requires sample-description data, run `50-sample-description.md` first.

## 2. Generate Proposal

Apply:

- editorial norms loaded in setup;
- journal-specific style skill, if available;
- `templates/accepted-anglicisms-it.md` if `ARTICLE_LANG=it`;
- minimum surgical change: alter only what the point requires.

Never collapse multiple separate concerns into a single proposal. If the same paragraph needs both citation correction and phrasing change, present two consecutive proposals, each with its own decision.

## 3. Present In Chat

```text
## Point N — <short title> · scope: <fragment|paragraph|whole article>

**Original** (`<article>:<line-range>`)
> <verbatim text>

**Proposta**
> <proposed full text>

**Modifiche:**
1. `<old>` → `<new>` [(motivazione)]
2. `<old>` → `<new>` [(motivazione)]
...

**Δ**: chars <signed> / words <signed> · risk: <low|medium|high>

**Norms respected**: <list>
**Possible exceptions**: <list, with reason>

**A/R/M?** (indicare i numeri delle modifiche, es. "A 2,4" oppure "M 3: sostituire X con Y")
```

Wait for the user. Do **not** apply pre-emptively.

Each modification is numbered. The user responds with:
- `A 1,3` → accept modifications 1 and 3 only.
- `R 2` → reject modification 2.
- `M 4: <direction>` → modify modification 4 as directed.
- `A` (no numbers) → accept all modifications.
- `R` (no numbers) → reject the entire point.

## 4. Handle Response

### Accept (selected numbers or all)

1. Apply via Edit on the article only the modifications accepted by the user. If some modifications were rejected or left pending, apply only the accepted ones.
2. Update the project file: each accepted modification → `Accepted`.
3. Increment the *accepted-since-last-bump* counter.
4. **Do not commit.**
5. **Do not advance automatically.** Output:

   ```text
   Applicate modifiche <numbers>. [Restano in sospeso le modifiche <numbers>.] Ci sono altri cambiamenti da fare in questo paragrafo?
   ```

   Wait for an explicit command from the user.

6. If the counter has reached `AUTO_BUMP_THRESHOLD`, after the user signals to advance, propose a bump (hand off to `60-bump-version.md`).

### Reject (selected numbers)

1. Mark rejected modifications as `Rejected` in the project file + reason.
2. No file edits for those modifications.
3. **Do not advance automatically.** Output:

   ```text
   Modifiche <numbers> respinte. [Restano in sospeso le modifiche <numbers>.] Ci sono altri cambiamenti da fare in questo paragrafo?
   ```

### Reject (entire point)

1. Mark the entire point `Rejected` + reason.
2. No file modifications.
3. Advance to next point.

### Modify <N>: <direction>

1. Regenerate modification N according to the user's direction.
2. Re-present the updated modification in context, keeping the same numbering.
3. Return to step 3. After eventual `Accept`, label the modification as `Modified` (not `Accepted`).

### Advance to next point

Only advance when the user gives an explicit command:
- "no, prossimo paragrafo"
- "passa al prossimo"
- "next"
- "prossimo"

## 5. Edge Cases

- **Multiple decisions in one user message** (for example, *"Accept all except point 3"*). Process them sequentially with the per-point logic above. Still no auto-commit.
- **Character overshoot after Accept.** Report and ask: `The overrun is now +X. Do you prefer to proceed and handle it in the final sweep, or look for a compensating cut now?`
- **Bibliography conflict.** If the user wants a key that does not exist or has dubious metadata, defer to `40-bibliography-check.md` and do not apply until cleared.
- **Anglicism not in whitelist** (`ARTICLE_LANG=it` only). Surface in the proposal block under `Possible exceptions`; the user decides whether to add it to the whitelist or rephrase.
- **Whole article scope.** Walk the article section by section. The user can pause at any moment with `pause` or `stop`, and resume later from the same point.

## 6. State Persistence

The accepted-since-bump counter and per-point decision state live entirely inside the `revision-plan-vN.md` file. On every Accept/Reject/Modify, rewrite the relevant section of that file. This way, an interrupted session resumes cleanly: when the skill is re-invoked, it reads the project file and continues from the first point still in `To decide` state.
