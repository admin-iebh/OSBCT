# -*- coding: utf-8 -*-
"""check_bold_fidelity.py -- compare the CORPUS'S BOLD against the PRINTED PAGE.

The edition prints in bold the words and phrases it is glossing.  Two things
already depend on that mark being right: the word-lookup panel's promotion rule
tests the bolded phrase against the paragraph on screen, and `link_by_gloss.py`
used the edition's bold as its DECIDER when rebuilding canon->commentary links.
THE BOLD HAD NEVER BEEN CHECKED AGAINST THE PRINTED PAGE.  What commit
`4d4a1db7` proved is only that spans SURVIVE re-segmentation -- 1,580/1,580
selecting byte-identical substrings -- which assumes `extract_bold.py` was right
to begin with.  Nothing tested that.

HOW THE BOLD IS READ OFF THE PAGE.  NOT from `fontname`: these PDFs carry ONE
font, `EHIOGN+VZTime`, and set bold by TEXT RENDER MODE 2 (fill+stroke faux
bold).  `pdfplumber` exposes `fontname` and does NOT expose the render mode, so
the font test that worked for indentation cannot work here -- measured on
`20KhuA01`, every character of every page reports the same fontname.  The render
mode is confirmed from the RAW CONTENT STREAM, independently of any text
interpreter: raw page 143 of `20KhuA01` carries eight `2 Tr` blocks holding 160
glyphs, and the rendered page (`pdftoppm`) shows exactly those words in bold.

WHY THIS IS NOT CIRCULAR.  `extract_bold.py` reads the same render mode, so the
PRIMITIVE is shared -- and it is verified against a rendered image, above, not
assumed.  What is NOT shared, and what this check actually tests, is the
ALIGNMENT: `extract_bold` locates a paragraph by `sig.find` over a
whole-volume signature built from pdfminer's own reading order, with a
sentence-level fallback when that fails.  This check never runs that.  It takes
the PRINTED LINE as the unit, locates each line in the corpus letter string with
the k-gram index `check_page_fidelity.py` already uses, and compares the page's
bold flags with the corpus's bold flags position by position.  Every fault
`sig.find` and its fallback can make -- a span on the wrong paragraph, a span
dropped, a span whose extent is short or long -- is visible to it.

WHAT IT DOES NOT DO.  It fixes nothing and writes no baseline.  A baseline over
unmeasured faults freezes them in.

Usage:
    python3 pipeline/check_bold_fidelity.py <VOL> [<VOL> ...]
    python3 pipeline/check_bold_fidelity.py <VOL> --controls
    python3 pipeline/check_bold_fidelity.py --all --out DIR --budget 35
    python3 pipeline/check_bold_fidelity.py <VOL> --dump DIR
"""
import sys, os, re, json, bisect, collections, time, unicodedata

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
sys.path.insert(0, os.path.join(ROOT, 'pipeline'))
import check_page_fidelity as CPF                      # noqa: E402

# DIGITS ARE DROPPED FROM BOTH SIDES.  The apparatus is set below `BODYSIZE`
# and a footnote MARKER is part of the apparatus -- it is a superscript at 8pt
# -- so the page's glyph stream loses it while the corpus paragraph text keeps
# it inline (`appaṭihatañāṇanimittānuttara4vimokkha`).  Matched with digits in,
# every line carrying a marker fails to locate and 26% of 20KhuA01's lines
# read as absent.  `check_page_fidelity.py` already keeps a digit-free
# projection of the corpus for the same reason; here it is the ONLY projection,
# because a bold span over a digit is not a thing the edition sets.
def letters(s):
    return CPF.DIGIT.sub('', CPF.letters(s))


def keepch(ch):
    return not (CPF.ALPHA.match(ch) or ch.isdigit())


Index = CPF.Index
jload = CPF.jload
NFC = lambda s: unicodedata.normalize('NFC', s or '')

FOLDER = {'canon': 'pali-unicode', 'commentary': 'atthakatha-unicode',
          'subcommentary': 'tika-unicode'}


def layer_of(vol):
    for layer, folder in FOLDER.items():
        if os.path.exists(os.path.join(ROOT, folder, vol + '.pdf')):
            return layer
    return None


def pdf_of(vol):
    l = layer_of(vol)
    return os.path.join(ROOT, FOLDER[l], vol + '.pdf') if l else None


# ------------------------------------------------------------------ page side
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter   # noqa
from pdfminer.pdfpage import PDFPage                                    # noqa
from pdfminer.converter import PDFPageAggregator                        # noqa
from pdfminer.layout import LTChar                                      # noqa


class RM(PDFPageAggregator):
    """Capture the text render mode on every glyph.

    pdfminer's layout objects do not carry it and pdfplumber does not expose
    it; `PDFTextState.render` is the only place it lives, and it is only in
    scope inside `render_string`.  This is the same capture `extract_bold.py`
    makes -- and it is the one thing the two share.  It is verified against a
    rendered page image and against the raw content stream, so it is measured,
    not assumed.
    """
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self._r = 0

    def render_string(self, ts, *a, **k):
        self._r = getattr(ts, 'render', 0)
        return super().render_string(ts, *a, **k)

    def render_char(self, *a, **k):
        adv = super().render_char(*a, **k)
        o = self.cur_item._objs
        if o and isinstance(o[-1], LTChar):
            o[-1].rendermode = self._r
        return adv


def _walk(o):
    for e in o:
        if isinstance(e, LTChar):
            yield e
        elif hasattr(e, '__iter__'):
            yield from _walk(e)


BODYSIZE = 11       # the apparatus is set smaller; body is 12
HEADGAP = 16        # a running head stands this far above the first body line
YTOL = 2.0          # two glyphs within this many points are on one line


def page_lines(vol, cache=True):
    """Printed lines with a BOLD FLAG PER CHARACTER, in reading order.

    Returns [[raw_page_1based, y, letters, flags]] where `letters` has been put
    through the same alphabet filter the corpus side uses and `flags` is the
    matching list of booleans.  Filtering to letters is what makes the two
    sides comparable at all: the PDF's glyph stream and `pdftotext`'s line
    stream disagree about spaces, and neither disagreement is evidence of
    anything.
    """
    cp = os.path.join(ROOT, '_xc', 'boldfid', '_pg2_%s.json' % vol)
    if cache and os.path.exists(cp):
        return json.load(open(cp, encoding='utf-8'))
    rs = PDFResourceManager()
    dev = RM(rs)
    ip = PDFPageInterpreter(rs, dev)
    out, heads = [], {}
    with open(pdf_of(vol), 'rb') as f:
        for pno, pg in enumerate(PDFPage.get_pages(f), 1):
            ip.process_page(pg)
            chars = [c for c in _walk(dev.get_result()) if c.size >= BODYSIZE]
            if not chars:
                continue
            ys = sorted({round(c.y1) for c in chars}, reverse=True)
            drop = ys[0] if (len(ys) >= 2 and (ys[0] - ys[1]) > HEADGAP) else None
            if drop is not None:
                hd = sorted((c for c in chars if round(c.y1) == drop),
                            key=lambda c: c.x0)
                heads[pno] = ''.join(c.get_text() for c in hd)
            chars = [c for c in chars if round(c.y1) != drop]
            if not chars:
                continue
            chars.sort(key=lambda c: (-c.y1, c.x0))
            grp, cury = [], None
            for c in chars:
                if cury is None or abs(c.y1 - cury) > YTOL:
                    grp.append([])
                    cury = c.y1
                grp[-1].append(c)
            for g in grp:
                g.sort(key=lambda c: c.x0)
                L, F = [], []
                for c in g:
                    b = getattr(c, 'rendermode', 0) == 2
                    for ch in NFC(c.get_text()):
                        if not keepch(ch):
                            continue
                        L.append(ch)
                        F.append(b)
                if L:
                    out.append([pno, round(g[0].y1, 1), ''.join(L), F])
    r = {'lines': out, 'heads': heads}
    if cache:
        json.dump(r, open(cp, 'w', encoding='utf-8'), ensure_ascii=False)
    return r


# ---------------------------------------------------------------- corpus side

def _charmap(t):
    """char index -> letter index, and the letter count."""
    m, n = [], 0
    for ch in t:
        m.append(n)
        if keepch(ch):
            n += 1
    m.append(n)
    return m, n


def _parts(txt, sp):
    """Split on newlines the way `add()` does, carrying the spans with them."""
    out, base = [], 0
    for part in str(txt or '').split('\n'):
        if CPF.letters(part):
            n = len(part)
            out.append((part, [(max(a, base) - base, min(b, base + n) - base)
                               for a, b in sp if b > base and a < base + n]))
        base += len(part) + 1
    return out


def corpus_bold(vol, control=None):
    """THE DATA STREAM: every paragraph's own text, in ordinal order, with the
    bold the maps put on it -- and, beside it, whether the reader DRAWS it.

    It is deliberately NOT `check_page_fidelity.corpus_stream`.  That function
    models what `reader2.html` draws, and what the reader draws is exactly the
    thing in question: 19AnA03 stores 506 of its paragraphs as `verse/` entries
    with an EMPTY `groups` and an `after`, so the reader draws the `after`
    blocks and the paragraph text -- carrying all 8,379 of the volume's bold
    spans -- is never rendered at all.  Judging the spans against a stream that
    does not contain the text they address would report every one of them as
    missing from the page, which is false: they are missing from the SCREEN.
    The two questions are separated:

      DATA  -- are the spans where the printed bold is?   (this stream)
      DRAWN -- does the reader put them on the page?      (`SPINE` / `BAND`)

    `SPINE` is what a reader gets opening the volume from the tree, `BAND` what
    they get with it hanging under a canon paragraph.  `block()` calls
    `fmtBold` -- the ONLY path that takes paragraph spans -- in its third
    branch alone, and the first two swallow every `asSpine` paragraph, so
    `SPINE` carries the `sections` gatha spans and nothing else.

    THE VERSE MAP IS NOT DRAWN FROM HERE.  A `verse/` entry's `groups` /
    `before` / `after` hold the printed lines a second time, and emitting them
    beside the paragraph text would put the same page line in the stream twice,
    once with its spans and once without -- so a monotone locator would score
    the second copy as bold missing.  They are left out, and printed lines that
    live ONLY there are reported as absent under their own name.
    """
    S = os.path.join(ROOT, 'site')
    c = jload('%s/%s.json' % (S, vol))
    if not c:
        return None
    bm = jload('%s/reader/bold/%s.bold.json' % (S, vol), {}) or {}
    sm = jload('%s/reader/bold/%s.sect.json' % (S, vol), {}) or {}
    sec = jload('%s/reader/sections/%s.json' % (S, vol), {}) or {}
    vm = jload('%s/reader/verse/%s.json' % (S, vol), {}) or {}
    udd = jload('%s/reader/uddana/%s.json' % (S, vol), {}) or {}
    btl = jload('%s/reader/booktitle/%s.json' % (S, vol), {}) or {}
    inc = jload('%s/reader/incipit/%s.json' % (S, vol), {}) or {}
    paras = c.get('paragraphs', [])

    # --- CONTROLS act on the CORPUS side only; the page is never touched.
    if control == 'wrongvol':
        bm = jload('%s/reader/bold/%s.bold.json'
                   % (S, CPF.control_alt_vol(vol)), {}) or {}
        sm = {}
    elif control == 'nobold':
        bm, sm = {}, {}
    elif control == 'shiftspans':
        bm = dict((k, [[a + 5, b + 5] for a, b in v]) for k, v in bm.items())
        sm = dict((k, [[a + 5, b + 5] for a, b in v]) for k, v in sm.items())
    elif control == 'halfspans':
        bm = dict((k, v[::2]) for k, v in bm.items())
        sm = dict((k, v[::2]) for k, v in sm.items())
    elif control == 'widenspans':
        bm = dict((k, [[a, b + 6] for a, b in v]) for k, v in bm.items())
        sm = dict((k, [[a, b + 6] for a, b in v]) for k, v in sm.items())

    segs = []                      # (cls, text, ord, spans, drawn_in_spine)
    for o, p in enumerate(paras):
        so = str(o)
        for l in (btl.get(so) if isinstance(btl.get(so), list)
                  else ([btl[so]] if so in btl else [])):
            for t, _x in _parts(l, []):
                segs.append(('T', t, o, [], 0))
        if so in inc:
            for t, _x in _parts(inc[so], []):
                segs.append(('I', t, o, [], 0))
        for i, e in enumerate(sec.get(so, [])):
            k = e.get('k')
            cls = 'V' if k == 'gatha' else ('P' if k == 'prose' else 'H')
            sp = ([tuple(x) for x in sm.get('%s:%d' % (so, i), [])]
                  if k == 'gatha' else [])
            for t, ps in _parts(e.get('l'), sp):
                segs.append((cls, t, o, ps, 1))
        for t, ps in _parts(p.get('text', ''),
                            [tuple(x) for x in bm.get(so, [])]):
            segs.append(('P', t, o, ps, 0))
        for b in udd.get(so, []):
            if b.get('label'):
                for t, _x in _parts(b['label'], []):
                    segs.append(('U', t, o, [], 0))
            for l in b.get('lines', []):
                for t, _x in _parts(l, []):
                    segs.append(('U', t, o, [], 0))

    buf, spans, DATA, SPINE, BAND = [], [], [], [], []
    pos = 0
    for cls, text, o, ps, dsp in segs:
        s2 = letters(text)
        cm, _n = _charmap(text)
        fd = [0] * len(s2)
        for a, b in ps:
            la = cm[max(0, min(a, len(text)))]
            lb = cm[max(0, min(b, len(text)))]
            for k in range(la, min(lb, len(s2))):
                fd[k] = 1
        spans.append((pos, pos + len(s2), cls, o))
        buf.append(s2)
        DATA += fd
        SPINE += [x * dsp for x in fd]
        BAND += fd
        pos += len(s2)
    hasgroups = set(int(k) for k, v in vm.items()
                    if isinstance(v, dict) and 'groups' in v)
    return {'c': c, 'segs': segs, 'C': ''.join(buf), 'spans': spans,
            'DATA': DATA, 'SPINE': SPINE, 'BAND': BAND,
            'hasgroups': hasgroups, 'bm': bm, 'sm': sm}


# ------------------------------------------------------------------- the pass

BACK = 40000


def _runs(flags, lo=0, hi=None):
    hi = len(flags) if hi is None else hi
    out, s = [], None
    for i in range(lo, hi):
        if flags[i]:
            if s is None:
                s = i
        elif s is not None:
            out.append((s, i))
            s = None
    if s is not None:
        out.append((s, hi))
    return out


def _accepted(vol):
    """raw pdf page (1-based) -> the page number `extract.py` gives it.

    `extract.py` numbers only the pages `split_page` ACCEPTS, which is the
    numbering every `pdf_page` in `site/<VOL>.json` is in; the PDF's own page
    index is not.  Without this map the corpus's own page range cannot be
    applied to a stream read straight from the PDF, and the edition's front
    matter -- its title pages, its alphabet tables and, worst, its CONTENTS
    LIST, whose lines are the body's own section titles and therefore DO
    locate in the corpus -- is judged as if it were body text.
    """
    ns = {}
    exec(compile(open(os.path.join(ROOT, 'pipeline', 'extract.py'),
                      encoding='utf-8').read(), 'extract_scan', 'exec'), ns)
    m, e = {}, 0
    for i, x in enumerate(ns['raw_pages'](pdf_of(vol)), 1):
        if ns['split_page'](x):
            e += 1
            m[i] = e
    return m


def _body_pages(vol, PL, HEADS, c):
    """Keep the raw pages that hold this volume's body, and say what was cut.

    THE SAME TWO EXCLUSIONS `check_page_fidelity.py` makes, on the same
    evidence.  The range is the corpus's own `pdf_page` extent, mapped back
    through `_accepted`; the edition's word index is recognised from the PAGE,
    by the words it prints in its own running head -- `Padānukkamo`,
    `Piṭṭhaṅkā` -- because a volume holding two works prints one index per work
    and an index can sit in the MIDDLE.
    """
    pgs = [p['pdf_page'] for p in c['paragraphs'] if p.get('pdf_page')] + \
          [h['pdf_page'] for h in c.get('headings', []) if h.get('pdf_page')]
    if not pgs:
        return PL, {'pages_kept': 0}
    LO, HI = min(pgs), max(pgs)
    m = _accepted(vol)
    idx = set(p for p, h in HEADS.items() if CPF.INDEXRE.search(h or ''))
    keep = set(p for p, e in m.items()
               if LO <= e <= HI and p not in idx)
    allp = set(l[0] for l in PL)
    return ([l for l in PL if l[0] in keep],
            {'pages_total': len(allp), 'pages_kept': len(keep & allp),
             'pages_outside_range': len(allp - keep - idx),
             'pages_index': len(idx & allp),
             'extract_pages': len(m), 'corpus_page_lo': LO, 'corpus_page_hi': HI})


def run(vol, control=None, dump=None):
    """Project the page's bold onto the corpus letter axis, then compare runs.

    NOT run by run within a printed LINE.  A bold phrase that wraps -- and 98
    of them do in 20KhuA01 alone -- is two runs on the page and one span in the
    corpus, and judged line by line every one of them came out as the corpus
    bolding MORE than the page: 158 false `MISALIGNED_long` in that volume
    before this was fixed.  Each located line writes its flags into a
    volume-wide array over the corpus's own letters, so a wrapped phrase is one
    run on both sides and the line break is not evidence of anything.

    `KNOWN` marks the letters some located printed line actually covered.
    Nothing outside it is judged: a span in a stretch of corpus the page stream
    never reached is neither right nor wrong here, and is counted under its own
    name rather than scored.
    """
    M = corpus_bold(vol, control)
    if M is None:
        return None
    C, DATA, SPINE, BAND = M['C'], M['DATA'], M['SPINE'], M['BAND']
    IX = Index(C)
    spans = M['spans']
    starts = [s[0] for s in spans]

    def clsat(a, b):
        out = set()
        k = max(0, bisect.bisect_right(starts, a) - 1)
        while k < len(spans) and spans[k][0] < b:
            if spans[k][1] > a:
                out.add(spans[k][2])
            k += 1
        return out

    def clsof(a, b):
        cs = clsat(a, b)
        return 'V' if 'V' in cs else ('H' if (cs & set('HTIU')) else 'P')

    PG = page_lines(vol)
    PL, trim = _body_pages(vol, PG['lines'], PG['heads'], M['c'])
    # --- CONTROL `pageshift` is applied BELOW, to the projected page bold,
    # not here.  Written first as a rotation of the per-line flag lists it was
    # very nearly inert -- 111 run-verdicts moved out of 1,060 -- because it
    # only swapped flags between lines of EQUAL LENGTH, which few are.  That is
    # the fourth control in this project to pass on input it was not actually
    # disturbing, and it is recorded rather than quietly replaced.
    st = collections.Counter()
    ex = collections.defaultdict(list)
    PAGE = [0] * len(C)
    KNOWN = [0] * len(C)
    at = [None] * len(C)
    # A LINE LOCATED BY `findany` IS WEAKER EVIDENCE than one the monotone
    # cursor found, because a short line can occur more than once and the
    # index returns the first.  Every verdict resting on one is tagged and
    # counted separately, so the census can be read with them and without.
    SOFT = [0] * len(C)
    cur = 0
    for pno, y, L, F in PL:
        st['page_lines'] += 1
        if len(F) != len(L):
            st['line_flag_mismatch'] += 1
            continue
        j = IX.find(L, cur)
        how = 'fwd'
        if j < 0:
            j = IX.find(L, max(0, cur - BACK))
            how = 'back'
        if j < 0:
            # THE STREAMS ARE IN DIFFERENT ORDERS IN PLACES.  The data stream
            # is ordinal order; a volume holding several works, or one whose
            # front matter the corpus files after the body, prints them in
            # another.  Without this the cursor sticks and 84% of 18Khu01
            # reads as absent -- which is a fault in the LOCATOR, not in the
            # corpus, so it is recovered and counted under its own name.
            j = IX.findany(L)
            how = 'any'
        if j < 0:
            st['line_absent'] += 1
            st['page_runs_in_absent_lines'] += len(_runs(F))
            st['page_bold_letters_in_absent_lines'] += sum(F)
            if len(ex['absent']) < 12 and any(F):
                ex['absent'].append([pno, L[:70]])
            continue
        st['line_found'] += 1
        st['line_found_' + how] += 1
        for k in range(len(L)):
            KNOWN[j + k] = 1
            if at[j + k] is None:
                at[j + k] = pno
            if how == 'any':
                SOFT[j + k] = 1
            if F[k]:
                PAGE[j + k] = 1
        # THE CURSOR FOLLOWS THE PAGE, INCLUDING BACKWARDS.  The data stream is
        # ordinal order and the printed page is not always in it -- a volume
        # holding several works, front matter the corpus files after the body.
        # Held monotone, the cursor overshoots once and never recovers: 84% of
        # 18Khu01 read as absent, and the `findany` rescues that forced put
        # page-208 lines onto the volume's opening, whose bold then scored as
        # missing.  Resyncing costs nothing and takes 18Khu01 from 418 forward
        # matches to most of the volume.
        cur = j + len(L)

    # A PAGE RUN IS SPLIT AT EVERY SEGMENT BOUNDARY BEFORE IT IS JUDGED.  The
    # edition sets a section heading in bold and then opens the paragraph
    # under it with a bold lemma; strip the punctuation and the newline and
    # the two are ONE run of bold letters -- `CūḷasīlavaṇṇanāAppamattakaṁ` --
    # of which the bold map rightly carries only the second half.  Judged
    # whole, every such pair scored as the map covering half a run: 64 false
    # `MISALIGNED_part` in 07DiA01 alone.  The heading and the paragraph are
    # different segments of the corpus, so the boundary is already known.
    def _split(a, b):
        cuts = [a]
        k = max(0, bisect.bisect_right(starts, a) - 1)
        while k < len(spans) and spans[k][0] < b:
            if a < spans[k][0] < b:
                cuts.append(spans[k][0])
            k += 1
        cuts.append(b)
        return [(cuts[i], cuts[i + 1]) for i in range(len(cuts) - 1)
                if cuts[i + 1] > cuts[i]]

    if control == 'pageshift':
        # Slide the PAGE's own bold seven letters out of register with the page
        # it was read from.  EVIDENCE ONLY: `KNOWN`, `DATA` and the corpus are
        # untouched, so nothing can re-synchronise.
        PAGE = PAGE[-7:] + PAGE[:-7]
    prun = [x for a0, b0 in _runs(PAGE) for x in _split(a0, b0)]
    st['page_run_boundary_splits'] = len(prun) - len(_runs(PAGE))
    for a, b in prun:
        st['page_runs'] += 1
        cl = clsof(a, b)
        st['page_runs_cls_' + cl] += 1
        soft = '_soft' if any(SOFT[a:b]) else ''
        st['page_runs' + soft] += 1 if soft else 0
        cov = sum(DATA[a:b])
        if cov == 0:
            st['MISSED'] += 1
            st['MISSED_' + cl] += 1
            st['MISSED' + soft] += 1 if soft else 0
            if len(ex['missed_' + cl]) < 12:
                ex['missed_' + cl].append([at[a], C[a:b][:70]])
        elif cov == b - a:
            # ...and the extent test must not look across the boundary it was
            # just split at, or every split reports the corpus as bolding more.
            sg = bisect.bisect_right(starts, a) - 1
            left = (a > 0 and DATA[a - 1] and KNOWN[a - 1]
                    and bisect.bisect_right(starts, a - 1) - 1 == sg)
            right = (b < len(C) and DATA[b] and KNOWN[b]
                     and bisect.bisect_right(starts, b) - 1 == sg)
            if left or right:
                st['MISALIGNED_long'] += 1
                st['MISALIGNED_long_' + cl] += 1
                if len(ex['long']) < 12:
                    x, y2 = a, b
                    while x > 0 and DATA[x - 1]:
                        x -= 1
                    while y2 < len(C) and DATA[y2]:
                        y2 += 1
                    ex['long'].append([at[a], C[a:b][:45], C[x:y2][:70]])
            else:
                st['EXACT'] += 1
                st['EXACT_' + cl] += 1
                st['EXACT' + soft] += 1 if soft else 0
        else:
            st['MISALIGNED_part'] += 1
            st['MISALIGNED_part_' + cl] += 1
            st['MISALIGNED_part' + soft] += 1 if soft else 0
            if len(ex['part']) < 12:
                ex['part'].append([at[a], C[a:b][:45],
                                   ''.join(C[k] for k in range(a, b)
                                           if DATA[k])[:45]])
        if not any(SPINE[a:b]) and cov:
            st['in_data_not_drawn_spine'] += 1
            st['in_data_not_drawn_spine_' + cl] += 1
        if not any(BAND[a:b]) and cov:
            st['in_data_not_drawn_band'] += 1

    for a, b in _runs(DATA):
        if not any(KNOWN[a:b]):
            st['corpus_runs_outside_page_stream'] += 1
            continue
        st['corpus_runs'] += 1
        if not any(PAGE[a:b]):
            st['SPURIOUS'] += 1
            st['SPURIOUS_soft'] += 1 if any(SOFT[a:b]) else 0
            st['SPURIOUS_' + clsof(a, b)] += 1
            if len(ex['spurious']) < 12:
                ex['spurious'].append([at[a], C[a:b][:70]])

    st.update(trim)
    nsp = nspc = 0
    for k, v in M['bm'].items():
        if int(k) in M['hasgroups']:
            nsp += len(v)
            nspc += sum(b - a for a, b in v)
    st['spans_on_verse_branch_ordinals'] = nsp
    st['chars_on_verse_branch_ordinals'] = nspc
    st['spans_in_data'] = sum(len(v) for v in M['bm'].values())
    st['sect_spans_in_data'] = sum(len(v) for v in M['sm'].values())
    st['paras_with_bold'] = len(M['bm'])
    st['corpus_letters'] = len(C)
    st['known_letters'] = sum(KNOWN)
    st['data_bold_letters'] = sum(DATA)
    st['spine_bold_letters'] = sum(SPINE)
    st['band_bold_letters'] = sum(BAND)
    st['page_bold_letters'] = sum(PAGE)
    if dump:
        json.dump({'vol': vol, 'stat': dict(st), 'ex': dict(ex)},
                  open(os.path.join(dump, vol + '.json'), 'w'),
                  ensure_ascii=False, indent=1)
    return dict(st), dict(ex)


CONTROLS = ['nobold', 'wrongvol', 'shiftspans', 'halfspans', 'widenspans',
            'pageshift']

KEYS = ['page_lines', 'line_found', 'line_absent', 'page_runs', 'EXACT',
        'MISSED', 'MISALIGNED_part', 'MISALIGNED_long', 'SPURIOUS',
        'in_data_not_drawn_spine', 'spans_in_data']


def allvols():
    v = set()
    for f in FOLDER.values():
        d = os.path.join(ROOT, f)
        if os.path.isdir(d):
            for x in os.listdir(d):
                if x.endswith('.pdf') and os.path.exists(
                        os.path.join(ROOT, 'site', x[:-4] + '.json')):
                    v.add(x[:-4])
    return sorted(v)


def main():
    a = sys.argv[1:]
    out = None
    if '--out' in a:
        i = a.index('--out')
        out = a[i + 1]
        del a[i:i + 2]
    dump = None
    if '--dump' in a:
        i = a.index('--dump')
        dump = a[i + 1]
        del a[i:i + 2]
    budget = 1e9
    if '--budget' in a:
        i = a.index('--budget')
        budget = float(a[i + 1])
        del a[i:i + 2]
    if '--controls' in a:
        a.remove('--controls')
        for vol in a:
            base, _ = run(vol)
            print('%s  base: %s' % (vol, '  '.join(
                '%s=%d' % (k, base.get(k, 0)) for k in KEYS[3:9])))
            for cn in CONTROLS:
                s, _ = run(vol, cn)
                moved = sum(abs(s.get(k, 0) - base.get(k, 0))
                            for k in ('EXACT', 'MISSED', 'MISALIGNED_part',
                                      'MISALIGNED_long', 'SPURIOUS'))
                print('  %-12s moved %6d run-verdicts   %s' % (
                    cn, moved, '  '.join('%s=%d' % (k, s.get(k, 0))
                                         for k in KEYS[3:9])))
        return
    shard = None
    if '--shard' in a:
        i = a.index('--shard')
        shard = tuple(int(x) for x in a[i + 1].split(':'))
        del a[i:i + 2]
    vols = allvols() if '--all' in a else [x for x in a if not x.startswith('--')]
    if shard:
        vols = [v for k, v in enumerate(vols) if k % shard[1] == shard[0]]
    t0 = time.time()
    left = 0
    for vol in vols:
        if out and os.path.exists(os.path.join(out, vol + '.json')):
            continue
        if time.time() - t0 > budget:
            left += 1
            continue
        r = run(vol, dump=(out or dump))
        if r is None:
            print('SKIP', vol)
            continue
        s = r[0]
        print('%-11s lines=%6d abs=%5d pruns=%6d EXACT=%6d MISS=%5d '
              'PART=%5d LONG=%5d SPUR=%5d notdrawn=%5d'
              % (vol, s.get('page_lines', 0), s.get('line_absent', 0),
                 s.get('page_runs', 0), s.get('EXACT', 0), s.get('MISSED', 0),
                 s.get('MISALIGNED_part', 0), s.get('MISALIGNED_long', 0),
                 s.get('SPURIOUS', 0), s.get('in_data_not_drawn_spine', 0)))
    if left:
        print('...budget reached, %d volumes left' % left)


if __name__ == '__main__':
    main()
