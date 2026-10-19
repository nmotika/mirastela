import type { Lang } from '../config';

// Bundle on the offer screen, child natal chart upsell, and report labels for them.
// sl, ro, cs, hu are drafts for native review.
export interface Shop {
  planNatal: string; planBundle: string; bundleWas: string; bundleBadge: string;
  bundleNote: string; later: string;
  kidEyebrow: string; kidTitle: string; kidSub: string; kidBullets: string[]; kidNo: string;
  kidFormTitle: string; kidFormSub: string; kidName: string; kidCta: string;
  tabChild: string; addPartner: string; addPartnerText: string;
  calTitle: string; calDesc: string; calLabels: [string, string, string]; calEx: [string, string, string]; calBullets: string[];
  calAddTitle: string; calAddText: string; calGoogle: string; calApple: string; calCopy: string; calCopied: string;
  waiver: string; waiverTerms: string; waiverErr: string; payPending: string;
  ckText: string; ckAll: string; ckNecessary: string; ckMore: string; ckSettings: string;
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
    calTitle: "Twój osobisty kalendarz astrologiczny", calDesc: "Każdy dzień w kalendarzu w telefonie oznaczony na podstawie Twojego kosmogramu, z krótką wskazówką. Do tego w każdy poniedziałek horoskop tygodniowy e-mailem.", calLabels: ["Super dzień", "Działaj", "Zwolnij"], calEx: ["Rozmowa, która zbliża", "Domknij zaległe sprawy", "Nie podejmuj dziś decyzji o pieniądzach"], calBullets: ["Działa w Kalendarzu Google, na iPhonie i w Outlooku", "Liczony z Twojego kosmogramu, nie ze znaku", "Horoskop tygodniowy w każdy poniedziałek"], calAddTitle: "Dodaj kalendarz do telefonu", calAddText: "Jedno kliknięcie i każdego dnia zobaczysz w kalendarzu, jaki to dzień dla Ciebie.", calGoogle: "Kalendarz Google", calApple: "iPhone / Apple", calCopy: "Kopiuj link (Outlook i inne)", calCopied: "Skopiowano",
    waiver: "Zgadzam się na natychmiastowe dostarczenie treści cyfrowych i przyjmuję do wiadomości, że z chwilą ich dostarczenia tracę prawo odstąpienia od umowy.", waiverTerms: "Regulamin", waiverErr: "Zaznacz zgodę, aby przejść do płatności.", payPending: "Płatność nie została jeszcze potwierdzona. Jeśli środki zostały pobrane, raport przyjdzie e-mailem w ciągu kilku minut. W razie problemu napisz na hello@mirastela.com.",
    ckText: "Używamy plików cookie niezbędnych do działania strony. Za Twoją zgodą także cookies reklamowych (Meta), aby mierzyć skuteczność reklam.", ckAll: "Akceptuję wszystkie", ckNecessary: "Tylko niezbędne", ckMore: "Więcej", ckSettings: "Ustawienia cookies",
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
    calTitle: "Tvoj osobni astrološki kalendar", calDesc: "Svaki dan u kalendaru na mobitelu označen prema tvojoj natalnoj karti, s kratkim savjetom. Uz to svakog ponedjeljka tjedni horoskop mailom.", calLabels: ["Super dan", "Djeluj", "Uspori"], calEx: ["Razgovor koji zbližava", "Završi ono što visi", "Danas ne odlučuj o novcu"], calBullets: ["Radi u Google kalendaru, na iPhoneu i u Outlooku", "Izračunat iz tvoje natalne karte, ne iz znaka", "Tjedni horoskop svakog ponedjeljka"], calAddTitle: "Dodaj kalendar na mobitel", calAddText: "Jedan klik i svaki dan u kalendaru vidiš kakav je dan za tebe.", calGoogle: "Google kalendar", calApple: "iPhone / Apple", calCopy: "Kopiraj poveznicu (Outlook i ostali)", calCopied: "Kopirano",
    waiver: "Pristajem da isporuka digitalnog sadržaja počne odmah i potvrđujem da time gubim pravo na jednostrani raskid ugovora.", waiverTerms: "Uvjeti korištenja", waiverErr: "Potvrdi suglasnost da bi nastavio/la na plaćanje.", payPending: "Plaćanje još nije potvrđeno. Ako je iznos naplaćen, izvještaj stiže e-mailom za nekoliko minuta. Ako ne stigne, javi nam se na hello@mirastela.com.",
    ckText: "Koristimo kolačiće nužne za rad stranice. Uz tvoju privolu i oglasne kolačiće (Meta), da mjerimo uspješnost oglasa.", ckAll: "Prihvaćam sve", ckNecessary: "Samo nužni", ckMore: "Više", ckSettings: "Postavke kolačića",
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
    calTitle: "Tvoj osebni astrološki koledar", calDesc: "Vsak dan v koledarju na telefonu označen po tvoji natalni karti, s kratkim nasvetom. Poleg tega vsak ponedeljek tedenski horoskop po e-pošti.", calLabels: ["Super dan", "Ukrepaj", "Upočasni"], calEx: ["Pogovor, ki zbliža", "Zaključi, kar visi", "Danes ne odločaj o denarju"], calBullets: ["Deluje v Google Koledarju, na iPhonu in v Outlooku", "Izračunan iz tvoje natalne karte, ne iz znamenja", "Tedenski horoskop vsak ponedeljek"], calAddTitle: "Dodaj koledar na telefon", calAddText: "En klik in vsak dan v koledarju vidiš, kakšen dan je zate.", calGoogle: "Google Koledar", calApple: "iPhone / Apple", calCopy: "Kopiraj povezavo (Outlook in drugi)", calCopied: "Kopirano",
    waiver: "Soglašam, da se dobava digitalne vsebine začne takoj, in potrjujem, da s tem izgubim pravico do odstopa od pogodbe.", waiverTerms: "Pogoji uporabe", waiverErr: "Za nadaljevanje na plačilo potrdi soglasje.", payPending: "Plačilo še ni potrjeno. Če je bil znesek bremenjen, poročilo prispe po e-pošti v nekaj minutah. Če ne prispe, nam piši na hello@mirastela.com.",
    ckText: "Uporabljamo piškotke, nujne za delovanje strani. S tvojim soglasjem tudi oglaševalske piškotke (Meta) za merjenje uspešnosti oglasov.", ckAll: "Sprejmem vse", ckNecessary: "Samo nujni", ckMore: "Več", ckSettings: "Nastavitve piškotkov",
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
    calTitle: "Calendarul tău astrologic personal", calDesc: "Fiecare zi din calendarul telefonului marcată după harta ta natală, cu un sfat scurt. În plus, în fiecare luni horoscopul săptămânal pe e-mail.", calLabels: ["Zi super", "Acționează", "Încetinește"], calEx: ["O discuție care apropie", "Termină ce ai amânat", "Azi nu lua decizii despre bani"], calBullets: ["Merge în Google Calendar, pe iPhone și în Outlook", "Calculat după harta ta natală, nu după zodie", "Horoscop săptămânal în fiecare luni"], calAddTitle: "Adaugă calendarul pe telefon", calAddText: "Un clic și vezi zilnic în calendar ce fel de zi este pentru tine.", calGoogle: "Google Calendar", calApple: "iPhone / Apple", calCopy: "Copiază linkul (Outlook și altele)", calCopied: "Copiat",
    waiver: "Sunt de acord ca furnizarea conținutului digital să înceapă imediat și confirm că astfel îmi pierd dreptul de retragere.", waiverTerms: "Termeni și condiții", waiverErr: "Bifează acordul pentru a continua la plată.", payPending: "Plata nu a fost încă confirmată. Dacă suma a fost debitată, raportul vine pe e-mail în câteva minute. Dacă nu ajunge, scrie-ne la hello@mirastela.com.",
    ckText: "Folosim cookie-uri necesare funcționării site-ului. Cu acordul tău, și cookie-uri de publicitate (Meta), pentru a măsura eficiența reclamelor.", ckAll: "Accept toate", ckNecessary: "Doar necesare", ckMore: "Detalii", ckSettings: "Setări cookie",
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
    calTitle: "Tvůj osobní astrologický kalendář", calDesc: "Každý den v kalendáři v telefonu označený podle tvého natálního horoskopu, s krátkou radou. K tomu každé pondělí týdenní horoskop e-mailem.", calLabels: ["Skvělý den", "Jednej", "Zpomal"], calEx: ["Rozhovor, který sblíží", "Dotáhni, co visí", "Dnes nerozhoduj o penězích"], calBullets: ["Funguje v Kalendáři Google, na iPhonu i v Outlooku", "Spočítaný z tvého horoskopu, ne ze znamení", "Týdenní horoskop každé pondělí"], calAddTitle: "Přidej si kalendář do telefonu", calAddText: "Jedno kliknutí a každý den v kalendáři uvidíš, jaký je to pro tebe den.", calGoogle: "Kalendář Google", calApple: "iPhone / Apple", calCopy: "Kopírovat odkaz (Outlook a další)", calCopied: "Zkopírováno",
    waiver: "Souhlasím s okamžitým dodáním digitálního obsahu a beru na vědomí, že tím ztrácím právo odstoupit od smlouvy.", waiverTerms: "Obchodní podmínky", waiverErr: "Pro pokračování k platbě potvrď souhlas.", payPending: "Platba zatím nebyla potvrzena. Pokud byla částka stržena, zpráva přijde e-mailem během několika minut. Pokud nepřijde, napiš nám na hello@mirastela.com.",
    ckText: "Používáme cookies nezbytné pro fungování webu. S tvým souhlasem také reklamní cookies (Meta) pro měření úspěšnosti reklam.", ckAll: "Přijmout vše", ckNecessary: "Jen nezbytné", ckMore: "Více", ckSettings: "Nastavení cookies",
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
    calTitle: "A személyes asztrológiai naptárad", calDesc: "A telefonod naptárában minden nap a születési képleted alapján jelölve, egy rövid tanáccsal. Mellé minden hétfőn heti horoszkóp e-mailben.", calLabels: ["Szuper nap", "Cselekedj", "Lassíts"], calEx: ["Egy közelebb hozó beszélgetés", "Zárd le, ami függőben van", "Ma ne dönts pénzről"], calBullets: ["Működik a Google Naptárban, iPhone-on és Outlookban", "A születési képletedből számolva, nem a jegyedből", "Heti horoszkóp minden hétfőn"], calAddTitle: "Add hozzá a naptárt a telefonodhoz", calAddText: "Egy kattintás, és minden nap látod a naptárban, milyen napod lesz.", calGoogle: "Google Naptár", calApple: "iPhone / Apple", calCopy: "Link másolása (Outlook és mások)", calCopied: "Másolva",
    waiver: "Hozzájárulok, hogy a digitális tartalom szolgáltatása azonnal megkezdődjön, és tudomásul veszem, hogy ezzel elveszítem az elállási jogomat.", waiverTerms: "ÁSZF", waiverErr: "A fizetéshez jelöld be a hozzájárulást.", payPending: "A fizetés még nincs megerősítve. Ha az összeget levonták, a jelentés néhány percen belül megérkezik e-mailben. Ha nem jön, írj nekünk: hello@mirastela.com.",
    ckText: "A weboldal működéséhez szükséges sütiket használunk. Hozzájárulásoddal hirdetési sütiket is (Meta), a hirdetések eredményességének méréséhez.", ckAll: "Mindet elfogadom", ckNecessary: "Csak a szükségesek", ckMore: "Részletek", ckSettings: "Süti beállítások",
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
    calTitle: "Your personal astrological calendar", calDesc: "Every day in your phone calendar marked from your natal chart, with a short tip. Plus a weekly horoscope by email every Monday.", calLabels: ["Great day", "Act", "Slow down"], calEx: ["A conversation that brings you closer", "Finish what is pending", "No money decisions today"], calBullets: ["Works in Google Calendar, on iPhone and in Outlook", "Calculated from your natal chart, not your sign", "Weekly horoscope every Monday"], calAddTitle: "Add the calendar to your phone", calAddText: "One click and every day your calendar shows what kind of day it is for you.", calGoogle: "Google Calendar", calApple: "iPhone / Apple", calCopy: "Copy link (Outlook and others)", calCopied: "Copied",
    waiver: "I agree that the digital content is supplied immediately and I acknowledge that I thereby lose my right of withdrawal.", waiverTerms: "Terms", waiverErr: "Please tick the box to continue to payment.", payPending: "Your payment is not confirmed yet. If you were charged, the report will arrive by email within a few minutes. If it does not, write to hello@mirastela.com.",
    ckText: "We use cookies that the site needs to work. With your consent, also advertising cookies (Meta) to measure how our ads perform.", ckAll: "Accept all", ckNecessary: "Necessary only", ckMore: "More", ckSettings: "Cookie settings",
  },
};
