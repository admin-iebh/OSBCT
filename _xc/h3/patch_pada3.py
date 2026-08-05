# -*- coding: utf-8 -*-
import io
P='pipeline/build_khu_volume.py'
s=io.open(P,encoding='utf-8').read()
OLD = """    n = sum(1 for t in h if CAESURA.search(t) or PADA_END.search(t.rstrip()))
"""
NEW = """    # THE MARGIN NUMBER IS STRIPPED FIRST, and leaving it in was a real fault:
    # 29Abhi01's Tikamatika sets `Kusala dhamma. (363, 985, 1384)`, and the
    # commas INSIDE the parenthesised reference list matched the caesura test,
    # so the gate admitted 118 of that volume's mātikā entries -- the reserved
    # non-gatha class -- while refusing them everywhere the list happened to
    # hold one number.  A caesura is a mark in the TEXT.
    hh = [MARGINREF.sub('', t).rstrip() for t in h]
    n = sum(1 for t in hh if CAESURA.search(t) or PADA_END.search(t))
"""
assert s.count(OLD)==1
s=s.replace(OLD,NEW)
OLD2 = """PADA_END = re.compile(r'[,;][\\u2019\\u201d\\'\"]?\\s*\\d*\\s*$')
"""
NEW2 = """PADA_END = re.compile(r'[,;][\\u2019\\u201d\\'\"]?\\s*\\d*\\s*$')
MARGINREF = re.compile(r'\\s*\\([\\d,\\s.\\u2013-]+\\)\\s*$')
"""
assert s.count(OLD2)==1
s=s.replace(OLD2,NEW2)
io.open(P,'w',encoding='utf-8').write(s)
print('patched pada3')
