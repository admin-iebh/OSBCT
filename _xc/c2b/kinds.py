# -*- coding: utf-8 -*-
"""Dump kat_items' per-line classification for a page range, with indents."""
import sys, os
sys.path.insert(0,'pipeline')
import build_khu_volume as B
vol=sys.argv[1]; a=int(sys.argv[2]); b=int(sys.argv[3])
B.use(vol)
pages=B.pdf_pages()
bk=B.BOOKS[0]
p0,p1=bk[1],bk[2]
body0=B.kat_book_body(pages,p0,p1)
print('book',bk[0],p0,p1,'body0=',body0)
# replicate the per-page part of kat_items by instrumenting
items=B.kat_items(pages,p0,p1)
# crude: re-run classification for the page range only via monkey view
for pg in range(a,b+1):
    lines=B.join_floating(B.page_lines(pages,pg))
    numcol,body,hang=B._kat_cols(lines,body0)
    print('--- pdf p%d  numcol=%s body=%s hang=%s' % (pg,numcol,body,hang))
    for i,t in lines:
        print('   %3d | %s' % (i,t[:100]))
