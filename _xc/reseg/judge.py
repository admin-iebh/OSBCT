import os,sys,json,re,subprocess,collections
ROOT=os.path.abspath('.')
def run(lo,hi):
    env=dict(os.environ,OLO=str(lo),OHI=str(hi),MODE='indent',WRITE='1',
             OUT='_xc/reseg/_tmp_%d_%d.json'%(lo,hi))
    subprocess.run([sys.executable,'_xc/reseg/reseg.py'],env=env,capture_output=True)
    return json.load(open('_xc/reseg/20KhuA01.json',encoding='utf-8'))['paragraphs']
for lo,hi in ((3,5),(3,6)):
    ps=run(lo,hi)
    ends=collections.Counter(); bad=[]
    for i in range(1,len(ps)):
        t=(ps[i-1]['text'] or '').rstrip()
        e=t[-1] if t else ''
        ends[e]+=1
        if e not in '.?!–-—:':
            bad.append((ps[i-1]['pdf_page'],t[-55:],(ps[i]['text'] or '')[:55]))
    print('band %d-%d  paras %d'%(lo,hi,len(ps)))
    print('   last char of the preceding ¶:',ends.most_common(8))
    print('   breaks NOT after a sentence end: %d (%.1f%%)'%(len(bad),100*len(bad)/(len(ps)-1)))
    for x in bad[:6]: print('      p%-4d ...%s  ||  %s'%x)
    print()
