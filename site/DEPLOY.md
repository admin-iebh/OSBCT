# Deploying the OSBCT site to Cloudflare Pages

This `site/` folder is a complete, self-contained static site. It needs no build step and
no server — every file is a static asset.

## What's in it

| | |
|---|---|
| `index.html` | landing page |
| `reader/reader.html` | reader with search, cross-layer navigation, variant apparatus |
| `search.html` | standalone search page |
| `<vol>.json` × 118 | paragraph text + structure, one per volume |
| `index/` | search shards + `terms.compact.json` |
| `reader/links/`, `reader/apparatus/` | cross-layer links and variant apparatus |

**468 files, ~310 MB.** Within Cloudflare Pages free-plan limits (20,000 files, 25 MiB per
file). The oversized `terms.json` was deliberately excluded — the site uses the smaller
`terms.compact.json`.

## Option A — dashboard (no tools)

1. Go to the Cloudflare dashboard → **Workers & Pages** → **Create** → **Pages** →
   **Upload assets**.
2. Name the project (e.g. `osbct-tipitaka`).
3. Drag the **contents** of this `site/` folder into the upload area (not the folder
   itself — its contents, so `index.html` sits at the root).
4. Deploy. You'll get a `https://osbct-tipitaka.pages.dev` URL.

## Option B — Wrangler CLI (repeatable)

```bash
npm install -g wrangler        # once
wrangler login                 # opens browser, authorises your Cloudflare account
cd ~/Documents/OSBCT
wrangler pages deploy site --project-name=osbct-tipitaka
```

Re-run the last command to publish updates.

## After first deploy

- **Custom domain:** Pages project → Custom domains → add your domain.
- **The Unicode PDFs are not included** (they'd add ~386 MB). To offer the facsimile
  pages, either add a `pdf/` folder to this site before deploying, or — better for large
  files — put them in Cloudflare R2 and link to them. Each PDF is under the 25 MiB limit,
  so either works.

## Note on the term index

First search loads `index/terms.compact.json` (~17 MB) once. For a production site you may
want to shard it further, but it is within limits as-is and fine for launch.

## Not a substitute for archiving

Per the project's own scope note, hosting needs maintenance. Alongside this deploy, deposit
a versioned snapshot of the corpus (the `corpus/` folder) in a permanent archive such as
Zenodo (issues a citable DOI) or the Internet Archive, so the verified text survives
independently of any running site.
