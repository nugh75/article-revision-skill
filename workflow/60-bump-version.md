# 60 — Bump Version

Triggered:

- when the user signals the end of a revision round, such as *"close this version"*;
- when the *accepted-since-last-bump* counter in the project file reaches `AUTO_BUMP_THRESHOLD` (default 5), and the skill proposes the bump in chat;
- when the user explicitly asks, such as *"create v(N+1) now"*.

Never bump without explicit confirmation.

## 1. Pre-Flight Checks

Before bumping:

- Show the count of accepted changes since the last bump and a short list of affected points.
- Report current char/word count and budget status.
- Ask the user to confirm the bump:

  ```text
  Ready to create a new version:
  - <K> accepted changes since the last bump
  - points: <list>
  - count: <M> chars (<over|under> by <N>)

  Proceed? (yes / no / show points again)
  ```

- If points are still `To decide`, mention them: `There are <X> points still open. Do you want to force the bump (points remain in the project file) or close them first?`

## 2. Run Bump Script

```bash
NEW_PATH=$(scripts/new_version.sh <current-article-path>)
```

The script:

- copies the current file with incremented `vN+1` and current timestamp `YYYY-MM-DD-HHMM`;
- preserves the `-anonymous` suffix if present;
- prints the new path on stdout.

Resulting filename pattern: `article-v(N+1)-YYYY-MM-DD-HHMM[-anonymous].md`. Multiple bumps in the same day get distinct files because the time differs.

## 3. Generate Diff Summary

```bash
scripts/diff_versions.sh --auto $NEW_PATH > revisions/<slug>/diff-vN-to-v(N+1).md
```

The diff lists what changed between the previous file and the new one. Useful for the *Change history* section of the final sheet.

## 4. Reset Counter

In the project file, reset `<!-- accepted_since_bump: 0 -->` and add an entry to a *Bump history* section at the bottom:

```markdown
## Bump History

- vN → v(N+1) — YYYY-MM-DD HH:MM — <K> accepted changes
```

## 5. Notify User

```text
Version v(N+1) created: <NEW_PATH>
timestamp: <YYYY-MM-DD HH:MM>
diff: <X> changed lines · chars <signed> · words <signed>

Counter reset. Pending uncommitted changes: N files.

Suggested commit message, if you want to commit:
  bump: vN → v(N+1) (<K> accepted points)

Ready to:
- continue revision on v(N+1)?
- generate the final sheet (`70-final-sheet.md`)?
- close the session?
```

The skill **does not commit**. The suggested message is provided in chat for the user to copy if desired.

## 6. Edge Case — Destination Already Exists

If `article-v(N+1)-YYYY-MM-DD-HHMM[-anonymous].md` already exists, which is unlikely with minute-level resolution, the script aborts. Ask:

> A file with the same timestamp already exists. Should I wait a minute and retry? (yes / cancel)
