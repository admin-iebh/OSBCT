# -*- coding: utf-8 -*-
"""Second edit: a display line is not only a deeply-indented one.  A SHORT line
at a SMALL inset is display too -- which is how this edition sets a quoted
gāthā at body+7 -- and that is the test `check_page_fidelity.py` reads off the
page.  Match it, or four-line gāthās at body+7 come out as prose."""
import io
P = '/sessions/rcw-01bcgpjfpcgbdwzs1dqi2qk7/mnt/OSBCT/pipeline/build_khu_volume.py'
s = io.open(P, encoding='utf-8').read()

def sub(old, new):
    global s
    assert s.count(old) == 1, (s.count(old), old[:60])
    s = s.replace(old, new)

sub("""PADAIN  = 8      # display: set this far right of the body column
NEARIN  = 3      # a paragraph opener's inset
CENTIN  = 16     # unambiguously centred -- a colophon or a title
RUNSTEP = 7      # indent step allowed between two lines of one display block""",
    """PADAIN  = 8      # display: set this far right of the body column
NEARIN  = 3      # a paragraph opener's inset -- and, when the line also stops
                 #   SHORT of the measure, the inset of a display line: this
                 #   edition sets many of its quoted gāthās at body+7
SHORTOF = 12     # how far short of the measure such a line must stop
ENDPAD  = 6      # how far short of it a deeply-indented line must stop
CENTIN  = 16     # unambiguously centred -- a colophon or a title
RUNSTEP = 7      # indent step allowed between two lines of one display block""")

sub("""    body0 = kat_book_body(pages, p0, p1)
    prose_col = bool(_vc) and body0 + NEARIN <= _vc.most_common(1)[0][0]""",
    """    body0 = kat_book_body(pages, p0, p1)
    prose_col = bool(_vc) and body0 + NEARIN <= _vc.most_common(1)[0][0]
    # THE MEASURE: the physical width of the set page, as the 99.5th percentile
    # of end columns over the whole book -- the same statistic
    # `check_page_fidelity.py:page_geometry` takes, and for the same reason: a
    # line that stops well short of it is display, however small its inset.
    _ends = sorted(ind + len(t) for pg in range(p0, p1 + 1)
                   for ind, t in page_lines(pages, pg))
    W = _ends[min(len(_ends) - 1, int(len(_ends) * 0.995))] if _ends else 72""")

sub("""            disp = [ind >= body0 + PADAIN for ind, t in lines]""",
    """            strong = [ind >= body0 + PADAIN and ind + len(t) <= W - ENDPAD
                      for ind, t in lines]
            disp = [strong[k] or (ind >= body0 + NEARIN
                                  and ind + len(t) <= W - SHORTOF)
                    for k, (ind, t) in enumerate(lines)]""")

sub("""                elif disp[i] and (
                        (i > 0 and disp[i - 1]
                         and abs(ind - lines[i - 1][0]) <= RUNSTEP)
                        or (i + 1 < len(lines) and disp[i + 1]
                            and abs(lines[i + 1][0] - ind) <= RUNSTEP)
                        or (vopen is not None and vopen <= ind)):""",
    """                elif disp[i] and (
                        (i > 0 and disp[i - 1]
                         and abs(ind - lines[i - 1][0]) <= RUNSTEP)
                        or (i + 1 < len(lines) and disp[i + 1]
                            and abs(lines[i + 1][0] - ind) <= RUNSTEP)
                        or (strong[i] and vopen is not None and vopen <= ind)):""")

io.open(P, 'w', encoding='utf-8').write(s)
print('patch2 applied')
