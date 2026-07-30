"""11-volume regression for build_khu_volume.py.

19Khu02-23Khu06 are compared BUILDER-vs-BUILDER against
pipeline/build_khu_volume.py.preniddesa (the shipped sections file for 19Khu02
differs from builder output by the 36 Guttilavimāna demotions the nav builder
makes afterwards, so builder-vs-shipped reads as a false failure there).
24Khu07/25Khu08/26Khu09/27Khu10 are compared BUILDER-vs-SHIPPED.
"""
import importlib.util, json, os, sys, shutil
from importlib.machinery import SourceFileLoader

# ROOT WAS A HARDCODED SESSION PATH, and this script lived in /tmp — which is
# scratch, and the session directory changes every session, so the essential
# regression was one `rm -rf` away from being lost and would have failed with a
# path error before that.  Now it derives from this file's own location and the
# snapshots live beside it under `_regress/` inside the repo.
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SNAP=os.path.join(ROOT,'_regress')
MAPS=('verse','sections','uddana','hide','incipit')
BUILDER=('19Khu02','20Khu03','21Khu04','22Khu05','23Khu06')
SHIPPED=('24Khu07','25Khu08','26Khu09','27Khu10','28Khu11','29Abhi01')

def load(path, name):
    spec=importlib.util.spec_from_loader(name, SourceFileLoader(name, path))
    m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

def build(mod, vol):
    mod.use(vol)
    v,s,u,h,i,rep = mod.build()
    return dict(zip(MAPS,(v,s,u,h,i)))

def snap(outdir, modpath, vols):
    os.makedirs(outdir, exist_ok=True)
    m=load(modpath,'bkv_'+os.path.basename(outdir))
    for vol in vols:
        d=build(m,vol)
        for k in MAPS:
            json.dump(d[k], open(os.path.join(outdir,'%s.%s.json'%(vol,k)),'w'),
                      ensure_ascii=False, sort_keys=True)

def shipped(outdir, vols):
    os.makedirs(outdir, exist_ok=True)
    for vol in vols:
        for k in MAPS:
            p=os.path.join(ROOT,'site/reader',k,vol+'.json')
            d=json.load(open(p)) if os.path.exists(p) else {}
            json.dump(d, open(os.path.join(outdir,'%s.%s.json'%(vol,k)),'w'),
                      ensure_ascii=False, sort_keys=True)

if __name__=='__main__':
    cmd=sys.argv[1]
    if cmd=='baseline':
        shutil.rmtree(os.path.join(SNAP,'base'), ignore_errors=True)
        snap(os.path.join(SNAP,'base'), os.path.join(ROOT,'pipeline/build_khu_volume.py.preniddesa'), BUILDER)
        shipped(os.path.join(SNAP,'base'), SHIPPED)
        print('baseline written')
    else:
        shutil.rmtree(os.path.join(SNAP,'cur'), ignore_errors=True)
        snap(os.path.join(SNAP,'cur'), os.path.join(ROOT,'pipeline/build_khu_volume.py'), BUILDER+SHIPPED)
        # !!! THE BASELINE BUILDER PREDATES THE GLYPH ERRATUM REGISTER.
        # `build_khu_volume.py.preniddesa` carries no `GLYPH_ERRATA` at all, so
        # it cannot apply a declared `apply_from`/`apply_to` to the printed
        # stream — and a volume that has one will differ FOREVER, as a PASS
        # reported as a FAIL.  20Khu03's uddāna prints `Aòjalī` for `Añjalī` in
        # a Theragāthā uddāna (2026-07-30); the old builder emits the broken
        # glyph, the current one the edition's own word.
        # The exemption is NAMED and PRINTED on every run, so the harness keeps
        # saying what it is not checking rather than quietly checking less.
        EXEMPT = {('20Khu03', 'uddana'): 'applied glyph erratum Aòjalī -> Añjalī; '
                                         'the baseline builder has no register',
                  ('20Khu03', 'verse'):  'same place, same reason'}
        bad=0; n=0; skipped=0
        for vol in BUILDER+SHIPPED:
            for k in MAPS:
                n+=1
                a=open(os.path.join(SNAP,'base','%s.%s.json'%(vol,k))).read()
                b=open(os.path.join(SNAP,'cur','%s.%s.json'%(vol,k))).read()
                if a==b:
                    continue
                if (vol,k) in EXEMPT:
                    skipped+=1
                    print('  EXEMPT %s %s — %s'%(vol,k,EXEMPT[(vol,k)]))
                    continue
                bad+=1; print('  DIFF %s %s  (base %d bytes, cur %d)'%(vol,k,len(a),len(b)))
        print('REGRESSION: %d/%d maps byte-identical across %d volumes'
              '%s  [%s]'
              %(n-bad-skipped,n,len(BUILDER+SHIPPED),
                ', %d exempt (named above)'%skipped if skipped else '',
                'OK' if not bad else 'FAIL'))
