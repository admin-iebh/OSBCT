#!/usr/bin/env python3
"""The panel's gate, moved to where the panel now lives — reader2 itself.

`gate.py` opens the prototype page.  That page is not what ships.  The argument
of 2026-07-30 applies again: 23,386 cross-references parsed correctly for weeks
and never reached the reader, and no gate could see it.  A gate that opens a
prototype cannot see whether the shipped reader opens a panel at all.

So this one drives `site/reader/reader2.html?wl=1&#<VOL>/<id>` in real Chromium,
clicks words in the rendered canon text and asserts what the panel shows against
`site/lookup/` directly:

  1. THE FLAG.  Without `?wl=1` the panel does not exist: no #wl node, no
     lookup/ request.  A feature behind a flag has to be OFF when the flag is.
  2. the panel opens and its header is the clicked surface form;
  3. the corpus counts shown equal the freq shard;
  4. the Edition tab's count equals the number of gloss rows keyed to the form
     (for an overflow form, the shard's stated total, not the page in hand);
  5. EVERY promoted row passes the check it is promoted for — its bold lemma
     really is a phrase of the paragraph on screen.  This is the whole design
     claim of the Edition tab and it is the one thing a reader cannot verify;
  6. the default tab is Edition, never PED (§9);
  7. no DPD text anywhere in the panel, ever;
  8. a form with no gloss says so rather than showing an empty list.

`--breakpoints` runs the other job: sweep the viewport in real Chromium and
report the width at which the side panel stops leaving a readable measure.  The
prototype's numbers were measured on the prototype's layout; reader2 has a
300px left pane and its own overlay rule at 861px, so they are a starting point
and not an answer.
"""
import json, glob, os, random, re, sys, collections
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
LOOKUP = os.path.join(REPO, 'site', 'lookup')
BASE = os.environ.get('GATE_BASE', 'http://localhost:8932')
SEED = 20260802
VOLS = os.environ.get('GATE_VOLS', '09Ma01,08Di03,18Khu01,37Abhi09,05Vin05').split(',')
N_PER_VOL = 8

FOLD = {'ā': 'a', 'ī': 'i', 'ū': 'u', 'ṁ': 'm', 'ṃ': 'm', 'ṅ': 'n', 'ñ': 'n',
        'ṭ': 't', 'ḍ': 'd', 'ṇ': 'n', 'ḷ': 'l'}
fold = lambda s: ''.join(FOLD.get(c, c) for c in s.lower())
VOWELS = set('aiueo')


def stem(w):
    f = re.sub(r'(.)\1+', r'\1', fold(w))
    while f and (f[-1] in 'mn' or f[-1] in VOWELS):
        f = f[:-1]
    return f


MAN = json.load(open(os.path.join(LOOKUP, 'index.json')))


def shard_of(setname, key):
    m = MAN['shards'][setname]
    f = fold(key)
    for d in range(2, 41):
        name = (f[:d] + '_' * d)[:d]
        if name in m:
            return name
    return None


_cache = {}


def look(setname, key):
    s = shard_of(setname, key)
    if not s:
        return None
    p = os.path.join(LOOKUP, setname, s + '.json')
    if p not in _cache:
        _cache[p] = json.load(open(p)) if os.path.exists(p) else {}
    o = _cache[p]
    return o.get(key, o.get(key.lower()))


def gloss_total(word):
    g = look('gloss', word)
    if g is None:
        return 0
    if isinstance(g, dict):
        return g.get('big', 0)
    return len(g)


def ped_total(word):
    hs = look('forms', word) or []
    return sum(len(look('ped', h) or []) for h in hs)


def run_gate():
    rng = random.Random(SEED)
    fails, checked = [], 0
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page(viewport={'width': 1400, 'height': 900})
        errors = []
        pg.on('pageerror', lambda e: errors.append(str(e)))

        # --- 1. the flag is off by default -----------------------------------
        reqs = []
        pg.on('request', lambda r: reqs.append(r.url))
        pg.goto(BASE + '/reader/reader2.html?wl=0', wait_until='domcontentloaded')
        pg.wait_for_timeout(1200)
        if pg.evaluate("!!document.getElementById('wl')"):
            fails.append('flag off: the panel node exists anyway')
        if any('/lookup/' in u for u in reqs):
            fails.append('flag off: lookup/ was fetched anyway')

        for vol in VOLS:
            pg.goto(BASE + f'/reader/reader2.html?wl=1#{vol}/0',
                    wait_until='domcontentloaded')
            try:
                pg.wait_for_selector('.para.canon', timeout=20000)
            except Exception:
                fails.append(f'{vol}: no canon paragraph rendered')
                continue
            pg.wait_for_timeout(400)

            words = pg.evaluate('''() => {
              const out = [];
              document.querySelectorAll('.para.canon').forEach(p => {
                const t = p.textContent;
                (t.match(/[a-zāīūṁṅñṭḍṇḷ’]{4,}/gi) || []).forEach(w => out.push([w, p.id]));
              });
              return out;
            }''')
            if not words:
                fails.append(f'{vol}: no words found in the rendered canon')
                continue
            # stratify: some with many gloss rows, some with few, some with none
            byband = collections.defaultdict(list)
            for w, pid in words:
                n = gloss_total(w)
                byband['0' if n == 0 else '1-10' if n <= 10 else 'many'].append((w, pid))
            pick = []
            for band in ('0', '1-10', 'many'):
                pool = byband[band]
                rng.shuffle(pool)
                pick += pool[:max(1, N_PER_VOL // 3)]

            for word, pid in pick:
                # !!! SCROLL FIRST, THEN MEASURE, IN TWO SEPARATE STEPS.  The
                # first version scrolled and read the rectangle in one
                # evaluate(); reader2 sets `content-visibility:auto` on every
                # paragraph, so scrolling makes previously-skipped paragraphs
                # lay out and everything below moves.  The rectangle was stale
                # by the time the mouse got there and the gate clicked a
                # different word — it reported `panāvuso` for a click aimed at
                # `phassanirodhaṁ`, which looked like a panel fault and was the
                # gate's own.
                # !!! CLOSE BEFORE MEASURING, NOT AFTER.  Closing the panel
                # removes the 380px right padding it puts on `.main`, so the
                # text REFLOWS — a rectangle measured with the panel still open
                # is stale the moment it closes, and the gate went from 0 to 19
                # failures reporting words it had never aimed at.
                pg.evaluate('''() => {
                  const x = document.getElementById('wlx'); if (x) x.click();
                  const wl = document.getElementById('wl');
                  if (wl) wl.dataset.state = 'stale';
                }''')
                pg.evaluate('''(pid) => {
                  const p = document.getElementById(pid);
                  if (p) p.scrollIntoView({block: 'center'});
                }''', pid)
                pg.wait_for_timeout(140)
                ok = pg.evaluate('''([word, pid]) => {
                  const p = document.getElementById(pid); if (!p) return null;
                  const rx = new RegExp('(^|[^a-zāīūṁṅñṭḍṇḷ’])' +
                        word.replace(/[.*+?^${}()|[\\]\\\\]/g, '\\\\$&') +
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
                              y: rect.y + rect.height / 2, text: p.textContent};
                    }
                    acc += L;
                  }
                  return null;
                }''', [word, pid])
                if not ok:
                    continue
                checked += 1
                pg.mouse.click(ok['x'], ok['y'])
                try:
                    pg.wait_for_selector('#wl[data-state="ready"]', timeout=20000)
                except Exception:
                    fails.append(f'{vol} {word}: the click opened no panel')
                    continue
                st = pg.evaluate('''() => ({
                  open: document.getElementById('wl').classList.contains('open'),
                  word: document.getElementById('wlw').textContent,
                  counts: document.getElementById('wlc').textContent,
                  tabs: Object.fromEntries([...document.querySelectorAll('#wlt button')]
                    .map(b => [b.dataset.tab, {
                      n: (b.querySelector('.wl-n') || {}).textContent || null,
                      sel: b.getAttribute('aria-selected') === 'true',
                      dis: b.classList.contains('dis')}])),
                  promoted: [...document.querySelectorAll('#wlb .wl-promo .wl-row .wl-lem')]
                    .map(e => e.textContent),
                  wordgrp: [...document.querySelectorAll('#wlb .wl-wordgrp .wl-row .wl-lem')]
                    .map(e => e.textContent),
                  body: document.getElementById('wlb').textContent,
                  // 10. NOTHING MAY SPILL OUTSIDE THE PANEL.  reader2's own
                  // sidebar already owns generic class names like `.row`
                  // (display:flex) and `.cite`; the panel's first version
                  // reused them, every gloss row came out as a squashed flex
                  // line and its citation was clipped off the right edge.  The
                  // gate could not see it because nothing measured geometry.
                  spill: (() => {
                    const wl = document.getElementById('wl').getBoundingClientRect();
                    let worst = 0, who = '';
                    document.querySelectorAll('#wlb *').forEach(e => {
                      const r = e.getBoundingClientRect();
                      if (!r.width) return;
                      const over = Math.max(r.right - wl.right, wl.left - r.left);
                      if (over > worst) { worst = over; who = e.className || e.tagName; }
                    });
                    return {px: Math.round(worst), who};
                  })()
                })''')

                def fail(m):
                    fails.append(f'{vol} {word}: {m}')

                if not st['open']:
                    fail('panel did not open'); continue
                shown = st['word']
                if fold(shown) != fold(word):
                    fail(f'header {shown!r} is not the clicked {word!r}'); continue
                # 3. counts
                fr = look('freq', shown) or look('freq', shown.lower())
                if fr:
                    if not st['counts'].startswith(str(fr[0]) + ' '):
                        fail(f'counts {st["counts"]!r} do not start with freq {fr[0]}')
                # 4. Edition count
                exp = gloss_total(shown)
                got = int((st['tabs'].get('ed') or {}).get('n') or 0)
                if got != exp:
                    fail(f'Edition count {got} != {exp} rows in the shard')
                # 6. default tab
                if exp and not (st['tabs'].get('ed') or {}).get('sel'):
                    fail('Edition is not the default tab')
                if exp and (st['tabs'].get('ped') or {}).get('sel'):
                    fail('PED opened by default — §9 says the edition speaks first')
                # PED count
                pexp = ped_total(shown)
                pgot = int((st['tabs'].get('ped') or {}).get('n') or 0)
                if pgot != pexp:
                    fail(f'PED count {pgot} != {pexp} entries in the shard')
                # 5. every promoted row really is about this paragraph
                # counts, not a set: a two-word lemma has to find two words
                pool = collections.Counter()
                for w2 in re.findall(r'[a-zāīūṁṅñṭḍṇḷ’A-ZĀĪŪṀṄÑṬḌṆḶ\'-]+',
                                     re.sub(r'\d+', ' ', ok['text'])):
                    pool[stem(w2)] += 1
                    if '-' in w2:
                        for part in w2.split('-'):
                            if part:
                                pool[stem(part)] += 1
                LEMWORDS = lambda s: [w2 for w2 in re.findall(
                    r"[a-zāīūṁṅñṭḍṇḷ’A-ZĀĪŪṀṄÑṬḌṆḶ'-]+", s) if len(w2) > 1]
                for lem in st['promoted']:
                    ws = LEMWORDS(lem)
                    need = collections.Counter(stem(w2) for w2 in ws)
                    missing = [s for s, c in need.items() if pool[s] < c]
                    if missing:
                        fail(f'promoted row {lem!r} is not in this paragraph '
                             f'(missing {missing})')
                    # a one-word lemma in the promoted groups would be the
                    # empty claim the four-group split exists to avoid
                    if len(ws) < 2:
                        fail(f'one-word lemma {lem!r} promoted as a phrase — '
                             f'"it stands in this paragraph" says nothing '
                             f'about a lemma that IS the clicked word')
                # 5b. "on the word itself" must really be the word itself
                for lem in st['wordgrp']:
                    ws = LEMWORDS(lem)
                    if len(ws) != 1 or stem(ws[0]) != stem(shown):
                        fail(f'"on the word itself" row {lem!r} is not this word')
                # 8. honesty when there is nothing
                if not exp and 'no gloss' not in st['body'].lower() \
                        and 'ninguna glosa' not in st['body'].lower():
                    if not (st['tabs'].get('ed') or {}).get('dis'):
                        fail('no gloss, but the tab neither says so nor is disabled')
                if st['spill']['px'] > 2:
                    fail(f'{st["spill"]["px"]}px of the panel body is outside the '
                         f'panel ({st["spill"]["who"]})')
                # 7. no DPD
                if 'digital pāḷi dictionary' in st['body'].lower() or 'dpd' in \
                        st['body'].lower():
                    fail('DPD text reached the panel')
        # --- 9. the phone.  390x844, the size the reader is most used at ----
        # A bottom sheet that covers the word it is explaining is no use, and a
        # tab row that leaves the viewport cannot be pressed.  Both measured
        # rather than assumed.
        ph = b.new_page(viewport={'width': 390, 'height': 844},
                        device_scale_factor=3, is_mobile=True, has_touch=True)
        ph.on('pageerror', lambda e: errors.append('phone: ' + str(e)))
        ph.goto(BASE + '/reader/reader2.html?wl=1#09Ma01/0',
                wait_until='domcontentloaded')
        try:
            ph.wait_for_selector('.para.canon', timeout=20000)
            ph.wait_for_timeout(400)
            hit = ph.evaluate('''() => {
              const p = document.querySelector('.para.canon');
              const walker = document.createTreeWalker(p, NodeFilter.SHOW_TEXT);
              let node;
              while ((node = walker.nextNode())) {
                const i = node.textContent.search(/[a-zāīūṁṅñṭḍṇḷ]{6,}/i);
                if (i >= 0) {
                  const r = document.createRange();
                  r.setStart(node, i + 1); r.setEnd(node, i + 4);
                  const rect = r.getBoundingClientRect();
                  if (rect.width > 0) return {x: rect.x + 2, y: rect.y + rect.height / 2};
                }
              }
              return null;
            }''')
            if not hit:
                fails.append('phone: no word to click')
            else:
                ph.mouse.click(hit['x'], hit['y'])
                ph.wait_for_selector('#wl[data-state="ready"]', timeout=20000)
                m = ph.evaluate('''() => {
                  const wl = document.getElementById('wl').getBoundingClientRect();
                  const mk = document.querySelector('.wl-mark');
                  const mr = mk ? mk.getBoundingClientRect() : null;
                  const tabs = [...document.querySelectorAll('#wlt button')]
                    .map(b => b.getBoundingClientRect());
                  return {sheet: document.body.classList.contains('wl-sheet'),
                          sheetTop: Math.round(wl.top), vh: innerHeight,
                          markBottom: mr ? Math.round(mr.bottom) : null,
                          markVisible: !!mr && mr.bottom < wl.top && mr.top > 40,
                          tabsIn: tabs.length > 0 &&
                                  tabs.every(r => r.right <= innerWidth + 1 &&
                                                  r.bottom <= wl.bottom),
                          tabH: tabs.length ? Math.round(tabs[0].height) : 0};
                }''')
                if not m['sheet']:
                    fails.append('phone: not a bottom sheet at 390px')
                if not m['markVisible']:
                    fails.append(f'phone: the clicked word is hidden by the sheet '
                                 f'(word bottom {m["markBottom"]}, sheet top {m["sheetTop"]})')
                if not m['tabsIn']:
                    fails.append('phone: a tab is outside the viewport or the sheet')
                if m['tabH'] and m['tabH'] < 28:
                    fails.append(f'phone: tab height {m["tabH"]}px is below a '
                                 f'usable touch target')
                checked += 1
        except Exception as e:
            fails.append(f'phone: {e}')
        ph.close()
        b.close()

    print(f'gate_reader: {checked} words clicked in reader2, {len(fails)} failures')
    for f in fails:
        print('  FAIL', f)
    if errors:
        print('page errors:', errors[:5])
    return 1 if fails or errors else 0


def run_breakpoints():
    """Sweep the real reader page and report where the side panel stops working.

    Two things are measured, not reasoned: the width of the text column with
    the panel open, and whether the panel overlaps the text.  Reported at each
    step so the threshold can be read off rather than asserted."""
    rows = []
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        for w in list(range(1500, 1020, -20)) + [1000, 960, 900, 861, 860, 800, 768, 700, 600, 500, 430, 390, 360, 320]:
            pg = b.new_page(viewport={'width': w, 'height': 900})
            pg.goto(BASE + '/reader/reader2.html?wl=1#09Ma01/0',
                    wait_until='domcontentloaded')
            try:
                pg.wait_for_selector('.para.canon', timeout=20000)
            except Exception:
                pg.close(); continue
            pg.wait_for_timeout(250)
            # the first text node of a paragraph is often the number span, one
            # character long; walk to the first node with something to click in
            hit = pg.evaluate('''() => {
              const p = document.querySelector('.para.canon');
              if (!p) return null;
              const walker = document.createTreeWalker(p, NodeFilter.SHOW_TEXT);
              let node;
              while ((node = walker.nextNode())) {
                if (/[a-zāīūṁṅñṭḍṇḷ]{6,}/i.test(node.textContent)) {
                  const i = node.textContent.search(/[a-zāīūṁṅñṭḍṇḷ]{6,}/i);
                  const r = document.createRange();
                  r.setStart(node, i + 1); r.setEnd(node, i + 4);
                  const rect = r.getBoundingClientRect();
                  if (rect.width > 0)
                    return {x: rect.x + 2, y: rect.y + rect.height / 2};
                }
              }
              return null;
            }''')
            if not hit:
                pg.close(); continue
            pg.mouse.click(hit['x'], hit['y'])
            try:
                pg.wait_for_selector('#wl[data-state="ready"]', timeout=15000)
            except Exception:
                pg.close(); continue
            m = pg.evaluate('''() => {
              const wl = document.getElementById('wl');
              const main = document.querySelector('main') || document.body;
              const p = document.querySelector('.para.canon');
              const wr = wl.getBoundingClientRect(), pr = p.getBoundingClientRect();
              const cs = getComputedStyle(p);
              return {mode: document.body.classList.contains('wl-side') ? 'side' : 'sheet',
                      panelW: Math.round(wr.width), panelH: Math.round(wr.height),
                      textW: Math.round(pr.width),
                      overlapX: Math.round(Math.max(0, pr.right - wr.left)),
                      chars: Math.round(pr.width / (parseFloat(cs.fontSize) * 0.5)),
                      sidebarShown: !!document.querySelector('.side') &&
                        getComputedStyle(document.querySelector('.side')).display !== 'none'};
            }''')
            m['w'] = w
            rows.append(m)
            pg.close()
        b.close()
    print(f'{"vw":>5} {"mode":>6} {"panel":>6} {"text":>6} {"~chars":>7} '
          f'{"overlapX":>9} {"left pane":>10}')
    for r in rows:
        print(f'{r["w"]:>5} {r["mode"]:>6} {r["panelW"]:>6} {r["textW"]:>6} '
              f'{r["chars"]:>7} {r["overlapX"]:>9} '
              f'{"shown" if r["sidebarShown"] else "hidden":>10}')
    json.dump(rows, open(os.path.join(ROOT, 'breakpoints_reader2.json'), 'w'),
              indent=1)
    return 0


if __name__ == '__main__':
    sys.exit(run_breakpoints() if '--breakpoints' in sys.argv else run_gate())
