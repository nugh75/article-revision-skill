# 12 — Read-only Audit

Triggered by `/r-audit [scope]`. Diagnose the requested manuscript scope and
return findings in chat without creating revision state.

## Contract

- Load the active manuscript and any existing norms, bibliography, and freeze
  ledger read-only through `10-setup.md`.
- Do not bootstrap unless a requested check truly requires missing
  infrastructure and the user separately approves its creation.
- Do not bump, create a task, save a sidecar, update the ledger, sync exports,
  stage, commit, or push.
- Read adjacent context for interpretation, but keep findings inside the named
  audit scope.

## Lenses

Choose only the lenses relevant to the request:

1. Run `wayfinder` for definitions, operational explanations, construct
   boundaries, relations, argumentative function, and local content
   architecture. For a full inventory or reordering proposal, route to
   `13-content-structure.md`.
2. Use `scrittura` for idea organization, clarity, cohesion, lexical precision,
   outlines, and readable alternatives.
3. Use `tone-of-voice` as a final style diagnostic after conceptual and factual
   checks.
4. Use `40-bibliography-check.md` or `51-data-verification.md` when a cited or
   numeric claim is in scope; verification remains read-only.

## Output

Report findings in priority order:

```text
## Audit — <scope>

### Blocking
- <locator> — <problem> — <why it matters>

### Important
- <locator> — <problem> — <recommended direction>

### Optional
- <locator> — <stylistic opportunity>

No files modified.
```

Distinguish conceptual defects from wording defects. Quote only the minimum
text needed to identify the issue. If the user later asks to apply fixes,
enter the tracked first-edit lifecycle in `10-setup.md`; do not treat the audit
request itself as edit or Git authorization.
