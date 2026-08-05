# -*- coding: utf-8 -*-
"""One volume of the BLOCKBREAK sweep, in its own process.

A SUBPROCESS PER VOLUME on purpose: the builder carries module-level state that
`use()` resets but that a reload does not obviously clear, and 101 volumes of
reload in one interpreter is a contamination risk nobody would see in the
output.  It also means one volume that raises does not end the run.

Writes _xc/hy1/sweep/<VOL>.json and nothing else.  Reads nothing but the PDFs
and blocks3/.  Never touches site/ and never runs with --write.
"""
import sys, os, json, re, importlib, collections

ROOT = os.path.abspath('.')
sys.path.insert(0, os.path.join(ROOT, 'pipeline'))
OUT = '_xc/hy1/sweep'
TERM = ('.', ',', ';', ':', '?', '!', '–', '—', '”', '’', ')', '-')
NRM = re.compile(r'[^0-9A-Za-zĀāĪīŪūṀṁṂṃṄṅÑñṬṭḌḍṆṇḶḷ]')


def build(vol, flag):
    os.environ['BLOCKBREAK'] = flag
    for m in list(sys.modules):
        if m.startswith('build_khu_volume_bb'):
            del sys.modules[m]
    mod = importlib.import_module('build_khu_volume_bb')
    mod.use(vol)
    v, s, u, h, i, r = mod.build()
    return {'verse': v, 'sections': s, 'uddana': u, 'hide': h, 'incipit': i}


def drawn(v):
    out = {}
    for k, e in v.items():
        acc = []

        def w(x):
            if isinstance(x, str):
                acc.append(x)
            elif isinstance(x, dict):
                for y in x.values():
                    w(y)
            elif isinstance(x, list):
                for y in x:
                    w(y)
        for kk in ('before', 'after', 'tail', 'groups'):
            w(e.get(kk))
        out[k] = acc
    return out


def main(vol):
    os.makedirs(OUT, exist_ok=True)
    dst = '%s/%s.json' % (OUT, vol)
    rec = {'vol': vol}
    try:
        A = build(vol, '0')
        B = build(vol, '1')
        da, db = drawn(A['verse']), drawn(B['verse'])
        la = sum(len(x) for x in da.values())
        lb = sum(len(x) for x in db.values())
        new, bad = [], []
        for k in da:
            sa = set(da[k])
            for x in db.get(k, []):
                if x not in sa:
                    new.append(x)
                    if (x or '').rstrip()[-1:] not in TERM:
                        bad.append(x)
        ja = ''.join(''.join(da[k]) for k in sorted(da, key=lambda z: int(z)))
        jb = ''.join(''.join(db[k]) for k in sorted(db, key=lambda z: int(z)))
        rec.update({
            'ok': True,
            'drawn_off': la, 'drawn_on': lb, 'delta': lb - la,
            'ordinals_moved': sum(1 for k in da if da.get(k) != db.get(k)),
            'new': len(new), 'mid_sentence': len(bad),
            'bad_sample': bad[:5],
            'letters_identical': NRM.sub('', ja) == NRM.sub('', jb),
            'maps_identical': {
                n: (json.dumps(A[n], sort_keys=True, ensure_ascii=False) ==
                    json.dumps(B[n], sort_keys=True, ensure_ascii=False))
                for n in ('sections', 'uddana', 'hide', 'incipit')},
        })
    except Exception as e:
        import traceback
        rec.update({'ok': False, 'error': '%s: %s' % (type(e).__name__, e),
                    'trace': traceback.format_exc()[-1200:]})
    json.dump(rec, open(dst, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    if rec.get('ok'):
        flags = []
        if rec['mid_sentence']:
            flags.append('MID-SENTENCE %d' % rec['mid_sentence'])
        if not rec['letters_identical']:
            flags.append('*** LETTERS CHANGED ***')
        for n, s in rec['maps_identical'].items():
            if not s:
                flags.append('*** %s CHANGED ***' % n)
        print('%-10s %6d -> %6d (%+5d)  new %5d  %s'
              % (vol, rec['drawn_off'], rec['drawn_on'], rec['delta'],
                 rec['new'], '  '.join(flags)), flush=True)
    else:
        print('%-10s ERROR %s' % (vol, rec['error']), flush=True)


main(sys.argv[1])
