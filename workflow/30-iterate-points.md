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

**Proposal**
> <proposed text>

**Δ**: chars <signed> / words <signed> · bibliography: <signed> entries · risk: <low|medium|high>

**Norms respected**: <list>
**Possible exceptions**: <list, with reason>

**Decision?** Accept / Reject / Modify
```

Wait for the user. Do **not** apply pre-emptively.

## 4. Handle Response

### Accept

1. Apply via Edit on the article, and on `.bib` or other files if relevant.
2. Update the project file: `Decision` = `Accepted`.
3. Increment the *accepted-since-last-bump* counter, stored as an HTML comment in the project file: `<!-- accepted_since_bump: N -->`.
4. Run `scripts/char_count.py --limit-from-env` and report the new count plus delta.
5. **Do not commit.** Acknowledge:

   ```text
   Applied. Pending uncommitted changes: N files.
   Count: M chars (<over|under> by X). Accepted since bump: <K>/<AUTO_BUMP_THRESHOLD>.
   ```

6. If the counter has reached `AUTO_BUMP_THRESHOLD`, propose a bump:

   ```text
   You accepted <AUTO_BUMP_THRESHOLD> changes since the last bump.
   Create a new file version now? (yes / continue)
   ```

   On `yes`, hand off to `60-bump-version.md`.
7. Move to the next point.

### Reject

1. Update the project file: `Decision` = `Rejected`, with the reason supplied by the user or `author choice` if none.
2. No file modifications.
3. Move on.

### Modify

1. Ask the user: `How should I modify the proposal?`
2. Regenerate the proposal in light of the new direction.
3. Return to step 3 of this workflow. After eventual `Accept`, label the point as `Modified` (not `Accepted`).

## 5. Edge Cases

- **Multiple decisions in one user message** (for example, *"Accept all except point 3"*). Process them sequentially with the per-point logic above. Still no auto-commit.
- **Character overshoot after Accept.** Report and ask: `The overrun is now +X. Do you prefer to proceed and handle it in the final sweep, or look for a compensating cut now?`
- **Bibliography conflict.** If the user wants a key that does not exist or has dubious metadata, defer to `40-bibliography-check.md` and do not apply until cleared.
- **Anglicism not in whitelist** (`ARTICLE_LANG=it` only). Surface in the proposal block under `Possible exceptions`; the user decides whether to add it to the whitelist or rephrase.
- **Whole article scope.** Walk the article section by section. The user can pause at any moment with `pause` or `stop`, and resume later from the same point.

## 6. State Persistence

The accepted-since-bump counter and per-point decision state live entirely inside the `revision-plan-vN.md` file. On every Accept/Reject/Modify, rewrite the relevant section of that file. This way, an interrupted session resumes cleanly: when the skill is re-invoked, it reads the project file and continues from the first point still in `To decide` state.
