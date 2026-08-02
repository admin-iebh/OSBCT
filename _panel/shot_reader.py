#!/usr/bin/env python3
"""Screenshots of the panel inside reader2 — desktop side and phone sheet."""
import sys, os
from playwright.sync_api import sync_playwright
BASE = os.environ.get('GATE_BASE', 'http://localhost:8932')
ROOT = os.path.dirname(os.path.abspath(__file__))

def shoot(pw, name, vw, vh, vol, word, mobile=False):
    b = pw.chromium.launch()
    pg = b.new_page(viewport={'width': vw, 'height': vh},
                    device_scale_factor=2, is_mobile=mobile, has_touch=mobile)
    pg.goto(BASE + f'/reader/reader2.html?wl=1#{vol}/0', wait_until='domcontentloaded')
    pg.wait_for_selector('.para.canon', timeout=20000)
    pg.wait_for_timeout(600)
    hit = pg.evaluate('''(word) => {
      for (const p of document.querySelectorAll('.para.canon')) {
        const i = p.textContent.indexOf(word); if (i < 0) continue;
        const w = document.createTreeWalker(p, NodeFilter.SHOW_TEXT);
        let acc = 0, node;
        while ((node = w.nextNode())) {
          const L = node.textContent.length;
          if (acc + L > i) {
            const r = document.createRange();
            r.setStart(node, i - acc); r.setEnd(node, Math.min(i - acc + 3, L));
            p.scrollIntoView({block: 'center'});
            const rect = r.getBoundingClientRect();
            if (rect.width > 0 && rect.top > 60 && rect.bottom < innerHeight - 20)
              return {x: rect.x + 2, y: rect.y + rect.height / 2};
          }
          acc += L;
        }
      }
      return null;
    }''', word)
    if hit:
        pg.mouse.click(hit['x'], hit['y'])
        pg.wait_for_selector('#wl[data-state="ready"]', timeout=20000)
        pg.wait_for_timeout(400)
    pg.screenshot(path=os.path.join(ROOT, name))
    print(name, 'ok' if hit else 'WORD NOT FOUND')
    b.close()

with sync_playwright() as pw:
    shoot(pw, 'shot_desktop.png', 1440, 900, '09Ma01', 'kāmahetu')
    shoot(pw, 'shot_phone.png', 390, 844, '09Ma01', 'khayaṁ', mobile=True)
