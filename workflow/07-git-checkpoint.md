# 07 — Explicit Git Checkpoint

Create and push a scoped checkpoint only after Git authorization distinct from
approval of manuscript text.

## Authorization

Valid authorization is one of:

- the user answers `sì` to the dedicated threshold prompt;
- the user explicitly requests `commit e push`;
- `/r-handoff --git`;
- a fully specified `/r-auto ... --git`.

`Accetta`, `applica`, `chiudi`, `fine`, `pause`, `stop`, `/r-handoff`, and a
plain `/r-auto` are not Git authorization.

## Interactive threshold

`AUTO_GIT_CHECKPOINT_THRESHOLD` defaults to `5`. After that many applied
changes, show and wait:

```text
Si sono accumulate <N> modifiche dall'ultimo checkpoint Git.
Vuoi creare un commit circoscritto ai file della sessione e fare push su <upstream>? (sì / non ora)
```

On `non ora`, preserve local work and prompt again only after another threshold
of changes. Never block safe local revision merely because publication was
deferred.

## Authorized automatic mode

Only `/r-auto ... --git` may use `mode=auto-authorized` at thresholds and final
closure without another prompt. Plain `/r-auto` keeps all changes local.

## Manifest and preflight

Build an explicit list containing only files created or changed by the active
revision round: article version, task, plan, ledger changes, bibliography/data
audits, auto reports, decision log, final sheet, and synchronized exports when
applicable.

- Exclude `.env`, unrelated paths, and unresolved globs.
- Never use `git add -A` or `git add .`.
- Stop if unrelated paths are already staged.
- Require a named branch and one configured upstream.
- Run the relevant semantic/scope checks and `git diff --check` before staging.

Run `scripts/git_checkpoint.sh` with the explicit manifest and normal hooks.
Verify a successful push by comparing `HEAD` with `git ls-remote`.

On failure, preserve files and any local commit. Report the exact error. Never
pull, merge, rebase, amend, reset, force-push, or bypass hooks automatically.

Git authorization never extends to PRs, tags, releases, Drive actions, or
unrelated files.
