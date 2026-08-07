# The edition's abbreviated paragraph range — a rule for all books

**Established by the reader, 2026-08-07:** *"You are right when you say `234-5.`
means 234–235, `415-20.` means 415–420. You should remember this for all books.
This is important."*

The implementation is `pipeline/printed_range.py`. **Import it; do not write
another range regex.** Three files in `pipeline/` each carried their own naive
copy, and one of them was the ratchet.

---

## The rule

A paragraph may open with a printed range covering several units:

```
278-281.  Disvā me -pa- pucchituṁ amataṁ padanti uttānatthameva.
234-5.    Tassa Anomadassissa Bhagavato Munino ...
415-20.   Tadaḍḍhakaṁ tato aḍḍhakaṁ ...
```

**The upper bound is abbreviated whenever its leading digits repeat the lower
bound's.** `234-5.` is 234–235; `415-20.` is 415–420; `1234-45.` is 1234–1245.
When the upper bound is written out in full — `278-281.` — it is left alone. The
test is purely on digit count: if the second number has fewer digits than the
first, restore the elided leading digits from the first.

## Why it matters, and why it is dangerous

Read naively, `234-5.` yields an empty range, so every unit it covers is reported
as having **no commentary paragraph** — which becomes *"this paragraph is not
commented"*. That is a confident denial that looks exactly like a real result,
and it is produced silently, at scale.

It is the same failure direction as the sandhi hazard in
`_xc/hy2/start_here_2026-08-07_pm.md`: an untested absence stated as a claim.

## Measured extent, over all 118 volumes

| | |
|---|---:|
| paragraphs with a leading printed range | 2,572 |
| **of which the upper bound is abbreviated** | **576 (22.4%)** |
| unit numbers a naive reader loses | 926 |

Worst volumes: `26KhuA07` 112, `06ViT06` 98, `28KhuA09` 46, `03VinA03` 43,
`27KhuA08` 36, `05ViT05` 34, `02VinA02` 24, `32KhuA13` 22, `04ViT04` 18,
`08DiT01` 17.

Re-derive at any time with `python3 pipeline/printed_range.py --census`.

## Two things deliberately NOT done

**No width guard.** Abbreviated ranges are 2–6 units almost always, but
`28KhuA09` p. 227 prints `604-57.` — 54 units — because the commentary declines
the whole *Serīsakapetavatthu* as identical with the *Serīsakavimānavatthu*, and
p. 240 prints `714-36.` for the *Revatīpetavatthu* the same way. Both were read
on the printed page. A plausibility threshold would have rejected exactly the two
places where the edition says the most in one line.

**No correction of the one malformed range.** `14Sam03` ord 592 prints
`1187-1179.` Both bounds are four digits, so nothing is elided and the range
simply descends. Working principle 3: `expand_range` returns `None`, the caller
falls back to the exact number, and this is recorded as an erratum rather than
repaired.

---

## Errors this found in earlier work (working principle 5)

**`check_links.py`, the ratchet, was misreading the edition.** Its `n_match`
measure — *does a link's target really carry the number the link claims* — used
the naive form, so a link correctly pointing at a `234-5.` paragraph for n=235
was counted as a **miss**. The published rate was understated:

```
n_match  55.20%  ->  55.74%     with the data completely unchanged
```

356 links were right all along and were being scored as wrong. Any judgement
made about link quality against the old figure was made against a number that
was too low.

`relink_by_name.py` and `link_by_gloss.py` carried the same defect. In both it
made a *range* paragraph look like it did not carry the number, so the placement
fell back to `covered` — a worse landing, not a wrong volume. Both now import
`printed_range`.

**Separately: `check_concordance.py`'s `targets` baseline was stale by 46.**
Discovered while explaining an apparent regression on the Buddhavagga apply. The
pre-apply repository measured 67,369 targets against a recorded baseline of
67,323. **The ratchet only fails when `targets` goes DOWN**, so 46 targets had
been added at some earlier point and no gate ever noticed. The Buddhavagga apply
itself accounts for its change exactly — 67,369 → 67,232, which is the 137
records it removed, and `outside` 3,163 → 3,147, which is the 16 ineligible ones
— but the drift was already there. **A one-sided ratchet measures one direction
and is silent in the other**, and that is worth knowing about every other
baseline in `pipeline/`.
