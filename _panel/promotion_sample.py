#!/usr/bin/env python3
"""Sample what the SHIPPED promotion rule actually promotes, by reading the
rendered panel — not by reimplementing the rule.

WHY NOT REIMPLEMENT IT
`_panel/proximity_variant.py` measures a rule that is NOT the one that ships.
Three differences, each of which changes the answer:

  1. it tests `belongs_pool(row['lemma'], pool)` — the printed lemma string —
     where the panel tests `inPara(row, pool)` over `row.k`, the PRE-COMPUTED
     STEMS, with multiplicity (`Tassa tassā` needs two `tassa`, not one);
  2. it reads `site/reader/links/*.fwd.json`, keyed by printed paragraph NUMBER
     and holding ONE commentary and ONE subcommentary target; the panel reads
     `site/reader/linksk/*.links.json`, keyed by ORDINAL and holding ARRAYS —
     so the panel's "linked" set is strictly larger;
  3. it pools `clean(p['text'])` — the raw paragraph text out of the volume
     JSON.  The panel pools `d.para.textContent`, which is what reader2 put on
     screen: that includes the APPARATUS BLOCK (variant readings and footnote
     text, `appBlock()`), the sutta title and the paragraph number, and it has
     had the leading `12. ` stripped and the incipit removed.  Words that exist
     only in a variant reading can satisfy the shipped rule and cannot satisfy
     the variant script's.

So the only honest way to measure the shipped rule is to run it.  This driver
opens reader2 in real Chromium exactly as `gate_reader.py` does, clicks words in
the rendered canon, and records the groups the panel actually drew.

THE GROUPS.  `viewEd` makes four.  Three are boxed and are the subject here:

  prox  .wl-promo    "In the commentary on this paragraph"
  here  .wl-promo    "On a phrase that stands in this paragraph"
  word  .wl-wordgrp  "On the word itself"
  rest  (unboxed)    "Other occurrences"

Output: promotion_population.json — one record per click.
"""
import json, os, re, sys, random, collections, time
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
BASE = os.environ.get('SAMPLE_BASE', 'http://localhost:8931')
SEED = int(os.environ.get('SAMPLE_SEED', '20260803'))
N_PER_VOL = int(os.environ.get('SAMPLE_N', '40'))
OUT = os.path.join(ROOT, 'promotion_population.json')

# The 40 canon volumes: those with a link map the panel can read.  51/52 are
# the Visuddhimagga, which has one too; it is not canon and is left out, so the
# population is "a reader reading the canon", which is what the tab is for.
VOLS = [os.path.basename(p).split('.')[0]
        for p in sorted(__import__('glob').glob(
            os.path.join(REPO, 'site/reader/linksk/*.links.json')))]
VOLS = [v for v in VOLS if not v.startswith(('51', '52'))]
assert len(VOLS) == 40, f'expected 40 canon volumes, got {len(VOLS)}: {VOLS}'

# Read the groups the panel DREW.  Labels are the English strings from panel.js
# S{}; the driver forces lang=en so they are deterministic.
READ_GROUPS = r'''() => {
  const b = document.getElementById('wlb');
  if (!b) return null;
  const out = {groups: [], tab: null};
  const sel = document.querySelector('#wlt button[aria-selected="true"]');
  out.tab = sel ? sel.dataset.tab : null;
  let label = null;
  const rowOf = r => ({
    l: (r.querySelector('.lem') || {}).textContent || '',
    g: (r.querySelector('.wl-g') || {}).textContent || '',
    cite: (r.querySelector('.wl-cite') || {}).textContent || '',
    href: (r.querySelector('a.wl-go') || {}).getAttribute
          ? (r.querySelector('a.wl-go') || {}).getAttribute('href') : null,
    flags: [...r.querySelectorAll('.wl-flag')].map(f => f.textContent)
  });
  for (const el of b.children) {
    if (el.classList.contains('wl-sub')) { label = el.textContent.trim(); continue; }
    if (el.classList.contains('wl-promo') || el.classList.contains('wl-wordgrp')) {
      out.groups.push({label: label, box: el.classList.contains('wl-promo') ? 'promo' : 'wordgrp',
                       rows: [...el.querySelectorAll('.wl-row')].map(rowOf)});
      label = null;
    }
  }
  // the unboxed remainder: .wl-row that are direct children of #wlb
  const loose = [...b.children].filter(e => e.classList.contains('wl-row'));
  if (loose.length) out.groups.push({label: 'REST', box: null, rows: loose.map(rowOf)});
  out.counts = (document.getElementById('wlc') || {}).textContent || '';
  out.word = (document.getElementById('wlw') || {}).textContent || '';
  return out;
}'''

CLICK_MEASURE = r'''([word, pid]) => {
  const p = document.getElementById(pid); if (!p) return null;
  const rx = new RegExp('(^|[^a-zāīūṁṅñṭḍṇḷ’])' +
        word.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') +
        '($|[^a-zāīūṁṅñṭḍṇḷ’0-9])');
  const t = p.textContent; const m = rx.exec(t); if (!m) return null;
  const i = m.index + m[1].length;
  const walker = document.createTreeWalker(p, NodeFilter.SHOW_TEXT);
  let acc = 0, node;
  while ((node = walker.nextNode())) {
    const L = node.textContent.length;
    if (acc + L > i) {
      const r = document.createRange();
      r.setStart(node, i - acc);
      r.setEnd(node, Math.min(i - acc + word.length, node.textContent.length));
      const rect = r.getBoundingClientRect();
      if (rect.top < 60 || rect.bottom > innerHeight - 10) return null;
      return {x: rect.x + Math.min(rect.width / 2, 5),
              y: rect.y + rect.height / 2, para: p.textContent};
    }
    acc += L;
  }
  return null;
}'''


def main():
    rng = random.Random(SEED)
    recs = []
    t0 = time.time()
    with sync_playwright() as pw:
        br = pw.chromium.launch()
        ctx = br.new_context(viewport={'width': 1440, 'height': 900})
        ctx.add_init_script("try{localStorage.setItem('osbct-lang','en')}catch(e){}")
        pg = ctx.new_page()
        for vi, vol in enumerate(VOLS):
            pg.goto(BASE + f'/reader/reader2.html?wl=1&wle=0#{vol}/0',
                    wait_until='domcontentloaded')
            try:
                pg.wait_for_selector('.para.canon', timeout=30000)
            except Exception:
                print(f'{vol}: no canon paragraph rendered', file=sys.stderr)
                continue
            pg.wait_for_timeout(400)
            words = pg.evaluate('''() => {
              const out = [];
              document.querySelectorAll('.para.canon').forEach(p => {
                const seen = new Set();
                (p.textContent.match(/[a-zāīūṁṅñṭḍṇḷ’]{4,}/gi) || []).forEach(w => {
                  if (seen.has(w)) return; seen.add(w); out.push([w, p.id]); });
              });
              return out;
            }''')
            if not words:
                print(f'{vol}: no words in rendered canon', file=sys.stderr)
                continue
            rng.shuffle(words)
            got = 0
            for word, pid in words:
                if got >= N_PER_VOL:
                    break
                # close first, THEN scroll, THEN measure — the panel's 380px
                # padding reflows the text and a rectangle measured across
                # either change aims the mouse at a different word.
                pg.evaluate('''() => {
                  const x = document.getElementById('wlx'); if (x) x.click();
                  const wl = document.getElementById('wl');
                  if (wl) wl.dataset.state = 'stale';
                }''')
                pg.evaluate('''(pid) => {
                  const p = document.getElementById(pid);
                  if (p) p.scrollIntoView({block: 'center'});
                }''', pid)
                pg.wait_for_timeout(120)
                ok = pg.evaluate(CLICK_MEASURE, [word, pid])
                if not ok:
                    continue
                pg.mouse.click(ok['x'], ok['y'])
                try:
                    pg.wait_for_selector('#wl[data-state="ready"]', timeout=20000)
                except Exception:
                    continue
                g = pg.evaluate(READ_GROUPS)
                if not g:
                    continue
                # the panel's own header word, not the one we aimed at
                if g['word'] and g['word'].lower() != word.lower():
                    word = g['word']
                got += 1
                recs.append({'vol': vol, 'pid': pid, 'word': word,
                             'para': ok['para'], 'counts': g['counts'],
                             'tab': g['tab'], 'groups': g['groups']})
            print(f'[{vi+1:2d}/40] {vol}: {got} clicks  '
                  f'({len(recs)} total, {time.time()-t0:.0f}s)', flush=True)
        br.close()
    json.dump(recs, open(OUT, 'w'), ensure_ascii=False)
    print(f'\nwrote {OUT}: {len(recs)} clicks')


if __name__ == '__main__':
    main()
