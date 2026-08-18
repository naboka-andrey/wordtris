from pathlib import Path
import re
from collections import Counter

from pymorphy3 import MorphAnalyzer
from wordfreq import top_n_list, zipf_frequency

MIN_LEN, MAX_LEN = 3, 16
ALLOWED_POS = {'NOUN','VERB','INFN','ADJF','ADJS','ADVB','NPRO','PRED','COMP'}
BLOCK_GRAMMEMES = {'Name','Surn','Patr','Geox','Orgn','Abbr','Fixd','LATN','ROMN'}
BLACK = set('''осо одав ски ооо ааа еее иии нии оон ссс рфс сша сср снг мвд гаи гиб гибдд гто нло нпо'''.split())
# Three-letter accidental combinations are extremely common in WORDtris, so this list
# is intentionally hand-curated. It includes ordinary inflected forms, verbs, adjectives,
# pronouns and adverbs, but not obscure dictionary curiosities or abbreviations.
SHORT3 = set('''
акт арт аут баб баз бак бал бан бар бас бег бед бей бес бил бит бич боб бог бои бой бок бор бот бою боя бук бум бур бык был быт бью
вам вар вас ваш веб век вел вес вид вне вод воз вон вор ври вру все всю вся
гад газ где геи гей ген гид год гол гон гор губ гул
дай дал дам дар даю дед дел дна дне дни дно дну дню дня дог док дом дуб дух душ дым дыр
его еда еде еду еды ежи ела еле ели ель ему ест ешь еще
жаб жар жги жду жди жив жил жир жми жри жук
зад зал зла зло злы зов зря зуб зуд
ива иве иву ивы игр иди иду имя ион иск ищи ищу
как кал кем кит код кож коз кол ком кон кот кто куб кум кэш
лад лай лак лап лба лбу лев лег лед лез леи лей лес лет лис лиц лоб лом лук луч
маг май мак мат мед мел мех миг мир мог мой мох муж мыл
нам наш нет низ нос нож
она они оно
пар пат пей пел пил пир пол поп пот пью
раз рад рай рак рев рис риф род рок рот ряд
сад сам сел сет сил сом сон суп суд сух сын сыр сыт
так там тех тих тип том тон топ тот тур тут
уха ухо
ход хор
чай час чек чем чин
шар шей шеф шла шли шов шел шум
щит
юн
яма ямы яму
'''.split())
WHITE = set('''
том тома тому томом томе томы томов томам томами томах
дуб дуба дубу дубом дубе дубы дубов дубам дубами дубах
бук бука буку буком буке буки буков букам буками буках
учи учил учила учили учит учат учим учите учусь учится учатся учиться
еду едет едут ехал ехала ехали ехать
воин воина воину воином воине воины воинов воинам воинами воинах
вена вены вену веной вене венам венами венах
пат мат гол сет риф кот лес лис дом дома тихо быстро красная играет
'''.split()) | SHORT3
CYR = re.compile(r'^[а-яё]+$', re.I)

morph = MorphAnalyzer()

def clean(w):
    w = w.lower().replace('ё','е')
    return w if MIN_LEN <= len(w) <= MAX_LEN and CYR.fullmatch(w) else None

def acceptable_parse(p):
    return p.tag.POS in ALLOWED_POS and not (set(p.tag.grammemes) & BLOCK_GRAMMEMES)

def direct_threshold(n):
    return 99 if n == 3 else 3.60 if n == 4 else 3.35 if n == 5 else 3.15

def generated_threshold(n):
    return 99 if n == 3 else 3.20 if n == 4 else 2.75 if n == 5 else 2.35

seeds = top_n_list('ru', 60000)
lemmas = {}
direct = set()
for raw in seeds:
    w = clean(raw)
    if not w or w in BLACK:
        continue
    # Only the most probable analysis is allowed. This prevents a name, typo or
    # function word from entering through a rare alternative dictionary analysis.
    p = morph.parse(w)[0]
    if not acceptable_parse(p):
        continue
    direct.add(w)
    lemma = clean(p.normal_form)
    if lemma:
        lemmas.setdefault(lemma, p)

words = set(WHITE)
for w in direct:
    if zipf_frequency(w, 'ru') >= direct_threshold(len(w)):
        words.add(w)

for lemma, p in lemmas.items():
    if zipf_frequency(lemma, 'ru') < 3.50:
        continue
    for form in p.lexeme:
        if form.tag.POS not in ALLOWED_POS or set(form.tag.grammemes) & BLOCK_GRAMMEMES:
            continue
        w = clean(form.word)
        if not w or w in BLACK:
            continue
        if zipf_frequency(w, 'ru') >= generated_threshold(len(w)):
            words.add(w)

# The 3-letter set is exactly the curated set; generated short curiosities are never allowed.
words = {w for w in words if len(w) != 3 or w in SHORT3}
words -= BLACK
words = {w for w in words if clean(w) == w}
required = {'том','дуб','бук','учи','еду','воин','вена','пат','мат','гол','сет','риф','кот','лес','дом','тихо','быстро','красная','играет'}
missing = required - words
if missing:
    raise SystemExit(f'missing required words: {sorted(missing)}')
if BLACK & words:
    raise SystemExit(f'blacklisted words leaked: {sorted(BLACK & words)}')

ordered = sorted(words, key=lambda x: (len(x), x))
Path('words.txt').write_text('\n'.join(ordered) + '\n', encoding='utf-8')

counts = Counter(map(len, ordered))
report = [f'TOTAL\t{len(ordered)}']
report += [f'LEN_{n}\t{counts[n]}' for n in range(MIN_LEN, MAX_LEN + 1)]
report += ['', 'THREE_LETTER_WORDS']
for w in [x for x in ordered if len(x) == 3]:
    p = morph.parse(w)[0]
    report.append(f'{w}\t{zipf_frequency(w,"ru"):.2f}\t{p.normal_form}\t{p.tag.POS or "?"}')
Path('dictionary_report.txt').write_text('\n'.join(report) + '\n', encoding='utf-8')
print(f'Wrote {len(words)} controlled word forms')
