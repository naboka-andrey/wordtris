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

# Cross-word fix: horizontal and vertical words never suppress one another.
old="all.push({w,cells,rp})}all.sort((a,b)=>b.w.length-a.w.length);let out=[],used=new Map();for(const f of all){let ks=f.cells.map(z=>z.x+','+z.y);if(ks.some(k=>(used.get(k)||0)>f.w.length))continue;out.push(f);ks.forEach(k=>used.set(k,Math.max(used.get(k)||0,f.w.length)))}return out}"
new="all.push({w,cells,rp,d:q.d})}all.sort((a,b)=>b.w.length-a.w.length);let out=[],used={h:new Map(),v:new Map()};for(const f of all){let ks=f.cells.map(z=>z.x+','+z.y),u=used[f.d];if(ks.some(k=>(u.get(k)||0)>f.w.length))continue;out.push(f);ks.forEach(k=>u.set(k,Math.max(u.get(k)||0,f.w.length)))}return out}"
if old in s:
    s=s.replace(old,new,1)
elif new not in s:
    raise SystemExit('Spanish cross-word find target missing')

p.write_text(s,encoding='utf-8')
print('Spanish center rotation + crossed-word logic patched')
