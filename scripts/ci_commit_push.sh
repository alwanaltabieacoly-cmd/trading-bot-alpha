#!/usr/bin/env bash
# Commit what is already staged and push it WITHOUT force.
#
# Usage:  bash scripts/ci_commit_push.sh "<commit message>"
#
# - Nothing staged  -> prints "nothing to commit" and exits 0.
# - Push rejected   -> another job/machine pushed first: rebase onto the remote
#                      branch and retry (max 3 attempts). Never force-pushes,
#                      so commits from other workflows or your PC are never lost.
# - Unstaged files  -> autostashed around the rebase. Without --autostash the
#                      rebase aborts ("You have unstaged changes") and the run
#                      loses its commit; that happened 2026-10-23 when Daily
#                      learning and Deliberate pushed at the same second.
# - Rebase conflict -> GENERATED artifacts (reports/decisions/learning/briefs/scan)
#                      resolve automatically: the replayed commit (newest) wins.
#                      Conflicts in code/config still fail loudly for a human.
set -euo pipefail

msg="${1:?usage: ci_commit_push.sh \"<commit message>\"}"

if git diff --staged --quiet; then
  echo "nothing to commit"
  exit 0
fi

git commit -m "$msg"

branch="${GITHUB_REF_NAME:-$(git rev-parse --abbrev-ref HEAD)}"

is_generated() {
  case "$1" in
    research/reports/*|research/LESSONS_AUTO.md|reports/decisions/*|user_data/decisions/*)
      return 0
      ;;
    *)
      return 1
      ;;
  esac
}

resolve_conflicts() {
  local conflicted unresolved=0
  conflicted="$(git diff --name-only --diff-filter=U || true)"
  if [ -z "$conflicted" ]; then
    return 0
  fi
  while IFS= read -r f; do
    [ -z "$f" ] && continue
    if is_generated "$f"; then
      # During a rebase, --theirs is the commit being replayed: our freshest artifact.
      git checkout --theirs -- "$f" 2>/dev/null || git checkout --ours -- "$f" 2>/dev/null || true
      git add -- "$f"
      echo "resolved generated artifact (newest wins): $f"
    else
      echo "::error::unresolved conflict in non-generated file: $f"
      unresolved=1
    fi
  done <<< "$conflicted"
  [ "$unresolved" -eq 0 ] || return 1
  GIT_EDITOR=true git rebase --continue
}

for attempt in 1 2 3; do
  if git push origin "HEAD:${branch}"; then
    exit 0
  fi
  echo "push rejected (attempt ${attempt}/3) - rebasing onto origin/${branch} and retrying"
  if ! git pull --rebase --autostash origin "${branch}"; then
    if ! resolve_conflicts; then
      git rebase --abort 2>/dev/null || true
      echo "::error::rebase conflict in a non-generated file - human review required"
      exit 1
    fi
  fi
done

echo "::error::push failed after 3 attempts"
exit 1
