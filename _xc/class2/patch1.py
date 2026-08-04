# -*- coding: utf-8 -*-
import io
p='pipeline/check_page_fidelity.py'
s=io.open(p,encoding='utf-8').read()
old = u"""    ends = sorted(l[2] + len(l[3]) for l in lines)
    W = ends[min(len(ends) - 1, int(len(ends) * 0.995))] if ends else 72
    return body, W
"""
new = u'''    ends = sorted(l[2] + len(l[3]) for l in lines)
    W = ends[min(len(ends) - 1, int(len(ends) * 0.995))] if ends else 72
    return body, W


def body_measure(lines, body, W):
    """How far a FULL prose line of this volume actually reaches.

    `W` is the physical width of the set page -- a hard maximum reached by a
    handful of lines.  It is NOT the width a normal line runs to, and taking
    `W - SHORT` for "short" was this instrument's largest error: in 40KhuA21
    W is 78, so `W - 12` is 66, and the MEDIAN body line of that volume ends
    at 67.  Half of its running prose scored as short, and any inset prose
    opener within RUNTOL of a gatha was swept into the gatha.

    Measured instead from the volume's own body-column lines: the 75th
    percentile of their end column, which is 67-72 across the corpus.
    """
    be = sorted(l[2] + len(l[3]) for l in lines if l[2] == body)
    if len(be) < 200:
        return W - 6
    return be[int(len(be) * 0.75)]


def display_column(lines, body, Bm):
    """The column at which THIS volume sets display matter, MEASURED.

    `body + INSET` is right for a prose volume and wrong for a verse one.
    20Khu03 sets its first pada at 3 and its second at 6; 18Khu01 sets 6 and 9;
    40KhuA21 sets 4 and 8.  Fixing the display column at body+8 puts an
    all-verse volume's whole text into the paragraph-opener band, where only
    the hanging-first-pada extension can rescue it -- and that extension is
    precisely the rule that misreads prose openers.  So the column is measured
    and the extension is then allowed to be strict.

    The measurement consults no corpus and no volume name: the leftmost column
    at or right of which the volume's lines are OVERWHELMINGLY short of its own
    body measure.  In a volume of running prose no such column exists short of
    body+INSET -- the opener band there is full-width prose -- and the default
    stands.  In an all-verse volume it is found at once (20Khu03: 2).
    """
    thr = Bm - 8
    n = len(lines)
    for d in range(body + 2, body + INSET):
        a = [l for l in lines if l[2] >= d]
        if len(a) < 0.02 * n:
            break
        if sum(1 for l in a if l[2] + len(l[3]) <= thr) >= 0.90 * len(a):
            return d
    return body + INSET
'''
assert s.count(old)==1, s.count(old)
s=s.replace(old,new)
io.open(p,'w',encoding='utf-8').write(s)
print('ok')
