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

Run `scripts/new_version.sh <current-article-path>` through the approved project
environment. The new name is
`<prefix>-v(N+1)-YYYY-MM-DD-HHMM[-anonymous].md`; remove a source `-drive`
provenance token and preserve `-anonymous`.

At the first-edit boundary, create the version before modifying it. Then create
the task file and reconcile the freeze ledger through `10-setup.md`.

For an additional mid-round bump, summarize accepted changes, open points, and
the length budget before asking. Carry ledger anchors forward; mark unmatched
anchors stale rather than dropping them.

Do not create an immediate Git checkpoint. The new version belongs to the local
active-session manifest until Git is separately authorized.

If the timestamped destination already exists, stop and ask whether to retry
with a new timestamp.
