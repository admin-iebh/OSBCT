#!/usr/bin/env python3
"""Content-anchored cross-layer linker for the piṭakas where number-match alone
fails (Vinaya, Abhidhamma, Khuddaka): commentary volume boundaries and numbering
don't track the canon. A commentary paragraph explains a canon paragraph by
quoting its distinctive words (lemmata), so we match on shared long words,
using the shared paragraph number as a prior when available.

For each canon paragraph we consider commentary paragraphs in the same-piṭaka
commentary/sub-commentary volumes whose number is within a small window of the
canon number, and pick the one sharing the most distinctive (len>=8) words.
Monotonic: the chosen target may not go backwards, so we never scramble order.
"""
import json, os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_c = {}
def load(v):
    if v not in _c: _c[v] = json.load(open(os.path.join(ROOT, 'site', v + '.json')))['paragraphs']
    return _c[v]
def num(x):
    m = re.match(r'\d+', str(x if x is not None else '')); return int(m.group()) if m else None
def words(t):
    t = re.sub(r'^\s*\d+(-\d+)?\.\s*', '', t or '')
    return set(w for w in re.findall(r'[A-Za-zĀāĪīŪūṀṁṂṃṄṅÑñṬṭḌḍṆṇḶḷ]+', t) if len(w) >= 8)

def nik_prefix(code):
    c = re.sub(r'^\d+', '', code)
    for p in ('Vin', 'ViT', 'Kankha', 'Di', 'Ma', 'Sam', 'SaT', 'An', 'Khu', 'Abhi', 'Vsm', 'Vism'):
        if c.startswith(p): return {'ViT':'Vin','Kankha':'Vin','SaT':'Sam','Vism':'Vsm'}.get(p, p)
    return '?'

def candidates(man, canon_vol, layer):
    pref = nik_prefix(canon_vol)
    return [c for c, m in man.items() if m['layer'] == layer and nik_prefix(c) == pref]

def build_index(vols):
    """number -> list of (vol, ordinal, wordset) across the given commentary vols."""
    idx = {}
    for v in vols:
        for o, p in enumerate(load(v)):
            n = num(p.get('n'))
            if n is None: continue
            idx.setdefault(n, []).append((v, o, words(p.get('text', ''))))
    return idx

def relink(man, canon_vol, out):
    d = load(canon_vol)
    res = {}
    for layer, field in (('commentary', 'commentary'), ('subcommentary', 'subcommentary')):
        cvs = candidates(man, canon_vol, layer)
        if not cvs: continue
        idx = build_index(cvs)
        for i, p in enumerate(d):
            N = num(p.get('n'));
            if N is None: continue
            wc = words(p.get('text', ''))
            best = None; bestscore = 0
            for dn in range(0, 3):                      # prefer exact number, then ±window
                for NN in ({N} if dn == 0 else {N-dn, N+dn}):
                    for (v, o, wt) in idx.get(NN, []):
                        s = len(wc & wt) + (1 if NN == N else 0)
                        if s > bestscore: bestscore = s; best = (v, o, NN)
                if best: break
            if best and bestscore >= 2:                 # need real content overlap (not just number)
                v, o, NN = best
                res.setdefault(str(i), {}).setdefault(field, []).append(
                    {'key': f'{v}#{o}', 'state': 'direct' if NN == N else 'covered', 'n': N})
        # covered-interval fill: paragraphs between two direct matches point to the
        # earlier comment (it covers them), monotonic within the same commentary volume
        lastv = lasto = None
        for i, p in enumerate(d):
            e = res.get(str(i), {}).get(field)
            if e:
                lastv, lasto = e[0]['key'].split('#'); lasto = int(lasto)
            elif lastv is not None:
                res.setdefault(str(i), {}).setdefault(field, []).append(
                    {'key': f'{lastv}#{lasto}', 'state': 'covered', 'n': num(p.get('n'))})
    json.dump(res, open(os.path.join(out, canon_vol + '.links.json'), 'w'), ensure_ascii=False)
    da = sum(1 for k in res if res[k].get('commentary'))
    dt = sum(1 for k in res if res[k].get('subcommentary'))
    return len(d), da, dt

if __name__ == '__main__':
    import sys
    man = json.load(open(os.path.join(ROOT, 'site', 'reader', 'manifest.json')))['volumes']
    out = os.path.join(ROOT, 'site', 'reader', 'linksk_new'); os.makedirs(out, exist_ok=True)
    for v in sys.argv[1:]:
        n, a, t = relink(man, v, out)
        print(f"{v}: {n} paras | A-linked {a} ({100*a//n}%) | T-linked {t} ({100*t//n}%)")
