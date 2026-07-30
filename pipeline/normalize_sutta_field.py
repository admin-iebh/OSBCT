#!/usr/bin/env python3
"""Normalize the per-paragraph `sutta` field within each sutta span to ONE title.

Root cause of the "two titles" the reader showed: the extractor captured page
running-headers into the `sutta` field, so a single sutta's paragraphs carry
more than one form — the bare opening-heading title on the first paragraph and,
on the following paragraphs, either the running-header form with the MN number
('Kandarakasutta' -> 'Kandarakasutta (51)') or, in a handful of cases, a
page-variant *spelling* ('Kukkuravatika' -> 'Kukkaravatika'). Any consumer that
starts a new heading when the field changes therefore prints the title twice.

This rewrites every non-'X' paragraph inside a sutta's span to the sutta's single
canonical title = the cleaned opening-heading form (matches the centred PDF
heading; verified). The base `text` is untouched — only the derived `sutta`
label is made consistent. Sutta spans are taken from the same corpus
`vagga`/`sutta` segmentation the nav builder uses, with the same dedup, and are
checked against the canonical SPEC before anything is written.
"""
import json, os, re, shutil, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_majjhima_nav import SPEC, fold, nkey, clean_label, edist, SITE

def sutta_spans(vol):
    """ordered [(canonical_title, start_ord, end_ord)] over the whole volume."""
    paras = json.load(open(SITE(vol)))['paragraphs']
    vaggas = []
    for i, p in enumerate(paras):
        vg = p.get('vagga')
        if not vg or vg == 'X': continue
        if not vaggas or vaggas[-1]['vagga'] != vg:
            vaggas.append({'vagga': vg, 'raw': []})
        s = p.get('sutta')
        if s and s != 'X':
            raw = vaggas[-1]['raw']
            if not raw or raw[-1][0] != s: raw.append((s, i))
    starts = []
    for v in vaggas:
        kept = []
        for (s, i) in v['raw']:
            k = nkey(s); dup = False
            for (_, ki, kk) in kept:
                if kk == k or (i - ki <= 4 and edist(kk, k) <= 2): dup = True; break
            if not dup: kept.append((s, i, k))
        starts += [(clean_label(s), i) for (s, i, k) in kept]
    # verify count
    exp = sum(c for _, c in SPEC[vol])
    if len(starts) != exp:
        raise SystemExit(f"REFUSED: {vol} found {len(starts)} suttas, expected {exp}")
    spans = []
    for idx, (title, s) in enumerate(starts):
        e = starts[idx + 1][1] if idx + 1 < len(starts) else len(paras)
        spans.append((title, s, e))
    return paras, spans

def main():
    total_changed = 0
    for vol in ('09Ma01', '10Ma02', '11Ma03'):
        paras, spans = sutta_spans(vol)
        changed = 0
        for title, s, e in spans:
            for i in range(s, e):
                cur = paras[i].get('sutta')
                if cur and cur != 'X' and cur != title:
                    paras[i]['sutta'] = title; changed += 1
        d = json.load(open(SITE(vol))); d['paragraphs'] = paras
        shutil.copy(SITE(vol), SITE(vol) + '.bak')
        json.dump(d, open(SITE(vol), 'w'), ensure_ascii=False)
        print(f"{vol}: normalized {changed} paragraph sutta-labels ({len(spans)} suttas); backup -> {vol}.json.bak")
        total_changed += changed
    print(f"TOTAL paragraphs relabelled: {total_changed}")

if __name__ == '__main__':
    main()
