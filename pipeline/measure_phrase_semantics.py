#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MEASURE, do not build: what a phrase means on the page today (a substring
of the normalised text, single spaces) against what a position store could
decide without the text (consecutive TOKENS, each matching its query word the
way a single-word search does).

2026-09-06.  Item 2 of the third session's list — phrase positions — was
measured for COST there (+66 % on every single-word search if stored in tp/;
a separate store otherwise).  This measures the other half: whether positions
could reproduce the page's answer at all.  They cannot, in either direction:

  * text-only  — the page counts `tassa bhagavato` inside `etassa bhagavato`,
                 `sabbe saṅkhārā` inside `sabbe saṅkhārāti`, `dhamm* ti` inside
                 `adhammaṁ ti`: a phrase's first word may end a longer token
                 and its last word may begin one.  Tokens say no.
  * tokens-only — `dhammā”ti`, `kāyena, vācāya`: the tokens are consecutive
                 but the printed text puts a quote or comma between them, and
                 the page's substring wants a single space.  Tokens say yes.

So a position store is not a prefilter for the current semantic; it is a
DIFFERENT semantic.  Which one is right is the reader's decision (§0 of the
speed brief was the same kind of decision for diacritics), and this script is
the ground truth for either: run it, read the two columns.

Both columns resolve a bare word to its EXACT key only (the page does the
same when the key exists; the substring sweep for a word that is no key is
not modelled here) and a wildcard to every key matching its pattern.

Usage:  python3 pipeline/measure_phrase_semantics.py "evaṁ me sutaṁ" "dhamm* ti" …
"""
import json,re,unicodedata,os,sys,glob,collections
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
canon=lambda s:unicodedata.normalize('NFC',s or '').lower().replace('ṃ','ṁ')
TOK=re.compile(r'[^a-zāīūṁṃṅñṇṭḍḷ]+',re.I)
man=json.load(open(ROOT+'/site/index/tp/index.json'))
vols=man['vols']
paras={}
for v in vols:
    P=[]
    for f in sorted(glob.glob(ROOT+'/site/index/tx/%s/*.json'%v),key=lambda x:int(os.path.basename(x)[:-5])):
        P+=json.load(open(f))['paras']
    paras[v]=[canon(p['text']) for p in P]
print('loaded',sum(len(x) for x in paras.values()),'paragraphs',file=sys.stderr)
def rxesc(s): return re.escape(s)
def wpat(w): return r'\S*'.join(rxesc(x) for x in w.split('*')) if '*' in w else rxesc(w)
def kpat(w): return '^'+'.*'.join(rxesc(x) for x in w.split('*'))+'$'
phrases=sys.argv[1:]
for ph in phrases:
    words=canon(ph).split()
    # text semantic (the page's): candidates = paragraphs where every word has a matching TOKEN (key), then substring/regex on text
    krx=[re.compile(kpat(w)) if '*' in w else None for w in words]
    phrx=re.compile(' '.join(wpat(w) for w in words))
    tp=to=tap=0  # text: phrase paras, occurrences, and-only
    pp=po=pap=0  # positions: token adjacency
    both=onlyT=onlyP=0
    for v in vols:
        for t in paras[v]:
            toks=[x for x in TOK.split(t) if x]
            # word i matches token? exact key or wildcard regex (bare word: exact key only — the page resolves an existing key to itself; if no key exists it sweeps substrings, ignored here)
            match=[[ (krx[i].match(x) is not None) if krx[i] else (x==words[i]) for x in toks] for i in range(len(words))]
            if not all(any(m) for m in match): continue
            # text
            c=len(phrx.findall(t))
            # positions
            n=0
            for j in range(len(toks)-len(words)+1):
                if all(match[i][j+i] for i in range(len(words))): n+=1
            if c: tp+=1; to+=c
            else: tap+=1
            if n: pp+=1; po+=n
            else: pap+=1
            if c and n: both+=1
            elif c: onlyT+=1
            elif n: onlyP+=1
    print('%-22s text: %5d paras %5d occ, and-only %5d | tokens: %5d paras %5d occ, and-only %5d | both %5d text-only %5d tokens-only %5d'%(ph,tp,to,tap,pp,po,pap,both,onlyT,onlyP))
