# -*- coding: utf-8 -*-
import io,re
p='pipeline/check_page_fidelity.py'
s=io.open(p,encoding='utf-8').read()
a=s.index(u"    if Bm is None:")
b=s.index(u"    # CONTROL: slide the page's own verdict three lines out of register")
new = u'''    if Bm is None:
        Bm = body_measure(lines, body, W)
    if DCOL is None:
        DCOL = display_column(lines, body, Bm)
    n = len(lines)
    ind = [l[2] for l in lines]
    end = [l[2] + len(l[3]) for l in lines]
    pg = [l[0] for l in lines]
    if not SHARP:
        # THE PRE-SHARPENING PAGE SIDE, kept so that the effect of the change
        # can be measured as a difference in ONE code version rather than
        # against a remembered number.  PAGEFID_SHARP=0 selects it.
        disp = [((ind[i] >= body + INSET and end[i] <= W - 6)
                 or (ind[i] >= body + NEAR and end[i] <= W - SHORT))
                for i in range(n)]
        cls = ['disp' if disp[i] else
               ('open' if ind[i] >= body + NEAR else 'body') for i in range(n)]
        verse = [False] * n
        i = 0
        while i < n:
            if not disp[i]:
                i += 1
                continue
            j = i + 1
            while (j < n and disp[j] and pg[j] == pg[j - 1]
                   and abs(ind[j] - ind[j - 1]) <= RUNTOL):
                j += 1
            a_ = i
            if (i > 0 and not disp[i - 1] and pg[i - 1] == pg[i]
                    and body + NEAR <= ind[i - 1]
                    and HANG <= ind[i] - ind[i - 1] <= RUNTOL):
                a_ = i - 1
            if j - a_ >= 2:
                for k in range(a_, j):
                    verse[k] = True
            i = j
        if control == 'shiftlines':
            verse = verse[3:] + verse[:3]
            cls = cls[3:] + cls[:3]
        return cls, verse, lines

    short_op = [end[i] <= Bm - 8 for i in range(n)]

    # R0  THE DISPLAY COLUMN.  A line set at or right of the volume's own
    #     measured display column, and short of the page, is display.  This is
    #     the only rule that needs no neighbour.
    disp = [((ind[i] >= body + INSET and end[i] <= W - 6)
             or (DCOL <= ind[i] < body + INSET and short_op[i]))
            for i in range(n)]

    # R1  THE HANGING FIRST PADA reaches ONE line left of the display column,
    #     by the width of its own verse number, so the hang is bounded.  The
    #     line it hangs onto must be display by R0 -- never by R1 or R2, or
    #     the rule chains and 18Khu01's `Tenetaṁ vuccati–` at 4 walks onto the
    #     pada at 6 that itself walked onto 9.
    hang = [False] * n
    if RULES & 1:
        for i in range(n):
            if disp[i] or not (body + NEAR <= ind[i] < DCOL) or not short_op[i]:
                continue
            j = i + 1
            if (j < n and disp[j] and pg[j] == pg[i]
                    and HANG <= ind[j] - ind[i] <= RUNTOL):
                hang[i] = True

    # R2  A GATHA SET WHOLLY IN THE OPENER BAND.  40KhuA21 p22 sets pada 1 at
    #     the body column and padas 2-4 at 4; the run at 4 is display and no
    #     R0 line is anywhere near it.  A RUN of two or more short opener-band
    #     lines is display -- one such line alone is a paragraph opener.  A
    #     hanging first pada is excluded from the run, which is what keeps the
    #     prose lead-in `Taṁ sutvā tāpaso nava2 gāthā abhāsi–` (p8, indent 4,
    #     immediately above the numbered pada at 4) out of the gatha below it.
    orun = [False] * n
    if RULES & 2:
        cand = [(body + NEAR <= ind[i] < DCOL) and short_op[i]
                and not disp[i] and not hang[i] for i in range(n)]
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
        if hang[i] or orun[i]:
            disp[i] = True

    # R3  THE NUMBERED PADA AT THE BODY COLUMN.  Where padas 2-4 hang right
    #     (40KhuA21 p22), pada 1 carries the verse number and sits at the body
    #     column itself.  It is admitted only when it CARRIES that number, is
    #     short, and the line below it is already display within the hang --
    #     without the number this admits every prose lead-in that introduces a
    #     quotation (`gāthamāha–`, p8).
    bhang = [False] * n
    if RULES & 4:
        for i in range(n):
            if disp[i] or ind[i] >= body + NEAR or not short_op[i]:
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

    cls = ['disp' if disp[i] else
           ('open' if ind[i] >= body + NEAR else 'body') for i in range(n)]

    verse = [False] * n
    i = 0
    while i < n:
        if not disp[i]:
            i += 1
            continue
        j = i + 1
        while (j < n and disp[j] and pg[j] == pg[j - 1]
               and abs(ind[j] - ind[j - 1]) <= RUNTOL):
            j += 1
        if j - i >= 2:
            for k in range(i, j):
                verse[k] = True
        i = j
'''
s = s[:a] + new + s[b:]

# constants
old_c = u"HANG = 2        # how far a hanging first pada must sit left of its block\n"
new_c = (u"HANG = 2        # how far a hanging first pada must sit left of its block\n"
         u"\n"
         u"# A printed verse number at the head of a line.  It does NOT by itself mean\n"
         u"# verse -- this edition numbers its prose paragraphs too -- so it is used only\n"
         u"# where geometry has already narrowed the question to one line (R3).\n"
         u"VNUM = re.compile(u'^[\\u2018\\u201c\\u2019\\u201d(\\\\[]{0,2}\\\\d{1,4}\\\\s*[.\\u2013-]')\n"
         u"\n"
         u"# PAGEFID_SHARP=0 selects the pre-sharpening page side; PAGEFID_RULES is a\n"
         u"# bitmask over R1/R2/R3 for measuring one rule at a time.\n"
         u"SHARP = os.environ.get('PAGEFID_SHARP', '1') != '0'\n"
         u"RULES = int(os.environ.get('PAGEFID_RULES', '7'))\n")
assert s.count(old_c)==1
s=s.replace(old_c,new_c)
io.open(p,'w',encoding='utf-8').write(s)
print('ok')
