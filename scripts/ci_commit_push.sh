#!/usr/bin/env bash
# Commit what is already staged and push it WITHOUT force.
#
# Usage:  bash scripts/ci_commit_push.sh "<commit message>"
#
# - Nothing staged  -> prints "nothing to commit" and exits 0.
# - Push rejected   -> another job/machine pushed first: rebase onto the remote
#                      branch and retry (max 3 attempts). Never force-pushes,
#                      so commits from other workflows or your PC are never lost.
# - Rebase conflict -> fails loudly (non-zero) so a human looks at it.
set -euo pipefail

msg="${1:?usage: ci_commit_push.sh \"<commit message>\"}"

if git diff --staged --quiet; then
  echo "nothing to commit"
  exit 0
fi

git commit -m "$msg"

branch="${GITHUB_REF_NAME:-$(git rev-parse --abbrev-ref HEAD)}"

for attempt in 1 2 3; do
  if git push origin "HEAD:${branch}"; then
    exit 0
  fi
  echo "push rejected (attempt ${attempt}/3) - rebasing onto origin/${branch} and retrying"
  git pull --rebase origin "${branch}"
done

echo "::error::push failed after 3 attempts"
exit 1
