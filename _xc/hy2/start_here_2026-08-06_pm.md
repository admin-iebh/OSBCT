# START HERE — after the 08-06 session

**The one thing blocking everything visible: the Pages deploy is failing, so
none of today's reader work is live.** The reader reported "two tooltips" three
times; the second and third reports were correct and my answers were wrong,
because the fix was committed and pushed but never published.

## The immediate question, and how to settle it in ten seconds

The source now has **exactly one** renderer of `data-tip` — verified against the
blob in `HEAD`, not a working copy, and by sweeping both shipped files for any
`content:attr(...)` or `:hover::after` rule. So either:

- **the deploy has not succeeded**, and the live site is older than the fix; or
- **there is a renderer not visible in the source**, and I am wrong.

**Right-click the second tooltip → Inspect.** What element it is ends the
question. Everything else is inference, including mine.

Second check, equally cheap: the console logs `OSBCT reader build: …` on load.
Local is **`a1a5de8aee10`**. Anything else means the page is not this build.

*(I could not check the live site myself — `web_fetch` on `buddha-dhamma.net`
timed out twice at 180s, so this sandbox appears to have no route to it. That is
a limit of my environment, not evidence about the site.)*

## The deploy failure — diagnosed, fix committed, NOT yet confirmed

Run for `8c86ae0`, "All jobs have failed", 11m31s, 3 annotations.

| | |
|---|---:|
| `site/` | **1.62 GB** |
| GitHub Pages limit | 1 GB |
| backup files (`*.bak*`, `*.pre*`, …), 1,751 of them | 478 MB |
| plain JSON in `lookup_eval/dpd/` whose `.gz` is what is fetched | 362 MB |
| **after pruning both** | **0.80 GB** |

`9afc1159` adds a step before the artifact upload running
`pipeline/prune_for_pages.py --write`, which prunes **the checkout, never the
repository**, and prints what it removes.

**This is an inference.** The run's 3 annotations were not readable from here.
Read them before trusting the diagnosis, and **check when a deploy last
succeeded** — if it has been failing for more than a day, the live site is stale
by more than today's work.

## What shipped today, in order

| commit | |
|---|---|
| `5ea43774` | the `35Abhi07` blocker: `block_shape` is a verdict about a block and was applied to a line |
| `5cfbfa96` | all 101 `katha` volumes swept — letters identical everywhere, 2 real mid-sentence lines |
| `03a1fffa` | the two big movers read on the page: both are flat gāthā, correctly repaired |
| `2b27462d` | **retraction** — the "111 corruptions" were a substring matcher |
| `481c7221` | `extract.py` reproduces the text but not the segmentation |
| `b689e8be` | **the hyphen migration REVERTED** — it stops the builder reproducing its own side-maps |
| `5bfc60e8` | the 320 condemned links are dimmed and say why |
| `87ca9d6a` | Read-more cut by a character budget, not a paragraph count |
| `bd355cd3` | panel tooltips placed above |
| `620181f3` | `atappaka` — the search box was gated on the corpus |
| `8c86ae01` | two tooltips: one `data-tip`, two renderers |
| `9afc1159` | the Pages artifact prune |

## Still open, and each needs the reader

1. **The 3,163 concordance violations** — same treatment as the 320, distinct
   wording. The path is proven.
2. **`none` vs `dim`.** The reader called a grey dashed dead button "dimmed",
   which is also what the new condemned chip is called. Two states, one word.
   Decide before the 3,163 arrive in that style.
3. **The hyphen repair** — parked. It is correct as text and cannot be applied
   without whatever in `build_khu_volume.py` matches paragraph text to printed
   lines. See `_xc/hy2/FINDINGS.md` §11.3.
4. **`RUNCHARS=1500`** — the reader's screenshots showed the previews are equal
   in text and not in height, because a paragraph costs more than its
   characters. A fixed per-paragraph overhead would fix it; not built.
5. **BLOCKBREAK** — still off. Two real mid-sentence lines (`32KhuA13`,
   `24KhuA05`) unread; `joined2.py` still on `blocks2/`.

## The lesson of the day, and it is mine

Three wrong locators (index for printed number, wrong volume, a number not
unique within its volume), one retracted measurement, one repair written to the
corpus and reverted, and two vacuous gates caught only by running them against
the code they replaced. Every one came from reporting before looking at the
thing reported. **The negative control — run the gate against the build that has
the bug — caught all four of the ones that were caught.** It is not optional.
