# -*- coding: utf-8 -*-
"""PROTOTYPE ONLY.  Re-segment 20KhuA01 by the PRINTED INDENT.

Writes _xc/reseg/20KhuA01.json.  Nothing in site/ or corpus/ is touched.

The text stream is EXACTLY the one `_fnprobe/rebuild_corpus.py` builds — same
raw_pages + glyph errata, same split_page, same classify_heading, same
`cur['text'] += ' ' + st`.  The ONLY change is one extra flush condition, so
the concatenated letters cannot move.  MODE=off reproduces the shipped 109.

THE RULE.  A paragraph opens at an indent and continues at the body column
(`build_khu_volume.py:127`).  Indent alone is NOT enough: the edition also sets
BLOCK QUOTATIONS with every line indented, and on pdf p22 the quotation's
continuation lines sit at indent 5 — the same column an ordinary paragraph
opens at.  The separator is the LOOKAHEAD: after a paragraph's first line the
text returns to the body column; inside a quote block it does not.
"""
import sys, os, re, json, importlib.util, statistics, collections
ROOT = os.path.abspath('.')
sys.path.insert(0, ROOT + '/pipeline')
import extract as E

spec = importlib.util.spec_from_file_location('rc', ROOT + '/_fnprobe/rebuild_corpus.py')
rc = importlib.util.module_from_spec(spec)
sys.argv = ['rebuild_corpus.py']
spec.loader.exec_module(rc)

VOL, PDF = '20KhuA01', ROOT + '/atthakatha-unicode/20KhuA01.pdf'
LO, HI = 19, 234
MODE   = os.environ.get('MODE', 'indent')
OLO    = int(os.environ.get('OLO', 3))
OHI    = int(os.environ.get('OHI', 6))
BODY   = int(os.environ.get('BODY', 0))     # the body column, measured: 0 on all 216 pages
OUT    = os.environ.get('OUT', '_xc/reseg/%s.json' % VOL)

# ---------- pass 1: the body-line stream, with indents, in reading order ----
src0 = open(ROOT + '/pipeline/extract.py', encoding='utf-8').read()
_raw = """def raw_pages(pdf):
    t=subprocess.run(['pdftotext','-enc','UTF-8','-layout',pdf,'-'],
                     capture_output=True).stdout.decode('utf-8','replace')
    return t.split('\\x0c')"""
assert src0.count(_raw) == 1, 'raw_pages in extract.py has moved'
GLYPH = _raw.replace(
    "    return t.split('\\x0c')",
    "    import json as _j, os as _o\n"
    "    _v = _o.path.basename(pdf)[:-4]\n"
    "    try:\n"
    "        _r = _j.load(open(_o.path.join(_o.path.dirname(_o.path.dirname(\n"
    "            _o.path.abspath(pdf))), 'data', 'glyph_errata.json'), encoding='utf-8'))\n"
    "    except Exception:\n"
    "        _r = {'entries': []}\n"
    "    for _e in _r.get('entries', ()):\n"
    "        if _e.get('vol') == _v and _e.get('apply_from') and _e.get('apply_to'):\n"
    "            t = t.replace(_e['apply_from'], _e['apply_to'])\n"
    "    return t.split('\\x0c')")

_scan = {}
exec(compile(src0.replace(_raw, GLYPH), 'extract_scan', 'exec'), _scan)
# pdf_page is the index among the pages split_page ACCEPTS, exactly as
# extract() numbers them (`pgs=[p for p in (...) if p]; enumerate(pgs,1)`).
# Numbering the raw pages instead put the whole map one or more pages out.
_ok = [d for d in (_scan['split_page'](x) for x in _scan['raw_pages'](PDF)) if d]
stream = []                                  # (pdf_page, line_idx, indent, text)
for i, d in enumerate(_ok, 1):
    for j, ln in enumerate(d['body']):
        if ln.strip():
            stream.append((i, j, len(ln) - len(ln.lstrip()), ln.strip()))

BREAKS = set()
if MODE == 'plumb':
    # THE PRINTED PAGE'S OWN SIGNAL, read from the PDF char stream.
    # Every body line starts at x0=62.6; the indent is set with LITERAL SPACE
    # CHARACTERS, not an x offset, so pdfplumber's x0 alone shows nothing.
    # Measured over the whole body (pdf pages 20-235 raw):
    #     0 leading spaces -> pdftotext indent 0      4217 lines   body column
    #     1 leading space  -> pdftotext indent 3-6     634 lines   PARAGRAPH OPENER
    #     3 leading spaces -> pdftotext indent 10-17   191 lines   display gathā
    # The classes do not overlap.  Block quotations are a separate text block
    # at x0 > 62.6 and are excluded by the x0 filter, which is why the pure
    # pdftotext band 3-6 over-breaks: it cannot see that difference.
    import pdfplumber, collections as _c
    _pl = pdfplumber.open(PDF)
    _lead = {}                                  # raw pdf page -> [(lead, text)]
    for _i in range(len(_pl.pages)):
        _rows = _c.defaultdict(list)
        for _ch in _pl.pages[_i].chars: _rows[round(_ch['top'], 0)].append(_ch)
        _ls = []
        for _t in sorted(_rows):
            _cs = sorted(_rows[_t], key=lambda c: c['x0'])
            _tx = ''.join(c['text'] for c in _cs)
            if not _tx.strip(): continue
            _ls.append((round(_cs[0]['x0'], 1), _tx))
        _cut = next((k for k, (x, t) in enumerate(_ls) if t.strip().startswith('_________')), len(_ls))
        _lead[_i + 1] = [(len(t) - len(t.lstrip()), t.strip())
                         for x, t in _ls[1:_cut] if abs(x - 62.6) <= 0.5]
    _pl.close()
    _raws = [k for k, d in enumerate((_scan['split_page'](x)
             for x in _scan['raw_pages'](PDF)), 1) if d]   # extract idx -> raw page
    _norm = lambda t: re.sub(r'[^A-Za-zĀāĪīŪūṀṁṄṅÑñṬṭḌḍṆṇḶḷ]', '', t)
    _hit = _tot = 0
    for pg, j, ind, st in stream:
        if not (3 <= ind <= 8): continue
        _tot += 1
        cand = _lead.get(_raws[pg - 1], [])
        k = _norm(st)[:40]
        m = [l for l, t in cand if _norm(t)[:40] == k]
        if m and m[0] == 1: BREAKS.add((pg, j)); _hit += 1
    print('  plumb: %d of %d indented lines matched as 1-space openers' % (_hit, _tot))
else:
    for k, (pg, j, ind, st) in enumerate(stream):
        if not (OLO <= ind <= OHI): continue
        nxt = stream[k + 1] if k + 1 < len(stream) else None
        if nxt is None: continue
        if nxt[2] != BODY: continue
        BREAKS.add((pg, j))

# ---------- pass 2: extract.py's own loop, with the extra flush -------------
src = src0.replace(_raw, GLYPH)
src = src.replace(
    """            kind=classify_heading(st,len(ln)-len(ln.lstrip()))
            if kind:""",
    """            kind=classify_heading(st,len(ln)-len(ln.lstrip()))
            if kind:
                if cur is not None and cur.get('unnumbered'): flush()""")
OPEN = """cur={'n':None,
                     'book':book['title'] if book else None,
                     'vagga':vagga['title'] if vagga else None,
                     'sutta':sutta['title'] if sutta else None,
                     'sutta_n':sutta['n'] if sutta else None,
                     'printed':p['printed'],'pdf_page':p['pdf_page'],'text':st,
                     'unnumbered':True,
                     'id':'/'.join([slug(book['title']) if book else 'X',
                                    slug(vagga['title']) if vagga else 'X',
                                    slug(sutta['title']) if sutta else 'X',
                                    'u%d' % p['pdf_page']])}"""
old = """            elif cur is not None: cur['text']+=' '+st"""
new = ("""            elif cur is not None:
                if BREAK(p['pdf_page'],_li): flush()
                if cur is None: """ + OPEN + """
                else: cur['text']+=' '+st
            else:
                """ + OPEN)
assert src.count(old) == 1
src = src.replace(old, new)
src = src.replace("""        for ln in p['body']:
            st=ln.strip()
            if not st: continue""",
"""        for _li,ln in enumerate(p['body']):
            st=ln.strip()
            if not st: continue""")

ns = {'BREAK': (lambda pg, li: MODE != 'off' and (pg, li) in BREAKS)}
exec(compile(src, 'extract_reseg', 'exec'), ns)
ns['PARA'] = re.compile(r'^\s*(\d{1,4})(?:-\d+)?\.\s+(?=\S)')
pgs, paras, heads = ns['extract'](PDF)
paras = rc.derive(VOL, paras)
keep = rc.derive(VOL, [p for p in paras if LO <= (p.get('pdf_page') or 0) <= HI])

L = sorted(len(p['text']) for p in keep)
print('MODE=%s  opener band %d-%d  body column %d' % (MODE, OLO, OHI, BODY))
print('  paragraphs %d   median %d   mean %d   max %d   total %d'
      % (len(keep), statistics.median(L), sum(L)/len(L), max(L), sum(L)))
print('  numbered %d  unnumbered %d   headings %d  heads/¶ %.2f'
      % (sum(1 for p in keep if p.get('n')), sum(1 for p in keep if p.get('unnumbered')),
         len(heads), len(heads)/len(keep)))
print('  ¶ >4000 chars: %d   >2000: %d' % (sum(1 for x in L if x > 4000),
                                           sum(1 for x in L if x > 2000)))
ship = json.load(open('%s/site/%s.json' % (ROOT, VOL), encoding='utf-8'))['paragraphs']
letters = lambda ps: re.sub(r'[^0-9A-Za-zĀāĪīŪūṀṁṄṅÑñṬṭḌḍṆṇḶḷ]', '',
                            ''.join(p.get('text') or '' for p in ps))
a, b = letters(ship), letters(keep)
print('  TEXT: shipped %d letters / reseg %d letters / delta %+d / identical=%s'
      % (len(a), len(b), len(b) - len(a), a == b))
if a != b:
    i = next((i for i in range(min(len(a), len(b))) if a[i] != b[i]), min(len(a), len(b)))
    print('     first divergence at %d: ship %r / reseg %r' % (i, a[i:i+70], b[i:i+70]))
# how many breaks land where the previous paragraph does NOT end a sentence
bad = [i for i in range(1, len(keep))
       if ((keep[i-1]['text'] or '').rstrip() or ' ')[-1] not in '.?!–-—:”']
print('  breaks not after a sentence end: %d of %d (%.1f%%)'
      % (len(bad), len(keep)-1, 100*len(bad)/max(1, len(keep)-1)))
for i in bad[:5]:
    print('     p%-4d ...%s  ||  %s' % (keep[i-1]['pdf_page'],
          (keep[i-1]['text'] or '')[-52:], (keep[i]['text'] or '')[:52]))
if os.environ.get('WRITE'):
    json.dump({'paragraphs': keep, 'headings': heads},
              open(os.path.join(ROOT, OUT), 'w', encoding='utf-8'), ensure_ascii=False)
    print('  WROTE %s' % OUT)
