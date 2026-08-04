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
        ind = collections.Counter(); vind = collections.Counter(); after = collections.Counter()
        for pg in range(p0, p1 + 1):
            ls = B.join_floating(B.page_lines(pages, pg))
            prev_v = None
            for i, t in ls:
                ind[i] += 1
                if B.VERSE.match(t) and i < 20:
                    vind[i] += 1; prev_v = i
                else:
                    if prev_v is not None:
                        after[(prev_v, i)] += 1
                    prev_v = None
        print(vol, bk[0][:20], 'ALL', sorted(ind.items())[:14])
        print('   vnum indents', sorted(vind.items(), key=lambda x: -x[1])[:6])
        print('   (vnum,next)', sorted(after.items(), key=lambda x: -x[1])[:8])
