# -*- coding: utf-8 -*-
"""Fifth edit: a SHORT line at a small inset only joins a display block when the
block is ALIGNED.

The weak display test (short of the measure, inset >= body+3) is what finds a
gāthā set at body+7.  It also finds the short lines of an indented QUOTED SUTTA
passage, whose long lines stay prose -- and a block that takes every second
line of a paragraph breaks the sentence across two render blocks (36KhuA17
p130's `Kathañca bhikkhave bhikkhu bhojane mattaññū hoti.`).  Pādas of one
gāthā are set at ONE indent; the sutta passage steps 6 -> 10.  So two lines
join a block across a step of up to RUNSTEP only when BOTH are deep-indented;
a weak line joins only what is aligned with it.
"""
import io
P = '/sessions/rcw-01bcgpjfpcgbdwzs1dqi2qk7/mnt/OSBCT/pipeline/build_khu_volume.py'
s = io.open(P, encoding='utf-8').read()
old = """                elif disp[i] and (
                        (i > 0 and disp[i - 1]
                         and abs(ind - lines[i - 1][0]) <= RUNSTEP)
                        or (i + 1 < len(lines) and disp[i + 1]
                            and abs(lines[i + 1][0] - ind) <= RUNSTEP)
                        or (strong[i] and vopen is not None and vopen <= ind)):"""
new = """                elif disp[i] and (
                        (i > 0 and disp[i - 1]
                         and abs(ind - lines[i - 1][0])
                         <= (RUNSTEP if strong[i] and strong[i - 1] else ALIGN))
                        or (i + 1 < len(lines) and disp[i + 1]
                            and abs(lines[i + 1][0] - ind)
                            <= (RUNSTEP if strong[i] and strong[i + 1] else ALIGN))
                        or (strong[i] and vopen is not None and vopen <= ind)):"""
assert s.count(old) == 1
s = s.replace(old, new)
old2 = """RUNSTEP = 7      # indent step allowed between two lines of one display block"""
new2 = """RUNSTEP = 7      # indent step allowed between two DEEP-indented lines of one
                 #   display block
ALIGN   = 2      # ...and between two lines when either is only short-and-inset"""
assert s.count(old2) == 1
s = s.replace(old2, new2)
io.open(P, 'w', encoding='utf-8').write(s)
print('patch5 applied')
