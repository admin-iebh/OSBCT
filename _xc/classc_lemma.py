#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Is Class C adjudicable link by link, or does it need the builder rebuilt?

CLASS C is the 14,278 forward link targets the edition does not assign for that
slot, but where it DOES assign something — so, unlike Class A, the target is not
impossible, merely unattested.  Volume identity cannot separate them: the Jātaka
commentary runs continuously across 22Khu05 and 23Khu06, so `20Khu03 -> 33KhuA14`
may be a real seam, while `39Abhi11 -> 48AbhiA01` (Paṭṭhāna IV pointing at the
Dhammasaṅgaṇī commentary) plainly is not.

THE TEST IS THE ONE THAT ALREADY WORKS, from `_xc/para_alignment2.py`: a
commentary paragraph opens by quoting the canon words it is about, and
`bold/<VOL>.bold.json` marks those quotations from the edition's own typography,
never from a number.  So for each `direct` link, does the TARGET paragraph's
bolded lemma actually occur in the canon paragraph that claims it?

Known baselines (2026-07-31b, measured the other way round, on rev pairs):
allowed 50.0% on 19,511 pairs, not-allowed 10.4% on 4,494.

CONTROL: the same lemma against a canon paragraph k places away in the same
volume.  Pāḷi is formulaic and a short lemma recurs, so the control is what
separates alignment from vocabulary.  A result is only readable against it.

Usage: python3 _xc/classc_lemma.py
"""
import json, os, re, sys, collections, unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LINKSK = os.path.join(ROOT, 'site/reader/linksk')
SLOTS = ('canon', 'commentary', 'subcommentary')
_p, _b = {}, {}


def paras(v):
    if v not in _p:
        q = os.path.join(ROOT, 'site', v + '.json')
        _p[v] = json.load(open(q, encoding='utf-8'))['paragraphs'] if os.path.exists(q) else None
    return _p[v]


def bold(v):
    if v not in _b:
        q = os.path.join(ROOT, 'site/reader/bold', v + '.bold.json')
        _b[v] = json.load(open(q, encoding='utf-8')) if os.path.exists(q) else None
    return _b[v]


def norm(s):
    return re.sub(r'[^a-zāīūṁṅñṭḍṇḷ ]', ' ', unicodedata.normalize('NFC', s or '').lower())


def squash(s):
    return re.sub(r'\s+', ' ', s).strip()


def lemmas(vol, ord_, minlen=6):
    b = bold(vol)
    if not b:
        return []
    ps = paras(vol)
    if not ps or not (0 <= ord_ < len(ps)):
        return []
    t = ps[ord_].get('text') or ''
    out = []
    for a, z in (b.get(str(ord_)) or []):
        w = re.sub(r'\s*n?ti$', '', squash(norm(t[a:z]))).strip()
        if len(w) >= minlen:
            out.append(w)
    return sorted(set(out), key=len, reverse=True)[:4]


def model():
    conc = json.load(open(os.path.join(ROOT, 'site/concordance.json'), encoding='utf-8'))
    allow = collections.defaultdict(lambda: {'commentary': set(), 'subcommentary': set()})
    for g in conc['groups']:
        f = {s: list(g[s]['files']) for s in SLOTS}
        pres = [s for s in SLOTS if f[s]]
        if not pres:
            continue
        spine, below = pres[0], pres[1:]
        for v in f[spine]:
            for s in below:
                allow[v][s].update(f[s])
    return allow


def run(shift=0):
    allow = model()
    # bucket -> [pairs, lemma found]; plus per-canon-volume and per-target detail
    agg = collections.defaultdict(lambda: [0, 0])
    bycanon = collections.defaultdict(lambda: [0, 0])
    bytarget = collections.defaultdict(lambda: [0, 0])
    for fn in sorted(os.listdir(LINKSK)):
        if not fn.endswith('.links.json'):
            continue
        cv = fn[:-len('.links.json')]
        cps = paras(cv)
        if not cps:
            continue
        al = allow.get(cv)
        if not al:
            continue
        for o, e in json.load(open(os.path.join(LINKSK, fn), encoding='utf-8')).items():
            co = int(o) + shift
            if not (0 <= co < len(cps)):
                continue
            body = squash(norm(cps[co].get('text') or ''))
            for slot in ('commentary', 'subcommentary'):
                for t in (e.get(slot) or []):
                    if t.get('state') != 'direct':
                        continue
                    tv, to = t['key'].split('#')
                    lem = lemmas(tv, int(to))
                    if not lem:
                        continue
                    hit = any(l in body for l in lem)
                    ok = tv in al[slot]
                    b = 'ALLOWED' if ok else 'CLASS C'
                    agg[b][0] += 1; agg[b][1] += hit
                    if not ok:
                        bycanon[cv][0] += 1; bycanon[cv][1] += hit
                        bytarget[(cv, tv)][0] += 1; bytarget[(cv, tv)][1] += hit
    return agg, bycanon, bytarget


if __name__ == '__main__':
    agg, bycanon, bytarget = run(0)
    print("Does the TARGET paragraph's bolded lemma occur in the canon paragraph")
    print("that links to it?  (`direct` links only; the number picks the pair,")
    print("the quotation is the evidence)\n")
    print('%-10s %10s %12s %8s' % ('bucket', 'pairs', 'lemma found', 'rate'))
    for b in ('ALLOWED', 'CLASS C'):
        n, a = agg[b]
        print('%-10s %10d %12d %7.1f%%' % (b, n, a, 100.0 * a / n if n else 0))

    print('\nCONTROL — same lemma, canon paragraph k places away:')
    for k in (1, 2, 5, 25):
        c, _, _ = run(k)
        line = '  shift %-3d' % k
        for b in ('ALLOWED', 'CLASS C'):
            n, a = c[b]
            line += '   %-8s %5.1f%%' % (b, (100.0 * a / n) if n else 0.0)
        print(line)

    print('\nCLASS C by canon volume (pairs >= 25), highest rate first:')
    rows = [(v, n, a, 100.0 * a / n) for v, (n, a) in bycanon.items() if n >= 25]
    for v, n, a, r in sorted(rows, key=lambda x: -x[3]):
        print('   %-10s %6d pairs %6d found %6.1f%%' % (v, n, a, r))

    print('\nCLASS C by (canon -> target) pair (pairs >= 25), highest rate first:')
    rows = [(k, n, a, 100.0 * a / n) for k, (n, a) in bytarget.items() if n >= 25]
    for (cv, tv), n, a, r in sorted(rows, key=lambda x: -x[3])[:28]:
        print('   %-10s -> %-10s %5d pairs %5d found %6.1f%%' % (cv, tv, n, a, r))
