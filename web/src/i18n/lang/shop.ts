import type { Lang } from '../config';

// Bundle on the offer screen, child natal chart upsell, and report labels for them.
// sl, ro, cs, hu are drafts for native review.
export interface Shop {
  planNatal: string; planBundle: string; bundleWas: string; bundleBadge: string;
  bundleNote: string; later: string;
  kidEyebrow: string; kidTitle: string; kidSub: string; kidBullets: string[]; kidNo: string;
  kidFormTitle: string; kidFormSub: string; kidName: string; kidCta: string;
  tabChild: string; addPartner: string; addPartnerText: string;
}

export const SHOP: Record<Lang, Shop> = {
  pl: {
    planNatal: 'Kosmogram', planBundle: 'Pakiet: kosmogram, dopasowanie i prognoza {year}', bundleWas: 'osobno {price}', bundleBadge: 'Najlepsza wartość',
    bundleNote: 'W pakiecie jest też dopasowanie z partnerem. Podaj dane partnera teraz albo później z poziomu raportu.', later: 'Dodam później',
    kidEyebrow: 'Dla rodziców', kidTitle: 'Kosmogram Twojego dziecka',
    kidSub: 'Jak Twoje dziecko czuje, uczy się i nawiązuje relacje. Napisany dla rodzica, z praktycznymi wskazówkami.',
    kidBullets: ['Temperament i potrzeby emocjonalne', 'Jak się uczy i co je motywuje', 'Jak wspierać jego mocne strony'], kidNo: 'Nie, dziękuję',
    kidFormTitle: 'Dane dziecka', kidFormSub: 'Data, godzina i miejsce urodzenia. Jeśli nie znasz godziny, też przygotujemy kosmogram.',
    kidName: 'Imię dziecka', kidCta: 'Przygotuj kosmogram dziecka',
    tabChild: 'Dziecko', addPartner: 'Dodaj dane partnera', addPartnerText: 'Dopasowanie z partnerem jest w Twoim pakiecie. Podaj dane partnera, a przygotujemy raport.',
  },
  hr: {
    planNatal: 'Natalna karta', planBundle: 'Paket: natalna karta, slaganje i prognoza {year}', bundleWas: 'zasebno {price}', bundleBadge: 'Najbolja vrijednost',
    bundleNote: 'U paketu je i slaganje s partnerom. Upiši podatke partnera sada ili kasnije iz izvještaja.', later: 'Dodat ću kasnije',
    kidEyebrow: 'Za roditelje', kidTitle: 'Natalna karta tvog djeteta',
    kidSub: 'Kako tvoje dijete osjeća, uči i povezuje se s drugima. Napisano za roditelja, s praktičnim savjetima.',
    kidBullets: ['Temperament i emocionalne potrebe', 'Kako uči i što ga motivira', 'Kako podržati njegove jake strane'], kidNo: 'Ne, hvala',
    kidFormTitle: 'Podaci o djetetu', kidFormSub: 'Datum, vrijeme i mjesto rođenja. Ako ne znaš vrijeme, kartu ćemo svejedno izraditi.',
    kidName: 'Ime djeteta', kidCta: 'Izradi kartu djeteta',
    tabChild: 'Dijete', addPartner: 'Dodaj podatke partnera', addPartnerText: 'Slaganje s partnerom je u tvom paketu. Upiši podatke partnera i izradit ćemo izvještaj.',
  },
  sl: {
    planNatal: 'Natalna karta', planBundle: 'Paket: natalna karta, ujemanje in napoved {year}', bundleWas: 'posamično {price}', bundleBadge: 'Najboljša vrednost',
    bundleNote: 'Paket vključuje tudi ujemanje s partnerjem. Vpiši partnerjeve podatke zdaj ali pozneje iz poročila.', later: 'Dodam pozneje',
    kidEyebrow: 'Za starše', kidTitle: 'Natalna karta tvojega otroka',
    kidSub: 'Kako tvoj otrok čuti, se uči in povezuje z drugimi. Napisano za starša, s praktičnimi nasveti.',
    kidBullets: ['Temperament in čustvene potrebe', 'Kako se uči in kaj ga motivira', 'Kako podpreti njegove močne strani'], kidNo: 'Ne, hvala',
    kidFormTitle: 'Podatki o otroku', kidFormSub: 'Datum, ura in kraj rojstva. Če ure ne poznaš, karto vseeno pripravimo.',
    kidName: 'Ime otroka', kidCta: 'Pripravi karto otroka',
    tabChild: 'Otrok', addPartner: 'Dodaj partnerjeve podatke', addPartnerText: 'Ujemanje s partnerjem je v tvojem paketu. Vpiši partnerjeve podatke in pripravili bomo poročilo.',
  },
  ro: {
    planNatal: 'Harta natală', planBundle: 'Pachet: harta natală, compatibilitate și prognoza {year}', bundleWas: 'separat {price}', bundleBadge: 'Cea mai bună valoare',
    bundleNote: 'Pachetul include și compatibilitatea cu partenerul. Introdu datele partenerului acum sau mai târziu, din raport.', later: 'Adaug mai târziu',
    kidEyebrow: 'Pentru părinți', kidTitle: 'Harta natală a copilului tău',
    kidSub: 'Cum simte, cum învață și cum se leagă copilul tău de ceilalți. Scrisă pentru părinte, cu sfaturi practice.',
    kidBullets: ['Temperament și nevoi emoționale', 'Cum învață și ce îl motivează', 'Cum îi susții punctele forte'], kidNo: 'Nu, mulțumesc',
    kidFormTitle: 'Datele copilului', kidFormSub: 'Data, ora și locul nașterii. Dacă nu știi ora, pregătim harta oricum.',
    kidName: 'Numele copilului', kidCta: 'Pregătește harta copilului',
    tabChild: 'Copilul', addPartner: 'Adaugă datele partenerului', addPartnerText: 'Compatibilitatea cu partenerul este în pachetul tău. Introdu datele partenerului și pregătim raportul.',
  },
  cs: {
    planNatal: 'Natální horoskop', planBundle: 'Balíček: natální horoskop, partnerský soulad a předpověď {year}', bundleWas: 'samostatně {price}', bundleBadge: 'Nejlepší hodnota',
    bundleNote: 'Balíček obsahuje i partnerský soulad. Zadej údaje partnera teď, nebo později ze zprávy.', later: 'Doplním později',
    kidEyebrow: 'Pro rodiče', kidTitle: 'Natální horoskop tvého dítěte',
    kidSub: 'Jak tvé dítě cítí, učí se a navazuje vztahy. Psáno pro rodiče, s praktickými radami.',
    kidBullets: ['Temperament a citové potřeby', 'Jak se učí a co ho motivuje', 'Jak podpořit jeho silné stránky'], kidNo: 'Ne, děkuji',
    kidFormTitle: 'Údaje o dítěti', kidFormSub: 'Datum, čas a místo narození. Pokud čas neznáš, horoskop připravíme i tak.',
    kidName: 'Jméno dítěte', kidCta: 'Připravit horoskop dítěte',
    tabChild: 'Dítě', addPartner: 'Doplnit údaje partnera', addPartnerText: 'Partnerský soulad je ve tvém balíčku. Doplň údaje partnera a připravíme zprávu.',
  },
  hu: {
    planNatal: 'Születési horoszkóp', planBundle: 'Csomag: születési horoszkóp, párkapcsolati összhang és {year}. évi előrejelzés', bundleWas: 'külön {price}', bundleBadge: 'Legjobb ár-érték',
    bundleNote: 'A csomagban a párkapcsolati összhang is benne van. Add meg a partner adatait most vagy később a riportból.', later: 'Később adom meg',
    kidEyebrow: 'Szülőknek', kidTitle: 'Gyermeked születési horoszkópja',
    kidSub: 'Hogyan érez, tanul és kapcsolódik másokhoz a gyermeked. Szülőknek írva, gyakorlati tanácsokkal.',
    kidBullets: ['Temperamentum és érzelmi igények', 'Hogyan tanul, és mi motiválja', 'Hogyan támogathatod az erősségeit'], kidNo: 'Nem, köszönöm',
    kidFormTitle: 'A gyermek adatai', kidFormSub: 'Születési dátum, idő és hely. Ha nem tudod az időt, a horoszkópot akkor is elkészítjük.',
    kidName: 'A gyermek neve', kidCta: 'Gyermek horoszkópjának elkészítése',
    tabChild: 'Gyermek', addPartner: 'Partner adatainak megadása', addPartnerText: 'A párkapcsolati összhang benne van a csomagodban. Add meg a partner adatait, és elkészítjük a riportot.',
  },
  en: {
    planNatal: 'Natal chart', planBundle: 'Bundle: natal chart, compatibility and {year} forecast', bundleWas: 'separately {price}', bundleBadge: 'Best value',
    bundleNote: "The bundle includes partner compatibility. Enter your partner's details now or later from your report.", later: "I'll add it later",
    kidEyebrow: 'For parents', kidTitle: "Your child's natal chart",
    kidSub: 'How your child feels, learns and connects with others. Written for the parent, with practical tips.',
    kidBullets: ['Temperament and emotional needs', 'How they learn and what motivates them', 'How to support their strengths'], kidNo: 'No, thanks',
    kidFormTitle: "Your child's details", kidFormSub: "Date, time and place of birth. If you don't know the time, we'll still prepare the chart.",
    kidName: "Child's name", kidCta: "Prepare my child's chart",
    tabChild: 'Child', addPartner: "Add your partner's details", addPartnerText: "Partner compatibility is in your bundle. Add your partner's details and we'll prepare the report.",
  },
};
