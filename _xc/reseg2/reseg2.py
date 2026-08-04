# -*- coding: utf-8 -*-
"""GENERALISED re-segmentation by the PRINTED INDENT.  reseg.py with the
three hardcoded constants (VOL, LO, HI) lifted out.

    python3 _xc/reseg2/reseg2.py <VOL> [--write]
    MODE=off  -> the control: must reproduce the SHIPPED paragraphs exactly.

LO/HI are read from `build_khu_volume.py`'s OWN spec ('books' tuple), not
guessed from the shipped file, so the body extent is the builder's and not a
re-derivation of it.

THE RULE (unchanged from reseg.py): a paragraph opens at an indent and
continues at the body column.  Indent alone is not enough -- block quotations
are set with every line indented -- so the separator is the LOOKAHEAD: after a
paragraph's first line the text returns to the body column.
"""
import sys, os, re, json, importlib.util, statistics, collections
ROOT = os.path.abspath('.')
sys.path.insert(0, ROOT + '/pipeline')
sys.path.insert(0, ROOT + '/_xc/reseg')
import pline

VOL = [a for a in sys.argv[1:] if not a.startswith('-')][0]
PDF = pline.pdf_of(VOL)

# --- LO/HI from the builder's own spec -------------------------------------
_bk = open(ROOT + '/pipeline/build_khu_volume.py', encoding='utf-8').read()
_i = _bk.find("\n '%s': {" % VOL)
assert _i > 0, 'no spec for %s in build_khu_volume.py' % VOL
_m = re.search(r"^\s+'books': \[(.*?)\],\s*$", _bk[_i:_i + 20000], re.M)
assert _m, 'no books tuple for %s' % VOL
_books = eval('[' + _m.group(1) + ']')
assert len(_books) == 1, '%s has %d books; reseg2 handles one' % (VOL, len(_books))
LO, HI, NPARA = _books[0][1], _books[0][2], _books[0][4]

import extract as E
spec = importlib.util.spec_from_file_location('rc', ROOT + '/_fnprobe/rebuild_corpus.py')
rc = importlib.util.module_from_spec(spec)
_argv = sys.argv[:]
sys.argv = ['rebuild_corpus.py']
spec.loader.exec_module(rc)
sys.argv = _argv

MODE = os.environ.get('MODE', 'indent')
OLO  = int(os.environ.get('OLO', 3))
OHI  = int(os.environ.get('OHI', 6))
BODY = int(os.environ.get('BODY', 0))
OUT  = os.environ.get('OUT', '_xc/reseg2/%s.json' % VOL)

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
_ok = [d for d in (_scan['split_page'](x) for x in _scan['raw_pages'](PDF)) if d]
stream = []
for i, d in enumerate(_ok, 1):
    for j, ln in enumerate(d['body']):
        if ln.strip():
            stream.append((i, j, len(ln) - len(ln.lstrip()), ln.strip()))

BREAKS = set()
if MODE != 'off':
    for k, (pg, j, ind, st) in enumerate(stream):
        if not (OLO <= ind <= OHI): continue
        nxt = stream[k + 1] if k + 1 < len(stream) else None
        if nxt is None: continue
        if nxt[2] != BODY: continue
        BREAKS.add((pg, j))

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
_sp = '%s/site/%s.json' % (ROOT, VOL)
_sp = _sp + '.prereseg2' if os.path.exists(_sp + '.prereseg2') else _sp
ship = json.load(open(_sp, encoding='utf-8'))['paragraphs']
SL = sorted(len(p.get('text') or '') for p in ship)
print('%s  MODE=%s  band %d-%d  body col %d  spec range %d-%d (spec ¶ %d)'
      % (VOL, MODE, OLO, OHI, BODY, LO, HI, NPARA))
print('  shipped   %5d ¶   median %6d  max %6d' % (len(ship), statistics.median(SL), max(SL)))
print('  reseg     %5d ¶   median %6d  max %6d  mean %d'
      % (len(keep), statistics.median(L), max(L), sum(L)/len(L)))
print('  numbered %d  unnumbered %d  headings %d  heads/¶ %.2f'
      % (sum(1 for p in keep if p.get('n')), sum(1 for p in keep if p.get('unnumbered')),
         len(heads), len(heads)/len(keep)))
print('  ¶ >4000 chars: %d   >2000: %d' % (sum(1 for x in L if x > 4000),
                                           sum(1 for x in L if x > 2000)))
letters = lambda ps: re.sub(r'[^0-9A-Za-zĀāĪīŪūṀṁṄṅÑñṬṭḌḍṆṇḶḷ]', '',
                            ''.join(p.get('text') or '' for p in ps))
a, b = letters(ship), letters(keep)
print('  TEXT: shipped %d letters / reseg %d / delta %+d / identical=%s'
      % (len(a), len(b), len(b) - len(a), a == b))
if a != b:
    i = next((i for i in range(min(len(a), len(b))) if a[i] != b[i]), min(len(a), len(b)))
    print('     first divergence at %d:\n       ship  %r\n       reseg %r' % (i, a[i:i+90], b[i:i+90]))

# ---- STRICT REFINEMENT: every shipped ¶ == space-join of a contiguous run ---
rm, j, ok, fail = {}, 0, 0, []
for i, sp in enumerate(ship):
    st = sp.get('text') or ''
    rm[i] = j
    acc, k = '', j
    while k < len(keep):
        t = keep[k]['text'] or ''
        acc = t if k == j else acc + ' ' + t
        k += 1
        if len(acc) >= len(st): break
    if acc == st: ok += 1
    else: fail.append(i)
    j = k
print('  STRICT REFINEMENT: %d of %d shipped ¶ are exact space-joins; consumed %d of %d new; FAIL %d'
      % (ok, len(ship), j, len(keep), len(fail)))
if fail: print('     first failures:', fail[:8])

bad = [i for i in range(1, len(keep))
       if ((keep[i-1]['text'] or '').rstrip() or ' ')[-1] not in '.?!–-—:”']
print('  breaks not after a sentence end: %d of %d (%.1f%%)'
      % (len(bad), len(keep)-1, 100*len(bad)/max(1, len(keep)-1)))

if '--write' in sys.argv:
    json.dump({'paragraphs': keep, 'headings': heads},
              open(os.path.join(ROOT, OUT), 'w', encoding='utf-8'), ensure_ascii=False)
    if ok == len(ship) and not fail:
        json.dump({str(k): v for k, v in rm.items()},
                  open('%s/_xc/reseg2/ord_remap_%s.json' % (ROOT, VOL), 'w', encoding='utf-8'),
                  ensure_ascii=False)
        print('  WROTE %s and ord_remap_%s.json' % (OUT, VOL))
    else:
        print('  WROTE %s   (NO REMAP: refinement failed)' % OUT)
