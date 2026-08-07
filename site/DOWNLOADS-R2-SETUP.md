# Hosting the Unicode PDFs on Cloudflare R2

The downloads page (`downloads.html`) lists all 118 volumes and links to the PDFs, and the
reader (`reader/reader2.html`) links into them page by page. The PDFs themselves are **not**
in the site bundle (they're 368 MB) — host them on R2 and point both pages at them.

> **CORRECTED 2026-08-07, and the correction is the point of this box.** Step 1 of this file
> used to offer the `r2.dev` development subdomain first and the custom domain as an
> afterthought, and step 3 named only `downloads.html`. Both instructions were followed
> exactly, and both produced a defect: the 118 PDFs were served for months over an origin
> Cloudflare documents as **rate-limited and not for production**, and the reader's constant
> was a second copy nobody had been told about. Written up in the appendix of
> `docs/R2_SETUP.md`. **The custom domain is now the instruction, not an alternative.**

## 1. Create the bucket and give it a custom domain

1. Cloudflare dashboard → **R2** → **Create bucket** → name it `osbct-pdfs`.
2. Open the bucket → **Settings** → **Custom Domains** → **Add** → `files.buddha-dhamma.net`
   → **Continue** → review the DNS record → **Connect Domain**. Wait for **Active**.

   The zone must already be in the same Cloudflare account as the bucket — that is
   Cloudflare's rule and it is the one thing that can stop this at the first move.
   `buddha-dhamma.net` is in the account (confirmed 2026-08-07).

**Do not use the R2.dev subdomain**, and do not point a CNAME at one — Cloudflare calls that
an unsupported access path. It is rate-limited, and caching, WAF and access controls do not
work through it. If it is already enabled, leave it running until step 3 is deployed and then
turn it off; disabling it first takes the PDFs off the live site in the interval.

**CORS is not needed on this bucket.** Both call sites are plain `<a href>` navigations, not
`fetch()`, so no preflight ever happens. This is the one place `osbct-pdfs` differs from
`osbct-dict`, where a CORS policy is mandatory (`docs/R2_SETUP.md` step 6). Recorded so that
nobody adds a policy here that does nothing, and nobody assumes one exists.

## 2. Upload the PDFs, preserving folder names

The download links use keys of the form `pali-unicode/06Di01.pdf`,
`atthakatha-unicode/07DiA01.pdf`, `tika-unicode/08DiT01.pdf`. So upload the three
`-unicode` folders **keeping their folder structure**.

Dashboard: R2 bucket → **Upload** → drag the three folders
(`pali-unicode`, `atthakatha-unicode`, `tika-unicode`) from `~/Documents/OSBCT`.

Or with Wrangler (faster for 118 files):

```bash
cd ~/Documents/OSBCT
for d in pali-unicode atthakatha-unicode tika-unicode; do
  for f in "$d"/*.pdf; do
    wrangler r2 object put "osbct-pdfs/$f" --file "$f" --remote
  done
done
```

## 3. Point the pages at the bucket — BOTH of them

There are **two** constants, in two files, and they must always name the same origin:

| file | line | constant |
|---|---|---|
| `site/downloads.html` | ~65 | `const R2_BASE = "https://files.buddha-dhamma.net";` |
| `site/reader/reader2.html` | ~395 | `const R2='https://files.buddha-dhamma.net';` |

`reader2.html` was missing from this list until 2026-08-07, which is how it came to sit on a
different instruction from the page beside it. Change one and not the other and the downloads
page is healthy while every `p. ⧉` link in the reader points at the old origin — or at nothing,
once that origin is turned off. `pipeline/check_pdf_origin.js` now compares the two constants
on every run, so the drift cannot repeat silently.

## 3a. Run the gate before you deploy, and again after

```
node pipeline/check_pdf_origin.js https://files.buddha-dhamma.net
```

Run it **before** the edit in step 3 — it reads the current origin out of `downloads.html` and
compares the two hosts byte for byte, so once the constant is changed there is nothing left to
compare against. It probes all 118 objects for the things that fail quietly: `Content-Type`,
`Content-Disposition`, Range support and size. Every one of those can be wrong while the link
still returns HTTP 200 and a file, and the reader lands on page 1 of a 400-page volume instead
of the passage he clicked.

`node pipeline/check_pdf_origin.js --selftest` proves the gate itself against a local stub
before you trust it against the bucket.

**Only after step 4 is deployed and you have opened a PDF from the new domain on the live
site**: bucket → **Settings** → **Public access** → disable the **R2.dev subdomain**.

## 4. Re-deploy the site

The site bundle changed (dark mode + downloads page), so redeploy it:

```bash
cd ~/Documents/OSBCT
wrangler pages deploy site --project-name=osbct-tipitaka
```

or drag the `site/` folder contents into the dashboard uploader again.

## Notes

- Each PDF is under 10 MB; R2 has no per-file issue at this size.
- R2 storage for 368 MB is well within the free tier; egress from R2 is free.
- Until `R2_BASE` is set, the downloads page shows a banner and the PDF buttons are disabled —
  the rest of the site is unaffected.
