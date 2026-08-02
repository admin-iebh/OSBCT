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
import json, glob, os, random, re, sys, collections, hashlib, io
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
LOOKUP = os.path.join(REPO, 'site', 'lookup')
ELOOKUP = os.path.join(REPO, 'site', 'lookup_eval')
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
EMAN = (json.load(open(os.path.join(ELOOKUP, 'index.json')))
        if os.path.exists(os.path.join(ELOOKUP, 'index.json')) else None)


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


_ecache = {}


def _egz(setname):
    """Is this eval set stored gzipped?  The manifest says so -- same rule
    panel.js uses.  A gate that reads the .json while the panel reads the
    .json.gz would assert against data the reader never sees."""
    return bool(EMAN and setname in (EMAN.get('gz') or []))


def _eread(path, setname):
    """Read a shard the way the panel would: .json.gz when the set is gzipped.

    !!! A BROKEN SHARD MUST DEGRADE, NOT RAISE.  `panel.js` returns null from
    `jfetch` for a shard it cannot inflate, so the reader sees an empty tab.
    If this raised instead, the negative controls would end as a traceback --
    which is not the gate reporting a failure, it is the gate falling over, and
    the two are not the same thing.  Empty here, so the emptiness is what gets
    asserted on."""
    if _egz(setname):
        gp = path + '.gz'
        if os.path.exists(gp):
            import gzip as _gz
            try:
                return json.loads(_gz.decompress(open(gp, 'rb').read()))
            except Exception:
                return {}
        return {} if not os.path.exists(path) else json.load(open(path))
    return json.load(open(path)) if os.path.exists(path) else {}


def elook(setname, key):
    """The evaluation store, read the same way the panel reads it."""
    if not EMAN:
        return None
    m = EMAN['shards'].get(setname) or {}
    f = fold(key)
    name = None
    for d in range(2, 41):
        cand = (f[:d] + '_' * d)[:d]
        if cand in m:
            name = cand
            break
    if not name:
        return None
    p = os.path.join(ELOOKUP, setname, name + '.json')
    if p not in _ecache:
        _ecache[p] = _eread(p, setname)
    o = _ecache[p]
    v = o.get(key, o.get(key.lower()))
    if isinstance(v, dict) and v.get('big') and v.get('pages'):
        merged = None
        for i in range(v['pages']):
            fp = os.path.join(ELOOKUP, setname, 'big', _safe(key) + f'.{i}.json')
            if not (os.path.exists(fp) or os.path.exists(fp + '.gz')):
                continue
            pg = (_eread(fp, setname) or {}).get('rows')
            if isinstance(pg, list):
                merged = (merged or []) + pg
            elif isinstance(pg, dict):
                merged = merged or {}
                merged.update(pg)
            else:
                merged = pg
        return merged
    return v


def _safe(k):
    return ''.join(c if c.isalnum() and c.isascii() else '-%d-' % ord(c)
                   for c in fold(k))


def eval_counts(word):
    """What the panel SHOULD show for this form, read the way the panel reads
    it -- including the paged lemma records, which is where a whole dictionary
    could silently go missing."""
    fr = elook('form', word)
    if not fr:
        return {}
    lems = [elook('lem', b) for b in fr.get('b', [])]
    lems = [x for x in lems if x]
    out = {'dpd': sum(1 for h in fr.get('h', []) if elook('dpd', h)),
           'abhi': sum(len(L['a']) for L in lems if L.get('a')),
           'peu': sum(1 for L in lems if L.get('p')),
           'ppn': sum(len(L['pn']) for L in lems if L.get('pn'))}
    # !!! COUNT DISTINCT BODIES, NOT ROWS.  The store holds the same body more
    # than once -- `build_eval.py` keyed PCED on fold(k) for each of {hw, acc,
    # cap}, so one body was stored once per distinct RAW spelling, and `fr.b`
    # then hands the panel two lemmas that fold to the same key.  Measured
    # before the fix: 60.9% of every APD row was an exact duplicate and 100% of
    # lemmas were affected.  The panel dedupes on the exact body string, so the
    # gate must expect the deduped number or it is asserting the bug.
    apd = collections.defaultdict(list)
    apd_raw = collections.Counter()
    for L in lems:
        for did, v in (L.get('apd') or {}).items():
            apd_raw[did] += len(v)
            for t in v:
                if t not in apd[did]:
                    apd[did].append(t)
    out['apd'] = {k: len(v) for k, v in apd.items()}
    out['apd_bodies'] = {k: list(v) for k, v in apd.items()}
    out['apd_total'] = sum(len(v) for v in apd.values())
    out['apd_raw_total'] = sum(apd_raw.values())
    return out


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


PEDKEY = re.compile(r'[^0-9a-zāīūṁṃṅñṭḍṇḷ]+')


def ped_key(body):
    """The panel's `pedKey`: the shipped PED set and PCED's dictionary "P" are
    the SAME dictionary, differing only in fullwidth punctuation, so they are
    merged into one section.  Compare on letters and digits alone."""
    return PEDKEY.sub('', re.sub(r'<[^>]*>', ' ', body).lower())


def ped_rows(word, exp, EVAL_ON):
    """How many rows the merged PED section should hold: the shipped rows, plus
    any "P" body not already among them."""
    keys, n = set(), 0
    for h in (look('forms', word) or []):
        for body in (look('ped', h) or []):
            keys.add(ped_key(body)); n += 1
    if EVAL_ON:
        for body in ((exp.get('apd_bodies') or {}).get('P') or []):
            k = ped_key(body)
            if k not in keys:
                keys.add(k); n += 1
    return n


VOLCACHE = {}


def run_gate(EVAL_ON=False):
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
        if any('/lookup_eval/' in u for u in reqs):
            fails.append('flag off: lookup_eval/ was fetched anyway')

        # the evaluation store must not be touched with only ?wl=1
        reqs2 = []
        pg2 = b.new_page(viewport={'width': 1280, 'height': 900})
        pg2.on('request', lambda r: reqs2.append(r.url))
        pg2.goto(BASE + '/reader/reader2.html?wl=1&wle=0#09Ma01/0',
                 wait_until='domcontentloaded')
        try:
            pg2.wait_for_selector('.para.canon', timeout=20000)
            pg2.wait_for_timeout(600)
            hit = pg2.evaluate('''() => {
              const p = document.querySelector('.para.canon');
              const w = document.createTreeWalker(p, NodeFilter.SHOW_TEXT);
              let node;
              while ((node = w.nextNode())) {
                const i = node.textContent.search(/[a-zāīūṁṅñṭḍṇḷ]{6,}/i);
                if (i >= 0) {
                  const r = document.createRange();
                  r.setStart(node, i + 1); r.setEnd(node, i + 4);
                  const rect = r.getBoundingClientRect();
                  if (rect.width > 0) return {x: rect.x + 2, y: rect.y + rect.height / 2};
                }
              }
              return null;}''')
            if hit:
                pg2.mouse.click(hit['x'], hit['y'])
                pg2.wait_for_selector('#wl[data-state="ready"]', timeout=20000)
                if any('/lookup_eval/' in u for u in reqs2):
                    fails.append('wle=0: the evaluation store was fetched anyway')
        except Exception as e:
            fails.append(f'wle=0 check: {e}')
        pg2.close()

        for vol in VOLS:
            pg.goto(BASE + f'/reader/reader2.html?wl=1&wle={1 if EVAL_ON else 0}#{vol}/0',
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
                    const body = document.getElementById('wlb');
                    // !!! CONTENT INSIDE A HORIZONTAL SCROLLER IS NOT A SPILL.
                    // getBoundingClientRect reports an element's full box even
                    // when an ancestor with overflow-x:auto is clipping it, so
                    // DPD's declension table -- deliberately made scrollable
                    // rather than squashed -- was reported as 34px outside the
                    // panel on every word that has one.  That was the gate
                    // being wrong, not the layout: the reader sees a clipped
                    // table they can drag, which is what was intended.  Skip
                    // anything a scrollable ancestor already contains.
                    const clipped = e => {
                      for (let a = e.parentElement; a && a !== body.parentElement;
                           a = a.parentElement) {
                        const ox = getComputedStyle(a).overflowX;
                        if (ox === 'auto' || ox === 'scroll' || ox === 'hidden')
                          return true;
                      }
                      return false;
                    };
                    let worst = 0, who = '';
                    document.querySelectorAll('#wlb *').forEach(e => {
                      const r = e.getBoundingClientRect();
                      if (!r.width || clipped(e)) return;
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
                exp_ed = gloss_total(shown)
                got = int((st['tabs'].get('ed') or {}).get('n') or 0)
                if got != exp_ed:
                    fail(f'Edition count {got} != {exp_ed} rows in the shard')
                # 6. default tab
                # §9's guarantee is about what a PUBLISHED build shows.  With
                # the evaluation flag on, the reader has asked for DPD first --
                # their comparison surface, their order.  With it off, this is
                # the publishable panel and the edition must be first and
                # selected; that is the assertion that matters and it is kept.
                if not EVAL_ON:
                    if exp_ed and not (st['tabs'].get('ed') or {}).get('sel'):
                        fail('Edition is not the default tab in the publishable panel')
                    if (st['tabs'].get('dict') or {}).get('sel') and exp_ed:
                        fail('the dictionary tab opened by default over the Edition')
                pexp = ped_total(shown)
                # !!! computed HERE, not further down.  Assertion 13 referenced
                # `exp` before the line that assigned it, so the whole
                # evaluation pass died with UnboundLocalError -- and because the
                # run still printed its first line, two "clean" runs were read
                # as passes when the second pass had not happened at all.
                exp = eval_counts(shown) if EVAL_ON else {}
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
                if not exp_ed and 'no gloss' not in st['body'].lower() \
                        and 'ninguna glosa' not in st['body'].lower():
                    if not (st['tabs'].get('ed') or {}).get('dis'):
                        fail('no gloss, but the tab neither says so nor is disabled')
                # 11. DPD's chips must LOOK like chips and their blocks must
                # start CLOSED.  Both are pure CSS, both silently did nothing
                # when a replace failed to match, and nothing in the gate could
                # see it: counts were right, geometry was right, and the entry
                # was a wall of text with four run-together links on top.
                if EVAL_ON and (st['tabs'].get('dpd') or {}).get('sel'):
                    chips = pg.evaluate('''() => {
                      const a = document.querySelector('#wlb a.dpd-button');
                      const h = document.querySelector('#wlb .content.hidden');
                      return {n: document.querySelectorAll('#wlb a.dpd-button').length,
                              disp: a ? getComputedStyle(a).display : null,
                              bg: a ? getComputedStyle(a).backgroundColor : null,
                              open: h ? getComputedStyle(h).display !== 'none' : false};
                    }''')
                    if chips['n']:
                        if chips['disp'] != 'inline-block':
                            fail(f'DPD chips are not styled as chips '
                                 f'(display {chips["disp"]})')
                        if chips['bg'] in ('rgba(0, 0, 0, 0)', 'transparent'):
                            fail('DPD chips have no chip background — the CSS '
                                 'is not reaching them')
                        if chips['open']:
                            fail('a DPD disclosure block is open before its '
                                 'chip was pressed')
                # 12. PRESS THINGS.  Assertions 1-11 check that controls are
                # present and styled; three separate controls were present,
                # styled, and bound to nothing at all -- the reader found the
                # DPD chips dead, and the reveals and the paging button were
                # dead beside them.  Presence is not behaviour.  Press one of
                # each and require the state to change.
                if EVAL_ON and (st['tabs'].get('dpd') or {}).get('sel'):
                    press = pg.evaluate('''() => {
                      const a = document.querySelector('#wlb a.dpd-button[data-target]');
                      if (!a) return null;
                      const t = document.querySelector('[id="' + a.dataset.target + '"]');
                      if (!t) return {err: 'chip target ' + a.dataset.target + ' does not exist'};
                      const before = getComputedStyle(t).display !== 'none';
                      a.click();
                      const after = getComputedStyle(t).display !== 'none';
                      return {label: a.textContent.trim(), before: before, after: after};
                    }''')
                    if press:
                        if press.get('err'):
                            fail(press['err'])
                        elif press['before']:
                            fail(f'DPD block "{press["label"]}" was already open')
                        elif not press['after']:
                            fail(f'pressing the DPD chip "{press["label"]}" '
                                 f'did nothing — it is not wired')
                if EVAL_ON and (st['tabs'].get('abhi') or {}).get('sel'):
                    rev = pg.evaluate('''() => {
                      const b = document.querySelector('#wlb button.wl-reveal');
                      if (!b) return null;
                      const t = b.nextElementSibling;
                      if (!t) return {err: 'reveal button has nothing after it'};
                      const before = !t.classList.contains('wl-hidden');
                      b.click();
                      return {before: before,
                              after: !t.classList.contains('wl-hidden')};
                    }''')
                    if rev:
                        if rev.get('err'):
                            fail(rev['err'])
                        elif rev['before']:
                            fail('an attributed reveal was open before it was pressed')
                        elif not rev['after']:
                            fail('pressing the reveal did nothing — it is not wired')
                # 13. EVERY DICTIONARY IN THE DATA MUST GET A SECTION.  The
                # count on the tab and the sections in the body are computed by
                # different paths -- one from the record, one from the
                # manifest's order list -- so they can disagree, and they did:
                # a stale manifest with no `apd_order` gave "APD 22" over a
                # single PED section.  Assert them against each other.
                # !!! OPEN THE TAB.  The first version of this assertion was
                # conditional on the APD tab being SELECTED -- and with the
                # evaluation flag on the default tab is DPD, so it was never
                # selected, the assertion never ran, and the negative control
                # passed.  A skipped assertion is worse than no assertion: it
                # reports success.  Click the tab, then look.
                if EVAL_ON and not (st['tabs'].get('dict') or {}).get('dis'):
                    pg.evaluate('''() => {
                      const b = document.querySelector('#wlt button[data-tab="dict"]');
                      if (b) b.click();
                    }''')
                    pg.wait_for_timeout(120)
                    secs = pg.evaluate('''() => [...document.querySelectorAll(
                      '#wlb .wl-sec')].map(e => e.id.replace('wl-s-',''))''')
                    # "P" is the PTS P-E Dictionary -- the SAME dictionary as the
                    # shipped PED set, and it used to draw a SECOND section
                    # carrying the same entry in fullwidth punctuation.  For
                    # `Nandane` that put one PED entry on screen five times.  It
                    # is merged into `_ped` now, so it must NOT appear alone.
                    want = set((exp.get('apd') or {}).keys()) - {'P'}
                    missing = sorted(want - set(secs))
                    if missing:
                        fail(f'APD tab draws no section for {missing} '
                             f'(sections drawn: {secs})')
                    if 'P' in secs:
                        fail('PED is drawn twice: "P" has its own section beside '
                             '_ped, and they are the same dictionary')
                    if want and not secs:
                        fail('APD tab has a count but drew no sections at all')
                    # 13b. NO SECTION MAY SHOW THE SAME BODY TWICE.  This is the
                    # guarantee the dedup exists for, and nothing else asserts
                    # it: counts and sections were both right while every entry
                    # was on screen two or three times.
                    dup = pg.evaluate('''() => {
                      const out = [];
                      document.querySelectorAll('#wlb .wl-sec').forEach(sec => {
                        const seen = {}, id = sec.id.replace('wl-s-','');
                        sec.querySelectorAll('.wl-row').forEach(r => {
                          const t = (r.innerText || '').replace(/^\s*\d+\.\s*/, '')
                                     .replace(/\s+/g, ' ').trim();
                          if (!t) return;
                          if (seen[t]) out.push(id); else seen[t] = 1;
                        });
                      });
                      return out;
                    }''')
                    if dup:
                        c = collections.Counter(dup)
                        fail(f'a section shows the same entry twice: '
                             f'{sorted(c.items())}')
                # 14. THE GLOSS CITATIONS ARE LINKS, AND THEY MUST LAND.
                # A citation link that 404s or scrolls nowhere is worse than
                # plain text -- it makes the reader doubt the reference.  So
                # this does not check that anchors EXIST (they did, in the
                # version that pointed at paragraph numbers instead of
                # ordinals, and every one of them was wrong).  It reads the
                # href, resolves it against the volume's own ord map, and
                # requires the target paragraph to be real.
                # !!! OPEN THE GLOSS TAB AND REQUIRE LINKS TO BE THERE.
                # The first version of this assertion only iterated whatever
                # anchors it found -- so suppressing every link entirely made it
                # pass with 0 failures, exactly the way assertion 13 once passed
                # by never running.  Negative control A proved it.  A word with
                # gloss rows MUST produce at least one citation link.
                pg.evaluate('''() => {
                  const b = document.querySelector('#wlt button[data-tab="ed"]');
                  if (b && !b.classList.contains('dis')) b.click();
                }''')
                pg.wait_for_timeout(120)
                links = pg.evaluate('''() => [...document.querySelectorAll(
                  '#wlb .wl-cite a.wl-go')].map(a => ({
                    href: a.getAttribute('href'),
                    text: (a.textContent || '').trim()}))''')
                n_cite = pg.evaluate(
                    "() => document.querySelectorAll('#wlb .wl-cite').length")
                if exp_ed and n_cite and not links:
                    fail(f'the Gloss tab shows {n_cite} citations and not one of '
                         f'them is a link into the passage')
                for a in links[:6]:
                    m = re.match(r'^#([^/]+)/(\d+)$', a['href'] or '')
                    if not m:
                        fail(f'gloss citation link is malformed: {a["href"]!r}')
                        continue
                    tvol, tord = m.group(1), int(m.group(2))
                    vpath = os.path.join(REPO, 'site', tvol + '.json')
                    if not os.path.exists(vpath):
                        fail(f'gloss citation points at a volume that is not '
                             f'published: {tvol}')
                        continue
                    paras = VOLCACHE.get(tvol)
                    if paras is None:
                        paras = json.load(open(vpath)).get('paragraphs') or []
                        VOLCACHE[tvol] = paras
                    if not (0 <= tord < len(paras)):
                        fail(f'gloss citation {a["href"]} is out of range: '
                             f'{tvol} has {len(paras)} paragraphs')
                        continue
                    # the printed number in the citation must be the number of
                    # the paragraph the ordinal actually lands on
                    want_n = paras[tord].get('n')
                    mm = re.search(r'§(\d+)', a['text'])
                    if mm and want_n is not None and int(mm.group(1)) != want_n:
                        fail(f'gloss citation says §{mm.group(1)} but '
                             f'{tvol}/{tord} is §{want_n}')
                if st['spill']['px'] > 2:
                    fail(f'{st["spill"]["px"]}px of the panel body is outside the '
                         f'panel ({st["spill"]["who"]})')
                # 9. THE EVALUATION FLAG.  Off, none of those tabs may exist
                # and nothing may be fetched from lookup_eval/.  On, every tab's
                # count must match the evaluation store.
                # The eleven tabs are now three: Edition, Abhidhāna, and one
                # `dict` tab holding the rest as sections.  Its count is the
                # sum of what is inside it, and with the flag off that is PED
                # alone -- so the same assertion covers both states.
                # !!! THE BADGE COUNTS DICTIONARIES, NOT ENTRIES -- the reader
                # clicked `Nandane`, the tab said 102, and 102 was 1 PED + 100
                # APD rows (of which only 50 were distinct) + 1 DPPN.  On an
                # aggregate tab the number answers "how many dictionaries have
                # this word"; the per-section entry totals are in the jump strip
                # and the headings.  With the flag OFF the same tab IS one
                # dictionary, so there it stays an entry count -- "PED 1" would
                # say nothing.
                n_ped_rows = ped_rows(shown, exp, EVAL_ON)
                if EVAL_ON:
                    want_dict = len(set((exp.get('apd') or {}).keys()) - {'P'})
                    if n_ped_rows:
                        want_dict += 1
                    if exp.get('ppn', 0):
                        want_dict += 1
                else:
                    want_dict = pexp
                got_dict = int((st['tabs'].get('dict') or {}).get('n') or 0)
                if got_dict != want_dict:
                    fail(f'{"APD" if EVAL_ON else "PED"} tab shows {got_dict}, '
                         f'sources give {want_dict} '
                         f'({"dictionaries" if EVAL_ON else "entries"})')
                if not EVAL_ON:
                    stray = [t for t in ('abhi', 'peu', 'dpd') if t in st['tabs']]
                    if stray:
                        fail(f'evaluation flag off but the tabs are there: {stray}')
                else:
                    got_ab = int((st['tabs'].get('abhi') or {}).get('n') or 0)
                    if got_ab != exp.get('abhi', 0):
                        fail(f'Abhidhāna tab shows {got_ab}, store has '
                             f'{exp.get("abhi", 0)}')
                    got_dpd = int((st['tabs'].get('dpd') or {}).get('n') or 0)
                    if got_dpd != exp.get('dpd', 0):
                        fail(f'DPD tab shows {got_dpd}, store has '
                             f'{exp.get("dpd", 0)}')
                # 7. NO DPD WHERE IT MAY NOT BE.  With the evaluation flag
                # off, not a character of it anywhere -- that is the §9
                # guarantee for anything publishable.  With the flag on it is
                # allowed, but only inside its own section of the dictionary
                # tab, never loose in the Edition or Abhidhāna tabs.
                low = st['body'].lower()
                if not EVAL_ON:
                    if 'digital pāḷi dictionary' in low or 'dpd' in low:
                        fail('DPD text reached the panel with the flag off')
                else:
                    # DPD now has its own TAB rather than a section inside
                    # the dictionary tab, so the containment test is "the DPD
                    # tab is the one on screen", not "inside #wl-s-dpd".  What
                    # is still asserted is the thing that matters: DPD markup
                    # never appears while some OTHER tab is selected.
                    where = pg.evaluate('''() => {
                      const sel = document.querySelector('#wlt button[aria-selected="true"]');
                      const tab = sel ? sel.dataset.tab : null;
                      if (tab === 'dpd') return [];
                      const hits = [];
                      document.querySelectorAll('#wlb *').forEach(e => {
                        if (/dpd/i.test(String(e.className))) hits.push(String(e.className));
                      });
                      return hits.slice(0, 3);
                    }''')
                    if where:
                        fail(f'DPD markup showing under another tab: {where}')
        # --- 10. RECURSIVE LOOKUP.  A Pāḷi word inside the panel is a word
        # like any other: clicking it looks it up, the back button appears, and
        # back returns to where the reader was.  It must be a no-op for a word
        # the corpus does not have, rather than an empty panel.
        try:
            pg.goto(BASE + '/reader/reader2.html?wl=1&wle=1#09Ma01/0',
                    wait_until='domcontentloaded')
            pg.wait_for_selector('.para.canon', timeout=20000)
            pg.wait_for_timeout(400)
            ok = pg.evaluate('''() => {
              for (const p of document.querySelectorAll('.para.canon')) {
                const i = p.textContent.indexOf('bhikkhave'); if (i < 0) continue;
                const w = document.createTreeWalker(p, NodeFilter.SHOW_TEXT);
                let acc = 0, node;
                while ((node = w.nextNode())) {
                  const L = node.textContent.length;
                  if (acc + L > i && i - acc >= 0) {
                    const r = document.createRange();
                    r.setStart(node, i - acc); r.setEnd(node, Math.min(i - acc + 4, L));
                    p.scrollIntoView({block: 'center'});
                    const rect = r.getBoundingClientRect();
                    if (rect.width > 0 && rect.top > 60 && rect.bottom < innerHeight - 20)
                      return {x: rect.x + 2, y: rect.y + rect.height / 2};
                  }
                  acc += L;
                }
              }
              return null;}''')
            if not ok:
                fails.append('recursive: no word to start from')
            else:
                pg.mouse.click(ok['x'], ok['y'])
                pg.wait_for_selector('#wl[data-state="ready"]', timeout=20000)
                first = pg.evaluate("document.getElementById('wlw').textContent")
                backshown = pg.evaluate(
                    "document.getElementById('wlback').classList.contains('on')")
                if backshown:
                    fails.append('recursive: the back button is showing before any jump')
                # click a Pāḷi word inside the Edition tab's gloss text
                inner = pg.evaluate('''() => {
                  const g = document.querySelector('#wlb .wl-g');
                  if (!g) return null;
                  const w = document.createTreeWalker(g, NodeFilter.SHOW_TEXT);
                  let node;
                  while ((node = w.nextNode())) {
                    const m = /[a-zāīūṁṅñṭḍṇḷ]{6,}/i.exec(node.textContent);
                    if (m) {
                      const r = document.createRange();
                      r.setStart(node, m.index + 1); r.setEnd(node, m.index + 4);
                      const rect = r.getBoundingClientRect();
                      if (rect.width > 0)
                        return {x: rect.x + 2, y: rect.y + rect.height / 2,
                                word: m[0]};
                    }
                  }
                  return null;}''')
                if inner:
                    pg.evaluate("document.getElementById('wl').dataset.state='stale'")
                    pg.mouse.click(inner['x'], inner['y'])
                    try:
                        pg.wait_for_selector('#wl[data-state="ready"]', timeout=8000)
                    except Exception:
                        pass
                    st2 = pg.evaluate('''() => ({
                      word: document.getElementById('wlw').textContent,
                      back: document.getElementById('wlback').classList.contains('on')
                    })''')
                    if st2['word'] != first:
                        # it jumped: the back button must be there and must work
                        if not st2['back']:
                            fails.append('recursive: jumped but no back button')
                        else:
                            pg.evaluate("document.getElementById('wlback').click()")
                            pg.wait_for_selector('#wl[data-state="ready"]', timeout=8000)
                            back = pg.evaluate("document.getElementById('wlw').textContent")
                            if back != first:
                                fails.append(f'recursive: back went to {back!r}, '
                                             f'not {first!r}')
                    checked += 1
        except Exception as e:
            fails.append(f'recursive: {e}')

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

    print(f'gate_reader [eval {"on" if EVAL_ON else "off"}]: {checked} words '
          f'clicked in reader2, {len(fails)} failures')
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


def check_version():
    """RULE 1, MECHANISED.  `WLV` in panel.js and the `?v=` on its script tag
    must agree with each other AND be bumped whenever the data is rebuilt.

    The fault this exists for: for most of a day nothing the panel fetched was
    versioned, and the reader saw a tab counting 22 entries and drawing one --
    their browser was serving an `index.json` from hours earlier.  No assertion
    could see it, because every count the gate checked was read from disk, not
    from what the browser had cached.

    So: digest the two manifests, and remember the digest beside the WLV that
    was current when it was taken.  If the data has changed and WLV has not,
    that is the fault, and it fails here.  Bumping WLV is the acknowledgement,
    and re-records the digest.
    """
    fails = []
    js = os.path.join(REPO, 'site', 'reader', 'panel.js')
    html = os.path.join(REPO, 'site', 'reader', 'reader2.html')
    m = re.search(r"var WLV = '([^']+)'", io.open(js, encoding='utf-8').read())
    if not m:
        return ['panel.js: no `var WLV = ...` — the version constant is gone']
    wlv = m.group(1)
    h = re.search(r"panel\.js\?v=([^\"']+)", io.open(html, encoding='utf-8').read())
    if not h:
        fails.append('reader2.html: panel.js script tag carries no ?v=')
    elif h.group(1) != wlv:
        fails.append(f'version drift: panel.js WLV={wlv} but reader2.html '
                     f'?v={h.group(1)} — the browser will cache one and fetch '
                     f'the other')

    dig = hashlib.sha1()
    for path in (os.path.join(LOOKUP, 'index.json'),
                 os.path.join(ELOOKUP, 'index.json')):
        dig.update(open(path, 'rb').read() if os.path.exists(path) else b'-')
    digest = dig.hexdigest()[:16]

    stamp = os.path.join(ROOT, 'data_version.json')
    rec = json.load(open(stamp)) if os.path.exists(stamp) else None
    if rec is None:
        json.dump({'wlv': wlv, 'digest': digest}, open(stamp, 'w'), indent=1)
        print(f'  version stamp recorded: WLV={wlv} digest={digest}')
    elif rec.get('digest') != digest and rec.get('wlv') == wlv:
        fails.append(f'the lookup data changed (digest {rec.get("digest")} -> '
                     f'{digest}) but WLV is still {wlv} — bump WLV in panel.js '
                     f'and the ?v= in reader2.html, or the reader keeps the '
                     f'old shards')
    elif rec.get('wlv') != wlv:
        json.dump({'wlv': wlv, 'digest': digest}, open(stamp, 'w'), indent=1)
        print(f'  version stamp updated: WLV={wlv} digest={digest}')
    return fails



# ---------------------------------------------------------------- TABS ----
# 12. EVERY TAB RENDERS, WITH A COUNT AND ITS SHARING LINE.
#
# !!! THE OLD DPD ASSERTION WAS VACUOUS AND REPORTED SUCCESS.  Assertion 6
# compares the DPD tab's badge against `elook('dpd', h)` -- BOTH SIDES READ THE
# SAME STORE.  With `site/lookup_eval/dpd/` absent (it is gitignored, so it is
# absent on any clean checkout, which is what Actions publishes) the store gave
# 0, the tab showed 0, and the gate reported 0 failures while the tab the whole
# exercise is about did not exist.  Same shape as assertion 14 iterating an
# empty list.
#
# So this pass asserts something the store cannot satisfy by being empty:
#   * the tab is ENABLED and its badge is > 0;
#   * pressing it renders a non-empty body;
#   * that body carries a `.wl-rights` sharing line with text in it;
#   * and the pass FAILS IF IT NEVER SAW A LIVE DPD TAB AT ALL -- the
#     non-vacuity guard, which is the assertion that the assertion ran.

TAB_MEASURE = r'''([word, pid]) => {
  const p = document.getElementById(pid); if (!p) return null;
  const rx = new RegExp('(^|[^a-zāīūṁṅñṭḍṇḷ’])' +
        word.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') +
        '($|[^a-zāīūṁṅñṭḍṇḷ’0-9])', 'i');
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
      return {x: rect.x + Math.min(rect.width / 2, 5), y: rect.y + rect.height / 2};
    }
    acc += L;
  }
  return null;
}'''

TAB_MIN_LIVE_DPD = 3


def _tab_words():
    """Canon words the store says have both DPD and Abhidhāna data."""
    out = []
    for vol in VOLS[:4]:
        p = os.path.join(REPO, 'site', vol + '.json')
        if not os.path.exists(p):
            continue
        seen, n_here = set(), 0
        for pp in json.load(open(p))['paragraphs'][:600]:
            for w in re.findall(r'[a-zāīūṁṅñṭḍṇḷ]{5,}', pp.get('text') or '', re.I):
                if w.lower() in seen or n_here >= 2:
                    continue
                seen.add(w.lower())
                e = eval_counts(w)
                if e.get('dpd', 0) > 0 and e.get('abhi', 0) > 0:
                    out.append((vol, w, e)); n_here += 1
    return out


def run_tabs(pinned=None):
    """`pinned` fixes the word list.

    !!! WITHOUT IT THE NEGATIVE CONTROLS DO NOT FIRE, AND THAT IS NOT A
    HYPOTHETICAL -- all three passed clean the first time they were run.  This
    pass chooses its words by asking the store which ones have DPD data; break
    a shard and those words stop qualifying, so it quietly PICKS AROUND THE
    DAMAGE and reports 8 live DPD tabs on a store that has just been corrupted.
    An adaptive sample cannot be its own control.  The controls pin the words
    first, then break exactly those words\' shards."""
    rng = random.Random(SEED)
    fails, checked, live_dpd = [], 0, 0

    def fail(m):
        fails.append(m)
        print(f'  FAIL tabs: {m}')

    # words that the store says have DPD, Abhidhāna and dictionary data, so a
    # zero badge is a real defect and not just a word nothing covers
    want = pinned if pinned is not None else _tab_words()
    if len(want) < TAB_MIN_LIVE_DPD:
        fail(f'could not find {TAB_MIN_LIVE_DPD} canon words with DPD data in the '
             f'store — found {len(want)}. The store is empty or unreadable; '
             f'every DPD assertion below would be vacuous.')
        print(f'gate_reader [tabs]: {len(fails)} failures')
        return 1 if fails else 0

    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page(viewport={'width': 1400, 'height': 900})
        errors = []
        pg.on('pageerror', lambda e: errors.append(str(e)))
        for vol, word, exp in want:
            pg.goto(BASE + f'/reader/reader2.html?wl=1&wle=1#{vol}/0',
                    wait_until='domcontentloaded')
            try:
                pg.wait_for_selector('.para.canon', timeout=30000)
            except Exception:
                fail(f'{vol}: no canon rendered')
                continue
            pg.wait_for_timeout(300)
            # Click the word in the rendered text, the way a reader does and
            # the way the rest of this gate does -- no test hook in shipped code.
            # plain substring is enough to pick the paragraph; TAB_MEASURE does
            # the exact word-boundary work when it aims the mouse
            pid = pg.evaluate('''(w) => {
              const needle = w.toLowerCase();
              for (const p of document.querySelectorAll('.para.canon'))
                if (p.textContent.toLowerCase().indexOf(needle) >= 0) return p.id;
              return null;
            }''', word)
            if not pid:
                continue
            pg.evaluate('''(pid) => {
              const p = document.getElementById(pid);
              if (p) p.scrollIntoView({block: 'center'});
            }''', pid)
            pg.wait_for_timeout(140)
            ok = pg.evaluate(TAB_MEASURE, [word, pid])
            if not ok:
                continue
            pg.mouse.click(ok['x'], ok['y'])
            try:
                pg.wait_for_selector('#wl[data-state="ready"]', timeout=20000)
            except Exception:
                fail(f'{word}: panel never became ready')
                continue
            checked += 1
            tabs = pg.evaluate('''() => Object.fromEntries(
              [...document.querySelectorAll('#wlt button')].map(b => [b.dataset.tab, {
                n: parseInt(((b.querySelector('.wl-n')||{}).textContent||'0'), 10) || 0,
                dis: b.classList.contains('dis')}]))''')
            if 'dpd' not in tabs:
                fail(f'{word}: no DPD tab with the evaluation flag on')
                continue
            if tabs['dpd']['dis'] or tabs['dpd']['n'] <= 0:
                fail(f'{word}: DPD tab disabled/zero ({tabs["dpd"]}) but the store '
                     f'holds {exp.get("dpd")} entries — the shards are not being read')
                continue
            live_dpd += 1
            for tab, info in tabs.items():
                if info['dis']:
                    continue
                pg.evaluate('''(t) => {
                  const b = document.querySelector('#wlt button[data-tab="'+t+'"]');
                  if (b) b.click();
                }''', tab)
                pg.wait_for_timeout(160)
                got = pg.evaluate('''() => {
                  const b = document.getElementById('wlb');
                  const r = b.querySelector('.wl-rights'), s = b.querySelector('.wl-src');
                  return {len: (b.textContent||'').trim().length,
                          rights: r ? (r.textContent||'').trim() : null,
                          src: s ? (s.textContent||'').trim() : null};
                }''')
                if got['len'] < 20:
                    fail(f'{word} [{tab}]: tab has a count of {info["n"]} but its '
                         f'body is empty ({got["len"]} chars)')
                if not got['src']:
                    fail(f'{word} [{tab}]: no attribution line')
                if tab in ('dpd', 'abhi') and not got['rights']:
                    fail(f'{word} [{tab}]: no sharing-terms line (.wl-rights) — '
                         f'the licence must ride with the source')
        if errors:
            fail(f'page errors: {errors[:2]}')
        b.close()

    # THE NON-VACUITY GUARD
    if live_dpd < TAB_MIN_LIVE_DPD:
        fail(f'only {live_dpd} of {checked} words produced a live DPD tab; this '
             f'pass proves nothing below {TAB_MIN_LIVE_DPD}')
    print(f'gate_reader [tabs]: {checked} words, {live_dpd} with a live DPD tab, '
          f'{len(fails)} failures')
    return 1 if fails else 0


# ------------------------------------------------- NEGATIVE CONTROLS ------
# A gate is only worth its runtime if it FAILS when the thing it guards is
# broken.  Rule 2 of the handoff, and assertion 14's history: a check that
# iterates an empty list reports success.
#
# The weak control is "delete the file" -- almost anything catches that.  The
# ones that matter here are the two failure modes gzip actually has in the
# wild: a TRUNCATED shard (interrupted upload, partial write) and a CORRUPT
# shard (a flipped byte).  Both still exist, still have the gzip magic, still
# return HTTP 200, and both must end as an empty DPD tab that the gate calls a
# failure -- not as garbled text on a reader's screen.
def _dpd_shard_paths(words):
    """The .json.gz files the tabs pass will actually read for these words."""
    out = []
    for w in words:
        fr = elook('form', w) or {}
        for h in (fr.get('h') or []):
            m = (EMAN['shards'].get('dpd') or {})
            f = fold(h)
            for d in range(2, 41):
                cand = (f[:d] + '_' * d)[:d]
                if cand in m:
                    p = os.path.join(ELOOKUP, 'dpd', cand + '.json.gz')
                    if os.path.exists(p) and p not in out:
                        out.append(p)
                    break
    return out


def run_negative_controls():
    print('\n--- negative controls: the tabs pass must FAIL on broken shards ---')
    # the same words the tabs pass picks, so the mutation is guaranteed to be
    # on the read path rather than on some shard nobody opens
    pinned = _tab_words()
    paths = _dpd_shard_paths([w for _, w, _ in pinned])
    print(f'  pinned {len(pinned)} words -> {len(paths)} DPD shards on the read path')
    if not paths:
        print('  FAIL: no DPD shard is on the read path — the control itself is vacuous')
        return 1

    def mutate_truncate(b):
        return b[:max(12, int(len(b) * 0.55))]

    def mutate_corrupt(b):
        a = bytearray(b)
        a[len(a) // 2] ^= 0xff        # flip a byte in the DEFLATE stream
        return bytes(a)

    def mutate_delete(b):
        return None

    bad = 0
    for name, mut in (('truncated .gz', mutate_truncate),
                      ('corrupt .gz', mutate_corrupt),
                      ('missing .gz', mutate_delete)):
        saved = {p: open(p, 'rb').read() for p in paths}
        try:
            for p in paths:
                nb = mut(saved[p])
                if nb is None:
                    os.remove(p)
                else:
                    open(p, 'wb').write(nb)
            _ecache.clear()
            rc = run_tabs(pinned=pinned)
            if rc == 0:
                print(f'  NEGATIVE CONTROL DID NOT FIRE: {name} — the gate passed '
                      f'with {len(paths)} broken shards on the read path')
                bad += 1
            else:
                print(f'  negative control fired: {name} ({len(paths)} shards)')
        finally:
            for p, b in saved.items():
                open(p, 'wb').write(b)
            _ecache.clear()
    print(f'--- negative controls: {bad} did not fire ---')
    return 1 if bad else 0

if __name__ == '__main__':
    if '--breakpoints' in sys.argv:
        sys.exit(run_breakpoints())
    vf = check_version()
    for f in vf:
        print(f'  FAIL version: {f}')
    print(f'gate_reader [version]: {len(vf)} failures')
    # both states of the evaluation flag, because "off" is an assertion too
    if '--tabs-only' in sys.argv:
        sys.exit(run_tabs())
    if '--negative-controls' in sys.argv:
        sys.exit(run_negative_controls())
    rc = run_gate(EVAL_ON=False)
    if '--no-eval' not in sys.argv:
        rc |= run_gate(EVAL_ON=True)
        rc |= run_tabs()
    sys.exit(rc | (1 if vf else 0))
