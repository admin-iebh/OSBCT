#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Does a cross-layer link point at the paragraph it says it points at?

WHY THIS EXISTS.  User-reported 2026-08-02: clicking **A** on the Aratisutta
landed on Pacchāsamaṇasuttavaṇṇanā and the title went blank.  The link record
read

    {"key": "19AnA03#86", "state": "covered", "n": 113}

and `19AnA03#86` is paragraph **112**.  THE RECORD CONTRADICTED ITS OWN TARGET,
and nothing in this repository looked.  That invariant is free -- both halves are
already in the files -- and it would have caught the fault on the day it was
introduced.  The lesson is the project's own: an assertion nobody wrote is
indistinguishable from one that passes.

WHY IT IS A RATCHET AND NOT A THRESHOLD.  The paragraph number is NOT a key:
only 28 of 118 volumes carry a non-decreasing series, 90 restart, and `21Khu04`
holds 4,347 duplicate numbers among 4,858 numbered paragraphs.  Some layers
genuinely do not correspond paragraph-for-paragraph, so a perfect score is not
available and demanding one would mean either a permanently red gate or a
threshold picked to be green, which measures nothing.  So this records the
CURRENT numbers and fails when they get WORSE.  A repair must move them up; a
regression cannot hide in an aggregate.

THREE MEASURES, because one can be gamed by dropping links:

  n-match      of the targets carrying a paragraph number, the share landing on
               a paragraph with that number (or on a range paragraph covering
               it -- the edition prints `111-114.` and means it)
  name-match   of the canon->layer links where BOTH sides name a sutta, the
               share whose names share a stem.  This is the one a reader feels:
               it is exactly "did the sutta keep its name"
  reachable    distinct layer paragraphs any link reaches.  Without this, a
               map could raise both rates by deleting every hard case

Usage:
  python3 pipeline/check_links.py                 # measure and compare
  python3 pipeline/check_links.py --record        # accept current as baseline
  python3 pipeline/check_links.py --negative-control
Exit 0 = no measure regressed.
"""
import json, os, re, sys, glob, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, 'site')
LINKS = os.path.join(SITE, 'reader', 'linksk')
BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    'links_baseline.json')
TOL = 0.001          # a tenth of a percentage point of float noise

RANGE = re.compile(r'^\s*(\d+)\s*[-–]\s*(\d+)\s*\.')
LEAD = re.compile(r'^[\d\s.,\-–()]+')
TAIL = re.compile(r'(vaṇṇanā|vaṇṇanaṁ|vaṇṇana)$')
KIND = re.compile(r'(suttanta|sutta|vagga|nipāta|pāḷi|kathā|desanā|dvaya|ṁ)+$')

_pc, _sn = {}, {}


def P(v):
    if v not in _pc:
        try:
            d = json.load(open(os.path.join(SITE, v + '.json'), encoding='utf-8'))
            _pc[v] = d.get('paragraphs') or d.get('paras') or []
        except Exception:
            _pc[v] = []
    return _pc[v]


def stem(s):
    s = (s or '').strip().lower()
    s = LEAD.sub('', s)
    s = re.sub(r'[^a-zāīūṁṃṅñṭḍṇḷ]', '', s)
    prev = None
    while prev != s:
        prev = s
        s = TAIL.sub('', s)
        s = KIND.sub('', s)
    return s


def name_at(v, i):
    """The section name covering ordinal i: the `sutta` field marks where a
    section opens, so it is carried forward."""
    if v not in _sn:
        out, cur, st = [], None, 0
        ps = P(v)
        for j, p in enumerate(ps):
            if p.get('sutta'):
                if cur is not None:
                    out.append((st, j - 1, cur))
                cur, st = p['sutta'], j
        if cur is not None:
            out.append((st, len(ps) - 1, cur))
        _sn[v] = out
    for a, b, nm in _sn[v]:
        if a <= i <= b:
            return nm
    return None


def measure(load=None):
    """`load` lets the negative control feed a perturbed map in memory."""
    nok = nbad = agree = dis = 0
    reach = set()
    worst = collections.Counter()
    for f in sorted(glob.glob(os.path.join(LINKS, '*.links.json'))):
        src = os.path.basename(f).split('.')[0]
        cps = P(src)
        if not cps:
            continue
        L = (load(f) if load else
             json.load(open(f, encoding='utf-8')))
        for ordk, e in L.items():
            i = int(ordk)
            if i >= len(cps):
                continue
            cn = name_at(src, i)
            for kind in ('commentary', 'subcommentary'):
                for t in (e.get(kind) or []):
                    key = t.get('key') or ''
                    if '#' not in key:
                        continue
                    v, o = key.rsplit('#', 1)
                    ps = P(v)
                    if not ps or int(o) >= len(ps):
                        continue
                    q = ps[int(o)]
                    reach.add(key)
                    n = t.get('n')
                    if n is not None:
                        m = RANGE.match(q.get('text') or '')
                        if q.get('n') == n or (m and int(m.group(1)) <= n
                                               <= int(m.group(2))):
                            nok += 1
                        else:
                            nbad += 1
                            worst[src] += 1
                    tn = name_at(v, int(o))
                    if cn and tn:
                        a, b = stem(cn), stem(tn)
                        if a and b and (a == b or a in b or b in a):
                            agree += 1
                        else:
                            dis += 1
    return {'n_match': round(100.0 * nok / max(nok + nbad, 1), 3),
            'name_match': round(100.0 * agree / max(agree + dis, 1), 3),
            'reachable': len(reach),
            'n_checked': nok + nbad, 'name_checked': agree + dis}, worst


def report(m, worst, base):
    print('  n-match     %7.2f%%  of %d numbered targets' % (m['n_match'], m['n_checked']))
    print('  name-match  %7.2f%%  of %d links naming a sutta on both sides'
          % (m['name_match'], m['name_checked']))
    print('  reachable   %7d    distinct layer paragraphs' % m['reachable'])
    fails = []
    if base:
        for k, label in (('n_match', 'n-match'), ('name_match', 'name-match'),
                         ('reachable', 'reachable paragraphs')):
            if m[k] < base[k] - (TOL if k != 'reachable' else 0):
                fails.append('%s fell from %s to %s' % (label, base[k], m[k]))
        print('  baseline    n-match %s%%  name-match %s%%  reachable %d'
              % (base['n_match'], base['name_match'], base['reachable']))
    else:
        print('  (no baseline recorded — run with --record)')
    if worst:
        print('  worst sources by wrong-number targets: %s'
              % ', '.join('%s %d' % kv for kv in worst.most_common(6)))
    return fails


if __name__ == '__main__':
    base = (json.load(open(BASE, encoding='utf-8'))
            if os.path.exists(BASE) else None)

    if '--negative-control' in sys.argv:
        # !!! A CHECK THAT CANNOT FAIL IS A COMMENT.  Shift every ordinal by one
        # in memory -- the shape of the reported fault, an off-by-one into the
        # neighbouring paragraph -- and require every measure to notice.
        def shifted(f):
            L = json.load(open(f, encoding='utf-8'))
            for e in L.values():
                for kind in ('commentary', 'subcommentary'):
                    for t in (e.get(kind) or []):
                        k = t.get('key') or ''
                        if '#' in k:
                            v, o = k.rsplit('#', 1)
                            t['key'] = '%s#%d' % (v, int(o) + 1)
            return L
        m, w = measure(load=shifted)
        print('--- negative control: every ordinal shifted by one ---')
        f = report(m, w, base)
        if not f:
            print('\nCONTROL IS BROKEN: shifting every link by one paragraph '
                  'did not move a single measure')
            sys.exit(1)
        print('\ncontrol fired: %s' % '; '.join(f))
        sys.exit(0)

    m, w = measure()
    print('cross-layer links, %s' % LINKS)
    fails = report(m, w, base)
    if '--record' in sys.argv:
        json.dump(m, open(BASE, 'w', encoding='utf-8'), indent=1)
        print('\nbaseline recorded')
        sys.exit(0)
    if fails:
        print('\nLINKS REGRESSED:')
        for x in fails:
            print('  - %s' % x)
        sys.exit(1)
    print('\nno measure regressed')
