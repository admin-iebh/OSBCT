import sys, os, collections
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'pipeline'))
import build_khu_volume as B
lo, hi = int(sys.argv[1]), int(sys.argv[2])
for vol in sys.argv[3:]:
    B.use(vol); pages = B.pdf_pages(); n = 0
    c = collections.Counter()
    for bk in B.BOOKS:
        if (bk[6] if len(bk) > 6 else 'verse') != 'verse':
            continue
        for pg in range(bk[1], bk[2] + 1):
            for i, t in B.join_floating(B.page_lines(pages, pg)):
                if lo <= i <= hi:
                    c[i] += 1
                    if n < 22:
                        print('%-9s p%-4d %2d| %s' % (vol, pg, i, t[:80])); n += 1
    print(vol, 'counts', sorted(c.items()))
