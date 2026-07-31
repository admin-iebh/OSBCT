#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Move the footnotes stranded in `site/reader/xrefs/<VOL>.json` into the file
the reader actually loads.

WHAT WAS WRONG.  `rebuild_apparatus.py` diverted a class of footnote — the ones
the edition marks with `*` or `+` rather than a number — into
`site/reader/xrefs/<VOL>.json` as raw strings.  **The reader loads that file
nowhere.**  It has been described in the handoff since 2026-07-30f as "1,298 raw
citation lines loaded by nothing", which undersold it twice over:

  * **1,294 of the 1,298 exist in NO other file.**  Only 4 are duplicated in
    `appk`.  They are not a redundant copy of anything; they are the edition's
    footnotes, in the corpus, on no page of the site.
  * **41 of them are not citations at all** but editorial prose —
    `Iminā lakkhaṇena sakavādīpucchā dassitā.` (32Abhi04, explaining the mātikā
    notation), `Catusaṭṭhimattā imā gāthāyo porāṇatālapaṇṇapotthakesu dissanti…`
    (34KhuA15, on sixty-four verses found in old palm-leaf manuscripts).

18 volumes, worst 24Khu07 (313), 18Khu01 (183), 27Khu10 (163), 28Khu11 (132),
07DiA01 (111).

AND THE GATE COULD NOT SEE IT.  `verify_apparatus.py:stored_notes()` read
`xrefs/<VOL>.json` and counted every line toward "stored", so the printed note
matched something and the volume scored clean while the reader had nothing to
show.  That is fixed in the same change; this script is what makes the fix
survivable, by putting the notes where the count claimed they already were.

ADDITIVE, and it proves it: every existing note keeps its `n`, `text`,
`variants` and `xrefs` unchanged — asserted, not assumed.  New notes are
appended to their own ordinal, carry the edition's own marker (`*`, `+`) as `n`,
and get `xrefs` from `parse_xrefs` like any other.  A line already present in
`appk` is skipped.

  --write   apply (backs each file up to .premerge first)
"""
import json, glob, os, re, shutil, sys, importlib.util as il

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = os.path.join(ROOT, 'site/reader/apparatus')
X = os.path.join(ROOT, 'site/reader/xrefs')
sp = il.spec_from_file_location('ex', os.path.join(ROOT, 'pipeline/extract.py'))
ex = il.module_from_spec(sp); sp.loader.exec_module(ex)

MARK = re.compile(r'^\s*([*+†‡])\s*')


def norm(s):
    return re.sub(r'\s+', ' ', (s or '')).strip()


def skeleton(d):
    """Every pre-existing note, exactly as it was."""
    return {o: [(n.get('n'), n.get('text'), json.dumps(n.get('variants'), sort_keys=True),
                 json.dumps(n.get('xrefs'), sort_keys=True, ensure_ascii=False))
                for n in arr] for o, arr in d.items()}


def run(write=False):
    rows = []
    tot_add = tot_skip = 0
    for xp in sorted(glob.glob(X + '/*.json')):
        vol = os.path.basename(xp)[:-5]
        raw = json.load(open(xp, encoding='utf-8'))
        if not raw:
            continue
        ap = os.path.join(A, vol + '.appk.json')
        if not os.path.exists(ap):
            rows.append((vol, 0, 0, 'NO appk FILE — skipped')); continue
        d = json.load(open(ap, encoding='utf-8'))
        before = skeleton(d)
        have = set()
        for arr in d.values():
            for n in arr:
                have.add(norm(n.get('text')))
        add = skip = 0
        for o, lines in raw.items():
            for l in lines:
                s = norm(l)
                if not s:
                    continue
                if s in have:
                    skip += 1; continue
                m = MARK.match(s)
                marker = m.group(1) if m else '*'
                text = s[m.end():] if m else s
                d.setdefault(o, []).append(
                    {'n': marker, 'text': text, 'variants': [],
                     'xrefs': ex.parse_xrefs(text)})
                add += 1
        # NOTHING that was already there may have moved
        after = skeleton(d)
        for o in before:
            assert after[o][:len(before[o])] == before[o], (vol, o)
        tot_add += add; tot_skip += skip
        rows.append((vol, add, skip, ''))
        if write and add:
            if not os.path.exists(ap + '.premerge'):
                shutil.copy(ap, ap + '.premerge')
            json.dump({k: d[k] for k in sorted(d, key=int)},
                      open(ap, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    return rows, tot_add, tot_skip


if __name__ == '__main__':
    w = '--write' in sys.argv
    rows, a, s = run(w)
    print('%-12s %7s %7s' % ('vol', 'added', 'dup'))
    for v, add, skip, note in sorted(rows, key=lambda r: -r[1]):
        if add or skip or note:
            print('%-12s %7d %7d  %s' % (v, add, skip, note))
    print('\n%d footnote(s) moved into appk, %d already there' % (a, s))
    print('WROTE' if w else 'DRY RUN — pass --write to apply')
