import type { Lang } from '../config';

// Second wave of SEO pages: the Moon sign calculator and the sub-pages of the yearly forecast (love, work)
// and of compatibility (friendship). Long texts come from api/seo_gen.py (kinds love, work, friend).
export interface Seo2 {
  moonSlug: string;
  moon: { nav: string; title: string; desc: string; h1: string; intro: string; aboutTitle: string; about: string };
  sub: { love: string; work: string; friend: string };
  love: { more: string; title: string; h1: string; h: { overview: string; single: string; couple: string; periods: string; advice: string } };
  work: { more: string; title: string; h1: string; h: { overview: string; career: string; money: string; periods: string; advice: string } };
  friend: { more: string; title: string; h1: string; h: { overall: string; strengths: string; challenges: string; tips: string } };
}

export const SEO2: Record<Lang, Seo2> = {
  hr: {
    moonSlug: 'kalkulator-mjesecevog-znaka',
    moon: {
      nav: 'Mjesečev znak', title: 'Kalkulator Mjesečevog znaka: Sunce, Mjesec i podznak · Mirastela',
      desc: 'Besplatno izračunaj u kojem je znaku bio Mjesec u trenutku tvog rođenja, uz Sunčev znak i podznak. Trebaju ti datum, vrijeme i mjesto rođenja.',
      h1: 'Kalkulator Mjesečevog znaka',
      intro: 'Upiši datum, vrijeme i mjesto rođenja. Izračunat ćemo tvoj Mjesečev znak, a uz njega i Sunčev znak i podznak, prema stvarnom položaju planeta.',
      aboutTitle: 'Što je Mjesečev znak?',
      about: 'Mjesečev znak je znak u kojem je Mjesec stajao u trenutku tvog rođenja. Dok Sunčev znak opisuje tko si, Mjesec govori kako osjećaš, što ti treba da se osjećaš sigurno i kako reagiraš kad nitko ne gleda. Mjesec mijenja znak svakih dva do tri dana, pa za siguran izračun pomaže i vrijeme rođenja.',
    },
    sub: { love: 'ljubav', work: 'posao', friend: 'prijateljstvo' },
    love: { more: 'Ljubav u 2027. za ostale znakove', title: '{sign} 2027: ljubavni horoskop · Mirastela', h1: '{sign}: ljubav u 2027.', h: { overview: 'Ljubav u 2027.', single: 'Ako nemaš partnera', couple: 'Ako si u vezi', periods: 'Najvažnija razdoblja za ljubav', advice: 'Savjet za ljubav u 2027.' } },
    work: { more: 'Posao u 2027. za ostale znakove', title: '{sign} 2027: posao i novac · Mirastela', h1: '{sign}: posao i novac u 2027.', h: { overview: 'Posao u 2027.', career: 'Karijera i prilike', money: 'Novac', periods: 'Najvažnija razdoblja za posao', advice: 'Savjet za posao u 2027.' } },
    friend: { more: '{sign}: prijateljstvo s ostalim znakovima', title: '{a} i {b}: prijateljstvo · Mirastela', h1: '{a} i {b} kao prijatelji', h: { overall: 'Kakvo je to prijateljstvo', strengths: 'Što ih povezuje', challenges: 'Gdje se sudaraju', tips: 'Kako sačuvati prijateljstvo' } },
  },
  pl: {
    moonSlug: 'kalkulator-znaku-ksiezyca',
    moon: {
      nav: 'Znak Księżyca', title: 'Kalkulator znaku Księżyca: Słońce, Księżyc i Ascendent · Mirastela',
      desc: 'Oblicz za darmo, w jakim znaku był Księżyc w chwili Twoich narodzin, razem ze znakiem Słońca i Ascendentem. Potrzebne są data, godzina i miejsce urodzenia.',
      h1: 'Kalkulator znaku Księżyca',
      intro: 'Podaj datę, godzinę i miejsce urodzenia. Obliczymy Twój znak Księżyca, a do tego znak Słońca i Ascendent, na podstawie rzeczywistego położenia planet.',
      aboutTitle: 'Czym jest znak Księżyca?',
      about: 'Znak Księżyca to znak, w którym stał Księżyc w chwili Twoich narodzin. Znak Słońca opisuje, kim jesteś, a Księżyc mówi o tym, co czujesz, czego potrzebujesz, by czuć się bezpiecznie, i jak reagujesz, gdy nikt nie patrzy. Księżyc zmienia znak co dwa, trzy dni, dlatego godzina urodzenia pomaga w dokładnym obliczeniu.',
    },
    sub: { love: 'milosc', work: 'praca', friend: 'przyjazn' },
    love: { more: 'Miłość w 2027 dla innych znaków', title: '{sign} 2027: horoskop miłosny · Mirastela', h1: '{sign}: miłość w 2027 roku', h: { overview: 'Miłość w 2027 roku', single: 'Jeśli nie masz partnera', couple: 'Jeśli jesteś w związku', periods: 'Najważniejsze okresy dla miłości', advice: 'Rada na miłość w 2027' } },
    work: { more: 'Praca w 2027 dla innych znaków', title: '{sign} 2027: praca i pieniądze · Mirastela', h1: '{sign}: praca i pieniądze w 2027 roku', h: { overview: 'Praca w 2027 roku', career: 'Kariera i szanse', money: 'Pieniądze', periods: 'Najważniejsze okresy dla pracy', advice: 'Rada na pracę w 2027' } },
    friend: { more: '{sign}: przyjaźń z innymi znakami', title: '{a} i {b}: przyjaźń · Mirastela', h1: '{a} i {b} jako przyjaciele', h: { overall: 'Jaka to przyjaźń', strengths: 'Co ich łączy', challenges: 'Gdzie się ścierają', tips: 'Jak dbać o tę przyjaźń' } },
  },
  sl: {
    moonSlug: 'izracun-luninega-znamenja',
    moon: {
      nav: 'Lunino znamenje', title: 'Izračun luninega znamenja: Sonce, Luna in ascendent · Mirastela',
      desc: 'Brezplačno izračunaj, v katerem znamenju je bila Luna ob tvojem rojstvu, skupaj s sončnim znamenjem in ascendentom. Potrebuješ datum, uro in kraj rojstva.',
      h1: 'Izračun luninega znamenja',
      intro: 'Vpiši datum, uro in kraj rojstva. Izračunali bomo tvoje lunino znamenje, poleg tega pa še sončno znamenje in ascendent, po resničnem položaju planetov.',
      aboutTitle: 'Kaj je lunino znamenje?',
      about: 'Lunino znamenje je znamenje, v katerem je stala Luna ob tvojem rojstvu. Sončno znamenje opisuje, kdo si, Luna pa pove, kako čutiš, kaj potrebuješ, da se počutiš varno, in kako se odzoveš, ko te nihče ne gleda. Luna zamenja znamenje vsake dva do tri dni, zato ura rojstva pomaga pri natančnem izračunu.',
    },
    sub: { love: 'ljubezen', work: 'delo', friend: 'prijateljstvo' },
    love: { more: 'Ljubezen v letu 2027 za druga znamenja', title: '{sign} 2027: ljubezenski horoskop · Mirastela', h1: '{sign}: ljubezen v letu 2027', h: { overview: 'Ljubezen v letu 2027', single: 'Če nimaš partnerja', couple: 'Če si v zvezi', periods: 'Najpomembnejša obdobja za ljubezen', advice: 'Nasvet za ljubezen v letu 2027' } },
    work: { more: 'Delo v letu 2027 za druga znamenja', title: '{sign} 2027: delo in denar · Mirastela', h1: '{sign}: delo in denar v letu 2027', h: { overview: 'Delo v letu 2027', career: 'Kariera in priložnosti', money: 'Denar', periods: 'Najpomembnejša obdobja za delo', advice: 'Nasvet za delo v letu 2027' } },
    friend: { more: '{sign}: prijateljstvo z drugimi znamenji', title: '{a} in {b}: prijateljstvo · Mirastela', h1: '{a} in {b} kot prijatelja', h: { overall: 'Kakšno je to prijateljstvo', strengths: 'Kaj ju povezuje', challenges: 'Kje se kresata', tips: 'Kako ohraniti prijateljstvo' } },
  },
  ro: {
    moonSlug: 'calculator-zodie-lunara',
    moon: {
      nav: 'Zodia lunară', title: 'Calculator zodie lunară: Soarele, Luna și ascendentul · Mirastela',
      desc: 'Află gratuit în ce zodie era Luna când te-ai născut, împreună cu zodia solară și ascendentul. Ai nevoie de data, ora și locul nașterii.',
      h1: 'Calculator zodie lunară',
      intro: 'Introdu data, ora și locul nașterii. Îți calculăm zodia lunară, plus zodia solară și ascendentul, după poziția reală a planetelor.',
      aboutTitle: 'Ce este zodia lunară?',
      about: 'Zodia lunară este semnul în care se afla Luna în momentul nașterii tale. Zodia solară descrie cine ești, iar Luna arată ce simți, de ce ai nevoie ca să te simți în siguranță și cum reacționezi când nu te vede nimeni. Luna schimbă semnul la fiecare două, trei zile, așa că ora nașterii ajută la un calcul exact.',
    },
    sub: { love: 'dragoste', work: 'cariera', friend: 'prietenie' },
    love: { more: 'Dragostea în 2027 pentru celelalte zodii', title: '{sign} 2027: horoscopul iubirii · Mirastela', h1: '{sign}: dragostea în 2027', h: { overview: 'Dragostea în 2027', single: 'Dacă nu ai un partener', couple: 'Dacă ești într-o relație', periods: 'Cele mai importante perioade pentru iubire', advice: 'Sfatul pentru iubire în 2027' } },
    work: { more: 'Cariera în 2027 pentru celelalte zodii', title: '{sign} 2027: carieră și bani · Mirastela', h1: '{sign}: cariera și banii în 2027', h: { overview: 'Munca în 2027', career: 'Carieră și oportunități', money: 'Bani', periods: 'Cele mai importante perioade pentru muncă', advice: 'Sfatul pentru muncă în 2027' } },
    friend: { more: '{sign}: prietenia cu celelalte zodii', title: '{a} și {b}: prietenie · Mirastela', h1: '{a} și {b} ca prieteni', h: { overall: 'Cum este această prietenie', strengths: 'Ce îi apropie', challenges: 'Unde se ciocnesc', tips: 'Cum păstrezi această prietenie' } },
  },
  cs: {
    moonSlug: 'vypocet-mesicniho-znameni',
    moon: {
      nav: 'Měsíční znamení', title: 'Výpočet měsíčního znamení: Slunce, Měsíc a ascendent · Mirastela',
      desc: 'Zdarma zjisti, v jakém znamení byl Měsíc v okamžiku tvého narození, spolu se slunečním znamením a ascendentem. Stačí datum, čas a místo narození.',
      h1: 'Výpočet měsíčního znamení',
      intro: 'Zadej datum, čas a místo narození. Spočítáme tvé měsíční znamení a k tomu sluneční znamení a ascendent, podle skutečné polohy planet.',
      aboutTitle: 'Co je měsíční znamení?',
      about: 'Měsíční znamení je znamení, ve kterém stál Měsíc v okamžiku tvého narození. Sluneční znamení popisuje, kdo jsi, Měsíc říká, jak cítíš, co potřebuješ k pocitu bezpečí, a jak reaguješ, když se nikdo nedívá. Měsíc mění znamení každé dva až tři dny, proto čas narození pomáhá k přesnému výpočtu.',
    },
    sub: { love: 'laska', work: 'prace', friend: 'pratelstvi' },
    love: { more: 'Láska v roce 2027 pro ostatní znamení', title: '{sign} 2027: horoskop lásky · Mirastela', h1: '{sign}: láska v roce 2027', h: { overview: 'Láska v roce 2027', single: 'Pokud nemáš partnera', couple: 'Pokud máš partnera', periods: 'Nejdůležitější období pro lásku', advice: 'Rada pro lásku v roce 2027' } },
    work: { more: 'Práce v roce 2027 pro ostatní znamení', title: '{sign} 2027: práce a peníze · Mirastela', h1: '{sign}: práce a peníze v roce 2027', h: { overview: 'Práce v roce 2027', career: 'Kariéra a příležitosti', money: 'Peníze', periods: 'Nejdůležitější období pro práci', advice: 'Rada pro práci v roce 2027' } },
    friend: { more: '{sign}: přátelství s ostatními znameními', title: '{a} a {b}: přátelství · Mirastela', h1: '{a} a {b} jako přátelé', h: { overall: 'Jaké je to přátelství', strengths: 'Co je spojuje', challenges: 'Kde se střetávají', tips: 'Jak přátelství udržet' } },
  },
  hu: {
    moonSlug: 'holdjegy-kalkulator',
    moon: {
      nav: 'Holdjegy', title: 'Holdjegy kalkulátor: Nap, Hold és aszcendens · Mirastela',
      desc: 'Számold ki ingyen, melyik jegyben állt a Hold, amikor születtél, a napjegyeddel és az aszcendenseddel együtt. Kell hozzá a születés dátuma, ideje és helye.',
      h1: 'Holdjegy kalkulátor',
      intro: 'Add meg a születésed dátumát, idejét és helyét. Kiszámoljuk a holdjegyedet, mellé a napjegyedet és az aszcendensedet, a bolygók valós helyzete alapján.',
      aboutTitle: 'Mi az a holdjegy?',
      about: 'A holdjegy az a jegy, amelyben a Hold a születésed pillanatában állt. A napjegy azt írja le, ki vagy, a Hold pedig azt, hogyan érzel, mire van szükséged a biztonságérzethez, és hogyan reagálsz, amikor senki sem lát. A Hold két-három naponta jegyet vált, ezért a születési idő segít a pontos számításban.',
    },
    sub: { love: 'szerelem', work: 'munka', friend: 'baratsag' },
    love: { more: 'Szerelem 2027-ben a többi jegynek', title: '{sign} 2027: szerelmi horoszkóp · Mirastela', h1: '{sign}: szerelem 2027-ben', h: { overview: 'Szerelem 2027-ben', single: 'Ha egyedülálló vagy', couple: 'Ha párkapcsolatban élsz', periods: 'A szerelem legfontosabb időszakai', advice: 'Tanács a szerelemhez 2027-re' } },
    work: { more: 'Munka 2027-ben a többi jegynek', title: '{sign} 2027: munka és pénz · Mirastela', h1: '{sign}: munka és pénz 2027-ben', h: { overview: 'Munka 2027-ben', career: 'Karrier és lehetőségek', money: 'Pénz', periods: 'A munka legfontosabb időszakai', advice: 'Tanács a munkához 2027-re' } },
    friend: { more: '{sign}: barátság a többi jeggyel', title: '{a} és {b}: barátság · Mirastela', h1: '{a} és {b} barátként', h: { overall: 'Milyen ez a barátság', strengths: 'Mi köti össze őket', challenges: 'Hol ütköznek', tips: 'Hogyan tartható meg a barátság' } },
  },
  de: {
    moonSlug: 'mondzeichen-berechnen',
    moon: {
      nav: 'Mondzeichen', title: 'Mondzeichen berechnen: Sonne, Mond und Aszendent · Mirastela',
      desc: 'Berechne kostenlos, in welchem Zeichen der Mond bei deiner Geburt stand, zusammen mit Sonnenzeichen und Aszendent. Du brauchst Datum, Uhrzeit und Ort der Geburt.',
      h1: 'Mondzeichen berechnen',
      intro: 'Gib Datum, Uhrzeit und Ort deiner Geburt ein. Wir berechnen dein Mondzeichen und dazu dein Sonnenzeichen und deinen Aszendenten, nach der tatsächlichen Stellung der Planeten.',
      aboutTitle: 'Was ist das Mondzeichen?',
      about: 'Das Mondzeichen ist das Zeichen, in dem der Mond im Moment deiner Geburt stand. Das Sonnenzeichen beschreibt, wer du bist, der Mond zeigt, wie du fühlst, was du brauchst, um dich sicher zu fühlen, und wie du reagierst, wenn niemand hinsieht. Der Mond wechselt alle zwei bis drei Tage das Zeichen, deshalb hilft die Geburtszeit bei einer genauen Berechnung.',
    },
    sub: { love: 'liebe', work: 'beruf', friend: 'freundschaft' },
    love: { more: 'Liebe 2027 für die anderen Zeichen', title: '{sign} 2027: Liebeshoroskop · Mirastela', h1: '{sign}: Liebe 2027', h: { overview: 'Die Liebe 2027', single: 'Wenn du Single bist', couple: 'Wenn du in einer Beziehung bist', periods: 'Die wichtigsten Phasen für die Liebe', advice: 'Dein Liebesrat für 2027' } },
    work: { more: 'Beruf 2027 für die anderen Zeichen', title: '{sign} 2027: Beruf und Finanzen · Mirastela', h1: '{sign}: Beruf und Geld 2027', h: { overview: 'Der Beruf 2027', career: 'Karriere und Chancen', money: 'Geld', periods: 'Die wichtigsten Phasen für den Beruf', advice: 'Dein Rat für den Beruf 2027' } },
    friend: { more: '{sign}: Freundschaft mit den anderen Zeichen', title: '{a} und {b}: Freundschaft · Mirastela', h1: '{a} und {b} als Freunde', h: { overall: 'Wie diese Freundschaft ist', strengths: 'Was sie verbindet', challenges: 'Wo es reibt', tips: 'So bleibt die Freundschaft stark' } },
  },
  fr: {
    moonSlug: 'calcul-signe-lunaire',
    moon: {
      nav: 'Signe lunaire', title: 'Calcul du signe lunaire : Soleil, Lune et ascendant · Mirastela',
      desc: 'Calcule gratuitement dans quel signe se trouvait la Lune à ta naissance, avec ton signe solaire et ton ascendant. Il te faut la date, l’heure et le lieu de naissance.',
      h1: 'Calcul du signe lunaire',
      intro: 'Saisis ta date, ton heure et ton lieu de naissance. Nous calculons ton signe lunaire, ainsi que ton signe solaire et ton ascendant, d’après la position réelle des planètes.',
      aboutTitle: 'Qu’est-ce que le signe lunaire ?',
      about: 'Le signe lunaire est le signe dans lequel se trouvait la Lune au moment de ta naissance. Le signe solaire décrit qui tu es, la Lune dit ce que tu ressens, ce dont tu as besoin pour te sentir en sécurité et comment tu réagis quand personne ne regarde. La Lune change de signe tous les deux ou trois jours, donc l’heure de naissance aide à un calcul précis.',
    },
    sub: { love: 'amour', work: 'travail', friend: 'amitie' },
    love: { more: 'L’amour en 2027 pour les autres signes', title: '{sign} 2027 : horoscope amoureux · Mirastela', h1: '{sign} : l’amour en 2027', h: { overview: 'L’amour en 2027', single: 'Si tu es célibataire', couple: 'Si tu es en couple', periods: 'Les périodes clés pour l’amour', advice: 'Le conseil amour pour 2027' } },
    work: { more: 'Le travail en 2027 pour les autres signes', title: '{sign} 2027 : travail et argent · Mirastela', h1: '{sign} : travail et argent en 2027', h: { overview: 'Le travail en 2027', career: 'Carrière et opportunités', money: 'Argent', periods: 'Les périodes clés pour le travail', advice: 'Le conseil travail pour 2027' } },
    friend: { more: '{sign} : l’amitié avec les autres signes', title: '{a} et {b} : amitié · Mirastela', h1: '{a} et {b} en amitié', h: { overall: 'Comment est cette amitié', strengths: 'Ce qui les rapproche', challenges: 'Là où ça frotte', tips: 'Comment garder cette amitié' } },
  },
  it: {
    moonSlug: 'calcolo-segno-lunare',
    moon: {
      nav: 'Segno lunare', title: 'Calcolo del segno lunare: Sole, Luna e ascendente · Mirastela',
      desc: 'Calcola gratis in che segno era la Luna al momento della tua nascita, insieme al segno solare e all’ascendente. Servono data, ora e luogo di nascita.',
      h1: 'Calcolo del segno lunare',
      intro: 'Inserisci data, ora e luogo di nascita. Calcoliamo il tuo segno lunare e, insieme, il segno solare e l’ascendente, secondo la posizione reale dei pianeti.',
      aboutTitle: 'Che cos’è il segno lunare?',
      about: 'Il segno lunare è il segno in cui si trovava la Luna al momento della tua nascita. Il segno solare descrive chi sei, la Luna racconta come senti, di cosa hai bisogno per sentirti al sicuro e come reagisci quando nessuno ti guarda. La Luna cambia segno ogni due o tre giorni, per questo l’ora di nascita aiuta a un calcolo preciso.',
    },
    sub: { love: 'amore', work: 'lavoro', friend: 'amicizia' },
    love: { more: 'L’amore nel 2027 per gli altri segni', title: 'Oroscopo 2027 {sign} in amore · Mirastela', h1: '{sign}: l’amore nel 2027', h: { overview: 'L’amore nel 2027', single: 'Se sei single', couple: 'Se sei in coppia', periods: 'I periodi chiave per l’amore', advice: 'Il consiglio d’amore per il 2027' } },
    work: { more: 'Il lavoro nel 2027 per gli altri segni', title: 'Oroscopo 2027 {sign}: lavoro e soldi · Mirastela', h1: '{sign}: lavoro e soldi nel 2027', h: { overview: 'Il lavoro nel 2027', career: 'Carriera e opportunità', money: 'Soldi', periods: 'I periodi chiave per il lavoro', advice: 'Il consiglio per il lavoro nel 2027' } },
    friend: { more: '{sign}: l’amicizia con gli altri segni', title: '{a} e {b}: amicizia · Mirastela', h1: '{a} e {b} come amici', h: { overall: 'Com’è questa amicizia', strengths: 'Cosa li unisce', challenges: 'Dove si scontrano', tips: 'Come mantenere l’amicizia' } },
  },
  es: {
    moonSlug: 'calculadora-signo-lunar',
    moon: {
      nav: 'Signo lunar', title: 'Calculadora del signo lunar: Sol, Luna y Ascendente · Mirastela',
      desc: 'Calcula gratis en qué signo estaba la Luna cuando naciste, junto con tu signo solar y tu Ascendente. Necesitas la fecha, la hora y el lugar de nacimiento.',
      h1: 'Calculadora del signo lunar',
      intro: 'Introduce tu fecha, hora y lugar de nacimiento. Calculamos tu signo lunar y, además, tu signo solar y tu Ascendente, según la posición real de los planetas.',
      aboutTitle: '¿Qué es el signo lunar?',
      about: 'El signo lunar es el signo en el que estaba la Luna en el momento de tu nacimiento. El signo solar describe quién eres; la Luna cuenta cómo sientes, qué necesitas para sentirte a salvo y cómo reaccionas cuando nadie te ve. La Luna cambia de signo cada dos o tres días, por eso la hora de nacimiento ayuda a un cálculo exacto.',
    },
    sub: { love: 'amor', work: 'trabajo', friend: 'amistad' },
    love: { more: 'El amor en 2027 para los demás signos', title: 'Horóscopo 2027 {sign}: amor · Mirastela', h1: '{sign}: el amor en 2027', h: { overview: 'El amor en 2027', single: 'Si no tienes pareja', couple: 'Si tienes pareja', periods: 'Los periodos clave para el amor', advice: 'El consejo de amor para 2027' } },
    work: { more: 'El trabajo en 2027 para los demás signos', title: 'Horóscopo 2027 {sign}: trabajo y dinero · Mirastela', h1: '{sign}: trabajo y dinero en 2027', h: { overview: 'El trabajo en 2027', career: 'Carrera y oportunidades', money: 'Dinero', periods: 'Los periodos clave para el trabajo', advice: 'El consejo de trabajo para 2027' } },
    friend: { more: '{sign}: la amistad con los demás signos', title: '{a} y {b}: amistad · Mirastela', h1: '{a} y {b} como amigos', h: { overall: 'Cómo es esta amistad', strengths: 'Qué los une', challenges: 'Dónde chocan', tips: 'Cómo cuidar esta amistad' } },
  },
  en: {
    moonSlug: 'moon-sign-calculator',
    moon: {
      nav: 'Moon sign', title: 'Moon sign calculator: Sun, Moon and rising sign · Mirastela',
      desc: 'Find out free which sign the Moon was in when you were born, together with your Sun sign and rising sign. You need your birth date, time and place.',
      h1: 'Moon sign calculator',
      intro: 'Enter your birth date, time and place. We calculate your Moon sign, plus your Sun sign and rising sign, from the real positions of the planets.',
      aboutTitle: 'What is a Moon sign?',
      about: 'Your Moon sign is the sign the Moon was in at the moment you were born. Your Sun sign describes who you are; the Moon shows how you feel, what you need to feel safe and how you react when nobody is watching. The Moon changes sign every two to three days, so your birth time helps with an exact result.',
    },
    sub: { love: 'love', work: 'career', friend: 'friendship' },
    love: { more: 'Love in 2027 for the other signs', title: '{sign} 2027 love horoscope · Mirastela', h1: '{sign}: love in 2027', h: { overview: 'Love in 2027', single: 'If you are single', couple: 'If you are in a relationship', periods: 'Key periods for love', advice: 'Love advice for 2027' } },
    work: { more: 'Work in 2027 for the other signs', title: '{sign} 2027 career and money horoscope · Mirastela', h1: '{sign}: career and money in 2027', h: { overview: 'Work in 2027', career: 'Career and opportunities', money: 'Money', periods: 'Key periods for work', advice: 'Career advice for 2027' } },
    friend: { more: '{sign} friendship with the other signs', title: '{a} and {b} friendship compatibility · Mirastela', h1: '{a} and {b} as friends', h: { overall: 'What this friendship is like', strengths: 'What connects them', challenges: 'Where they clash', tips: 'How to keep the friendship strong' } },
  },
};
