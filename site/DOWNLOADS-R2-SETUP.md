# Hosting the Unicode PDFs on Cloudflare R2

The downloads page (`downloads.html`) lists all 118 volumes and links to the PDFs. The PDFs
themselves are **not** in the site bundle (they're 368 MB) — host them on R2 and point the
page at them.

## 1. Create a public R2 bucket

1. Cloudflare dashboard → **R2** → **Create bucket** → name it e.g. `osbct-pdfs`.
2. Open the bucket → **Settings** → **Public access** → enable **R2.dev subdomain**
   (gives you a URL like `https://pub-xxxxxxxx.r2.dev`). Or connect a custom domain such as
   `files.buddha-dhamma.net` under the same settings.

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

## 3. Point the page at the bucket

Edit `site/downloads.html`, find the CONFIG line near the bottom, and set your public base URL:

```js
const R2_BASE = "https://pub-xxxxxxxx.r2.dev";
```

(or `"https://files.buddha-dhamma.net"` if you connected a custom domain). Save.

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
