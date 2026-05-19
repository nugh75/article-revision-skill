#!/usr/bin/env bash
# gdrive_sync.sh — rclone fallback for the Drive collaboration workflow
# (workflow/80-gdrive-collab.md). Use only when the claude.ai Google Drive
# MCP connector is unavailable.
#
# Requires: rclone with a configured Drive remote.
#   rclone config            # create a remote, e.g. named "gdrive"
#
# Env:
#   RCLONE_REMOTE   rclone remote name           (default: gdrive)
#   GDRIVE_PATH     remote path for this project  (e.g. "ECPS/revisione-7862")
#
# Usage:
#   gdrive_sync.sh push <local-file> [<local-file> ...]   # repo -> Drive
#   gdrive_sync.sh pull <local-dir>                        # Drive -> repo (feedback)
#   gdrive_sync.sh ls                                      # list remote folder
#
# The script never shares the folder or emails anyone. Sharing with
# colleagues is done by the user in the Drive UI.

set -euo pipefail

REMOTE="${RCLONE_REMOTE:-gdrive}"
RPATH="${GDRIVE_PATH:?set GDRIVE_PATH to the remote folder path}"

command -v rclone >/dev/null || { echo "rclone not installed" >&2; exit 1; }

cmd="${1:-}"; shift || true
case "$cmd" in
  push)
    [ "$#" -ge 1 ] || { echo "push needs at least one file" >&2; exit 2; }
    for f in "$@"; do
      [ -f "$f" ] || { echo "skip (not a file): $f" >&2; continue; }
      rclone copy -P "$f" "${REMOTE}:${RPATH}/"
      echo "pushed: $f -> ${REMOTE}:${RPATH}/"
    done
    ;;
  pull)
    dest="${1:?pull needs a local destination dir}"
    mkdir -p "$dest"
    rclone copy -P "${REMOTE}:${RPATH}/feedback" "$dest"
    rclone copy -P "${REMOTE}:${RPATH}/approvals.md" "$dest" 2>/dev/null || true
    echo "pulled feedback -> $dest"
    ;;
  ls)
    rclone lsf "${REMOTE}:${RPATH}"
    ;;
  *)
    echo "usage: gdrive_sync.sh {push <files...>|pull <dir>|ls}" >&2
    exit 2
    ;;
esac
