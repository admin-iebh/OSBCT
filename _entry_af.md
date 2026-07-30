## VINAYA 3 — 03Vin03 PAIRS 479/479 AND IS **NOT WRITTEN** (2026-07-26af)

    03Vin03   pairing     479 printed units / 479 corpus ¶, 0 n-mismatches,
                          once `head_words` was measured rather than assumed
              body        14 524 0 490 {4,1} -> 0 missing / 0 chunks / 0 not in
                          PDF / **2 RENDERED-TOO-OFTEN** — unexplained
              STATE       side-maps WITHDRAWN to
                          `_to_delete/03Vin03_unverified/`.  The volume is NOT
                          done and must not be counted as done.
    also      32Abhi04 corrected — 45 pādas were being drawn as colophons
              `_abhi04verify.js` 277/277 (its 35-gāthā-block assertion encoded
              the defect and is now 44, with the reason recorded in the file)
              regression 55/55; 01Vin01, 02Vin02, 31Abhi03, 36Abhi08 re-gated
              clean on all three gates after the rule change

### `head_words` — THE WORD CAP IS A MEASUREMENT, NOT A CONSTANT

Under `heads_by_form` a NUMBERED line is a heading only when it is centred AND
short AND unpunctuated within. "Short" has been **2** since 36Abhi08 measured it
there, and every Abhidhamma volume since has agreed. 03Vin03's section titles
are three and four words — "Āpattiyā adassane ukkhittakavatthūni", "Saṁghe
bhinne cīvaruppādakathā" — so four of them were read as numbered UNITS.

MEASURED on that volume: of its 769 numbered printed lines, **282 are ≤4 words
with no internal period and centred at body+14 or beyond, and every one is a
section title**; the 473 that are longer are all units; and of the 14 that are
short but sit LOW, the six ending at a heading stem are titles whose own length
pushed them down (the recurring "a centred line's indent falls as its name
grows") and the rest are units the stem test correctly refuses. So
`head_words: 4` here, defaulting to the 2 every shipped volume was measured at.

### `pada_runon` WIDENED TO THE WHOLE RUN — and a fourth shipped volume fixed

01Vin01's couplets alternate comma / stop, so looking one line back reaches
them. **03Vin03 prints long gāthā in which every pāda ends in a stop** and only
some carry a comma at the caesura, and there the line above says nothing. What
the page says is that they are ONE BLOCK: a maximal run of display lines at a
single indent. If any line in that run carries a comma, the run is verse and
none of it is a closing line.

**THE ONE EXCEPTION IS THE EDITION'S OWN STRICT COLOPHON FORM** — a line that
both NAMES a section and says it is FINISHED. 31Abhi03 p94 sets "Asaṅgahitena
sampayuttavippayuttapadaniddeso terasamo." at the SAME indent as the six gāthā
lines above it. Measured over every kathā book with a SPEC: the run test
reclassifies 476 lines and the strict form rescues **exactly that one**.

**32Abhi04 had 45 pādas drawn as colophons** — "Tayassu dhammā jahitā
bhavanti.", "Sīlabbataṁ vāpi yadatthi kiñci." and 43 more — and a false
colophon also CUT the block it stood in, so the volume drew 35 gāthā blocks
where it prints 44. Fixed and re-gated. **26Khu09, 27Khu10 and 28Khu11 were
suspected on the same evidence and CLEARED**: the form test fires there but the
classification never reaches it. That makes **four** shipped volumes corrected
by this class in two sessions (31Abhi03, 32Abhi04, 33Abhi05, 36Abhi08).

### !!! WHY 03Vin03 IS NOT WRITTEN — an unexplained RENDER duplication

The body gate reports **2 chunks rendered twice, printed once**, both in the
Mahākhandhaka's opening (printed units 4 and 5, "Atha kho Bhagavā sattāhassa
accayena tamhā samādhimhā vuṭṭhahitvā …"). Established so far, by measurement:

  * the phrase is printed ONCE, is in the corpus ONCE, and appears in exactly
    ONE side-map entry;
  * the RENDER contains it TWICE — two distinct text nodes, one in the
    `.para.canon` itself and one in a `div.gatha-after` INSIDE it;
  * 476 of the 479 verse entries have an `after` that repeats their own corpus
    paragraph's opening, which is how the kathā path is supposed to work (it
    draws the body from the PRINTED stream), so that alone is not the fault;
  * **01Vin01 and 02Vin02 pass the same gate at `rendered-too-often 0` with the
    same builder and the same reader**, so this is specific to this volume;
  * a count of "units whose 70-character opening appears more than once in the
    render" gives 125 of 479, but **91 of those are explained by the Vinaya's
    formulaic openings** ("Idha pana bhikkhave bhikkhusaṁghena tajjanīyakammakato
    …" occurs 10 times), so that figure is NOT evidence of 125 defects and must
    not be quoted as one.

What is NOT yet known is the mechanism, and therefore whether the remaining ~34
are real. **FLAG RATHER THAN GUESS**: the side-maps are withdrawn rather than
shipped on a gate result that is not understood. `03Vin03` also carries
commentary links (`ATp.3 ⧉` renders immediately before the duplicated text),
which 01Vin01 and 02Vin02 have far fewer of — that is the first thing to test.

### Where the Vinaya stands

    01Vin01  DONE, three gates          02Vin02  DONE, three gates
    03Vin03  PAIRS, NOT WRITTEN         04Vin04  scouted only
    05Vin05  scouted only
    the NAV of all five is untouched

`head_words: 4`, `pada_runon` and `wrap_display` are in `SPEC['03Vin03']` and
its pairing is proved; only the render question is open.


---

