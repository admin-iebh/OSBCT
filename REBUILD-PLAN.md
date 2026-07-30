# OSBCT — Full Reader Rebuild Plan

*Prepared for IEBH / BTHAR · Sixth Buddhist Council Tipiṭaka (Chaṭṭhasaṅgītipiṭaka)*

## Objective

Rebuild the reader at **buddha-dhamma.net** into a production, three-layer scholarly reader that carries everything validated in the prototype — three colour-coded trees, top-bar search, the P/A/T layer model, Columns / Tabs / Single views, per-paragraph cite / copy / facsimile, cross-layer jumps, true edition bold, and lemma-outline reading — running against the full 118-volume corpus rather than a single embedded sutta.

Two principles carry over from the whole project: the **base text is never silently altered** (corrections live as overlays), and **display enrichment is derived, never invented** (bold, links, and segments all trace back to the printed edition).

## What already exists (and stays)

The corpus is done: 118 Unicode volumes, 83,751 paragraphs with hierarchy and printed-page anchors, 54,036 variant readings, cross-layer links at ~97.9%, a diacritic-insensitive search index, the ES/EN interface, dark mode, facsimile PDFs on R2, the errata register, the Zenodo DOI, and the Cloudflare + GitHub-mirror hosting. The rebuild reuses all of this; it does not re-do extraction from scratch.

## Phase 0 — Decisions to lock first

A short set of choices shape the data model, so we settle them before building:

1. **Lemma-outline granularity for the Ṭīkā.** The Aṭṭhakathā segments cleanly at sentence-initial lemmata; the Ṭīkā often introduces its term mid-sentence, giving coarser units. Options: accept coarser Ṭīkā units, or invest in a smarter boundary rule. Recommendation: ship the simple rule first, refine later.
2. **Cross-layer jump behaviour.** Switch into a focused Tabs view (current prototype behaviour) versus scroll-in-place within the current view. Recommendation: scroll-in-place when the target layer is already visible, else switch.
3. **Mobile default.** Columns can't fit a phone. Recommendation: phones default to Single/Tabs; Columns is desktop-only.
4. **Commentary segmentation storage.** Keep coarse paragraphs plus render-time outline (simplest), versus pre-segmenting into stored sub-units. Recommendation: precompute lemma-segment offsets in the data so search and citation can address a lemma.

## Phase 1 — Data re-extraction and enrichment — ✅ COMPLETE

Done: render-mode bold extracted across all 118 volumes (477,721 spans, ordinal-keyed, 0 out-of-range, spot-verified); the leading-paragraph linking gap fixed as part of the unique-key link rebuild in Phase 2. Builders saved in `pipeline/` (`extract_bold.py`, `build_links.py`). Original notes below.

This is the only genuinely new data work, and the prototype has de-risked all of it.

**1a. Render-mode bold, corpus-wide.** Run the render-mode-2 extraction (the faux-bold stroke that marks lemmata) over all 118 volumes, positionally aligned to each paragraph's text, storing bold as character-offset spans. Validated at 95% (Aṭṭhakathā) / 99% (Ṭīkā) on Brahmajāla; extraction is fast (~0.03s/page). Handle the two known artifacts: the occasional one-character span boundary, and the ~5% of short paragraphs that don't align (add a fallback matcher and a coverage report).

**1b. Linking fix for leading paragraphs.** The division-based linker drops paragraphs whose `vagga` is `None` because they precede the first heading (this is why Brahmajāla ¶1–2 had no commentary). Add a paragraph-number fallback (sutta + N) for any canon paragraph the division method leaves unlinked, then re-run linking across all volumes and re-measure coverage (expect a rise above 97.9%).

**1c. Lemma segmentation.** From the bold head-lemmata, precompute comment-unit boundaries per commentary paragraph (offsets), powering the expand/collapse outline and making a lemma individually citable.

**1d. Regenerate derived artifacts.** Rebuild the search index, link shards, and apparatus attachments from the updated corpus.

## Phase 2 — Data model and build outputs — ✅ COMPLETE

Done: unique `key` (`<VOL>#<ordinal>`) added to all 83,751 paragraphs and to the search shards; apparatus re-keyed to ordinals and dup-id losses recovered (22,970 entries / 68,412 notes, 1,571 recovered); cross-layer links rebuilt on unique keys (98.0% commentary, 53.2% subcommentary, 0 broken targets), now emitted as **lists** so multiple commentaries/subcommentaries attach; reverse links rebuilt (16,560 targets). New keyed outputs live at `site/reader/apparatus/*.appk.json` and `site/reader/linksk/`. Builders in `pipeline/`. A notable finding: some texts have **more than one commentary or subcommentary** (e.g. Brahmajāla has purāṇa- and abhinava-Ṭīkās) — the reader must render multiple A/T targets. Original notes below.

**Assign a stable unique key to every paragraph — this is now the top structural priority.** Phase 1a surfaced that paragraph IDs are *not* unique: 12,110 collisions across 65 volumes, because the ID is built from hierarchy + number and, where the hierarchy fields are `X` and numbering restarts per section (Abhidhamma enumerations, Khuddaka verse), IDs repeat (e.g. `.../X/X/1` many times). Everything keyed by ID is affected — cross-layer links, apparatus attachment, citations, reader anchors, and search-result jumps — including on the current live site. The rebuild must key every paragraph by something unique (volume + ordinal position is simplest and is already how the Phase 1a bold data is stored), and we should audit each ID-keyed feature on the live site for latent collisions.

Then fix the per-paragraph schema once: unique `key`, `text`, `bold` spans, `links` (A/T with state and target key), `apparatus`, `printed`/`pdf_page` anchors, `peyyala`, and `segments`. Generate the **three colour-coded trees** from the real hierarchy (Tipiṭaka / Aṭṭhakathā / Ṭīkā), keyed to **text names**, not volume codes. Keep the on-demand loading model (per-volume shards) so the reader never embeds the whole corpus — a hard requirement at 118 volumes.

## Phase 3 — Reader rebuild

Port the prototype's interaction model into the production reader, feature by feature, against live data:

- Three-layer colour-coded tree sidebar (text-name navigation) + sidebar hide/show.
- Top-bar global search wired to the real index, with the results dropdown.
- P/A/T layer model with the larger custom tooltips.
- Columns / Tabs / Single, with Single respecting the selected layers.
- Per-paragraph cite, copy, facsimile page (both the horizontal marker and the inline tag), and the P/A/T cross-layer jumps.
- Real bold lemmata from Phase 1a.
- Lemma-outline expand/collapse for long commentaries.
- Footnote apparatus with siglum tooltips.
- Mobile fallback per the Phase 0 decision.

## Phase 4 — Site integration

Fold in the existing site so nothing regresses: the ↩-to-canon back navigation, clickable printed cross-references, the R2 facsimile links, the errata register, the downloads page, the About page, the ES/EN toggle, and dark mode. Carry over the recent reader polish (header no longer wraps A−/A+; enlarged custom tooltips).

## Phase 5 — QA and validation

Before deploy: verify bold coverage and spot-render pages to confirm alignment; re-check linking coverage and zero broken targets; test search across layers; exercise Columns/Tabs/Single on desktop and mobile; and confirm citations, facsimiles, and errata all resolve. Use an automated pass (and a verification subagent for the high-stakes bold/linking numbers) rather than eyeballing alone.

## Phase 6 — Deploy and archive

Stage to a preview, then publish: redeploy `site/` to Cloudflare (apex), push for the GitHub Pages mirror, refresh any changed R2 PDFs, and cut a new **versioned Zenodo release** so the DOI record reflects the rebuild.

## Sequencing and rough effort

Phase 1 (data) is the critical path and the highest-value new work — the bold and linking improvements benefit the existing site too, independent of the UI. Phases 2–4 (model + reader) are the bulk of the build and can proceed once the schema is fixed. Phases 5–6 close it out. A sensible order: **0 → 1 → 2 → 3 → 4 → 5 → 6**, with Phase 1a/1b landing first because they also improve the current live reader.

## Risks and mitigations

The main risk is **alignment drift** on long merged commentary paragraphs during bold extraction; mitigated by the exact-substring positional method (proven character-accurate) plus a coverage report flagging any paragraph that fails to align. The second is **scope creep in the reader**; mitigated by porting only the prototype-validated features and deferring anything new to a later pass. Everything else is well-trodden — the corpus, hosting, and search are already in production.
