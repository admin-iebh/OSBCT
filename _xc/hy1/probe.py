import json, os, sys, io, importlib.util
ROOT='/sessions/quirky-fervent-wright/mnt/OSBCT'
spec = importlib.util.spec_from_file_location('va', ROOT+'/pipeline/verify_all_volumes.py')
va = importlib.util.module_from_spec(spec); spec.loader.exec_module(va)
vr = va.vr
out={}
for vol in ('46KhuA27','12DiT05'):
    p0,p1,n = va.page_range(vol)
    buf=io.StringIO(); old=sys.stdout; sys.stdout=buf
    try: fl,fc,rv,dp = vr.verify(vol,p0,p1,0,n,4,quiet=True)
    finally: sys.stdout=old
    print('==',vol,'pages',p0,p1,'ords',n,' lines',len(fl),'chunks',len(fc),'rev',len(rv),'dup',len(dp))
    print('  -- REVERSE misses --')
    for o,k,x,y,c in rv:
        print('   ord%-6s [%s] stops at word %d/%d' % (o,k,x,y))
        print('      %s' % c[:240].replace('\n',' | '))
    print('  -- FORWARD line misses --')
    for l in fl[:10]: print('     %s' % str(l)[:200])
    print('  -- FORWARD chunk misses --')
    for l in fc[:10]: print('     %s' % str(l)[:200])
    print()
