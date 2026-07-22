# Sixth Buddhist Council Tipiṭaka (Chaṭṭhasaṅgītipiṭaka)

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21495339.svg)](https://doi.org/10.5281/zenodo.21495339)

A searchable, cross-referenced **Unicode** corpus of the Sixth Buddhist Council recension of the
Pāḷi Tipiṭaka, together with its **Aṭṭhakathā** (commentaries) and **Ṭīkā** (subcommentaries) —
118 volumes in all.

**Live site:** https://tipitaka.buddha-dhamma.net

A project of the Instituto de Estudios Buddhistas Hispano (IEBH) and Buddhismo Theravāda
México-Hispano AR (BTHAR).

---

## What this is

The source edition (Ministry of Religious Affairs, Yangon; Pāḷi Series, romanised from the
Myanmar-script Sixth Council edition) was distributed as PDFs whose text layer used a legacy
8-bit font (VZTimes) mapped to Latin-1 code points instead of Unicode — so copying *nibbāna*
produced `nibbÈna`. This project converts that legacy text to verified Unicode, extracts the
structure of the edition, links the three layers, and publishes the result as a static website.

Key facts:

- **118 volumes** — 40 Tipiṭaka, 52 Aṭṭhakathā, 26 Ṭīkā
- **83,751 paragraphs**, hierarchically addressed and anchored to printed page numbers
- **54,000+ variant readings** extracted from the footnote apparatus, tagged by witness siglum
- **~94%** of canon paragraphs linked to their commentary (interval model), and onward to subcommentary
- Pages render **pixel-identically to the print** — only the text layer was corrected

The method, verification, and known limitations are documented in [`docs/`](docs/).

## Repository layout

| Path | Contents |
|---|---|
| `site/` | the complete static website (reader, search, downloads, about) — directly deployable |
| `site/index/` | per-volume search shards + diacritic-folded term index |
| `site/reader/` | reader app, cross-layer link shards, variant apparatus |
| `data/` | canonical data: `concordance.json` (volume map), `links_all.json` (all cross-layer links) |
| `pipeline/` | extraction code (`extract.py`); see [`docs/`](docs/) for the full method |
| `docs/` | method and verification reports |

The source and Unicode PDFs are **not** in this repository (public domain; served from Cloudflare
R2 and archived on Zenodo). See `.gitignore`.

## Deploying

`site/` is a self-contained static site. See [`site/DEPLOY.md`](site/DEPLOY.md). In short: it is served
on Cloudflare Pages; the downloadable PDFs are on Cloudflare R2 (see
[`site/DOWNLOADS-R2-SETUP.md`](site/DOWNLOADS-R2-SETUP.md)).

## Source & licensing

**Text.** The Pāḷi text is from the Sixth Council edition published by the Ministry of Religious
Affairs, Yangon, for free distribution as a Gift of the Dhamma. It is treated here as public
domain. *(Confirm the exact terms before any commercial reuse — see the credits notice.)*

**This project's code and data** (the pipeline, the website, the extracted structure, links, and
apparatus) are released under the licence in [`LICENSE.md`](LICENSE.md).

## How to cite

See [`CITATION.cff`](CITATION.cff). A versioned snapshot is archived on Zenodo with DOI
[10.5281/zenodo.21495339](https://doi.org/10.5281/zenodo.21495339).

## Contact

admin@iebh.org · admin@bthar.org
