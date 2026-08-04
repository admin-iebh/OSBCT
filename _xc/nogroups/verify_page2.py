# -*- coding: utf-8 -*-
"""Anchor-relative page verification of the no-`groups` verse entries.

v1 (`verify_page.py`) ran one global cursor per entry, so a line the edition
prints many times (a book title, a repeated gāthā pāda) matched its FIRST
occurrence in the volume rather than the one beside the anchor.  Here the
cursor is anchored: `before` is located BACKWARDS from the anchor's first
printed line, `after` FORWARDS from its last, and an item is accepted only if
it is found within GAP printed lines of where the run has reached.

Verdict per role: `at-position` (every item located in the anchor's own
neighbourhood, in printed order) or `off-position` with the reason.

    python3 _xc/nogroups/verify_page2.py --out DIR [--budget SECS]
"""
import json, os, sys, time

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'pipeline'))
sys.path.insert(0, os.path.join(ROOT, '_xc', 'reseg'))
import pline                                     # noqa: E402
from locate import Page, letters                 # noqa: E402
import check_page_fidelity as CPF                # noqa: E402

GAP = 40        # printed lines the run may skip (headings, colophons, uddāna)


def nogroups(vol):
    p = '%s/site/reader/verse/%s.json' % (ROOT, vol)
    if not os.path.exists(p):
        return {}
    j = json.load(open(p, encoding='utf-8'))
    return {k: e for k, e in j.items()
            if isinstance(e, dict) and 'groups' not in e}


def flat(e, role):
    x = e.get(role)
    if x is None:
        return []
    xs = [x] if isinstance(x, str) else list(x)
    out = []
    for p in xs:
        if isinstance(p, dict) and p.get('gatha'):
            for l in p['gatha']:
                out.append(('gatha', l))
        elif isinstance(p, dict) and p.get('t') is not None:
            out.append(('t', p['t']))
        else:
            out.append(('str', p))
    return out


def run(vol):
    st = pline.stream(vol)
    pg = Page(st)
    body, W = CPF.page_geometry(st)
    cls, verse, _ = CPF.page_classes(st, body, W)
    paras = json.load(open('%s/site/%s.json' % (ROOT, vol), encoding='utf-8'))['paragraphs']
    out = {'vol': vol, 'entries': []}
    ent = nogroups(vol)
    for k in sorted(ent, key=lambda s: int(s)):
        e, o = ent[k], int(k)
        atxt = (paras[o].get('text') or '') if o < len(paras) else ''
        asp = pg.span(atxt) or pg.span(atxt[:400]) or pg.span(atxt[:150])
        rec = {'ord': o, 'anchor': (asp[0], asp[1]) if asp else None,
               'anchor_pdf': (st[asp[0]][0], st[asp[1]][0]) if asp else None,
               'roles': {}}
        for role in ('before', 'after'):
            its = flat(e, role)
            if not its:
                continue
            r = {'n': len(its), 'ok': 0, 'not_on_page': [], 'off_position': [],
                 'pV': 0, 'pP': 0, 'lone': 0, 'lines': []}
            if not asp:
                r['verdict'] = 'anchor-not-located'
                rec['roles'][role] = r
                continue
            if role == 'after':
                cur = asp[1]                     # walk forwards from the anchor end
                seq = its
            else:
                cur = asp[0]                     # walk backwards from the anchor start
                seq = list(reversed(its))
            for kind, t in seq:
                occ, i = [], 0
                L = letters(t)
                if not L:
                    r['ok'] += 1
                    continue
                while True:
                    i = pg.text.find(L, i)
                    if i < 0:
                        break
                    occ.append(pg.line_of(i))
                    i += 1
                if not occ:
                    r['not_on_page'].append(t[:70])
                    continue
                if role == 'after':
                    cand = [x for x in occ if x > cur]
                    pick = min(cand) if cand else None
                else:
                    cand = [x for x in occ if x < cur]
                    pick = max(cand) if cand else None
                if pick is None or abs(pick - cur) > GAP:
                    r['off_position'].append(
                        {'t': t[:70], 'occ_pdf': sorted({st[x][0] for x in occ}),
                         'cursor_pdf': st[cur][0]})
                    continue
                r['ok'] += 1
                r['lines'].append(pick)
                cur = pick
                if verse[pick]:
                    r['pV'] += 1
                elif cls[pick] == 'disp':
                    r['lone'] += 1
                else:
                    r['pP'] += 1
            if r['lines']:
                lo, hi = min(r['lines']), max(r['lines'])
                r['pdf'] = [st[lo][0], st[hi][0]]
                r['span_lines'] = hi - lo + 1
            del r['lines']
            r['verdict'] = ('at-position' if r['ok'] == r['n']
                            else 'PARTIAL' if r['ok'] else 'OFF')
            rec['roles'][role] = r
        out['entries'].append(rec)
    return out


def main():
    a = sys.argv[1:]
    outd = a[a.index('--out') + 1] if '--out' in a else None
    budget = float(a[a.index('--budget') + 1]) if '--budget' in a else 1e9
    skip = set()
    for fl in ('--out', '--budget'):
        if fl in a:
            skip.add(a[a.index(fl) + 1])
    vols = [x for x in a if not x.startswith('--') and x not in skip]
    if not vols:
        vols = sorted(v for v in
                      (f[:-5] for f in os.listdir('%s/site/reader/verse' % ROOT)
                       if f.endswith('.json')) if nogroups(v))
    t0 = time.time()
    for v in vols:
        if outd and os.path.exists('%s/%s.json' % (outd, v)):
            continue
        if time.time() - t0 > budget:
            print('BUDGET'); return
        r = run(v)
        if outd:
            os.makedirs(outd, exist_ok=True)
            json.dump(r, open('%s/%s.json' % (outd, v), 'w', encoding='utf-8'),
                      ensure_ascii=False)
            print('done', v)
        else:
            print(json.dumps(r, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
