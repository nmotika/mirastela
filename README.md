# Mirastela

Funnel za natalnu kartu: Astro (statični web, 7 jezika) + FastAPI (izračun karte).

## Struktura
- `web/` Astro 5. Stranice: `/{jezik}/` landing, `/{jezik}/start/` kviz → izračun → e-mail → ponuda.
  Jezici: pl (prvo tržište), hr, sl, ro, cs, hu, en. Tekstovi u `web/src/i18n/lang/*.ts`.
  sl, cs, ro i hu su nacrti: prije lansiranja ih treba pregledati izvorni govornik.
- `api/` FastAPI: `/api/cities` (offline GeoNames, s vremenskim zonama), `/api/sun`, `/api/chart`, `/api/lead` (SQLite).

## Pokretanje lokalno
```
cd api
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt      (Windows; na Linuxu .venv/bin/pip)
.venv\Scripts\uvicorn app:app --port 8000

cd web
npm install
npm run dev        → http://localhost:4321/pl/   (/api ide na port 8000)
```

## Kupon i izvještaji (testna faza)
- Kupon preskače naplatu: na ponudi "Masz kod?", zadani kod `MIRATEST`.
  Kodovi se zadaju varijablom `MIRASTELA_COUPONS` (npr. `MIRATEST,ANNA2026`). Bez valjanog koda narudžba vraća 402.
- Proizvodi: natalni izvještaj, partnerski (sinastrija, kod statusa "u vezi" ili "komplicirano") i godišnja prognoza
  (kod statusa "sam/a"). Godina prognoze: sljedeća ako je listopad ili kasnije, inače tekuća.
- Izvještaj piše Claude: postavi `ANTHROPIC_API_KEY` (model: `MIRASTELA_MODEL`, zadano `claude-sonnet-5-5`).
  Bez ključa izvještaj je "TEST MODE" i prikazuje točno one podatke koje bi model dobio, za provjeru točnosti.
- Stranica izvještaja: `/{jezik}/report/?o=TOKEN`, s karticama, tablicom pozicija, aspektima ili tranzitima,
  i gumbom "Preuzmi PDF" (ispis preglednika u PDF, s posebnim stilom za ispis).
- Promptovi su u `api/report.py`: pravila stila, redoslijed poglavlja i činjenice iz karte.

## Izračun
Swiss Ephemeris (pyswisseph), ugrađena Moshierova efemerida (bez datoteka podataka),
kuće Placidus (iznad polarnog kruga Whole Sign). Provjereno na J2000.0: Sunce 280,369°, Mjesec 223,32°.
Bez vremena rođenja: računa se za podne, bez podznaka, kuća i aspekata Mjeseca.

## Licenca: važno
Swiss Ephemeris se ovdje koristi pod GNU AGPL. Dok se ne kupi Professional licenca (CHF 700),
javni servis mora korisnicima ponuditi cijeli izvorni kod (npr. javni GitHub repozitorij,
link u podnožju; postavi `MIRASTELA_SOURCE_URL`). Kad se kupi licenca, ta obveza otpada.

## Sljedeće
1. Stripe Checkout (BLIK za PL, kartice, Apple/Google Pay) i stranica za pretplatu.
2. E-mail s linkom na izvještaj nakon narudžbe.
3. E-mail sažetak nakon prijave, pravni tekstovi, deploy (statični web + API).
