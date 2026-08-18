from pathlib import Path
p=Path('ESP/index.html')
s=p.read_text(encoding='utf-8')
s=s.replace('← Toca izquierda &nbsp; · &nbsp; Toca derecha →<br>↓ Desliza para soltar &nbsp; · &nbsp; ↑ Desliza para girar<small>También puedes deslizar a izquierda o derecha</small>','← Toca izquierda &nbsp; · &nbsp; Centro: girar &nbsp; · &nbsp; Toca derecha →<br>↓ Desliza para soltar &nbsp; · &nbsp; ↑ Desliza para girar<small>También puedes deslizar a izquierda o derecha</small>')
s=s.replace('Móvil: toca izquierda/derecha para mover; desliza ←/→ para mover, ↓ para soltar, ↑ para girar.','Móvil: toca izquierda/derecha para mover, toca el centro para girar; desliza ←/→ para mover, ↓ para soltar, ↑ para girar.')
old="""const shell=$('gameShell');let sx=0,sy=0;const SW=28;
shell.addEventListener('touchstart',e=>{if(!e.touches.length)return;const t=e.touches[0];sx=t.clientX;sy=t.clientY},{passive:true});
shell.addEventListener('touchmove',e=>{if(e.cancelable)e.preventDefault()},{passive:false});
shell.addEventListener('touchend',e=>{if(!e.changedTouches.length)return;const t=e.changedTouches[0],dx=t.clientX-sx,dy=t.clientY-sy,ax=Math.abs(dx),ay=Math.abs(dy);hideHint();if(Math.max(ax,ay)>=SW){if(ay>ax){if(dy>0)drop();else rot()}else move(dx>0?1:-1);return}const r=shell.getBoundingClientRect();move(t.clientX<r.left+r.width/2?-1:1)},{passive:false});"""
new="""const shell=$('gameShell');let sx=0,sy=0;const SW=28,CENT=0.28;
shell.addEventListener('touchstart',e=>{if(!e.touches.length)return;const t=e.touches[0];sx=t.clientX;sy=t.clientY},{passive:true});
shell.addEventListener('touchmove',e=>{if(e.cancelable)e.preventDefault()},{passive:false});
shell.addEventListener('touchend',e=>{if(!e.changedTouches.length)return;const t=e.changedTouches[0],dx=t.clientX-sx,dy=t.clientY-sy,ax=Math.abs(dx),ay=Math.abs(dy);hideHint();if(Math.max(ax,ay)>=SW){if(ay>ax){if(dy>0)drop();else rot()}else move(dx>0?1:-1);return}const r=shell.getBoundingClientRect(),u=(t.clientX-r.left)/r.width;if(u>=.5-CENT/2&&u<=.5+CENT/2)rot();else move(u<.5?-1:1)},{passive:false});"""
if old in s:s=s.replace(old,new)
elif 'CENT=0.28' not in s: raise SystemExit('Spanish touch handler target missing')
p.write_text(s,encoding='utf-8')
print('Spanish center tap rotation patched')
