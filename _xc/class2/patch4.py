# -*- coding: utf-8 -*-
import io
p='pipeline/check_page_fidelity.py'
s=io.open(p,encoding='utf-8').read()
old = u"""        cand = [(body + NEAR <= ind[i] < DCOL) and short_op[i]
                and not disp[i] and not hang[i] for i in range(n)]"""
new = u"""        # The line kept OUT of the run is the prose LEAD-IN -- the one whose
        # next line is a hanging first pada (`Taṁ sutvā tāpaso nava2 gāthā
        # abhāsi–`, 40KhuA21 p8 indent 4, sitting immediately above the
        # numbered pada also at 4).  Keeping the hanging pada itself out
        # instead was the first attempt and it was wrong: it broke every
        # opener-band gatha whose own last line happened to hang, and cost
        # 40KhuA21 650 page-verse lines.
        cand = [(body + NEAR <= ind[i] < DCOL) and short_op[i] and not disp[i]
                and not (i + 1 < n and pg[i + 1] == pg[i] and hang[i + 1])
                for i in range(n)]"""
assert s.count(old)==1
s=s.replace(old,new)
io.open(p,'w',encoding='utf-8').write(s)
print('ok')
