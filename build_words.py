from pathlib import Path
import re

from pymorphy3 import MorphAnalyzer
from wordfreq import top_n_list, zipf_frequency

MIN_LEN, MAX_LEN = 3, 16
ALLOWED_POS = {'NOUN','VERB','INFN','ADJF','ADJS','ADVB','NPRO','PRED','COMP'}
BLOCK_GRAMMEMES = {'Name','Surn','Patr','Geox','Orgn','Abbr','Fixd','LATN','ROMN'}
BLACK = set('''осо одав ски ооо ааа еее иии нии оон ссс рфс сша сср снг мвд гаи гиб гибдд гто нло нпо'''.split())
WHITE = set('''
том тома тому томом томе томы томов томам томами томах
дуб дуба дубу дубом дубе дубы дубов дубам дубами дубах
бук бука буку буком буке буки буков букам буками буках
учи учил учила учили учит учат учим учите учусь учится учатся учиться
еду едет едут ехал ехала ехали ехать
воин воина воину воином воине воины воинов воинам воинами воинах
вена вены вену веной вене венам венами венах
пат мат гол сет риф кот лес лис дом домы дома тихо быстро красная играет
'''.split())
CYR = re.compile(r'^[а-яё]+$', re.I)

morph = MorphAnalyzer()

def clean(w):
    w = w.lower().replace('ё','е')
    return w if MIN_LEN <= len(w) <= MAX_LEN and CYR.fullmatch(w) else None

def acceptable_parse(p):
    return p.tag.POS in ALLOWED_POS and not (set(p.tag.grammemes) & BLOCK_GRAMMEMES)

# Modern frequent surface forms are the gate that chooses useful lemmas.
seeds = top_n_list('ru', 60000)
lemmas = {}
direct = set()
for raw in seeds:
    w = clean(raw)
    if not w or w in BLACK:
        continue
    parses = [p for p in morph.parse(w) if acceptable_parse(p)]
    if not parses:
        continue
    p = parses[0]
    direct.add(w)
    lemma = clean(p.normal_form)
    if lemma:
        lemmas.setdefault(lemma, p)

words = set(WHITE)
# Keep genuinely frequent surface forms regardless of whether they are inflected.
for w in direct:
    if zipf_frequency(w, 'ru') >= 3.15:
        words.add(w)

# Expand only lemmas already observed in modern frequent text. Generated forms still
# need some corpus presence, which cuts dictionary curiosities but keeps ordinary cases/verbs.
for lemma, p in lemmas.items():
    if zipf_frequency(lemma, 'ru') < 3.25:
        continue
    for form in p.lexeme:
        if form.tag.POS not in ALLOWED_POS or set(form.tag.grammemes) & BLOCK_GRAMMEMES:
            continue
        w = clean(form.word)
        if not w or w in BLACK:
            continue
        if zipf_frequency(w, 'ru') >= 2.15:
            words.add(w)

words -= BLACK
# Hard validation: no garbage shape, no duplicates, required gameplay words present.
words = {w for w in words if clean(w) == w}
required = {'том','дуб','бук','учи','еду','воин','вена','пат','мат','гол','сет','риф','кот','лес','дом','тихо','быстро','красная','играет'}
missing = required - words
if missing:
    raise SystemExit(f'missing required words: {sorted(missing)}')
leaked = BLACK & words
if leaked:
    raise SystemExit(f'blacklisted words leaked: {sorted(leaked)}')

out = '\n'.join(sorted(words, key=lambda x: (len(x), x))) + '\n'
Path('words.txt').write_text(out, encoding='utf-8')
print(f'Wrote {len(words)} controlled word forms')
