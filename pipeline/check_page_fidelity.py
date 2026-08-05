# -*- coding: utf-8 -*-
"""check_page_fidelity.py -- compare the CORPUS against the PRINTED PAGE.

Every other check in `pipeline/` compares the corpus against itself: links
against links, ordinals against `sutta_n`, letters against letters.  A volume
that has lost structure passes all of them, because what remains is internally
consistent.  This one has an external frame -- the printed line stream of the
PDF -- and asks two questions of every printed body line:

  1. TEXT      -- does the corpus carry this line's letters, in order?
  2. CLASS     -- does the corpus render it as what the page SETS it as?
                  page-verse drawn as prose, and page-prose drawn as verse,
                  are counted SEPARATELY.  A check that sees only one
                  direction is half a check.

EVIDENCE SOURCE.  `_xc/reseg/pline.py`: `pipeline/extract.py`'s own
`raw_pages` + `split_page` over the PDF, with the glyph-errata register
applied.  Running heads and the footnote apparatus are already removed by
`split_page`.  Each item is `[pdf_page, line_index, indent, text]` where
`indent` is the LITERAL leading-space count of the `pdftotext -layout` stream
-- which is how this edition encodes structure.  pdfplumber's `x0` alone does
not show it.

CORPUS SIDE.  Not `site/<VOL>.json` alone: the reader draws a volume from
`site/<VOL>.json` plus six side-maps, and the structural class of a printed
line can live in any of them.  20KhuA01's Ganthārambhakathā verses, for
example, are in NEITHER the paragraph text NOR `verse/` -- they are
`sections/` entries with `k:'gatha'`.  So the corpus stream is assembled the
way `reader2.html` assembles it (`canonFront` + `canonHead` + `block` + `udd`),
and each emitted piece carries the class the reader gives it.

WHAT IT DOES NOT DO.  It fixes nothing and it writes no baseline.  A baseline
recorded over unmeasured faults freezes them in.

Usage:
    python3 pipeline/check_page_fidelity.py <VOL> [<VOL> ...]
    python3 pipeline/check_page_fidelity.py --all
    python3 pipeline/check_page_fidelity.py --all --json out.json
    python3 pipeline/check_page_fidelity.py <VOL> --control <name>
    python3 pipeline/check_page_fidelity.py <VOL> --controls     # run them all
    python3 pipeline/check_page_fidelity.py --all --out DIR --budget 35
        resumable census: one <VOL>.json per volume, volumes already present
        are skipped, and the run stops cleanly after BUDGET seconds.  The
        device bridge kills a backgrounded job between calls, so the census is
        driven by repeating this command until it reports nothing left.
"""
import sys, os, re, json, bisect, collections, time

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
sys.path.insert(0, os.path.join(ROOT, '_xc', 'reseg'))
import pline                                          # noqa: E402

# reseg.py's own alphabet filter, UNCHANGED -- digits included, because a
# footnote marker is part of what the page prints and dropping it here would
# be normalising away the evidence.  Where a miss is caused by a digit alone
# it is recovered and reported under its own name (`digit_only`), never
# silently forgiven.
ALPHA = re.compile(r'[^0-9A-Za-zĀāĪīŪūṀṁṂṃṄṅÑñṬṭḌḍṆṇḶḷ]')
DIGIT = re.compile(r'[0-9]')

# The edition's own word index, by the words it prints at the head of every one
# of its pages.  A volume that holds two works prints ONE INDEX PER WORK, so an
# index can sit in the MIDDLE of the volume -- 22AbhiT01 pdf p224-238 and
# 23AbhiT02 p251-263 are 893 printed lines of index between two ṭīkā, and
# counting them as text the corpus had lost would have overstated the loss by
# a quarter.  Recognised from the PAGE, not from the corpus.
INDEXRE = re.compile(r'Padānukkam|Piṭṭhaṅk|anukkamaṇik|[Ss]ūci|Gāthāsūci')


def letters(s):
    return ALPHA.sub('', s or '')


def jload(p, d=None):
    try:
        return json.load(open(p, encoding='utf-8'))
    except Exception:
        return d


# ---------------------------------------------------------------- corpus side

# classes:  P prose   V verse (display gatha)   H heading   T book title
#           I incipit (the homage)              U uddana / colophon (italic,
#                                                  centred -- neither)
def corpus_stream(vol, control=None):
    """The volume as the READER draws it: ordered (class, text) segments."""
    S = os.path.join(ROOT, 'site')
    c = jload('%s/%s.json' % (S, vol))
    if not c:
        return None, None
    vm = jload('%s/reader/verse/%s.json' % (S, vol), {}) or {}
    hd = jload('%s/reader/hide/%s.json' % (S, vol), {}) or {}
    sec = jload('%s/reader/sections/%s.json' % (S, vol), {}) or {}
    udd = jload('%s/reader/uddana/%s.json' % (S, vol), {}) or {}
    btl = jload('%s/reader/booktitle/%s.json' % (S, vol), {}) or {}
    inc = jload('%s/reader/incipit/%s.json' % (S, vol), {}) or {}
    toc = jload('%s/reader/toc/%s.toc.json' % (S, vol), None)
    hidden = set(str(k) for k in (hd if isinstance(hd, list) else hd.keys()))
    paras = c.get('paragraphs', [])
    heads = c.get('headings', [])

    # --- CONTROL: scramble.  Feed the corpus of a DIFFERENT volume.
    if control == 'wrongvol':
        alt = jload('%s/%s.json' % (S, control_alt_vol(vol)))
        if alt:
            paras = alt.get('paragraphs', [])
            heads = alt.get('headings', [])
            vm, sec, udd, btl, inc, toc, hidden = {}, {}, {}, {}, {}, None, set()

    segs = []                                   # (class, text, ord)

    def add(cls, t, o):
        if t is None:
            return
        for part in str(t).split('\n'):
            if letters(part):
                segs.append((cls, part, o))

    # headings the reader draws where there is no `sections/` file, plus the
    # pdf-toc labels for the 40 canon volumes.  Kept as a per-ordinal map so
    # they are emitted in stream position.
    hmap = collections.defaultdict(list)
    if toc:
        def walk(node):
            for b in node.get('books', []):
                emit(b.get('title'), b.get('key'))
                for ch in b.get('chapters', []):
                    emit(ch.get('label'), ch.get('key'))
                    for s in ch.get('subs', []):
                        emit(s.get('label'), s.get('key'))

        def emit(lab, key):
            if lab and key and '#' in key:
                hmap[int(key.split('#')[1])].append(lab)
        walk(toc)

    # `headings` carries no ordinal, only pdf_page -- interleave by page.
    hi, byord = 0, collections.defaultdict(list)
    for o, p in enumerate(paras):
        pg = p.get('pdf_page')
        while hi < len(heads) and pg is not None and \
                heads[hi].get('pdf_page') is not None and heads[hi]['pdf_page'] <= pg:
            byord[o].append(heads[hi].get('title'))
            hi += 1
    for k in range(hi, len(heads)):
        byord[max(0, len(paras) - 1)].append(heads[k].get('title'))

    def prose_block(x, o):
        if isinstance(x, dict):
            if 'gatha' in x:
                for l in x['gatha']:
                    add('V', l, o)
            elif 't' in x:
                add('P', x['t'], o)
        elif x is not None:
            add('P', x, o)

    # A RESIDUE LINE THAT IS ALREADY A `booktitle/` STACK LINE IS NOT DRAWN.
    # block() drops it: the residue reader attaches an unlocated printed line to
    # whatever paragraph is current, and a book's own title page is exactly what
    # it cannot locate, so six items corpus-wide are a title-stack line sitting
    # on the next ordinal.  Mirror the reader or the model over-counts them.
    _tl = set()
    for _v in btl.values():
        for _l in (_v if isinstance(_v, list) else [_v]):
            _tl.add(letters(str(_l)).lower())

    def keep_frame(x):
        if x is None:
            return None
        if not isinstance(x, list):
            return None if (isinstance(x, str) and letters(x).lower() in _tl) else x
        r = [q for q in x
             if not (isinstance(q, str) and letters(q).lower() in _tl)]
        return r or None

    def blocks(x, o):
        if x is None:
            return
        if isinstance(x, list):
            for b in x:
                prose_block(b, o)
        else:
            prose_block(x, o)

    for o, p in enumerate(paras):
        so = str(o)
        for l in (btl.get(so) if isinstance(btl.get(so), list) else
                  ([btl[so]] if so in btl else [])):
            add('T', l, o)
        if so in inc:
            add('I', inc[so], o)
        if sec:
            for e in sec.get(so, []):
                k = e.get('k')
                add('V' if k == 'gatha' else ('P' if k == 'prose' else 'H'), e.get('l'), o)
        else:
            for l in hmap.get(o, []):
                add('H', l, o)
            for l in byord.get(o, []):
                add('H', l, o)
        e = vm.get(so)
        if e and 'groups' in e:
            if e.get('before') is not None:
                blocks(e.get('before'), o)
            elif e['groups']:
                # THE UDANA FALLBACK, modelled exactly as `reader2.html` runs
                # it: with no `before`, the narrative lead-in is lifted out of
                # the CORPUS paragraph so it stands above the gatha -- and only
                # when the groups do not already carry it.  Without this the
                # whole of the Udāna's prose narrative is invisible to the
                # check and 18Khu01 reads as catastrophically missing.
                m = re.match(r'^([\s\S]*?udāna\S*\s+udānes[iī][–-])', p.get('text', '') or '')
                if m:
                    g_all = letters(' '.join(' '.join(g) for g in e['groups'])).lower()
                    if letters(m.group(1)).lower() not in g_all:
                        add('P', m.group(1), o)
            for g in e['groups']:
                for l in g:
                    add('V', l, o)
            blocks(e.get('after'), o)
            if e.get('tail'):
                add('P', e['tail'], o)
        elif so in hidden:
            pass                                # merge-absorbed into a neighbour
        else:
            # AN ENTRY WITH NO `groups` KEY FRAMES THE PARAGRAPH, IT DOES NOT
            # SUBSTITUTE FOR IT: `before` + the corpus text + `after`.  That is
            # what `build_khu_volume.py` writes such an entry FOR and what
            # `verify_render_vs_pdf.py:render_parts` has always modelled;
            # `reader2.html` gated the whole verse branch on `vmap.groups` and
            # so drew neither, which is how the census of 2026-08-04 found
            # 2,976 printed lines sitting in 30 volumes' side-maps unrendered.
            # The reader was corrected (block(), the `else if(asSpine)` branch)
            # and this model follows it.
            # --- CONTROL: dropframe.  Draw the paragraph WITHOUT its frame,
            # which is exactly what `reader2.html` did before 2026-08-04.  It
            # must put the printed lines back into `absent`; if it does not,
            # this branch is not the thing that carries them.
            if e and control != 'dropframe':
                blocks(keep_frame(e.get('before')), o)
            add('P', p.get('text', ''), o)
            if e and control != 'dropframe':
                blocks(keep_frame(e.get('after')), o)
        for b in udd.get(so, []):
            # !!! A `plain` BLOCK IN THE UDDĀNA MAP IS NOT DRAWN AS AN UDDĀNA,
            # AND THIS MODEL SAID IT WAS.  `uddanaHTML` has two shapes:
            #   b.plain  -> `<div class="head …">` for its head and ONE
            #               `<div class="para … pali">` holding `lines.join(' ')`
            #               — an ordinary body paragraph and an ordinary heading;
            #   otherwise-> `<div class="udd-label">` and `<div class="udd-verse">`,
            #               which is the centred italic uddāna style.
            # Everything here was tagged 'U'.  The `plain` shape is what
            # `kat_build.tail_add` gives PROSE printed after a book's last
            # numbered unit (and what the Jātaka repair, `722d8e6b`, already
            # emitted), so that prose scored as PROSE_AS_UDDANA — class 3 — on
            # volumes where the reader draws it as plain prose all along.
            # MEASURED: correcting it moves 2,262 printed lines out of class 3
            # over the 118 volumes, 1,837 of them in `35KhuA16` alone, WITHOUT
            # any volume data changing.  The reader was right and the instrument
            # was wrong, which is the third time this week.
            if b.get('plain'):
                if b.get('head'):
                    add('H', b['head'], o)
                if b.get('lines'):
                    add('P', ' '.join(b['lines']), o)
                continue
            if b.get('label'):
                add('U', b['label'], o)
            for l in b.get('lines', []):
                add('U', l, o)

    # --- CONTROL: class-blind.  Every segment becomes prose / becomes verse.
    if control == 'allprose':
        segs = [('P', t, o) for (k, t, o) in segs]
    elif control == 'allverse':
        segs = [('V', t, o) for (k, t, o) in segs]
    elif control == 'shiftclass':
        # keep the text, rotate the CLASSES by 7 segments
        ks = [s[0] for s in segs]
        ks = ks[7:] + ks[:7]
        segs = [(ks[i], segs[i][1], segs[i][2]) for i in range(len(segs))]
    return c, segs


def control_alt_vol(vol):
    return '19AnA03' if vol != '19AnA03' else '20KhuA01'


# ------------------------------------------------------------------ page side

def page_geometry(lines):
    """Body column and right measure, MEASURED from the volume's own lines.

    The body column is the LEFTMOST column at which the volume regularly sets
    a line -- the smallest indent carrying at least 5% of its lines -- and NOT
    the modal indent.  In a volume that is almost entirely verse the modal
    indent is the verse's own: 20Khu03 (Therāpadānapāḷi) has its mode at 3,
    which is where its first padas hang, and taking that for the body column
    put the whole Apadāna one class out.

    The measure is the 99.5th percentile of end columns over the whole volume:
    the physical width of the set page, which is a constant of the volume's
    typography.  It must NOT be measured from body-column lines only -- in an
    all-verse volume no line fills the measure and the estimate collapses
    (20Khu03: 58 against a true 70).
    """
    n = len(lines)
    ind = collections.Counter(l[2] for l in lines)
    body = 0
    for k in sorted(ind):
        if ind[k] >= 0.05 * n:
            body = k
            break
    ends = sorted(l[2] + len(l[3]) for l in lines)
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


# PAGEFID_PAGECOL=0 selects the VOLUME-WIDE display column, kept for the same
# reason PAGEFID_SHARP is kept: so the effect of making the column per-page is
# a difference INSIDE one code version.
PAGECOL = os.environ.get('PAGEFID_PAGECOL', '1') != '0'

# reporting only: how many of the volume's pages named a column of their own
PGSTAT = [0, 0]
PGLOW, PGTOT = {}, {}

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
    """The display column MEASURED PER PRINTED PAGE, never above the volume's.

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
    """
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


INSET = 8       # leading spaces that put a line unambiguously OFF the body column
NEAR = 3        # a small inset: one leading space -- the paragraph-opener class
SHORT = 12      # how far short of the measure a small-inset line must stop
RUNTOL = 7      # indent step allowed between two lines of one display block
HANG = 2        # how far a hanging first pada must sit left of its block
OPEN0 = 2       # LEFT EDGE of the opener band.  Not NEAR: 31KhuA12 hangs its
                # numbered first pada at body+2 and sets the second at body+7,
                # so a band starting at body+3 saw the second pada standing
                # alone, called it a lone display line, and left 144 printed
                # lines of Therigatha unjudged.

# A printed number at the head of a line.  It does NOT by itself mean verse --
# this edition numbers its prose paragraphs too, and 32KhuA13's numbered lines
# have a median end column of 66 against its gatha's 53 -- so it is consulted
# only where geometry has already narrowed the question to one line (R3).
VNUM = re.compile(u'^[\u2018\u201c\u2019\u201d(\\[]{0,2}\\d{1,4}\\s*[.\u2013-]')

# PAGEFID_SHARP=0 selects the PRE-SHARPENING page side, kept so that the effect
# of the change can be measured as a difference within ONE code version rather
# than against a remembered number.  PAGEFID_RULES is a bitmask over R2 and R3.
SHARP = os.environ.get('PAGEFID_SHARP', '1') != '0'
RULES = int(os.environ.get('PAGEFID_RULES', '3'))


def page_classes(lines, body, W, Bm=None, DCOL=None, control=None):
    """Per printed line: 'disp' | 'open' | 'body', and verse-block membership.

    Read off the page only.  Nothing here consults the corpus, which is the
    whole point: a class derived from the corpus cannot judge the corpus.

    The edition encodes structure as INDENT -- literal leading spaces in the
    `pdftotext -layout` stream, which is what `extract.py`'s own
    `classify_heading` already reads (`indent < 12` disqualifies a heading):

      * body column, no leading space            -> running prose
      * one leading space (body+3 .. body+7)     -> a paragraph OPENER
      * three leading spaces (>= body+8)         -> DISPLAY: gatha, centred
                                                    titles, colophons

    Consecutive display lines on one page join into a BLOCK while the indent
    step between them stays within RUNTOL.  A block is then extended backwards
    over ONE opener-column line when the block hangs HANG..RUNTOL to its right
    -- that is the numbered first pada, which hangs left by the width of its
    own number: 20Khu03 sets `436. Tāhaṁ dhammaṁ suṇitvāna,` at 5 against its
    second pada at 10, 18Khu01's Maṅgalasutta 5 against 8.  Requiring the step
    to be small is what stops a centred title at 27 from swallowing the prose
    opener at 4 above it.

    A block of two or more lines is page-VERSE.  A display line standing alone
    is a centred title or a one-line colophon and is not judged as either.
    Everything that is not display is page-PROSE, short last lines included:
    at the body column, left-aligned, there is no ambiguity.

    SHARPENED 2026-08-04.  What the page side was getting wrong, measured:

      * "short" was `W - SHORT`, and W is the 99.5th percentile of end columns
        -- a hard maximum, not the width a line runs to.  40KhuA21's W is 78,
        so `W - 12` is 66, and the MEDIAN body line of that volume ends at 67.
        Half its running prose scored as short.  It is now `body_measure() - 8`.
      * the display column was fixed at `body + INSET`.  20Khu03 sets its first
        pada at 3 and its second at 6; 18Khu01 sets 6 and 9; 40KhuA21 sets 4
        and 8.  It is now measured (`display_column`).
      * a single short inset line was display on its own geometry, so every
        one-line paragraph and every prose lead-in that introduces a quotation
        was swept into the gatha printed under it.  Nothing in the opener band
        is display now without a SECOND line agreeing (R2, R3).
    """
    if Bm is None:
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
        PGSTAT[0] = sum(1 for v in pcol.values() if v < DCOL)
        PGSTAT[1] = len(pcol)
    else:
        dc = [DCOL] * n
        PGSTAT[0], PGSTAT[1] = 0, len(set(pg))

    if not SHARP:
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
    #     measured display column, and short of the page, is display.  The
    #     only rule that needs no second line.
    disp = [((ind[i] >= body + INSET and end[i] <= W - 6)
             or (dc[i] <= ind[i] < body + INSET and short_op[i]))
            for i in range(n)]

    # R1 WAS TRIED, MEASURED, AND IS NOT HERE -- recorded because it is the
    #    natural thing to reach for and it is what the old page side did.  It
    #    reads a short line one step left of a display line as the hanging
    #    first pada and admits it.  It ADMITS PROSE LEAD-INS: `Taṁ sutvā
    #    tāpaso nava2 gāthā abhāsi–` (40KhuA21 p8) sits one step left of a
    #    gatha exactly as a hanging pada does.  Measured, it takes 40KhuA21
    #    from class2 57 / class1 49 to 73 / 214, and 18Khu01 from 845 to 1084.
    #    The hanging pada is reached instead by R2, where it is one line of a
    #    run, and by R3, where it carries the verse number at the body column
    #    -- both of which require a second line's agreement.

    # R2  A GATHA SET IN THE OPENER BAND.  40KhuA21 p22 sets pada 1 at the body
    #     column and padas 2-4 at 4; 31KhuA12 p117 sets pada 1 at 2 and pada 2
    #     at 7.  No R0 line is anywhere near either.  A RUN of two or more short
    #     opener-band lines is display; ONE such line standing alone is a
    #     paragraph opener -- which is the distinction the old page side could
    #     not draw, and the whole of its class-2 noise.
    orun = [False] * n
    if RULES & 1:
        # THE BAND IS THE WHOLE OPENER BAND, NOT `< dc[i]`.  With a per-page
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

    # R3  THE NUMBERED PADA AT THE BODY COLUMN.  Where padas 2-4 hang right,
    #     pada 1 carries the verse number and sits at the body column itself.
    #     Admitted only when it CARRIES that number, is short, and the line
    #     below it is already display within the hang -- without the number
    #     this admits every prose lead-in that introduces a quotation
    #     (`gāthamāha–`, 40KhuA21 p8).  It moves no fault count: such a line
    #     differs from the corpus in its digits and is already counted under
    #     `digit_only`.  It is here so that the page MODEL is right.
    if RULES & 2:
        bhang = [False] * n
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
    # CONTROL: slide the page's own verdict three lines out of register with
    # the page.  It must NOT rotate `lines` as well -- that shifts evidence and
    # judgement together and the monotone search simply re-synchronises, which
    # is how this control came out nearly inert the first time it was run.
    if control == 'shiftlines':
        verse = verse[3:] + verse[:3]
        cls = cls[3:] + cls[:3]
    return cls, verse, lines


# ------------------------------------------------------------------- the pass

K = 16          # k-gram index width
CAP = 64        # positions kept per k-gram


class Index(object):
    """A k-gram index over the corpus letter string.

    Not an optimisation for its own sake: without it every miss costs a full
    scan of the volume's letters, and a volume with a thousand missing lines
    takes minutes.  The index makes every lookup -- hit, miss, and
    longest-prefix -- O(1) in the length of the corpus, so the census over 118
    volumes is a few minutes rather than a few hours.  It changes no answer:
    `verify()` asserts index and str.find agree line for line.
    """

    def __init__(self, C):
        self.C = C
        d = {}
        for i in range(len(C) - K + 1):
            g = C[i:i + K]
            v = d.get(g)
            if v is None:
                d[g] = [i]
            elif len(v) < CAP:
                v.append(i)
        self.d = d

    def cands(self, t):
        if len(t) < K:
            return None
        return self.d.get(t[:K])

    def find(self, t, frm=0):
        """First position >= frm where t occurs; -1 if none (>= frm)."""
        if len(t) < K:
            return self.C.find(t, frm)
        v = self.d.get(t[:K])
        if not v:
            return -1
        for p in v:
            if p >= frm and self.C.startswith(t, p):
                return p
        # the cap may have truncated the list -- fall back to the real scan
        if len(v) >= CAP:
            return self.C.find(t, frm)
        return -1

    def findany(self, t):
        if len(t) < K:
            return self.C.find(t)
        v = self.d.get(t[:K])
        if not v:
            return -1
        for p in v:
            if self.C.startswith(t, p):
                return p
        if len(v) >= CAP:
            return self.C.find(t)
        return -1

    def prefix(self, t):
        """Length of the longest prefix of t that occurs anywhere."""
        v = self.cands(t)
        if v is None:
            n = min(len(t), K)
            while n > 0 and self.C.find(t[:n]) < 0:
                n -= 1
            return n
        if not v:
            n = K - 1
            while n > 0 and self.C.find(t[:n]) < 0:
                n -= 1
            return n
        best = K
        for p in v:
            n = 0
            m = min(len(t), len(self.C) - p)
            while n < m and self.C[p + n] == t[n]:
                n += 1
            if n > best:
                best = n
        return best


BACK = 40000            # how far behind the cursor a line may legitimately be


def run(vol, control=None, verbose=False):
    c, segs = corpus_stream(vol, control)
    if c is None:
        return None
    st = pline.stream(vol)
    pgs = [p['pdf_page'] for p in c['paragraphs'] if p.get('pdf_page')] + \
          [h['pdf_page'] for h in c.get('headings', []) if h.get('pdf_page')]
    if not pgs:
        return None
    LO, HI = min(pgs), max(pgs)
    lines = [x for x in st if LO <= x[0] <= HI and letters(x[3])]
    outside = len([x for x in st if not (LO <= x[0] <= HI) and letters(x[3])])
    if not lines:
        return None

    body, W = page_geometry(lines)
    Bm = body_measure(lines, body, W)
    DCOL = display_column(lines, body, Bm)
    pcls, pverse, lines = page_classes(lines, body, W, Bm, DCOL, control)
    PGLOW[vol], PGTOT[vol] = PGSTAT[0], PGSTAT[1]

    buf, spans = [], []
    pos = 0
    for k, t, o in segs:
        s = letters(t)
        spans.append((pos, pos + len(s), k))
        buf.append(s)
        pos += len(s)
    C = ''.join(buf)
    IX = Index(C)
    Cnod = DIGIT.sub('', C)
    IXnod = Index(Cnod)
    starts = [s[0] for s in spans]

    def classes_over(a, b):
        out = set()
        k = max(0, bisect.bisect_right(starts, a) - 1)
        while k < len(spans) and spans[k][0] < b:
            if spans[k][1] > a:
                out.add(spans[k][2])
            k += 1
        return out

    selftest = os.environ.get('SELFTEST') == '1'
    stat = collections.Counter()
    faults = collections.defaultdict(list)
    pgtot, pgabs = collections.Counter(), collections.Counter()
    rows = []
    cur = 0
    for i, l in enumerate(lines):
        pgtot[l[0]] += 1
        t = letters(l[3])
        hit, how = -1, None
        if selftest:
            a, b = IX.find(t, cur), C.find(t, cur)
            assert a == b, (vol, i, a, b, l[3][:60])
        j = IX.find(t, cur)
        if j >= 0:
            hit, how = j, 'ok'
        else:
            j = IX.find(t, max(0, cur - BACK))
            if j >= 0:
                hit, how = j, 'back'
            else:
                j = IX.findany(t)
                if j >= 0:
                    hit, how = j, 'outoforder'
        if hit < 0:
            # digits only?  a footnote marker the corpus placed differently
            td = DIGIT.sub('', t)
            if td and IXnod.findany(td) >= 0:
                stat['digit_only'] += 1
                faults['digit_only'].append(i)
                if verbose:
                    rows.append([l[0], l[2], l[2] + len(l[3]),
                                 'verse' if pverse[i] else 'prose',
                                 '-', 'digit_only', l[3]])
                continue
            # a PREFIX of the line -- the line straddles a corpus boundary,
            # or only part of it survives
            best = IX.prefix(t)
            v = 'partial' if best >= 12 else 'absent'
            pgabs[l[0]] += 1
            if best >= 12:
                stat['partial'] += 1
                faults['partial'].append((i, best, len(t)))
            else:
                stat['absent'] += 1
                faults['absent'].append(i)
            if verbose:
                rows.append([l[0], l[2], l[2] + len(l[3]),
                             'verse' if pverse[i] else 'prose', '-', v, l[3]])
            continue
        stat[how] += 1
        cur = hit + len(t)
        cs = classes_over(hit, hit + len(t))
        pv = pverse[i]
        drawn = 'V' if cs == {'V'} else ('P' if cs == {'P'} else
                                         ('H' if cs == {'H'} else
                                          ('U' if cs == {'U'} else
                                           ('T' if cs == {'T'} else
                                            ('I' if cs == {'I'} else 'mix')))))
        stat['page_verse' if pv else 'page_prose'] += 1
        verdict = how
        if pv:
            if drawn in ('P',):
                stat['VERSE_AS_PROSE'] += 1
                faults['VERSE_AS_PROSE'].append(i)
                verdict = 'VERSE_AS_PROSE'
            elif drawn in ('H', 'T'):
                stat['VERSE_AS_HEADING'] += 1
                faults['VERSE_AS_HEADING'].append(i)
                verdict = 'VERSE_AS_HEADING'
            elif drawn in ('V', 'U', 'I'):
                stat['verse_ok'] += 1
                verdict = 'verse_ok'
            else:
                stat['verse_mixed'] += 1
                verdict = 'verse_mixed'
        else:
            # Every non-display line is page-prose, short last lines included:
            # at the body column, left-aligned, there is no ambiguity.  A
            # DISPLAY line standing alone is NEITHER -- a centred title or a
            # one-line colophon -- and is left unjudged, or every
            # `Hetupaccayavāro.` in the Paṭṭhāna counts as prose the corpus
            # centred: 1,153 such lines in 36Abhi08 alone.
            if pcls[i] != 'disp':
                stat['prose_judged'] += 1
                if drawn == 'V':
                    stat['PROSE_AS_VERSE'] += 1
                    faults['PROSE_AS_VERSE'].append(i)
                    verdict = 'PROSE_AS_VERSE'
                elif drawn == 'U':
                    stat['PROSE_AS_UDDANA'] += 1
                    faults['PROSE_AS_UDDANA'].append(i)
                    verdict = 'PROSE_AS_UDDANA'
                elif drawn in ('P', 'H', 'T', 'I'):
                    stat['prose_ok'] += 1
                    verdict = 'prose_ok'
                else:
                    stat['prose_mixed'] += 1
                    verdict = 'prose_mixed'
            else:
                stat['lone_display'] += 1
                verdict = 'lone_display'
        if verbose:
            rows.append([l[0], l[2], l[2] + len(l[3]),
                         'verse' if pv else ('lone' if pcls[i] == 'disp' else 'prose'),
                         drawn, verdict, l[3]])

    # THE PRINTED BACK MATTER.  Most volumes close with the edition's own word
    # index (`Padānukkamo / Piṭṭhaṅkā`), which the corpus does not carry and is
    # not asked to.  It is not a fault, but it is not nothing either, so it is
    # separated OUT of the fault counts and reported under its own name: the
    # longest run of TRAILING pages on which four fifths of the printed lines
    # are missing.  The same is done at the head for a contents listing.
    # The boundary is chosen as the MAXIMUM-SCORING SUFFIX, each page scoring
    # (missing - half its lines).  A plain backward walk stops at the first
    # well-matched page inside the index (18Khu01's index runs from p477 and a
    # walk stopped at p546); a "longest suffix over 50%" rule does the opposite
    # and swallows clean body pages that the index's own surplus can carry.
    # The maximum-scoring suffix extends only while pages pay their way, so it
    # lands on the first page of the index and stops.  The chosen range is
    # reported (`tail_pages`) so it can be read against the PDF, which is how
    # it was checked: 19AnA03 -> p379, `Saṁvaṇṇitapadānaṁ anukkamaṇikā`.
    pages = sorted(pgtot)
    tot = [pgtot[p] for p in pages]
    ab = [pgabs[p] for p in pages]
    n = len(pages)
    best, bi, run_ = 0.0, n, 0.0
    for i in range(n - 1, -1, -1):
        run_ += ab[i] - 0.5 * tot[i]
        if run_ > best and n - i >= 3:
            best, bi = run_, i
    tail = pages[bi:] if bi < n else []
    best, hj, run_ = 0.0, -1, 0.0
    for i in range(n):
        if tail and pages[i] >= tail[0]:
            break
        run_ += ab[i] - 0.5 * tot[i]
        if run_ > best and i + 1 >= 3:
            best, hj = run_, i
    head = pages[:hj + 1] if hj >= 0 else []
    edge = set(tail) | set(head)
    stat['edge_lines'] = sum(pgtot[p] for p in edge)
    stat['edge_absent'] = sum(pgabs[p] for p in edge)

    # WHERE the corpus loses text, as printed page ranges: contiguous runs of
    # pages, outside the front/back matter, on which half the printed lines are
    # not carried.  A count alone does not tell anyone where to look.
    gaps, cur_ = [], None
    for p in pages:
        if p in edge:
            cur_ = None
            continue
        if pgtot[p] >= 4 and pgabs[p] >= 0.5 * pgtot[p]:
            if cur_ and cur_[1] == p - 1:
                cur_[1] = p
                cur_[2] += pgabs[p]
            else:
                cur_ = [p, p, pgabs[p], 'gap']
                gaps.append(cur_)
        else:
            cur_ = None
    # An interior run that is the edition's own word index is named as such and
    # taken out of the loss, exactly as the tail index is.
    for g in gaps:
        hits = sum(1 for l in lines if g[0] <= l[0] <= g[1] and INDEXRE.search(l[3]))
        if hits >= 3:
            g[3] = 'index'
            stat['index_lines'] += sum(pgtot[p] for p in range(g[0], g[1] + 1))
            stat['index_absent'] += g[2]

    res = dict(vol=vol, control=control, pdf_lo=LO, pdf_hi=HI, gaps=gaps,
               head_pages=[min(head), max(head)] if head else None,
               tail_pages=[min(tail), max(tail)] if tail else None,
               printed_lines=len(lines), lines_out_of_extent=outside,
               body_col=body, measure=W, body_measure=Bm, display_col=DCOL,
               page_col=bool(PAGECOL), pages_lowered=PGLOW.get(vol, 0),
               pages_total=PGTOT.get(vol, 0),
               sharp=bool(SHARP), rules=RULES, corpus_segments=len(segs),
               corpus_letters=len(C), stats=dict(stat))
    if verbose:
        res['rows'] = rows
    res['faults'] = {k: len(v) for k, v in faults.items()}
    return res


def summarise(r):
    s = r['stats']
    carried = s.get('ok', 0) + s.get('back', 0) + s.get('outoforder', 0)
    n = r['printed_lines'] - s.get('edge_lines', 0) - s.get('index_lines', 0)
    miss = (s.get('absent', 0) + s.get('partial', 0)
            - s.get('edge_absent', 0) - s.get('index_absent', 0))
    return ('%-10s body %6d  miss %5d (%5.2f%%)  digit %4d  edge %5d'
            '   V-as-P %5d  V-as-H %4d  P-as-V %5d  P-as-U %4d  pV %5d pP %6d'
            % (r['vol'], n, miss, 100.0 * miss / max(1, n),
               s.get('digit_only', 0),
               s.get('edge_lines', 0) + s.get('index_lines', 0),
               s.get('VERSE_AS_PROSE', 0), s.get('VERSE_AS_HEADING', 0),
               s.get('PROSE_AS_VERSE', 0), s.get('PROSE_AS_UDDANA', 0),
               s.get('page_verse', 0), s.get('page_prose', 0)))


def all_vols():
    out = []
    for d in ('pali-unicode', 'atthakatha-unicode', 'tika-unicode'):
        p = os.path.join(ROOT, d)
        if not os.path.isdir(p):
            continue
        for f in sorted(os.listdir(p)):
            if f.endswith('.pdf'):
                v = f[:-4]
                if os.path.exists(os.path.join(ROOT, 'site', v + '.json')):
                    out.append(v)
    return out


CONTROLS = ('wrongvol', 'allprose', 'allverse', 'shiftclass', 'shiftlines',
            'dropframe')


def main(argv):
    # THE MODE FLAGS ARE READ FIRST AND ECHOED.  A previous harness in this
    # project cleaned sys.argv before reading its mode flag, so all three of
    # its controls silently ran the honest input and all three passed.
    ctl = None
    if '--control' in argv:
        ctl = argv[argv.index('--control') + 1]
    doall = '--all' in argv
    docontrols = '--controls' in argv
    outp = argv[argv.index('--json') + 1] if '--json' in argv else None
    dump = argv[argv.index('--dump') + 1] if '--dump' in argv else None
    outd = argv[argv.index('--out') + 1] if '--out' in argv else None
    budget = float(argv[argv.index('--budget') + 1]) if '--budget' in argv else None
    vols = [a for a in argv[1:] if not a.startswith('--')]
    if outd:
        vols = [v for v in vols if v != outd]
    if budget:
        vols = [v for v in vols if v != argv[argv.index('--budget') + 1]]
    if ctl:
        vols = [v for v in vols if v != ctl]
    if outp:
        vols = [v for v in vols if v != outp]
    if dump:
        vols = [v for v in vols if v != dump]
    if doall:
        vols = all_vols()
    if not vols:
        print(__doc__)
        return 2
    if outd:
        if not os.path.isdir(outd):
            os.makedirs(outd)
        todo = [v for v in vols if not os.path.exists('%s/%s.json' % (outd, v))]
        sys.stderr.write('MODE: control=%s out=%s done=%d todo=%d\n'
                         % (ctl, outd, len(vols) - len(todo), len(todo)))
        vols = todo
    else:
        sys.stderr.write('MODE: control=%s volumes=%d\n' % (ctl, len(vols)))

    t0 = time.time()
    out = []
    for v in vols:
        if budget and time.time() - t0 > budget:
            sys.stderr.write('BUDGET reached, %d volumes left\n'
                             % (len(vols) - len(out)))
            break
        if docontrols:
            # Each control is scored by HOW MANY PRINTED LINES change verdict,
            # not by whether some summary number moved.  A control that fires
            # on nothing is not a control, and it says so here.
            base = run(v, verbose=True)
            bv = [x[5] for x in base['rows']]
            print(summarise(base) + '   [honest]')
            for cn in CONTROLS:
                r = run(v, control=cn, verbose=True)
                rv = [x[5] for x in r['rows']]
                n = sum(1 for a, b in zip(bv, rv) if a != b) + abs(len(bv) - len(rv))
                print(summarise(r) + '   [%s] fired on %d of %d lines%s'
                      % (cn, n, len(bv), '   *** VACUOUS ***' if n == 0 else ''))
            continue
        r = run(v, control=ctl, verbose=bool(dump))
        if r is None:
            sys.stderr.write('skip %s\n' % v)
            continue
        if dump:
            json.dump(r, open('%s/%s.rows.json' % (dump, v), 'w', encoding='utf-8'),
                      ensure_ascii=False)
            r = dict(r)
            r.pop('rows', None)
        out.append(r)
        if outd:
            json.dump(r, open('%s/%s.json' % (outd, v), 'w', encoding='utf-8'),
                      ensure_ascii=False)
        print(summarise(r))
        sys.stdout.flush()
    if outp:
        json.dump(out, open(outp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        sys.stderr.write('wrote %s (%d volumes)\n' % (outp, len(out)))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
