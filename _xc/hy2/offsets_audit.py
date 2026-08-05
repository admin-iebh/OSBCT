# -*- coding: utf-8 -*-
"""WHICH reader artefacts are keyed to character offsets into paragraphs[].text?

The migration deletes one character per vowel-branch occurrence.  Anything
holding an OFFSET into that string moves; anything holding the TEXT ITSELF must
be rewritten the same way or it stops matching.  Both are failure modes and this
distinguishes them.

Method, per artefact directory, on one volume known to carry the fault:
  * OFFSET evidence -- an integer pair [a,b] where text[a:b] is a real substring
    of the paragraph.  Confirmed by CHECKING, not by the field name.
  * TEXT evidence   -- a string value that occurs verbatim in some paragraph.

Reported per directory with a worked example, so a claim can be checked.
"""
import json, os, sys, collections

VOL = sys.argv[1] if len(sys.argv) > 1 else '09DiT02'
DIRS = ('apparatus', 'bold', 'hide', 'incipit', 'links', 'linksk',
        'booktitle', 'verse', 'uddana', 'sections', 'toc', 'xrefs', 'ord',
        'pbreak')

paras = json.load(open('site/%s.json' % VOL, encoding='utf-8'))['paragraphs']
texts = [(p.get('text') or '') for p in paras]
byn = {}
for i, p in enumerate(paras):
    byn.setdefault(str(p.get('n')), i)
    byn.setdefault(str(i), i)
alltext = '\n'.join(texts)


def para_for(key):
    i = byn.get(str(key))
    return texts[i] if i is not None else None


def probe(obj, key, out, depth=0):
    """walk; look for [int,int] pairs that slice the keyed paragraph"""
    if depth > 6:
        return
    if isinstance(obj, list):
        if (len(obj) == 2 and all(isinstance(x, int) for x in obj)
                and 0 <= obj[0] < obj[1]):
            t = para_for(key)
            if t and obj[1] <= len(t):
                s = t[obj[0]:obj[1]]
                if s.strip():
                    out['offset_pairs'] += 1
                    if len(out['ex_off']) < 2:
                        out['ex_off'].append((key, obj, s[:40]))
            return
        for x in obj:
            probe(x, key, out, depth + 1)
    elif isinstance(obj, dict):
        for x in obj.values():
            probe(x, key, out, depth + 1)
    elif isinstance(obj, str):
        if len(obj) >= 14 and obj in alltext:
            out['verbatim_strings'] += 1
            if len(out['ex_txt']) < 2:
                out['ex_txt'].append((key, obj[:52]))


print('== %s ==  %d paragraphs' % (VOL, len(paras)))
for d in DIRS:
    p = 'site/reader/' + d
    if not os.path.isdir(p):
        print('   %-11s (absent)' % d)
        continue
    f = next((x for x in sorted(os.listdir(p)) if x.startswith(VOL + '.')), None)
    if not f:
        print('   %-11s no file for this volume' % d)
        continue
    try:
        data = json.load(open(p + '/' + f, encoding='utf-8'))
    except Exception as e:
        print('   %-11s unreadable (%s)' % (d, type(e).__name__))
        continue
    out = collections.Counter()
    out['ex_off'] = []
    out['ex_txt'] = []
    if isinstance(data, dict):
        for k, v in data.items():
            probe(v, k, out)
    else:
        probe(data, None, out)
    flag = 'OFFSETS' if out['offset_pairs'] else ('text' if out['verbatim_strings'] else '-')
    print('   %-11s %-8s offset-pairs %6d   verbatim strings %6d   (%s)'
          % (d, flag, out['offset_pairs'], out['verbatim_strings'], f))
    for k, ob, s in out['ex_off']:
        print('        off  key %-6s %s -> %r' % (k, ob, s))
    for k, s in out['ex_txt']:
        print('        text key %-6s %r' % (k, s))
