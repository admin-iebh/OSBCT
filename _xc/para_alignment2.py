#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OPEN QUESTION #1, tested WITHOUT using the paragraph number.

THE FIRST ATTEMPT WAS CIRCULAR AND IS RECORDED HERE SO NOBODY REPEATS IT.
Comparing `n` across the pairs in `site/reader/links/<VOL>.rev.json` gives
**100.0% on 24,159 pairs** against a 0-0.2% control — and it means nothing,
because `pipeline/build_links_bynum.py` CREATES the `direct` state BY matching
that very number ("canon N -> the commentary paragraph numbered N").  The test
measured the builder's compliance with its own docstring.

THIS TEST USES THE LEMMA INSTEAD.  A commentary paragraph opens by quoting the
canon words it is about, and the corpus already marks those quotations: the
`bold/<VOL>.bold.json` side-map holds their character spans, built from the
edition's own typography and never from a number.  So:

    for each `direct` pair, does the commentary's bolded lemma actually occur
    in the canon paragraph that the number says it explains?

CONTROL: the same lemma against the canon paragraph k places away in the same
volume.  Pāḷi is formulaic and a short lemma can recur, so the control is what
separates alignment from vocabulary.
"""
import json, glob, os, re, sys, collections, unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_c = {}


def paras(v):
    if v not in _c:
        p = os.path.join(ROOT, 'site', v + '.json')
        _c[v] = json.load(open(p, encoding='utf-8'))['paragraphs'] if os.path.exists(p) else None
    return _c[v]


def norm(s):
    s = unicodedata.normalize('NFC', s or '').lower()
    return re.sub(r'[^a-zāīūṁṅñṭḍṇḷ ]', ' ', s)


def squash(s):
    return re.sub(r'\s+', ' ', s).strip()


def lemmas(vol, ord_, minlen=6):
    """The bolded quotations of a commentary paragraph, longest first."""
    b = _bold(vol)
    if not b:
        return []
    spans = b.get(str(ord_)) or []
    ps = paras(vol)
    if not ps or not (0 <= ord_ < len(ps)):
        return []
    t = ps[ord_].get('text') or ''
    out = []
    for a, z in spans:
        w = squash(norm(t[a:z]))
        # a lemma is quoted with its `ti` enclitic; the canon has the bare word
        w = re.sub(r'\s*n?ti$', '', w).strip()
        if len(w) >= minlen:
            out.append(w)
    return sorted(set(out), key=len, reverse=True)[:4]


_bcache = {}


def _bold(vol):
    if vol not in _bcache:
        p = os.path.join(ROOT, 'site/reader/bold', vol + '.bold.json')
        _bcache[vol] = json.load(open(p, encoding='utf-8')) if os.path.exists(p) else None
    return _bcache[vol]


def run(shift=0):
    man = json.load(open(os.path.join(ROOT, 'site/reader/manifest.json'),
                        encoding='utf-8'))['volumes']
    per = collections.defaultdict(lambda: [0, 0])
    for rp in sorted(glob.glob(os.path.join(ROOT, 'site/reader/links/*.rev.json'))):
        vol = os.path.basename(rp)[:-9]
        layer = man.get(vol, {}).get('layer', '?')
        if _bold(vol) is None or paras(vol) is None:
            continue
        rev = json.load(open(rp, encoding='utf-8'))
        items = sorted((int(o), e) for o, e in rev.items()
                       if e.get('state') == 'direct' and e.get('canon'))
        for i, (o, e) in enumerate(items):
            lem = lemmas(vol, o)
            if not lem:
                continue
            j = i + shift
            if not (0 <= j < len(items)):
                continue
            cv, co = items[j][1]['canon'].split('#')
            cps = paras(cv)
            if not cps or not (0 <= int(co) < len(cps)):
                continue
            body = squash(norm(cps[int(co)].get('text') or ''))
            per[layer][0] += 1
            per[layer][1] += any(l in body for l in lem)
    return per


if __name__ == '__main__':
    print('Does the commentary\'s BOLDED LEMMA occur in the canon paragraph the\n'
          'paragraph number says it explains?  (the number is used only to pick\n'
          'the pair; the evidence is the quotation)\n')
    real = run(0)
    print('%-16s %10s %10s %8s' % ('layer', 'pairs', 'lemma found', 'rate'))
    for lay in sorted(real):
        n, a = real[lay]
        print('%-16s %10d %10d %7.1f%%' % (lay, n, a, 100.0 * a / n if n else 0))
    print('\nCONTROL — same lemma, canon paragraph k places away:')
    for k in (1, 2, 5, 25):
        ctl = run(k)
        line = '  shift %-3d' % k
        for lay in sorted(real):
            n, a = ctl.get(lay, (0, 0))
            line += '   %-14s %5.1f%%' % (lay, (100.0 * a / n) if n else 0.0)
        print(line)
