# START HERE — 2026-08-08 pm

## STATE AS OF v2.6.0 (2026-08-08, end of the second long session)

v2.5.0 AND v2.6.0 both released, deposited, DOIs recorded (…21853330,
…21855790), site live.  Done since this file was written: the whole search
arc (multi-word, wildcard, layer chips, per-layer caps, ordering, bucketed
term index BOTH halves), the APD gear + summary line, DPD refreshed to
2026-07-28 with family tables WORKING (store rebuilt from the reader's
GoldenDict folder, mounted at ~/GoldenDict/dpd), vatthu heads golden (data
fix), fix_vagga_heads on all remaining volumes (212 heads, census empty),
version chip on every page with hover/tap popover date.  Gates:
check_search.js 40, check_apd_gear.js 27, both green; every one shown to
fail on the build that had its bug.

**REMAINING, in the reader's chosen order (links LAST):**
 1. Parked display decisions (reader's): verbatim-repeat display
    (5,376 of 22,527), `none` vs `dim`, capping the concordance tooltip.
 2. Search heavy half (per-volume shard split into postings + text) — ONLY
    if the reader's live-network verdict says common-word searches hurt.
 3. ~~The hyphen repair~~ **DONE, both sessions, 2026-08-08 late**: the
    matcher's third join candidate broke the §11.3 blocker (hy2/FINDINGS
    §11.6), then the corpus-wide apply as one operation — 7,291 deletions,
    127,867 bold spans + 7,548 pbreak offsets shifted (the dimension the
    08-05 audit predates; all 101 volumes re-derived from the printed page
    and byte-EQUAL to the shift), search index re-emitted, bold baseline
    moved deliberately: **+42,343 lemmas drawn (339,569 → 381,912), losses
    in NO volume**.  Remaining from that family: the consonant branch
    (1,521, ca-saddo class, unadjudicated per hy2 §2), extract.py:204
    hygiene, and the ~17% undrawn bold spans still unexplained (now
    smaller — remeasure before believing the number).
 3b. **ITALICS REMOVED (2026-08-08 late, reader's decision made total by
    census)**: no italic face exists in any of the 118 PDFs; .gatha,
    .incipit, .udd-verse, .gatha-count dropped, .appx i pinned normal.
    **HOMAGE UNIFIED AT THE DRAW**: 12 printed variants across 211 homages
    (census re-run CASE-BLIND after the reader caught `Namo Tassa` — a
    case-sensitive census of a capitalisation question), all verified at
    their printed pages, errata E068-E077; corpus and incipit maps keep
    the print; homageNorm draws the official line at every book head.
 4. ~~Housekeeping~~ **MOSTLY DONE 2026-08-08 late**: checkout@v5 (Node
    24); `Ekaṁ nāma kintipañhavaṇṇanā` in the nav at #174 via rebuild
    (which also dropped two GHOST nodes whose heads left sections/, and
    corrected Nigamanakathā to #668); `claude/` reconstructed from the
    surviving records, marked as such; baselines audited — links,
    concordance, ordinal, fn-markers ALL "no measure regressed".
    **Remaining in this bucket:** the NINE kintipañha heads still tail-of-
    paragraph (the deferred corpus split, 2026-07-28r — the two dropped
    gāthā heads are the same family); check_derived's flag — the legacy
    links artifact is loaded by nothing: reader to decide retire vs
    rebuild; BLOCKBREAK off; `position` unmeasured for 114 volumes; the
    WLV gate; the offline package (§2 permission first).
 4a2. **E021 RESOLVED 2026-08-09 pm — NOT AN ERRATUM, NOTHING APPLIED.**  The
    x in 10Ma02 ¶296 (`jānāsi, x maraṇenapi`, printed p.247, pdf p.253) is
    SET IN PRINT: the edition's own unnumbered position siglum, paired with
    the `+` eleven lines below, both keying the one foot-note (vākyadvayaṁ …
    dutiyaṭṭhāne yeva dissati).  Corpus preserves both marks; register entry
    now category=not_an_erratum, status=resolved, with TWO superseded
    suggestions recorded (the original deletion; this session's `( )`
    reading, which belonged to the different omission site at ¶295 printed
    p.246 — corpus already correct there).  LESSONS: (1) the first
    page-match is not the right page-match — MN 82 repeats the speech, and
    the `( )` evidence came from the wrong occurrence until pbreak said the
    offsets disagreed; (2) a census glyph can be the EDITION's mark — which
    is exactly what the ~110-glyph visual review sheet exists to catch, so
    this strengthens the case for ordering it.  OPENED, NOT CLOSED: the `+`
    note is ABSENT from the live apparatus (10Ma02.app.json has no key for
    ¶296; text survives in `_xc/hy1/blocks*/10Ma02.json`), and unnumbered-
    siglum notes elsewhere are GLUED onto numbered notes (¶295 app note 2
    carries the `( )` note appended).  Extraction class.  Measure the
    unnumbered-siglum classes (`*`, `+`, `x`, `( )`) corpus-wide before any
    repair.  Stamp 963375c10f40 → f078d6411162; commit message in
    `COMMIT_MSG_e021.bak`.
 4a3. **BOTH INSTRUMENTS BUILT AND RUN, 2026-08-09 pm (same session).**
    (1) `pipeline/build_glyph_review.py` → `_review/glyph_review.html`:
    50 sites (41 register glyph candidates + 9 sidecar/control/vocab
    extras; the "~110" above was stale), ALL 50 located with printed-page
    clips in `_review/clips_b/`, three-way verdicts + JSON export, nothing
    applied from the sheet.  Every context-carrying page is rendered, not
    the first match — X009 (27Khu10 `q`) draws both p.146 and p.206, and
    its clip already settles it: print reads `Ḍahantaṁ` (pdftotext decoded
    the byte as `q`; glyph-free needles catch this decoder-divergence
    class).  Page-number entries (E063/E064/E066) and homages (E068–E077)
    are glyphless, other classes, excluded.  **AWAITS THE READER'S
    VERDICTS** — export JSON from the sheet, then apply confirmations by
    the E035/E021 precedent.
    (2) `pipeline/measure_sigla.py` (selftest: both witnessed 10Ma02 cases
    must report as witnessed): `( )` 188 marks / 28 in paragraphs with NO
    apparatus entry; `+` 597/298; `*` 3,470/2,067; `x` 1/1.  2,535 marked
    paragraphs in 76 volumes, 1,427 without any apparatus entry.  "Entry
    present" deliberately does NOT claim the symbol's note is inside
    standalone — the ¶295 gluing needed the printed page.  Spot-checks:
    paragraph-initial `*`/`+` are the also-at cross-reference class; some
    `( )` carry a trailing NUMBERED marker (`( )2`) whose note travels the
    numbered path.  Detail `_review/sigla_report.json`; commit message
    `COMMIT_MSG_review.bak`.  HAZARD RECONFIRMED: repo files cannot be
    deleted from the sandbox — `_review/clips/` (first run, superseded by
    `clips_b/`) needs host deletion.
 4a4. **READER'S VERDICTS RECEIVED AND PERSISTED (2026-08-09 pm, end of
    session) — NOT YET APPLIED.  START THE NEXT SESSION HERE.**  49 of the
    sheet's 50 sites judged (X007 unanswered); raw export in
    `_review/verdicts_2026-08-09.json`; the joined apply table with the
    printed-page adjudications in `_review/apply_table_2026-08-09.json`.
    CONVENTION MEASURED ON E035 BEFORE ANY WRITE: `corpus/*.txt` KEEPS the
    printed (corrupt) reading by principle 3 — application means
    `site/<vol>.json` + derived stores, AND the pair must land in
    `data/glyph_errata.json` (182 entries, 67 with pairs, applied at build
    time) or the next rebuild regresses it.  CLASS A, 37 rows: the served
    text ALREADY carries the reader-confirmed reading — what remains is
    register status=confirmed + application notes, no text change.  CLASS B,
    12 rows (E002 E005 E011 E018 E034 E037 E038 E039 E042 E043 E044 E049):
    the quick probe could NOT confirm the current site reading — E042 shows
    a real THIRD reading (site `…vaḍḍhanī` vs reader `…vaḍḍhane`); each
    needs its own look before writing.  Adjudications made against the
    printed page and recorded in the apply table: ṭṭh restored where the
    register's suggestion carried a ṭth slip (E002 E030 E031 E041; E055 the
    reader caught himself); edition's ṁ over the reader's ṃ (E034 X003
    X009); ṇ in the 08DiA02 `n\x8f`→`ṇa` class incl. X002 X006 (print shows
    the displaced-dot nạ, same page prints Buddhañāṇassa); print's hyphen
    kept in Rāhu-asurindo/-aṁ (E011 E017); Ḍ capital in X008 Ḍayhantu (a
    BOLD lemma — E031 is too).  All 49 pairs are Δ0 except E044/E055 (+1 —
    offset shifting needed there).  X-rows need NEW register entries
    (E078+); X007 stays a sheet row only.
 4a4b. **VERDICTS APPLIED 2026-08-09 (next session).**  39 register entries
    candidate → confirmed (register now 47 confirmed / 20 candidate / 1
    resolved), each noting that the served text already carries the reading
    via `data/glyph_errata.json`, applied over the PDF text layer before
    extraction.  ELEVEN suggested readings were WRONG in the register and are
    corrected against the printed page with the superseded reading kept —
    the ṭth slips (E002 E030 E031 E041 E055), E006 `passimi`→`passāmi`,
    E033 `paveṇenti`→`pavesenti`, E034 `patimaṇḍitaṁ`→`paṭimaṇḍitaṁ`, E036
    `Aujalī`→`Añjalī`, E011/E017 printed_reading widened to the whole
    hyphenated word.  The applied PAIRS were right throughout; the
    register's summary of them had rotted.
    **THE CLASS A/B SPLIT DID NOT SURVIVE RE-MEASUREMENT:** 10 of the 12
    class-B rows measure like class A — the earlier probe matched the
    reader's typed string, not the adjudicated one, so ṃ/ṁ and ṭth/ṭṭh read
    as failures to locate.  **E044 SETTLED** against the printed page and
    the sheet verdict superseded (the edition prints the parallel member of
    the same sentence `“maman”ti mānavinibandhā diṭṭhi`, with the space;
    three more agree in 26Khu09) — left `candidate` for the reader's word.
    **E042 STILL OPEN, three readings:** applied `vaḍḍhanī`, reader
    `vaḍḍhane`, printed `vaḍḍhaní`; the applied pair is an inference, not a
    witness (`í` is a one-place glyph and the register says so), and the
    neighbouring codepoints resolve two ways each.  **SETTLED BY THE READER
    THE SAME DAY: `vaḍḍhane`.**  The applied pair is changed and the
    superseded `vaḍḍhanī` kept with the reason it fell.  ONE word of served
    text moved, Δ0 in characters — site/25VsmT01.json, the volume index
    (display form AND folded key — the first sweep missed the folded one),
    the verse store, terms.compact, its bucket, five lookup stores; pbreak
    re-derived BYTE-EQUAL, pagespan rebuilt.  **E044 confirmed by the reader
    as the applied pair reads** (`“maman”ti mānavinibandhā diṭṭhi`, with the
    space).  Register now **49 confirmed / 18 candidate / 1 resolved**.
    **THE NINE X-ROWS ARE NOT ERRATA — no E078+ opened.**  The Unicode PDFs
    read correctly at every one; the corrupt forms live only in `corpus/`,
    gitignored, last written 2026-07-29, whose `*.errata.json` sidecars (the
    sheet's own input, `build_glyph_review.py:73`) are dated 2026-07-21.
    See `claude/x_rows_are_a_stale_snapshot.md`, which also CORRECTS this
    file's stated convention: `corpus/*.txt` keeps the corrupt reading
    because it is stale and unpublished, **not** "by principle 3".
    **OPEN, for the reader:** stop `corpus/*.errata.json` feeding the review
    sheet, or the next sheet re-raises these nine; and X007 is now suspect
    for the same reason — check it against the live PDF before asking again.
    `glyph_errata.json` entries UNCHANGED (182, verified byte-equal);
    proposals corrected (`ó` is 7/8, not 7/7 — 18AnA02 has carried `fix='s'`
    all along while the summary claimed `ṇ`) and a `displaced_dot` class
    recorded.  Stamp `361c9aa7c2d9 → e72ad62629c1`; commit message
    `COMMIT_MSG_verdicts.bak`.
 4a5. **v2.7.0 BUMPED (this session): all three checklist files** —
    `.zenodo.json` (version + New-in paragraph), `CITATION.cff` (version,
    date-released 2026-08-09), `site/i18n.js` (OSBCT_VERSION) — stamp
    `f078d6411162 → 361c9aa7c2d9`.  TAG NOT CUT — the reader cuts it LAST
    on the host after commit+push; DOI to be added to CITATION.cff after
    Zenodo mints it.  Commit message `COMMIT_MSG_270.bak`.
 4b. **CORRECT THE PDFs FROM THE ERRATA REGISTER (reader, 2026-08-08) —
    PDF SIDE ON STANDBY (reader, 2026-08-09); the SEVEN CONFIRMED WORDS
    ARE APPLIED TO THE CORPUS.**  Shown the seven belief-only corrupt
    words, the reader confirmed six and CORRECTED one: `Kumbhizādīsupi`
    = `Kumbhi ādīsupi` (z is a SPACE, not l; register note records the
    superseded suggestion).  All seven applied — corpus, verse stores,
    idx shards, terms.compact, buckets, demo-links — every replacement
    length-preserving, so pbreak re-derived byte-EQUAL (sidecar hashes
    refreshed, pagespan rebuilt, stamp 963375c10f40).  Register entries
    status=confirmed with the application noted.  LESSON BANKED: a dead
    term prefix leaves a stale bucket; build_term_buckets.py now empties
    orphan buckets itself.  What REMAINS of 4b: the per-entry audit of
    the 22 other-layer entries, the ~110 single-witness glyph visual
    review sheet (offered, not yet ordered), and the PDF correction
    itself (ToUnicode injection, one volume first) — ON STANDBY.
    docs/PDF_ERRATA.md (generated from data/errata.json — 68 entries, 39
    volumes; regenerate with pipeline/build_pdf_errata_doc.py) is the work
    list.  MEASURED state of the register vs the corpus: 31 glyph-class
    entries are corrected IN THE CORPUS with attribution (the
    apply_from/apply_to mechanism); 14 preserved as printed (wrong ¶
    numbers, the homage variants — display-normalised only); 22 live at
    other layers (sections/ headings, incipit maps) and need a per-entry
    audit before anything else.  PDF correction itself connects to the §6
    scope decision (ToUnicode injection preferred, one volume first), and
    every candidate stays pending scholarly confirmation.
 5. **THE LINKS (postponed by the reader, deliberately last):** the three
    placer recommendations (block applying 20Khu03 vaggas 2–42, which sit
    computed in `_xc/linksk_toc/`), the shadowing defect FIRST, the
    verbatim-repeat target measure, the three inversions, spot-check
    against the printed page, the concordance gate; and the assessment of
    2026-08-09[read: 08-08]: a printed-page ground-truth sample and
    provenance tiers in the UI are what turn "accurate" into a number.

<!-- Supersedes start_here_2026-08-08.md, which is still correct about everything
     except its open item 1b (the apparatus half is DONE and its diagnosis was
     wrong) and its open item 1 (evidence gathered, decision still the reader's).
     Read §State, then §"Next, in order". -->

## State

**Done, not yet committed: the footnote markers, twice over.**
`pipeline/check_fn_markers.js` carries two assertions; all 118 volumes green on
both; the selftest catches the injected defect on both.
BUILD `6151ac21bbbd` → `ab3632cc3580`. Commit message in `COMMIT_MSG.bak`.

  1. **Markers lost to the bold lemma** — 3,480 of 70,598 (4.93%).
  2. **Markers after a closing bracket** — 684 more, `)` 433, `”` 237, `’` 14,
     which the letter-only class could never see. Reader's own example proves
     the rule: `gāthamāha)`³ carries `( ) natthi (Sī)`, and the parenthesis the
     marker stands after IS the parenthesis the note calls absent.
  3. **The note made reachable from the marker** — ord 210 is 19,871 characters
     and its note block sat six screens below the marker. Tooltip on each
     marker. Pairing is positional and claimed only where the marker count and
     the note count agree (45,901 of 69,000, 66.5%); otherwise every candidate is
     shown and the tooltip says the pairing is not established.
  4. **Each printed page's notes drawn at the foot of that page** — which is
     where the edition sets them, and the reader's third report was that they
     were not there. Ord 210 spans SIXTEEN pages, 146–162, and every note sat in
     one block at the end. The page is derived from the MARKER's offset against
     `pbreak/`, because the apparatus data carries no page: `<vol>.app.json` is
     keyed `Work/X/X/<paragraph number>`. **45,901 of 73,431 notes (62.5%)**
     placeable; on paragraphs that actually cross a break, 30,124 of 54,426
     (55.3%). The rest stay in the end-of-paragraph block.

  5. **The opening quote moved to the page it opens** — `pbreak` cut between the
     `“` and `Diṭṭho`, stranding a quote mark alone at the foot of p. 146. The
     PRINTED page settles it: pdf 154 opens `“Diṭṭho hi me”ti`. **1,562 of
     35,043 mid-paragraph breaks (4.46%)** land after an opening mark — 1,459
     `“`, 62 `(`, 41 `‘`. Seven of ten random cases resolved against the PDF, all
     seven with the quote on the new page, none against.

  6. **The bold lemmas the reader found missing** — `Buddhavīrā`, `Namo
     tyatthū`, `Sabbasattānamuttamā`, `yo maṁ dukkhā pamocesi…`, `sabbadukkhan`,
     all on ONE drawn line that failed to locate over one line-break hyphen:
     corpus `…vīriya- nipphattiyā` against drawn `…vīriyanipphattiyā`. The locate
     retries against the joined text and DRAWS the joined text with spans
     remapped, so no hyphen reaches the page. **Five volumes, 31,391 spans:
     25,233 drawn (80.4%) → 26,053 (83.0%).** Ord 210 draws all 41.

**The gate now carries four assertions**, and the third found a defect the
moment it existed: four volumes drew MORE note rows than the data holds, because
`pbreak` can name the same page twice and the foot was emitted twice. A page is
spent once drawn. The fourth is a TWO-SIDED bold baseline,
`pipeline/bold_baseline.json`, 118 volumes, **339,569 lemmas**, failing on any
change in either direction — verified to bite by moving one entry by 5.
All 118 volumes: **55,453 notes, 55,453 rows**; 50,239 markers backed by a note,
50,239 carrying it.

**Unchanged: `_xc/linksk_toc/20Khu03.links.json`** still holds vaggas 2–42 →
`33KhuA14`, still NOT applied. Nothing was written to `site/reader/linksk/`.

## THE APPARATUS ITEM IS CLOSED, AND THE 08-08 HANDOFF DIAGNOSED IT WRONG

The handoff said "establish whether the A band renders apparatus at all or only
the canon layer does". It renders it everywhere. Measured in the real reader:
`31KhuA12` 111 paragraphs whose data carries notes, 111 that drew the `.appx`
block; `32KhuA13` 125 of 125; `09DiT02` 62 of 62; every band, every layer.

What was actually missing was the MARKER — the digit glued to the annotated
word. Five call sites assembled the HTML and then ran `([letter])(\d{1,2})` over
it, and a bold lemma ending on the annotated letter broke the adjacency:
`<b class="lemma">Apadāne</b>2`. **3,480 of 70,598 markers, 4.93%**, 1,817 ṭīkā,
1,494 aṭṭhakathā, 169 canon — which is exactly where the reader met it and
exactly why it looked inconsistent inside one paragraph.

The handoff's own example was right and its reasoning was not: `31KhuA12` ord 210
DOES carry seven notes and DID draw them; what it did not draw was
*Apadāne*<sup>4</sup>. **Reading the source instead of rendering it is what put
the diagnosis one layer away from the fault.** Run the instrument against the
build that has the bug.

## THE ORDINAL-WORD SPAN — EVIDENCE GATHERED, DECISION NOT TAKEN

Set aside when the reader redirected to the apparatus. The measurement stands
and it says the reader was right on 08-07.

`33KhuA14` ords 561–569 are the whole of commentary vagga 40, printed pp. 202–205.
Read them straight through:

    561  (no n)  Cattālīsamavagge apadāne ... Pilindavacchattherassa apadānaṁ.  [intro]
    562  n=1     1. So ekadivasaṁ Satthu santike ...                            [gloss]
    563  n=3     3. Bahū me'dhigatā bhogāti ...                                 [gloss]
    564  (no n)  Dutiyatatiyacatutthapañcamāpadānāni UTTĀNĀNEVĀTI.              [dismissal]
    565  (no n)  Chaṭṭhāpadāne ... Bākulattherassa apadānaṁ.                    [intro]
    566  n=386   386. So arahā hutvā ...                                        [gloss]
    567  (no n)  Sattamāpadāne ... Girimānandattherassa apadānaṁ.               [intro]
    568  n=419   419. So arahattaṁ patvā ...                                    [gloss]
    569  (no n)  Aṭṭhamanavamadasamāpadānāni UTTĀNATTHĀNEVĀTI.                  [dismissal]

The placer currently produces, for vagga 40, **2 links by number and 132 by
ordinal word** — and the 132 land like this:

    ord 564  ← 33 canon paragraphs   "the 2nd, 3rd, 4th and 5th are self-evident"
    ord 565  ← 33 canon paragraphs
    ord 567  ← 30 canon paragraphs
    ord 569  ← 36 canon paragraphs   "the 8th, 9th and 10th are self-evident"

**69 of those 132 links point at a one-line sentence saying the commentary has
nothing to say.** `uttānāni eva` is the edition declaring silence, and the
placer is reading the declaration as a gloss. A reader who clicks is shown
"these are plain".

So the ordinal-word paragraphs are TWO kinds and the code treats them as one:

  - **intro** (561, 565, 567) — names the apadāna, quotes its opening words
    (`nagare Haṁsavatiyāti-ādikaṁ`), tells the elder's story. Real commentary,
    but on the apadāna's OPENING, not on all 257 of its verses.
  - **dismissal** (564, 569) — `uttānāni eva`, `uttānatthāni eva`. The opposite
    of a gloss. These should place NOTHING and their canon span is
    `not_commented`, which is what the edition says in so many words.

**A second defect, found in the same measurement and not in the handoff:** the
ordinal-word candidate SHADOWS the numbered one, because `place()` takes
`cand[0]`, the earliest candidate at or after the floor, and the intro sits
before the numbered gloss. Vagga 40 escapes it only because `Cattālīsama-`
(fortieth) is above the `v <= 12` cut in `APOS` and so ord 561 places nothing.
Where the intro IS matched, canon 1 and canon 3 would both land on the intro and
the paragraphs the edition itself numbers `1.` and `3.` would never be reached.
**Look for this before changing anything else: it moves links off paragraphs the
edition addressed by number, which is the strongest evidence there is.**

Recommended, for the reader to accept or refuse:

  1. an ordinal-word paragraph whose opening is a `uttāna-` dismissal places
     nothing, and its canon span is `not_commented`;
  2. an ordinal-word intro places only the FIRST canon paragraph of the apadāna
     it names — the one whose words it quotes — not the whole span;
  3. a numbered candidate beats an ordinal-word candidate for the same n,
     whatever their order.

All three REDUCE the link count, which is the direction §"SANDHI COST THREE
SEPARATE FIXES" warns about — so measure before and after, and check the drop
lands on the paragraphs above and nowhere else.

## Next, in order

0. ~~**The reader asked for the SEARCH BOX next**~~ **DONE 2026-08-08 (search
   session), not yet committed** — all three asks; see the DONE block at the top
   of **`_xc/hy2/start_here_search.md`**, commit message in
   `COMMIT_MSG.bak`, gate `pipeline/check_search.js` (selftest fails 7/10
   on the pre-fix build). BUILD `ab3632cc3580` → `3bcc7431b9a5`. Left open:
   `search.html` drift (one word only, naive `book` field).

0b. ~~**THE VATTHU NAMES ARE STYLED DIFFERENTLY**~~ **DONE 2026-08-09, the
   printed page settled it.**  pymupdf over the PDFs: the edition sets
   `1. Cakkhupālattheravatthu` IDENTICALLY in 18Khu01 (pdf p.38) and 21KhuA02
   (pdf p.9) — 12pt centred — and in the canon it is typographically EQUAL to
   `1. Yamakavagga`.  So the DATA was fixed, not the CSS:
   `pipeline/fix_vatthu_heads.py` (fix_vagga_heads idiom) reclassified
   18Khu01's 304 heads vatthu→sutta; 19Khu02's ~36 vatthu-kind heads are
   DELIBERATE sub-series demotions (build_19khu02_nav.py) and the script
   refuses that volume.  Plus 3 headless uddana entries corpus-wide given
   hk=sutta (one Dhp vatthu drawn via uddana/, two Jātaka titles in 22Khu05).
   Verified rendered: zero `.head.vatthu` in 18Khu01, both layers golden.
   Reader confirmed direction on return ("most of the titles are golden").
   Original report kept below for the record: "in the Dhammapadapāḷi the names
   like `1. Cakkhupālattheravatthu` and so on shouldn't be golden colour like
   in other places like in its commentary?"

   **MEASURED — the two layers carry different head kinds for the same name:**

       18Khu01  (canon, holds Dhammapadapāḷi)   book 52, vagga 10,
                                                sutta 265, **vatthu 304**
       21KhuA02 (Dhammapada-aṭṭhakathā I)       vagga 8,  sutta 95,  vatthu 0
       22KhuA03 (Dhammapada-aṭṭhakathā II)      vagga 18, sutta 211, vatthu 0

   `reader2.html:1519` maps `HCLS={book:'sutta', vagga:'vagga', sutta:'section',
   vatthu:'vatthu'}`, and the CSS at :182-183 gives

       .head.section  font-size:14.5px  color: var(--accent)     <- GOLDEN
       .head.vatthu   font-size:13px    color: var(--mut)        <- muted grey

   So `1. Cakkhupālattheravatthu` is muted in the canon and golden in the
   commentary, and the ONLY reason is that the extraction assigned a different
   `hk`. The commentary volumes carry no `vatthu` kind at all — every vatthu
   name in them falls through as `sutta`.

   **This is the same shape as the open item at §"Errors in earlier work" 4** —
   "258 heads in 18 volumes name a vagga but are classified `sutta`, because the
   extraction takes a head's kind from typography and the PDF does not centre
   them". Same cause, different symptom: a head's LEVEL is being inferred from
   how it was set, and the two layers were set differently.

   !!! DO NOT SIMPLY RECOLOUR ONE OF THEM. Which is right is a question about
   the PRINTED PAGE — how the edition sets these names in `18Khu01` against how
   it sets them in `21KhuA02`/`22KhuA03`. Extract both from the PDFs and compare,
   the way pdf page 154 of `31KhuA12` settled the stranded quote. If the edition
   sets them alike, one layer's `hk` is wrong and the DATA should be fixed, not
   the CSS. If the edition really does set them differently, then the reader is
   faithful and the question is whether we want to be.

   **AND ASK THE READER WHICH DIRECTION HE MEANT.** His sentence can be read as
   "they should be golden here too" or as "they should not be golden anywhere".
   Do not guess; a wrong guess here silently restyles 304 heads in the canon or
   306 in the commentary.

1. **The three recommendations above**, as the reader decides them. Still blocks
   applying vaggas 2–42.
2. **The verbatim-repeat link target** — the other defect the reader found on
   08-07, untouched. `19Khu02` ord 3294 → `31KhuA12` ord **207**, which is the
   canon verse repeated, where the gloss is ord **210**. Record carries
   `by: None`, so it is an old-builder link. **Measure how many of the 5,376
   verbatim repeats are link targets before deciding.**
3. **The three inversions** (vaggas 18, 34, 35).
4. **Spot-check against the printed page** before applying —
   `_xc/hy2/20Khu03_vaggas2-42_dryrun.md`.
5. **The concordance gate** when vaggas 2–42 land. Reader's decision, not taken.
6. ~~**`fix_vagga_heads.py` on the other 17 volumes**~~ **DONE 2026-08-09**:
   16 volumes, 212 heads (census had tightened since the 258/18 count),
   applied one run each, census now empty.  Rendering verified (`head vagga`
   in the real reader), `check_links.py` "no measure regressed".  The placer,
   when the links work unparks, now runs against sound vagga boundaries.
7. **Audit the remaining `pipeline/` baselines for drift.**
8. **`20KhuA01` ord 174** carries a section head the nav does not.

## THE BOLD LEMMAS — FIXED FOR THE HYPHEN CLASS, ~17% STILL UNEXPLAINED

Reader, 2026-08-08: "in the phrase *Tattha Buddhavīrāti* **Buddhavīrā** should be
bold ... also *Namo tyatthū* ... and *Sabbasattānamuttamā* and *yo maṁ dukkhā
pamocesi, aññañca bahukaṁ janan* and *sabbadukkhan*. I wonder if there are other
bolds missing."

There are, and every one he named is on ONE drawn line.

**The spans are all present in the data.** `bold/31KhuA12.bold.json` ord 210
carries 41 spans including `(120,130) Buddhavīrā`, `Namo`, `tyatthū`,
`Sabbasattānamuttamā`, `yo`, `maṁ`, `dukkhā`, `pamocesi`. Nothing is missing from
the extraction. What fails is the LOCATE: the verse branch draws the printed line
stream and finds each drawn line in the corpus paragraph by `indexOf`, and this
line is not found.

**The cause is the unrepaired line-break hyphen** — the open item the previous
handoff lists as "the hyphen repair (8,790 words, 109 volumes)". At character 125
the corpus text reads `catubbidhasammappadhānavīriya- nipphattiyā` and the drawn
line reads `catubbidhasammappadhānavīriyanipphattiyā`. One hyphen, and the whole
line loses its bold — and with it eight of the lemmas the reader was looking for.

**MEASURED over five volumes, 31,391 spans: 25,233 drawn (80.4%). A
hyphen-tolerant locate would draw 26,032 (82.9%) — +799 spans.** Per volume:
31KhuA12 95.0→95.6, 32KhuA13 89.7→90.1, 09DiT02 64.3→68.0, 25VsmT01 79.1→82.9,
29KhuA10 94.0→94.2.

**This partly contradicts what `reader2.html` says about itself.** Its comment
records 85.9% located and concludes the rest "are not reachable from the
ordinal-keyed spans and no reader change fixes them". For the hyphen class that
is false: joining `- ` before matching reaches them, and the reader's own example
is one. The other ~17% remains unexplained and unmeasured.

**Design note for whoever does it:** locate in the JOINED string and draw the
JOINED string with spans mapped into that address space. Mapping back to the raw
text and drawing that would put `vīriya- nipphattiyā` on the page — a hyphen the
reader would then be right to report.

## ~~DPD FAMILY BLOCKS — BLOCKED ON SOURCE~~ DONE 2026-08-09 pm

The reader connected `/Users/aovb/GoldenDict/dpd`.  The keys were in the
inline `data_<lemma>` scripts the trim stripped; content in res/'s three
family_*_json.js.  `pipeline/rebuild_dpd_families.py` refreshed the whole
dpd store onto the 2026-07-28 DPD release (measured first: May→July differs
in dates on 63k entries, real updates on 10,990), pre-rendered 9,716
families into `stores/lookup_eval/family/`, stamped 77,894 divs with
`data-fk`; panel's `famFill` fetches on chip click.  Gate 25 assertions.
**R2 UPLOAD REQUIRED: dpd/ and family/ both** — until then production
serves the old store (WLV 20260809a busts it).  Original blocked note below
for the record.

## DPD FAMILY BLOCKS — BLOCKED ON SOURCE (2026-08-09)

The reader wants root family / compound family / idioms BACK WITH CONTENT
(they were scrubbed as eternal-loading stubs).  Diagnosis: `_panel/sources.py
dpd_trim` strips ALL `<script>` and its own docstring says it meant to keep
root-family content — the hypothesis (UNVERIFIED, one raw entry settles it)
is that DPD's GoldenDict export carries the family data inside the scripts.
The source is GONE: it was `/mnt/user-data/uploads/GoldenDict` in an earlier
session; GitHub releases are unreachable from the sandbox.  The reader is
asked to copy the GoldenDict folder into `_gd_src/GoldenDict/` in the repo
(needs `dpd/dpd.idx`, `dpd.syn.dz`, `dpd.dict.dz`).  Then: diagnose one raw
entry FIRST, fix the trim to extract families before stripping scripts,
rebuild the dpd shards only, bump **WLV** (stores change — not just the
script tag), extend `check_apd_gear.js` (sāvaka `family_root` has content,
chip present — the scrub spares contentful blocks by design), stamp, commit.

## Opened by this session, not closed

**397 note numbers have no marker anywhere in their paragraph's text**, in any
form — counted while measuring the bracket forms. They are notes keyed to an
ordinal whose text does not carry the digit at all, so either the keying or the
extraction is off by a paragraph. Nobody has looked. It is 0.9% of 44,917.

**The marker→note pairing is unestablished for a third of the corpus.** 45,901
of 69,000 markers sit in a digit whose marker count and note count agree, and the
reader is told plainly about the other 23,099 rather than being shown a guess.
Closing that gap means keying notes to the marker's OFFSET, not to its number —
which is the same shape of problem as the paragraph number not being a key.

**The verse map re-segments markers away from the paragraph text**, and nobody
has asked why. `check_fn_markers.js` reports the number on every volume that has
one: 09DiT02 907 in `text` against 868 in the drawn lines, 19Khu02 927 against
925, 27Khu10 494 against **564 the other way**. The gate deliberately does not
absorb it. It is a question about `verse/`, not about the apparatus, and it is
the kind of quiet divergence §"a one-sided ratchet is silent in one direction"
is about.

## Still open from the previous handoff — unchanged

Parked by the reader: the verbatim-repeat display (5,376 of 22,527), `none` vs
`dim`, ~~the APD tab's defaults and gear~~ **(DONE 2026-08-09 as decided on
08-06: CPED+PED open, gear for the rest, §9 note, one-line collapsed headers
with counts, `osbct-apdgear`; gate `pipeline/check_apd_gear.js`, 14 assertions,
selftest fails 9/14 on the pre-gear panel; panel.js script tag bumped to
20260809a, WLV unchanged)**, capping the concordance tooltip.

BLOCKBREAK still off; the hyphen repair (8,790 words, 109 volumes); classes 1
and 2 suspect; **position, unmeasured for 114 of 118 volumes**; the verse branch
for band blocks; the `WLV` gate; `.gitignore`'s stale store rule; the offline
package (§2 permission before bundling PDFs); `claude/` has never existed in git
though four files cite it; Node 20 deprecation on the Pages workflow.

## Hazards — unchanged, plus two

- **`.git` is write-protected from the sandbox.** Commit message goes to the
  repository root with a `*.bak` name.
- **Files under `_xc/` cannot be deleted from the sandbox either** — `rm` returns
  "Operation not permitted". `_xc/hy2/_dump.js` and `_xc/hy2/_gap.js` are
  throwaway probes left behind for that reason; delete them on the host.
- **jsdom OOMs at about 20 volumes in one process.** `check_fn_markers.js --all`
  dies around `06VinSg06` with `Ineffective mark-compacts near heap limit`. Run
  it in batches of 4–8 volumes per process; the 118-volume sweep was done that
  way.
- Do not write an angle-bracket placeholder into a shell command.
- Clear git locks on the host at the end of every session.
- Never "Re-run failed jobs" on Pages; start a fresh run.
- **`stamp_build.py --write` is not optional after any change under `site/`.**
  Done this session, twice: `6151ac21bbbd` → `f051d390acfe` → `eac8bb93c9fd`.
- **Run the placer for the range LAST.**

## The method

> **RUN THE INSTRUMENT AGAINST THE BUILD THAT HAS THE BUG.**

> **COMPARE AGAINST THE PRINTED PAGE, NEVER AGAINST THE CORPUS — AND THAT
> INCLUDES COMPARING AGAINST YOUR OWN OUTPUT.**

> **A REFACTOR THAT TURNS LINKS INTO ASSERTIONS OF SILENCE IS THE MOST DANGEROUS
> SHAPE OF CHANGE IN THIS PIPELINE.**

And the addition this session earned:

> **WHEN A CHECK DISAGREES WITH THE READER, SUSPECT THE CHECK FIRST.** Two
> versions of `check_fn_markers.js` reported their own mistakes as the reader's
> failures — 30 invented markers that were the verse map, then a near-total
> blackout that was an exclusion throwing away the ṭīkā's own prose. Both would
> have been believed if the numbers had been slightly less absurd. Every gate in
> `pipeline/` should be assumed to have one of these in it until it has been
> made to fail on purpose.
