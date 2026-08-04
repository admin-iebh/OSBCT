# -*- coding: utf-8 -*-
"""Fourth edit: PRINTED ORDER inside a unit.

`cur_groups` and `cur_after` are two sinks and the reader draws every group
before any of the after-blocks.  That is right for the canon, where a unit IS
its gāthā and the prose follows it.  In a commentary a unit's gāthā can be
printed in the MIDDLE of its narrative -- 41KhuA22 p323 sets six pāda lines
thirteen printed pages after unit 783's own gāthā -- and putting them in the
group draws them before the prose they follow.  So once prose has been emitted
for this unit, a display block goes into `after` as a `{'gatha': [...]}` block,
which `render_parts`, `check_page_fidelity` and the reader all already draw.
Gated on the book having a prose column, so the canon path is untouched.
"""
import io
P = '/sessions/rcw-01bcgpjfpcgbdwzs1dqi2qk7/mnt/OSBCT/pipeline/build_khu_volume.py'
s = io.open(P, encoding='utf-8').read()

def sub(old, new):
    global s
    assert s.count(old) == 1, (s.count(old), old[:60])
    s = s.replace(old, new)

sub("""                elif kind == 'pada':
                    if cur_groups:
                        cur_groups[-1].append(it[1])""",
    """                elif kind == 'pada':
                    if _pcol and cur_after:
                        _lb = cur_after[-1]
                        if isinstance(_lb, dict) and 'gatha' in _lb:
                            _add_line(_lb['gatha'], it[1])
                        else:
                            cur_after.append({'gatha': [it[1]]})
                    elif cur_groups:
                        cur_groups[-1].append(it[1])""")

sub("""                    prev = cur_after[-1] if cur_after else ''
                    if prev and (prev.endswith('-') or kind == 'pcont'):""",
    """                    prev = (cur_after[-1] if cur_after
                            and isinstance(cur_after[-1], str) else '')
                    if prev and (prev.endswith('-') or kind == 'pcont'):""")

io.open(P, 'w', encoding='utf-8').write(s)
print('patch4 applied')
