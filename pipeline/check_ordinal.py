#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Does the commentary agree with the link about which sutta it is glossing?

WHY THIS EXISTS.  The commentary states its own position in the vagga, in
words, at the head of the paragraph:

    113. Sattame adhammacariyāti...          "in the seventh"
    107. Ekādasamassa paṭhame asubhāti...    "of the eleventh, in the first"

3,617 paragraphs say this and nothing in the repository had ever read it.  The
canon side already carries the same number -- `sutta_n` is a sutta's position in
its vagga -- so for every link the two can be compared, and the comparison is
free.  It is immune to both faults that defeated everything else: the paragraph
number is not a key (`19AnA03` holds two paragraphs numbered 113), and the
formulaic vocabulary that made the content test useless in the Abhidhamma does
not touch an ordinal.

WHAT IT MEASURES, AND THE FLOOR IT IS MEASURED AGAINST.  `sutta_n` runs 1..10
over most of the Aṅguttara, so agreement by chance is not small -- 9.2% from the
observed distribution alone.  Every rate here is therefore printed beside the
same test run against the canon paragraph 25 places away.  A rate without its
floor is not evidence; `_xc/residue_split2.py` is in this repository because a
test that scored 10.8% against a 6.7% floor looked like a finding until the floor
was measured.

WHAT IT DOES NOT MEASURE.  The ordinal names a position WITHIN a vagga, so a
link that is wrong by whole vaggas can still agree: two regions ten suttas apart
line up position-for-position.  222 links pass this and fail the name test for
exactly that reason.  The two are complementary; neither is a substitute.

WHY A RATCHET AND NOT A THRESHOLD.  Same reason as `pipeline/check_links.py`:
some layers genuinely do not correspond, a perfect score is not available, and a
threshold picked to be green measures nothing.  This records the current numbers
and fails when they get worse.

Usage:
  python3 pipeline/check_ordinal.py                  # measure and compare
  python3 pipeline/check_ordinal.py --record         # accept current as baseline
  python3 pipeline/check_ordinal.py --negative-control
Exit 0 = no measure regressed.
"""
import json, os, re, sys, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import ordinal_words

SITE = os.path.join(ROOT, 'site')
LINKS = os.path.join(SITE, 'reader', 'linksk')
BASE = os.path.join(HERE, 'ordinal_baseline.json')
TOL = 0.001
FAR = 25
VOLFILE = re.compile(r'^\d\d[A-Za-z][A-Za-z0-9]*\.json$')

LEAD = re.compile(r'^[\d\s.,\-–()]+')
TAIL = re.compile(r'(vaṇṇanā|vaṇṇānā|vaṇṇanaṁ|vaṇṇana)$')
KIND = re.compile(r'(suttanta|sutta|vagga|nipāta|pāḷi|kathā|desanā|dvaya|ṁ)+$')


def stem(s):
    """The section-name stemmer of `pipeline/relink_by_name.py`, with one
    addition: `vaṇṇānā` (long ā) is stripped too.  It occurs twice, in
    `14SamA01`, and both were counted as name mismatches until now."""
    s = (s or '').strip().lower()
    s = LEAD.sub('', s)
    s = re.sub(r'[^a-zāīūṁṃṅñṭḍṇḷ]', '', s)
    prev = None
    while prev != s:
        prev = s
        s = TAIL.sub('', s)
        s = KIND.sub('', s)
    return s


_pc = {}
def P(v):
    if v not in _pc:
        try:
            _pc[v] = json.load(open(os.path.join(SITE, v + '.json'),
                                    encoding='utf-8')).get('paragraphs') or []
        except Exception:
            _pc[v] = []
    return _pc[v]


_oc = {}
def O(v):
    """{index: ordinal} for every paragraph of v that states one."""
    if v not in _oc:
        _oc[v] = {i: o for i, o in
                  ((i, ordinal_words.read(p.get('text', ''))[0])
                   for i, p in enumerate(P(v))) if o is not None}
    return _oc[v]


_sc = {}
def name_at(v, i):
    """The section name covering paragraph i -- the `sutta` field marks where a
    section opens, not every member, so it is forward-filled."""
    if v not in _sc:
        run, cur = [], None
        for p in P(v):
            cur = p.get('sutta') or cur
            run.append(cur)
        _sc[v] = run
    r = _sc[v]
    return r[i] if 0 <= i < len(r) else None


def sn(p):
    try:
        return int(p.get('sutta_n'))
    except (TypeError, ValueError):
        return None


def measure(shift=0):
    m = collections.Counter()
    for f in sorted(os.listdir(SITE)):
        if VOLFILE.match(f):
            m['stated'] += len(O(f[:-5]))
    for f in sorted(os.listdir(LINKS)):
        if not f.endswith('.links.json'):
            continue
        cv = f[:-len('.links.json')]
        cps = P(cv)
        if not cps:
            continue
        links = json.load(open(os.path.join(LINKS, f), encoding='utf-8'))
        for si, rec in links.items():
            i = int(si)
            if i >= len(cps):
                continue
            a = sn(cps[i])
            if a is None:
                continue
            cn = stem(name_at(cv, i))
            for layer in ('commentary', 'subcommentary'):
                for ent in rec.get(layer) or []:
                    if ent.get('state') != 'direct':
                        continue
                    tv, _, tis = (ent.get('key') or '').partition('#')
                    if not tis.isdigit():
                        continue
                    ti = int(tis) + shift
                    o = O(tv).get(ti)
                    if o is None:
                        continue
                    m['checked'] += 1
                    hit = (o == a)
                    m['match'] += hit
                    if ent.get('by') == 'name':
                        m['byname'] += 1
                        m['byname_match'] += hit
                    tps = P(tv)
                    tn = stem(tps[ti].get('sutta')) if ti < len(tps) else ''
                    if cn and tn:
                        m['named'] += 1
                        m['named_agree'] += (cn == tn)
                        if not hit:
                            m['cond_named'] += 1
                            m['cond_named_bad'] += (cn != tn)
                    elif not hit:
                        m['cond_nameless'] += 1
                    for d in (-FAR, FAR):
                        j = i + d
                        if 0 <= j < len(cps):
                            b = sn(cps[j])
                            if b is not None:
                                m['far'] += 1
                                m['far_match'] += (b == o)
    return m


def rates(m):
    def pc(a, b):
        return round(100.0 * m[a] / m[b], 3) if m[b] else 0.0
    return {
        'stated': m['stated'],
        'checked': m['checked'],
        'ord_match': pc('match', 'checked'),
        'ord_floor': pc('far_match', 'far'),
        'byname_match': pc('byname_match', 'byname'),
        'condemned': m['checked'] - m['match'],
        'condemned_nameless': m['cond_nameless'],
        'condemned_name_concurs': pc('cond_named_bad', 'cond_named'),
    }


# ratchet direction: +1 must not fall, -1 must not rise
DIR = {'stated': 1, 'checked': 1, 'ord_match': 1, 'byname_match': 1,
       'condemned': -1, 'ord_floor': 0, 'condemned_nameless': 0,
       'condemned_name_concurs': 0}


def report(r, base):
    fails = []
    for k in ('stated', 'checked', 'ord_match', 'ord_floor', 'byname_match',
              'condemned', 'condemned_nameless', 'condemned_name_concurs'):
        v, b = r[k], (base or {}).get(k)
        unit = '%' if k.endswith(('match', 'floor', 'concurs')) else ''
        line = '  %-24s %10s%s' % (k, v, unit)
        if b is not None:
            line += '   was %s%s' % (b, unit)
            d = DIR[k]
            if d and ((d > 0 and v < b - TOL) or (d < 0 and v > b + TOL)):
                line += '   REGRESSED'
                fails.append('%s %s%s -> %s%s' % (k, b, unit, v, unit))
        print(line)
    print('\n  margin over the shift-%d floor: %+.1f points'
          % (FAR, r['ord_match'] - r['ord_floor']))
    return fails


if __name__ == '__main__':
    base = None
    if os.path.exists(BASE):
        base = json.load(open(BASE, encoding='utf-8'))

    if '--negative-control' in sys.argv:
        r = rates(measure(shift=1))
        print('--- negative control: every link target read one paragraph on ---')
        ok = base and r['ord_match'] < base['ord_match'] - 5
        report(r, base)
        if not ok:
            print('\nCONTROL IS BROKEN: reading the neighbouring paragraph did '
                  'not move the agreement rate')
            sys.exit(1)
        print('\ncontrol fired')
        sys.exit(0)

    r = rates(measure())
    print('stated ordinals against cross-layer links, %s' % LINKS)
    fails = report(r, base)
    if '--record' in sys.argv:
        json.dump(r, open(BASE, 'w', encoding='utf-8'), indent=1)
        print('\nbaseline recorded')
        sys.exit(0)
    if fails:
        print('\nORDINAL AGREEMENT REGRESSED:')
        for x in fails:
            print('  - %s' % x)
        sys.exit(1)
    print('\nno measure regressed')
