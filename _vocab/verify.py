#!/usr/bin/env python3
"""Independent recount of the headline figures, by a different code path.

tokenise.py walks the string character by character. This walks it with a
regular expression. If the two disagree on a single token, one of them is
wrong and the measurement is not evidence.
"""
import json, re, os, collections

ROOT = os.path.dirname(os.path.abspath(__file__))
MAN = json.load(open(os.path.join(ROOT, 'manifest.json')))['volumes']

P = 'aāiīuūeokgṅcjñṭḍṇtdnpbmyrlvshḷṁ'
P = P + P.upper()
MARK = re.compile(r'([a-zāīūṁṅñṭḍṇḷ])(\d{1,2})\b')
DIGITS = re.compile(r'\d+')
# hyphen and elision-apostrophe are word-internal only when flanked by letters
TOK_SPLIT = re.compile(f'[{P}]+(?:[’\'][{P}]+)*')
TOK_JOIN = re.compile(f'[{P}]+(?:[-’\'][{P}]+)*')


def toks(t, joined):
    t = DIGITS.sub(' ', MARK.sub(r'\1', t))
    return (TOK_JOIN if joined else TOK_SPLIT).findall(t)


def main():
    fj = collections.Counter()
    fs = collections.Counter()
    per_layer = collections.defaultdict(collections.Counter)
    nhidden = 0
    for vol in sorted(MAN):
        layer = MAN[vol]['layer']
        d = json.load(open(os.path.join(ROOT, 'vol', vol + '.json')))
        hp = os.path.join(ROOT, 'hide', vol + '.json')
        hide = {int(k) for k in json.load(open(hp))} if os.path.exists(hp) else set()
        for i, p in enumerate(d['paragraphs']):
            if i in hide:
                nhidden += 1
                continue
            for w in toks(p['text'], True):
                fj[w.lower()] += 1
            for w in toks(p['text'], False):
                fs[w.lower()] += 1
                per_layer[layer][w.lower()] += 1
    ok = True
    for name, ctr in [('freq_join', fj), ('freq_split', fs)]:
        other = collections.Counter(json.load(open(os.path.join(ROOT, name + '.json'))))
        same = (ctr == other)
        ok &= same
        print(f'{name}: recount tokens={sum(ctr.values()):,} types={len(ctr):,}  '
              f'original tokens={sum(other.values()):,} types={len(other):,}  '
              f'IDENTICAL={same}')
        if not same:
            diff = [(w, ctr[w], other[w]) for w in set(ctr) | set(other)
                    if ctr[w] != other[w]]
            print('  first disagreements:', diff[:10], '... total', len(diff))
    print('hidden paragraphs skipped:', nhidden)
    print('VERIFY', 'PASS' if ok else 'FAIL')


if __name__ == '__main__':
    main()
