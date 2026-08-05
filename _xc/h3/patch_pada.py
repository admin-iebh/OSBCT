# -*- coding: utf-8 -*-
import io
P='pipeline/build_khu_volume.py'
s=io.open(P,encoding='utf-8').read()

OLD = """    if os.environ.get('C2COL', '0') == '1':
        body = body0 if pbody > body0 + 2 else pbody
    else:
        body = pbody if hanging else (body0 if pbody > body0 + 2 else pbody)
    return numc, body, hanging
"""
NEW = """    # APPLIED, AND SEPARATED BY A MEASUREMENT RATHER THAN BY A VOLUME NAME.
    # `hanging` is true of a page of numbered gatha AND of a matika list, and
    # geometry cannot tell them apart -- 29Abhi01 p32 sets `107. Nirutti
    # dhamma. (1314)` at 5 with its pair at 10, which is the same shape as
    # 30KhuA11 p9's `267. "Alankata suvasana,` at 4 with its second pada at 9.
    # WHAT SEPARATES THEM IS THE CAESURA.  A pada carries a comma at the break
    # -- `Majjhe mahapathe nari, turiye naccati nattaki.` -- and a matika entry
    # does not: `Niruttipatha dhamma. (1314)`, `Indriyam sotam.`,
    # `nirodhasamapattiya nanam.`.  This is the same measurement that proved
    # the class-1 lines were gatha at `1757a61a` (129 of 138 carried it), used
    # here on the other side of the glass.
    if os.environ.get('C2COL', '1') == '1' and _pada_page(lines, pbody):
        body = body0 if pbody > body0 + 2 else pbody
    else:
        body = pbody if hanging else (body0 if pbody > body0 + 2 else pbody)
    return numc, body, hanging


CAESURA = re.compile(r'\\w[\\u2019\\u201d\\'\"]?[,;] +\\w')


def _pada_page(lines, pbody):
    \"\"\"Does this page set PADAS at its hanging column, or a MATIKA list?

    Read off the page's own text: a pada is a half-verse and the edition sets
    the caesura with a comma, so a run of padas carries one and a run of
    matika entries does not.  Judged over the page's hanging lines only, and
    refused outright when there are fewer than three of them -- one or two
    short lines are a colophon or a title and decide nothing.

    RESERVED, AND THIS IS WHAT KEEPS IT RESERVED: 35Abhi07's Yamaka matika
    pairs (`Sotam indriyam. . Indriyam sotam.`), 26Khu09's Patisambhida
    matika, and 29Abhi01's Dukamatika are the non-gatha display class the
    reader has not yet ruled on.  None of them carries a caesura, so none of
    them moves.
    \"\"\"
    h = [t for i, t in lines if i == pbody and len(t.split()) >= 3]
    if len(h) < 3:
        return False
    return sum(1 for t in h if CAESURA.search(t)) * 2 >= len(h)
"""
assert s.count(OLD)==1
s=s.replace(OLD,NEW)
io.open(P,'w',encoding='utf-8').write(s)
print('patched pada')
