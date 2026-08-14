#!/usr/bin/env bash
# Create and push a scoped revision checkpoint without absorbing unrelated work.

set -euo pipefail

# Automatic checkpoints must fail clearly instead of opening credential or SSH
# prompts that would turn a background checkpoint into an interactive action.
export GIT_TERMINAL_PROMPT=0
export GCM_INTERACTIVE=never
if [[ -z "${GIT_SSH_COMMAND:-}" ]]; then
  export GIT_SSH_COMMAND="ssh -o BatchMode=yes"
fi

usage() {
  echo "usage: git_checkpoint.sh --message <text> [--repo <path>] [--remote <name> --branch <name>] -- <session-file>..." >&2
  exit 2
}

REPO="."
MESSAGE=""
REMOTE=""
BRANCH=""
FILES=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo)
      [[ $# -ge 2 ]] || usage
      REPO="$2"
      shift 2
      ;;
    --message)
      [[ $# -ge 2 ]] || usage
      MESSAGE="$2"
      shift 2
      ;;
    --remote)
      [[ $# -ge 2 ]] || usage
      REMOTE="$2"
      shift 2
      ;;
    --branch)
      [[ $# -ge 2 ]] || usage
      BRANCH="$2"
      shift 2
      ;;
    --)
      shift
      FILES=("$@")
      break
      ;;
    *)
      usage
      ;;
  esac
done

[[ -n "$MESSAGE" && ${#FILES[@]} -gt 0 ]] || usage
command -v git >/dev/null || { echo "git not installed" >&2; exit 3; }
command -v realpath >/dev/null || { echo "realpath not installed" >&2; exit 3; }

ROOT="$(git -C "$REPO" rev-parse --show-toplevel 2>/dev/null)" || {
  echo "not a git repository: $REPO" >&2
  exit 3
}

for marker in MERGE_HEAD REBASE_HEAD CHERRY_PICK_HEAD REVERT_HEAD; do
  marker_path="$(git -C "$ROOT" rev-parse --git-path "$marker")"
  [[ ! -e "$marker_path" ]] || {
    echo "git operation in progress: $marker" >&2
    exit 4
  }
done

CURRENT_BRANCH="$(git -C "$ROOT" symbolic-ref --quiet --short HEAD 2>/dev/null)" || {
  echo "detached HEAD: automatic checkpoint refused" >&2
  exit 4
}

if [[ -z "$REMOTE" || -z "$BRANCH" ]]; then
  UPSTREAM="$(git -C "$ROOT" rev-parse --abbrev-ref --symbolic-full-name '@{upstream}' 2>/dev/null)" || {
    echo "no upstream configured for $CURRENT_BRANCH" >&2
    exit 4
  }
  [[ "$UPSTREAM" == */* ]] || {
    echo "invalid upstream: $UPSTREAM" >&2
    exit 4
  }
  [[ -n "$REMOTE" ]] || REMOTE="${UPSTREAM%%/*}"
  [[ -n "$BRANCH" ]] || BRANCH="${UPSTREAM#*/}"
fi

git -C "$ROOT" remote get-url "$REMOTE" >/dev/null 2>&1 || {
  echo "unknown git remote: $REMOTE" >&2
  exit 4
}

declare -A ALLOWED=()
REL_FILES=()
for file in "${FILES[@]}"; do
  if [[ "$file" = /* ]]; then
    absolute="$(realpath -m -- "$file")"
  else
    absolute="$(realpath -m -- "$ROOT/$file")"
  fi
  relative="$(realpath --relative-to="$ROOT" -- "$absolute")"
  case "$relative" in
    ..|../*|.git|.git/*)
      echo "session path escapes repository: $file" >&2
      exit 5
      ;;
    .env|*/.env|.env.*|*/.env.*)
      echo "refusing to checkpoint environment file: $relative" >&2
      exit 5
      ;;
  esac
  if [[ -z "${ALLOWED[$relative]+x}" ]]; then
    ALLOWED["$relative"]=1
    REL_FILES+=("$relative")
  fi
done

while IFS= read -r -d '' staged; do
  [[ -n "${ALLOWED[$staged]+x}" ]] || {
    echo "unrelated staged path blocks automatic checkpoint: $staged" >&2
    exit 5
  }
done < <(git -C "$ROOT" diff --cached --name-only -z)

REMOTE_REF="refs/remotes/$REMOTE/$BRANCH"
git -C "$ROOT" fetch --quiet "$REMOTE" "+refs/heads/$BRANCH:$REMOTE_REF" || {
  echo "cannot fetch $REMOTE/$BRANCH" >&2
  exit 6
}
git -C "$ROOT" merge-base --is-ancestor "$REMOTE_REF" HEAD || {
  echo "remote branch is not an ancestor of HEAD; pull/rebase requires human review" >&2
  exit 6
}

git -C "$ROOT" diff --check -- "${REL_FILES[@]}"
git -C "$ROOT" add -- "${REL_FILES[@]}"

while IFS= read -r -d '' staged; do
  [[ -n "${ALLOWED[$staged]+x}" ]] || {
    echo "unrelated staged path detected after staging: $staged" >&2
    exit 5
  }
done < <(git -C "$ROOT" diff --cached --name-only -z)

if git -C "$ROOT" diff --cached --quiet -- "${REL_FILES[@]}"; then
  echo "status=noop"
  echo "remote=$REMOTE"
  echo "branch=$BRANCH"
  exit 0
fi

git -C "$ROOT" diff --cached --check
git -C "$ROOT" commit -m "$MESSAGE"
COMMIT="$(git -C "$ROOT" rev-parse HEAD)"

if ! git -C "$ROOT" push "$REMOTE" "HEAD:refs/heads/$BRANCH"; then
  echo "status=push-failed"
  echo "commit=$COMMIT"
  echo "remote=$REMOTE"
  echo "branch=$BRANCH"
  exit 7
fi

REMOTE_COMMIT="$(git -C "$ROOT" ls-remote --heads "$REMOTE" "refs/heads/$BRANCH" | awk 'NR == 1 {print $1}')"
if [[ "$REMOTE_COMMIT" != "$COMMIT" ]]; then
  echo "remote verification failed: expected $COMMIT, found ${REMOTE_COMMIT:-none}" >&2
  echo "status=verify-failed"
  echo "commit=$COMMIT"
  echo "remote=$REMOTE"
  echo "branch=$BRANCH"
  exit 8
fi

echo "status=pushed"
echo "commit=$COMMIT"
echo "remote=$REMOTE"
echo "branch=$BRANCH"
