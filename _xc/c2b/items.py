import sys
sys.path.insert(0,'pipeline')
import build_khu_volume as B
vol=sys.argv[1]; a=int(sys.argv[2]); b=int(sys.argv[3])
B.use(vol); pages=B.pdf_pages(); bk=B.BOOKS[0]
items=B.kat_items(pages,bk[1],bk[2])
for it in items:
    pg = it[-1]
    if a<=pg<=b:
        print('%-7s p%-4s %s' % (it[0], pg, (it[2] if it[0]=='unit' else it[1])[:90]))
