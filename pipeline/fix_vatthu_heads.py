#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Reclassify 18Khu01's vatthu-named heads from `vatthu` to `sutta`.

REPORTED BY THE READER, 2026-08-08 and again on return: "in the Dhammapadapāḷi
the names like `1. Cakkhupālattheravatthu` and so on shouldn't be golden colour
like in other places like in its commentary?" — and, on return: "the canon
shows `1. Cakkhupālattheravatthu` in a different color when most of the titles
are golden."

SETTLED AGAINST THE PRINTED PAGE (2026-08-09, pymupdf over the source PDFs),
as the handoff demanded — not by recolouring:

    18Khu01  pdf p.38   `1. Yamakavagga`             12pt centred
                        `1. Cakkhupālattheravatthu`  12pt centred
    21KhuA02 pdf p.9    `1. Yamakavagga`             17pt centred
                        `1. Cakkhupālattheravatthu`  12pt centred

The edition sets the vatthu name IDENTICALLY in both volumes — 12pt, centred,
VZTime — and in the canon it is not even subordinate to the vagga head: the
two are typographically EQUAL.  The muted 13px `vatthu` styling the reader saw
in the canon is therefore not the edition's doing; it is the extraction's.

CENSUS: 983 heads corpus-wide have a label ending in `vatthu`.  676 of them,
in 13 volumes — including six canon volumes — are already kind `sutta` and
draw golden.  The `vatthu` kind occurs in exactly two volumes: 18Khu01 (304,
every one a Dhammapada vatthu title) and 19Khu02 (as part of ~36 sub-series
demotions).

!!! 19Khu02 IS LEFT ALONE.  Its `vatthu`-kind heads are DELIBERATE:
`build_19khu02_nav.py` demotes Guttilavimāna's sub-series titles to the
subordinate class because the reading pane would otherwise flatten a hierarchy
the tree established.  That is a real subordination the edition's own
structure carries.  The Dhammapada titles carry no such subordination on the
printed page, which is the whole point of this script.

THE TEST IS THE NAME PLUS THE KIND: a head is reclassified only where its
label ends in `vatthu` AND its kind is `vatthu`, in the volume named on the
command line.  One volume per run, as `fix_vagga_heads.py` does, and for the
same recorded reason.

Usage:
  python3 pipeline/fix_vatthu_heads.py 18Khu01            # report only
  python3 pipeline/fix_vatthu_heads.py 18Khu01 --apply    # rewrite sections/
  python3 pipeline/fix_vatthu_heads.py --census           # all volumes, no write
"""
import json, re, sys, glob, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECD = os.path.join(ROOT, 'site', 'reader', 'sections')
VATTHU = re.compile(r'vatthu\s*$', re.IGNORECASE)

def fold(s):
    return s.lower().replace('ū', 'u').replace('ā', 'a')

def scan(path):
    d = json.load(open(path, encoding='utf-8'))
    hits = []
    for o, arr in d.items():
        for h in (arr or []):
            if h.get('k') == 'vatthu' and VATTHU.search(fold(h.get('l', ''))):
                hits.append((int(o), h))
    return d, sorted(hits, key=lambda x: x[0])

def census():
    for f in sorted(glob.glob(os.path.join(SECD, '*.json'))):
        vol = os.path.basename(f)[:-5]
        _, hits = scan(f)
        if hits:
            print(f'  {vol}: {len(hits)} head(s) of kind `vatthu` whose label ends in vatthu')

def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    if '--census' in sys.argv:
        census(); return
    if len(args) != 1:
        print(__doc__); sys.exit(2)
    vol = args[0]
    if vol == '19Khu02':
        print('19Khu02 is refused by design: its `vatthu` heads are deliberate '
              'sub-series demotions (see build_19khu02_nav.py).'); sys.exit(1)
    path = os.path.join(SECD, vol + '.json')
    d, hits = scan(path)
    print(f'{vol}: {len(hits)} head(s) to reclassify vatthu -> sutta')
    for o, h in hits[:8]:
        print(f'  ord {o}: {h["l"]}')
    if len(hits) > 8:
        print(f'  … and {len(hits)-8} more')
    if '--apply' not in sys.argv:
        print('report only; nothing written (use --apply)'); return
    for _, h in hits:
        h['k'] = 'sutta'
    json.dump(d, open(path, 'w', encoding='utf-8'), ensure_ascii=False)
    print(f'written: {path}')

if __name__ == '__main__':
    main()
