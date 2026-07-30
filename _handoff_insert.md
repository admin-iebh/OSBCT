## NIDDESA — 24Khu07 + 25Khu08 DONE END TO END, ALL THREE GATES (2026-07-26b)

    body          24Khu07  verify_render_vs_pdf.py 24Khu07  4 413 0 212 {4,2,1} -> 0/0/0/0
                  25Khu08  verify_render_vs_pdf.py 25Khu08  5 311 0 335 {4,2,1} -> 0/0/0/0
    apparatus     24Khu07  0 spliced / 0 variants-not-stored / 2 xrefs  (was 0 / 3 / 31)
                  25Khu08  0 / 0 / 0                                    (was 0 / 8 / 0)
    presentation  check_layout.js 24Khu07 25Khu08 -> ok, incipit x1 each
                  node _niddesaverify.js -> 47 / 47
    nav           build_niddesa_nav.py (NEW) -> checked against the edition's own MĀTIKĀ

**THE BASELINE IN THIS FILE WAS INFLATED, FOR THE REASON THIS FILE ALREADY NAMES.**
It recorded 24Khu07 at 140 lines / 153 chunks / 21 rev and 25Khu08 at 116 / 89 / 14,
from the sweep. Over each volume's ACTUAL TEXT EXTENT the starting figures were
**65 / 55 / 21 / 0** and **116 / 89 / 14 / 0**. 24Khu07's sweep range ran into the
printed word index exactly as 22Khu05's and 23Khu06's do — and here for a second,
compounding reason: **the corpus itself captured two pages of that index as
paragraphs** (see below), so `page_range()` had paragraph anchors inside the back
matter and no marker could stop it. Text extents, measured: 24Khu07 ends at pdf
index 413 ("Mahāniddesapāḷi niṭṭhitā."), 25Khu08 at 311 ("Catuttho vaggo." /
"Cūḷaniddesapāḷi niṭṭhitā.").

**THE THREE OPEN QUESTIONS THIS FILE RAISED ARE ANSWERED, AND TWO OF ITS GUESSES
WERE WRONG.**
 (a) **The low paragraph-per-page count is LEGITIMATE — nothing was merged.** A
     numbered unit here is not a verse: it is one Suttanipāta verse quoted as a
     LEMMA followed by its whole niddesa, frequently five or more printed pages
     of prose, closing "Tenāha Bhagavā–" and the lemma repeated. One printed
     lemma per corpus paragraph, shown two independent ways: the PDF sets 210 and
     161 numbered lemmas against 210 and 161 corpus paragraphs, and the
     Suttanipāta's own Aṭṭhakavagga has 210 verses against 24Khu07's n = 1..210
     with no gap. Had this been read as a merge defect the whole volume would
     have been split wrongly.
 (b) **The 21 and 14 `rev` were NOT splices.** They were mid-paragraph corpus
     DROPS (the paragraph jumps, so the rendered block stops matching partway)
     plus, in 24Khu07, the two back-matter paragraphs. Nothing was spliced in
     either volume — `merged` is empty for both.
 (c) **`n_scope` and the verse machinery genuinely do not apply**, as this file
     suspected. `mode: 'niddesa'` in `build_khu_volume.py` replaces them.

**THE BUILDER'S NEW NIDDESA PATH — `mode: 'niddesa'` on a SPEC book entry.**
Gated per BOOK, so the verse path is untouched BY CONSTRUCTION and the
19Khu02/20Khu03/21Khu04/22Khu05/23Khu06 regression is what proves it (run after
every one of the four edits made here; 5 volumes x 5 maps byte-identical each
time, compared BUILDER-vs-BUILDER against `build_khu_volume.py.preniddesa`).
 * **Lemmas pair with corpus paragraphs BY POSITION, 1:1**, `n` kept only as a
   cross-check — the same choice the Jātaka needed and for the same reason (see
   ERRATA). The two sides are independent (printed lemma lines / corpus
   paragraph array), so the pairing is a real check; the builder refuses to
   build the book if the counts differ.
 * **The commentary becomes `after`, split into the PRINTED PARAGRAPHS**, with
   gāthā quoted inside it emitted as `{"gatha": […]}` blocks — a shape the
   reader's `proseOne()` and the harness's `_plist()` already understood. Result
   1,261 + 969 prose paragraphs and 279 + 199 gāthā blocks where the corpus had
   one run-on paragraph per section and no structure at all.
 * **Geometry, measured not assumed** (`nid_items`): indent base+0..2 is prose
   CONTINUATION, base+3..7 a prose PARAGRAPH OPENER or the numbered lemma,
   base+8 and up is display material. `base` is the page's own leftmost indent,
   and a page with no body column at all (25Khu08's last) is read as entirely
   display — the same rule the verse path uses for a page with no verse number.

**25Khu08 IS TWO HALVES AND THE EDITION'S OWN MĀTIKĀ PRINTS THEM AS TWO BLOCKS.**
Pages 1-21 set the Pārāyanavagga TEXT (Vatthugāthā, the 16 māṇavapucchās,
Pārāyanatthutigāthā, Pārāyanānugītigāthā) as plain verse with no commentary;
only from page 24 does the niddesa begin. The first half is ordinary verse and
uses the ordinary verse path (174/174 mapped). Both blocks are headed bare
"Pārāyanavagga", in the mātikā and in the body, so **the nav has two rows with
the same label** — the edition nowhere distinguishes them and inventing
"text"/"niddesa" or "I"/"II" would repeat the Jātaka mistake in reverse. They are
told apart by their children. **RAISE THIS WITH THE USER if the duplicate label
reads badly in the sidebar; it is a deliberate choice, not an oversight.**

**ERRATUM — the edition's own, PRESERVED VERBATIM.** 25Khu08 p229 opens the
Khaggavisāṇasuttaniddesa with **"211."** where the sequence requires 121 (the
previous lemma is 120, the next 122). The corpus reproduces it faithfully
(ord294 carries n=211). Pairing by POSITION places it correctly; a number-keyed
map would have seen an ascent to 211 and then a descent to 122, i.e. a false
segment boundary, and desynced everything after it. Recorded in `ERRATA` and
asserted in `_niddesaverify.js` so a later change cannot silently "correct" it.

**24Khu07's CORPUS HOLDS TWO PAGES OF THE PRINTED WORD INDEX AS PARAGRAPHS** —
ord210 and ord211, 15,000 characters each, book field "Mahāniddesapāḷiyaṁ",
n=130 and n=121, i.e. "Saṁvaṇṇitapadānaṁ anukkamaṇikā". Same class as the
14Sam03#598 back-matter paragraph an earlier session DELETED from the corpus.
Handled differently on the user's decision: HIDDEN via `hide/24Khu07.json`,
because the corpus is no longer edited. **Standing caveat: anything reading
`site/24Khu07.json` directly — a search index, an export, the Unicode-PDF plan —
still sees them.** Worth a scan of the other volumes for the same shape; this is
the second instance found.

**TWO HARNESS DEFECTS FOUND HERE, BOTH AFFECTING ALL 118 VOLUMES.** Backup
`pipeline/verify_render_vs_pdf.py.prehdr2`.
 1. **THE RUNNING-HEADER RULE WAS STATED CORRECTLY AND THEN NOT APPLIED, TWICE.**
    This file already says "a running header in this edition is a TITLE… a
    sentence-ending line is content however reliably it falls at a page top".
    The test was `not (re.search(r'[.?!]\d*$', t) and len(t.split()) > 3)` —
    (i) the `> 3` exempted SHORT sentence-ending lines, and a short sentence is
    still a sentence, so the Niddesa formula "…uddhaṁ adho / tiriyañcāpi
    majjhe." and the Pārāyana refrain "Nā'penti'me Gotamasāsanamhā." entered the
    set; (ii) it tested only SENTENCE punctuation, so a verse PĀDA ending in a
    COMMA — "Yaṁ yaṁ disaṁ vajati Bhūripañño," — entered it too. Every page-top
    occurrence of an absorbed line is DELETED FROM THE PRINTED SIDE, so the
    render then holds content the print appears not to have: on 25Khu08 that was
    4 rendered blocks reported not-in-PDF and 2 reported rendered-too-often,
    every one of them correct. **This is the THIRD time recurring content has
    been absorbed into this set** (Udāna's "udānesi–" lines, then the Apadāna
    refrain), and each earlier fix tightened one axis and left the next open.
    Now: terminal punctuation of any kind means content, no length exemption.
 2. **A LINE GLUED TO THE FOOTNOTE RULE LOSES ONE CHARACTER, AND IT IS THE
    HYPHEN.** `pdf_lines` reads PLAIN pdftotext; 25Khu08 p63 ends its last body
    line "pararūpavedanāsaññāsaṅkhāra-", hyphenated across the break, and plain
    mode swallows that hyphen into the rule's glyph run (`-layout` shows it), so
    `norm()` could no longer rejoin it with "viññāṇaṁ." on the next page. Text
    ending in a WORD CHARACTER immediately against the rule is exactly that case
    — a line that genuinely ends before the rule is separated from it by
    whitespace — so the hyphen is restored. Separately, `pdf_lines` now rejoins
    a line ending in '-' with the next FOR THE LINE-LEVEL DIRECTION TOO; the
    chunk and reverse directions read the list as one joined stream where
    `norm()` already did this, and only the per-line test was comparing the two
    halves as if they were whole words.
 **RE-RUN AFTER BOTH: 18Khu01, 19Khu02, 20Khu03, 21Khu04, 22Khu05 and 23Khu06 are
 all still 0/0/0/0 at minw 4 and 1.** `docs/verify_report.md` predates them and
 its counts move corpus-wide again.

**TWO MORE WRONG-ROLE DEFECTS, EACH CAUGHT BY A REPORT RATHER THAN BY A GATE.**
Both would have shipped at 0/0/0/0 — the text was present and contiguous in each
case; only its ROLE was wrong.
 1. `nid_is_colo` first tested only for an ordinal/completion word, and pulled
    FOUR GĀTHĀ PĀDAS out of the commentary into the colophon stream — 24Khu07
    p227/228 "Diṭṭhī hi tesampi tathā samattā." and p235 "Diṭṭhī hi sā tassa
    tathā samattā." — because *samattā* is also ordinary Pāḷi. A colophon must
    ALSO name a section (niddes|vagg|gāthā|pucchā|pāḷi). Found by reading the
    `--show` listing, which is why that listing exists and should stay.
 2. **A HEADING IS NOT ALWAYS NUMBERED.** 25Khu08 sets three of them bare —
    "Pārāyanavagga" over the whole book and "Pārāyanatthutigāthā" /
    "Pārāyanānugītigāthā" over its last two sections, all three listed in the
    edition's own mātikā. The verse path tested only `HEADNUM`, so all three
    went down the colophon path and rendered as centred closing material after
    the PREVIOUS section. Now recognised by CONTENT as well (`HEADTXT`), as
    every other part of that file already does. Regression re-run: unchanged.

**NAV — `pipeline/build_niddesa_nav.py` (NEW), AND ITS CHECK IS A REAL TWO-INPUT
CHECK.** Shape chosen by the user: book -> vagga -> suttaniddesa, with the
numbered lemma sections in ☰ Contents rather than in the tree — which is also
exactly the depth the edition's mātikā lists and no deeper.

    Mahāniddesapāḷi   1. Aṭṭhakavagga    16 suttaniddesas
    Cūḷaniddesapāḷi   Pārāyanavagga      19 text sections   (the vagga's own text)
                      Pārāyanavagga      19 niddesas, the 19th
                                         (Khaggavisāṇasuttaniddesa) divided into
                                         four vaggas — MIXED DEPTH, the edition's

The tree is built from the headings printed over each section in the BODY, then
checked against the MĀTIKĀ printed in the front matter — a different page, set by
the editors as their own table of contents, derived from neither. It refuses to
write unless every section matches in count and order: 16/16 and 38/38, exact.
Two spellings differ between the two pages and BOTH ARE KEPT as printed —
24Khu07's mātikā sets "Cūḷaviyūhasuttaniddesa" and "Tuvaṭṭakasuttaniddesa" where
the body heads "Cūḷabyūhasuttaniddesa" and "Tuvaṭakasuttaniddesa". The section
colophons add three more of the edition's own variations, all preserved:
"Tassametteyyasuttaniddeso" for Tissametteyya, "Mahābyūhasuttaniddeso" for
Mahāviyūha, and 25Khu08's "Jātukaṇṇi-" for Jatukaṇṇi.

**KNOWN, FLAGGED, NOT GUESSED — 24Khu07's 2 remaining cross-references.** Real
p284 prints "* Dī 2. 33; Ma 1. 225; Ma 2. 292; Saṁ 1. 139 piṭṭhesupi." and
"+ Khu 8. 93, 178; Khu 9. 127, 227 piṭṭhādīsu.". The edition prints the SAME two
references on a neighbouring page in slightly different wording ("…Khu 8.
177piṭṭhesupi.", "…piṭṭhesupi.") and THOSE forms are stored. The cause is
structural and worth recording for the corpus-wide apparatus sweep: a
cross-reference line carries no marker, so `rebuild_apparatus` anchors it to the
first paragraph STARTING on its page — and in a niddesa volume most pages have
none (measured gaps between consecutive paragraph starts in 24Khu07: 1 page 103x,
2 pages 59x, up to 10). Anchoring such a line to the paragraph that COVERS the
page would fix it; that changes anchoring for all 118 volumes and belongs with
the sweep, not here. **And the reader still does not render `xrefs/` at all** —
24Khu07's 309 cross-reference lines across 190 anchors are stored and invisible,
the same standing item as 18Khu01 and 19Khu02.

**APPARATUS REBUILT for both volumes** (`rebuild_apparatus.py --write`; backups
`*.preapp`). 24Khu07: 471 printed notes anchored, 465 structured, 513 variants,
sigla-per-variant 1:355 2:149 3:9. 25Khu08: 547 anchored, 517 structured, 546
variants, 1:456 2:88 3:2. The multi-witness sigla are being parsed here, so
these two volumes have the post-`.prevar` parser and do not need redoing when
the corpus-wide sweep runs.

SUITE RE-RUN AFTER EVERYTHING, ALL GREEN: `_19khu02verify` 53/53, `_apadanafix`
16/16, `_apadanaverify` 15/15, `_booktitleverify` 285/285, `_btrender` 18/18,
`_jatakaverify` 82/82, `_khu01verify` all, `_snverify` all, `_19bleed` no bleed,
`_niddesaverify` 47/47; `check_layout.js` ok on 18Khu01 19Khu02 20Khu03 21Khu04
22Khu05 23Khu06 24Khu07 25Khu08 06Di01 09Ma01 12Sam01 15An01 40Abhi12.
NOTE: the jsdom scripts now need **`node --max-old-space-size=4096`** — the two
new trees push `_apadanafix` and `_booktitleverify` over the default heap. Use
that flag for every `_*.js` from now on.
Reader build bumped to `2026-07-26a-niddesa`. Backups: `site/reader/nav.json.baknid`,
`site/reader/reader2.html.baknid`, `pipeline/build_khu_volume.py.preniddesa`,
`pipeline/verify_render_vs_pdf.py.prehdr2`.

---

