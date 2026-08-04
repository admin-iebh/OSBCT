# -*- coding: utf-8 -*-
"""Verify the 75 no-`groups` verse entries AGAINST THE PRINTED PAGE.

For every `before`/`after` item of every entry that carries no `groups` key:

  * is its text on the printed page at all?
  * does it sit where the entry says -- `before` ABOVE the anchor paragraph's
    own printed text, `after` BELOW it?
  * what class does the PAGE set it in -- display block (verse) or prose?

Nothing here consults `check_page_fidelity.py`'s corpus side; the page classes
come from that module's own page-side reader, which reads indent alone.

    python3 _xc/nogroups/verify_page.py --out DIR [--budget SECS]
"""
import json, os, sys, time, collections

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'pipeline'))
sys.path.insert(0, os.path.join(ROOT, '_xc', 'reseg'))
import pline                                    # noqa: E402
from locate import Page, letters                # noqa: E402
import check_page_fidelity as CPF               # noqa: E402


def entries(vol):
    p = '%s/site/reader/verse/%s.json' % (ROOT, vol)
    if not os.path.exists(p):
        return {}
    j = json.load(open(p, encoding='utf-8'))
    return {k: e for k, e in j.items()
            if isinstance(e, dict) and 'groups' not in e}


def items_of(e, role):
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
    st = pline.stream(vol) if hasattr(pline, 'stream') else pline.load(vol)
    pg = Page(st)
    body, W = CPF.page_geometry(st)
    cls, verse, _ = CPF.page_classes(st, body, W)
    paras = json.load(open('%s/site/%s.json' % (ROOT, vol), encoding='utf-8'))['paragraphs']
    out = {'vol': vol, 'entries': []}
    for k in sorted(entries(vol), key=lambda s: int(s)):
        e = entries(vol)[k]
        o = int(k)
        atxt = (paras[o].get('text') or '') if o < len(paras) else ''
        asp = pg.span(atxt)
        # fall back to the first 400 letters of the anchor if the whole is not
        # contiguous on the page (a paragraph may span a dropped heading)
        if asp is None:
            asp = pg.span(atxt[:400])
        rec = {'ord': o, 'anchor_span': asp[:2] if asp else None,
               'anchor_letters': len(letters(atxt)), 'roles': {}}
        for role in ('before', 'after'):
            its = items_of(e, role)
            if not its:
                continue
            r = {'n': len(its), 'found': 0, 'missing': [], 'lines': [],
                 'page_verse': 0, 'page_prose': 0, 'lone': 0,
                 'wrong_side': 0, 'pdf_pages': []}
            # monotone cursor: `before` runs up to the anchor, `after` from it
            cur = 0
            for kind, t in its:
                i = pg.find(t, cur)
                if i < 0:
                    i = pg.find(t, 0)           # allow a restart
                if i < 0:
                    r['missing'].append(t[:70])
                    continue
                r['found'] += 1
                cur = i + len(letters(t))
                ln = pg.line_of(i)
                r['lines'].append(ln)
                r['pdf_pages'].append(st[ln][0])
                if verse[ln]:
                    r['page_verse'] += 1
                elif cls[ln] == 'disp':
                    r['lone'] += 1
                else:
                    r['page_prose'] += 1
                if asp:
                    if role == 'before' and ln > asp[0]:
                        r['wrong_side'] += 1
                    if role == 'after' and ln < asp[1]:
                        r['wrong_side'] += 1
            if r['lines']:
                r['line_lo'], r['line_hi'] = min(r['lines']), max(r['lines'])
                r['pdf_lo'], r['pdf_hi'] = min(r['pdf_pages']), max(r['pdf_pages'])
                r['contiguous'] = (r['line_hi'] - r['line_lo'] + 1 == len(r['lines']))
                r['monotone'] = all(b > a for a, b in zip(r['lines'], r['lines'][1:]))
            del r['lines'], r['pdf_pages']
            rec['roles'][role] = r
        out['entries'].append(rec)
    return out


def main():
    a = sys.argv[1:]
    outd = a[a.index('--out') + 1] if '--out' in a else None
    budget = float(a[a.index('--budget') + 1]) if '--budget' in a else 1e9
    vols = [x for x in a if not x.startswith('--')
            and x not in ([outd] if outd else []) ]
    vols = [v for v in vols if os.path.exists('%s/site/%s.json' % (ROOT, v))]
    if not vols:
        vols = sorted({os.path.basename(f)[:-5]
                       for f in os.listdir('%s/site/reader/verse' % ROOT)
                       if f.endswith('.json')})
        vols = [v for v in vols if entries(v)]
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
