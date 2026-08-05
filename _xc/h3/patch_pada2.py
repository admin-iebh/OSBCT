# -*- coding: utf-8 -*-
import io
P='pipeline/build_khu_volume.py'
s=io.open(P,encoding='utf-8').read()
OLD_RE = """CAESURA = re.compile(r'\\w[\\u2019\\u201d\\'\"]?[,;] +\\w')
"""
NEW_RE = """CAESURA = re.compile(r'\\w[\\u2019\\u201d\\'\"]?[,;] +\\w')
PADA_END = re.compile(r'[,;][\\u2019\\u201d\\'\"]?\\s*\\d*\\s*$')
"""
assert s.count(OLD_RE)==1
s=s.replace(OLD_RE,NEW_RE)

OLD = """    h = [t for i, t in lines if i == pbody and len(t.split()) >= 3]
    if len(h) < 3:
        return False
    return sum(1 for t in h if CAESURA.search(t)) * 2 >= len(h)
"""
NEW = """    h = [t for i, t in lines if i == pbody and len(t.split()) >= 3]
    if len(h) < 3:
        return False
    # A PADA IS MARKED EITHER WAY, and BOTH have to be counted.  In the eight-
    # syllable metres the caesura falls inside the printed line and is set with
    # a comma (`Majjhe mahapathe nari, turiye naccati nattaki.`); in the
    # eleven-syllable ones each printed line IS one pada and the comma falls at
    # its END (`Panaya passitva satova jhayati,`).  Counting only the internal
    # comma refused 317 repairs on 17 pages of 30KhuA11 alone -- p168's
    # Indavajira stanzas -- which is the whole of the Therigatha shape the
    # reader reported.  A matika entry is marked NEITHER way: it is a closed
    # nominal phrase that ends in a full stop.
    n = sum(1 for t in h if CAESURA.search(t) or PADA_END.search(t.rstrip()))
    # A QUARTER, and the margin is not a tuned one: measured over the pages
    # this decides, a page of padas scores 33-100% and a page of matika 0%.
    # 29Abhi01 p32 (`Niruttipatha dhamma. (1314)`), 26Khu09 p12
    # (`nirodhasamapattiya nanam.`) and 35Abhi07's Yamaka pairs
    # (`Indriyam sotam.`) are all exactly 0.
    return n * 4 >= len(h)
"""
assert s.count(OLD)==1
s=s.replace(OLD,NEW)
io.open(P,'w',encoding='utf-8').write(s)
print('patched pada2')
