#!/usr/bin/env python3
"""Restructure the Itivuttaka nav node into a nipāta→vagga hierarchy (matching the
PDF table of contents): 4 nipātas, each holding its vaggas (Ekaka 3, Duka 2,
Tika 5, Catukka 0 — its 13 suttas sit directly under the nipāta). Run AFTER
build_khuddaka_nav.py (which produces a flat vagga list for Itivuttaka)."""
import json, os

NAV = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'site', 'reader', 'nav.json')
VOL = '18Khu01'
# nipāta -> (display, first-ord, [(vagga display, first-ord)])
NIPATAS = [
    ('1. Ekakanipāta', 593, [('1. Paṭhamavagga', 593), ('2. Dutiyavagga', 603), ('3. Tatiyavagga', 613)]),
    ('2. Dukanipāta', 620, [('1. Paṭhamavagga', 620), ('2. Dutiyavagga', 630)]),
    ('3. Tikanipāta', 642, [('1. Paṭhamavagga', 642), ('2. Dutiyavagga', 652),
                            ('3. Tatiyavagga', 662), ('4. Catutthavagga', 672), ('5. Pañcamavagga', 682)]),
    ('4. Catukkanipāta', 692, []),   # no sub-vaggas
]

def main():
    nav = json.load(open(NAV))
    kh = next(n for L in nav['layers'] if L['layer'] == 'canon'
              for n in L['nikayas'] if n['nikaya'] == 'Khuddakanikāya')
    it = next(v for v in kh['volumes'] if v['title'] == 'Itivuttakapāḷi')
    subs_by_key = {vg['key']: vg.get('subs', []) for vg in it.get('vaggas', [])}
    nipatas = []
    for disp, fo, vaggas in NIPATAS:
        key = f'{VOL}#{fo}'
        node = {'label': disp, 'key': key}
        if vaggas:
            node['vaggas'] = [{'label': vd, 'key': f'{VOL}#{vo}', 'subs': subs_by_key.get(f'{VOL}#{vo}', [])}
                              for vd, vo in vaggas]
        else:
            node['subs'] = subs_by_key.get(key, [])   # Catukka suttas
        nipatas.append(node)
    it['nipatas'] = nipatas
    it.pop('nipata', None)          # replace the flat-vagga rendering
    json.dump(nav, open(NAV, 'w'), ensure_ascii=False)
    print(f"Itivuttaka nav: {len(nipatas)} nipātas, "
          f"{sum(len(n.get('vaggas', [])) for n in nipatas)} vaggas nested")

if __name__ == '__main__':
    main()
