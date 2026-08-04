# -*- coding: utf-8 -*-
"""WHAT THE PRINTED PAGE OPENS WITH -- the fixture the browser proof grades against.

`pipeline/check_layout.js` can assert that a `page N` rule is drawn in the right
place only if it knows, independently of the corpus and of `pbreak/`, what the
printed page N begins with.  This writes that: the first body line of the first
pdf page whose running header carries folio N, letters only, from
`_xc/reseg/pline.py` + `_xc/pagemark/folio.py`.

  _xc/pagemark/expect/<VOL>.json = {"<printed>": "<letters of its first line>"}

  python3 _xc/pagemark/expect.py [VOL ...] [--shard i:n]
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'pipeline'))
sys.path.insert(0, os.path.join(ROOT, '_xc', 'reseg'))
sys.path.insert(0, HERE)
import check_page_fidelity as CPF   # noqa: E402
import pline                        # noqa: E402
import folio as FOL                 # noqa: E402

OUT = os.path.join(HERE, 'expect')


def build(vol):
    F = dict(FOL.folio(vol))
    ps = json.load(open('%s/site/%s.json' % (ROOT, vol), encoding='utf-8'))['paragraphs']
    for p in ps:
        if p.get('pdf_page') and isinstance(p.get('printed'), int):
            F[p['pdf_page']] = p['printed']
    out, seen = {}, set()
    for pg, li, ind, txt in pline.stream(vol):
        f = F.get(pg)
        if f is None or f in seen:
            continue
        t = CPF.letters(txt)
        if not t:
            continue
        seen.add(f)
        out[str(f)] = t[:60]
    return out


if __name__ == '__main__':
    a = sys.argv[1:]
    shard = None
    if '--shard' in a:
        i = a.index('--shard'); shard = tuple(int(x) for x in a[i + 1].split(':')); del a[i:i + 2]
    vols = ([x for x in a if not x.startswith('--')] or
            sorted(json.load(open(ROOT + '/site/reader/manifest.json', encoding='utf-8'))['volumes']))
    if shard:
        vols = [v for i, v in enumerate(vols) if i % shard[1] == shard[0]]
    if not os.path.isdir(OUT):
        os.makedirs(OUT)
    for v in vols:
        p = os.path.join(OUT, v + '.json')
        if os.path.exists(p):
            continue
        try:
            d = build(v)
        except Exception as e:
            print('ERR', v, type(e).__name__, e); continue
        json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False)
        print('%-11s %d printed pages' % (v, len(d)))
