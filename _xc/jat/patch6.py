# -*- coding: utf-8 -*-
"""Sixth edit: the `no_reprint` filter must see inside a gāthā block.

`_cwhole` drops a `before`/`after` residue whose whole text is already a corpus
paragraph, so the body draws it once.  It inspected STRINGS only.  A display
block is now stored as `{'gatha': [...]}`, and 42KhuA23's two narrative
lead-ins -- `Tato nāgarājā mahāsattaṁ disvā gāthamāha-` and `Mahāsatto pana
paṭinivatto, atha naṁ Puṇṇako āha-`, the very two the filter was written for --
land inside one, where it could not see them.  `verify_render_vs_pdf` counted
them: rendered 2x, printed 1x.
"""
import io
P = '/sessions/rcw-01bcgpjfpcgbdwzs1dqi2qk7/mnt/OSBCT/pipeline/build_khu_volume.py'
s = io.open(P, encoding='utf-8').read()
old = """                    _xs = [x for x in _xs
                           if not (isinstance(x, str)
                                   and _cwhole.get(_sq(x), cur_ord) != cur_ord)]
                    if _xs:"""
new = """                    _keep = []
                    for x in _xs:
                        if isinstance(x, str):
                            if _cwhole.get(_sq(x), cur_ord) == cur_ord:
                                _keep.append(x)
                            continue
                        if isinstance(x, dict) and 'gatha' in x:
                            _g = [l for l in x['gatha']
                                  if _cwhole.get(_sq(l), cur_ord) == cur_ord]
                            if _g:
                                _keep.append({'gatha': _g})
                            continue
                        _keep.append(x)
                    _xs = _keep
                    if _xs:"""
assert s.count(old) == 1
s = s.replace(old, new)
io.open(P, 'w', encoding='utf-8').write(s)
print('patch6 applied')
