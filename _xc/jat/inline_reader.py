# -*- coding: utf-8 -*-
"""jsdom does NOT fetch <script src>.  Build a copy of reader2.html with i18n.js
and panel.js INLINED, for `check_layout.js` to boot via OSBCT_READER -- without
which the proof runs against a reader missing two scripts."""
import io, os, re
R = '/sessions/rcw-01bcgpjfpcgbdwzs1dqi2qk7/mnt/OSBCT/site'
h = io.open(R + '/reader/reader2.html', encoding='utf-8').read()
n = 0
for tag, src in re.findall(r'(<script src="([^"]+)"[^>]*></script>)', h):
    p = src.split('?')[0]
    f = os.path.join(R, p[3:]) if p.startswith('../') else os.path.join(R, 'reader', p)
    js = io.open(f, encoding='utf-8').read()
    h = h.replace(tag, '<script>\n' + js + '\n</script>')
    n += 1
    print('inlined', f, len(js))
io.open(R + '/reader/_reader2_inlined.html', 'w', encoding='utf-8').write(h)
print('wrote site/reader/_reader2_inlined.html, %d scripts inlined' % n)
