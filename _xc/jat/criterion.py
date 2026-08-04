import sys, os, collections
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'pipeline'))
import build_khu_volume as B
for vol in sys.argv[1:]:
    B.use(vol); pages = B.pdf_pages()
    for bk in B.BOOKS:
        if (bk[6] if len(bk) > 6 else 'verse') != 'verse':
            continue
        p0, p1 = bk[1], bk[2]
        body0 = B.kat_book_body(pages, p0, p1)
        c = collections.Counter()
        for pg in range(p0, p1 + 1):
            for i, t in B.page_lines(pages, pg):
                if B.VERSE.match(t) and i < 20:
                    c[i] += 1
        vcol = c.most_common(1)[0][0] if c else None
        print('%-9s %-24s body0 %2d vcol %s top %s PROSE_COL %s'
              % (vol, bk[0][:24], body0, vcol, c.most_common(4),
                 bool(c) and body0 + 3 <= vcol))
