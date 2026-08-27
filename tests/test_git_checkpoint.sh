#!/usr/bin/env bash
set -euo pipefail

SKILL_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TEST_ROOT="$(mktemp -d)"
trap 'rm -rf -- "$TEST_ROOT"' EXIT

REMOTE="$TEST_ROOT/remote.git"
WORK="$TEST_ROOT/work"

git init --bare --initial-branch=main "$REMOTE" >/dev/null
git init --initial-branch=main "$WORK" >/dev/null
git -C "$WORK" config user.name "Contract Test"
git -C "$WORK" config user.email "contract@example.invalid"
printf '%s\n' "base" > "$WORK/allowed.md"
printf '%s\n' "base" > "$WORK/unrelated.md"
git -C "$WORK" add allowed.md unrelated.md
git -C "$WORK" commit -m "base" >/dev/null
git -C "$WORK" remote add origin "$REMOTE"
git -C "$WORK" push -u origin main >/dev/null

printf '%s\n' "allowed change" > "$WORK/allowed.md"
"$SKILL_ROOT/scripts/git_checkpoint.sh" \
  --repo "$WORK" --message "test: allowed" -- allowed.md >/dev/null
test "$(git -C "$WORK" rev-parse HEAD)" = \
  "$(git --git-dir="$REMOTE" rev-parse refs/heads/main)"

printf '%s\n' "staged elsewhere" > "$WORK/unrelated.md"
git -C "$WORK" add unrelated.md
printf '%s\n' "next allowed change" > "$WORK/allowed.md"
if "$SKILL_ROOT/scripts/git_checkpoint.sh" \
  --repo "$WORK" --message "test: reject staged" -- allowed.md >/dev/null 2>&1; then
  printf '%s\n' "expected unrelated staged path rejection" >&2
  exit 1
fi
git -C "$WORK" restore --staged unrelated.md

printf '%s\n' "secret" > "$WORK/.env"
if "$SKILL_ROOT/scripts/git_checkpoint.sh" \
  --repo "$WORK" --message "test: reject env" -- .env >/dev/null 2>&1; then
  printf '%s\n' "expected .env rejection" >&2
  exit 1
fi

printf '%s\n' "git-checkpoint-tests=ok"
