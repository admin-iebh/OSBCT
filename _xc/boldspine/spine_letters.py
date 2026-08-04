# Corpus-wide spine/band bold LETTERS under the gate's own model, before and
# after.  Corpus side only -- no PDF -- so it runs over all 118 volumes in
# seconds and can be compared straight against the recorded census.
import sys,os,json,glob
sys.path.insert(0,'pipeline')
import check_bold_fidelity as B
tot={'spine':0,'band':0}; per={}
for f in sorted(glob.glob('site/reader/bold/*.bold.json')):
    vol=os.path.basename(f)[:-10]
    M=B.corpus_bold(vol)
    if not M: continue
    s,b=sum(M['SPINE']),sum(M['BAND'])
    per[vol]=[s,b]; tot['spine']+=s; tot['band']+=b
json.dump(per,open('_xc/boldspine/spine_letters.json','w'))
print('volumes',len(per),'spine_bold_letters',tot['spine'],'band_bold_letters',tot['band'])
for v in ['20KhuA01','19AnA03','07DiA01','21KhuA02','52Vism02']:
    print(' ',v,per.get(v))
