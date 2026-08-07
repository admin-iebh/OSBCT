# v2.4.0 — the dictionaries move out, and the archive keeps them

*Released 7 August 2026. 118 volumes, 89,512 paragraphs — **unchanged**.*

**No text changed in this release.** Not a paragraph, not a variant reading, not a
cross-reference. The corpus figures above are identical to v2.3.0's and are meant to be:
this release is entirely about where the dictionary data is *served from*, and about making
sure that an archived copy of this deposit still works when the serving arrangement is gone.

Anyone citing the corpus can treat v2.3.0 and v2.4.0 as the same text.

## What changed

**The dictionary stores moved out of `site/` and are served from a bucket.**
`site/lookup/` and `site/lookup_eval/` — 24,599 files — are now `stores/lookup/` and
`stores/lookup_eval/`, and the reader fetches them from `https://dict.buddha-dhamma.net/`
(Cloudflare R2).

**The site went from 26,576 published files to 1,977.** GitHub Pages republishes the whole
site on every push and gives up after ten minutes, a ceiling that **cannot be raised** —
600,000 ms is the maximum, not the default. Through late July and early August the site
failed to publish repeatedly at ~11m40s. It was never a size problem: CI checks out 833 MB,
comfortably inside the limit. It was the file count, and 93% of the files were dictionary
shards. The first two deploys after the move took **2m01s** and **1m41s**.

**The stores are still in this repository, and that is the point.** They could have been
moved to the bucket and deleted from here; that would have fixed the same problem and
quietly broken something else. **They are tracked, so they are inside this deposit** — all
24,599 of them — and a reader who has only the archived DOI a decade from now gets the
dictionaries along with the corpus.

**And the reader can find them there.** The panel tries the bucket first and falls back to
the copy inside the archive on any failure — 404, DNS, CORS, offline. Without that, the
deposit would have contained every shard on disk beside a reader looking for a domain that
may no longer exist: empty tabs, no error, and the files sitting right there. **Preserving
the data and teaching the reader to ignore it is worse than not preserving it, because it
looks fine.** This was caught while preparing this release, and it is the reason the release
waited a few hours.

**Nothing about lookup speed changed.** The shards were not merged or resized, so a word
lookup downloads exactly what it downloaded before. The one new cost is a single DNS lookup
and TLS handshake to a second origin on the first lookup of a session.

## Instruments

- **`pipeline/check_r2_origin.js`** — compares every probe **byte for byte** against the
  repository rather than trusting an HTTP 200, and runs three negative controls each time.
  It found two hazards nobody had named: **164 shard filenames are not ASCII** (`’ ‘ “ ” ° √`)
  and **458 contain a space** — the larger group, and the one that hides, because a space is
  printable ASCII and passes any "is it ascii" test. All survive the round trip intact.
- **`pipeline/check_archive_fallback.js`** — runs every sampled word twice, once with the
  bucket answering and once with it forcibly refused, and asserts the two results are
  **identical**. Comparing rather than asserting keeps a pre-existing defect from blocking a
  release, and keeps this gate honest about what it does and does not cover.
- **`pipeline/r2_upload.sh`** — takes its file list from `git ls-files`, not from the
  filesystem. Its first version did the latter and uploaded 11,229 deliberately gitignored
  files; the count check caught it because it compares against git rather than against what
  it had just uploaded.

## Known and unresolved

- **`check_lookup_reach` reports one failure**, on `sāmugiya`: the panel draws four
  dictionary tabs and reports its no-entry state in the same breath. **Pre-existing** —
  verified by re-running against the previous build — and unrelated to this release. It is
  not closed and should not be until it is understood.
- **The 118 Unicode PDFs are served from a rate-limited development URL.** Not part of this
  release; recorded in `docs/R2_SETUP.md` with the repair, in order.
- **`?v=WLV` cache-busting is still a human step** with no gate behind it. The bucket's
  `Cache-Control` is deliberately one day rather than one year because of that.

## Provenance, unchanged

Converted from the romanised Pāḷi Series published by the **Ministry of Religious Affairs,
Yangon** (first published 2008; romanised from the Myanmar version of 2001). This is the
official Sixth Council edition, not the VRI / Igatpuri digital edition. Where the two differ,
this project follows the printed edition, and errata are recorded rather than silently
corrected.
