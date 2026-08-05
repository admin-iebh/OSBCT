# -*- coding: utf-8 -*-
"""Join the BLOCK MAP to `pline`'s indexing, so the boundary is usable.

The block map is keyed by pdftotext page and bbox line order.  Every instrument
in this project reads `pline.stream()`, whose page numbers count only the pages
`split_page` ACCEPTS and whose lines exclude the running head and the footnote
apparatus.  The two therefore disagree on both axes.

  page axis : rebuilt here exactly as pline._build does it -- run split_page over
              raw_pages and record, for each ACCEPTED page, its raw index.  Not
              inferred from an offset; 07ViT07's would have been wrong.
  line axis : pline's lines are a SUBSEQUENCE of the block map's (the head and
              the footnotes are dropped), so they are aligned in order by
              normalised text, never by position.

Output per volume: a list parallel to `pline.stream(vol)`, each entry
[block_start, block_kind], and an alignment rate.  A volume that does not align
is reported, not defaulted.
"""
import json, os, sys, re, collections

ROOT = os.path.abspath('.')
sys.path.insert(0, os.path.join(ROOT, '_xc', 'reseg'))
sys.path.insert(0, os.path.join(ROOT, '_xc', 'hy1'))
import pline                                                   # noqa: E402
import adjudicate as A                                         # noqa: E402
A.B = '_xc/hy1/blocks2'
OUT = '_xc/hy1/bjoin2'
# DIGITS ARE DROPPED for the alignment key.  A superscript footnote marker has a
# smaller yMin and its own x, so in the bbox word order it lands wherever that x
# falls -- pline reads `viharitukāmo1.` from -layout while the bbox line reads
# `1 Santaṁ … viharitukāmo .`.  Keeping the digit made those two strings differ
# and cost ~8% of the alignment.  check_page_fidelity separates digits for the
# same reason (`digit_only`).
NRM = re.compile(r'[^A-Za-zĀāĪīŪūṀṁṂṃṄṅÑñṬṭḌḍṆṇḶḷ]')
n = lambda s: NRM.sub('', s or '')


def _extract_ns():
    """extract.py with pline's own glyph-errata patch applied to raw_pages.

    Same patch, same assertion, so this reads the identical printed stream pline
    reads -- if extract.py's raw_pages moves, both fail together rather than
    silently diverging."""
    src = open(ROOT + '/pipeline/extract.py', encoding='utf-8').read()
    RAW = """def raw_pages(pdf):
    t=subprocess.run(['pdftotext','-enc','UTF-8','-layout',pdf,'-'],
                     capture_output=True).stdout.decode('utf-8','replace')
    return t.split('\\x0c')"""
    assert src.count(RAW) == 1, 'raw_pages in extract.py has moved'
    GL = RAW.replace("    return t.split('\\x0c')",
                     "    import json as _j, os as _o\n"
                     "    _v = _o.path.basename(pdf)[:-4]\n"
                     "    try:\n"
                     "        _r = _j.load(open(_o.path.join(_o.path.dirname(_o.path.dirname(\n"
                     "            _o.path.abspath(pdf))), 'data', 'glyph_errata.json'), encoding='utf-8'))\n"
                     "    except Exception:\n"
                     "        _r = {'entries': []}\n"
                     "    for _e in _r.get('entries', ()):\n"
                     "        if _e.get('vol') == _v and _e.get('apply_from') and _e.get('apply_to'):\n"
                     "            t = t.replace(_e['apply_from'], _e['apply_to'])\n"
                     "    return t.split('\\x0c')")
    ns = {}
    exec(compile(src.replace(RAW, GL), 'extract_scan', 'exec'), ns)
    return ns


_NS = None


def accepted_pages(vol):
    """[raw pdftotext index] for each page pline ACCEPTS, in pline's own order."""
    global _NS
    if _NS is None:
        _NS = _extract_ns()
    raws = _NS['raw_pages'](pline.pdf_of(vol))
    return [ri for ri, page in enumerate(raws, 1) if _NS['split_page'](page)]


def join(vol):
    st = pline.stream(vol)
    raw_of = accepted_pages(vol)
    try:
        BL = json.load(open('%s/%s.json' % (A.B, vol), encoding='utf-8'))
    except Exception:
        return None
    margin = A.vol_margin(vol, BL)
    kinds = {}
    for pg, p in BL.items():
        starts = {}
        for k, b in A.judge_page(p, margin)[2]:
            for i, l in enumerate(b):
                starts[id(l)] = (1 if i == 0 else 0, k)
        kinds[int(pg)] = [(l[3], starts[id(l)]) for l in p['lines']]
    bypage = collections.defaultdict(list)
    for i, l in enumerate(st):
        bypage[l[0]].append(i)
    res = [None] * len(st)
    ok = miss = 0
    for plpg, idxs in bypage.items():
        raw = raw_of[plpg - 1] if plpg - 1 < len(raw_of) else None
        seq = kinds.get(raw, [])
        j = 0
        for i in idxs:
            t = n(st[i][3])
            hit = None
            for k in range(j, len(seq)):
                if n(seq[k][0]) == t or (t and t in n(seq[k][0])):
                    hit = k
                    break
            if hit is None:
                miss += 1
                res[i] = [0, 'unaligned']
            else:
                ok += 1
                res[i] = list(seq[hit][1])
                j = hit + 1
    return res, ok, miss, len(st)


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    vols = sys.argv[1:] or sorted(f[:-5] for f in os.listdir(A.B))
    tot_ok = tot_miss = 0
    bad = []
    for v in vols:
        if os.path.exists('%s/%s.json' % (OUT, v)):
            continue                      # resumable; delete a file to redo it
        r = join(v)
        if not r:
            continue
        res, ok, miss, nl = r
        json.dump(res, open('%s/%s.json' % (OUT, v), 'w', encoding='utf-8'))
        tot_ok += ok; tot_miss += miss
        rate = 100.0 * ok / max(1, ok + miss)
        if rate < 97.0:
            bad.append((v, rate, miss))
        print('%-10s aligned %6d / %6d  (%5.1f%%)' % (v, ok, ok + miss, rate), flush=True)
    print()
    print('TOTAL aligned %d of %d (%.2f%%)' % (tot_ok, tot_ok + tot_miss,
                                               100.0 * tot_ok / max(1, tot_ok + tot_miss)))
    print('volumes below 97%%: %s' % (bad if bad else 'none'))
