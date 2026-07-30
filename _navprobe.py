#!/usr/bin/env python3
"""Prove a change to build_abhidhamma_nav.py moves NO shipped volume.

Runs every Abhidhamma volume's nav build with the OLD file and the NEW one,
each writing into its own scratch copy of nav.json, and compares the resulting
nav bytes and the build's own report.  Usage: python3 _navprobe.py old|new
"""
import importlib.util, io, json, os, shutil, sys, contextlib

ROOT = os.path.dirname(os.path.abspath(__file__))
tag = sys.argv[1]
src = os.path.join(ROOT, 'pipeline', 'build_abhidhamma_nav.py'
                   + ('.previnaya' if tag == 'old' else ''))
out = os.path.join(ROOT, '_navprobe')
os.makedirs(out, exist_ok=True)

def load():
    import importlib.machinery
    spec = importlib.util.spec_from_file_location(
        '_bn_' + tag, src,
        loader=importlib.machinery.SourceFileLoader('_bn_' + tag, src))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

vols = list(load().SPEC)
print(len(vols), 'volumes:', ' '.join(vols))
rep = {}
for v in vols:
    nav = os.path.join(out, '%s_%s.json' % (tag, v))
    shutil.copy(os.path.join(ROOT, 'site/reader/nav.json'), nav)
    m = load()
    m.NAV = nav
    sys.argv = ['x', v, '--write']
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            m.main()
    except SystemExit as e:
        buf.write('EXIT %s\n' % e)
    rep[v] = buf.getvalue().replace(nav, '<NAV>')
    j = json.load(open(nav, encoding='utf-8'))
    node = [x for L in j['layers'] for nk in L.get('nikayas', [])
            for x in nk.get('volumes', []) if x.get('vol') == v]
    rep[v + '#tree'] = json.dumps(node, ensure_ascii=False, sort_keys=True)
json.dump(rep, open(os.path.join(out, tag + '.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('wrote', os.path.join(out, tag + '.json'))
