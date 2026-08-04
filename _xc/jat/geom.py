# -*- coding: utf-8 -*-
"""The geometry of every VERSE-mode book, measured with the builder's own reader."""
import sys, os, collections
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'pipeline'))
import build_khu_volume as B

def main(vols):
    for vol in vols:
        B.use(vol)
        pages = B.pdf_pages()
        for bi, bk in enumerate(B.BOOKS):
            title, p0, p1 = bk[0], bk[1], bk[2]
            mode = bk[6] if len(bk) > 6 else 'verse'
            if mode != 'verse':
                continue
            body0 = B.kat_book_body(pages, p0, p1)
            ind = collections.Counter()
            nverse = 0
            for pg in range(p0, p1 + 1):
                for i, t in B.page_lines(pages, pg):
                    ind[i] += 1
                    if B.VERSE.match(t) and i < 20:
                        nverse += 1
            n = sum(ind.values()) or 1
            at = sum(v for k, v in ind.items() if k <= body0 + 2)
            near = sum(v for k, v in ind.items() if body0 + 3 <= k <= body0 + 7)
            far = sum(v for k, v in ind.items() if k >= body0 + 8)
            print('%-9s bk%d %-34s pp%4d-%4d  lines %6d  body0 %2d  '
                  'at-body %5.1f%%  +3..7 %5.1f%%  >=+8 %5.1f%%  numbered %5.1f%%'
                  % (vol, bi, title[:34], p0, p1, n, body0,
                     100.0*at/n, 100.0*near/n, 100.0*far/n, 100.0*nverse/n))
            sys.stdout.flush()

if __name__ == '__main__':
    main(sys.argv[1:])
