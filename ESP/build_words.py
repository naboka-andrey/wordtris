from pathlib import Path
from collections import Counter
from urllib.request import Request, urlopen
import re
import unicodedata

MIN_LEN, MAX_LEN = 3, 16
WORD_RE = re.compile(r'^[a-záéíóúüñ]+$', re.I)
SOURCE = 'https://raw.githubusercontent.com/mazyvan/most-common-spanish-words/master/most-common-spanish-words-v4.txt'

# Three-letter strings appear accidentally very often in WORDtris, so they are
# hand-curated instead of accepting every short corpus token.
SHORT3 = set('''
ahí ahi aun aún ave bar boa cal can col con dar del día dio dos eco eje era ese esa eso fue fin fui gas han hay haz hoy iba ida iré ley los las luz mal mar mas más mes mil mis muy nos ola oro osa oso pan paz pie por que qué red rey río sal sea sed ser sin sol son soy sur sus tal tan ten tía tia tío tio tos tus uno uva vas vea ven ver vez voy amo ama dan das doy has lee leo pon usa use año
'''.split())

# Protect ordinary forms that should always be playable even if the upstream
# frequency list changes.
WHITE = set('''
ser soy eres somos sois son era eras éramos erais eran fui fuiste fue fuimos fuisteis fueron sido siendo
estar estoy estás está estamos estáis están estaba estabas estábamos estabais estaban estuve estuviste estuvo estuvimos estuvisteis estuvieron estado estando
tener tengo tienes tiene tenemos tenéis tienen tenía tenías teníamos tenían tuve tuviste tuvo tuvimos tuvieron tenido teniendo
hacer hago haces hace hacemos hacéis hacen hacía hacías hacíamos hacían hice hiciste hizo hicimos hicieron hecho haciendo
voy vas vamos vais van iba ibas íbamos iban ido yendo
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

# Common proper names, places, abbreviations and web/technical tokens that can
# occur in subtitle-derived frequency lists but should not count as vocabulary.
BLACK = set('''
www http https com org net app pdf jpg jpeg png html css javascript api url sms gps cpu gpu usb dvd
madrid barcelona valencia sevilla malaga málaga bilbao zaragoza españa mexico méxico argentina chile peru perú colombia venezuela brasil brazil cuba ecuador bolivia paraguay uruguay panama panamá
juan jose josé maria maría pedro pablo carlos david daniel miguel angel ángel antonio manuel francisco javier alejandro fernando sergio diego alberto raul raúl ruben rubén jorge luis jesus jesús
ana laura lucia lucía carmen elena isabel paula sara sofia sofía marta patricia monica mónica sandra rosa beatriz natalia cristina silvia teresa
john jack mike michael james robert william george richard thomas charles
messi ronaldo google facebook instagram twitter youtube whatsapp tiktok amazon apple microsoft samsung sony
'''.split())


def clean(raw: str):
    w = unicodedata.normalize('NFC', raw.strip().lower())
    if MIN_LEN <= len(w) <= MAX_LEN and WORD_RE.fullmatch(w):
        return w
    return None


def accepted(raw: str):
    w = clean(raw)
    if not w or w in BLACK:
        return None
    if len(w) == 3 and w not in SHORT3:
        return None
    return w

req = Request(SOURCE, headers={'User-Agent': 'WORDtris-dictionary-builder/1.0'})
with urlopen(req, timeout=30) as response:
    text = response.read().decode('utf-8')

words = set(WHITE)
for line in text.splitlines():
    w = accepted(line)
    if w:
        words.add(w)

words -= BLACK
words = {w for w in words if accepted(w) == w}

required = {
    'que','qué','con','por','sin','del','los','las','una','uno','dos','más','muy',
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
