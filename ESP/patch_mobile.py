from pathlib import Path

p=Path('ESP/index.html')
s=p.read_text(encoding='utf-8')

old=""".help{border-top:1px solid #303a49;margin-top:18px;padding-top:16px;line-height:1.55}@media(max-width:820px){.wrap{grid-template-columns:1fr;max-width:500px}}"""
new=""".help{border-top:1px solid #303a49;margin-top:18px;padding-top:16px;line-height:1.55}.game-shell{position:relative}.touch-hint{display:none;position:absolute;inset:0;z-index:3;align-items:center;justify-content:center;text-align:center;padding:28px;pointer-events:none;background:linear-gradient(180deg,#0b1016aa,#0b1016dd);border-radius:12px;color:#fff;font-weight:800;line-height:1.55}.touch-hint small{display:block;margin-top:8px;color:#c5ced9;font-weight:600}.mobile-score{display:none}@media(max-width:820px){body{padding:8px;overflow-x:hidden}.wrap{grid-template-columns:1fr;max-width:500px;gap:8px}.card{padding:8px;border-radius:14px}.side{padding:12px}.game-shell{touch-action:none;user-select:none;-webkit-user-select:none}.touch-hint.show{display:flex}.mobile-score{display:flex;justify-content:space-between;align-items:center;margin-top:7px;padding:8px 12px;background:#202835;border:1px solid #334052;border-radius:11px;font-size:12px;color:#a9b4c2}.mobile-score strong{font-size:20px;color:#f3f6fb}.side .stats{display:none}.side h1,.side .sub{display:none}#game{max-height:calc(100vh - 62px);width:auto;max-width:100%;margin:auto}.help{font-size:12px}}"""
assert old in s
s=s.replace(old,new,1)

old='<body><div class="wrap"><div class="card"><canvas id="game" width="300" height="600"></canvas></div>'
new='<body><div class="wrap"><div class="card"><div id="gameShell" class="game-shell"><canvas id="game" width="300" height="600"></canvas><div id="touchHint" class="touch-hint"><div>← Toca izquierda &nbsp; · &nbsp; Toca derecha →<br>↓ Desliza para soltar &nbsp; · &nbsp; ↑ Desliza para girar<small>También puedes deslizar a izquierda o derecha</small></div></div></div><div class="mobile-score"><span>PUNTOS</span><strong id="mobileScore">0</strong><span>NIVEL <b id="mobileLevel">1</b></span></div></div>'
assert old in s
s=s.replace(old,new,1)

old="let W=new Set(BASE.map(fold)),BL=new Map(),SY=[],board,cur,next,score=0,total=0,best=0,level=1,ms=1200,last=performance.now(),acc=0,paused=false,over=false,busy=false,flash=new Set(),rep=new Map(),strong=false,bombFlash=new Set();"
new=old[:-1]+",touchHintVisible=true;"
assert old in s
s=s.replace(old,new,1)

old="function reset(){board=Array.from({length:R},()=>Array(C).fill(null));score=total=best=0;level=1;ms=1200;paused=over=busy=false;cur=piece();next=piece();ui();drawNext();msg('Forma palabras','Las palabras de 3 letras o más desaparecen en horizontal y vertical.')}"
new="function reset(){board=Array.from({length:R},()=>Array(C).fill(null));score=total=best=0;level=1;ms=1200;paused=over=busy=false;cur=piece();next=piece();touchHintVisible=true;const h=$('touchHint');if(h)h.classList.add('show');ui();drawNext();msg('Forma palabras','Las palabras de 3 letras o más desaparecen en horizontal y vertical.')}function hideTouchHint(){if(!touchHintVisible)return;touchHintVisible=false;const h=$('touchHint');if(h)h.classList.remove('show')}"
assert old in s
s=s.replace(old,new,1)

old="function ui(){$('score').textContent=score.toLocaleString('es-ES');$('level').textContent=level;$('words').textContent=total;$('best').textContent=best;$('pause').textContent=paused?'Continuar':'Pausa'}"
new="function ui(){$('score').textContent=score.toLocaleString('es-ES');$('level').textContent=level;$('words').textContent=total;$('best').textContent=best;$('pause').textContent=paused?'Continuar':'Pausa';if($('mobileScore'))$('mobileScore').textContent=score.toLocaleString('es-ES');if($('mobileLevel'))$('mobileLevel').textContent=level}"
assert old in s
s=s.replace(old,new,1)

old="document.addEventListener('keydown',e=>{if(['ArrowLeft','ArrowRight','ArrowUp','ArrowDown',' '].includes(e.key))e.preventDefault();if(e.key==='ArrowLeft')move(-1);if(e.key==='ArrowRight')move(1);if(e.key==='ArrowUp')rot();if(e.key==='ArrowDown')down();if(e.key===' ')drop()});$('new').onclick=reset;"
new="""document.addEventListener('keydown',e=>{if(['ArrowLeft','ArrowRight','ArrowUp','ArrowDown',' '].includes(e.key))e.preventDefault();if(e.key==='ArrowLeft')move(-1);if(e.key==='ArrowRight')move(1);if(e.key==='ArrowUp')rot();if(e.key==='ArrowDown')down();if(e.key===' ')drop()});
const shell=$('gameShell');let tx=0,ty=0,tt=0,movedTouch=false;const SWIPE=28;
shell.addEventListener('touchstart',e=>{if(!e.touches.length)return;const t=e.touches[0];tx=t.clientX;ty=t.clientY;tt=Date.now();movedTouch=false},{passive:true});
shell.addEventListener('touchmove',e=>{if(e.cancelable)e.preventDefault()},{passive:false});
shell.addEventListener('touchend',e=>{if(!e.changedTouches.length)return;const t=e.changedTouches[0],dx=t.clientX-tx,dy=t.clientY-ty,ax=Math.abs(dx),ay=Math.abs(dy);hideTouchHint();if(Math.max(ax,ay)>=SWIPE){movedTouch=true;if(ay>ax){if(dy>0)drop();else rot()}else move(dx>0?1:-1);return}const r=shell.getBoundingClientRect();move(t.clientX<r.left+r.width/2?-1:1)},{passive:false});
shell.addEventListener('contextmenu',e=>e.preventDefault());
$('new').onclick=reset;"""
assert old in s
s=s.replace(old,new,1)

p.write_text(s,encoding='utf-8')
print('Patched Spanish mobile controls and mobile HUD')
