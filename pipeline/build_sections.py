#!/usr/bin/env python3
"""Build a precisely-anchored inline-heading side-map per volume, so the reading
pane draws ONE clean heading per section at the exact paragraph — replacing the
old buildOutline path that rendered the raw corpus `headings` list (end-markers,
commentary vatthu titles, and coarse pdf_page anchoring that collapsed several
headings onto one paragraph).

Uses pipeline/anchor_headings.py, which pairs each heading with the paragraph
that immediately follows it in PDF reading order (matched by the paragraph's
opening text — reliable even though the ornamental heading font extracts as
gibberish), and takes the clean title from the corpus `headings` array.

Output: site/reader/sections/<VOL>.json  =  { "<ord>": [ {l: label, k: level} ] }
level = 'book' | 'vagga' | 'sutta'
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anchor_headings as ah

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'site', 'reader', 'sections')

def build_volume(vol):
    pdf = os.path.join(ROOT, 'pali-unicode', vol + '.pdf')
    if not os.path.exists(pdf):
        return None
    r = ah.build(vol, pdf)
    m = {}
    def add(key, label, lv):
        o = key.split('#')[1]
        m.setdefault(o, [])
        if not any(x['l'] == label for x in m[o]):
            m[o].append({'l': label, 'k': lv})
    for b in r['books']:
        if b.get('title'):
            add(b['key'], b['title'], 'book')
        for c in b['chapters']:
            add(c['key'], c['label'], 'vagga')
            for s in c.get('subs', []):
                add(s['key'], s['label'], 'sutta')
    return m

def main(vols):
    os.makedirs(OUT, exist_ok=True)
    for vol in vols:
        m = build_volume(vol)
        if m is None:
            print(f"{vol}: no pdf"); continue
        json.dump(m, open(os.path.join(OUT, vol + '.json'), 'w'), ensure_ascii=False)
        print(f"{vol}: {sum(len(v) for v in m.values())} inline headings over {len(m)} anchors")

if __name__ == '__main__':
    if sys.argv[1:]:
        main(sys.argv[1:])
    else:
        man = json.load(open(os.path.join(ROOT, 'site', 'reader', 'manifest.json')))['volumes']
        main(sorted(c for c, mm in man.items() if mm['layer'] == 'canon'))
