#!/usr/bin/env python3
"""Render proximity_sample.json as a readable sheet for hand judgement."""
import json, os, sys, re

ROOT = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(ROOT, 'proximity_sample.json')))
lo = int(sys.argv[1]) if len(sys.argv) > 1 else 0
hi = int(sys.argv[2]) if len(sys.argv) > 2 else len(d['judge'])


def around(text, word, span=340):
    i = text.lower().find(word.lower())
    if i < 0:
        return text[:span]
    a = max(0, i - span // 2)
    b = min(len(text), i + len(word) + span // 2)
    s = text[a:b]
    return ('…' if a else '') + s + ('…' if b < len(text) else '')


for k, j in enumerate(d['judge'][lo:hi], start=lo):
    print(f'--- #{k}  [{j["band"]}]  {j["word"]}  ({j["n_rows"]} rows, '
          f'{j["n_prox"]} proximity)  {j["vol"]} §{j["para"]} p.{j["printed"]} — {j["sutta"]}')
    print(f'CANON  {around(j["canon"], j["word"])}')
    for r in j['prox']:
        print(f'PROX   [{r["v"]} §{r["n"]}] {r["l"]} — {r["g"]}')
    for r in j['others']:
        print(f'other  [{r["v"]} §{r["n"]}] {r["l"]} — {r["g"][:150]}')
    print()
