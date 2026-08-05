# -*- coding: utf-8 -*-
import io,re
P='pipeline/build_khu_volume.py'
s=io.open(P,encoding='utf-8').read()
i=s.index("        # !!! AND THE STRIP IS NOW UNCONDITIONAL")
j=s.index("        c = re.sub(r'\\s*\\(\\d+\\)\\s*$', '', core)\n")
k=j+len("        c = re.sub(r'\\s*\\(\\d+\\)\\s*$', '', core)\n")
old = """        c = (re.sub(r'\\s*\\(\\d+\\)\\s*$', '', core)
             if SPEC[VOL].get('margin_verse_numbers') else core)
"""
s = s[:i] + old + s[k:]
io.open(P,'w',encoding='utf-8').write(s)
print('reverted head')
