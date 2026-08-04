# -*- coding: utf-8 -*-
"""Apply the prose-column classifier to the verse path.  Exact-string edits,
each asserted, so a silent no-op is impossible."""
import io, sys, os
P = '/sessions/rcw-01bcgpjfpcgbdwzs1dqi2qk7/mnt/OSBCT/pipeline/build_khu_volume.py'
s = io.open(P, encoding='utf-8').read()
n = 0

def sub(old, new, count=1):
    global s, n
    assert s.count(old) == count, (s.count(old), old[:70])
    s = s.replace(old, new)
    n += 1

OLD_HEAD = '''def items_for(pages, p0, p1):
    """('centre',txt,pg) | ('verse',n,txt,pg) | ('pada',txt,pg) | ('prose',txt,pg)"""
    items = []
    for pg in range(p0, p1 + 1):
        lines = join_floating(page_lines(pages, pg))
        if not lines:
            continue
        vind = [i for i, t in lines if VERSE.match(t) and i < 20]
'''

NEW_HEAD = '''# THE VERSE PATH'S COLUMNS.  Same columns the kathā path already reads, and the
# same ones `check_page_fidelity.py` reads off the printed page: the body
# column, one leading space for a paragraph OPENER, three for DISPLAY.
PADAIN  = 8      # display: set this far right of the body column
NEARIN  = 3      # a paragraph opener's inset
CENTIN  = 16     # unambiguously centred -- a colophon or a title
RUNSTEP = 7      # indent step allowed between two lines of one display block


def items_for(pages, p0, p1):
    """('centre',txt,pg) | ('verse',n,txt,pg) | ('pada',txt,pg) | ('prose',txt,pg)
    and, in a book that HAS a prose column, ('popen'|'pcont',txt,pg).

    DOES THIS BOOK HAVE A PROSE COLUMN?  Measured, never declared: the book's
    body column (`kat_book_body`, the kathā path's own measurement) against the
    column at which the book sets its verse NUMBERS.  In the nine canon verse
    books the numbers stand at 3-6 and the body column measures 8-11 -- the
    "body" of such a book IS its pāda column, it has no prose column at all,
    and the branch below must not fire.  In the seven Jātaka commentaries the
    body column is 0 and the numbers stand at 4: running commentary prose at
    the margin, gāthās inset.  The measurement separates 9 books from 7 with
    nothing near the boundary.

    WITHOUT THIS the function had no notion of a body column: it took the
    LEFTMOST VERSE NUMBER ON EACH PAGE for one and called everything within 12
    columns of it a pāda, so the Jātaka commentary's running prose became
    pādas of the gāthā above it (25,783 printed lines corpus-wide, 80% of them
    here); and a page carrying no verse number at all fell into the
    colophon-page branch, where EVERY line became a centred item and was drawn
    in the uddāna style (12,617 lines, 79% of them here).  One missing
    measurement, two branches -- see `_xc/jat/`.
    """
    from collections import Counter
    items = []
    _vc = Counter()
    for pg in range(p0, p1 + 1):
        for ind, t in page_lines(pages, pg):
            if VERSE.match(t) and ind < 20:
                _vc[ind] += 1
    body0 = kat_book_body(pages, p0, p1)
    prose_col = bool(_vc) and body0 + NEARIN <= _vc.most_common(1)[0][0]
    vopen = None            # the indent of the open display block's number
    for pg in range(p0, p1 + 1):
        lines = join_floating(page_lines(pages, pg))
        if not lines:
            continue
        if prose_col:
            # Read off the indent, page by page, with ONE piece of state
            # carried across the page break: a gāthā whose pādas continue onto
            # the next page.
            disp = [ind >= body0 + PADAIN for ind, t in lines]
            for i, (ind, t) in enumerate(lines):
                m = VERSE.match(t)
                if HOMAGE.search(t):
                    items.append(('homage', t, pg)); vopen = None
                elif ind >= body0 + CENTIN:
                    # a colophon or a centred title: NOT judged as prose by the
                    # page-fidelity check either, and left exactly where it is
                    # -- `(Sattamo bhāgo)` and its four siblings live here.
                    items.append(('centre', t, pg)); vopen = None
                elif m and HEADTXT.match(head_body(m.group(2))):
                    items.append(('centre', t, pg)); vopen = None
                elif m:
                    items.append(('verse', int(m.group(1)), m.group(2), pg))
                    vopen = ind
                elif disp[i] and (
                        (i > 0 and disp[i - 1]
                         and abs(ind - lines[i - 1][0]) <= RUNSTEP)
                        or (i + 1 < len(lines) and disp[i + 1]
                            and abs(lines[i + 1][0] - ind) <= RUNSTEP)
                        or (vopen is not None and vopen <= ind)):
                    # a pāda: either one line of a display BLOCK, or set under
                    # a verse number and no further left than it.  A display
                    # line standing ALONE is neither, and falls through to the
                    # prose branch rather than being called verse.
                    items.append(('pada', t, pg))
                else:
                    items.append(('popen' if ind >= body0 + NEARIN else 'pcont',
                                  t, pg))
                    vopen = None
            continue
        vind = [i for i, t in lines if VERSE.match(t) and i < 20]
'''
sub(OLD_HEAD, NEW_HEAD)

# ---- the emitter: the new kinds are prose, and paragraph-aware -------------
sub("""            if kind in ('pada', 'prose', 'centre') and it[1].strip() == title:""",
    """            if kind in ('pada', 'prose', 'popen', 'pcont', 'centre') \\
                    and it[1].strip() == title:""")

sub("""            elif kind in ('pada', 'prose'):
                if not opened:""",
    """            elif kind in ('pada', 'prose', 'popen', 'pcont'):
                if not opened:""")

sub("""                    else:
                        _po = pend_open[-1] if pend_open else None
                        if (_po is not None and _po['k'] == 'prose'
                                and not PROSEOPEN.match(it[1])):
                            _po['l'] = hyjoin(_po['l'], it[1])
                        else:
                            pend_open.append({'l': it[1], 'k': 'prose'})""",
    """                    else:
                        # A CONTINUATION LINE JOINS ITS PARAGRAPH; an OPENER
                        # starts one.  On a book with a prose column the page
                        # says which is which (`pcont`/`popen`); elsewhere the
                        # only prose the path sees is PROSEOPEN's, unchanged.
                        _po = pend_open[-1] if pend_open else None
                        _join = (kind == 'pcont' if kind in ('popen', 'pcont')
                                 else not PROSEOPEN.match(it[1]))
                        if _po is not None and _po['k'] == 'prose' and _join:
                            _po['l'] = hyjoin(_po['l'], it[1])
                        else:
                            pend_open.append({'l': it[1], 'k': 'prose'})""")

sub("""                elif pend_heads:
                    # same precedence as in the centred branch: a heading is open,
                    # so this is its opener and belongs to the heading's own verse,
                    # not to the previous section's closing block
                    pend_before.append(it[1])
                elif in_tail and pend_centre:""",
    """                elif pend_heads:
                    # same precedence as in the centred branch: a heading is open,
                    # so this is its opener and belongs to the heading's own verse,
                    # not to the previous section's closing block
                    if (kind == 'pcont' and pend_before
                            and isinstance(pend_before[-1], str)):
                        pend_before[-1] = hyjoin(pend_before[-1], it[1])
                    else:
                        pend_before.append(it[1])
                elif (in_tail and pend_centre
                      and kind not in ('popen', 'pcont')):""")

sub("""                    prev = cur_after[-1] if cur_after else ''
                    if prev.endswith('-'):
                        cur_after[-1] = hyjoin(prev, it[1])
                    else:
                        cur_after.append(it[1])""",
    """                    prev = cur_after[-1] if cur_after else ''
                    if prev and (prev.endswith('-') or kind == 'pcont'):
                        cur_after[-1] = hyjoin(prev, it[1])
                    else:
                        cur_after.append(it[1])""")

io.open(P, 'w', encoding='utf-8').write(s)
print('edits applied:', n)
