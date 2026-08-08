#!/bin/bash
# Commit and push OSBCT.  Usage:  ./push.sh
#
# The three commands underneath are ordinary git:
#
#     git add -A
#     git commit -F COMMIT_MSG.bak
#     git push
#
# What this script adds is three guards, each for something that has actually
# gone wrong here.
#
#   1. THE STALE `.git/index.lock`.  The agent works from a sandbox that cannot
#      delete it, so it is left behind and blocks the next `git add`.  Only
#      ZERO-BYTE locks are removed: a lock with contents may belong to a git
#      process that is genuinely running, and deleting that one corrupts things.
#
#   2. A STALE COMMIT MESSAGE.  `COMMIT_MSG.bak` is rewritten each session.  If a
#      session ends without rewriting it, `-F` would commit the PREVIOUS message
#      and the history would describe the wrong change.  The first line is
#      compared against HEAD's and the script stops if they match.
#
#   3. AN UNSTAMPED BUILD.  `stamp_build.py --write` is not optional after any
#      change under `site/`, and forgetting it means every visitor keeps the
#      cached old reader.  If `site/` is modified but `site/build.json` is not,
#      that is the signature of a forgotten stamp and the script stops.
#
# Nothing here is clever.  Each guard exists because the plain three commands
# were run without it once.
set -u
cd "$(dirname "$0")" || exit 1

# 1 --------------------------------------------------------------- stale lock
find .git -maxdepth 2 -name '*.lock' -size 0 -delete 2>/dev/null

# 2 -------------------------------------------------------- stale commit message
if [ ! -s COMMIT_MSG.bak ]; then
  echo "STOP: COMMIT_MSG.bak is missing or empty." >&2; exit 1
fi
new_subject=$(head -1 COMMIT_MSG.bak)
old_subject=$(git log -1 --pretty=%s 2>/dev/null)
if [ "$new_subject" = "$old_subject" ]; then
  echo "STOP: COMMIT_MSG.bak still carries the message of the last commit:" >&2
  echo "      \"$new_subject\"" >&2
  echo "      Either the session did not rewrite it, or this change has no" >&2
  echo "      message of its own.  Edit COMMIT_MSG.bak, or run:" >&2
  echo "         git add -A && git commit -F COMMIT_MSG.bak && git push" >&2
  exit 1
fi

# 3 ------------------------------------------------------------ unstamped build
if ! git diff --quiet -- site/ && git diff --quiet -- site/build.json; then
  echo "STOP: site/ is modified but site/build.json is not." >&2
  echo "      That is a forgotten stamp.  Run:" >&2
  echo "         python3 pipeline/stamp_build.py --write" >&2
  exit 1
fi

# ------------------------------------------------------------------ the commit
echo "About to commit:"
git status --short
echo
echo "Message: $new_subject"
printf 'Enter to continue, Ctrl-C to stop. '
read -r _

git add -A || exit 1
git commit -F COMMIT_MSG.bak || exit 1
git push || exit 1

echo
echo "Pushed.  Now start a FRESH Pages run in GitHub → Actions."
echo "Never use 'Re-run failed jobs'; click 'Run workflow' instead."
echo "Then hard-reload the reader (Cmd-Shift-R) so the old build is not served."
