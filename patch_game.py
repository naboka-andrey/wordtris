from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

# Existing dictionary/startup fixes (idempotent).
repls=[
("const BASE=['пат'","const BASE=['том','дуб','бук','учи','еду','пат'"),
("const s=new Set(BASE);const local=await fetch('words.txt?v=5'","const s=new Set();const local=await fetch('words.txt?v=7'"),
("reset();dict();requestAnimationFrame(loop)})();","async function boot(){await dict();reset();requestAnimationFrame(loop)}boot()})();")]
for old,new in repls:
    if old in s:
        if s.count(old)!=1: raise SystemExit('ambiguous patch target: '+old[:50])
        s=s.replace(old,new)
    elif new not in s:
        raise SystemExit('patch target missing: '+old[:50])

# Mobile layout: touch-safe board, on-board hint, compact score/level under board.
if 'id="mobileHint"' not in s:
    css=""".gamecard{position:relative}.mobile-hud{display:none}.mobile-hint{display:none;position:absolute;left:50%;top:42%;transform:translate(-50%,-50%);z-index:5;width:82%;padding:16px 14px;border-radius:16px;background:#10161ee8;border:1px solid #ffffff35;text-align:center;font-size:14px;line-height:1.45;font-weight:700;pointer-events:none;transition:opacity .25s}.mobile-hint b{display:block;font-size:18px;margin-bottom:7px}.mobile-hint.hide{opacity:0}.gamecard canvas{touch-action:none;user-select:none;-webkit-user-select:none}@media(max-width:820px){body{padding:6px 6px 16px}.wrap{grid-template-columns:1fr;max-width:430px;gap:8px}.card{border-radius:14px;padding:6px}.side{padding:12px}.gamecard{padding:4px}#game{max-height:calc(100svh - 78px);width:auto;max-width:100%;margin:auto}.mobile-hud{display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-top:6px}.mobile-hud .mh{background:#202835;border:1px solid #334052;border-radius:10px;padding:7px 10px;display:flex;justify-content:space-between;align-items:center}.mobile-hud .mh span{font-size:10px;color:#9ba7b6}.mobile-hud .mh b{font-size:18px}.mobile-hint{display:block}.side .stats{margin-top:10px}}"""
    s=s.replace('</style></head>',css+'</style></head>')
    old='<div class="card"><canvas id="game" width="300" height="600"></canvas></div>'
    new='<div class="card gamecard"><canvas id="game" width="300" height="600"></canvas><div id="mobileHint" class="mobile-hint"><b>Управление</b>Тап слева / справа — двигать<br>← → свайп — двигать<br>↓ свайп — бросить<br>↑ свайп — повернуть</div><div class="mobile-hud"><div class="mh"><span>ОЧКИ</span><b id="mobileScore">0</b></div><div class="mh"><span>УРОВЕНЬ</span><b id="mobileLevel">1</b></div></div></div>'
    if old not in s: raise SystemExit('mobile board target missing')
    s=s.replace(old,new,1)

# Keep compact mobile HUD synchronized with normal stats.
old="function ui(){$('score').textContent=score.toLocaleString('ru-RU');$('level').textContent=level;$('words').textContent=total;$('best').textContent=best;$('pause').textContent=paused?'Продолжить':'Пауза'}"
new="function ui(){$('score').textContent=score.toLocaleString('ru-RU');$('level').textContent=level;$('words').textContent=total;$('best').textContent=best;$('pause').textContent=paused?'Продолжить':'Пауза';if($('mobileScore'))$('mobileScore').textContent=score.toLocaleString('ru-RU');if($('mobileLevel'))$('mobileLevel').textContent=level}"
if old in s: s=s.replace(old,new,1)
elif new not in s: raise SystemExit('ui target missing')

# Some older builds used another pause label expression; patch generically if necessary.
if "$('mobileScore')" not in s:
    marker="function ui(){"
    a=s.find(marker); b=s.find('}function msg(',a)
    if a<0 or b<0: raise SystemExit('cannot locate ui function')
    ui=s[a:b+1]
    ui2=ui[:-1]+";if($('mobileScore'))$('mobileScore').textContent=score.toLocaleString('ru-RU');if($('mobileLevel'))$('mobileLevel').textContent=level}"
    s=s[:a]+ui2+s[b+1:]

# Mobile gestures. Horizontal swipe/tap moves one cell, down drops, up rotates.
if 'function hideMobileHint()' not in s:
    touch="""function hideMobileHint(){let h=$('mobileHint');if(h&&!h.classList.contains('hide')){h.classList.add('hide');setTimeout(()=>h.style.display='none',260)}}let tx=0,ty=0,tt=0;g.addEventListener('touchstart',e=>{if(!e.touches.length)return;tx=e.touches[0].clientX;ty=e.touches[0].clientY;tt=performance.now();e.preventDefault()},{passive:false});g.addEventListener('touchmove',e=>{e.preventDefault()},{passive:false});g.addEventListener('touchend',e=>{let t=e.changedTouches&&e.changedTouches[0];if(!t)return;let dx=t.clientX-tx,dy=t.clientY-ty,ax=Math.abs(dx),ay=Math.abs(dy),dt=performance.now()-tt;hideMobileHint();if(ay>45&&ay>ax*1.15){if(dy>0)drop();else rot();return}if(ax>38&&ax>ay*1.1){move(dx>0?1:-1);return}if(ax<18&&ay<18&&dt<450){let r=g.getBoundingClientRect();move(t.clientX<r.left+r.width/2?-1:1)}e.preventDefault()},{passive:false});"""
    marker="document.addEventListener('keydown'"
    if marker not in s: raise SystemExit('keyboard marker missing')
    s=s.replace(marker,touch+marker,1)

# Show the hint again for each new game on mobile.
old="function reset(){board=Array.from({length:R},()=>Array(C).fill(null));"
new="function reset(){let h=$('mobileHint');if(h&&matchMedia('(max-width:820px)').matches){h.style.display='block';h.classList.remove('hide')}board=Array.from({length:R},()=>Array(C).fill(null));"
if old in s: s=s.replace(old,new,1)
elif new not in s: raise SystemExit('reset target missing')

p.write_text(s,encoding='utf-8')
print('index.html audited + mobile controls present')
