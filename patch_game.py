from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

repls=[
("const BASE=['пат'","const BASE=['том','дуб','бук','учи','еду','пат'"),
("const s=new Set(BASE);const local=await fetch('words.txt?v=5'","const s=new Set();const local=await fetch('words.txt?v=7'"),
("reset();dict();requestAnimationFrame(loop)})();","async function boot(){await dict();reset();requestAnimationFrame(loop)}boot()})();")]
for old,new in repls:
    if old in s:
        s=s.replace(old,new,1)

if 'id="mobileHint"' not in s:
    css=""".gamecard{position:relative}.mobile-hud{display:none}.mobile-hint{display:none;position:absolute;left:50%;top:42%;transform:translate(-50%,-50%);z-index:5;width:86%;padding:16px 14px;border-radius:16px;background:#10161ee8;border:1px solid #ffffff35;text-align:center;font-size:14px;line-height:1.45;font-weight:700;pointer-events:none;transition:opacity .25s}.mobile-hint b{display:block;font-size:18px;margin-bottom:7px}.mobile-hint.hide{opacity:0}.gamecard canvas{touch-action:none;user-select:none;-webkit-user-select:none}@media(max-width:820px){body{padding:6px 6px 16px}.wrap{grid-template-columns:1fr;max-width:430px;gap:8px}.card{border-radius:14px;padding:6px}.side{padding:12px}.gamecard{padding:4px}#game{max-height:calc(100svh - 78px);width:auto;max-width:100%;margin:auto}.mobile-hud{display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-top:6px}.mobile-hud .mh{background:#202835;border:1px solid #334052;border-radius:10px;padding:7px 10px;display:flex;justify-content:space-between;align-items:center}.mobile-hud .mh span{font-size:10px;color:#9ba7b6}.mobile-hud .mh b{font-size:18px}.mobile-hint{display:block}.side .stats{margin-top:10px}}"""
    s=s.replace('</style></head>',css+'</style></head>',1)
    old='<div class="card"><canvas id="game" width="300" height="600"></canvas></div>'
    new='<div class="card gamecard"><canvas id="game" width="300" height="600"></canvas><div id="mobileHint" class="mobile-hint"><b>Управление</b>Тап слева / справа — двигать<br>Тап по центру — повернуть<br>← → свайп — двигать<br>↓ свайп — бросить · ↑ — повернуть</div><div class="mobile-hud"><div class="mh"><span>ОЧКИ</span><b id="mobileScore">0</b></div><div class="mh"><span>УРОВЕНЬ</span><b id="mobileLevel">1</b></div></div></div>'
    if old not in s: raise SystemExit('mobile board target missing')
    s=s.replace(old,new,1)
else:
    s=s.replace('Тап слева / справа — двигать<br>← → свайп — двигать<br>↓ свайп — бросить<br>↑ свайп — повернуть','Тап слева / справа — двигать<br>Тап по центру — повернуть<br>← → свайп — двигать<br>↓ свайп — бросить · ↑ — повернуть')

if "$('mobileScore')" not in s:
    a=s.find('function ui(){'); b=s.find('}function msg(',a)
    if a<0 or b<0: raise SystemExit('cannot locate ui function')
    ui=s[a:b+1]
    ui2=ui[:-1]+";if($('mobileScore'))$('mobileScore').textContent=score.toLocaleString('ru-RU');if($('mobileLevel'))$('mobileLevel').textContent=level}"
    s=s[:a]+ui2+s[b+1:]

start=s.find('function hideMobileHint()')
end=s.find("document.addEventListener('keydown'",start)
if start>=0 and end>start:
    s=s[:start]+s[end:]
touch="""function hideMobileHint(){let h=$('mobileHint');if(h&&!h.classList.contains('hide')){h.classList.add('hide');setTimeout(()=>h.style.display='none',260)}}let tx=0,ty=0,tt=0;const TOUCH_SWIPE=28,TOUCH_CENTER=.28;g.addEventListener('touchstart',e=>{if(!e.touches.length)return;tx=e.touches[0].clientX;ty=e.touches[0].clientY;tt=performance.now();e.preventDefault()},{passive:false});g.addEventListener('touchmove',e=>{e.preventDefault()},{passive:false});g.addEventListener('touchend',e=>{let t=e.changedTouches&&e.changedTouches[0];if(!t)return;let dx=t.clientX-tx,dy=t.clientY-ty,ax=Math.abs(dx),ay=Math.abs(dy);hideMobileHint();if(Math.max(ax,ay)>=TOUCH_SWIPE){if(ay>ax){if(dy>0)drop();else rot()}else move(dx>0?1:-1);e.preventDefault();return}let r=g.getBoundingClientRect(),u=(t.clientX-r.left)/r.width;if(u>=.5-TOUCH_CENTER/2&&u<=.5+TOUCH_CENTER/2)rot();else move(u<.5?-1:1);e.preventDefault()},{passive:false});"""
marker="document.addEventListener('keydown'"
if marker not in s: marker="addEventListener('keydown'"
if marker not in s: raise SystemExit('keyboard marker missing')
s=s.replace(marker,touch+marker,1)

old="function reset(){board=Array.from({length:R},()=>Array(C).fill(null));"
new="function reset(){let h=$('mobileHint');if(h&&matchMedia('(max-width:820px)').matches){h.style.display='block';h.classList.remove('hide')}board=Array.from({length:R},()=>Array(C).fill(null));"
if old in s:s=s.replace(old,new,1)

# Cross-word fix: longest-word priority applies only within the same direction.
old="all.push({w,cells,rp})}all.sort((a,b)=>b.w.length-a.w.length);let out=[],used=new Map();for(const f of all){let ks=f.cells.map(z=>z.x+','+z.y);if(ks.some(k=>(used.get(k)||0)>f.w.length))continue;out.push(f);ks.forEach(k=>used.set(k,Math.max(used.get(k)||0,f.w.length)))}return out}"
new="all.push({w,cells,rp,d:q.d})}all.sort((a,b)=>b.w.length-a.w.length);let out=[],used={h:new Map(),v:new Map()};for(const f of all){let ks=f.cells.map(z=>z.x+','+z.y),u=used[f.d];if(ks.some(k=>(u.get(k)||0)>f.w.length))continue;out.push(f);ks.forEach(k=>u.set(k,Math.max(u.get(k)||0,f.w.length)))}return out}"
if old in s:
    s=s.replace(old,new,1)
elif new not in s:
    raise SystemExit('cross-word find target missing')

p.write_text(s,encoding='utf-8')
print('Russian controls + crossed-word logic patched')
