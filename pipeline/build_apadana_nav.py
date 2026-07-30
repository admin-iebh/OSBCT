#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build the Apadāna nav BY THE EDITION'S OWN DIVISION, across two volumes.

The user chose the edition's division over the physical volumes.  The edition
prints ONE Apadānapāḷi, closing it with "Therāpadānaṁ samattaṁ." and then
"Apadānapāḷi samattā."; the physical split into 20Khu03 / 21Khu04 cuts
Therāpadāna in half at vagga 42/43 and is an artefact of binding, not structure.

    Apadānapāḷi
      Therāpadāna            56 vaggas, numbered CONTINUOUSLY 1-56
        1. Buddhavagga       … 42. Bhaddālivagga     (20Khu03)
        43. Sakiṁsammajjakavagga … 56. Yasavagga     (21Khu04)
          <apadāna leaves>
      Therīapadāna           4 vaggas                (21Khu04)
        <apadāna leaves>

Every VAGGA and every APADĀNA lies wholly inside one volume; only the two upper
grouping rows span volumes, and those are expand-only, exactly as the nikāya
rows above them already are.  So this needs no change to render()'s slicing —
see the note at the end of the module for what that does and does not buy.

21Khu04's other two books (Buddhavaṁsa, Cariyāpiṭaka) get their own nodes.
"""
import json, os, re, shutil, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAV  = os.path.join(ROOT, 'site/reader/nav.json')

# (vol, ord_lo, ord_hi) slices, in printed order, per work
THERA = [('20Khu03', 0, 4461), ('21Khu04', 0, 2072)]
THERI = [('21Khu04', 2072, 3432)]
OTHER = [('Buddhavaṁsapāḷi', '21Khu04', 3432, 4502),
         ('Cariyāpiṭakapāḷi', '21Khu04', 4502, 4858)]

SPEC = {'Therāpadāna': 56, 'Therīapadāna': 4}   # the edition's own vagga counts

# The edition sets TEN apadānas to a vagga.  Two vaggas differ, and the edition
# itself says so: Buddhavagga carries Buddha-apadāna and Paccekabuddha-apadāna
# in front of its ten (12), and Yasavagga's last apadāna is labelled
# "Raṭṭhapālattherassāpadānaṁ EKĀDASAMAṀ" — the eleventh (11).
# This is the check that matters.  A total taken from tradition would have
# passed at 559 while four printed headings were silently missing, because the
# edition numbers four of Buddhavagga's ten as "3-1." … "3-10." and the rest as
# "3. 3." … "3. 8."; only the per-vagga count exposes the gap.
PER_VAGGA = {'Therāpadāna': {'1. Buddhavagga': 12, '56. Yasavagga': 11}}


def sections(vol):
    p = os.path.join(ROOT, 'site/reader/sections', vol + '.json')
    out = []
    for k, arr in json.load(open(p)).items():
        for h in arr:
            out.append((int(k), h['l'], h.get('k')))
    out.sort(key=lambda x: (x[0], ['book', 'vagga', 'sutta', 'vatthu'].index(x[2])
                            if x[2] in ('book', 'vagga', 'sutta', 'vatthu') else 9))
    return out


def vaggas_for(slices):
    """[{label, key, kids:[apadāna leaves]}] over a list of (vol, lo, hi) slices.

    THE LAST VAGGA OF EACH SLICE GETS AN EXPLICIT `end`.  Without it the reader
    gives a final node no upper bound and runs it to the END OF ITS VOLUME, so
    Therāpadāna's 56th vagga swallowed Therīapadāna, Buddhavaṁsa and
    Cariyāpiṭaka — the work did not stop where the edition stops it.  The bound
    is the slice's own `hi`, which comes from the printed book-end colophon.
    """
    out = []
    for vol, lo, hi in slices:
        cur, first = None, len(out)
        for o, label, k in sections(vol):
            if not (lo <= o < hi):
                continue
            key = f'{vol}#{o}'
            if k == 'vagga':
                cur = {'label': label, 'key': key, 'kids': []}
                out.append(cur)
            elif k in ('sutta', 'vatthu') and cur is not None:
                cur['kids'].append({'label': label, 'key': key, 'kids': []})
        if len(out) > first:
            out[-1]['end'] = hi
            # and the last apadāna inside it stops there too
            if out[-1]['kids']:
                out[-1]['kids'][-1]['end'] = hi
    return out


def main():
    thera = vaggas_for(THERA)
    theri = vaggas_for(THERI)
    bad = []
    for name, got in (('Therāpadāna', thera), ('Therīapadāna', theri)):
        if len(got) != SPEC[name]:
            bad.append(f'{name}: {len(got)} vaggas, the edition has {SPEC[name]}')
        nums = [int(m.group(1)) for m in (re.match(r'(\d+)\.', v['label']) for v in got) if m]
        if nums != list(range(1, len(got) + 1)):
            bad.append(f'{name}: vagga numbering is {nums[:5]}…{nums[-3:]}, expected 1-{len(got)} '
                       f'continuous (the edition does NOT renumber at the volume break)')
        exc = PER_VAGGA.get(name, {})
        for v in got:
            want = exc.get(v['label'], 10)
            if len(v['kids']) != want:
                bad.append(f'{name} / {v["label"]}: {len(v["kids"])} apadānas, the edition sets {want}')
    for b in bad:
        print('FAIL:', b)
    if bad:
        sys.exit(1)
    for name, got in (('Therāpadāna', thera), ('Therīapadāna', theri)):
        print('  %-14s %2d vaggas, %4d apadānas' % (name, len(got), sum(len(v['kids']) for v in got)))

    apadana = {
        'vol': '20Khu03', 'work': 'Apadānapāḷi', 'title': 'Apadānapāḷi',
        'first': '20Khu03#0',
        'tree': [
            {'label': 'Therāpadāna',  'key': '20Khu03#0',    'kids': thera},
            # explicit end: Buddhavaṁsa follows in the SAME volume, so this must
            # not run to the volume's end the way a final node otherwise would.
            {'label': 'Therīapadāna', 'key': '21Khu04#2072', 'end': 3432, 'kids': theri},
        ],
    }

    others = []
    for title, vol, lo, hi in OTHER:
        kids = []
        cur = None
        for o, label, k in sections(vol):
            if not (lo <= o < hi):
                continue
            key = f'{vol}#{o}'
            if k in ('book', 'vagga'):
                cur = {'label': label, 'key': key, 'kids': []}
                kids.append(cur)
            elif k in ('sutta', 'vatthu'):
                (cur['kids'] if cur else kids).append({'label': label, 'key': key, 'kids': []})
        if kids:
            kids[-1]['end'] = hi
            if kids[-1]['kids']:
                kids[-1]['kids'][-1]['end'] = hi
        others.append({'vol': vol, 'work': title, 'title': title,
                       'first': f'{vol}#{lo}', 'tree': kids})
        print('  %-14s %d chapters, %d leaves' % (title, len(kids),
                                                  sum(len(x['kids']) for x in kids)))

    nav = json.load(open(NAV))
    canon = next(L for L in nav['layers'] if L['layer'] == 'canon')
    nk = next(n for n in canon['nikayas'] if n['nikaya'] == 'Khuddakanikāya')
    vols = nk['volumes']
    at = next(i for i, v in enumerate(vols) if v['vol'] in ('20Khu03', '21Khu04'))
    keep = [v for v in vols if v['vol'] not in ('20Khu03', '21Khu04')]
    nk['volumes'] = keep[:at] + [apadana] + others + keep[at:]
    shutil.copy(NAV, NAV + '.bakapa')
    json.dump(nav, open(NAV, 'w'), ensure_ascii=False)
    print('nav.json patched: Apadānapāḷi + %d further books (backup nav.json.bakapa)' % len(others))


if __name__ == '__main__':
    main()

# WHAT THIS DOES NOT DO: the two grouping rows (Apadānapāḷi, Therāpadāna) expand
# but do not open a reading pane, because render() slices ONE volume's paragraph
# array.  Reading Therāpadāna end to end as a single scroll — 6,533 paragraphs
# across two volumes — would need render() to take a list of (vol, ord) units
# instead of a slice plus a base offset.  Every vagga and every apadāna opens
# normally.  Saṁyutta already stops at saṁyutta level for the same size reason.
