#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Repair the ORDINAL of an existing cross-layer link using the sutta name.

WHY.  User-reported 2026-08-02: clicking **A** on the Aratisutta lands on a
different sutta and the title goes blank.  Measured cause: the paragraph number
is not a key.  Only **28 of 118** volumes carry a non-decreasing paragraph-number
series; **90 restart**, because a commentary volume covers several nipatas and
the numbering begins again with each.  `19AnA03` holds TWO paragraphs numbered
113 -- ord 255 (Aratisuttavannana, p.142) and ord 490
(Adhammasuttadvayavannana, p.336) -- and the live link points at neither: the
monotonic walk in `build_links_bynum.py` was in the wrong region and fell back to
`state: "covered"`, the nearest EARLIER number, which is 112.

That is open question 8.1 of the project instructions -- "Do paragraph numbers
genuinely align across all three layers?  Test before building" -- answered in
the negative, after it was built on.

WHAT THIS DOES, AND WHAT IT DELIBERATELY DOES NOT.  It does NOT re-route
volumes.  `build_links_bynum.py` recorded, with numbers, that a full rebuild
constrained by the concordance LOST on both axes at once, and that removing the
wrong volume does not make the ordinal right.  So the target VOLUME is taken as
given and only the ORDINAL inside it is reconsidered -- the minimum change that
addresses the measured fault.

THE DISCRIMINATOR IS THE NAME.  The commentary on the Aratisutta is called
`Aratisuttavannana`.  Where the number is ambiguous the name is not.  So:

  * both volumes are cut into SECTIONS -- a named paragraph and every unnamed
    paragraph after it, since the `sutta` field is sparse (21-24% of canon and
    commentary paragraphs carry one) and marks where a section OPENS;
  * the canon paragraph's section name is stemmed and matched against the target
    volume's section names;
  * the number match then runs INSIDE that section only.

On the 28 monotonic volumes this changes nothing.  On the 90 restarting ones it
confines the walk to the right region before the number is consulted at all,
which is exactly what failed.

WHERE THERE IS NO NAME ON EITHER SIDE, NOTHING IS TOUCHED.  Most of the
Abhidhamma has no sutta names, and a repair that guessed there would be trading
a measured fault for an unmeasured one.

Writes to `_xc/linksk_named/`, NEVER into `site/` -- defect 3 of
`build_links_bynum.py`: `site/` is published and hashed into BUILD, so a dry run
would move the cache-buster for every visitor.
"""
import json, os, re, sys, collections

# repo root: this file lives in pipeline/, like every other build script
ROOT = os.environ.get(
    'RELINK_ROOT',
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SITE = os.path.join(ROOT, 'site')
LINKS = os.path.join(SITE, 'reader', 'linksk')
OUT = os.path.join(ROOT, '_xc', 'linksk_named')

_pc = {}


def P(v):
    if v not in _pc:
        p = os.path.join(SITE, v + '.json')
        try:
            d = json.load(open(p, encoding='utf-8'))
            _pc[v] = d.get('paragraphs') or d.get('paras') or []
        except Exception:
            _pc[v] = []
    return _pc[v]


# the abbreviated upper bound (`234-5.` = 234-235) -- see printed_range.py
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from printed_range import expand_range
LEAD = re.compile(r'^[\d\s.,\-–()]+')
TAIL = re.compile(r'(vaṇṇanā|vaṇṇanaṁ|vaṇṇana)$')
KIND = re.compile(r'(suttanta|sutta|vagga|nipāta|pāḷi|kathā|desanā|dvaya|ṁ)+$')


def stem(s):
    """A comparable core for 'Aratisutta' and 'Aratisuttavaṇṇanā'.

    Strips the leading numbering ('1-2. '), then the commentary's -vaṇṇanā, then
    the genre words both sides append.  Deliberately blunt: it is used only to
    decide WHICH SECTION, never to assert that two things are the same text.
    """
    s = (s or '').strip().lower()
    s = LEAD.sub('', s)
    s = re.sub(r'[^a-zāīūṁṃṅñṭḍṇḷ]', '', s)
    prev = None
    while prev != s:
        prev = s
        s = TAIL.sub('', s)
        s = KIND.sub('', s)
    return s


def sections(ps):
    """(start, end, name) runs.  A section opens at a NAMED paragraph and runs
    to the paragraph before the next named one -- the `sutta` field marks the
    opening, not every member."""
    out, cur, start = [], None, 0
    for i, p in enumerate(ps):
        s = p.get('sutta')
        if s:
            if cur is not None:
                out.append((start, i - 1, cur))
            cur, start = s, i
    if cur is not None:
        out.append((start, len(ps) - 1, cur))
    return out


_sc = {}


def secs(v):
    if v not in _sc:
        ss = sections(P(v))
        by = collections.defaultdict(list)
        for a, b, nm in ss:
            k = stem(nm)
            if k:
                by[k].append((a, b))
        _sc[v] = (ss, by)
    return _sc[v]


def canon_name(v, i):
    """The section name covering canon ordinal i (forward-filled)."""
    ss, _ = secs(v)
    for a, b, nm in ss:
        if a <= i <= b:
            return nm
    return None


def place(v, a, b, n):
    """Inside [a,b] of volume v, find the paragraph for number n.

    Exact number wins; a range paragraph that covers n is equally exact (the
    edition prints '111-114.' and means it); otherwise the nearest EARLIER
    numbered paragraph, which is what 'covered' has always meant.  Falls back to
    the section's own opening, never outside it.
    """
    ps = P(v)
    b = min(b, len(ps) - 1)
    best = None
    for j in range(a, b + 1):
        q = ps[j]
        if q.get('n') == n:
            return j, 'direct'
        r = expand_range(q.get('text') or '')
        if r and r[0] <= n <= r[1]:
            return j, 'direct'
        if q.get('n') is not None and q['n'] <= n:
            best = j
    return (best, 'covered') if best is not None else (a, 'covered')


def run(write=True, out=None, part=None):
    """`part` is (k, n): process only the k-th of n slices of the link files.

    The bridged filesystem this is run over caps a command at 45 seconds, and a
    background process does not survive the call, so the work has to be
    divisible.  Slicing by FILE keeps each slice self-contained -- a link file
    is rewritten whole or not at all.
    """
    out = out or OUT
    os.makedirs(out, exist_ok=True)
    stat = collections.Counter()
    moved_by_vol = collections.Counter()
    changes = []
    files = [f for f in sorted(os.listdir(LINKS)) if f.endswith('.links.json')]
    if part:
        k, n = part
        files = [f for j, f in enumerate(files) if j % n == k]
    for f in files:
        src = f.split('.')[0]
        L = json.load(open(os.path.join(LINKS, f), encoding='utf-8'))
        cps = P(src)
        if not cps:
            if write:
                json.dump(L, open(os.path.join(out, f), 'w', encoding='utf-8'),
                          ensure_ascii=False)
            continue
        for ordk, e in L.items():
            i = int(ordk)
            if i >= len(cps):
                continue
            cname = canon_name(src, i)
            ck = stem(cname) if cname else None
            cn = cps[i].get('n')
            for kind in ('commentary', 'subcommentary'):
                for t in (e.get(kind) or []):
                    stat['targets'] += 1
                    key = t.get('key') or ''
                    if '#' not in key:
                        continue
                    tv, o = key.rsplit('#', 1)
                    o = int(o)
                    n = t.get('n', cn)
                    if not ck or n is None:
                        stat['no anchor'] += 1
                        continue
                    _, by = secs(tv)
                    cands = by.get(ck) or []
                    if not cands:
                        stat['no matching section in target'] += 1
                        continue
                    if len(cands) > 1:
                        # several sections of that name: prefer one that really
                        # carries the number, else the one nearest where the
                        # existing link already points.  Ambiguity is resolved,
                        # never ignored -- and it is counted, so the residue is
                        # visible instead of implied.
                        withn = [c for c in cands
                                 if place(tv, c[0], c[1], n)[1] == 'direct']
                        cands = withn or cands
                        cands = sorted(cands, key=lambda c: abs(c[0] - o))
                        stat['ambiguous section name'] += 1
                    a, b = cands[0]
                    j, st = place(tv, a, b, n)
                    if j == o:
                        stat['unchanged'] += 1
                        continue
                    stat['MOVED'] += 1
                    stat['moved ' + st] += 1
                    moved_by_vol[src] += 1
                    if len(changes) < 12:
                        ps = P(tv)
                        changes.append((src, i, cname, key, '->',
                                        '%s#%d' % (tv, j),
                                        ps[j].get('sutta') or '(unnamed)', st))
                    t['key'] = '%s#%d' % (tv, j)
                    t['state'] = st
                    t['by'] = 'name'
        if write:
            json.dump(L, open(os.path.join(out, f), 'w', encoding='utf-8'),
                      ensure_ascii=False)
    return stat, moved_by_vol, changes


if __name__ == '__main__':
    a = sys.argv[1:]
    # !!! `--apply` IS THE ONLY WAY THIS TOUCHES site/.  Default output is
    # _xc/linksk_named/, for the same reason build_links_bynum.py records as its
    # defect 3: site/ is published and hashed into BUILD, so a dry run there
    # would move the cache-buster for every visitor.
    out = LINKS if '--apply' in a else OUT
    part = None
    if '--part' in a:
        k, n = a[a.index('--part') + 1].split('/')
        part = (int(k), int(n))
    st, per, ch = run(write='--dry' not in a, out=out, part=part)
    print('writing to %s%s' % (out, '  [PART %s/%s]' % part if part else ''))
    print('link targets seen            %7d' % st['targets'])
    print('  no name on the canon side  %7d' % st['no anchor'])
    print('  no section of that name in')
    print('  the target volume          %7d' % st['no matching section in target'])
    print('  ambiguous (>1 section of')
    print('  that name), resolved       %7d' % st['ambiguous section name'])
    print('  already correct            %7d' % st['unchanged'])
    print('  MOVED                      %7d  (direct %d, covered %d)'
          % (st['MOVED'], st['moved direct'], st['moved covered']))
    print()
    for c in ch:
        print('  ', c)
    print()
    print('most moved source volumes:', per.most_common(10))
