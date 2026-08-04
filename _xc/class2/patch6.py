# -*- coding: utf-8 -*-
import io
p='pipeline/check_page_fidelity.py'
s=io.open(p,encoding='utf-8').read()
a=s.index(u"    # R1  THE HANGING FIRST PADA reaches ONE line left")
b=s.index(u"    cls = ['disp' if disp[i] else")
new = u'''    # R1 WAS TRIED AND IS NOT HERE, and the measurement is recorded because it
    #    is the natural thing to reach for.  It read a line one step left of a
    #    display line as the hanging first pada and admitted it.  Measured, it
    #    ADMITS PROSE LEAD-INS: on 40KhuA21 it takes class 2 from 57 to 73 and
    #    class 1 from 49 to 214, and on 18Khu01 class 2 from 845 to 1084 --
    #    because `Taṁ sutvā tāpaso nava2 gāthā abhāsi–` sits one step left of a
    #    gatha exactly as a hanging pada does.  The hanging pada is instead
    #    reached by R2 (it is one line of an opener-band run) and by R3 (where
    #    it carries the verse number at the body column), both of which need a
    #    second line's agreement before they admit anything.

    # R2  A GATHA SET IN THE OPENER BAND.  40KhuA21 p22 sets pada 1 at the body
    #     column and padas 2-4 at 4; 31KhuA12 p117 sets pada 1 at 2 and pada 2
    #     at 7.  No R0 line is anywhere near either.  A RUN of two or more
    #     short opener-band lines is display; ONE such line alone is a
    #     paragraph opener, which is the whole distinction the old page side
    #     could not draw.
    orun = [False] * n
    if RULES & 1:
        cand = [(body + OPEN0 <= ind[i] < DCOL) and short_op[i] and not disp[i]
                for i in range(n)]
        i = 0
        while i < n:
            if not cand[i]:
                i += 1
                continue
            j = i + 1
            while (j < n and cand[j] and pg[j] == pg[j - 1]
                   and abs(ind[j] - ind[j - 1]) <= RUNTOL):
                j += 1
            if j - i >= 2:
                for k in range(i, j):
                    orun[k] = True
            i = j
    for i in range(n):
        if orun[i]:
            disp[i] = True

    # R3  THE NUMBERED PADA AT THE BODY COLUMN.  Where padas 2-4 hang right
    #     (40KhuA21 p22), pada 1 carries the verse number and sits at the body
    #     column itself.  Admitted only when it CARRIES that number, is short,
    #     and the line below it is already display within the hang -- without
    #     the number this admits every prose lead-in that introduces a
    #     quotation (`gāthamāha–`, p8).  It moves no fault count, because such
    #     a line differs from the corpus in its digits and is already counted
    #     under `digit_only`; it is here so that the page MODEL is right.
    bhang = [False] * n
    if RULES & 2:
        for i in range(n):
            if disp[i] or ind[i] >= body + OPEN0 or not short_op[i]:
                continue
            if not VNUM.match(lines[i][3]):
                continue
            j = i + 1
            if (j < n and disp[j] and pg[j] == pg[i]
                    and HANG <= ind[j] - ind[i] <= RUNTOL):
                bhang[i] = True
    for i in range(n):
        if bhang[i]:
            disp[i] = True

'''
s = s[:a] + new + s[b:]
s = s.replace(u"RULES = int(os.environ.get('PAGEFID_RULES', '7'))",
              u"RULES = int(os.environ.get('PAGEFID_RULES', '3'))")
io.open(p,'w',encoding='utf-8').write(s)
print('ok')
