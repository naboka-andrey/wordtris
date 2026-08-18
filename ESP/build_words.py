from pathlib import Path
from collections import Counter
import re
import unicodedata

import spacy
from wordfreq import top_n_list, zipf_frequency

MIN_LEN, MAX_LEN = 3, 16
WORD_RE = re.compile(r'^[a-záéíóúüñ]+$', re.I)

# Three-letter strings occur by accident very often in WORDtris, so they are
# deliberately hand-curated instead of trusting a large corpus blindly.
SHORT3 = set('''
ahi aún aun ave bar boa cal can col con dar del día dio dos eco eje era ese esa eso fue fin fui gas hay haz hoy iba ida iré ley los las luz mal mar mas más mes mil muy nos ola oro osa oso pan paz pie por que red rey río sal sea sed ser sin sol son soy sur tal tan té te tí tia tía tio tío tos tres? uno uva vas vea ven ver vez voy web ya
amo ama dan das dio doy haz has lee leo pon sal sé se ten usa use va
'''.replace('tres?','').split())

# Explicitly required common words/forms. They also protect us against a POS
# tagger occasionally misreading a word in isolation.
WHITE = set('''
ser soy eres es somos sois son era eras éramos erais eran fui fuiste fue fuimos fuisteis fueron sido siendo
estar estoy estás está estamos estáis están estaba estabas estábamos estabais estaban estuve estuviste estuvo estuvimos estuvisteis estuvieron estado estando
tener tengo tienes tiene tenemos tenéis tienen tenía tenías teníamos tenían tuve tuviste tuvo tuvimos tuvieron tenido teniendo
hacer hago haces hace hacemos hacéis hacen hacía hacías hacíamos hacían hice hiciste hizo hicimos hicieron hecho haciendo
ir voy vas va vamos vais van iba ibas íbamos iban fui fuiste fue fuimos fueron ido yendo
decir digo dices dice decimos decís dicen decía dije dijiste dijo dijimos dijeron dicho diciendo
poder puedo puedes puede podemos podéis pueden podía pude pudo pudieron podido pudiendo
querer quiero quieres quiere queremos queréis quieren quería quise quiso quisieron querido queriendo
hablar hablo hablas habla hablamos habláis hablan hablé habló hablaron hablado hablando
comer como comes come comemos coméis comen comí comió comieron comido comiendo
vivir vivo vives vive vivimos vivís viven viví vivió vivieron vivido viviendo
venir vengo vienes viene venimos venís vienen vine vino vinieron venido viniendo
salir salgo sales sale salimos salís salen salí salió salieron salido saliendo
entrar entro entras entra entramos entráis entran entré entró entraron entrado entrando
casa casas libro libros mesa mesas silla sillas palabra palabras juego juegos amigo amiga amigos amigas niño niña niños niñas padre padres madre madres
agua aguas fuego fuegos aire aires tierra tierras mar mares río ríos lago lagos playa playas calle calles ciudad ciudades coche coches tren trenes hotel hoteles
música cine teatro mundo vida tiempo año años día días noche noches mano manos pie pies ojo ojos boca bocas sol luna
bien mal grande grandes pequeño pequeña pequeños pequeñas rojo roja rojos rojas verde verdes azul azules
'''.split()) | SHORT3

BLACK = set('''
www http https com org net app pdf jpg png html css js api url sms gps cpu gpu usb dvd
madrid barcelona españa spain mexico méxico argentina chile peru perú colombia venezuela
juan jose josé maria maría pedro pablo carlos david daniel ana laura lucia lucía
'''.split())

nlp = spacy.load('es_core_news_sm', disable=['parser', 'ner', 'lemmatizer'])


def clean(raw: str):
    w = unicodedata.normalize('NFC', raw.strip().lower())
    if MIN_LEN <= len(w) <= MAX_LEN and WORD_RE.fullmatch(w):
        return w
    return None


def threshold(n: int):
    if n == 3:
        return 99.0
    if n == 4:
        return 3.85
    if n == 5:
        return 3.55
    return 3.20

# wordfreq contains real surface forms, not only lemmas. This is important for
# Spanish: common conjugated verbs, plurals and gendered adjective forms are
# therefore included when people actually use them.
raw_candidates = []
seen = set()
for raw in top_n_list('es', 110000):
    w = clean(raw)
    if not w or w in seen or w in BLACK or len(w) == 3:
        continue
    if zipf_frequency(w, 'es') < threshold(len(w)):
        continue
    seen.add(w)
    raw_candidates.append(w)

words = set(WHITE)

# A contextual tagger is used as a second filter. We reject proper names,
# numbers, punctuation and unknown tokens; ordinary function words are allowed.
for w, doc in zip(raw_candidates, nlp.pipe(raw_candidates, batch_size=512)):
    if not doc or len(doc) != 1:
        continue
    tok = doc[0]
    if tok.pos_ in {'PROPN', 'NUM', 'PUNCT', 'SYM', 'X'}:
        continue
    if tok.is_oov and zipf_frequency(w, 'es') < 4.0:
        continue
    words.add(w)

words -= BLACK
words = {w for w in words if clean(w) == w and (len(w) != 3 or w in SHORT3)}

required = {
    'que','con','por','sin','del','los','las','una','uno','dos','más','muy',
    'ser','soy','eres','está','son','fue','fui','voy','vas','casa','casas',
    'hablo','hablas','habla','hablamos','comer','comiendo','vivir','viviendo',
    'tengo','tienes','tiene','hago','haces','hace','puedo','puedes','quiere',
    'niño','niña','años','día','días','música'
}
missing = required - words
if missing:
    raise SystemExit(f'missing required Spanish words: {sorted(missing)}')

ordered = sorted(words, key=lambda x: (len(x), x))
Path('ESP/words.txt').write_text('\n'.join(ordered) + '\n', encoding='utf-8')

counts = Counter(map(len, ordered))
report = [f'TOTAL\t{len(ordered)}']
report += [f'LEN_{n}\t{counts[n]}' for n in range(MIN_LEN, MAX_LEN + 1)]
report += ['', 'THREE_LETTER_WORDS']
report += sorted(w for w in ordered if len(w) == 3)
Path('ESP/dictionary_report.txt').write_text('\n'.join(report) + '\n', encoding='utf-8')
print(f'Wrote {len(ordered)} controlled Spanish word forms')
