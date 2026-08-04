# -*- coding: utf-8 -*-
"""THE PRINTED FOLIO OF EVERY PDF PAGE, read from the running header.

`_xc/reseg/pline.py` gives the printed LINES of a volume but throws the page's
header away -- which is where the folio is.  This reproduces `extract.py`'s own
page acceptance (`raw_pages` + `split_page`, glyph errata applied, exactly as
pline does) and keeps `split_page`'s `printed`, then re-runs extract.py's OWN
front-matter cut and folio interpolation, so the map is the same arithmetic the
corpus was built with rather than a second guess at it.

  folio(vol) -> {pdf_page: printed_int}   over BODY pages only

VERIFIED, not assumed: `check(vol)` compares the map against the corpus's own
(pdf_page -> printed) pairs.  Every disagreement is reported.
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(ROOT, '_xc', 'reseg'))
import pline  # noqa: E402

CACHE = os.path.join(HERE, '_folio_%s.json')


def _build(vol):
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
    ns = {}
    exec(compile(src0.replace(_raw, GLYPH), 'extract_scan', 'exec'), ns)
    pdf = pline.pdf_of(vol)
    pgs = [d for d in (ns['split_page'](x) for x in ns['raw_pages'](pdf)) if d]
    for i, p in enumerate(pgs, 1):
        p['pdf_page'] = i
    first = next((i for i, p in enumerate(pgs)
                  if any('Namo tassa Bhagavato' in l for l in p['body'])), None)
    if first is None:
        first = next((i for i, p in enumerate(pgs)
                      if isinstance(p['printed'], int) and p['printed'] <= 3), 0)
    body = list(pgs[first:])
    for i, p in enumerate(body):
        if isinstance(p['printed'], int):
            continue
        nxt = next((j for j in range(i + 1, len(body)) if isinstance(body[j]['printed'], int)), None)
        prv = next((j for j in range(i - 1, -1, -1) if isinstance(body[j]['printed'], int)), None)
        if nxt is not None:
            p['printed'] = body[nxt]['printed'] - (nxt - i)
        elif prv is not None:
            p['printed'] = body[prv]['printed'] + (i - prv)
    return {str(p['pdf_page']): p['printed'] for p in body
            if isinstance(p['printed'], int)}


def folio(vol):
    p = CACHE % vol
    if os.path.exists(p):
        d = json.load(open(p, encoding='utf-8'))
    else:
        d = _build(vol)
        json.dump(d, open(p, 'w', encoding='utf-8'))
    return {int(k): v for k, v in d.items()}


def check(vol):
    ps = json.load(open('%s/site/%s.json' % (ROOT, vol), encoding='utf-8'))['paragraphs']
    F = folio(vol)
    ok = bad = 0
    rows = []
    seen = set()
    for p in ps:
        pg, pr = p.get('pdf_page'), p.get('printed')
        if not pg or not isinstance(pr, int) or pg in seen:
            continue
        seen.add(pg)
        if F.get(pg) == pr:
            ok += 1
        else:
            bad += 1
            rows.append((pg, pr, F.get(pg)))
    return ok, bad, rows


if __name__ == '__main__':
    vols = [a for a in sys.argv[1:] if not a.startswith('-')]
    if not vols:
        man = json.load(open(ROOT + '/site/reader/manifest.json', encoding='utf-8'))['volumes']
        vols = sorted(man)
    T = B = 0
    for v in vols:
        try:
            ok, bad, rows = check(v)
        except Exception as e:
            print('ERR', v, type(e).__name__, e)
            continue
        T += ok
        B += bad
        print('%-11s pages with a paragraph: %4d agree, %3d DISAGREE %s'
              % (v, ok, bad, rows[:4] if bad else ''))
    print('TOTAL %d agree, %d disagree' % (T, B))
