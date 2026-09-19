# 08 — Revision tasks and archive

Use for `/r-tasks`, `/r-archive`, or a request to organize revision records.
This is administrative maintenance: no manuscript edit, bump, freeze, export,
cloud sync, or Git publication. The user's request to archive authorizes local
relocation; preview it and proceed within that scope.

Run with the project virtual environment. Resolve `SKILL_ROOT` to this skill's
installed directory; `PROJECT_ROOT` is the repository and `SLUG` is its existing
directory under `revisions/` (do not infer it from the filename if ambiguous).

```bash
"$PROJECT_ROOT/.venv/bin/python" "$SKILL_ROOT/scripts/revision_registry.py" status --project "$PROJECT_ROOT" --slug "$SLUG"
```

| Command | Script operation | Effect |
|---|---|---|
| `/r-tasks` | `status` | Read current sources and print pending work |
| `/r-tasks --refresh` | `refresh` | Regenerate `TASKS.md` and `ARCHIVE.md` |
| `/r-tasks --check` | `check` | Fail if the index is stale or archive integrity changed |
| `/r-archive` | `archive` | Read-only list of eligible files |
| `/r-archive --apply` | `archive --apply` | Move eligible files, repair revision references, regenerate indexes |

Eligibility: explicit terminal task states or applied proposal states; diffs,
final sheets and automation traces are historical records. An old date, an
accepted proposal, or a later article version alone never proves completion.
Unclassified proposals and audits stay visible as `da-verificare`.

For legacy inconsistencies, inspect the decision log and later tasks. Record an
evidence-backed administrative classification in
`revisions/<slug>/registry-decisions.json`: keys are original repository-relative
paths; values contain `status` and `evidence`. Supported terminal values are
`completed`, `closed`, `absorbed`, `superseded`, and `applied`. Retain source
wording; classify unresolved records as pending or leave them unclassified.

`archive-manifest.json` records old/new paths, reasons and integrity hashes.
Use it to resolve an old path. Archived content remains searchable, including
deferred items; a closed round never means its deferred suggestions are done.
Before reusing an old proposal, reconcile its scope with the current article,
ledger and newer decisions. Record each actual deferred intention in the ledger
or existing backlog, with source, next action and status; preserve diagnostic
read-only mode unless saving the intention was authorized.

After authorized task creation, updates, handoff, closure, or saving/updating a
proposal, run `refresh` when the project has opted in by having `TASKS.md`.
After closure offer an archive preview; apply only within an archive request.
`/r-status` also reads the live task report when opted in, alongside the ledger.

Completion: run `check`; every moved source has a manifest entry; unresolved
tasks, unclassified suggestions, ledger intentions and active `DA-SVILUPPARE`
markers remain discoverable. Report counts and outstanding uncertainty.
