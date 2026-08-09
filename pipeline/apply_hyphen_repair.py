#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""THE VOWEL-BRANCH HYPHEN REPAIR, corpus-wide, as ONE operation.

Session 2 of the repair hy2/FINDINGS records: §2 classified, §11 built and
proved the migration, §11.3 reverted it on the builder blocker, §11.6 broke
the blocker (the run placer's third join candidate, shipped fd2c24f0, proved
byte-identical on unmigrated text and exact on the migrated pilot).

THIS SCRIPT IS _xc/hy2/migrate.py's LOGIC CARRIED VERBATIM — the BAD/PEY
regexes, holes/shift, the per-volume bold key convention with NO fallback
(the 50AbhiA03 lesson), the span-content control — PLUS THE DIMENSION THE
08-05 AUDIT COULD NOT SEE because it did not exist yet:

  !!! pbreak/<VOL>.json CARRIES CHARACTER OFFSETS INTO paragraphs[].text.
  migrate.py's docstring says "pbreak/ ... no offsets" and that was TRUE ON
  2026-08-05; the offset-bearing pbreak (rawOffset, the notes-at-page-foot
  address space) was derived 2026-08-08 (_xc/pagemark/derive.py).  Running
  the old migration today would silently strand every page cut in a
  migrated paragraph up to 210 characters late.

  Entry shape [rawOffset, printed, pdfPage, drawnIndex?, drawnOffset?]:
  rawOffset SHIFTS (it addresses the text this script edits); -1 and 0 are
  sentinels and are left; drawnIndex/drawnOffset address the DRAWN printed
  lines, which this script does not touch, and are left.

CONTROLS, all fatal, all run in the dry run:
  * every bold span's selected substring identical before/after (minus an
    inside-span deleted space, counted separately);
  * every shifted rawOffset still points at THE SAME CHARACTER:
    old_text[old] == new_text[new];
  * a volume whose bold key convention cannot be decided is skipped WHOLE —
    text, bold and pbreak together, never desynced.

Usage:  python3 pipeline/apply_hyphen_repair.py [VOL ...] [--write]
"""
import json, os, re, sys, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

BAD = re.compile(r'(?<=[a-zāīūṁṃṅñṭḍṇḷ])- (?=[aāiīuūeoAĀIĪUŪEO])')
PEY = re.compile(r'-(?:pa|pe|la)- ')
WRITE = '--write' in sys.argv
ONLY = [a for a in sys.argv[1:] if not a.startswith('--')]


def holes(t):
    return [m.start() + 1 for m in BAD.finditer(PEY.sub('#####', t))]


def shift(off, hs):
    return off - sum(1 for h in hs if h < off)


def bold_convention(bold, paras):
    byidx = {str(i): (p.get('text') or '') for i, p in enumerate(paras)}
    byn = {str(p.get('n')): (p.get('text') or '') for p in paras}

    def score(m):
        ok = tot = 0
        for k, sp in list(bold.items())[:500]:
            t = m.get(k)
            if t is None:
                continue
            for a, b in sp:
                tot += 1
                s = t[a:b]
                if s and s == s.strip():
                    ok += 1
        return ok, tot
    oi, ti = score(byidx)
    on, tn = score(byn)
    if ti and oi / ti >= 0.95 and (not tn or oi / ti > on / max(1, tn)):
        return 'index'
    if tn and on / tn >= 0.95:
        return 'n'
    return None


def main():
    vols = ONLY or sorted(f[:-5] for f in os.listdir('site') if f.endswith('.json'))
    tot = collections.Counter()
    skipped = []
    for vol in vols:
        sp = 'site/%s.json' % vol
        try:
            d = json.load(open(sp, encoding='utf-8'))
        except Exception:
            continue
        if not isinstance(d, dict) or 'paragraphs' not in d:
            continue
        paras = d['paragraphs']
        bp = 'site/reader/bold/%s.bold.json' % vol
        bold = json.load(open(bp, encoding='utf-8')) if os.path.exists(bp) else {}
        pp = 'site/reader/pbreak/%s.json' % vol
        pbrk = json.load(open(pp, encoding='utf-8')) if os.path.exists(pp) else {}
        conv = bold_convention(bold, paras) if bold else None
        if bold and conv is None:
            print('%-10s *** BOLD KEY CONVENTION UNDECIDED -- SKIPPING VOLUME' % vol)
            skipped.append(vol)
            continue
        st = collections.Counter()
        newtexts = {}
        allholes = {}
        newbold = {}
        for i, p in enumerate(paras):
            t = (p.get('text') or '')
            hs = holes(t)
            allholes[i] = hs
            if not hs:
                continue
            st['paragraphs'] += 1
            st['deletions'] += len(hs)
            nt = ''.join(c for j, c in enumerate(t) if j not in set(hs))
            newtexts[i] = nt
            k = (str(i) if conv == 'index' else
                 str(p.get('n')) if conv == 'n' else None)
            if k is not None and k in bold:
                out = []
                for a, b in bold[k]:
                    na, nb = shift(a, hs), shift(b, hs)
                    st['spans'] += 1
                    if nb != b or na != a:
                        st['spans_shifted'] += 1
                    inside = [h for h in hs if a <= h < b]
                    want = ''.join(c for j, c in enumerate(t[a:b])
                                   if (j + a) not in set(inside))
                    if nt[na:nb] != want:
                        st['SPAN CONTENT CHANGED'] += 1
                        if st['SPAN CONTENT CHANGED'] <= 3:
                            print('   !! %s ord %s  %r -> %r (wanted %r)'
                                  % (vol, k, t[a:b][:40], nt[na:nb][:40], want[:40]))
                    elif inside:
                        st['span_lost_an_inner_space'] += 1
                    out.append([na, nb])
                newbold[k] = out
        # ---- pbreak rawOffsets, the dimension migrate.py predates ----
        newpbrk = {}
        for ok_, rows in pbrk.items():
            try:
                oi_ = int(ok_)
            except Exception:
                newpbrk[ok_] = rows
                continue
            hs = allholes.get(oi_, [])
            if not hs:
                newpbrk[ok_] = rows
                continue
            t = (paras[oi_].get('text') or '')
            nt = newtexts.get(oi_, t)
            out = []
            for row in rows:
                row = list(row)
                off = row[0]
                if isinstance(off, int) and off > 0:
                    noff = shift(off, hs)
                    st['pbreak_offsets'] += 1
                    if noff != off:
                        st['pbreak_shifted'] += 1
                    if off < len(t) and (noff >= len(nt) or t[off] != nt[noff]):
                        st['PBREAK ANCHOR MOVED'] += 1
                        if st['PBREAK ANCHOR MOVED'] <= 3:
                            print('   !! %s pbreak ord %s off %d->%d  %r vs %r'
                                  % (vol, ok_, off, noff,
                                     t[off:off + 12], nt[noff:noff + 12]))
                    row[0] = noff
                out.append(row)
            newpbrk[ok_] = out
        if not st['deletions']:
            continue
        tot.update(st)
        print('%-10s paras %4d  del %5d  spans %6d/%6d  pbreak %4d/%4d  content-chg %d  anchor-moved %d'
              % (vol, st['paragraphs'], st['deletions'], st['spans_shifted'],
                 st['spans'], st['pbreak_shifted'], st['pbreak_offsets'],
                 st['SPAN CONTENT CHANGED'], st['PBREAK ANCHOR MOVED']))
        if WRITE:
            if st['SPAN CONTENT CHANGED'] or st['PBREAK ANCHOR MOVED']:
                print('   REFUSING TO WRITE %s: a control failed above' % vol)
                skipped.append(vol)
                continue
            for i, nt in newtexts.items():
                paras[i]['text'] = nt
            json.dump(d, open(sp, 'w', encoding='utf-8'), ensure_ascii=False)
            if newbold:
                bold.update(newbold)
                json.dump(bold, open(bp, 'w', encoding='utf-8'), ensure_ascii=False)
            if pbrk:
                json.dump(newpbrk, open(pp, 'w', encoding='utf-8'), ensure_ascii=False)
    print()
    print('%s  paragraphs %d  deletions %d  spans %d/%d  pbreak %d/%d  '
          'CONTENT CHANGED %d  ANCHOR MOVED %d  skipped %s'
          % ('WROTE' if WRITE else 'DRY RUN', tot['paragraphs'], tot['deletions'],
             tot['spans_shifted'], tot['spans'], tot['pbreak_shifted'],
             tot['pbreak_offsets'], tot['SPAN CONTENT CHANGED'],
             tot['PBREAK ANCHOR MOVED'], skipped or 'none'))


if __name__ == '__main__':
    main()
