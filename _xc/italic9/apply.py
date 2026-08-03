# -*- coding: utf-8 -*-
"""Apply the correction to the SEVEN volumes whose rebuild the printed page
supports, by splicing the replayed emitter's ordinal into the shipped file.

Only the one changed ordinal is replaced; every other ordinal is left as its
shipped bytes (the replay proved them equal, and splicing means that is not
merely believed).  `bold/<VOL>.sect.json` is re-keyed through rekey_sect.py
whether or not it has content, so the re-keying is on the same path in use
that it is in proof.

Backups: <path>.presect
"""
import json, os, shutil, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rekey_sect import rekey, Straddle

ROOT = '/sessions/rcw-01bcgpjfpcgbdwzs1dqi2qk7/mnt/OSBCT'
FIX = [('02Vin02', '0', 3), ('06VinSg06', '0', 1), ('14SamA01', '0', 5),
       ('17AnA01', '0', 3), ('27Khu10', '151', 1), ('36Abhi08', '0', 1),
       ('38Abhi10', '0', 6)]


def words(arr):
    return sum(len(str(x.get('l', x.get('t', ''))).split()) for x in arr)


def main(write):
    tot_in = tot_out = 0
    for vol, ordk, idx in FIX:
        sp = '%s/site/reader/sections/%s.json' % (ROOT, vol)
        S = json.load(open(sp, encoding='utf-8'))
        R = json.load(open('%s/_xc/italic9/rebuilt/%s.json' % (ROOT, vol),
                           encoding='utf-8'))['sections']
        R = {str(o): a for o, a in R.items()}
        assert set(S) == set(R), vol
        moved = [k for k in S if S[k] != R[k]]
        assert moved == [ordk], '%s moved %r, expected only %s' % (vol, moved, ordk)
        wi, wo = words(S[ordk]), words(R[ordk])
        tot_in += wi; tot_out += wo
        assert wi == wo, '%s WORD STREAM NOT CONSERVED %d -> %d' % (vol, wi, wo)
        old_text = str(S[ordk][idx].get('l', ''))
        k = len(R[ordk]) - len(S[ordk]) + 1
        new_texts = [str(x.get('l', '')) for x in R[ordk][idx:idx + k]]

        bp = '%s/site/reader/bold/%s.sect.json' % (ROOT, vol)
        sect = json.load(open(bp, encoding='utf-8')) if os.path.exists(bp) else None
        nsect = None
        if sect is not None:
            nsect = rekey(sect, ordk, idx, old_text, new_texts)

        print('%-12s ord%-4s entries %d->%d  split %d->%d pieces  words %d==%d  '
              'sect.json %s'
              % (vol, ordk, len(S[ordk]), len(R[ordk]), 1, k, wi, wo,
                 ('absent' if sect is None else
                  '%d keys -> %d keys%s' % (len(sect), len(nsect),
                                            '' if sect else ' (empty)'))))
        for j, x in enumerate(R[ordk][idx:idx + k]):
            print('        %s  %s' % (x['k'], str(x['l'])[:80].replace('\n', ' | ')))
        if write:
            S[ordk] = R[ordk]
            if not os.path.exists(sp + '.presect'):
                shutil.copy(sp, sp + '.presect')
            json.dump(S, open(sp, 'w', encoding='utf-8'), ensure_ascii=False)
            if sect is not None:
                if not os.path.exists(bp + '.presect'):
                    shutil.copy(bp, bp + '.presect')
                json.dump(nsect, open(bp, 'w', encoding='utf-8'), ensure_ascii=False)
    print()
    print('WORD STREAM over all seven: %d in, %d out  %s'
          % (tot_in, tot_out, 'CONSERVED' if tot_in == tot_out else 'CHANGED'))
    print('WRITTEN' if write else 'dry run -- nothing written')


if __name__ == '__main__':
    main('--write' in sys.argv)
