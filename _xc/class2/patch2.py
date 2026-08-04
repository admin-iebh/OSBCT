# -*- coding: utf-8 -*-
import io
p='pipeline/check_page_fidelity.py'
s=io.open(p,encoding='utf-8').read()

old_sig = u"def page_classes(lines, body, W, control=None):"
new_sig = u"def page_classes(lines, body, W, Bm=None, DCOL=None, control=None):"
assert s.count(old_sig)==1
s=s.replace(old_sig,new_sig)

old = u"""    cls, disp = [], []
    for l in lines:
        ind, end = l[2], l[2] + len(l[3])
        d = ((ind >= body + INSET and end <= W - 6)
             or (ind >= body + NEAR and end <= W - SHORT))
        disp.append(d)
        cls.append('disp' if d else ('open' if ind >= body + NEAR else 'body'))
    verse = [False] * len(lines)
    i = 0
    while i < len(lines):
        if not disp[i]:
            i += 1
            continue
        j = i + 1
        while (j < len(lines) and disp[j] and lines[j][0] == lines[j - 1][0]
               and abs(lines[j][2] - lines[j - 1][2]) <= RUNTOL):
            j += 1
        a = i
        if (i > 0 and not disp[i - 1] and lines[i - 1][0] == lines[i][0]
                and body + NEAR <= lines[i - 1][2]
                and HANG <= lines[i][2] - lines[i - 1][2] <= RUNTOL):
            a = i - 1
        if j - a >= 2:
            for k in range(a, j):
                verse[k] = True
        i = j
"""
new = u'''    if Bm is None:
        Bm = body_measure(lines, body, W)
    if DCOL is None:
        DCOL = display_column(lines, body, Bm)
    cls, disp = [], []
    for l in lines:
        ind, end = l[2], l[2] + len(l[3])
        d = ((ind >= body + INSET and end <= W - 6)
             or (DCOL <= ind < body + INSET and end <= Bm - 8))
        disp.append(d)
        cls.append('disp' if d else ('open' if ind >= body + NEAR else 'body'))
    # THE HANGING FIRST PADA, and nothing else, may reach left out of the
    # display column into the paragraph-opener band.  It hangs because of the
    # width of its own verse number, so the hang is bounded; and the line it
    # hangs onto must be display ON ITS OWN GEOMETRY, never another hang --
    # without that the rule chains, and 18Khu01's `Tenetaṁ vuccati–` at 4
    # walks onto the numbered pada at 6 that itself walked onto 9.
    #
    # The opener band is also held to the BODY MEASURE, not to W - SHORT.  The
    # two together are what stop `Tattha kosikinti ... pati` (40KhuA21 p11,
    # indent 5, ending at 66) from being read as the first pada of the gatha
    # printed above it.
    hang = [False] * len(lines)
    for i, l in enumerate(lines):
        if disp[i] or not (body + NEAR <= l[2] < DCOL):
            continue
        if l[2] + len(l[3]) > Bm - 8:
            continue
        j = i + 1
        if (j < len(lines) and disp[j] and lines[j][0] == l[0]
                and HANG <= lines[j][2] - l[2] <= RUNTOL):
            hang[i] = True
    for i in range(len(lines)):
        if hang[i]:
            disp[i] = True
            cls[i] = 'disp'
    verse = [False] * len(lines)
    i = 0
    while i < len(lines):
        if not disp[i]:
            i += 1
            continue
        j = i + 1
        while (j < len(lines) and disp[j] and lines[j][0] == lines[j - 1][0]
               and abs(lines[j][2] - lines[j - 1][2]) <= RUNTOL):
            j += 1
        if j - i >= 2:
            for k in range(i, j):
                verse[k] = True
        i = j
'''
assert s.count(old)==1
s=s.replace(old,new)

old2 = u"""    body, W = page_geometry(lines)
    pcls, pverse, lines = page_classes(lines, body, W, control)
"""
new2 = u"""    body, W = page_geometry(lines)
    Bm = body_measure(lines, body, W)
    DCOL = display_column(lines, body, Bm)
    pcls, pverse, lines = page_classes(lines, body, W, Bm, DCOL, control)
"""
assert s.count(old2)==1
s=s.replace(old2,new2)

old3 = u"""               body_col=body, measure=W, corpus_segments=len(segs),"""
new3 = u"""               body_col=body, measure=W, body_measure=Bm, display_col=DCOL,
               corpus_segments=len(segs),"""
assert s.count(old3)==1
s=s.replace(old3,new3)
io.open(p,'w',encoding='utf-8').write(s)
print('ok')
