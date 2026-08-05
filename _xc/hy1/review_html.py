# -*- coding: utf-8 -*-
import json, html, collections

items = json.load(open('_xc/hy1/review.json', encoding='utf-8'))
by_vol = collections.defaultdict(list)
for c in items:
    by_vol[c['vol']].append(c)

H = []
A = H.append
A('''<!doctype html><meta charset="utf-8">
<title>67 hyphen lines the page-side classifier calls verse</title>
<style>
:root{color-scheme:light}
body{background:#fbfaf7;color:#1d1c1a;font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
     max-width:1080px;margin:0 auto;padding:32px 28px 120px}
h1{font-size:24px;margin:0 0 6px;letter-spacing:-.01em}
h2{font-size:15px;margin:38px 0 10px;padding-bottom:6px;border-bottom:1px solid #ddd9d0;
   font-family:ui-monospace,SFMono-Regular,Menlo,monospace;color:#6b4f1d}
.lede{color:#4a4740;margin:0 0 22px;font-size:14.5px}
.lede b{color:#1d1c1a}
.key{background:#fff;border:1px solid #e2ded4;border-radius:7px;padding:14px 16px;margin:0 0 26px;font-size:13.5px}
.key div{margin:5px 0}
.case{background:#fff;border:1px solid #e2ded4;border-radius:7px;margin:0 0 14px;overflow:hidden}
.hd{display:flex;gap:14px;align-items:baseline;padding:9px 14px;background:#f4f1ea;
    border-bottom:1px solid #e2ded4;font-size:12.5px;font-family:ui-monospace,Menlo,monospace}
.hd .pg{font-weight:600;color:#1d1c1a}
.hd .vd{margin-left:auto;color:#6b6558}
.vd.bad{color:#9a3412;font-weight:600}
pre{margin:0;padding:12px 14px 14px;font:13px/1.62 ui-monospace,SFMono-Regular,Menlo,monospace;
    white-space:pre-wrap;word-break:break-word;overflow-wrap:anywhere}
.ind{color:#b8b2a4;user-select:none}
.hit{background:#fff2c9;display:block;border-left:3px solid #d69e2e;margin-left:-14px;padding-left:11px}
.cont{background:#eaf3fb;display:block;border-left:3px solid #6aa3d5;margin-left:-14px;padding-left:11px}
.toc{font-size:13px;columns:4;margin:0 0 8px}
.toc a{color:#6b4f1d;text-decoration:none;font-family:ui-monospace,Menlo,monospace}
.toc a:hover{text-decoration:underline}
</style>''')
A('<h1>67 hyphen lines the page-side classifier calls verse</h1>')
A('''<p class=lede>Every printed line below ends in a <b>mid-word hyphen</b> &mdash; its word finishes on
the next line &mdash; and <code>check_page_fidelity</code>&rsquo;s page side judges it <b>verse</b>.
The peyy&#257;la <code>-pa-</code> / <code>-pe-</code> / <code>-la-</code> lines are excluded: those are complete
tokens, not word breaks, and <code>hyjoin</code> already knows them.</p>''')
A('''<div class=key>
<div><b>The question for each:</b> is the highlighted line part of a stanza, or is it prose?</div>
<div><span style="background:#fff2c9;border-left:3px solid #d69e2e;padding:1px 6px">the hyphen line</span>
 &nbsp; <span style="background:#eaf3fb;border-left:3px solid #6aa3d5;padding:1px 6px">its continuation</span></div>
<div style="margin-top:9px;color:#4a4740"><b>Verse</b> &rarr; the classifier is right, and the edition
really does break a compound across a p&#257;da. Nothing to do.</div>
<div style="color:#4a4740"><b>Prose</b> &rarr; the classifier is wrong, as it is on
<code>12DiT05</code> p300, and the line is one of a stack of short glosses at the paragraph
indent that only <i>looks</i> like p&#257;das. That is a class&#8209;1 fault.</div>
<div style="margin-top:9px;color:#6b6558">The indent at the left is the edition&rsquo;s own leading-space
count, which is how this edition encodes structure. Page numbers are pdftotext <code>\\f</code> indices,
so they open directly in the PDF.</div>
</div>''')

A('<div class=toc>')
for vol in sorted(by_vol):
    A('<a href="#%s">%s&nbsp;(%d)</a><br>' % (vol, vol, len(by_vol[vol])))
A('</div>')

for vol in sorted(by_vol):
    A('<h2 id="%s">%s &mdash; %d</h2>' % (vol, vol, len(by_vol[vol])))
    for c in by_vol[vol]:
        bad = '' if c['verdict'] in ('verse_ok',) else ' bad'
        A('<div class=case><div class=hd><span class=pg>PDF p%d</span>'
          '<span>indent %d</span><span class="vd%s">%s</span></div><pre>'
          % (c['pg'], c['ind'], bad, html.escape(c['verdict'])))
        for ind, text, is_hit, is_cont in c['ctx']:
            cls = 'hit' if is_hit else ('cont' if is_cont else '')
            line = ('<span class=ind>%3d</span>  %s%s'
                    % (ind, '&nbsp;' * ind, html.escape(text)))
            A('<span class="%s">%s</span>' % (cls, line) if cls else line)
        A('</pre></div>')

open('_xc/hy1/review.html', 'w', encoding='utf-8').write('\n'.join(H))
print('wrote _xc/hy1/review.html  (%d cases, %d volumes)' % (len(items), len(by_vol)))
