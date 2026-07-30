#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A NAME index — every printed heading, so a sutta can be found by its name.

!!! WHY THIS IS NEEDED.  The text index is built from `paragraphs[].text`, and a
printed HEADING does not live there — it lives in `sections/`.  So section names
were **not searchable at all**: `Oghataraṇasutta`, `Mūlapariyāyasutta`,
`Ovādavagga` and `Maṅgalasuttavaṇṇanā` all returned nothing, and `Maṅgalasutta`
returned only the four volumes that happen to mention the word in running prose.
Measured 2026-07-30j over 20 volumes: of 4,440 printed headings, **209 have even
their own last word anywhere in their paragraph's text and 4,231 do not.**

SOURCES, all of them already gated against the edition:
  * `sections/`  — every printed heading, keyed to volume and ORDINAL
  * `uddana/`    — the headings set after a numbered unit, same keying
  * the corpus's own `book` / `vagga` / `sutta` fields, for structural names the
    volume carries but does not print as a heading at that ordinal

The ordinal is what makes an entry USEFUL: it is exactly what `reader2.html`
now accepts as `#VOL#ORD`, so a name hit opens the section itself.

Output `site/index/names.json`:
    {"vols": [...], "rows": [[labelIdx, volIdx, ord, layerIdx], ...],
     "labels": [...], "layers": [...]}
Labels are interned because a name like `Nidānavaṇṇanā` is printed in dozens of
volumes; interning them takes the file from ~3 MB to well under one.  Matching
is done in the browser by folding each label once at load — 16k strings, which
is far cheaper than shipping an inverted index for them.

Usage: python3 pipeline/build_name_index.py [--write]
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'site', 'index')
LAYERS = ['canon', 'commentary', 'subcommentary']


def rows_for(vol, layer):
    out = []
    sp = os.path.join(ROOT, 'site/reader/sections', vol + '.json')
    up = os.path.join(ROOT, 'site/reader/uddana', vol + '.json')
    hide = {}
    hp = os.path.join(ROOT, 'site/reader/hide', vol + '.json')
    if os.path.exists(hp):
        hide = json.load(open(hp, encoding='utf-8'))
    if os.path.exists(sp):
        for k, es in json.load(open(sp, encoding='utf-8')).items():
            if k in hide:
                continue        # a hidden ordinal draws nothing; a link to it
                                # renders nothing (2026-07-29t)
            for e in es:
                if e.get('k') in ('gatha', 'booktitle'):
                    continue
                out.append((e['l'].strip(), int(k)))
    if os.path.exists(up):
        for k, bs in json.load(open(up, encoding='utf-8')).items():
            if k in hide:
                continue
            for b in bs:
                if b.get('head'):
                    out.append((b['head'].strip(), int(k)))
    # ...and the structural names the corpus carries.  A canon sutta whose
    # heading is printed once, above its first paragraph, is already covered by
    # `sections/`; this adds the names for volumes that carry the field without
    # a printed heading at that ordinal, and is deduped against the above.
    P = json.load(open(os.path.join(ROOT, 'site', vol + '.json'),
                       encoding='utf-8'))['paragraphs']
    seen = {(l, o) for l, o in out}
    firsts = {}
    for i, p in enumerate(P):
        if str(i) in hide:
            continue
        for f in ('sutta', 'vagga', 'book'):
            v = p.get(f)
            if v and v != 'X':
                firsts.setdefault((f, v.strip()), i)
    for (_f, v), i in firsts.items():
        if (v, i) not in seen:
            out.append((v, i))
    # ONE ENTRY PER SECTION, NOT TWO.  `sections/` prints `1. Oghataraṇasutta`
    # while the corpus field carries the bare `Oghataraṇasutta`, both at the
    # same ordinal — the same section named twice.  The PRINTED form wins, so a
    # label is dropped when another label at the same ordinal ends with it.
    import re as _re
    byord = {}
    for lab, o in out:
        byord.setdefault(o, []).append(lab)
    keep = []
    for lab, o in out:
        core = _re.sub(r'^\d+(?:-\d+)?\.\s*', '', lab).strip().lower()
        if any(x != lab and _re.sub(r'^\d+(?:-\d+)?\.\s*', '', x).strip().lower()
               .endswith(core) and len(x) > len(lab) for x in byord[o]):
            continue
        keep.append((lab, o))
    return sorted(set(keep))


def main():
    man = json.load(open(os.path.join(ROOT, 'site/reader/manifest.json'),
                         encoding='utf-8'))['volumes']
    vols = sorted(man)
    labels, lidx, rows = [], {}, []
    for vi, vol in enumerate(vols):
        ly = LAYERS.index(man[vol]['layer'])
        for lab, ordi in rows_for(vol, man[vol]['layer']):
            if not lab:
                continue
            j = lidx.get(lab)
            if j is None:
                j = lidx[lab] = len(labels); labels.append(lab)
            rows.append([j, vi, ordi, ly])
    data = {'vols': vols, 'layers': LAYERS, 'labels': labels, 'rows': rows}
    print('%d volumes | %d name rows | %d distinct labels'
          % (len(vols), len(rows), len(labels)))
    if '--write' in sys.argv:
        p = os.path.join(OUT, 'names.json')
        tmp = p + '.tmp'
        json.dump(data, open(tmp, 'w'), ensure_ascii=False, separators=(',', ':'))
        os.replace(tmp, p)
        print('wrote %s  (%.2f MB)' % (p, os.path.getsize(p) / 1e6))
    else:
        print('DRY RUN — pass --write')


if __name__ == '__main__':
    main()
