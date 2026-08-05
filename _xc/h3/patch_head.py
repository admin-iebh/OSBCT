# -*- coding: utf-8 -*-
import io
P='pipeline/build_khu_volume.py'
s=io.open(P,encoding='utf-8').read()
OLD = """        c = (re.sub(r'\\s*\\(\\d+\\)\\s*$', '', core)
             if SPEC[VOL].get('margin_verse_numbers') else core)
        return len(c.split()) <= 6 and not c.endswith('.')
"""
NEW = """        # !!! AND THE STRIP IS NOW UNCONDITIONAL, because the margin number is
        # a fact of THIS EDITION'S typography and not a property of one volume.
        # Left per-volume, it let 29Abhi01's Dukamātikā through: the page sets
        # `107. Nirutti dhammā. (1314)` and its pair `Niruttipathā dhammā.
        # (1314)` as a numbered couplet, the pair's second half ends in a full
        # stop, and the margin number hid it -- so the form test claimed 35 of
        # them as SECTION HEADINGS the moment `C2COL` let the page's display
        # column fall.  35 invented suttas in the nav, out of a mātikā list.
        # MEASURED over every shipped side-map that holds headings: exactly
        # FOUR entries anywhere are a full stop hidden by a margin number --
        # 3 in 38Abhi10 (`Alobhaṁ paṭicca adoso amoho. ... (1)`, Paṭṭhāna prose
        # run together) and 1 in 09DiT02 (`Tato Satthā Tathāgato”ti. (7)`, the
        # tail of a quoted gāthā).  Neither is a title.  So the general rule
        # takes four wrong headings and nothing else.
        c = re.sub(r'\\s*\\(\\d+\\)\\s*$', '', core)
        return len(c.split()) <= 6 and not c.endswith('.')
"""
assert s.count(OLD)==1, s.count(OLD)
s=s.replace(OLD,NEW)
io.open(P,'w',encoding='utf-8').write(s)
print('patched head')
