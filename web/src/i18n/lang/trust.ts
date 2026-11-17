// Trust signals: the key-dates table on the yearly pages, the byline under article titles and the
// "how we work" (methodology) page. Texts per language.
import type { Lang } from '../config';

type Ecl = 'total solar eclipse' | 'annular solar eclipse' | 'partial solar eclipse' | 'hybrid solar eclipse'
  | 'total lunar eclipse' | 'partial lunar eclipse' | 'penumbral lunar eclipse';

export interface Trust {
  slug: string; nav: string; title: string; desc: string; byline: string;
  table: { h: string; cols: [string, string, string]; wholeYear: string; note: string; retro: string; areas: string[]; ecl: Record<Ecl, string> };
}

const ecl = (a: string[]): Record<Ecl, string> => ({
  'total solar eclipse': a[0], 'annular solar eclipse': a[1], 'partial solar eclipse': a[2], 'hybrid solar eclipse': a[0],
  'total lunar eclipse': a[3], 'partial lunar eclipse': a[4], 'penumbral lunar eclipse': a[5],
});

export const TRUST: Record<Lang, Trust> = {
  hr: {
    slug: 'kako-radimo', nav: 'Kako radimo', title: 'Kako radimo: izračun i nastanak tekstova · Mirastela',
    desc: 'Kako Mirastela izračunava položaje planeta i kako nastaju horoskopi i opisi na stranici.',
    byline: 'Izračunato iz astronomskih efemerida · Kako radimo',
    table: {
      h: 'Ključni datumi 2027. za znak {sign}', cols: ['Razdoblje', 'Što se događa', 'Područje života'], wholeYear: 'cijela godina',
      note: 'Datumi su izračunati iz astronomskih efemerida (Swiss Ephemeris), a područje života prema solarnim kućama za ovaj znak.',
      retro: '{planet} retrogradan {signIn}',
      areas: ['ja, tijelo i dojam', 'novac i vrijednosti', 'komunikacija i bliža okolina', 'dom i obitelj', 'ljubav, zabava i kreativnost', 'posao, rutine i zdravlje', 'partnerstva', 'zajednički novac i intima', 'putovanja, učenje i uvjerenja', 'karijera i ugled', 'prijatelji i planovi', 'odmor i unutarnji svijet'],
      ecl: ecl(['potpuna pomrčina Sunca', 'prstenasta pomrčina Sunca', 'djelomična pomrčina Sunca', 'potpuna pomrčina Mjeseca', 'djelomična pomrčina Mjeseca', 'polusjenovna pomrčina Mjeseca']),
    },
  },
  en: {
    slug: 'how-we-work', nav: 'How we work', title: 'How we work: calculations and texts · Mirastela',
    desc: 'How Mirastela calculates planetary positions and how the horoscopes and descriptions on the site are written.',
    byline: 'Calculated from astronomical ephemerides · How we work',
    table: {
      h: 'Key dates 2027: {sign}', cols: ['Period', 'What happens', 'Area of life'], wholeYear: 'all year',
      note: 'Dates calculated from astronomical ephemerides (Swiss Ephemeris); the area of life follows the solar houses for this sign.',
      retro: '{planet} retrograde {signIn}',
      areas: ['self, body and image', 'money and values', 'communication and surroundings', 'home and family', 'love, fun and creativity', 'work, routines and health', 'partnerships', 'shared money and intimacy', 'travel, study and beliefs', 'career and reputation', 'friends and plans', 'rest and inner life'],
      ecl: ecl(['total solar eclipse', 'annular solar eclipse', 'partial solar eclipse', 'total lunar eclipse', 'partial lunar eclipse', 'penumbral lunar eclipse']),
    },
  },
  pl: {
    slug: 'jak-pracujemy', nav: 'Jak pracujemy', title: 'Jak pracujemy: obliczenia i teksty · Mirastela',
    desc: 'Jak Mirastela oblicza położenie planet i jak powstają horoskopy oraz opisy na stronie.',
    byline: 'Obliczone na podstawie efemeryd astronomicznych · Jak pracujemy',
    table: {
      h: 'Najważniejsze daty 2027: {sign}', cols: ['Okres', 'Co się dzieje', 'Obszar życia'], wholeYear: 'cały rok',
      note: 'Daty obliczone na podstawie efemeryd astronomicznych (Swiss Ephemeris), obszar życia według domów słonecznych dla tego znaku.',
      retro: '{planet} retrogradny {signIn}',
      areas: ['ja, ciało i wizerunek', 'pieniądze i wartości', 'komunikacja i otoczenie', 'dom i rodzina', 'miłość, zabawa i twórczość', 'praca, rutyna i zdrowie', 'związki partnerskie', 'wspólne finanse i bliskość', 'podróże, nauka i przekonania', 'kariera i reputacja', 'przyjaciele i plany', 'odpoczynek i życie wewnętrzne'],
      ecl: ecl(['całkowite zaćmienie Słońca', 'obrączkowe zaćmienie Słońca', 'częściowe zaćmienie Słońca', 'całkowite zaćmienie Księżyca', 'częściowe zaćmienie Księżyca', 'półcieniowe zaćmienie Księżyca']),
    },
  },
  sl: {
    slug: 'kako-delamo', nav: 'Kako delamo', title: 'Kako delamo: izračuni in besedila · Mirastela',
    desc: 'Kako Mirastela izračuna položaje planetov in kako nastanejo horoskopi ter opisi na strani.',
    byline: 'Izračunano iz astronomskih efemerid · Kako delamo',
    table: {
      h: 'Ključni datumi 2027: {sign}', cols: ['Obdobje', 'Kaj se dogaja', 'Področje življenja'], wholeYear: 'vse leto',
      note: 'Datumi so izračunani iz astronomskih efemerid (Swiss Ephemeris), področje življenja pa po sončnih hišah za to znamenje.',
      retro: '{planet} retrograden {signIn}',
      areas: ['jaz, telo in vtis', 'denar in vrednote', 'komunikacija in okolica', 'dom in družina', 'ljubezen, zabava in ustvarjalnost', 'delo, rutina in zdravje', 'partnerstva', 'skupni denar in intimnost', 'potovanja, učenje in prepričanja', 'kariera in ugled', 'prijatelji in načrti', 'počitek in notranji svet'],
      ecl: ecl(['popolni Sončev mrk', 'kolobarjasti Sončev mrk', 'delni Sončev mrk', 'popolni Lunin mrk', 'delni Lunin mrk', 'polsenčni Lunin mrk']),
    },
  },
  ro: {
    slug: 'cum-lucram', nav: 'Cum lucrăm', title: 'Cum lucrăm: calcule și texte · Mirastela',
    desc: 'Cum calculează Mirastela pozițiile planetelor și cum sunt scrise horoscoapele și descrierile de pe site.',
    byline: 'Calculat din efemeride astronomice · Cum lucrăm',
    table: {
      h: 'Date-cheie 2027: {sign}', cols: ['Perioada', 'Ce se întâmplă', 'Domeniul vieții'], wholeYear: 'tot anul',
      note: 'Datele sunt calculate din efemeride astronomice (Swiss Ephemeris), iar domeniul vieții după casele solare pentru această zodie.',
      retro: '{planet} retrograd {signIn}',
      areas: ['sine, corp și imagine', 'bani și valori', 'comunicare și anturaj', 'casă și familie', 'iubire, distracție și creativitate', 'muncă, rutină și sănătate', 'parteneriate', 'bani comuni și intimitate', 'călătorii, studii și convingeri', 'carieră și reputație', 'prieteni și planuri', 'odihnă și viață interioară'],
      ecl: ecl(['eclipsă totală de Soare', 'eclipsă inelară de Soare', 'eclipsă parțială de Soare', 'eclipsă totală de Lună', 'eclipsă parțială de Lună', 'eclipsă de Lună prin penumbră']),
    },
  },
  cs: {
    slug: 'jak-pracujeme', nav: 'Jak pracujeme', title: 'Jak pracujeme: výpočty a texty · Mirastela',
    desc: 'Jak Mirastela počítá polohy planet a jak vznikají horoskopy a popisy na webu.',
    byline: 'Vypočteno z astronomických efemerid · Jak pracujeme',
    table: {
      h: 'Klíčová data 2027: {sign}', cols: ['Období', 'Co se děje', 'Oblast života'], wholeYear: 'celý rok',
      note: 'Data jsou vypočtena z astronomických efemerid (Swiss Ephemeris), oblast života podle slunečních domů pro toto znamení.',
      retro: '{planet} retrográdní {signIn}',
      areas: ['já, tělo a dojem', 'peníze a hodnoty', 'komunikace a okolí', 'domov a rodina', 'láska, zábava a tvořivost', 'práce, rutina a zdraví', 'partnerství', 'společné peníze a intimita', 'cestování, studium a přesvědčení', 'kariéra a pověst', 'přátelé a plány', 'odpočinek a vnitřní svět'],
      ecl: ecl(['úplné zatmění Slunce', 'prstencové zatmění Slunce', 'částečné zatmění Slunce', 'úplné zatmění Měsíce', 'částečné zatmění Měsíce', 'polostínové zatmění Měsíce']),
    },
  },
  hu: {
    slug: 'hogyan-dolgozunk', nav: 'Hogyan dolgozunk', title: 'Hogyan dolgozunk: számítások és szövegek · Mirastela',
    desc: 'Hogyan számolja a Mirastela a bolygók helyzetét, és hogyan készülnek a horoszkópok és leírások.',
    byline: 'Csillagászati efemeridákból számolva · Hogyan dolgozunk',
    table: {
      h: 'Fontos dátumok 2027: {sign}', cols: ['Időszak', 'Mi történik', 'Életterület'], wholeYear: 'egész évben',
      note: 'A dátumokat csillagászati efemeridákból számoljuk (Swiss Ephemeris), az életterületet pedig a csillagjegy szoláris házai szerint.',
      retro: '{planet} retrográd {signIn}',
      areas: ['önmagad, test és megjelenés', 'pénz és értékek', 'kommunikáció és környezet', 'otthon és család', 'szerelem, szórakozás és kreativitás', 'munka, rutin és egészség', 'párkapcsolatok', 'közös pénz és intimitás', 'utazás, tanulás és hit', 'karrier és hírnév', 'barátok és tervek', 'pihenés és belső világ'],
      ecl: ecl(['teljes napfogyatkozás', 'gyűrűs napfogyatkozás', 'részleges napfogyatkozás', 'teljes holdfogyatkozás', 'részleges holdfogyatkozás', 'félárnyékos holdfogyatkozás']),
    },
  },
  de: {
    slug: 'so-arbeiten-wir', nav: 'So arbeiten wir', title: 'So arbeiten wir: Berechnung und Texte · Mirastela',
    desc: 'Wie Mirastela Planetenstände berechnet und wie die Horoskope und Beschreibungen auf der Seite entstehen.',
    byline: 'Aus astronomischen Ephemeriden berechnet · So arbeiten wir',
    table: {
      h: 'Wichtige Termine 2027: {sign}', cols: ['Zeitraum', 'Was passiert', 'Lebensbereich'], wholeYear: 'ganzes Jahr',
      note: 'Die Daten sind aus astronomischen Ephemeriden berechnet (Swiss Ephemeris), der Lebensbereich nach den Sonnenhäusern dieses Zeichens.',
      retro: '{planet} rückläufig {signIn}',
      areas: ['Ich, Körper und Ausstrahlung', 'Geld und Werte', 'Kommunikation und Umfeld', 'Zuhause und Familie', 'Liebe, Spaß und Kreativität', 'Arbeit, Alltag und Gesundheit', 'Partnerschaften', 'gemeinsames Geld und Intimität', 'Reisen, Lernen und Überzeugungen', 'Karriere und Ansehen', 'Freunde und Pläne', 'Rückzug und Innenleben'],
      ecl: ecl(['totale Sonnenfinsternis', 'ringförmige Sonnenfinsternis', 'partielle Sonnenfinsternis', 'totale Mondfinsternis', 'partielle Mondfinsternis', 'Halbschatten-Mondfinsternis']),
    },
  },
  fr: {
    slug: 'notre-methode', nav: 'Notre méthode', title: 'Notre méthode : calculs et textes · Mirastela',
    desc: 'Comment Mirastela calcule la position des planètes et comment sont rédigés les horoscopes et descriptions du site.',
    byline: 'Calculé à partir des éphémérides astronomiques · Notre méthode',
    table: {
      h: 'Dates clés 2027 : {sign}', cols: ['Période', 'Ce qui se passe', 'Domaine de vie'], wholeYear: "toute l'année",
      note: 'Dates calculées à partir des éphémérides astronomiques (Swiss Ephemeris), domaine de vie selon les maisons solaires de ce signe.',
      retro: '{planet} rétrograde {signIn}',
      areas: ['soi, corps et image', 'argent et valeurs', 'communication et entourage', 'foyer et famille', 'amour, loisirs et créativité', 'travail, routine et santé', 'partenariats', 'argent partagé et intimité', 'voyages, études et convictions', 'carrière et réputation', 'amis et projets', 'repos et vie intérieure'],
      ecl: ecl(['éclipse totale de Soleil', 'éclipse annulaire de Soleil', 'éclipse partielle de Soleil', 'éclipse totale de Lune', 'éclipse partielle de Lune', 'éclipse pénombrale de Lune']),
    },
  },
  it: {
    slug: 'il-nostro-metodo', nav: 'Il nostro metodo', title: 'Il nostro metodo: calcoli e testi · Mirastela',
    desc: 'Come Mirastela calcola le posizioni dei pianeti e come nascono gli oroscopi e le descrizioni del sito.',
    byline: 'Calcolato dalle effemeridi astronomiche · Il nostro metodo',
    table: {
      h: 'Date chiave 2027: {sign}', cols: ['Periodo', 'Cosa succede', 'Area della vita'], wholeYear: "tutto l'anno",
      note: 'Date calcolate dalle effemeridi astronomiche (Swiss Ephemeris), area della vita secondo le case solari di questo segno.',
      retro: '{planet} retrogrado {signIn}',
      areas: ['sé, corpo e immagine', 'denaro e valori', 'comunicazione e ambiente vicino', 'casa e famiglia', 'amore, svago e creatività', 'lavoro, routine e salute', 'relazioni di coppia', 'denaro condiviso e intimità', 'viaggi, studio e convinzioni', 'carriera e reputazione', 'amici e progetti', 'riposo e vita interiore'],
      ecl: ecl(['eclissi totale di Sole', 'eclissi anulare di Sole', 'eclissi parziale di Sole', 'eclissi totale di Luna', 'eclissi parziale di Luna', 'eclissi lunare di penombra']),
    },
  },
  es: {
    slug: 'como-trabajamos', nav: 'Cómo trabajamos', title: 'Cómo trabajamos: cálculos y textos · Mirastela',
    desc: 'Cómo calcula Mirastela la posición de los planetas y cómo se escriben los horóscopos y descripciones del sitio.',
    byline: 'Calculado con efemérides astronómicas · Cómo trabajamos',
    table: {
      h: 'Fechas clave 2027: {sign}', cols: ['Periodo', 'Qué ocurre', 'Área de la vida'], wholeYear: 'todo el año',
      note: 'Fechas calculadas con efemérides astronómicas (Swiss Ephemeris) y área de la vida según las casas solares de este signo.',
      retro: '{planet} retrógrado {signIn}',
      areas: ['yo, cuerpo e imagen', 'dinero y valores', 'comunicación y entorno', 'hogar y familia', 'amor, ocio y creatividad', 'trabajo, rutina y salud', 'relaciones de pareja', 'dinero compartido e intimidad', 'viajes, estudios y creencias', 'carrera y reputación', 'amigos y proyectos', 'descanso y vida interior'],
      ecl: ecl(['eclipse total de Sol', 'eclipse anular de Sol', 'eclipse parcial de Sol', 'eclipse total de Luna', 'eclipse parcial de Luna', 'eclipse lunar penumbral']),
    },
  },
};
