# -*- coding: utf-8 -*-
"""The PRINTED LINE STREAM of a volume, in reading order, cached to JSON.

This is the EVIDENCE SOURCE the side-map checks use.  It is deliberately NOT
derived from the corpus or from any remap: it is `pipeline/extract.py`'s own
`raw_pages` + `split_page` (with the glyph-errata register, as every consumer
that reads the PDF must apply -- see _fnprobe/rebuild_corpus.py), so a check
written against it is a check against the printed page and not against the
arithmetic that produced the thing being checked.

Each item: [pdf_page, line_index_within_page, indent, text].
`pdf_page` is numbered exactly as extract() numbers it -- among the pages
split_page ACCEPTS, not among the raw pages.
"""
import json, os, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_pline_%s.json')

FOLDERS = ('pali-unicode', 'atthakatha-unicode', 'tika-unicode')


def pdf_of(v):
    for d in FOLDERS:
        p = '%s/%s/%s.pdf' % (ROOT, d, v)
        if os.path.exists(p):
            return p
    raise SystemExit('no pdf for ' + v)


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
    pdf = pdf_of(vol)
    ok = [d for d in (ns['split_page'](x) for x in ns['raw_pages'](pdf)) if d]
    out = []
    for i, d in enumerate(ok, 1):
        for j, ln in enumerate(d['body']):
            if ln.strip():
                out.append([i, j, len(ln) - len(ln.lstrip()), ln.strip()])
    return out


def stream(vol):
    p = CACHE % vol
    if os.path.exists(p):
        return json.load(open(p, encoding='utf-8'))
    s = _build(vol)
    json.dump(s, open(p, 'w', encoding='utf-8'), ensure_ascii=False)
    return s


if __name__ == '__main__':
    v = sys.argv[1] if len(sys.argv) > 1 else '20KhuA01'
    s = stream(v)
    print('%s: %d printed body lines over %d pdf pages' % (v, len(s), s[-1][0]))
