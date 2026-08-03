#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""THE COMMENTARY SAYS WHICH SUTTA IT IS COMMENTING ON. READ IT.

A commentary paragraph opens by naming its own position in the vagga in words:

    113. Sattame adhammacariyāti...          "in the seventh"
    107. Ekādasamassa paṭhame asubhāti...    "of the eleventh, in the first"

This module only EXTRACTS that statement.  It decides nothing and writes
nothing.  What the statement is worth was measured before anything was built on
it -- see `pipeline/check_ordinal.py` and
`claude/the_commentary_states_its_own_position.md`.

WHAT IT IS NOT.  The ordinal names a position WITHIN A VAGGA.  It therefore
cannot see a link that is wrong by whole vaggas: two regions ten suttas apart
line up position-for-position, and measurement confirmed the coincidence is
real.  The section NAME sees that fault; this sees the one the name cannot,
where no name is printed.  They are complementary detectors, not rivals.
"""
import re, unicodedata

# locative singular -- "in the Nth".  Variants are the edition's, not invented:
# both spellings occur in the printed text.
LOC = {
    'paṭhame':1,'dutiye':2,'tatiye':3,'catutthe':4,'pañcame':5,'chaṭṭhe':6,
    'sattame':7,'aṭṭhame':8,'navame':9,'dasame':10,'ekādasame':11,
    'dvādasame':12,'bārasame':12,'terasame':13,'telasame':13,'teḷasame':13,
    'cuddasame':14,'catuddasame':14,'coddasame':14,
    'pannarasame':15,'paṇṇarasame':15,'pañcadasame':15,
    'soḷasame':16,'sattarasame':17,'sattadasame':17,
    'aṭṭhārasame':18,'aṭṭhadasame':18,'ekūnavīsatime':19,'ūnavīsatime':19,
    'vīsatime':20,'vīsame':20,'ekavīsatime':21,'bāvīsatime':22,'dvāvīsatime':22,
    'tevīsatime':23,'catuvīsatime':24,'pañcavīsatime':25,'chabbīsatime':26,
    'sattavīsatime':27,'aṭṭhavīsatime':28,'ekūnatiṁsatime':29,'tiṁsatime':30,
}
GEN = {w[:-1] + 'assa': v for w, v in LOC.items()}   # paṭhame -> paṭhamassa

# leading printed number(s): "113. ", "5-6. ", "(12) 1. "
LEAD = re.compile(r'^[\s\d().,\-–—]*')
WORD = re.compile(r'^([A-Za-zĀāĪīŪūṀṁṂṃṄṅÑñṬṭḌḍṆṇḶḷ]+)')


def _words(text, k=4):
    s = LEAD.sub('', text or '')
    out = []
    for _ in range(k):
        m = WORD.match(s)
        if not m:
            break
        out.append(m.group(1))
        s = s[m.end():].lstrip('  ')
        # a following 'ti / -ti quotation mark ends the opening formula
        if s[:1] in ('“', '"'):
            break
    return out


def read(text):
    """Return (ordinal, genitive, matched_form) or (None, None, None).

    `ordinal`  -- position of this sutta within its vagga, stated in the
                  locative.  This is the signal.
    `genitive` -- ordinal of the containing unit, when stated.  Recorded but
                  NOT used as a key: the level it names varies (vagga within
                  paṇṇāsaka, or paṇṇāsaka itself) and that has not been
                  established.
    """
    ws = _words(text)
    if not ws:
        return (None, None, None)
    gen = None
    for i, w in enumerate(ws[:2]):
        lw = w.lower()
        if lw in LOC:
            return (LOC[lw], gen, w)
        if i == 0 and lw in GEN:
            gen = GEN[lw]
            continue
        if i == 0 and lw.endswith('assa'):
            gen = 0          # a named unit, e.g. Pañcakanipātassa
            continue
        break
    return (None, gen, None)
