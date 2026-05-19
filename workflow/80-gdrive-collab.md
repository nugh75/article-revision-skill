# 80 — Google Drive Collaboration

Triggered by `/r-gdrive`. Creates and syncs a shared Drive folder so
colleagues can read the revised article and leave suggestions, then pulls
their feedback back into the project as a revision source.

Two backends, in priority order:

1. **MCP connector** (`claude.ai Google Drive`) — preferred. Tools:
   `search_files`, `create_file`, `read_file_content`,
   `download_file_content`, `copy_file`, `get_file_metadata`,
   `get_file_permissions`, `list_recent_files`. The user must authenticate
   once via `/mcp`.
2. **rclone fallback** — `scripts/gdrive_sync.sh` for environments without
   the MCP connector. Requires a configured rclone Drive remote.

The skill never adds collaborators itself (no permission-write tool /
rclone scope). Sharing the folder with colleagues is the user's action in
the Drive UI; surface this explicitly.

## Sub-command: `create`

1. Read `GDRIVE_REVIEW_FOLDER_ID` from `.env`. If set and still valid
   (`get_file_metadata` succeeds), reuse it — do not create a duplicate.
2. Otherwise ask the user for the parent folder (search by name with
   `search_files`, `mimeType = 'application/vnd.google-apps.folder'`).
   Never create at Drive root silently.
3. Create `revisione-<slug>/` under the chosen parent
   (`create_file`, mime `application/vnd.google-apps.folder`).
4. Inside it, create:
   - the **article Google Doc** — only **after the first revision pass**
     (avoid uploading a duplicate of the already-submitted text). Convert
     the current `article-vN.md` to a Google Doc (`create_file` with
     `text/plain` content auto-converts, or upload a `.docx`).
   - an empty `feedback/` subfolder for free-form colleague notes.
   - `approvals.md` from `templates/approvals.md` (structured fallback).
5. Write the resulting folder id back to `.env` as
   `GDRIVE_REVIEW_FOLDER_ID` (ask before editing `.env`).
6. Tell the user to **Share** `revisione-<slug>/` with colleagues
   (suggesting access) from the Drive UI.

## Sub-command: `push`

Upload the latest revised version (and, if generated, the redline + the
response-to-reviewers letter) into `revisione-<slug>/`. Use a clear name
including the version, e.g. `articolo-<slug>-vN-revisione`. Do not
overwrite the colleagues' working Doc without confirming.

## Sub-command: `sync` (pull feedback in)

1. List `revisione-<slug>/` and `feedback/` (`search_files` by `parentId`).
2. For the article Google Doc: `read_file_content` to get the body.
   Inline Google Docs **comments/suggestions** may not be exposed by the
   connector — if they are not retrievable, instruct colleagues to either
   accept their suggestions into the body or record verdicts in
   `approvals.md`.
3. Download every file in `feedback/` and `approvals.md`
   (`download_file_content`).
4. Consolidate into `revisions/<slug>/sources/drive-feedback-<YYYY-MM-DD>.md`
   — same role as `reviewer-feedback.md`: a **source**, not auto-applied.
5. Summarise in chat: how many colleague notes, how many map to existing
   points, how many are new. The user then runs `/r-approve` or a revision
   pass referencing this source.

## Notes

- Confidential manuscript under double-blind review: the shared folder is
  private to invited colleagues; never make it link-public.
- The skill does not email. It only places files and reads them back.
