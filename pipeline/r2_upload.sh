#!/usr/bin/env bash
#
# Upload the dictionary stores to the Cloudflare R2 bucket.
#
# WRITTEN 2026-08-07 for the D+B decision in docs/DEPLOY_SCALE.md 6a.  Run by
# the reader, on his own machine, with his own credentials.  NOTHING in this
# file contains a secret and nothing in it should ever be made to: rclone holds
# the credentials in its own config, which is the point.
#
# ---------------------------------------------------------------------------
# WHAT THIS DOES *NOT* DO, AND THAT IS DELIBERATE
#
# It does not move, delete or rewrite a single file in the repository.  At the
# point this script runs, `site/lookup/` and `site/lookup_eval/` are exactly
# where they have always been and Pages is still publishing them.  This is a
# COPY to a second place, so that the second place can be tested before
# anything depends on it.  The relocation is step 4 of 6a and comes later.
#
# Re-running is cheap and is the intended way to update a dictionary:
# `--checksum` sends only what actually changed.  That is the answer to "can we
# update the dictionaries?" -- an update becomes a sync to the bucket plus a
# repo commit, and the Pages deploy never sees it.
#
# ---------------------------------------------------------------------------
# ONE-TIME SETUP, BY HAND, BEFORE THE FIRST RUN
#
#   1. Create the R2 bucket in the Cloudflare dashboard.
#   2. Bind a custom domain to it (working name: dict.buddha-dhamma.net).
#      A custom domain, not the r2.dev development URL -- r2.dev is rate
#      limited and not meant to be depended on.
#   3. Apply the CORS policy in `pipeline/r2_cors.json`.  dict.<domain> is a
#      DIFFERENT ORIGIN from <domain>, so without this every fetch fails and
#      the dictionary panel is silently empty.
#   4. `rclone config` -- new remote, type `s3`, provider `Cloudflare`,
#      endpoint `https://<ACCOUNT_ID>.r2.cloudflarestorage.com`, and an R2 API
#      token with Object Read & Write.  Name the remote `osbct-r2`.
#   5. Set BUCKET below, then run this script from the repository root.
#
# ---------------------------------------------------------------------------
# THE CONTENT-TYPE DECISION, WHICH IS THE WHOLE RISK -- see DEPLOY_SCALE 6b
#
# `jfetch` (site/reader/panel.js:499) sniffs the gzip magic bytes because a
# `.gz` can arrive EITHER as opaque compressed bytes (host sets no
# Content-Encoding, panel inflates it itself) OR already inflated by the
# browser (host sets `Content-Encoding: gzip`).  Both branches exist; only one
# runs, and which one is the HOST's choice.
#
# This script deliberately chooses the OPAQUE form -- `application/gzip`, no
# `Content-Encoding` -- because that is what GitHub Pages does today and what
# is therefore already proven in production.  Changing the origin and the
# encoding semantics in the same step would mean a failure could be either.
#
# If you change this, you are changing which branch of `jfetch` runs in
# production, and `pipeline/check_r2_origin.js` must be re-run.  Do not change
# it casually and do not change it at the same time as anything else.
#
set -euo pipefail

BUCKET="${OSBCT_R2_BUCKET:-osbct-dict}"
REMOTE="${OSBCT_R2_REMOTE:-osbct-r2}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Cache-Control.  Every fetch is versioned `?v=WLV` (panel.js:346), so in
# principle these objects could be immutable for a year.  They are NOT set that
# way yet, because the WLV bump is a human step with no gate behind it and a
# forgotten bump against a one-year cache is unrecoverable for a reader who has
# already loaded the page.  One day is the honest setting until that gate
# exists; raise it afterwards, not before.  DEPLOY_SCALE 6c.
CACHE="public, max-age=86400"

if ! command -v rclone >/dev/null 2>&1; then
  echo "rclone is not installed.  https://rclone.org/downloads/" >&2
  exit 1
fi

if [ ! -d "$ROOT/site/lookup" ] || [ ! -d "$ROOT/site/lookup_eval" ]; then
  # After step 4 of 6a the stores live at stores/ instead.  Say so rather than
  # uploading nothing and reporting success, which is the failure this project
  # keeps meeting.
  if [ -d "$ROOT/stores/lookup" ]; then
    echo "The stores have been relocated to stores/.  Edit SRC below." >&2
  else
    echo "Cannot find the stores under $ROOT/site/." >&2
  fi
  exit 1
fi

echo "==> uploading to ${REMOTE}:${BUCKET}"
echo "    source: $ROOT/site/{lookup,lookup_eval}"
echo

# Three passes, because the content type differs and rclone applies
# --header-upload to everything it touches in one run.
#
# Pass order matters only in that `*.json` does NOT match `*.json.gz` in
# rclone's globbing, so the two passes do not overlap.  Verified by the counts
# printed at the end: 13,369 .json + 11,229 .json.gz + 1 LICENSE = 24,599.

for pair in "lookup" "lookup_eval"; do
  SRC="$ROOT/site/$pair"
  DST="${REMOTE}:${BUCKET}/$pair"

  echo "--> $pair : plain .json (application/json)"
  rclone copy "$SRC" "$DST" \
    --include "*.json" \
    --header-upload "Content-Type: application/json; charset=utf-8" \
    --header-upload "Cache-Control: $CACHE" \
    --checksum --transfers 32 --checkers 32 --stats 10s

  echo "--> $pair : gzipped shards (application/gzip, NO Content-Encoding)"
  rclone copy "$SRC" "$DST" \
    --include "*.json.gz" \
    --header-upload "Content-Type: application/gzip" \
    --header-upload "Cache-Control: $CACHE" \
    --checksum --transfers 32 --checkers 32 --stats 10s

  echo "--> $pair : everything else (LICENSE and any stray file)"
  rclone copy "$SRC" "$DST" \
    --exclude "*.json" --exclude "*.json.gz" \
    --header-upload "Content-Type: text/plain; charset=utf-8" \
    --header-upload "Cache-Control: $CACHE" \
    --checksum --transfers 8 --checkers 8 --stats 10s
done

echo
echo "==> counting what landed"
for pair in "lookup" "lookup_eval"; do
  n=$(rclone size "${REMOTE}:${BUCKET}/$pair" --json | python3 -c 'import json,sys;print(json.load(sys.stdin)["count"])')
  local_n=$(cd "$ROOT" && git ls-files "site/$pair" | wc -l | tr -d ' ')
  echo "    $pair : $n in the bucket, $local_n tracked in git"
  if [ "$n" != "$local_n" ]; then
    echo "    !! MISMATCH.  Do not proceed to the origin gate until this is explained." >&2
  fi
done

echo
echo "Next: run pipeline/check_r2_origin.js against the custom domain."
echo "Do NOT relocate anything out of site/ until that gate is green."
