# -*- coding: utf-8 -*-
"""Apply the re-segmentation of one or more volumes into site/.

Idempotent: reads the prepared files in _xc/reseg2/ and the .prereseg2 backups,
never its own output.  Backs up every file it touches to <path>.prereseg2
BEFORE writing anything.

    python3 _xc/reseg2/apply2.py <VOL> [<VOL> ...] [--write]
"""
import json, os, re, sys, shutil, collections
R = os.path.abspath('.') + '/'
VOLS = [a for a in sys.argv[1:] if not a.startswith('-')]
W = '--write' in sys.argv
SUF = '.prereseg2'


def J(p):
    return json.load(open(R + p, encoding='utf-8'))


def backup(p):
    if not os.path.exists(R + p):
        return False
    if not os.path.exists(R + p + SUF):
        if W:
            shutil.copy2(R + p, R + p + SUF)
        return True
    return False


def src_of(p):
    """always read the PRE-state, so a re-run is idempotent"""
    return (p + SUF) if os.path.exists(R + p + SUF) else p


def put(p, d, label=''):
    if W:
        json.dump(d, open(R + p, 'w', encoding='utf-8'), ensure_ascii=False)
    print('    %-56s %s %d keys %s'
          % (p, 'wrote' if W else 'would write',
             len(d) if hasattr(d, '__len__') else 0, label))


# ---- collect the file list and back everything up first --------------------
TOUCH = ['site/reader/nav.json']
for V in VOLS:
    TOUCH += ['site/%s.json' % V,
              'site/reader/bold/%s.bold.json' % V,
              'site/reader/verse/%s.json' % V,
              'site/reader/uddana/%s.json' % V,
              'site/reader/hide/%s.json' % V,
              'site/reader/sections/%s.json' % V,
              'site/reader/incipit/%s.json' % V,
              'site/reader/booktitle/%s.json' % V,
              'site/reader/ord/%s.json' % V,
              'site/reader/apparatus/%s.appk.json' % V,
              'site/reader/linksk/%s.rev.json' % V,
              'site/reader/links/%s.rev.json' % V,
              'site/index/%s.idx.json' % V]
INB = collections.defaultdict(list)
for f in sorted(os.listdir(R + 'site/reader/linksk')):
    if not f.endswith('.links.json'):
        continue
    txt = open(R + 'site/reader/linksk/' + f, encoding='utf-8').read()
    for V in VOLS:
        if ('"%s#' % V) in txt:
            INB[f].append(V)
TOUCH += ['site/reader/linksk/' + f for f in INB]
TOUCH += ['site/index/terms.compact.json', 'site/reader/pageindex.json',
          'site/reader/pagespan.json']
made = sum(1 for p in dict.fromkeys(TOUCH) if backup(p))
print('BACKUPS: %d new %s files (%d paths in scope)' % (made, SUF, len(set(TOUCH))))

REMAP = {V: {int(k): v for k, v in J('_xc/reseg2/ord_remap_%s.json' % V).items()}
         for V in VOLS}

for V in VOLS:
    print('== %s' % V)
    remap = REMAP[V]
    res = J('_xc/reseg2/%s.json' % V)
    ids = J('_xc/reseg2/b1/ids_%s.json' % V)['ids']
    assert len(ids) == len(res['paragraphs'])
    for i, p in enumerate(res['paragraphs']):
        p['id'] = ids[i]
        assert p['key'] == '%s#%d' % (V, i)
    assert len(set(p['id'] for p in res['paragraphs'])) == len(ids), 'id collision'
    print('  corpus: %d paragraphs, %d distinct ids' % (len(ids), len(set(ids))))
    if W:
        json.dump(res, open(R + 'site/%s.json' % V, 'w', encoding='utf-8'),
                  ensure_ascii=False)
    else:
        print('    site/%s.json  would write %d paragraphs' % (V, len(ids)))
    for src, dst in [
            ('_xc/reseg2/bold/%s.bold.json' % V,        'site/reader/bold/%s.bold.json' % V),
            ('_xc/reseg2/b2/verse_%s.json' % V,         'site/reader/verse/%s.json' % V),
            ('_xc/reseg2/b2/final_uddana_%s.json' % V,  'site/reader/uddana/%s.json' % V),
            ('_xc/reseg2/b2/final_hide_%s.json' % V,    'site/reader/hide/%s.json' % V),
            ('_xc/reseg2/b2/final_sections_%s.json' % V, 'site/reader/sections/%s.json' % V),
            ('_xc/reseg2/b3/incipit_%s.json' % V,       'site/reader/incipit/%s.json' % V),
            ('_xc/reseg2/b3/booktitle_%s.json' % V,     'site/reader/booktitle/%s.json' % V),
            ('_xc/reseg2/b3/ord_%s.json' % V,           'site/reader/ord/%s.json' % V)]:
        put(dst, J(src))
    # legacy links/<VOL>.rev.json -- read by nothing, kept consistent
    pl = 'site/reader/links/%s.rev.json' % V
    if os.path.exists(R + pl):
        lr = J(src_of(pl))
        put(pl, {str(remap[int(k)]): v for k, v in lr.items()}, '(legacy rev)')

# ---- inbound targets in OTHER volumes' link maps ---------------------------
tot = 0
for f, vs in sorted(INB.items()):
    p = 'site/reader/linksk/' + f
    L = json.load(open(R + src_of(p), encoding='utf-8'))
    n = 0
    for ordk, e in L.items():
        for slot in ('commentary', 'subcommentary'):
            for t in (e.get(slot) or []):
                k = t.get('key') or ''
                V = k.split('#')[0]
                if V in REMAP:
                    o = int(k.split('#')[1])
                    t['key'] = '%s#%d' % (V, REMAP[V][o])
                    n += 1
    tot += n
    if W:
        json.dump(L, open(R + p, 'w', encoding='utf-8'), ensure_ascii=False)
    print('  %-52s %d inbound targets remapped %s' % (p, n, vs))
print('INBOUND TARGETS REMAPPED: %d across %d files' % (tot, len(INB)))

# ---- nav.json: re-key every "<VOL>#<ord>" ---------------------------------
pnav = 'site/reader/nav.json'
raw = open(R + src_of(pnav), encoding='utf-8').read()
cnt = collections.Counter()


def sub(m):
    V, o = m.group(1), int(m.group(2))
    if V not in REMAP:
        return m.group(0)
    cnt[V] += 1
    return '"%s#%d"' % (V, REMAP[V][o])


raw2 = re.sub(r'"(%s)#(\d+)"' % '|'.join(VOLS), sub, raw)
if W:
    open(R + pnav, 'w', encoding='utf-8').write(raw2)
print('NAV: re-keyed %s (total %d)' % (dict(cnt), sum(cnt.values())))
print('DRY RUN -- nothing written' if not W else 'WRITTEN')
