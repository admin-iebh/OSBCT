#!/usr/bin/env python3
"""Screenshot + interaction probe for the panel prototype.
Usage: shot.py <width> <height> <outprefix> [clickword] [tab]
Clicks the first occurrence of clickword in the text (via caret walk in page JS),
then screenshots. Real Chromium, real dimensions — per the standing instruction.
"""
import sys, json
from playwright.sync_api import sync_playwright

W, H, out = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
word = sys.argv[4] if len(sys.argv) > 4 else None
tab = sys.argv[5] if len(sys.argv) > 5 else None

with sync_playwright() as pw:
    b = pw.chromium.launch()
    pg = b.new_page(viewport={'width': W, 'height': H},
                    device_scale_factor=2)
    msgs = []
    pg.on('console', lambda m: msgs.append(m.type + ': ' + m.text))
    pg.on('pageerror', lambda e: msgs.append('PAGEERROR: ' + str(e)))
    pg.goto('http://localhost:8931/', wait_until='networkidle')
    pg.wait_for_selector('p.para', timeout=8000)
    if word:
        # find the word's pixel position inside the first paragraph containing it
        box = pg.evaluate('''(word)=>{
          const ps=[...document.querySelectorAll('p.para')];
          for(const p of ps){
            const t=p.textContent;
            const i=t.indexOf(word);
            if(i<0)continue;
            const walker=document.createTreeWalker(p,NodeFilter.SHOW_TEXT);
            let acc=0,node;
            while((node=walker.nextNode())){
              const L=node.textContent.length;
              if(acc+L>i){
                const r=document.createRange();
                r.setStart(node,i-acc);r.setEnd(node,i-acc+word.length);
                p.scrollIntoView({block:'center'});
                let rect2=r.getBoundingClientRect();
                // centre the WORD, not the paragraph — long paragraphs
                // overflow the viewport and leave the word off-screen
                window.scrollBy(0, rect2.y - innerHeight/2);
                rect2=r.getBoundingClientRect();
                return {x:rect2.x+rect2.width/2,y:rect2.y+rect2.height/2,n:p.dataset.n};
              }
              acc+=L;
            }
          }
          return null;
        }''', word)
        if not box:
            print('WORD NOT FOUND:', word); sys.exit(2)
        pg.mouse.click(box['x'], box['y'])
        pg.wait_for_selector('#panel[data-state="ready"]', timeout=20000)
        pg.wait_for_timeout(150)
        if tab:
            pg.click(f'#ptabs button[data-tab="{tab}"]')
            pg.wait_for_timeout(400)
    pg.screenshot(path=out + '.png', full_page=False)
    state = pg.evaluate('''()=>({
      panelOpen:document.getElementById('panel').classList.contains('open'),
      word:document.getElementById('pword').textContent,
      counts:document.getElementById('pcounts').textContent,
      tabs:[...document.querySelectorAll('#ptabs button')].map(b=>({t:b.dataset.tab,
        sel:b.getAttribute('aria-selected'),dis:b.classList.contains('dis'),label:b.textContent.trim()})),
      bodyChars:document.getElementById('pbody').textContent.length,
      panelRect:(r=>({x:r.x,y:r.y,w:r.width,h:r.height}))(document.getElementById('panel').getBoundingClientRect()),
      textW:document.getElementById('text').getBoundingClientRect().width,
      vw:innerWidth,vh:innerHeight
    })''')
    print(json.dumps(state, ensure_ascii=False, indent=1))
    if msgs: print('CONSOLE:', '\n'.join(msgs[:10]))
    b.close()
