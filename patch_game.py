from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')
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
p.write_text(s,encoding='utf-8')
print('index.html audited patch present')
