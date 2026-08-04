# -*- coding: utf-8 -*-
import io
p='pipeline/check_page_fidelity.py'
s=io.open(p,encoding='utf-8').read()
old_c = u"NEAR = 3        # a small inset: one leading space -- the paragraph-opener class\n"
new_c = (u"NEAR = 3        # a small inset: one leading space -- the paragraph-opener class\n"
         u"OPEN0 = 2       # left edge of the OPENER BAND.  Not NEAR: 31KhuA12 hangs its\n"
         u"                # numbered first pada at body+2 and sets the second at body+7,\n"
         u"                # so a band starting at body+3 saw the second pada alone, made\n"
         u"                # it a lone display line, and left 144 printed lines unjudged.\n")
assert s.count(old_c)==1
s=s.replace(old_c,new_c)
for a,b in ((u"if disp[i] or not (body + NEAR <= ind[i] < DCOL) or not short_op[i]:",
             u"if disp[i] or not (body + OPEN0 <= ind[i] < DCOL) or not short_op[i]:"),
            (u"        cand = [(body + NEAR <= ind[i] < DCOL) and short_op[i] and not disp[i]",
             u"        cand = [(body + OPEN0 <= ind[i] < DCOL) and short_op[i] and not disp[i]"),
            (u"            if disp[i] or ind[i] >= body + NEAR or not short_op[i]:",
             u"            if disp[i] or ind[i] >= body + OPEN0 or not short_op[i]:")):
    assert s.count(a)==1, a
    s=s.replace(a,b)
io.open(p,'w',encoding='utf-8').write(s)
print('ok')
