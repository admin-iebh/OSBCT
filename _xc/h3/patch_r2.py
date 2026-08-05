# -*- coding: utf-8 -*-
import io
P = 'pipeline/check_page_fidelity.py'
s = io.open(P, encoding='utf-8').read()

OLD = """        cand = [(body + OPEN0 <= ind[i] < dc[i]) and short_op[i] and not disp[i]
                for i in range(n)]
"""
NEW = """        # THE BAND IS THE WHOLE OPENER BAND, NOT `< dc[i]`.  With a per-page
        # column the two rules split a single printed block between them: on a
        # page whose column falls to 4, a gatha set at 3 and 5 has its second
        # line taken by R0 and leaves the first standing alone, so a run that
        # WAS two lines becomes two singletons and the block is lost.  A line
        # R0 has already admitted still counts as a member of the run; only
        # the rest need marking.  Making the band independent of the column is
        # also what makes `disp` MONOTONE as the column falls -- lowering it
        # can now only ADD display, never take it away, which is the property
        # that lets a per-page column be trusted.
        cand = [(body + OPEN0 <= ind[i] < body + INSET) and short_op[i]
                for i in range(n)]
"""
assert s.count(OLD) == 1
s = s.replace(OLD, NEW)
io.open(P, 'w', encoding='utf-8').write(s)
print('patched r2')
