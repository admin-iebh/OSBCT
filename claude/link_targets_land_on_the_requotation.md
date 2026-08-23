# Links landing on the commentary's re-quotation, per book

> **EVERY NUMBER BELOW IS AN UNDERCOUNT. Established 2026-08-23; do not plan
> against this table until it is re-measured.**
>
> The test used here compares whole strings, and **the canon carries
> footnote-marker digits inside the word** (`malyadhare1`, `Imāsāhaṁ1`) where
> the commentary's reprint does not. It also cannot see a quote that the
> edition abridged with peyyala, or one with prose appended after it.
>
> On the one row since measured properly — `19Khu02 → 27KhuA08` — the true
> figures are **907 links on a reprint, not 500**, and **435 same-numbered
> gloss pairs, not 267**. That row is now repaired: 437 links moved,
> `claude/vimanavatthu_links_moved_to_the_gloss.md`.
>
> The four rows reading **0** in the "same-n gloss found" column are the least
> trustworthy of all — `31KhuA12` is already known by hand to have a gloss this
> test could not see.

Measured 2026-08-09 over `site/reader/linksk/` at build `92157e0692e0`.
A link is counted when the target paragraph's text IS the canon paragraph's
text — the commentary reprinting the verse, not commenting on it.

**This is a worksheet, not a rule.** How each commentary relates to its canon
is a per-book question (the reader, 2026-08-09), and the numbers below say so:
the offset from quote to gloss is not constant, and in many pairs no
same-numbered gloss exists at all, which means those books are built
differently rather than that the gloss is absent.

| canon | commentary | direct links | on a repeat | % | same-n gloss found | offset |
|---|---|---:|---:|---:|---:|---:|
| 23Khu06 | 42KhuA23 | 1645 | 755 | 46% | 0 | — |
| 19Khu02 | 30KhuA11 | 1004 | 668 | 67% | 0 | — |
| 23Khu06 | 40KhuA21 | 1220 | 552 | 45% | 341 | 248 |
| 19Khu02 | 27KhuA08 | 937 | 500 | 53% | 267 | 7 |
| 22Khu05 | 39KhuA20 | 1130 | 473 | 42% | 325 | 159 |
| 21Khu04 | 34KhuA15 | 964 | 414 | 43% | 312 | 81 |
| 23Khu06 | 41KhuA22 | 774 | 381 | 49% | 0 | — |
| 19Khu02 | 28KhuA09 | 703 | 349 | 50% | 221 | 3 |
| 19Khu02 | 31KhuA12 | 520 | 320 | 62% | 0 | — |
| 22Khu05 | 38KhuA19 | 793 | 202 | 25% | 154 | 200 |
| 22Khu05 | 40KhuA21 | 335 | 127 | 38% | 86 | 338 |
| 18Khu01 | 22KhuA03 | 309 | 65 | 21% | 1 | 9 |
| 22Khu05 | 37KhuA18 | 343 | 57 | 17% | 17 | 217 |
| 19Khu02 | 29KhuA10 | 251 | 51 | 20% | 0 | — |
| 21Khu04 | 35KhuA16 | 312 | 28 | 9% | 21 | 125 |
| 18Khu01 | 21KhuA02 | 119 | 13 | 11% | 0 | — |
| 27Khu10 | 21KhuT01 | 212 | 1 | 0% | 1 | 22 |

**Totals across the pairs listed: 11571 direct links, 4956 on a repeat, 1746 with a same-numbered gloss further on.**

## First example in each pair

| canon ¶ | current target (the quotation) | candidate gloss |
|---|---|---|
| `23Khu06#2` | `40KhuA21#342` | `40KhuA21#590` |
| `19Khu02#0` | `27KhuA08#4` | `27KhuA08#11` |
| `22Khu05#1348` | `39KhuA20#2` | `39KhuA20#161` |
| `21Khu04#3451` | `34KhuA15#32` | `34KhuA15#113` |
| `19Khu02#1034` | `28KhuA09#4` | `28KhuA09#7` |
| `22Khu05#504` | `38KhuA19#6` | `38KhuA19#206` |
| `22Khu05#2617` | `40KhuA21#3` | `40KhuA21#341` |
| `18Khu01#343` | `22KhuA03#153` | `22KhuA03#162` |
| `22Khu05#160` | `37KhuA18#12` | `37KhuA18#229` |
| `21Khu04#4506` | `35KhuA16#8` | `35KhuA16#133` |
| `27Khu10#26` | `21KhuT01#168` | `21KhuT01#190` |
