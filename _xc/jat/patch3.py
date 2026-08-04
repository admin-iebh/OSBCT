# -*- coding: utf-8 -*-
"""Third edit: in a book WITH a prose column, a plain colophon does not open an
uddāna tail.

The tail exists for the canon's mnemonic verse, which the page sets at the pāda
indent after a vagga colophon, so the emitter takes "everything in the body
column after a centred line, until the next verse number" into that colophon's
block.  In a commentary that rule swallows the NEXT section's opening gāthā and
its gloss (41KhuA22 ord811: `Mahā-umaṅgakhaṇḍaṁ niṭṭhitaṁ.` followed by six
printed pāda lines and their commentary).  An uddāna LABEL still opens a tail --
that is the case the rule was written for.
"""
import io
P = '/sessions/rcw-01bcgpjfpcgbdwzs1dqi2qk7/mnt/OSBCT/pipeline/build_khu_volume.py'
s = io.open(P, encoding='utf-8').read()

def sub(old, new):
    global s
    assert s.count(old) == 1, (s.count(old), old[:60])
    s = s.replace(old, new)

sub("""        in_tail = False
        items_extra = []""",
    """        in_tail = False
        # Does this book have a prose column?  `items_for` says so by emitting
        # the paragraph kinds at all; nothing is declared per volume.
        _pcol = any(it[0] in ('popen', 'pcont') for it in items)
        items_extra = []""")

sub("""                else:
                    pend_centre.append({'label': None, 'lines': [t], 'app': []})
                    in_tail = True""",
    """                else:
                    pend_centre.append({'label': None, 'lines': [t], 'app': []})
                    in_tail = not _pcol""")

io.open(P, 'w', encoding='utf-8').write(s)
print('patch3 applied')
