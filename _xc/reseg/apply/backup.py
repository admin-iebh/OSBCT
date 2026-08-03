import os, shutil, sys
ROOT='/sessions/rcw-01bcgpjfpcgbdwzs1dqi2qk7/mnt/OSBCT'
FILES=[
 'site/20KhuA01.json',
 'site/reader/bold/20KhuA01.bold.json',
 'site/reader/verse/20KhuA01.json',
 'site/reader/uddana/20KhuA01.json',
 'site/reader/hide/20KhuA01.json',
 'site/reader/sections/20KhuA01.json',
 'site/reader/incipit/20KhuA01.json',
 'site/reader/booktitle/20KhuA01.json',
 'site/reader/ord/20KhuA01.json',
 'site/reader/xrefs/20KhuA01.json',
 'site/reader/apparatus/20KhuA01.app.json',
 'site/reader/apparatus/20KhuA01.appk.json',
 'site/reader/linksk/20KhuA01.rev.json',
 'site/reader/links/20KhuA01.rev.json',
 'site/reader/linksk/18Khu01.links.json',
 'site/reader/linksk/19Khu02.links.json',
 'site/reader/linksk/22Khu05.links.json',
 'site/reader/linksk/23Khu06.links.json',
 'site/reader/linksk/25Khu08.links.json',
 'site/reader/linksk/26Khu09.links.json',
 'site/reader/linksk/27Khu10.links.json',
 'site/reader/nav.json',
 'site/index/20KhuA01.idx.json',
 'site/index/terms.compact.json',
 'site/reader/pageindex.json',
 'site/reader/pagespan.json',
 'site/build.json',
 'site/reader/reader2.html',
 'site/reader/reader.html',
 'site/search.html',
 'site/errata.html',
 'site/downloads.html',
 'site/about.html',
 'site/index.html',
 'site/demo-links.html',
 'pipeline/links_baseline.json',
 'pipeline/ordinal_baseline.json',
 'pipeline/concordance_baseline.json',
]
made=[]; missing=[]; already=[]
for f in FILES:
    p=os.path.join(ROOT,f)
    if not os.path.exists(p): missing.append(f); continue
    b=p+'.prereseg'
    if os.path.exists(b): already.append(f); continue
    if len(sys.argv)>1 and sys.argv[1]=='--write':
        shutil.copy2(p,b)
    made.append(f)
print('WOULD BACK UP' if len(sys.argv)<2 else 'BACKED UP', len(made))
for f in made: print('  ', f+'.prereseg')
if already: print('ALREADY PRESENT:', already)
if missing: print('MISSING (not backed up):', missing)
