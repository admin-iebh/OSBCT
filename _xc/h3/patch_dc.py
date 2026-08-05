# -*- coding: utf-8 -*-
import io
P = 'pipeline/check_page_fidelity.py'
s = io.open(P, encoding='utf-8').read()

OLD_TAIL = """    thr = Bm - 8
    n = len(lines)
    for d in range(body + 2, body + INSET):
        a = [l for l in lines if l[2] >= d]
        if len(a) < 0.02 * n:
            break
        if sum(1 for l in a if l[2] + len(l[3]) <= thr) >= 0.90 * len(a):
            return d
    return body + INSET
"""
NEW_TAIL = """    thr = Bm - 8
    n = len(lines)
    for d in range(body + 2, body + INSET):
        a = [l for l in lines if l[2] >= d]
        if len(a) < 0.02 * n:
            break
        if sum(1 for l in a if l[2] + len(l[3]) <= thr) >= 0.90 * len(a):
            return d
    return body + INSET


# PAGEFID_PAGECOL=0 selects the VOLUME-WIDE display column, kept for the same
# reason PAGEFID_SHARP is kept: so the effect of making the column per-page is
# a difference INSIDE one code version.
PAGECOL = os.environ.get('PAGEFID_PAGECOL', '1') != '0'

PGMIN = 4       # a page must set at least this many lines at the candidate
                # column before the page is allowed to name one.  Without it a
                # single centred title on a page of prose names the column: at
                # 30 lines a page, `0.02 * n` is 0.6, so ONE line passed the
                # size test and its own shortness passed the 90% test.
PGDENS = 5.0    # LINES PER INSET LINE.  The gate that separates a page whose
                # inset lines are PARAGRAPH OPENERS from one whose inset lines
                # are PADAS, and it is measured, not named: over the corpus a
                # prose page runs 8.3-10.4 lines per opener-band line and a
                # verse page 1.93.  Nothing here consults a volume name --
                # 18Khu01 sets its padas at one space and is judged by this
                # same measurement as every other volume.


def display_column_pages(lines, body, Bm, DCOL):
    \"\"\"The display column MEASURED PER PRINTED PAGE, never above the volume's.

    One number per volume cannot see a page that sets its gatha at 4 in a
    volume whose column is 8, and that is exactly what 30KhuA11 does.  Its
    p252 prints

        659. “Yathapi bhaddo ajanno, dhure yutto dhurassaho.      <- indent 0
             Mathito atibharena, samyugam nativattati.           <- indent 5

    -- the numbered first pada at the body column and the second hanging at 5,
    ALTERNATING.  R2 wants a RUN of two opener-band lines and never sees one
    because a numbered line sits between every pair; R3 wants the line below to
    be display already, which only R2 could have made it.  Each rule waits for
    the other and 130 printed lines of Therigatha go unread.  With the page's
    own column at 2 the second padas are R0 display on their own geometry, R3
    then admits the numbered first padas, and the block is verse.

    The measurement may only move the column LEFT of the volume's, and only on
    evidence the page itself carries: at least PGMIN lines at the column, at
    least one line in PGDENS of the page (so a page of prose with three inset
    openers cannot name a column), and 90% of them short of the body measure --
    the same test `display_column` makes, on the page instead of the volume.
    \"\"\"
    thr = Bm - 8
    out = {}
    by = collections.defaultdict(list)
    for l in lines:
        by[l[0]].append(l)
    for p, pl in by.items():
        n = len(pl)
        got = DCOL
        for d in range(body + 2, DCOL):
            a = [l for l in pl if l[2] >= d]
            if len(a) < PGMIN or len(a) * PGDENS < n:
                break
            if sum(1 for l in a if l[2] + len(l[3]) <= thr) >= 0.90 * len(a):
                got = d
                break
        out[p] = got
    return out
"""
assert s.count(OLD_TAIL) == 1
s = s.replace(OLD_TAIL, NEW_TAIL)

# --- page_classes: use the per-page column ------------------------------
OLD = """    if Bm is None:
        Bm = body_measure(lines, body, W)
    if DCOL is None:
        DCOL = display_column(lines, body, Bm)
    n = len(lines)
    ind = [l[2] for l in lines]
    end = [l[2] + len(l[3]) for l in lines]
    pg = [l[0] for l in lines]
"""
NEW = """    if Bm is None:
        Bm = body_measure(lines, body, W)
    if DCOL is None:
        DCOL = display_column(lines, body, Bm)
    n = len(lines)
    ind = [l[2] for l in lines]
    end = [l[2] + len(l[3]) for l in lines]
    pg = [l[0] for l in lines]
    if PAGECOL:
        pcol = display_column_pages(lines, body, Bm, DCOL)
        dc = [pcol[pg[i]] for i in range(n)]
    else:
        dc = [DCOL] * n
"""
assert s.count(OLD) == 1
s = s.replace(OLD, NEW)

OLD = """    disp = [((ind[i] >= body + INSET and end[i] <= W - 6)
             or (DCOL <= ind[i] < body + INSET and short_op[i]))
            for i in range(n)]
"""
NEW = """    disp = [((ind[i] >= body + INSET and end[i] <= W - 6)
             or (dc[i] <= ind[i] < body + INSET and short_op[i]))
            for i in range(n)]
"""
assert s.count(OLD) == 1
s = s.replace(OLD, NEW)

OLD = """        cand = [(body + OPEN0 <= ind[i] < DCOL) and short_op[i] and not disp[i]
                for i in range(n)]
"""
NEW = """        cand = [(body + OPEN0 <= ind[i] < dc[i]) and short_op[i] and not disp[i]
                for i in range(n)]
"""
assert s.count(OLD) == 1
s = s.replace(OLD, NEW)

# --- report the per-page column ----------------------------------------
OLD = """               body_col=body, measure=W, body_measure=Bm, display_col=DCOL,
               sharp=bool(SHARP), rules=RULES, corpus_segments=len(segs),"""
NEW = """               body_col=body, measure=W, body_measure=Bm, display_col=DCOL,
               page_col=bool(PAGECOL), pages_lowered=PGLOW.get(vol, 0),
               pages_total=PGTOT.get(vol, 0),
               sharp=bool(SHARP), rules=RULES, corpus_segments=len(segs),"""
assert s.count(OLD) == 1
s = s.replace(OLD, NEW)

# record how many pages named their own column, per volume
OLD = """    if PAGECOL:
        pcol = display_column_pages(lines, body, Bm, DCOL)
        dc = [pcol[pg[i]] for i in range(n)]
    else:
        dc = [DCOL] * n
"""
NEW = """    if PAGECOL:
        pcol = display_column_pages(lines, body, Bm, DCOL)
        dc = [pcol[pg[i]] for i in range(n)]
        PGSTAT[0] = sum(1 for v in pcol.values() if v < DCOL)
        PGSTAT[1] = len(pcol)
    else:
        dc = [DCOL] * n
        PGSTAT[0], PGSTAT[1] = 0, len(set(pg))
"""
assert s.count(OLD) == 1
s = s.replace(OLD, NEW)

OLD = """PAGECOL = os.environ.get('PAGEFID_PAGECOL', '1') != '0'
"""
NEW = """PAGECOL = os.environ.get('PAGEFID_PAGECOL', '1') != '0'

# reporting only: how many of the volume's pages named a column of their own
PGSTAT = [0, 0]
PGLOW, PGTOT = {}, {}
"""
assert s.count(OLD) == 1
s = s.replace(OLD, NEW)

OLD = """    pcls, pverse, lines = page_classes(lines, body, W, Bm, DCOL, control)
"""
NEW = """    pcls, pverse, lines = page_classes(lines, body, W, Bm, DCOL, control)
    PGLOW[vol], PGTOT[vol] = PGSTAT[0], PGSTAT[1]
"""
assert s.count(OLD) == 1
s = s.replace(OLD, NEW)

io.open(P, 'w', encoding='utf-8').write(s)
print('patched')
