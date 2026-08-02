#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""THE ABSOLUTE TEST DOES NOT DISCRIMINATE. MEASURE THE FLOOR, THEN BEAT IT.

`_xc/residue_split.py` split the 44.8% residue and printed its own refutation:

    shift 0    confirmed 10.8%    one better 20.6%
    shift 25   confirmed  6.7%    one better 18.8%

A test that scores nearly the same against a canon paragraph twenty-five places
away is not evidence.  The reason is where the residue lives -- Abhidhamma and
Vinaya -- and those texts are formulaic: the Paṭṭhāna repeats the same phrases
thousands of times, so "the commentary quotes a word that occurs in this
paragraph" is nearly free.

TWO CHANGES, both aimed at that.

1. THE FLOOR IS MEASURED PER VOLUME.  One rate over 118 volumes hides a rule
   that is sound in `18Khu01` and worthless in `39Abhi11`.  Every volume gets
   its own shift-25 floor beside its shift-0 rate, and the DIFFERENCE is the
   only number worth reading.

2. THE TEST IS DISCRIMINATIVE, NOT ABSOLUTE.  Not "does the target quote
   something in this paragraph" but "does it quote something that is in THIS
   paragraph and NOT in its neighbours".  A lemma matching here and also 25
   paragraphs away is vocabulary; a lemma matching here and nowhere near is
   alignment.  Same evidence, used against the formulaic text instead of being
   defeated by it.

       score(candidate) = lemmas of the candidate found in canon i
                          MINUS lemmas of the candidate found in canon i±25

   and a candidate is only proposed when its score is positive AND strictly
   greater than every rival's -- a margin, because a tie between two candidates
   is not evidence for either.

3. AND THE PROPOSAL IS CROSS-CHECKED AGAINST A CRITERION IT CANNOT SEE.  Where
   both sides name a section, the NAME says whether a target belongs to this
   sutta -- the discriminator that repaired the links on 2026-08-02, and one
   the content score knows nothing about.  So on the subset where names exist,
   this reports how often the content-proposed target agrees by name, against
   how often the CURRENT target does.  If content-proposal does not beat the
   link already in the file on that subset, it is not a repair, and this
   script's job is to say so before anything is written.

Usage:  python3 _xc/residue_split2.py [--window W] [--vol VOL]
Writes nothing.
"""
import json, os, re, sys, collections, unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, 'site')
LINKS = os.path.join(SITE, 'reader', 'linksk')
BOLD = os.path.join(SITE, 'reader', 'bold')
RANGE = re.compile(r'^\s*(\d+)\s*[-–]\s*(\d+)\s*\.')
LEAD = re.compile(r'^[\d\s.,\-–()]+')
TAIL = re.compile(r'(vaṇṇanā|vaṇṇanaṁ|vaṇṇana)$')
KIND = re.compile(r'(suttanta|sutta|vagga|nipāta|pāḷi|kathā|desanā|dvaya|ṁ)+$')
WINDOW, MINLEN, MAXLEM, FAR = 8, 6, 6, 25

_p, _b, _bynum, _sn, _lem, _body = {}, {}, {}, {}, {}, {}


def P(v):
    if v not in _p:
        q = os.path.join(SITE, v + '.json')
        try:
            d = json.load(open(q, encoding='utf-8'))
            _p[v] = d.get('paragraphs') or d.get('paras') or []
        except Exception:
            _p[v] = []
    return _p[v]


def B(v):
    if v not in _b:
        try:
            _b[v] = json.load(open(os.path.join(BOLD, v + '.bold.json'), encoding='utf-8'))
        except Exception:
            _b[v] = {}
    return _b[v]


def bynum(v):
    if v not in _bynum:
        m = collections.defaultdict(list)
        for i, q in enumerate(P(v)):
            n = q.get('n')
            if n is not None:
                m[n].append(i)
            r = RANGE.match(q.get('text') or '')
            if r:
                for k in range(int(r.group(1)), int(r.group(2)) + 1):
                    if i not in m[k]:
                        m[k].append(i)
        _bynum[v] = m
    return _bynum[v]


def norm(s):
    return re.sub(r'[^a-zāīūṁṅñṭḍṇḷ ]', ' ',
                  unicodedata.normalize('NFC', s or '').lower())


squash = lambda s: re.sub(r'\s+', ' ', s).strip()


def body(v, i):
    k = (v, i)
    if k not in _body:
        ps = P(v)
        _body[k] = squash(norm(ps[i].get('text') or '')) if 0 <= i < len(ps) else ''
    return _body[k]


def lemmas(vol, ord_):
    k = (vol, ord_)
    if k in _lem:
        return _lem[k]
    out, b, ps = [], B(vol), P(vol)
    if b and 0 <= ord_ < len(ps):
        t = ps[ord_].get('text') or ''
        for a, z in (b.get(str(ord_)) or []):
            w = re.sub(r'\s*n?ti$', '', squash(norm(t[a:z]))).strip()
            if len(w) >= MINLEN:
                out.append(w)
        out = sorted(set(out), key=len, reverse=True)[:MAXLEM]
    _lem[k] = out
    return out


def stem(s):
    s = LEAD.sub('', (s or '').strip().lower())
    s = re.sub(r'[^a-zāīūṁṃṅñṭḍṇḷ]', '', s)
    prev = None
    while prev != s:
        prev = s
        s = TAIL.sub('', s)
        s = KIND.sub('', s)
    return s


def name_at(v, i):
    if v not in _sn:
        out, cur, st = [], None, 0
        for j, p in enumerate(P(v)):
            if p.get('sutta'):
                if cur is not None:
                    out.append((st, j - 1, cur))
                cur, st = p['sutta'], j
        if cur is not None:
            out.append((st, len(P(v)) - 1, cur))
        _sn[v] = out
    for a, b, nm in _sn[v]:
        if a <= i <= b:
            return nm
    return None


def agree(a, b):
    a, b = stem(a or ''), stem(b or '')
    return bool(a and b and (a == b or a in b or b in a))


def score(tv, to, cv, ci):
    """+1 for each lemma of the candidate found in canon ci, -1 for each found
    in the far neighbours.  A lemma that matches here AND 25 away is
    vocabulary; only the difference is alignment."""
    lem = lemmas(tv, to)
    if not lem:
        return None
    here = body(cv, ci)
    far = [body(cv, ci - FAR), body(cv, ci + FAR)]
    s = 0
    for l in lem:
        if l in here:
            s += 1
            if any(l in f for f in far if f):
                s -= 1
    return s


def run(shift=0, window=WINDOW, only=None):
    """-> per-volume Counter, and the name cross-check tallies."""
    per = collections.defaultdict(collections.Counter)
    chk = collections.Counter()
    for fn in sorted(os.listdir(LINKS)):
        if not fn.endswith('.links.json'):
            continue
        cv = fn[:-len('.links.json')]
        if only and cv != only:
            continue
        cps = P(cv)
        if not cps:
            continue
        for ordk, e in json.load(open(os.path.join(LINKS, fn), encoding='utf-8')).items():
            i = int(ordk)
            ci = i + shift
            if not (0 <= ci < len(cps)):
                continue
            for slot in ('commentary', 'subcommentary'):
                for t in (e.get(slot) or []):
                    key, n = t.get('key') or '', t.get('n')
                    if n is None or '#' not in key:
                        continue
                    tv, to = key.rsplit('#', 1)
                    to = int(to)
                    ps = P(tv)
                    if not ps or to >= len(ps):
                        continue
                    q = ps[to]
                    m = RANGE.match(q.get('text') or '')
                    if q.get('n') == n or (m and int(m.group(1)) <= n <= int(m.group(2))):
                        continue                       # aligned; not residue
                    per[cv]['residue'] += 1
                    cand = [o for o in bynum(tv).get(n, []) if o != to]
                    cand += [o for o in range(max(0, to - window),
                                              min(len(ps), to + window + 1))]
                    best, bestsc, ties = None, 0, 0
                    for o in dict.fromkeys(cand):
                        s = score(tv, o, cv, ci)
                        if s is None:
                            continue
                        if s > bestsc:
                            best, bestsc, ties = o, s, 1
                        elif s == bestsc and s > 0:
                            ties += 1
                    if bestsc <= 0:
                        per[cv]['none'] += 1
                        continue
                    if ties > 1:
                        per[cv]['tied'] += 1
                        continue
                    if best == to:
                        per[cv]['confirmed'] += 1
                        continue
                    per[cv]['proposed'] += 1
                    # ---- the cross-check the score cannot see
                    cn = name_at(cv, ci)
                    if not cn:
                        continue
                    old, new = name_at(tv, to), name_at(tv, best)
                    if old is None and new is None:
                        continue
                    chk['pairs'] += 1
                    if agree(cn, old):
                        chk['old_agrees'] += 1
                    if agree(cn, new):
                        chk['new_agrees'] += 1
    return per, chk


def main():
    window, only = WINDOW, None
    if '--window' in sys.argv:
        window = int(sys.argv[sys.argv.index('--window') + 1])
    if '--vol' in sys.argv:
        only = sys.argv[sys.argv.index('--vol') + 1]
    per0, chk = run(0, window, only)
    perF, _ = run(FAR, window, only)

    def rate(c, k):
        return 100.0 * c[k] / max(c['residue'], 1)

    tot0 = collections.Counter()
    totF = collections.Counter()
    for c in per0.values():
        tot0.update(c)
    for c in perF.values():
        totF.update(c)

    print('DISCRIMINATIVE SCORE — lemma found here MINUS lemma found %d away\n' % FAR)
    print('%-10s %8s %10s %8s %10s %8s %9s'
          % ('volume', 'residue', 'confirmed', 'floor', 'proposed', 'floor', 'signal'))
    rows = []
    for v, c in per0.items():
        if c['residue'] < 200:
            continue
        f = perF.get(v, collections.Counter())
        rows.append((v, c['residue'], rate(c, 'confirmed'), rate(f, 'confirmed'),
                     rate(c, 'proposed'), rate(f, 'proposed'),
                     rate(c, 'confirmed') - rate(f, 'confirmed')))
    for r in sorted(rows, key=lambda x: -x[6]):
        print('%-10s %8d %9.1f%% %7.1f%% %9.1f%% %7.1f%% %8.1f'
              % r)
    print('%-10s %8d %9.1f%% %7.1f%% %9.1f%% %7.1f%% %8.1f'
          % ('ALL', tot0['residue'], rate(tot0, 'confirmed'), rate(totF, 'confirmed'),
             rate(tot0, 'proposed'), rate(totF, 'proposed'),
             rate(tot0, 'confirmed') - rate(totF, 'confirmed')))
    print('\n  tied %d · no positive score %d' % (tot0['tied'], tot0['none']))

    print('\nCROSS-CHECK against the NAME, which the score cannot see.')
    print('Residue targets the score would MOVE, where a name exists on both sides:')
    p = chk['pairs']
    print('  pairs                                  %6d' % p)
    print('  the link now in the file agrees by name %6d  %5.1f%%'
          % (chk['old_agrees'], 100.0 * chk['old_agrees'] / max(p, 1)))
    print('  the content proposal agrees by name     %6d  %5.1f%%'
          % (chk['new_agrees'], 100.0 * chk['new_agrees'] / max(p, 1)))
    print('\nIf the second is not clearly higher than the first, this is not a repair.')


if __name__ == '__main__':
    main()
