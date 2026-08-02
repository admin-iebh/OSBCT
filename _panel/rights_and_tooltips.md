# Tab tooltips and per-dictionary sharing lines — draft for review

2026-08-02. Written for the word-lookup panel. **Nothing here is wired up yet** — this is the
text, for judging, before it becomes strings in `panel.js` and `apd_books` in `build_eval.py`.

Two rules govern every line below.

1. **Principle 2 — flag rather than guess.** A licence I have not confirmed is written as
   *unconfirmed*, not softened into something that reads like permission. Six of these are
   unconfirmed and each says so in the text the reader sees.
2. **§9 — the reader must be able to tell whose voice is speaking.** Every dictionary line ends
   by saying what it is *for*: the Gloss and Abhidhāna tabs carry authority, everything else is a
   reference or a filter.

**Where each string goes.** Tab tooltips are `wl_tip_*` in `panel.js`. The per-dictionary line
belongs in the **build's book table** (`apd_books[id]`, a new `rights` field) and is rendered by
the existing `wl-src` line — *not* in a list inside `panel.js`. That is the invariant that
stopped the panel and the build drifting apart, and adding rights text must not break it.

---

## 1. Tab tooltips

| tab | EN | ES |
|---|---|---|
| **Gloss** | The edition's own glosses — aṭṭhakathā and ṭīkā | Las glosas de la edición misma — aṭṭhakathā y ṭīkā |
| **Abhidhāna** | Tipiṭaka-Pāḷi-Myanmā-Abhidhāna — the Sixth Council's own lexicon, glossed from the aṭṭhakathā and ṭīkā. The one dictionary §9 admits as an authority. | Tipiṭaka-Pāḷi-Myanmā-Abhidhāna — el léxico del propio Sexto Concilio, glosado desde la aṭṭhakathā y la ṭīkā. El único diccionario que §9 admite como autoridad. |
| **APD** | The dictionaries aggregated at dictionary.sutta.org, plus CPED and PPN — one section each, each with its own terms of sharing. Reference, never the panel's voice (§9). | Los diccionarios reunidos en dictionary.sutta.org, más CPED y PPN — una sección cada uno, cada una con sus propios términos de distribución. Referencia, nunca la voz del panel (§9). |
| **DPD** | Digital Pāḷi Dictionary — CC BY-NC-SA 4.0. Evaluation only: §9 excludes it as a voice, and that decision precedes the licence. | Digital Pāḷi Dictionary — CC BY-NC-SA 4.0. Sólo evaluación: §9 lo excluye como voz, y esa decisión precede a la licencia. |
| **PED** *(publishable panel)* | PTS Pali-English Dictionary (Rhys Davids & Stede, 1921–25) — public domain | PTS Pali-English Dictionary (Rhys Davids y Stede, 1921–25) — dominio público |

The Gloss tooltip is unchanged, as you asked — only the tab label moved from *Edition/Edición* to
**Gloss/Glosa**.

---

## 2. Per-dictionary sharing lines

### Confirmed

| dictionary | sharing line (EN) |
|---|---|
| **PED** — PTS Pali-English Dictionary, Rhys Davids & Stede, 1921–25 | **Public domain** by age of publication. Free to redistribute, including commercially. |
| **DPD** — Digital Pāḷi Dictionary, Bodhirasa | **CC BY-NC-SA 4.0** — attribute, non-commercial, share alike. Verified at `github.com/digitalpalidictionary/dpd-db`, 2026-08-02. Used here at build time only; no DPD text is published. |
| **DOP** — A Dictionary of Pāli, Margaret Cone | **© Pali Text Society, in print and on sale.** All rights reserved. May be consulted locally; **may never be published from this site**. Digitisation is partial by letter (m ≈ 2 entries, s ≈ 418) — do not read absence as absence from the work. |

### Unconfirmed — must not ship until settled

Each of these carries the same closing sentence in the reader-facing text: *permission for
redistribution has not been confirmed; shown here for evaluation only.*

| dictionary | what is actually known |
|---|---|
| **Tipiṭaka-Pāḷi-Myanmā-Abhidhāna** — Ministry of Religious Affairs, Yangon; via pm12e.csv 2020-12-09, `bksubhuti/Tipitaka-Pali-Projector` | The Ministry's permission recorded in §2 covers the **Pāḷi Series**. §8 Q6 asks whether it reaches this publication. It has not been answered. Two permissions are needed, not one: the Ministry's, and the pm12e digitisers'. |
| **PEU** — the Abhidhāna's English rendering, StarDict 2024-02-24, encoded by Bodhirasa | Same permission question as the Abhidhāna. 72.2% human translation; the remaining 12,425 entries are Google-Translate and stay behind their own reveal, never mixed into the human text. |
| **CPED** — Concise Pali-English Dictionary, A. P. Buddhadatta | Universally redistributed, no formal licence found. Informal permission is not permission. |
| **PPN** — Dictionary of Pāli Proper Names, G. P. Malalasekera, 1937–38 | PTS. Widely redistributed; the formal position is murky. Not the same case as PED — 1937–38 is not clear of copyright everywhere PED is. |
| **CPD** — A Critical Pāli Dictionary, Copenhagen | Covers a–kh only, unfinished by design. Terms not established. |
| **NCPED / Simsapa Combined** | Derived from the PED/CPED lineage; the derivation's own terms are not established. |
| **Nyanatiloka** — Buddhist Dictionary, Nyanatiloka Mahāthera (PCED "N") | Distributed freely by the Buddhist Publication Society; a specific licence grant has not been located. A doctrinal glossary, not a lexicon. |
| **VRI** — Pali-Dictionary, Vipassana Research Institute (PCED "I") | Terms not established. |
| **TPM** — Tipiṭaka Pāḷi-Myanmar Dictionary (PCED "K", Burmese, Zawgyi→Unicode) | Terms not established. A second, independent copy of the Abhidhāna's digitisation lineage — its value here is as the **verification witness** for pm12e. |
| **PWG** — Pali Word Grammar from the Pali Myanmar Dictionary (PCED "B") | Terms not established. |
| **Roots** — Pali Roots Dictionary, ဓာတ်အဘိဓာန် (PCED "O") | Terms not established. Relevant to step 4, Saddanīti Dhātumālā. |
| **U Hau Sein** — Pāḷi-Myanmar Dictionary (PCED "R") | Terms not established. |

**A note on the PCED dataset as a whole.** `github.com/siongui/pali` and `siongui/data` are
released under the Unlicense — but that covers **siongui's code and compilation**, not the
underlying dictionaries, each of which keeps its own author's rights. An aggregator's licence
never launders its sources. That is why every PCED-derived line above still reads *unconfirmed*.

### The edition itself

| | |
|---|---|
| **The Gloss tab** — Sixth Buddhist Council Tipiṭaka, aṭṭhakathā and ṭīkā, Ministry of Religious Affairs, Yangon | The credits page grants permission to duplicate for **free, non-commercial distribution**. Commercial use is **not** covered and must not be assumed (§2). |

---

## 3. Two things I would not do without asking

**Do not write a licence line for a source that has none.** The temptation with the twelve
unconfirmed rows is to find a form of words that sounds settled. Every one of them should read as
unsettled until someone answers, because the reader of a published site cannot tell the
difference and would be entitled to rely on it.

**"Free to distribute" and "free to publish on a website" are different claims.** §8 Q5 asks the
second question about the edition itself and it is still open. The distribution permission in §2
is what allows the corpus work; it is not yet established that it allows the site.
