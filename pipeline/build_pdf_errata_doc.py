#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Render docs/PDF_ERRATA.md from data/errata.json.

WHY A GENERATED DOC.  The reader asked (2026-08-08) for a document of the
errata found in the printed PDFs, "so we can correct them later".  The
register `data/errata.json` is the single source — it feeds the site's
Errata page — and a hand-written doc beside it would drift the way this
project's citation metadata drifted three times.  So the doc is RENDERED,
carries a banner saying so, and correcting course means editing the
register and re-running this.

Usage:  python3 pipeline/build_pdf_errata_doc.py
"""
import json, os, collections, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'data', 'errata.json')
OUT = os.path.join(ROOT, 'docs', 'PDF_ERRATA.md')

d = json.load(open(SRC, encoding='utf-8'))
entries = d['entries']
byvol = collections.defaultdict(list)
for e in entries:
    byvol[e['volume']].append(e)

L = []
L.append('# Errata of the printed edition, for later correction')
L.append('')
L.append('<!-- GENERATED from data/errata.json by pipeline/build_pdf_errata_doc.py')
L.append('     — edit the REGISTER, not this file, and regenerate.  The same')
L.append('     register feeds the site\'s Errata page. -->')
L.append('')
L.append('Rendered %s from a register of **%d entries**.  The corpus never'
         % (datetime.date.today().isoformat(), len(entries)))
L.append('alters these readings (working principle 3): the printed reading is')
L.append('preserved wherever the text is quoted, and every emendation below is a')
L.append('**candidate pending scholarly confirmation**.  This document exists so')
L.append('that a future corrected printing — or an errata sheet sent to the')
L.append('publisher — can be prepared from one list.')
L.append('')
L.append('| # | Volume | Printed p. | Printed reading | Suggested reading | Confidence |')
L.append('|---|--------|-----------:|-----------------|-------------------|------------|')
for vol in sorted(byvol):
    for e in sorted(byvol[vol], key=lambda x: (x.get('printed_page') or 0)):
        L.append('| %s | %s | %s | `%s` | `%s` | %s |' % (
            e['id'], vol, e.get('printed_page', '?'),
            (e.get('printed_reading') or '').replace('|', '\\|'),
            (e.get('suggested_reading') or '').replace('|', '\\|'),
            e.get('confidence', '?')))
L.append('')
L.append('## Notes per entry')
L.append('')
for vol in sorted(byvol):
    L.append('### %s' % vol)
    L.append('')
    for e in sorted(byvol[vol], key=lambda x: (x.get('printed_page') or 0)):
        note = (e.get('note') or '').strip()
        L.append('- **%s** (printed p. %s, %s): %s' % (
            e['id'], e.get('printed_page', '?'), e.get('layer', '?'), note))
    L.append('')

os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT, 'w', encoding='utf-8').write('\n'.join(L) + '\n')
vols = len(byvol)
print('wrote %s: %d entries across %d volumes' % (OUT, len(entries), vols))
