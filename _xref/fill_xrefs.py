"""Fill the `xrefs` field on the notes the READER actually loads.

`pipeline/rebuild_apparatus.py` writes every note it anchors with `'xrefs': []`
hardcoded and diverts the citation lines to `site/reader/xrefs/<VOL>.json` as raw
strings, which nothing in the reader loads.  So in every volume that script
rebuilt, `resolveXref()` is never called and a printed citation renders as dead
text instead of a `->` link.

This pass is ADDITIVE and touches ONE field: for every note in
`apparatus/<VOL>.appk.json` it sets `xrefs = parse_xrefs(note['text'])` using
`pipeline/extract.py`'s own parser — the same function that produced the 27,153
xrefs in the section-keyed `app.json`, verified to reproduce all 66,841 of those
notes EXACTLY before this was written.  No note is added, removed, reordered or
retexted; `n`, `text` and `variants` are untouched, and the check below proves it.

  --write   apply (backs each file up to .prexref first)
"""
import json, glob, os, shutil, sys, importlib.util as il

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = os.path.join(ROOT, 'site/reader/apparatus')
sp = il.spec_from_file_location('ex', os.path.join(ROOT, 'pipeline/extract.py'))
ex = il.module_from_spec(sp); sp.loader.exec_module(ex)

def skeleton(d):
    """Everything except the xrefs field — must be identical before and after."""
    return {o: [(n.get('n'), n.get('text'), json.dumps(n.get('variants'), sort_keys=True))
                for n in arr] for o, arr in d.items()}

def run(write=False):
    rows = []; tot_before = tot_after = 0
    for p in sorted(glob.glob(A + '/*.appk.json')):
        vol = os.path.basename(p)[:-10]
        d = json.load(open(p, encoding='utf-8'))
        before_sk = skeleton(d)
        # COMPARE CONTENT, NOT COUNTS.  This used to gate the write on
        # `after != before`, so a parser change that RE-READ a citation without
        # changing how many there are wrote nothing — e.g. `Sārattha-Tī 3. 345`
        # read as the siglum `Tī` and then correctly as `Sārattha-Tī`: same
        # count, different work, silently not applied (found 2026-07-30i).
        before_x = json.dumps([n.get('xrefs') for arr in d.values() for n in arr],
                              sort_keys=True, ensure_ascii=False)
        before = sum(len(n.get('xrefs') or []) for arr in d.values() for n in arr)
        gained_notes = 0
        for arr in d.values():
            for n in arr:
                new = ex.parse_xrefs(n.get('text', '') or '')
                if new and not (n.get('xrefs') or []): gained_notes += 1
                n['xrefs'] = new
        after = sum(len(n.get('xrefs') or []) for arr in d.values() for n in arr)
        after_x = json.dumps([n.get('xrefs') for arr in d.values() for n in arr],
                             sort_keys=True, ensure_ascii=False)
        assert skeleton(d) == before_sk, vol      # nothing but xrefs may move
        tot_before += before; tot_after += after
        dirty = after_x != before_x
        if dirty:
            rows.append((vol, before, after, gained_notes))
        if write and dirty:
            if not os.path.exists(p + '.prexref'): shutil.copy(p, p + '.prexref')
            json.dump({k: d[k] for k in sorted(d, key=int)},
                      open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    return rows, tot_before, tot_after

if __name__ == '__main__':
    w = '--write' in sys.argv
    rows, b, a = run(w)
    print('volumes changed %d | xrefs %d -> %d  (+%d)' % (len(rows), b, a, a - b))
    print('%-12s %7s %7s %8s' % ('vol', 'before', 'after', 'notes+'))
    for r in sorted(rows, key=lambda r: -(r[2] - r[1]))[:12]:
        print('%-12s %7d %7d %8d' % r)
    print('WROTE' if w else 'DRY RUN — pass --write to apply')
