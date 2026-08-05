"""For every printed line that ends in a line-break hyphen AND is judged
page-verse, what does the NEXT printed line look like?

The claim under test (08-04 doc §6.2) is 'a pada never ends mid-word'.  If that
is true universally, no hyphen line should ever be page-verse.  If it is true
only of a run's LAST line, then the ones that matter are those whose
continuation falls OUTSIDE the display run -- next line page-prose."""
import sys, os, json, collections
sys.path.insert(0, os.path.abspath('pipeline'))
import check_page_fidelity as cpf

vols = sys.argv[1:]
run_end, run_mid, out = [], [], {}
for v in vols:
    r = cpf.run(v, verbose=True)
    rows = r['rows']
    # rows come back in emission order; reorder by (pdf_page, printed order)
    for i, x in enumerate(rows):
        if not (x[6] or '').rstrip().endswith('-'):
            continue
        if x[3] != 'verse':
            continue
        nxt = rows[i + 1] if i + 1 < len(rows) else None
        rec = [v, x[0], x[1], x[5], x[6][:70],
               (nxt[3] if nxt else None), (nxt[1] if nxt else None),
               (nxt[6][:60] if nxt else None)]
        (run_end if (nxt and nxt[3] == 'prose') else run_mid).append(rec)
print('page-verse hyphen lines: %d' % (len(run_end) + len(run_mid)))
print('  continuation is page-PROSE  (run ENDS mid-word) : %d' % len(run_end))
print('  continuation is page-VERSE  (run continues)     : %d' % len(run_mid))
print()
print('--- RUN ENDS mid-word (the §6.2 shape) ---')
for x in run_end:
    print('  %-10s p%-4d ind=%-3d %-16s %s' % (x[0], x[1], x[2], x[3], x[4]))
    print('  %-10s      ind=%-3s -> %-13s %s' % ('', x[6], x[5], x[7]))
print()
print('--- run CONTINUES (genuine hyphenated pada?) ---')
for x in run_mid[:25]:
    print('  %-10s p%-4d ind=%-3d %-16s %s' % (x[0], x[1], x[2], x[3], x[4]))
    print('  %-10s      ind=%-3s -> %-13s %s' % ('', x[6], x[5], x[7]))
