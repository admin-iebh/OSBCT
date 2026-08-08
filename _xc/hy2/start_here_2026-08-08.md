# START HERE — 2026-08-08

<!-- Supersedes start_here_2026-08-07_pm.md, which is still correct about
     everything except its open items 1 and 3, both of which moved. Read this
     block, then §"Next, in order". -->

## State

**Committed and deployed: Buddhavagga.** `20Khu03` vagga 1 → `32KhuA13`,
530 linked + 133 not commented + 0 cannot establish = 663, the vagga's canon
numbered paragraphs exactly. Gloss confirms 506 of 517 targets carrying bold
(97.9%), and all eleven disagreements land on range paragraphs where the
commentary covers several verses at once — no unexplained residue.

**In `_xc/linksk_toc/` only, NOT applied: vaggas 2–42 → `33KhuA14`.**
761 linked + 3,037 not commented = 3,798. Of the links, **444 by paragraph
number and 317 by ordinal word**. Three inversions unresolved.

BUILD `1e7e28f2c125` → `6151ac21bbbd`.

## The instrument, and the order it works in

`pipeline/link_by_toc.py`, gate `pipeline/check_toc_links.py` (8 assertions,
selftest injects each defect ALONE and confirms each is caught alone).

    VAGGA   region bounded by the commentary's vagga heads, paired by NAME.
            A head may cover SEVERAL canon vaggas — `21-23.`, `34.`+ādi — and
            the words in its text say which.
    NUMBER  inside that region only. Unique there, so it is the address.
    ORDINAL for commentary paragraphs carrying no number: the edition names
            which apadāna in words.
    GLOSS   confirmation only, never placement.

Whatever the region does not account for is `not_commented`.

## THE FIRST THING TO SETTLE TOMORROW

**Reader, at the end of 08-07:** *"`1. Pilindavacchatthera-apadānavaṇṇanā` is
only one page with two numbered paragraphs 1 and 3 to comment on 257 verses."*

**That is a verdict on the ordinal-word mechanism and it has not been acted
on.** The placer currently gives a commentary paragraph identified by ordinal
word the WHOLE canon apadāna span — so vagga 40 alone takes 257 links, every
verse of Pilindavaccha's apadāna landing on the same page. The reader's
observation says the commentary there carries numbered paragraphs **1** and
**3** and nothing else: by his account the honest reading is that canon 1 and 3
are commented and the remaining 255 verses are not.

**So the ordinal-word span is probably over-claiming, in the direction that
manufactures links.** 317 of the 761 are placed this way. Settle this before
anything is applied. The narrow reading — ordinal word places only the
paragraphs the commentary actually numbers, and the ordinal word serves to
identify WHICH apadāna those numbers belong to — is likely right and would move
most of the 317 into `not_commented`.

## TWO DEFECTS THE READER FOUND AT THE END OF 08-07, BOTH VERIFIED

**1. A link that lands on the canon repeated back, not on the gloss.**
`19Khu02` ord 3294 (n=159, printed p. 397) — Mahāpajāpatī Gotamī's verse
*Mātā putto pitā bhātā … Yathābhuccamajānantī, saṁsariṁhaṁ anibbisaṁ* —
links `direct` to `31KhuA12` ord **207**, printed p. 146. That paragraph is the
**verbatim canon verse**, nothing else. The actual gloss is `31KhuA12` ord
**210**, same printed page: *Tattha **yathābhuccamajānantī**ti pavattihetu-ādiṁ
yathābhūtaṁ anavabujjhantī. **Saṁsariṁ haṁ anibbisan**ti …*

So the reader clicks **A** and is shown the line he just read. The record
carries `by: None` — it predates every `by` this pipeline writes, so it is an
old-builder link, not one of ours.

**This is the parked "verbatim repeat" item (5,376 of 22,527) with a concrete
cost attached, and it is no longer only a display question.** The commentary
prints the canon lemma as a heading before glossing it; a link that stops at the
heading is a link to nothing. The fix is presumably: where a candidate target is
a verbatim repeat of the canon paragraph, advance to the next paragraph that is
not. **Measure how many of the 5,376 are link targets before deciding.**

**2. The apparatus is extracted and keyed, and the reader is not showing it.**
NOT an extraction defect — I checked, and my first check was wrong. The files
are `<vol>.app.json` / `<vol>.appk.json` (464 files); looking for `<vol>.json`
reported "0 of 118 volumes have an apparatus", which is false.

`31KhuA12.appk.json` holds **111 keyed entries**, and ord 210 carries seven,
including `3 → "Sāvaketi (Sī, I)"` and `4 → "Khu 4. 206 piṭṭhādīsu."`. Those are
exactly the markers standing as bare digits in the reader — *sāvake**3***,
*Apadāne**4**–* — with no note attached and no marker styling. Some markers on
the same page render as superscripts and some do not, so the rendering is
inconsistent within one paragraph.

Corpus-wide there are **70,598** digits glued to a letter across the 118
volumes. Start from `reader2.html:551`, which loads `apparatus/<vol>.appk.json`,
and establish whether the A band renders apparatus at all or only the canon
layer does.

## Three inversions, unresolved

Vaggas 18, 34, 35, one link each crossing its neighbour. Every other assertion
passes on all 42 vaggas. `place()` walks a monotonic `floor` and falls back to
an earlier candidate when none lies forward; that fallback is where they come
from. Look at whether the fallback should exist at all.

## SANDHI COST THREE SEPARATE FIXES IN ONE DAY, ALL IN THE SAME DIRECTION

- `vagga` + `ādi` = `vagg**ā**di` — stripping a literal `ādi` left `vagg` and
  missed all four `ādi` heads, which are exactly the ones bounding several
  vaggas at once.
- `tatiya` + `apadāne` = `tatiy**ā**padāne` — the literal stem never matched the
  form that names an apadāna without a thera word between.
- the adjacency window was 4 characters and `tther` is five.

**Every one produced FEWER links, and fewer links become assertions of silence,
not visible errors.** That is the direction that does not announce itself. Any
change to matching in this area must be measured by the link count before and
after, not by whether the gate stays green.

## Errata found, none corrected (working principle 3)

- **`32KhuA13` prints 442 twice** — ord 321 (p. 305), sitting among 421/430/431
  where a `422` belongs, and ord 330 (p. 309), which glosses *ajjhāyako* and is
  the real one. Taking the first sent canon 442 four printed pages backwards.
  **Assertion 7 caught it on a volume already applied and already passing all
  eight assertions.**
- **`32KhuA13` prints 310 twice** — ords 255, 256, both p. 259.
- **`33KhuA14` prints `10.` for both** `10. Sudhāvagga` (p. 114) and
  `10. Bhikkhadāyivagga` (p. 120); the canon has Bhikkhadāyi = 11. Pairing by
  name handles it; pairing by number would have mis-paired vagga 10 and lost
  vagga 11 entirely.
- **`14Sam03` ord 592 prints `1187-1179.`**, descending. `expand_range` returns
  None and the caller falls back to the exact number.

## Errors in earlier work found this session (principle 5)

1. **`check_links.py`, the ratchet, misread the edition.** It carried the naive
   `(\d+)-(\d+)`, so a link correctly pointing at a `234-5.` paragraph for
   n=235 was scored a MISS. `n_match` 55.20% → **55.74%** with the data
   unchanged: 356 links right all along. `relink_by_name.py` and
   `link_by_gloss.py` had it too. All four now import `printed_range.py`.
2. **`check_concordance.py`'s `targets` baseline was stale by 46** before any
   change: the repository measured 67,369 against a recorded 67,323. The gate
   only fails when `targets` goes DOWN, so upward drift was invisible.
   **A one-sided ratchet is silent in one direction** — this applies to every
   other baseline in `pipeline/` and none of them has been audited.
3. **Canon 5 was written out as `cannot_establish` while `32KhuA13` p. 111
   quotes it in full and glosses it word by word.** Cause: the commentary
   section holding it paired with nothing, so its numbers fell outside every
   search span — a fact about the pairing procedure reported as a fact about the
   edition, and handed to the reader as a decision. **All seven assertions were
   green over that file**, because every one audited the links that WERE made.
   Assertion 8 now tests what was NOT linked. Its selftest case is that defect.
4. **258 heads in 18 volumes name a vagga but are classified `sutta`**, because
   the extraction takes a head's kind from typography and the PDF does not centre
   them. Only `33KhuA14` is fixed. `pipeline/fix_vagga_heads.py --census` lists
   the rest. Until a volume is fixed its vagga regions run together and a bare
   number matches wherever it likes inside the over-wide region.

## Next, in order

1. **Settle the ordinal-word span** — §"THE FIRST THING" above. Blocks applying
   vaggas 2–42.
1b. **The two defects the reader found** — the verbatim-repeat link target and
   the unrendered apparatus. Both verified, both above.
2. **The three inversions.**
3. **Spot-check against the printed page** before applying —
   `_xc/hy2/20Khu03_vaggas2-42_dryrun.md` has the list with printed pages.
   A green gate is evidence nothing got worse, not that the thing is true; it
   took the reader opening p. 111 to find canon 5.
4. **The concordance gate.** When vaggas 2–42 land, `check_concordance.py` will
   fail: `site/concordance.json` gives `20Khu03 → 32KhuA13` alone and ~1,300
   correct links into `33KhuA14` will register as violations. Amend the entry,
   teach the gate to defer to the per-book map, or retire it for books done
   properly. **Reader's decision, not taken yet.**
5. **`fix_vagga_heads.py` on the other 17 volumes**, one at a time.
6. **Audit the remaining `pipeline/` baselines for drift.**
7. **`20KhuA01` ord 174** carries a section head (`Ekaṁ nāma kintipañhavaṇṇanā`)
   the nav does not. The only real residue of the old "front matter" item.

## CLOSED, and the handoff was wrong about it

**Open item 3 of the 08-07 pm handoff — "690 unnumbered leading records
unreachable because the nav keys on the paragraph number" — is not true.**
The nav keys on the ORDINAL (`vol#ord`). Measured: 63 volumes have unnumbered
leading records, **53 are reachable from the nav**, and the 10 that are not have
one or two records each — a title line and *Namo tassa* — with the first nav
point on the very next paragraph. The nav already carries every head the
extraction found, bar the `20KhuA01` one above.

## Still open from the previous handoff — unchanged

Parked by the reader: the verbatim-repeat display (5,376 of 22,527), `none` vs
`dim`, the APD tab's defaults and gear, capping the concordance tooltip.

BLOCKBREAK still off; the hyphen repair (8,790 words, 109 volumes); classes 1
and 2 suspect; **position, unmeasured for 114 of 118 volumes — the largest thing
outstanding**; the verse branch for band blocks; the `WLV` gate (bucket
`Cache-Control` pinned at one day until it exists); `.gitignore`'s stale store
rule; the offline package (§2 permission must be confirmed before bundling
PDFs); `claude/` has never existed in git though four files cite it; Node 20
deprecation on the Pages workflow.

## Hazards

- **`.git` is write-protected from the sandbox.** Commit message goes to the
  repository root with a `*.bak` name.
- **Do not write an angle-bracket placeholder into a shell command** — it is a
  redirect in zsh.
- **Clear git locks on the host at the end of every session:**
  `find .git -maxdepth 2 -name '*.lock*' -size 0 -delete`
- **Never "Re-run failed jobs" on Pages**; start a fresh run.
- **`stamp_build.py --write` is not optional after any change under `site/`.**
- **Run the placer for the range LAST.** `link_by_toc.py` reads the live file and
  writes the whole volume, so a later single-vagga run silently discards an
  earlier range run's output. That happened this session and produced a page of
  gate failures that were an artefact of run order.

## The method

> **RUN THE INSTRUMENT AGAINST THE BUILD THAT HAS THE BUG.**

> **COMPARE AGAINST THE PRINTED PAGE, NEVER AGAINST THE CORPUS — AND THAT
> INCLUDES COMPARING AGAINST YOUR OWN OUTPUT.**

And the addition this session earned:

> **A REFACTOR THAT TURNS LINKS INTO ASSERTIONS OF SILENCE IS THE MOST DANGEROUS
> SHAPE OF CHANGE IN THIS PIPELINE.** Rebuilding the candidate map dropped every
> ordinal-word placement — 688 links fell to 448 — and nothing failed, because
> the lost ones simply became `not_commented`, which is a claim rather than an
> error. Measure the link count across every change to matching.
