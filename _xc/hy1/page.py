import sys, os
sys.path.insert(0, os.path.abspath('_xc/reseg'))
import pline
vol, pg = sys.argv[1], int(sys.argv[2])
lines = pline.stream(vol)
sel = [l for l in lines if l[0] == pg]
print('=== %s  printed PDF page %d   (%d lines) ===' % (vol, pg, len(sel)))
for l in sel:
    print('ind%-3d | %s%s' % (l[2], ' ' * l[2], l[3]))
