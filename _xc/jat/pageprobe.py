# -*- coding: utf-8 -*-
"""Does `items_for`'s per-page body column explain classes 1 and 3?

Run the BUILDER's own page reader over each Jātaka volume's verse book and
report, per page: whether the page carries a verse number at all (`vind`), the
body column it would take, and the book's body column as `kat_book_body`
measures it.  Then cross-tabulate against the printed lines the page-fidelity
check flagged.
"""
import sys, os, json, collections
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'pipeline'))
import build_khu_volume as B

def probe(vol):
    B.use(vol)
    pages = B.pdf_pages()
    out = {}
    for bkspec in B.BOOKS:
        title, p0, p1, o0, o1, lastv = bkspec[:6]
        mode = bkspec[6] if len(bkspec) > 6 else 'verse'
        if mode != 'verse':
            continue
        bodybk = B.kat_book_body(pages, p0, p1)
        for pg in range(p0, p1 + 1):
            lines = B.join_floating(B.page_lines(pages, pg))
            if not lines:
                continue
            vind = [i for i, t in lines if B.VERSE.match(t) and i < 20]
            out[pg] = dict(nv=len(vind), body=(min(vind) if vind else None),
                           bookbody=bodybk, n=len(lines))
    return out

def main(vols):
    for vol in vols:
        pp = probe(vol)
        rows = json.load(open('%s/_xc/jat/%s.rows.json' % (ROOT, vol), encoding='utf-8'))['rows']
        c = collections.Counter()
        for r in rows:
            v = r[5]
            if v not in ('PROSE_AS_UDDANA', 'PROSE_AS_VERSE'):
                continue
            p = pp.get(r[0])
            key = 'no-verse-number page' if (p and p['nv'] == 0) else \
                  ('body>=bookbody+3' if p and p['body'] is not None and p['body'] >= p['bookbody'] + 3
                   else 'body ok')
            c[(v, key)] += 1
        nvp = sum(1 for p in pp.values() if p['nv'] == 0)
        print('%-9s pages %4d  no-verse-number pages %4d  bookbody %d' %
              (vol, len(pp), nvp, list(pp.values())[0]['bookbody'] if pp else -1))
        for k in sorted(c):
            print('        %-16s %-22s %5d' % (k[0], k[1], c[k]))

if __name__ == '__main__':
    main(sys.argv[1:])
