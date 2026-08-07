# A downloadable package that runs locally — the groundwork, and what is left

**Asked for by the reader on 2026-08-07, to be built later.** This file exists so the
measurements taken that day are not re-derived, and so whoever builds it knows the one way
to get it subtly wrong.

**Wanted:** something a person can download and run on their own machine — the corpus, the
reader, the dictionaries **and the PDFs** — with no network at all.

---

## What already works, measured on 2026-08-07

**Most of it.** The archive fallback added the same day (`site/reader/panel.js`, `jfetch`)
means an unpacked copy of this repository is already a working offline reader.

Served from the **repository root**, all of these answered `200`:

```
/site/index.html
/site/reader/reader2.html
/stores/lookup/index.json
/stores/lookup_eval/dpd/be.json.gz
```

**No CDN dependency.** Every `http(s)` URL in `site/**/*.{html,js,css}` was listed: the only
ones present are self-references to `buddha-dhamma.net`, the PDF bucket, and one example in a
doc. Type is self-hosted (`site/fonts/`). Nothing is fetched from a third party, so the
reader runs with the network cable out.

## The one way to get it wrong, and it is silent

**The server must sit at the REPOSITORY ROOT, not at `site/`.**

`panel.js` is loaded by `site/reader/reader2.html`, so its fallback path `../../stores/`
resolves from `site/reader/` to `/stores/`. Serve `site/` as the root — which is what GitHub
Pages does — and that path cannot climb above the document root. Measured:

| server root | `/stores/lookup/index.json` |
|---|---:|
| repository root | **200** |
| `site/` | **404** |

The failure is the site loading perfectly with **empty dictionary tabs and no error**. That
is the exact silent failure the fallback was written to prevent, reintroduced by launching
it wrongly. **A launcher script is therefore not a convenience, it is the fix.**

**It also needs a real server.** Opening `file://…/reader2.html` will not work: `fetch` is
blocked on file origins. Any static server will do.

## What is missing from the package today

**The 118 Unicode PDFs.** They are not in this repository — they live in the `osbct-pdfs`
bucket, ~386 MB — so a package built from a checkout has a downloads page whose links fail
offline. **The reader asked for the PDFs to be included**, so this is the substantive work,
and it is a size and licensing question before it is a technical one:

- the repository is already ~317 MB as a release zip; adding the PDFs roughly doubles it
- the Ministry's permission covers free, non-commercial distribution — §2 of the project
  instructions says to **confirm it before any public release** and not to assume it covers
  commercial use. A downloadable bundle is a distribution, so that confirmation belongs
  here, not after.

## What building it would involve

1. **`serve.sh` at the repository root** — start a static server *at that level*, open
   `/site/index.html`, and refuse to run if it is invoked from inside `site/`. That last
   part is the whole point.
2. **`OFFLINE.md`** — three lines for a non-technical reader, plus what to do if the
   dictionary tabs are empty (you are serving the wrong directory).
3. **A decision on the PDFs**: bundled (large, needs the permission confirmed), or fetched
   once by a script into `pali-unicode/` etc. where `downloads.html` already expects them.
4. **A gate.** `pipeline/check_archive_fallback.js` already proves the reader finds its
   dictionaries with the origin gone; the missing check is that the *packaged* artefact,
   unpacked into a clean directory and launched by `serve.sh`, does the same — including the
   PDF links if they are bundled.

**Do not build it from `git archive` alone without step 4.** The deposit already carries one
erratum from shipping a tarball nobody unpacked and checked (`docs/DEPOSIT_ERRATA.md`).
