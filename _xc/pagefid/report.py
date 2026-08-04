# -*- coding: utf-8 -*-
"""Collate `pipeline/check_page_fidelity.py --out` into the census and the
fault taxonomy.

    python3 _xc/pagefid/report.py [CENSUSDIR]     # default _xc/pagefid/census

Prints, in order: the per-volume census; the fault classes ranked by how many
PRINTED LINES each affects, with the volumes that carry them; and the page
ranges where the corpus carries no text at all.
"""
import sys, os, json, glob, collections

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
D = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, '_xc', 'pagefid', 'census')

FAM = [
    ('Jātaka-aṭṭhakathā (7 vols)', ['36KhuA17', '37KhuA18', '38KhuA19', '39KhuA20',
                                    '40KhuA21', '41KhuA22', '42KhuA23']),
    ('Theragāthā/Therīgāthā-aṭṭhakathā', ['29KhuA10', '30KhuA11', '31KhuA12']),
    ('Apadāna-aṭṭhakathā', ['32KhuA13', '33KhuA14']),
    ('Ṭīkā (26 vols)', None),
]
TIKA = ('ViT', 'DiT', 'MaT', 'SaT', 'AnT', 'AbhiT', 'VsmT', 'KhuT')


def layer(v):
    if any(t in v for t in TIKA):
        return 'tika'
    if 'A0' in v or 'A1' in v or 'A2' in v or v.endswith('Kankha') or 'Vism' in v \
            or 'VinSg' in v:
        return 'commentary'
    return 'canon'


def main():
    rs = [json.load(open(f, encoding='utf-8')) for f in sorted(glob.glob(D + '/*.json'))]
    rs.sort(key=lambda r: r['vol'])
    if not rs:
        raise SystemExit('no census in ' + D)

    rows, agg = [], collections.Counter()
    for r in rs:
        s = r['stats']
        body = (r['printed_lines'] - s.get('edge_lines', 0) - s.get('index_lines', 0))
        miss = (s.get('absent', 0) + s.get('partial', 0)
                - s.get('edge_absent', 0) - s.get('index_absent', 0))
        d = dict(vol=r['vol'], body=body, miss=miss,
                 digit=s.get('digit_only', 0), pV=s.get('page_verse', 0),
                 vp=s.get('VERSE_AS_PROSE', 0), vh=s.get('VERSE_AS_HEADING', 0),
                 pv=s.get('PROSE_AS_VERSE', 0), pu=s.get('PROSE_AS_UDDANA', 0),
                 vok=s.get('verse_ok', 0), pok=s.get('prose_ok', 0),
                 lone=s.get('lone_display', 0),
                 edge=s.get('edge_lines', 0) + s.get('index_lines', 0),
                 pj=s.get('prose_judged', 0), gaps=r.get('gaps', []))
        rows.append(d)
        for k, v in d.items():
            if isinstance(v, int):
                agg[k] += v

    print('=' * 96)
    print('CENSUS -- 118 volumes, the corpus against the printed page')
    print('=' * 96)
    h = ('%-10s %7s %5s %6s %7s %6s %5s %6s %6s %6s'
         % ('vol', 'body', 'miss', 'digit', 'pVerse', 'VasP', '%', 'VasH', 'PasV', 'PasU'))
    print(h)
    print('-' * len(h))
    for d in rows:
        print('%-10s %7d %5d %6d %7d %6d %5.1f %6d %6d %6d'
              % (d['vol'], d['body'], d['miss'], d['digit'], d['pV'], d['vp'],
                 100.0 * d['vp'] / max(1, d['pV']), d['vh'], d['pv'], d['pu']))
    print('-' * len(h))
    print('%-10s %7d %5d %6d %7d %6d %5.1f %6d %6d %6d'
          % ('TOTAL', agg['body'], agg['miss'], agg['digit'], agg['pV'], agg['vp'],
             100.0 * agg['vp'] / max(1, agg['pV']), agg['vh'], agg['pv'], agg['pu']))
    print()
    print('printed body lines checked      %9d   (front/back matter excluded: %d)'
          % (agg['body'], agg['edge']))
    print('  the corpus does not carry     %9d   %.2f%%' % (agg['miss'], 100.0 * agg['miss'] / agg['body']))
    print('  differ only in digits         %9d   %.2f%%' % (agg['digit'], 100.0 * agg['digit'] / agg['body']))
    print('page-VERSE lines                %9d   drawn as verse %d (%.1f%%)'
          % (agg['pV'], agg['vok'], 100.0 * agg['vok'] / max(1, agg['pV'])))
    print('page-PROSE lines judged         %9d   drawn as prose %d (%.1f%%)'
          % (agg['pj'], agg['pok'], 100.0 * agg['pok'] / max(1, agg['pj'])))
    print('lone display lines, not judged  %9d' % agg['lone'])

    print()
    print('=' * 96)
    print('FAULT TAXONOMY -- ranked by printed lines affected')
    print('=' * 96)
    CLS = [
        ('1  page-PROSE set as display VERSE', 'pv',
         'running commentary prose drawn line-by-line inside a <div class="gatha">'),
        ('2  page-VERSE run together as PROSE', 'vp',
         'a printed gatha block flattened into a running paragraph'),
        ('3  page-PROSE drawn as uddana/colophon', 'pu',
         'body prose drawn centred and italic in the .uddana style'),
        ('4  page-VERSE drawn as a HEADING', 'vh',
         'a printed display line taken into sections/ or headings as a title'),
        ('5  printed text the corpus does not carry', 'miss',
         'the line\'s letters are not in the volume at all'),
    ]
    for name, key, note in CLS:
        tot = agg[key]
        top = sorted(rows, key=lambda d: -d[key])[:10]
        print('\n%-42s %8d lines  (%.1f%% of body)' % (name, tot, 100.0 * tot / agg['body']))
        print('   %s' % note)
        print('   worst: ' + ', '.join('%s %d' % (d['vol'], d[key]) for d in top if d[key]))
        for label, vols in FAM[:3]:
            n = sum(d[key] for d in rows if d['vol'] in vols)
            if n:
                print('   %-34s %7d  (%.0f%% of the class)' % (label, n, 100.0 * n / max(1, tot)))
        n = sum(d[key] for d in rows if layer(d['vol']) == 'tika')
        print('   %-34s %7d  (%.0f%% of the class)' % ('Ṭīkā layer', n, 100.0 * n / max(1, tot)))

    print()
    print('=' * 96)
    print('WHERE THE TEXT IS MISSING -- printed page ranges, half the lines or more')
    print('=' * 96)
    for d in rows:
        g = [x for x in d['gaps'] if len(x) < 4 or x[3] != 'index']
        if g:
            print('%-10s %s' % (d['vol'], '  '.join(
                ('pdf p%d-%d (%d lines)' % (x[0], x[1], x[2])) if x[1] > x[0]
                else ('pdf p%d (%d)' % (x[0], x[2])) for x in g)))
    print()
    print('(the edition\'s own word indexes, printed inside a volume that holds two')
    print(' works, are named from the page and excluded above:')
    for d in rows:
        g = [x for x in d['gaps'] if len(x) > 3 and x[3] == 'index']
        if g:
            print('   %-10s %s' % (d['vol'], '  '.join('p%d-%d' % (x[0], x[1]) for x in g)))
    print(' )')


if __name__ == '__main__':
    main()
