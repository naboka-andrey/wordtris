from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')
repls=[
("const BASE=['пат'","const BASE=['том','дуб','бук','учи','еду','пат'"),
("const s=new Set(BASE);const local=await fetch('words.txt?v=5'","const s=new Set();const local=await fetch('words.txt?v=7'"),
("reset();dict();requestAnimationFrame(loop)})();","async function boot(){await dict();reset();requestAnimationFrame(loop)}boot()})();")]
for old,new in repls:
    if s.count(old)!=1: raise SystemExit('patch target mismatch: '+old[:50])
    s=s.replace(old,new)
p.write_text(s,encoding='utf-8')
print('patched index.html')
