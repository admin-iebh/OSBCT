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

        # --- 1. THE OFF SWITCH.  Inverted 2026-08-02, NOT deleted. -----------
        #
        # This used to assert that WITHOUT `?wl=1` there is no #wl node and no
        # lookup/ request — the panel being off by default.  The default is now
        # ON, because off-by-default did not mean "optional", it meant
        # UNREACHABLE: nothing anywhere in site/ linked to `?wl=1`, so no
        # visitor ever arrived at the panel at all.
        #
        # !!! THE ASSERTION IS INVERTED, NOT REMOVED, AND THAT IS THE POINT.
        # What it really guarantees is not "the default is off" but "there is a
        # way to switch this off, and switching it off is TOTAL — no node, no
        # fetch, no listener".  That is a §9 guarantee: it is what lets the page
        # be served to a reader who wants only the edition.  Deleting the
        # assertion along with the default would retire the guarantee silently
        # and nothing would ever tell us.  So it now aims at `?wl=0`.
        #
        # Two separate claims, and both are checked below, because the flag is
        # persisted: `?wl=0` must work on a cold visit, and it must STILL be off
        # on the next visit with no query string at all.
        reqs = []
        pg.on('request', lambda r: reqs.append(r.url))
        pg.goto(BASE + '/reader/reader2.html?wl=0', wait_until='domcontentloaded')
        pg.wait_for_timeout(1200)
        if pg.evaluate("!!document.getElementById('wl')"):
            fails.append('wl=0: the panel node exists anyway')
        if any('/lookup/' in u for u in reqs):
            fails.append('wl=0: lookup/ was fetched anyway')
        if any('/lookup_eval/' in u for u in reqs):
            fails.append('wl=0: lookup_eval/ was fetched anyway')
        # the choice has to survive the next page load, or "off" is one
        # navigation deep and the reader who turned it off gets it back
        reqs_sticky = []
        pg.on('request', lambda r: reqs_sticky.append(r.url))
        pg.goto(BASE + '/reader/reader2.html', wait_until='domcontentloaded')
        pg.wait_for_timeout(1000)
        if pg.evaluate("!!document.getElementById('wl')"):
            fails.append('wl=0 did not stick: the panel is back on the next '
                         'visit with no query string')
        if any('/lookup/' in u for u in reqs_sticky):
            fails.append('wl=0 did not stick: lookup/ was fetched on the next '
                         'visit')
        # --- 1b. AND THE DEFAULT REALLY IS ON, for a reader with no history. --
        # The complement of the above, and the assertion the whole change is
        # for.  A fresh context — no localStorage — must get the panel without
        # asking for it.  Without this, reverting the default to off would pass
        # the gate clean, which is how it stayed unreachable through four gate
        # passes in the first place.
        fresh = b.new_context(viewport={'width': 1280, 'height': 900})
        fpg = fresh.new_page()
        fpg.goto(BASE + '/reader/reader2.html#09Ma01/0',
                 wait_until='domcontentloaded')
        try:
            fpg.wait_for_selector('.para.canon', timeout=20000)
            fpg.wait_for_timeout(700)
            if not fpg.evaluate("!!document.getElementById('wl')"):
                fails.append('DEFAULT: a first-time reader with no query string '
                             'and no localStorage gets no panel node — the '
                             'feature is unreachable again')
        except Exception as e:
            fails.append(f'default-on check: {e}')
        fresh.close()

        # --- 1c. THE OTHER DEFAULT: every tab, for a first-time reader. -------
        # `wle` now defaults ON too, so a fresh context must get the full tab
        # row without asking.  Same reasoning as 1b: without this, a revert to
        # off-by-default passes the gate clean and the tabs quietly vanish for
        # everyone while every other assertion stays green.
        # Conditional on the evaluation store existing, because it is gitignored
        # and absent on a clean checkout — a silent skip here would be the
        # vacuous-pass fault over again, so it says which it did.
        if EMAN is not None:
            f2 = b.new_context(viewport={'width': 1280, 'height': 900})
            fp2 = f2.new_page()
            fp2.goto(BASE + '/reader/reader2.html#09Ma01/0',
                     wait_until='domcontentloaded')
            try:
                fp2.wait_for_selector('.para.canon', timeout=20000)
                fp2.wait_for_timeout(600)
                h2 = fp2.evaluate('''() => {
                  const p = document.querySelector('.para.canon');
                  const w = document.createTreeWalker(p, NodeFilter.SHOW_TEXT);
                  let n;
                  while ((n = w.nextNode())) {
                    const i = n.textContent.search(/[a-zāīūṁṅñṭḍṇḷ]{6,}/i);
                    if (i >= 0) { const r = document.createRange();
                      r.setStart(n, i + 1); r.setEnd(n, i + 4);
                      const q = r.getBoundingClientRect();
                      if (q.width > 0) return {x: q.x + 2, y: q.y + q.height / 2}; }
                  } return null;}''')
                if h2:
                    fp2.mouse.click(h2['x'], h2['y'])
                    fp2.wait_for_selector('#wl[data-state="ready"]', timeout=20000)
                    tabs_seen = fp2.evaluate(
                        "() => [...document.querySelectorAll('#wlt button')]"
                        ".map(b => b.dataset.tab)")
                    for t in ('dpd', 'abhi', 'dict', 'ed'):
                        if t not in tabs_seen:
                            fails.append(
                                f'DEFAULT TABS: a first-time reader with no query '
                                f'string gets no {t!r} tab (saw {tabs_seen}) — the '
                                f'evaluation tabs are hidden again')
            except Exception as e:
                fails.append(f'default-tabs check: {e}')
            f2.close()
        else:
            print('  note: 1c NOT EXERCISED — site/lookup_eval/ absent, so the '
                  'default tab row cannot be checked here')

        # the evaluation store must not be touched with ?wle=0
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
                # !!! 5c. THE NON-VACUITY GUARD FOR 5 AND 5b.  Both loops above
                # iterate a list read out of the DOM with `.wl-promo .wl-row
                # .wl-lem`, and for as long as assertion 5 has existed that
                # selector matched NOTHING: `rowHtml` emitted `class="lem g"`,
                # unprefixed, while the panel's CSS and this gate both look for
                # `wl-lem`/`wl-g`.  28 promoted rows on screen, 0 seen here, 0
                # failures reported — and assertion 5 is the one the docstring
                # calls "the whole design claim of the Edition tab and the one
                # thing a reader cannot verify".  Third instance of this exact
                # shape after assertions 14 and 6.  So: if the panel drew boxed
                # rows, this pass MUST have found lemmas in them.
                n_boxed = pg.evaluate(
                    "() => document.querySelectorAll('#wlb .wl-promo .wl-row,'"
                    " + ' #wlb .wl-wordgrp .wl-row').length")
                if n_boxed and not (st['promoted'] or st['wordgrp']):
                    fail(f'{n_boxed} boxed rows are on screen but the gate '
                         f'extracted 0 lemmas from them — assertion 5 is '
                         f'iterating an empty list and cannot fail')
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

# ------------------------------------------------------- TYPE & CONTRAST ----
# 15. THE PANEL FOLLOWS THE READER, THE PĀḶI IS NOT SHRUNK, AND THE COLOURS
#     REACH AA.
#
# !!! THIS PASS PRESSES A+ INSTEAD OF READING A NUMBER ONCE.  That is the whole
# point of it, and it is the §0 lesson applied in advance rather than after the
# fact.  An assertion that merely reads `getComputedStyle('.wl-b').fontSize` and
# finds 13.5px would be satisfied by a hardcoded 13.5px -- which is exactly the
# bug this change exists to remove.  The claim is not "the panel body is some
# size", it is "the panel body MOVES WHEN THE READER MOVES IT", and only
# pressing the control can tell those apart.  Six controls were once present,
# styled, counted and dead while the gate read 0 failures; a design pass is the
# likeliest place to reintroduce that, so this pass presses.
#
# It asserts, in order:
#   A1  the panel body tracks --rsize     (pressed: A+ x3 must move it)
#   A2  panel Pāḷi == clicked Pāḷi        (.wl-g is not smaller than .wl-b)
#   A4  Burmese is at least 16px          (and stays the largest in the body)
#   A5  .wl-sub / .wl-why >= 11px, and .wl-why is --fg and not --mut
#   A3  no request reaches Google, the local woff2 actually loads, and the
#       DIACRITICS specifically are covered -- not merely the family name
#   B   every text token clears 4.5:1 against BOTH --panel and --app, in BOTH
#       themes, and white-on-token clears 4.5:1 where white text sits on one

TYPE_READ = r'''() => {
  const cs = s => { const e = document.querySelector(s); return e ? getComputedStyle(e) : null; };
  const px = s => { const c = cs(s); return c ? parseFloat(c.fontSize) : null; };
  const root = getComputedStyle(document.documentElement);
  const tok = n => (root.getPropertyValue(n) || '').trim();
  const why = cs('#wl .wl-why');
  return {
    rsize:  tok('--rsize'),
    para:   px('.para.canon'),
    body:   px('#wl .wl-b'),
    g:      px('#wl .wl-g:not(.wl-lem)'),   // the GLOSS, not the lemma span
                                            // (the lemma carries both classes
                                            //  and is first in the DOM)
    lem:    px('#wl .wl-lem'),
    my:     px('#wl .wl-my'),
    sub:    px('#wl .wl-sub'),
    whyPx:  why ? parseFloat(why.fontSize) : null,
    whyCol: why ? why.color : null,
    fgCol:  (() => { const d = document.createElement('span');
                     d.style.color = 'var(--fg)'; document.body.appendChild(d);
                     const c = getComputedStyle(d).color; d.remove(); return c; })(),
    mutCol: (() => { const d = document.createElement('span');
                     d.style.color = 'var(--mut)'; document.body.appendChild(d);
                     const c = getComputedStyle(d).color; d.remove(); return c; })(),
    // A3 behavioural: does the loaded face actually cover the Pāḷi diacritics?
    // `document.fonts.check(font, text)` answers for THAT TEXT, so a font that
    // loaded but carries no ṁ ṅ ṭ ḍ ṇ ḷ still fails -- which is the failure
    // mode the self-hosting exists to prevent.
    faceAny:   document.fonts.check('400 15.5px "Gentium Plus"', 'a'),
    faceDiac:  document.fonts.check('400 15.5px "Gentium Plus"', 'āīūṁṃṅñṭḍṇḷ'),
    faceBold:  document.fonts.check('700 15.5px "Gentium Plus"', 'āīūṁṃṅñṭḍṇḷ'),
    faceInter: document.fonts.check('400 13.5px "Inter"', 'āīūṁṃṅñṭḍṇḷ'),
  };
}'''

TOKENS_READ = r'''() => {
  const r = getComputedStyle(document.documentElement);
  const out = {};
  for (const n of ['--panel','--app','--bg','--fg','--mut','--faint','--canon',
                   '--comm','--tika','--accent','--chipfg'])
    out[n] = (r.getPropertyValue(n) || '').trim();
  return out;
}'''


def _lin(c):
    c /= 255.0
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4


def _lum(h):
    h = h.strip().lstrip('#')
    if h.startswith('rgb'):
        h = re.findall(r'\d+', h)
        r, g, b = (int(x) for x in h[:3])
    else:
        if len(h) == 3:
            h = ''.join(c * 2 for c in h)
        r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return .2126 * _lin(r) + .7152 * _lin(g) + .0722 * _lin(b)


def contrast(a, b):
    la, lb = _lum(a), _lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + .05) / (lo + .05)


# which tokens are text, and therefore need 4.5:1 -- and which are not.
# !!! --canon IS NOT TEXT.  It is a 3px border on .para.canon and .wl-wordgrp,
# a legend dot, and the BACKGROUND of `.lbtn.on[data-k=canon]`, which sets
# `color:#fff`.  Asserting 4.5:1 for it as a foreground would be asserting the
# wrong thing; what actually has to hold is white-on-it.  Checked in the source
# before it was written down -- the paragraph numbers are --accent, not --canon.
TEXT_TOKENS  = ['--fg', '--mut', '--accent', '--comm', '--tika', '--chipfg']
THIRD_TIER   = ['--faint']                                   # 3:1, deliberately
# !!! AND THE CASE WHERE A TOKEN IS THE BACKGROUND, NOT THE FOREGROUND.  This
# is the one the earlier survey missed entirely: it measured every token as a
# foreground against --panel and stopped, so it reported the dark theme as
# "fine, leave it alone" while `.lchip.a` and `.lbtn.on` were putting white text
# on --comm at 2.25:1 and on --canon at 2.18:1.  Those three tokens are LIGHT in
# dark theme -- gold, mint, lilac -- so white on them is close to invisible.
# The label colour is --panel, which flips with the theme; assert it as the
# reader will actually see it rather than assuming #fff.
PANEL_ON     = ['--canon', '--comm', '--tika']               # .lchip / .lbtn.on


def run_design(pin=None):
    """A1-A5 and B, on the shipped reader, with the control pressed."""
    fails, seen_panel = [], False
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page(viewport={'width': 1400, 'height': 900})
        reqs, bad_status = [], []
        pg.on('request', lambda r: reqs.append(r.url))
        pg.on('response', lambda r: bad_status.append((r.url, r.status))
              if ('/fonts/' in r.url and r.status >= 400) else None)
        vol = (pin or VOLS)[0]
        # !!! THIS PASS OPENED THE READER WITH `wle=0`, AND A4 MEASURES A THING
        # THAT ONLY EXISTS WITH `wle=1`.  `.wl-my` is drawn by the Abhidhana and
        # the APD, both behind the evaluation flag, so with the flag off there
        # was no Burmese in the panel by construction -- and A4 then reported
        # "NOT EXERCISED" and attributed it to the store being absent, which
        # made the note itself misleading: the store's absence was never the
        # only reason, and on a machine that HAS the store the pass still could
        # not run.  Follow the store: exercise the evaluation surface where it
        # exists, and stay off it where it does not.
        _wle = 1 if EMAN is not None else 0
        pg.goto(BASE + f'/reader/reader2.html?wl=1&wle={_wle}#{vol}/0',
                wait_until='domcontentloaded')
        try:
            pg.wait_for_selector('.para.canon', timeout=20000)
        except Exception:
            return ['design: no canon paragraph rendered'], 1
        pg.wait_for_timeout(500)
        pg.evaluate('document.fonts.ready')

        # --- A3, before anything else: where did the type come from? --------
        if any('fonts.googleapis.com' in u or 'fonts.gstatic.com' in u for u in reqs):
            fails.append('A3: the reader still requests type from Google — the '
                         'whole point of self-hosting is that it does not')
        local = [u for u in reqs if u.endswith('.woff2')]
        if not local:
            fails.append('A3: no local .woff2 was fetched at all — the '
                         '@font-face block is not being used')
        for u, s in bad_status:
            fails.append(f'A3: {u.rsplit("/", 1)[-1]} returned {s}')

        # --- open the panel on a word that has a Burmese block --------------
        # `.wl-my` only exists on words the Abhidhāna covers, so a word picked
        # at random would make A4 vacuous -- the same shape as assertion 14
        # iterating an empty list.  Try words until one draws every element the
        # pass measures, and FAIL if none does.
        words = pg.evaluate('''() => {
          const out = [];
          document.querySelectorAll('.para.canon').forEach(p => {
            const t = p.textContent;
            (t.match(/[a-zāīūṁṅñṭḍṇḷ’]{5,}/gi) || []).slice(0, 40)
              .forEach(w => out.push([w, p.id]));
          });
          return out; }''')
        need = ('#wl .wl-g:not(.wl-lem)', '#wl .wl-lem', '#wl .wl-sub',
                '#wl .wl-why')
        base = None
        for word, pid in words[:60]:
            hit = pg.evaluate(TAB_MEASURE, [word, pid])
            if not hit:
                continue
            pg.evaluate('''() => { const x = document.getElementById('wlx');
                                   if (x) x.click();
                                   const w = document.getElementById('wl');
                                   if (w) w.dataset.state = 'stale'; }''')
            pg.wait_for_timeout(60)
            hit = pg.evaluate(TAB_MEASURE, [word, pid])
            if not hit:
                continue
            pg.mouse.click(hit['x'], hit['y'])
            try:
                pg.wait_for_selector('#wl[data-state="ready"]', timeout=8000)
            except Exception:
                continue
            pg.evaluate('''() => { const b =
              document.querySelector('#wlt button[data-tab="ed"]');
              if (b && !b.classList.contains('dis')) b.click(); }''')
            pg.wait_for_timeout(150)
            if pg.evaluate('(s) => s.every(x => !!document.querySelector(x))',
                           list(need)):
                base = pg.evaluate(TYPE_READ)
                # !!! `.wl-my` IS NOT ON THE EDITION TAB, AND THIS PASS IS
                # STANDING ON IT.  A4 read base['my'] out of a measurement
                # taken three lines after clicking `data-tab="ed"`, so the
                # Burmese it exists to measure was NEVER IN THE DOM and
                # base['my'] was structurally always None.  That never
                # showed, because with the evaluation store absent A4
                # printed NOT EXERCISED and stopped there -- so the first
                # run that could exercise it was also the first run that
                # could see the assertion was broken.  Measured: the
                # Burmese lives on the `abhi` and `dict` tabs, at 16.5px.
                #
                # The comment above the word loop already said the right
                # thing -- a word picked at random would make A4 vacuous,
                # try words until one draws every element the pass measures
                # -- but `need` never contained `.wl-my`, so the intent was
                # written down and not implemented.  Both halves are fixed:
                # find the tab the Burmese is on and measure it there, and,
                # when the store is present, REQUIRE it, so a word no source
                # glosses in Burmese moves the probe on instead of quietly
                # emptying the assertion.
                #
                # POLL, DO NOT GUESS A DELAY: a tab renders asynchronously,
                # so clicking and reading in the same turn finds nothing --
                # which is how the first attempt at this fix concluded,
                # wrongly, that no word in the Majjhima had any Burmese.
                myv = None
                for _t in pg.evaluate(
                        "() => [...document.querySelectorAll('#wlt button')]"
                        ".filter(b => !b.classList.contains('dis'))"
                        ".map(b => b.dataset.tab)"):
                    pg.evaluate(
                        "t => { const b = document.querySelector("
                        "  '#wlt button[data-tab=\"' + t + '\"]');"
                        " if (b) b.click(); }", _t)
                    for _ in range(8):
                        myv = pg.evaluate(
                        "() => { const e = document.querySelector('#wl .wl-my');"
                        " if (!e) return null; const c = getComputedStyle(e);"
                        " return {my: parseFloat(c.fontSize), fam: c.fontFamily,"
                        "         n: document.querySelectorAll('#wl .wl-my').length}; }")
                        if myv:
                            break
                        pg.wait_for_timeout(150)
                    if myv:
                        myv['tab'] = _t
                        break
                pg.evaluate(
                    "() => { const b = document.querySelector("
                    "  '#wlt button[data-tab=\"ed\"]');"
                    " if (b && !b.classList.contains('dis')) b.click(); }")
                pg.wait_for_timeout(250)
                if EMAN is not None and not myv:
                    continue        # no Burmese anywhere for this word
                if myv:
                    base['my'] = myv['my']
                    base['myFam'] = myv['fam']
                    base['myN'] = myv['n']
                    base['myTab'] = myv['tab']
                seen_panel = True
                break
        if not seen_panel:
            # the non-vacuity guard: this pass may not report success by never
            # having had a panel to measure.  !!! PRINT, DO NOT JUST RETURN —
            # the first version returned silently and produced a bare exit code
            # 1 with no output, which is only marginally better than the vacuous
            # pass it exists to prevent.
            fails.append('design: no clicked word produced a panel carrying all '
                         'of ' + ', '.join(need) + ' — the pass measured '
                         'nothing and must not report success')
            b.close()
            for f in fails:
                print(f'  FAIL design: {f}')
            print(f'gate_reader [design]: {len(fails)} failures')
            return fails, 1

        if not base['faceAny']:
            fails.append('A3: "Gentium Plus" did not load at all')
        elif not base['faceDiac']:
            fails.append('A3: "Gentium Plus" loaded but does not cover '
                         'ā ī ū ṁ ṃ ṅ ñ ṭ ḍ ṇ ḷ — the latin-ext subset is '
                         'missing and every diacritic will render as tofu')
        if base['faceAny'] and not base['faceBold']:
            fails.append('A3: Gentium Plus 700 does not cover the diacritics')
        if not base['faceInter']:
            fails.append('A3: "Inter" does not cover the diacritics — the Pāḷi '
                         'book names in the left pane are set in it')

        # --- A2: the Pāḷi in the panel is not smaller than the Pāḷi clicked --
        if base['g'] is None or base['body'] is None:
            fails.append('A2: could not measure .wl-g against .wl-b')
        else:
            if base['g'] < base['body'] - 0.01:
                fails.append(f'A2: panel Pāḷi is {base["g"]}px but the English '
                             f'body is {base["body"]}px — the script the reader '
                             f'clicked to see better is the smaller of the two')
            if base['para'] and abs(base['g'] - base['para']) > 0.51:
                fails.append(f'A2: panel Pāḷi is {base["g"]}px and the clicked '
                             f'Pāḷi is {base["para"]}px')
            if base['lem'] and base['lem'] < base['body'] - 0.01:
                fails.append(f'A2: .wl-lem is {base["lem"]}px, under the '
                             f'{base["body"]}px body')

        # --- A4 / A5 -------------------------------------------------------
        # !!! A4 IS ONLY EXERCISED WHEN THE ABHIDHĀNA IS PRESENT.  `.wl-my` is
        # drawn by the Abhidhāna renderer, which lives behind ?wle=1 and reads
        # site/lookup_eval/ -- gitignored, so absent on any clean checkout.
        # With the flag off there is no Burmese in the panel at all, and a
        # silent skip here would be assertion 14's empty list over again: a pass
        # reporting success for a check it never ran.  So SAY SO, and make it a
        # failure only where the data to run it exists.
        if base['my'] is None:
            msg = ('A4 NOT EXERCISED: no .wl-my in the panel — Burmese is drawn '
                   'only under ?wle=1 with site/lookup_eval/ present')
            if EMAN is not None:
                fails.append(msg + ', and the evaluation store IS present here')
            else:
                print(f'  note: {msg}; run with the evaluation store to cover it')
        if base['my'] is not None:
            print('  A4 measured: %s Burmese block(s) on the %r tab at '
                  '%.1fpx in %s'
                  % (base.get('myN'), base.get('myTab'), base['my'],
                     (base.get('myFam') or '?').split(',')[0].strip('\"')))
        if base['my'] is not None and base['my'] < 16:
            fails.append(f'A4: Burmese is {base["my"]}px; stacked consonants, '
                         f'asat and kinzi are not separable below 16px')
        if base['my'] is not None and base['g'] and base['my'] <= base['g']:
            fails.append(f'A4: Burmese ({base["my"]}px) is not larger than the '
                         f'Latin-script Pāḷi ({base["g"]}px)')
        for k, label in (('sub', '.wl-sub'), ('whyPx', '.wl-why')):
            if base[k] is not None and base[k] < 11:
                fails.append(f'A5: {label} is {base[k]}px, under the 11px floor')
        if base['whyCol'] and base['mutCol'] and base['whyCol'] == base['mutCol']:
            fails.append('A5: .wl-why is still --mut — it is the design claim '
                         'of the Gloss tab, not a footnote, and must be --fg')

        # --- A6: THE HOVER AFFORDANCE.  Move the mouse, do not read the CSS. --
        # Defaulting the panel on made it reachable; it did not make it visible.
        # The underline under the word beneath the pointer is the only thing
        # telling a reader that the text is clickable at all, so it is now load
        # bearing for the whole feature and gets an assertion that MOVES A MOUSE
        # — presence of the CSS rule proves nothing, which is §0's entire point.
        hov = pg.evaluate('''() => {
          // find a word rect in the rendered canon, on screen
          const p = document.querySelector('.para.canon');
          const w = document.createTreeWalker(p, NodeFilter.SHOW_TEXT);
          let n;
          while ((n = w.nextNode())) {
            const i = n.textContent.search(/[a-zāīūṁṅñṭḍṇḷ]{6,}/i);
            if (i >= 0) {
              const r = document.createRange();
              r.setStart(n, i + 1); r.setEnd(n, i + 4);
              const b = r.getBoundingClientRect();
              if (b.width > 0 && b.top > 80 && b.bottom < innerHeight - 20)
                return {x: b.x + 2, y: b.y + b.height / 2};
            }
          }
          return null;}''')
        if not hov:
            fails.append('A6: no on-screen word to hover — assertion not run')
        else:
            pg.mouse.move(hov['x'] - 200, hov['y'])   # start off the word
            pg.wait_for_timeout(120)
            before_h = pg.evaluate(
                "() => [document.querySelectorAll('.wl-hov').length,"
                " document.querySelectorAll('.para.wl-hot').length]")
            pg.mouse.move(hov['x'], hov['y'])
            pg.wait_for_timeout(200)
            on_h = pg.evaluate('''() => {
              const e = [...document.querySelectorAll('.wl-hov')];
              const p = document.querySelector('.para.wl-hot');
              return {n: e.length,
                      w: e.length ? Math.round(e[0].getBoundingClientRect().width) : 0,
                      pe: e.length ? getComputedStyle(e[0]).pointerEvents : null,
                      cursor: p ? getComputedStyle(p).cursor : null};}''')
            if on_h['n'] == 0:
                fails.append('A6: hovering a word draws no underline — the '
                             'panel is on but nothing tells a reader so')
            if on_h['n'] and on_h['w'] < 4:
                fails.append(f'A6: the hover underline is {on_h["w"]}px wide')
            # !!! IF THIS IS NOT `none` EVERY CLICK LANDS ON THE OVERLAY AND THE
            # PANEL NEVER OPENS.  The affordance would break the thing it
            # advertises, and the geometry assertions would not notice.
            if on_h['n'] and on_h['pe'] != 'none':
                fails.append(f'A6: the hover overlay has pointer-events '
                             f'{on_h["pe"]!r} — it will swallow the click')
            if on_h['cursor'] != 'pointer':
                fails.append(f'A6: the hovered paragraph\'s cursor is '
                             f'{on_h["cursor"]!r}, not pointer')
            # and it must come back off, or the underline is just decoration
            pg.mouse.move(hov['x'] - 200, hov['y'])
            pg.wait_for_timeout(200)
            off_h = pg.evaluate(
                "() => [document.querySelectorAll('.wl-hov').length,"
                " document.querySelectorAll('.para.wl-hot').length]")
            if off_h[0] or off_h[1]:
                fails.append(f'A6: moving off the word left {off_h[0]} '
                             f'underline(s) and {off_h[1]} hot paragraph(s)')
            if before_h[0] or before_h[1]:
                fails.append('A6: an underline existed before the pointer was '
                             'ever over a word')
            # the click must still work with the affordance in play
            pg.mouse.move(hov['x'], hov['y'])
            pg.wait_for_timeout(150)
            pg.evaluate('''() => { const x = document.getElementById('wlx');
                                   if (x) x.click();
                                   const w = document.getElementById('wl');
                                   if (w) w.dataset.state = 'stale'; }''')
            pg.mouse.click(hov['x'], hov['y'])
            try:
                pg.wait_for_selector('#wl[data-state="ready"]', timeout=10000)
            except Exception:
                fails.append('A6: with the hover underline drawn, clicking the '
                             'word no longer opens the panel')

        # --- A1: PRESS THE CONTROL.  This is the assertion that matters. ----
        before = dict(base)
        pg.evaluate('''() => { for (let i = 0; i < 3; i++)
                                 document.getElementById('finc').click(); }''')
        pg.wait_for_timeout(300)
        after = pg.evaluate(TYPE_READ)
        moved = []
        for k, label in (('body', 'the English body'), ('g', 'the Pāḷi gloss'),
                         ('lem', 'the lemma'), ('my', 'the Burmese')):
            if before[k] is None or after[k] is None:
                continue
            if after[k] <= before[k] + 0.01:
                fails.append(f'A1: A+ pressed three times and {label} stayed at '
                             f'{before[k]}px — the panel does not follow the '
                             f'reader\'s own text-size control')
            else:
                moved.append(f'{label} {before[k]}->{after[k]}px')
        if after['para'] and before['para'] and after['para'] <= before['para']:
            fails.append('A1: A+ did not even move the canon text — the control '
                         'itself is broken and this pass proves nothing')
        pg.evaluate('''() => { for (let i = 0; i < 3; i++)
                                 document.getElementById('fdec').click(); }''')

        # --- B: contrast, in both themes, against both backgrounds ----------
        for theme in ('light', 'dark'):
            pg.evaluate('(t) => document.documentElement.setAttribute('
                        '"data-theme", t)', theme)
            pg.wait_for_timeout(80)
            T = pg.evaluate(TOKENS_READ)
            for bgname in ('--panel', '--app'):
                bg = T[bgname]
                for t in TEXT_TOKENS:
                    r = contrast(T[t], bg)
                    if r < 4.5:
                        fails.append(f'B[{theme}]: {t} {T[t]} on {bgname} '
                                     f'{bg} is {r:.2f}:1, under AA 4.5')
                for t in THIRD_TIER:
                    r = contrast(T[t], bg)
                    if r < 3.0:
                        fails.append(f'B[{theme}]: {t} {T[t]} on {bgname} '
                                     f'{bg} is {r:.2f}:1, under 3:1')
            for t in PANEL_ON:
                r = contrast(T['--panel'], T[t])
                if r < 4.5:
                    fails.append(f'B[{theme}]: the layer label on {t} {T[t]} is '
                                 f'{r:.2f}:1 — .lchip and .lbtn.on set the text '
                                 f'to --panel and put it directly on this token')
        pg.evaluate('() => document.documentElement.setAttribute('
                    '"data-theme", "light")')
        b.close()
    for f in fails:
        print(f'  FAIL design: {f}')
    if moved:
        print(f'  A+ moved: {"; ".join(moved)}')
    print(f'gate_reader [design]: {len(fails)} failures')
    return fails, (1 if fails else 0)


def run_design_negative_controls():
    """Every assertion above, broken on purpose.  An assertion that cannot be
    made to fail is not an assertion.  These patch the SHIPPED files on disk and
    restore them, so what is broken is what runs -- not a copy."""
    print('\n--- negative controls: the design pass must FAIL when broken ---')
    js = os.path.join(REPO, 'site', 'reader', 'panel.js')
    html = os.path.join(REPO, 'site', 'reader', 'reader2.html')
    cases = [
        ('A1 panel body hardcoded again', js,
         'font-size:calc(var(--rsize, 15.5px) - 2px);line-height:1.55',
         'font-size:13.5px;line-height:1.55'),
        ('A2 Pāḷi left to inherit', js,
         '#wl .wl-g{font-family:"Gentium Plus",Georgia,serif;'
         'font-size:var(--rsize, 15.5px)}',
         '#wl .wl-g{font-family:"Gentium Plus",Georgia,serif}'),
        ('A4 Burmese back to 15px', js,
         'font-size:calc(var(--rsize, 15.5px) + 1px);line-height:1.9;margin:.25em 0',
         'font-size:15px;line-height:1.9;margin:.25em 0'),
        ('A5 why-line back to 10.5px --mut', js,
         "#wl .wl-why{font-size:11px;color:var(--fg);",
         "#wl .wl-why{font-size:10.5px;color:var(--mut);"),
        ('B --mut back to its sub-AA value', html, '--mut:#756d63', '--mut:#8a8175'),
        ('B --canon back, layer label 3.24:1', html,
         '--canon:#976e27', '--canon:#b8862f'),
        ('A6 hover affordance never bound', js,
         '  hoverBind();\n', '\n'),
        ('A6 overlay swallows the click', js,
         "'.wl-hov{position:fixed;pointer-events:none;z-index:40;'",
         "'.wl-hov{position:fixed;z-index:40;'"),
        ('A3 type back on Google Fonts', html,
         '<link href="../fonts/fonts.css" rel="stylesheet">',
         '<link href="https://fonts.googleapis.com/css2?family=Gentium+Plus:'
         'ital,wght@0,400;0,700;1,400&family=Inter:wght@400;500;600&display=swap"'
         ' rel="stylesheet">'),
    ]
    # !!! A CONTROL FOR AN ASSERTION THAT CANNOT RUN IS NOT A CONTROL.  A4 is
    # only exercised when the Abhidhāna is present (site/lookup_eval/, behind
    # ?wle=1), so on a clean checkout breaking `.wl-my` cannot make the design
    # pass fail — and counting that as "did not fire" would be reporting a
    # tooling gap as a defect, while counting it as "fired" would be worse.
    # Say plainly that it was not run, and where to run it.
    if EMAN is None:
        skipped = [c for c in cases if c[0].startswith('A4')]
        cases = [c for c in cases if not c[0].startswith('A4')]
        for c in skipped:
            print(f'  NOT EXERCISABLE HERE: {c[0]} — A4 needs the evaluation '
                  f'store; run this with site/lookup_eval/ present')

    bad = 0
    for name, path, find, repl in cases:
        src = io.open(path, encoding='utf-8').read()
        # !!! ASSERT THE PATCH MATCHED.  Six faults in one earlier session came
        # from String.replace calls that matched nothing and said nothing; a
        # control that silently patched nothing would "fire" by not firing.
        if src.count(find) != 1:
            print(f'  CONTROL IS BROKEN: {name} — its anchor matches '
                  f'{src.count(find)} times, not 1')
            bad += 1
            continue
        try:
            io.open(path, 'w', encoding='utf-8').write(src.replace(find, repl))
            f, rc = run_design()
            if rc == 0:
                print(f'  NEGATIVE CONTROL DID NOT FIRE: {name}')
                bad += 1
            else:
                print(f'  negative control fired: {name} '
                      f'({len(f)} failure(s), first: {f[0][:78]}…)')
        finally:
            io.open(path, 'w', encoding='utf-8').write(src)
    print(f'--- design negative controls: {bad} did not fire ---')
    return 1 if bad else 0


def run_flag_negative_controls():
    """Assertion 1, both directions, broken on purpose.

    The default flipped from off to on, and the assertion that guarded it was
    INVERTED rather than deleted.  An inverted assertion is worth exactly as
    much as its ability to fail, and there are two distinct ways this can now
    go wrong -- the off switch stops working, or the default quietly goes back
    to off and the panel is unreachable again without anything saying so.  One
    control each.
    """
    print('\n--- negative controls: the flag assertions must FAIL when broken ---')
    js = os.path.join(REPO, 'site', 'reader', 'panel.js')
    ON_BLOCK = ("var ON = true;\n"
                "try { if (localStorage.getItem('osbct-wl') === '0') ON = false; } catch (e) {}\n"
                "if (q.get('wl') === '1') ON = true;\n"
                "if (q.get('wl') === '0') ON = false;")
    cases = [
        # the change itself, reverted: does anything notice the panel is
        # unreachable again?  Before this control existed, nothing did -- four
        # gate passes ran clean on a build no reader could reach.
        ('the default silently goes back to OFF', ON_BLOCK,
         ON_BLOCK.replace('var ON = true;', 'var ON = false;')
                 .replace("if (localStorage.getItem('osbct-wl') === '0') ON = false;",
                          "ON = localStorage.getItem('osbct-wl') === '1';")),
        # and the §9 guarantee: ?wl=0 must be total, not cosmetic.
        # !!! THE FIRST VERSION OF THIS CONTROL DID NOT FIRE, AND THE ASSERTION
        # WAS RIGHT.  It deleted only `if (q.get('wl') === '0') ON = false;` --
        # but the block above it writes `?wl=0` into localStorage BEFORE the
        # read, so the off switch still worked through the stored value and the
        # gate correctly saw nothing wrong.  A control that breaks one of two
        # redundant paths tests nothing.  Remove both: ON, with no way out.
        ('?wl=0 stops turning the panel off', ON_BLOCK, 'var ON = true;'),
    ]
    bad = 0
    for name, find, repl in cases:
        src = io.open(js, encoding='utf-8').read()
        if src.count(find) != 1:
            print(f'  CONTROL IS BROKEN: {name} — its anchor matches '
                  f'{src.count(find)} times, not 1')
            bad += 1
            continue
        try:
            io.open(js, 'w', encoding='utf-8').write(src.replace(find, repl))
            rc = run_gate(EVAL_ON=False)
            if rc == 0:
                print(f'  NEGATIVE CONTROL DID NOT FIRE: {name}')
                bad += 1
            else:
                print(f'  negative control fired: {name}')
        finally:
            io.open(js, 'w', encoding='utf-8').write(src)
    print(f'--- flag negative controls: {bad} did not fire ---')
    return 1 if bad else 0


def _search_probe():
    """A query the shipped index really answers, chosen deterministically.

    Picked from `site/index/terms.compact.json` rather than hard-coded, so the
    gate keeps working when the corpus is rebuilt, and returns the volume and
    ordinals the INDEX says the term is at -- computed here, from the files,
    independently of anything the page does.  That independence is the point:
    an assertion that reads the answer off the same DOM it is judging can
    only tell you the DOM is self-consistent.
    """
    tp = os.path.join(REPO, 'site', 'index', 'terms.compact.json')
    if not os.path.exists(tp):
        return None
    T = json.load(open(tp))
    rng = random.Random(SEED)
    # only volumes whose shard is actually on disk, so a partial checkout
    # narrows the probe instead of failing it
    have = {i for i, v in enumerate(T['vols'])
            if os.path.exists(os.path.join(REPO, 'site', 'index',
                                           v + '.idx.json'))}
    keys = [k for k in T['terms']
            if len(k) >= 6 and k.isalpha()
            and len(T['terms'][k]) == 1 and T['terms'][k][0] in have]
    keys.sort()
    rng.shuffle(keys)
    for term in keys[:60]:
        vi = T['terms'][term][0]
        vol = T['vols'][vi]
        sp = os.path.join(REPO, 'site', 'index', vol + '.idx.json')
        sh = json.load(open(sp))
        post = sh['inv'].get(term) or []
        ords = [sh['paras'][pi].get('ord') for pi, _ in post]
        if post and all(o is not None for o in ords):
            return {'term': term, 'vol': vol, 'ords': ords,
                    'layer': T['layers'][vi], 'npara': len(sh['paras'])}
    return None


# `pali-unicode` etc. -> the layer letter the result row must pass to openHit
_SLAYER = {'pali-unicode': 'canon', 'atthakatha-unicode': 'A',
           'tika-unicode': 'T'}


def run_search():
    """DOES CLICKING A SEARCH HIT OPEN THE PASSAGE IT POINTS AT?

    User-reported 2026-08-02, and dead since 8d5bebed: the top-bar box built
    every occurrence row as `openKey(p.key, ...)`, and `key` IS NOT A FIELD
    THE INDEX EMITS.  Measured over all 118 shards: present on 0 of 86,365
    paragraphs; `ord` present on all of them, and `build_search_index.py`
    says so in its own docstring.  So every hit called `openKey('undefined')`,
    `parseKey` split it into the volume `'undefine'` and the ordinal `NaN`,
    the reader drew nothing, and the layer band said "No Aṭṭhakathā is linked
    to the passages on screen."  A wrong answer wearing an honest one's face.

    Nothing in this repository could see it.  `search.html` was correct, so
    every check of the search DATA passed; the reader's own gate never typed
    anything into the box.  So this asserts the whole path a reader walks --
    type, look, click, arrive -- and it asserts ARRIVAL against the index
    files rather than against the page.

    Three things, and the third is the one that matters:
      a. the box returns rows for a term the index really carries (non-vacuity
         -- an empty dropdown must not read as a pass);
      b. every row carries a key of the form VOL#ORD, with VOL a volume that
         exists and ORD inside that volume's paragraph count;
      c. clicking the first row draws paragraphs, leaves no empty-band note,
         and highlights the term INSIDE the paragraph the row pointed at.
    """
    probe = _search_probe()
    fails = []
    if not probe:
        print('  note: SEARCH NOT EXERCISED — site/index/ absent, so the '
              'result rows cannot be checked here')
        print('gate_reader [search]: 0 failures (NOT EXERCISED)')
        return 0
    term, vol, ords = probe['term'], probe['vol'], probe['ords']
    want_key = '%s#%d' % (vol, ords[0])
    want_kind = _SLAYER.get(probe['layer'], 'canon')

    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page(viewport={'width': 1400, 'height': 900})
        errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto(BASE + '/reader/reader2.html?wl=0#%s#0' % vol,
                wait_until='domcontentloaded')
        try:
            pg.wait_for_selector('.para', timeout=30000)
            pg.fill('#sq', term)
            pg.wait_for_selector('#sdrop .sresult', timeout=30000)
            rows = pg.evaluate(
                "() => [...document.querySelectorAll('#sdrop .sresult')]"
                ".map(d => d.getAttribute('onclick') || '')")
        except Exception as e:
            rows = []
            fails.append('search for %r never produced a result row: %s'
                         % (term, e))

        # (a) non-vacuity, phrased against the FILES: the index says this term
        # is there, so an empty dropdown is a failure and not an empty loop.
        if not rows:
            fails.append('the index carries %r in %s at ords %s, and the box '
                         'showed no occurrence row at all' % (term, vol, ords))

        # (b) every key must be one the reader can actually parse
        vol_paras = {vol: probe['npara']}
        bad = _bad_keys(rows, vol_paras)
        fails.extend(bad)

        # THE CONTROL, run in the same breath as the assertion it guards.  If
        # `_bad_keys` cannot catch the exact string that shipped for two days,
        # then (b) above is a comment, not a check.
        if not _bad_keys(["openHit('undefined','A')"], vol_paras):
            fails.append('CONTROL IS BROKEN: the row-key check accepts '
                         "openHit('undefined', ...), which is the defect it "
                         'exists to catch')

        # (c) arrival
        if rows:
            try:
                pg.click('#sdrop .sresult')
                pg.wait_for_timeout(1500)
                got = pg.evaluate("""() => ({
                    small: (document.querySelector('#doctitle small')||{}).textContent||'',
                    paras: document.querySelectorAll('.para').length,
                    band: (document.querySelector('.bandnote')||{}).textContent||'',
                    markIn: [...document.querySelectorAll('mark.shl')]
                              .map(m => (m.closest('.para')||{}).id),
                })""")
                if 'undefine' in got['small']:
                    fails.append('clicking a hit left the title bar reading %r'
                                 % got['small'])
                if got['paras'] == 0:
                    fails.append('clicking a hit for %r drew 0 paragraphs '
                                 '(the volume has %d)' % (term, probe['npara']))
                if got['band']:
                    fails.append('clicking a hit left an empty-layer note on '
                                 'screen: %r' % got['band'])
                want_el = 'p-' + want_key.replace('#', '-')
                if want_el not in (got['markIn'] or []):
                    fails.append('the term is not highlighted in the paragraph '
                                 'the row points at (%s); marks landed in %r'
                                 % (want_el, got['markIn']))
            except Exception as e:
                fails.append('clicking the first hit for %r raised: %s'
                             % (term, e))
        # (c2) AND IT MUST LAND ON THE WORD, AT A PHONE SIZE TOO.  Centring
        # the PARAGRAPH is not arriving: measured on 51Vism01 §180 at 390x844
        # the paragraph is 2841px in a 657px viewport and the highlighted word
        # came to rest 571px BELOW THE FOLD -- on screen by no measure a reader
        # would accept, and reported as "one has to look around to find it".
        # Asserted at both sizes because the desktop case merely looked poor
        # while the phone case was actually broken.
        try:
            for vw, vh in ((1400, 900), (390, 844)):
                c4 = b.new_context(viewport={'width': vw, 'height': vh})
                p4 = c4.new_page()
                p4.goto(BASE + '/reader/reader2.html?wl=0', wait_until='domcontentloaded')
                p4.wait_for_timeout(1000)
                p4.fill('#sq', term)
                p4.wait_for_selector('#sdrop .sresult', timeout=30000)
                p4.click('#sdrop .sresult')
                p4.wait_for_timeout(3000)
                land = p4.evaluate("""() => {
                    const sc = document.getElementById('scroll');
                    const m = document.querySelector('mark.shl');
                    if (!m) return null;
                    const vb = sc.getBoundingClientRect(), mb = m.getBoundingClientRect();
                    return {top: Math.round(mb.top - vb.top),
                            h: Math.round(vb.height),
                            on: mb.top >= vb.top && mb.bottom <= vb.bottom,
                            ph: Math.round(m.closest('.para').getBoundingClientRect().height)};
                }""")
                if not land:
                    fails.append('%dx%d: nothing was highlighted after the click'
                                 % (vw, vh))
                elif not land['on']:
                    fails.append('%dx%d: the hit is OFF SCREEN — the word sits at '
                                 'y=%d in a %dpx viewport (its paragraph is %dpx '
                                 'tall)' % (vw, vh, land['top'], land['h'], land['ph']))
                c4.close()
        except Exception as e:
            fails.append('landing check raised: %s' % e)

        # (d) ONE FAILED FETCH OF THE TERM MAP MUST NOT KILL THE BOX.
        # `ensureTerms` used to cache `jget`'s fallback -- an EMPTY term map --
        # as though it were the answer, and its own `if (TERMS) return` then
        # guaranteed it was never fetched again.  Every later keystroke
        # answered "No matches", confidently and wrongly, for the rest of the
        # page load.  Reported 2026-08-02 as "the search box only works when
        # there is text in the reader pane": the 22 MB request loses exactly
        # where it contends with nav.json, pageindex, pagespan, concordance
        # and the fonts, which is a cold load.
        # The recovery half of this is the assertion that cannot be satisfied
        # by absence -- it demands ROWS, from a page that has already failed
        # once.
        try:
            c3 = b.new_context(viewport={'width': 1400, 'height': 900})
            p3 = c3.new_page()
            seen = {'n': 0}

            def _route(r):
                seen['n'] += 1
                r.abort('failed') if seen['n'] == 1 else r.continue_()

            p3.route('**/terms.compact.json*', _route)
            p3.goto(BASE + '/reader/reader2.html?wl=0', wait_until='domcontentloaded')
            p3.wait_for_timeout(1200)
            p3.fill('#sq', term)
            p3.wait_for_timeout(2500)
            said = p3.evaluate(
                "() => (document.getElementById('sdrop').textContent||'').trim()")
            if not said:
                fails.append('with the term map failing, the box showed nothing '
                             'at all — indistinguishable from a dead search box')
            elif 'occurrence' not in said and 'could not be loaded' not in said \
                    and 'no se pudo' not in said.lower():
                fails.append('with the term map failing, the box said %r rather '
                             'than saying the index failed' % said[:70])
            p3.fill('#sq', term[:-1])
            p3.wait_for_timeout(400)
            p3.fill('#sq', term)
            p3.wait_for_timeout(4000)
            back = p3.evaluate(
                "() => document.querySelectorAll('#sdrop .sresult').length")
            if back == 0:
                fails.append('after the term map failed once, a later keystroke '
                             'still returned nothing (%d request(s) made) — the '
                             'failed fetch is cached as the answer'
                             % seen['n'])
            c3.close()
        except Exception as e:
            fails.append('failed-index-fetch check raised: %s' % e)

        if errs:
            fails.append('page errors during search: %s' % errs[:3])
        b.close()

    for f in fails:
        print('  FAIL search: %s' % f)
    print('gate_reader [search]: %d failures  (probe %r -> %s, expected %s, '
          'kind %s)' % (len(fails), term, ords, want_key, want_kind))
    return 1 if fails else 0


def _bad_keys(onclicks, vol_paras):
    """The row-key assertion, factored out so its own control can call it."""
    out = []
    for i, oc in enumerate(onclicks):
        m = re.search(r"open(?:Hit|Key)\('([^']*)'", oc or '')
        if not m:
            # a row with no handler at all is only acceptable if it says so
            out.append('row %d has no openHit(...) handler: %r' % (i, oc[:80]))
            continue
        k = m.group(1)
        km = re.match(r'^([0-9A-Za-z]+)#(\d+)$', k)
        if not km:
            out.append('row %d carries the unusable key %r — this is the '
                       '2026-08-02 defect' % (i, k))
            continue
        v, o = km.group(1), int(km.group(2))
        if v in vol_paras and not (0 <= o < vol_paras[v]):
            out.append('row %d points at %s ordinal %d, outside that volume '
                       '(%d paragraphs)' % (i, v, o, vol_paras[v]))
    return out


def _layer_probe():
    """A canon paragraph deep in a volume, inside a NAMED section, that has a
    commentary link.  Chosen from the files, not from the page."""
    for vol in VOLS:
        vp = os.path.join(REPO, 'site', vol + '.json')
        lp = os.path.join(REPO, 'site', 'reader', 'linksk', vol + '.links.json')
        if not (os.path.exists(vp) and os.path.exists(lp)):
            continue
        d = json.load(open(vp, encoding='utf-8'))
        ps = d.get('paragraphs') or d.get('paras') or []
        L = json.load(open(lp, encoding='utf-8'))
        name, best = None, None
        for i, q in enumerate(ps):
            if q.get('sutta') and q['sutta'] != 'X':
                name = q['sutta']
            if i < len(ps) // 2 or not name:
                continue          # deep enough that a scroll jump is visible
            e = L.get(str(i)) or {}
            if e.get('commentary'):
                best = (vol, i, name, e['commentary'][0]['key'])
                break
        if best:
            return best
    return None


def run_layers():
    """PRESSING A LAYER BUTTON MUST NOT MOVE THE READER, AND THE SUTTA MUST
    KEEP ITS NAME.

    User-reported twice on 2026-08-02 -- "click in A it takes the user to a
    place that it is not the Commentary and the Sutta looses its name".  The
    first diagnosis found the link data wrong, which it was, fixed it, and
    reported the fault closed.  It was not: the reported behaviour has TWO
    causes and only one was in the data.

      * `render()` rebuilds `#scroll` wholesale, and pressing A roughly DOUBLES
        the blocks in the stream, so the browser's preserved `scrollTop` -- a
        PIXEL offset into a document that just changed height -- lands
        somewhere else.  Measured: top of view `p-16An02-383` before,
        `p-16An02-216` after, twenty-two printed pages earlier.
      * the title takes its sutta name from `state.cursutta`, which ONLY the
        sidebar tree sets, so arriving by search or by hash titled the pane
        with the nipata and the sutta had no name on screen at all.

    Both were visible in the first session's own test output and read past.
    This asserts the reader's experience instead of the data underneath it: go
    to a named sutta deep in a volume, press A, press T, and require that the
    paragraph at the top of the view is THE SAME ONE each time and that the
    title still names the sutta.  At a phone width as well, because the jump
    scales with document height and is worse there.
    """
    probe = _layer_probe()
    if not probe:
        print('  note: LAYERS NOT EXERCISED -- no volume with a named deep '
              'paragraph carrying a commentary link')
        print('gate_reader [layers]: 0 failures (NOT EXERCISED)')
        return 0
    vol, ord_, name, ckey = probe
    pid = 'p-%s-%d' % (vol, ord_)
    fails = []
    READ = ("() => { const sc = document.getElementById('scroll');"
            " const vt = sc.getBoundingClientRect().top;"
            " for (const p of sc.querySelectorAll('.para')) {"
            "   const r = p.getBoundingClientRect();"
            "   if (r.bottom > vt + 4) return {top: p.id,"
            "     title: document.querySelector('#doctitle').firstChild"
            "            ? document.querySelector('#doctitle').firstChild.textContent : ''}; }"
            " return {top: null, title: ''}; }")
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        for vw, vh in ((1400, 900), (390, 844)):
            ctx = b.new_context(viewport={'width': vw, 'height': vh})
            pg = ctx.new_page()
            try:
                pg.goto(BASE + '/reader/reader2.html?wl=0#%s#%d' % (vol, ord_),
                        wait_until='domcontentloaded')
                pg.wait_for_selector('.para', timeout=30000)
                pg.wait_for_timeout(1500)
                a = pg.evaluate(READ)
                if a['top'] != pid:
                    fails.append('%dx%d: opening %s#%d did not put %s at the top '
                                 'of the view (got %s)'
                                 % (vw, vh, vol, ord_, pid, a['top']))
                if name.split()[-1][:6].lower() not in (a['title'] or '').lower():
                    fails.append('%dx%d: arriving at %r the pane is titled %r -- '
                                 'the sutta has no name on screen'
                                 % (vw, vh, name, a['title']))
                for k in ('A', 'T'):
                    pg.click('#layerbar button[data-k="%s"]' % k)
                    pg.wait_for_timeout(2500)
                    g = pg.evaluate(READ)
                    if g['top'] != a['top']:
                        fails.append('%dx%d: pressing %s moved the reader from '
                                     '%s to %s -- the re-render kept the pixel '
                                     'offset, not the paragraph'
                                     % (vw, vh, k, a['top'], g['top']))
                # and the commentary drawn under the canon paragraph must be the
                # one the map names -- the data half of the same complaint
                nxt = pg.evaluate(
                    "(id) => { const all = [...document.querySelectorAll('#scroll .para')];"
                    " const i = all.findIndex(p => p.id === id);"
                    " return i >= 0 && all[i + 1] ? all[i + 1].id : null; }", pid)
                want = 'p-' + ckey.replace('#', '-')
                if nxt != want:
                    fails.append('%dx%d: the block under %s is %r, but the map '
                                 'says %s' % (vw, vh, pid, nxt, ckey))
            except Exception as e:
                fails.append('%dx%d: layer check raised: %s' % (vw, vh, e))
            ctx.close()
        b.close()
    for f in fails:
        print('  FAIL layers: %s' % f)
    print('gate_reader [layers]: %d failures  (probe %s#%d %r -> %s)'
          % (len(fails), vol, ord_, name, ckey))
    return 1 if fails else 0


if __name__ == '__main__':
    if '--breakpoints' in sys.argv:
        sys.exit(run_breakpoints())
    if '--flag-negative-controls' in sys.argv:
        sys.exit(run_flag_negative_controls())
    if '--design-only' in sys.argv:
        sys.exit(run_design()[1])
    if '--design-negative-controls' in sys.argv:
        sys.exit(run_design_negative_controls())
    if '--search-only' in sys.argv:
        sys.exit(run_search())
    if '--layers-only' in sys.argv:
        sys.exit(run_layers())
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
    rc |= run_design()[1]
    # the search box is part of the reader a visitor uses, and until
    # 2026-08-02 nothing here ever typed into it -- see run_search
    rc |= run_search()
    # the layer buttons are the other thing a reader presses constantly and
    # nothing here had ever pressed -- see run_layers
    rc |= run_layers()
    if '--no-eval' not in sys.argv:
        rc |= run_gate(EVAL_ON=True)
        rc |= run_tabs()
    sys.exit(rc | (1 if vf else 0))
