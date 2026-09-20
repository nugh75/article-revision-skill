# 60 — Create a Working Version

Create a new manuscript version when the first approved edit of a tracked round
is about to be applied, when `/r-auto` begins, or when the user explicitly asks
for `/r-bump`. Read-only diagnosis never bumps.

`direct-apply` never calls this workflow. An explicit request to edit a named
version in place controls unless the user also asks to start a tracked round.

## Authorization

- `mode=first-edit`: the explicit acceptance of the proposed file edit
  authorizes the version copy needed to apply it. Announce the action.
- `/r-auto` with task and scope authorizes its first working version.
- `/r-bump` or an extra mid-round bump requires explicit confirmation.

No bump authorizes commit or push.

## Create

On an integrated project (`05_Script/tesi.py` exists), the same script delegates
to the project coordinator. Set `BUMP_MESSAGE` to the reason for the new round.
It synchronizes the clouds first, requires an unambiguous active source, creates
the version and technical log, carries ledger anchors forward and synchronizes
those records. Standard output remains the new absolute article path.
For first-edit revision, this uses `--prepare`: generate Word only after the
approved edits through the export workflow. An explicit terminal `make bump`
also generates and synchronizes Word immediately. A typed bump command is an
explicit request; do not ask for the same confirmation a second time.
If the cloud has a newer source than the supplied path, stop and revalidate the
approved edits against that source. If a version was created but a later step
failed, keep it and resume export/sync; never retry by creating another version.

Run `scripts/new_version.sh <current-article-path>` through the approved project
environment. The new name is
`<prefix>-v(N+1)-YYYY-MM-DD-HHMM[-anonymous].md`; remove a source `-drive`
provenance token and preserve `-anonymous`.

At the first-edit boundary, create the version before modifying it. Then create
the task file through `10-setup.md`. On integrated projects, the coordinator
already carried the ledger forward; read its result rather than repeating it.

For an additional mid-round bump, summarize accepted changes, open points, and
the length budget before asking. Carry ledger anchors forward; mark unmatched
anchors stale rather than dropping them. Then run `scripts/freeze_check.py` on the
new version (`15-freeze-ledger.md` §13.6, §14); a passage reported `stale` after a
bump means the bump altered locked text, so report it before continuing.

Do not create an immediate Git checkpoint. The new version belongs to the local
active-session manifest until Git is separately authorized.

If the timestamped destination already exists, stop and ask whether to retry
with a new timestamp.
