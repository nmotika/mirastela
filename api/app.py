"""Mirastela API: city search, natal chart, leads, orders, reports, emails, subscriptions, daily horoscopes."""
from __future__ import annotations

import os
import json
import re
import secrets
import sqlite3
from datetime import date, datetime, time, timedelta, timezone

from fastapi import BackgroundTasks, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

def _load_env():
    path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(path):
        for line in open(path, encoding="utf-8"):
            if "=" in line and not line.lstrip().startswith("#"):
                k, v = line.strip().split("=", 1)
                if v:
                    os.environ.setdefault(k, v)


_load_env()

import cal
import capi
import chart
import pay
import cities
import emails
import gifts
import affiliates
import guard
import mailer
import report
import sky

DB_PATH = os.environ.get("MIRASTELA_DB", os.path.join(os.path.dirname(__file__), "mirastela.db"))
SOURCE_URL = os.environ.get("MIRASTELA_SOURCE_URL", "")  # AGPL: link to this source code

app = FastAPI(title="Mirastela API")
PROXY_SECRET = os.environ.get("MIRASTELA_PROXY_SECRET", "")


@app.middleware("http")
async def require_proxy_secret(request: Request, call_next):
    """In production only the Cloudflare Pages proxy may call the API."""
    if PROXY_SECRET and request.url.path != "/api/health" \
            and request.headers.get("x-proxy-secret") != PROXY_SECRET:
        return JSONResponse({"detail": "forbidden"}, status_code=403)
    return await call_next(request)


app.add_middleware(CORSMiddleware, allow_origins=os.environ.get("CORS_ORIGINS", "*").split(","),
                   allow_methods=["GET", "POST"], allow_headers=["*"])


def db():
    con = sqlite3.connect(DB_PATH)
    con.execute("""create table if not exists leads(
        id integer primary key, created text, email text, lang text, name text,
        birth_date text, birth_time text, city_id integer, focus text, status text,
        marketing_consent integer)""")
    con.execute("""create table if not exists orders(
        token text primary key, created text, lang text, email text, name text,
        input text, chart text, coupon text)""")
    con.execute("""create table if not exists items(
        id integer primary key, token text, product text, input text, data text,
        status text, markdown text, model text, created text, unique(token, product))""")
    con.execute("""create table if not exists subs(
        token text primary key, created text, email text, lang text, name text, chart text,
        freq text, status text, order_token text, coupon text, last_sent text)""")
    con.execute("""create table if not exists feedback(
        id integer primary key, created text, email text, answers text, ua text)""")
    con.execute("""create table if not exists daily(
        lang text, day text, data text, model text, created text, primary key(lang, day))""")
    con.execute("""create table if not exists caldays(
        sub text, day text, label text, title text, text text, model text, created text, primary key(sub, day))""")
    cols = {r[1] for r in con.execute("pragma table_info(leads)")}
    if "token" not in cols:
        con.execute("alter table leads add column token text")
    if "src" not in cols:
        con.execute("alter table leads add column src text")
    for col in ("summary", "consent_v", "reminded"):
        if col not in cols:
            con.execute(f"alter table leads add column {col} text")
            if col == "consent_v":  # every consent so far was given with the first wording of the checkbox
                con.execute("update leads set consent_v='v1' where marketing_consent=1")
    con.execute("create table if not exists optout(email text primary key, created text, via text)")
    sub_cols = {r[1] for r in con.execute("pragma table_info(subs)")}
    for col in ("cal", "stripe_customer", "stripe_sub"):
        if col not in sub_cols:
            con.execute(f"alter table subs add column {col} text")
    if "paid" not in {r[1] for r in con.execute("pragma table_info(orders)")}:
        con.execute("alter table orders add column paid integer default 1")  # rows before payments existed were coupon orders
    gifts.schema(con)
    affiliates.schema(con)
    con.execute("create table if not exists daily_parts(lang text, day text, first integer, data text, model text, primary key(lang, day, first))")
    con.execute("create table if not exists daily_batches(id text primary key, created text, status text, items text)")
    con.execute("""create table if not exists payments(
        session text primary key, token text, kind text, product text, status text, created text, done text, consent text)""")
    pay_cols = {r[1] for r in con.execute("pragma table_info(payments)")}
    for col in ("consent", "track", "price_key"):
        if col not in pay_cols:
            con.execute(f"alter table payments add column {col} text")
    return con


def _parse_coupons(raw: str) -> dict[str, int]:
    """MIRASTELA_COUPONS=FREECODE,MIRA50:50,ANA15:15 -> {code: percent off}. No percent means free (100)."""
    out = {}
    for part in raw.split(","):
        code, _, pct = part.strip().partition(":")
        pct = pct.strip()
        if not code.strip() or (pct and not pct.isdigit()):
            continue  # a typo in the percent must never turn a code into a free one
        out[code.strip().upper()] = max(1, min(100, int(pct))) if pct else 100
    return out


COUPONS = _parse_coupons(os.environ.get("MIRASTELA_COUPONS", "MIRATEST"))
COUPONS.update({c: p for c, p in affiliates.AFFILIATES.items() if p > 0})  # a partner code is also its discount code
PRODUCTS = ("natal", "partner", "forecast")


def forecast_year() -> int:
    today = datetime.now(timezone.utc).date()
    return today.year + 1 if today.month >= 10 else today.year


def birth_chart(d: str, t: str | None, city_id: int) -> dict:
    city = cities.get(city_id)
    if not city:
        raise HTTPException(404, "city not found")
    clock = time.fromisoformat(t) if t else None
    res = chart.calculate(chart.BirthData(date.fromisoformat(d), clock, city["lat"], city["lon"], city["tz"]))
    res["city"] = {k: city[k] for k in ("id", "name", "country", "tz")}
    return res


@app.get("/api/health")
def health():
    return {"ok": True, "source": SOURCE_URL}


@app.get("/api/cities")
def city_search(q: str, lang: str = "en"):
    return cities.search(q, lang)


@app.get("/api/sun")
def sun_sign(d: date):
    """Sun sign for a date at 12:00 UTC (quick reward in the quiz; the full chart is exact)."""
    res = chart.calculate(chart.BirthData(d, time(12, 0), 0.0, 0.0, "UTC"))
    sun = res["planets"][0]
    return {"sign": sun["sign"], "signIndex": sun["signIndex"]}


class ChartIn(BaseModel):
    date: date
    time: str | None = Field(None, pattern=r"^\d{2}:\d{2}$")
    cityId: int


@app.post("/api/chart")
def make_chart(body: ChartIn, request: Request):
    guard.per_ip(DB_PATH, request, "chart", 60, 600)
    city = cities.get(body.cityId)
    if not city:
        raise HTTPException(404, "city not found")
    if not (date(1900, 1, 1) <= body.date <= datetime.now(timezone.utc).date()):
        raise HTTPException(422, "date out of range")
    clock = time.fromisoformat(body.time) if body.time else None
    res = chart.calculate(chart.BirthData(body.date, clock, city["lat"], city["lon"], city["tz"]))
    res["city"] = {k: city[k] for k in ("id", "name", "country", "tz")}
    return res


class TrackIn(BaseModel):
    """Browser identifiers for the Meta pixel, sent only after the visitor accepted marketing cookies."""
    consent: bool = False
    fbp: str = Field("", max_length=200)
    fbc: str = Field("", max_length=300)


def _track(t: "TrackIn | None", request: Request) -> dict:
    if not t or not t.consent:
        return {}
    return {"consent": True, "fbp": t.fbp, "fbc": t.fbc, "ip": guard.client_ip(request), "ua": request.headers.get("user-agent", "")[:400]}


class LeadIn(BaseModel):
    email: str
    lang: str = "pl"
    name: str = ""
    date: str = ""
    time: str | None = None
    cityId: int | None = None
    focus: list[str] = []
    status: str = ""
    marketingConsent: bool = False
    track: TrackIn | None = None
    src: dict[str, str] | None = None  # visit source: referring host, utm tags, landing page
    captcha: str | None = Field(None, max_length=4000)


def _src_json(src: dict[str, str] | None) -> str | None:
    keep = ("landing", "ref", "source", "medium", "campaign", "content", "term", "click", "aff")
    clean = {k: str(src[k])[:120] for k in keep if src and src.get(k)}
    return json.dumps(clean, ensure_ascii=False) if clean else None


@app.post("/api/lead")
def lead(body: LeadIn, bg: BackgroundTasks, request: Request):
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", body.email):
        raise HTTPException(422, "invalid email")
    guard.per_ip(DB_PATH, request, "lead", 6, 600)
    guard.limit(DB_PATH, f"lead-mail:{body.email.lower()}", 4, 3600)
    guard.turnstile(body.captcha, request)
    token = secrets.token_urlsafe(12)
    with db() as con:
        con.execute("insert into leads(created,email,lang,name,birth_date,birth_time,city_id,focus,status,marketing_consent,token,src,consent_v)"
                    " values(?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (datetime.now(timezone.utc).isoformat(), body.email.lower(), body.lang, body.name[:80],
                     body.date, body.time, body.cityId, ",".join(body.focus), body.status,
                     int(body.marketingConsent), token, _src_json(body.src), CONSENT_V if body.marketingConsent else None))
        affiliates.attribute(con, body.email, (body.src or {}).get("aff"), "lead")
    if body.date and body.cityId:
        bg.add_task(_send_summary, token)
    bg.add_task(capi.send, "Lead", f"lead_{token}", f"{emails.SITE}/{_lang(body.lang)}/start/", body.email,
                _track(body.track, request), name=body.name, lang=_lang(body.lang))
    return {"ok": True, "token": token}


def _lang(x: str) -> str:
    return x if x in report.LANG_NAME else "en"


CONSENT_V = "v1"  # wording of the marketing checkbox (quiz.emailConsent); bump when the text changes


def _lead_offer(lang: str, src: str | None) -> tuple[str, str]:
    """Natal price as the lead will see it (partner discount included) and the partner code for the link."""
    aff = affiliates.valid((json.loads(src) if src else {}).get("aff"))
    cur, minor = pay.price(lang, "natal", affiliates.AFFILIATES.get(aff, 0))
    return emails.money(lang, cur, minor), aff


def _resume_url(lang: str, token: str, aff: str, campaign: str) -> str:
    return (f"{emails.SITE}/{lang}/start/?r={token}" + (f"&p={aff}" if aff else "")
            + f"&utm_source=email&utm_medium={campaign}&utm_campaign=lead")


def _send_summary(token: str):
    """Free summary of the chart, written by the fast model: who they are, one tension, and questions the
    full report answers (kept for the reminder), with a button that shows the price."""
    with db() as con:
        email, lang, name, d, t, city_id, focus, status, src = con.execute(
            "select email, lang, name, birth_date, birth_time, city_id, focus, status, src from leads where token=?", (token,)).fetchone()
    lang = _lang(lang)
    natal = birth_chart(d, t, city_id)
    focus_l = [f for f in (focus or "").split(",") if f]
    sun, moon = natal["planets"][0], natal["planets"][1]
    fallback = {"paragraphs": [f"TEST MODE: sun {sun['sign']} {sun['deg']}°, moon {moon['sign']} {moon['deg']}°."], "questions": []}
    paras, qs = [], []
    for attempt in range(2):
        try:
            out, _ = report.generate_json(report.prompt_summary(lang, name, natal, focus_l, status or ""), report.SUMMARY_SCHEMA,
                                          max_tokens=8000, fallback=fallback)
            out = out or {}
            raw_p, raw_q = out.get("paragraphs"), out.get("questions")
            paras = [p.strip() for p in ([raw_p] if isinstance(raw_p, str) else raw_p or []) if isinstance(p, str) and p.strip()]
            qs = [q.strip() for q in ([raw_q] if isinstance(raw_q, str) else raw_q or []) if isinstance(q, str) and q.strip()][:3]
            if paras:
                break
            print("summary", token[:6], "empty", attempt, str(out)[:300], flush=True)
        except Exception as e:
            print("summary", token[:6], "error", attempt, repr(e)[:300], flush=True)
    with db() as con:
        con.execute("update leads set summary=? where token=?", (json.dumps({"paragraphs": paras, "questions": qs}, ensure_ascii=False), token))
    price, aff = _lead_offer(lang, src)
    subject, html = emails.summary2(lang, name, natal, paras, qs, price, _resume_url(lang, token, aff, "summary"))
    mailer.send(DB_PATH, email, "summary", subject, html)


def send_reminders(now: datetime | None = None) -> int:
    """One reminder, 24 to 48 hours after the summary, to leads who opted in to marketing e-mails, have not
    bought and have not opted out. Uses one of the open questions from their summary. Runs every hour."""
    now = now or datetime.now(timezone.utc)
    lo, hi = (now - timedelta(hours=48)).isoformat(), (now - timedelta(hours=24)).isoformat()
    sent = 0
    with db() as con:
        rows = con.execute(
            """select l.token, lower(l.email), l.lang, l.name, l.summary, l.src from leads l
               where l.marketing_consent=1 and l.reminded is null and l.summary is not null
                 and l.created between ? and ?
                 and lower(l.email) not in (select email from optout)
                 and lower(l.email) not in (select lower(email) from orders where paid=1)
                 and lower(l.email) not in (select lower(email) from leads where reminded is not null)
               order by l.created desc""", (lo, hi)).fetchall()
    done: set[str] = set()
    for token, email, lang, name, summ, src in rows:
        if email in done:
            continue  # the latest lead of each address only
        done.add(email)
        qs = (json.loads(summ) or {}).get("questions") or []
        with db() as con:  # mark first: a crash must never send twice
            con.execute("update leads set reminded=? where lower(email)=?", (now.isoformat(), email))
        if not qs:
            continue
        lang = _lang(lang)
        price, aff = _lead_offer(lang, src)
        subject, html = emails.reminder(lang, name, qs[0], price, _resume_url(lang, token, aff, "reminder"),
                                        f"{emails.SITE}/api/unsub/{token}")
        mailer.send(DB_PATH, email, "reminder", subject, html, unsubscribe_url=f"{emails.SITE}/api/unsub/{token}")
        sent += 1
    return sent


@app.get("/api/lead/{token}")
def get_lead(token: str):
    """Restores the funnel from the link in the summary email."""
    with db() as con:
        row = con.execute("select email, lang, name, birth_date, birth_time, city_id, focus, status from leads where token=?",
                          (token,)).fetchone()
    if not row:
        raise HTTPException(404, "not found")
    email, lang, name, d, t, city_id, focus, status = row
    city = cities.get(city_id) if city_id else None
    return {"email": email, "lang": lang, "name": name, "date": d, "time": t, "status": status,
            "focus": [f for f in (focus or "").split(",") if f],
            "city": {k: city[k] for k in ("id", "name", "country", "countryName", "tz")} if city else None}


# ---------------------------------------------------------------- orders
class PartnerIn(BaseModel):
    name: str = Field("", max_length=40)
    date: date
    time: str | None = Field(None, pattern=r"^\d{2}:\d{2}$")
    cityId: int


class OrderIn(BaseModel):
    lang: str = "pl"
    email: str
    name: str = Field("", max_length=40)
    date: date
    time: str | None = Field(None, pattern=r"^\d{2}:\d{2}$")
    cityId: int
    focus: list[str] = []
    status: str = ""
    coupon: str = ""
    aff: str = Field("", max_length=40)  # partner code from the partner link
    bundle: bool = False
    consent: bool = False  # withdrawal waiver ticked on the offer screen
    track: TrackIn | None = None


class AddIn(BaseModel):
    product: str
    partner: PartnerIn | None = None
    consent: bool = False
    track: TrackIn | None = None


def _coupon_pct(code: str) -> int:
    """Percent off for a code: 0 unknown, 100 free, else a discount on one-time purchases."""
    return COUPONS.get((code or "").strip().upper(), 0)


def _coupon_ok(code: str) -> bool:
    """A free-access code (100 %): everything for that order, including the subscription, is free."""
    return _coupon_pct(code) == 100


def _build(token: str, product: str):
    """Compute the product's data and write the report (runs in the background)."""
    with db() as con:
        lang, name, inp, natal = con.execute(
            "select lang, name, input, chart from orders where token=?", (token,)).fetchone()
        item_input = con.execute("select input from items where token=? and product=?", (token, product)).fetchone()[0]
    natal, inp = json.loads(natal), json.loads(inp)
    age = report.age_from(inp.get("date", ""))
    try:
        if product == "natal":
            bal = chart.balance(natal)
            data = {"balance": bal}
            prompt = report.prompt_natal(lang, name, natal, inp.get("focus", []), bal, age)
        elif product == "child":
            p = json.loads(item_input)
            cc = birth_chart(p["date"], p.get("time"), p["cityId"])
            bal = chart.balance(cc)
            data = {"child": p, "childChart": cc, "balance": bal}
            prompt = report.prompt_child(lang, name, p.get("name", ""), cc, bal, report.age_from(p["date"]))
        elif product == "partner":
            p = json.loads(item_input)
            pc = birth_chart(p["date"], p.get("time"), p["cityId"])
            syn = chart.synastry(natal, pc)
            data = {"partner": p, "partnerChart": pc, "synastry": syn}
            prompt = report.prompt_partner(lang, name, p.get("name", ""), natal, pc, syn, age)
        else:
            tr = chart.transits(natal, forecast_year())
            data = {"transits": tr}
            prompt = report.prompt_forecast(lang, name, natal, tr, inp.get("focus", []), age)
        md, model = report.generate(prompt)
        data["v"] = 2  # layered format: summary first, '> ' astrology lines, glossary last
        status = "ready"
    except Exception as exc:  # keep the error visible for debugging
        data, md, model, status = {"error": str(exc)}, "", "", "error"
    with db() as con:
        con.execute("update items set data=?, markdown=?, model=?, status=? where token=? and product=?",
                    (json.dumps(data), md, model, status, token, product))
        email = con.execute("select email from orders where token=?", (token,)).fetchone()[0]
    if status == "ready":
        lang = _lang(lang)
        with db() as con:
            coupon = (con.execute("select coupon from orders where token=?", (token,)).fetchone() or [""])[0]
        subject, html = emails.report_ready(lang, name, product, forecast_year(),
                                            f"{emails.SITE}/{lang}/report/?o={token}&t={product}", paid=not (_coupon_ok(coupon or "") or (coupon or "").startswith("GIFT:")))
        mailer.send(DB_PATH, email, f"report-{product}", subject, html)


def _add_item(token: str, product: str, item_input: dict | None, bg: BackgroundTasks):
    with db() as con:
        con.execute("insert or ignore into items(token, product, input, status, created) values(?,?,?,?,?)",
                    (token, product, json.dumps(item_input or {}), "pending", datetime.now(timezone.utc).isoformat()))
    bg.add_task(_build, token, product)


@app.post("/api/order")
def create_order(body: OrderIn, bg: BackgroundTasks, request: Request):
    guard.per_ip(DB_PATH, request, "order", 10, 600)
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", body.email):
        raise HTTPException(422, "invalid email")
    with db() as con:
        gift = gifts.active(con, body.coupon)
    if gift:  # the gifted product only; later add-ons are paid as usual
        body.bundle = gift["product"] == "bundle"
    pct = 100 if gift else _coupon_pct(body.coupon)
    free = pct == 100
    if not free and not pay.enabled():
        raise HTTPException(402, "payment required")
    if not free and not body.consent:
        raise HTTPException(422, "consent required")
    natal = birth_chart(body.date.isoformat(), body.time, body.cityId)
    token = secrets.token_urlsafe(16)
    with db() as con:
        if gift and not gifts.redeem(con, gift["code"], token):
            raise HTTPException(409, "gift code already used")
        con.execute("insert into orders(token, created, lang, email, name, input, chart, coupon, paid) values(?,?,?,?,?,?,?,?,?)",
                    (token, datetime.now(timezone.utc).isoformat(), body.lang, body.email.lower(), body.name,
                     body.model_dump_json(exclude={"coupon"}), json.dumps(natal),
                     f"GIFT:{gift['code']}" if gift else (body.coupon.strip().upper() if pct else ""), 1 if free else 0))
        affiliates.attribute(con, body.email, body.aff or body.coupon, "order")
    if not free:
        key = "bundle" if body.bundle else "natal"
        return {"token": token, "checkout": _checkout(token, _lang(body.lang), body.email, key, "order", key, "offer",
                                                      _track(body.track, request), pct)}
    _fulfil_order(token, bg)
    return {"token": token}


def _fulfil_order(token: str, bg: BackgroundTasks):
    with db() as con:
        inp = json.loads(con.execute("select input from orders where token=?", (token,)).fetchone()[0])
    _add_item(token, "natal", None, bg)
    if inp.get("bundle"):  # natal + yearly forecast now; the partner report once their details are given
        _add_item(token, "forecast", None, bg)


def _checkout(token: str, lang: str, email: str, key: str, kind: str, product: str, cancel_step: str,
              track: dict | None = None, pct: int = 0, success_url: str | None = None, cancel_url: str | None = None) -> str:
    """Stripe Checkout for one purchase. The caller has checked that the withdrawal waiver was ticked;
    its time and wording version are kept with the payment as the record of consent."""
    s = pay.create_session(lang, email, key, forecast_year(), {"token": token, "kind": kind, "product": product}, cancel_step, pct,
                           success_url, cancel_url)
    now = datetime.now(timezone.utc).isoformat()
    with db() as con:
        con.execute("insert into payments(session, token, kind, product, status, created, consent, track, price_key)"
                    " values(?,?,?,?,?,?,?,?,?)",
                    (s["id"], token, kind, product, "open", now, f"waiver-v1 {lang} {now}", json.dumps(track or {}), key))
    return s["url"]


@app.post("/api/coupon")
def check_coupon(body: dict, request: Request):
    guard.per_ip(DB_PATH, request, "coupon", 10, 600)
    code = str(body.get("code", ""))
    with db() as con:
        g = gifts.active(con, code)
    if g:  # a gift code: the gifted product, free
        return {"valid": True, "percent": 100, "gift": g["product"]}
    pct = _coupon_pct(code)
    return {"valid": pct > 0, "percent": pct}


@app.post("/api/order/{token}/add")
def add_product(token: str, body: AddIn, bg: BackgroundTasks, request: Request):
    guard.per_ip(DB_PATH, request, "add", 20, 600)
    if body.product not in ("partner", "forecast", "child"):
        raise HTTPException(422, "unknown product")
    with db() as con:
        row = con.execute("select coupon, input, paid, lang, email from orders where token=?", (token,)).fetchone()
        have = {r[0]: r[1] for r in con.execute("select product, status from items where token=?", (token,))}
    if not row:
        raise HTTPException(404, "order not found")
    coupon, inp, paid, lang, email = row
    if not paid:
        raise HTTPException(402, "order not paid")
    if have.get(body.product, "unpaid") != "unpaid":
        return {"ok": True}  # already bought
    if body.product in ("partner", "child") and not body.partner:
        raise HTTPException(422, "birth data required")
    item_input = body.partner.model_dump(mode="json") if body.partner else None
    included = body.product == "partner" and json.loads(inp).get("bundle")
    if _coupon_ok(coupon or "") or included:
        _add_item(token, body.product, item_input, bg)
        return {"ok": True}
    if not pay.enabled():
        raise HTTPException(402, "payment required")
    if not body.consent:
        raise HTTPException(422, "consent required")
    with db() as con:  # keep the birth data with the unpaid item; payment turns it on
        con.execute("insert into items(token, product, input, status, created) values(?,?,?,?,?)"
                    " on conflict(token, product) do update set input=excluded.input",
                    (token, body.product, json.dumps(item_input or {}), "unpaid", datetime.now(timezone.utc).isoformat()))
    return {"ok": False, "checkout": _checkout(token, _lang(lang), email, body.product, "add", body.product, "upsell",
                                               _track(body.track, request), _coupon_pct(coupon or ""))}


@app.get("/api/order/{token}")
def get_order(token: str):
    with db() as con:
        row = con.execute("select lang, name, chart, input from orders where token=?", (token,)).fetchone()
        if not row:
            raise HTTPException(404, "order not found")
        items = con.execute("select product, status, markdown, data, model from items where token=? and status!='unpaid'"
                            " order by id", (token,)).fetchall()
        sub = con.execute("select cal from subs where order_token=? and status='active'", (token,)).fetchone()
    lang, name, natal, inp = row
    return {
        "cal": cal_url(sub[0]) if sub and sub[0] else None,
        "lang": lang, "name": name, "chart": chart.add_cusps(json.loads(natal)), "input": json.loads(inp),
        "forecastYear": forecast_year(),
        "items": [{"product": p, "status": s, "markdown": md or "", "data": json.loads(d) if d else None, "model": m}
                  for p, s, md, d, m in items],
    }


class PdfIn(BaseModel):
    """Labels the website shows in the reader's language; plain strings, escaped in pdf.py."""
    product: str = Field(pattern="^(natal|partner|forecast|child)$")
    head: dict[str, object] = {}
    tables: list[dict[str, object]] = []
    basis: str = Field("", max_length=60)


@app.post("/api/pdf/{token}")
def report_pdf(token: str, body: PdfIn, request: Request):
    """The report as a downloadable PDF file."""
    from fastapi.responses import Response
    import pdf
    guard.per_ip(DB_PATH, request, "pdf", 20, 600)
    with db() as con:
        row = con.execute("select chart from orders where token=?", (token,)).fetchone()
        it = con.execute("select markdown, data, status from items where token=? and product=?", (token, body.product)).fetchone()
    if not row or not it or it[2] != "ready":
        raise HTTPException(404, "not ready")
    data = json.loads(it[1] or "{}")
    chart_ = {"partner": data.get("partnerChart"), "child": data.get("childChart")}.get(body.product, json.loads(row[0]))
    if body.product == "partner":
        chart_ = json.loads(row[0])  # the wheel shows the reader's chart; the partner's data is in the tables
    head = {k: str(v)[:300] for k, v in body.head.items() if k in ("kicker", "title", "birth", "disclaimer", "lang")}
    head["big3"] = [[str(c)[:80] for c in r][:3] for r in (body.head.get("big3") or [])[:3] if isinstance(r, list)]
    tables = [{"title": str(t.get("title", ""))[:120],
               "rows": [[str(c)[:160] for c in r][:4] for r in (t.get("rows") or [])[:40] if isinstance(r, list)]}
              for t in body.tables[:4]]
    out = pdf.render(it[0] or "", chart_, head, tables, body.basis, data.get("v") == 2)
    return Response(out, media_type="application/pdf",
                    headers={"Content-Disposition": f'attachment; filename="mirastela-{body.product}.pdf"'})


# ---------------------------------------------------------------- subscriptions
class SubIn(BaseModel):
    order: str
    freq: str = Field("weekly", pattern="^(daily|weekly)$")
    plan: str = Field("year", pattern="^(month|year)$")
    consent: bool = False
    track: TrackIn | None = None


CAL_AHEAD = 14  # days of calendar entries kept ready ahead of today


def cal_url(cal_token: str) -> str:
    return f"{emails.SITE}/api/cal/{cal_token}.ics"


def fill_calendar(sub_token: str, ahead: int = CAL_AHEAD):
    """Generate missing calendar days from today to today + ahead, in batches of up to 7."""
    with db() as con:
        row = con.execute("select lang, name, chart from subs where token=?", (sub_token,)).fetchone()
        if not row:
            return
        have = {r[0] for r in con.execute("select day from caldays where sub=? and day>=?", (sub_token, sky.today().isoformat()))}
    lang, name, natal = _lang(row[0]), row[1], json.loads(row[2])
    missing = [sky.today() + timedelta(days=i) for i in range(ahead) if (sky.today() + timedelta(days=i)).isoformat() not in have]
    while missing:
        start = missing[0]
        n = 1
        while n < 7 and n < len(missing) and missing[n] == start + timedelta(days=n):
            n += 1
        entries = cal.generate(lang, name, natal, start, n)
        now = datetime.now(timezone.utc).isoformat()
        with db() as con:
            con.executemany("insert or replace into caldays(sub, day, label, title, text, model, created) values(?,?,?,?,?,?,?)",
                            [(sub_token, e["day"], e["label"], e["title"], e["text"], e["model"], now) for e in entries])
        missing = missing[n:]


def _fill_calendar_safe(sub_token: str):
    try:
        fill_calendar(sub_token)
    except Exception as e:
        print("calendar", sub_token[:6], "error", e)


@app.get("/api/cal/{name}")
def calendar_feed(name: str):
    """ICS feed that calendar apps poll. The token in the URL is the only key, separate from the unsubscribe token."""
    from fastapi.responses import Response
    cal_token = name.removesuffix(".ics")
    with db() as con:
        row = con.execute("select token, lang, name, status from subs where cal=?", (cal_token,)).fetchone()
        if not row:
            raise HTTPException(404, "not found")
        sub_token, lang, nm, status = row
        since = (sky.today() - timedelta(days=60)).isoformat()
        q = "select day, label, title, text from caldays where sub=? and day>=?"
        if status != "active":  # after cancelling, the calendar keeps past days but gets no new ones
            q += f" and day<='{sky.today().isoformat()}'"
        rows = con.execute(q + " order by day", (sub_token, since)).fetchall()
    body = cal.ics(_lang(lang), nm, cal_token, rows, f"{emails.SITE}/{_lang(lang)}/")
    return Response(body, media_type="text/calendar; charset=utf-8",
                    headers={"Content-Disposition": 'inline; filename="mirastela.ics"'})


@app.post("/api/subscribe")
def subscribe(body: SubIn, bg: BackgroundTasks, request: Request):
    guard.per_ip(DB_PATH, request, "sub", 10, 600)
    with db() as con:
        row = con.execute("select lang, email, name, chart, coupon from orders where token=?", (body.order,)).fetchone()
        if not row:
            raise HTTPException(404, "order not found")
        lang, email, name, natal, coupon = row
    if _coupon_ok(coupon or ""):
        return {"ok": True, "cal": _activate_sub(body.order, body.freq, bg)}
    if not pay.enabled():
        raise HTTPException(402, "payment required")
    if not body.consent:
        raise HTTPException(422, "consent required")
    return {"ok": False, "checkout": _checkout(body.order, _lang(lang), email, f"sub_{body.plan}", "sub", body.plan, "sub",
                                               _track(body.track, request))}


def _activate_sub(order: str, freq: str, bg: BackgroundTasks, customer: str | None = None, stripe_sub: str | None = None) -> str:
    """Create or re-activate the subscription for an order, send the welcome email, start the calendar."""
    with db() as con:
        lang, email, name, natal, coupon = con.execute(
            "select lang, email, name, chart, coupon from orders where token=?", (order,)).fetchone()
        existing = con.execute("select token, cal from subs where order_token=?", (order,)).fetchone()
        token = existing[0] if existing else secrets.token_urlsafe(16)
        cal_token = (existing[1] if existing else None) or secrets.token_urlsafe(18)
        con.execute("insert into subs(token, created, email, lang, name, chart, freq, status, order_token, coupon, last_sent, cal,"
                    " stripe_customer, stripe_sub) values(?,?,?,?,?,?,?,?,?,?,?,?,?,?) on conflict(token) do update set"
                    " freq=excluded.freq, status='active', cal=excluded.cal,"
                    " stripe_customer=coalesce(excluded.stripe_customer, stripe_customer), stripe_sub=coalesce(excluded.stripe_sub, stripe_sub)",
                    (token, datetime.now(timezone.utc).isoformat(), email, _lang(lang), name, natal, freq,
                     "active", order, coupon, None, cal_token, customer, stripe_sub))
    unsub = f"{emails.SITE}/api/unsub/{token}"
    subject, html = emails.sub_welcome(_lang(lang), name, freq, unsub, cal_url(cal_token))
    mailer.send(DB_PATH, email, "sub-welcome", subject, html, unsubscribe_url=unsub)
    bg.add_task(_fill_calendar_safe, token)
    return cal_url(cal_token)


# ---------------------------------------------------------------- payments
def _fulfil(session_id: str, meta: dict, bg: BackgroundTasks, customer: str | None = None, stripe_sub: str | None = None) -> dict:
    """Turn a paid Checkout Session into the product. Safe to call twice (webhook and return page race)."""
    token, kind, product = meta.get("token", ""), meta.get("kind", ""), meta.get("product", "")
    with db() as con:
        claimed = con.execute("update payments set status='paid', done=? where session=? and status='open'",
                              (datetime.now(timezone.utc).isoformat(), session_id)).rowcount
    if kind == "gift":
        return _fulfil_gift(session_id, token, product, bool(claimed), bg)
    with db() as con:
        email, lang, oname = con.execute("select email, lang, name from orders where token=?", (token,)).fetchone() or ("", "en", "")
        prow = con.execute("select price_key, track from payments where session=?", (session_id,)).fetchone()
    lang = _lang(lang)
    key = (prow[0] if prow and prow[0] else ("sub_" + product if kind == "sub" else product))
    with db() as con:
        crow = con.execute("select coupon from orders where token=?", (token,)).fetchone()
    cur, minor = pay.price(lang, key, 0 if kind == "sub" else _coupon_pct(crow[0] if crow else ""))
    out = {"token": token, "kind": kind, "product": product, "email": email,
           "value": minor / 100, "currency": cur.upper(), "eventId": f"pur_{session_id}"}
    if kind == "sub":
        with db() as con:
            row = con.execute("select cal from subs where order_token=? and status='active'", (token,)).fetchone()
        out["cal"] = cal_url(row[0]) if row and row[0] else None
    if not claimed:
        return out
    with db() as con:
        affiliates.record(con, session_id, email, kind, key, minor / 100, cur)
    bg.add_task(capi.send, "Purchase", f"pur_{session_id}", f"{emails.SITE}/{lang}/start/", email,
                json.loads(prow[1]) if prow and prow[1] else {}, minor / 100, cur, key, name=oname or "", lang=lang)
    if kind == "order":
        with db() as con:
            con.execute("update orders set paid=1 where token=?", (token,))
        _fulfil_order(token, bg)
    elif kind == "add":
        with db() as con:
            con.execute("update items set status='pending' where token=? and product=? and status='unpaid'", (token, product))
        bg.add_task(_build, token, product)
    elif kind == "sub":
        out["cal"] = _activate_sub(token, "weekly", bg, customer, stripe_sub)
    return out


GIFT_SLUG = {"pl": "prezent", "hr": "poklon", "sl": "darilo", "ro": "cadou", "cs": "darek", "hu": "ajandek",
             "en": "gift", "de": "geschenk", "fr": "cadeau", "it": "regalo"}  # must match web/src/i18n/lang/gift.ts


def _fulfil_gift(session_id: str, code: str, product: str, claimed: bool, bg: BackgroundTasks) -> dict:
    with db() as con:
        if claimed:
            con.execute("update gifts set status='active', session=? where code=? and status='unpaid'", (session_id, code))
        g = gifts.info(con, code) or {}
        email = (con.execute("select email from gifts where code=?", (code,)).fetchone() or [""])[0]
        prow = con.execute("select track from payments where session=?", (session_id,)).fetchone()
    lang = _lang(g.get("lang", "en"))
    cur, minor = pay.price(lang, product)
    out = {"token": code, "kind": "gift", "product": product, "email": email, "gift": g,
           "value": minor / 100, "currency": cur.upper(), "eventId": f"pur_{session_id}"}
    if claimed and g:
        with db() as con:
            affiliates.record(con, session_id, email, "gift", product, minor / 100, cur)
        card = f"{emails.SITE}/{lang}/{GIFT_SLUG[lang]}/?code={code}"
        subject, html = gifts.email(lang, code, pay.product_name(lang, product, forecast_year()), g["expires"], card)
        mailer.send(DB_PATH, email, "gift", subject, html)
        bg.add_task(capi.send, "Purchase", f"pur_{session_id}", f"{emails.SITE}/{lang}/{GIFT_SLUG[lang]}/", email,
                    json.loads(prow[0]) if prow and prow[0] else {}, minor / 100, cur, product, lang=lang)
    return out


class GiftIn(BaseModel):
    lang: str = "en"
    email: str
    product: str = "natal"
    toName: str = Field("", max_length=40)
    fromName: str = Field("", max_length=40)
    message: str = Field("", max_length=300)
    track: TrackIn | None = None
    aff: str = Field("", max_length=40)


@app.post("/api/gift")
def buy_gift(body: GiftIn, request: Request):
    """Start buying a gift: an unpaid code and a Stripe Checkout; the code turns active once paid."""
    guard.per_ip(DB_PATH, request, "gift", 10, 600)
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", body.email):
        raise HTTPException(422, "invalid email")
    if body.product not in gifts.PRODUCTS:
        raise HTTPException(422, "unknown product")
    if not pay.enabled():
        raise HTTPException(402, "payment required")
    lang = _lang(body.lang)
    with db() as con:
        code = gifts.create(con, lang, body.email, body.product, body.toName.strip(), body.fromName.strip(), body.message.strip())
        affiliates.attribute(con, body.email, body.aff, "gift")
    page = f"{emails.SITE}/{lang}/{GIFT_SLUG[lang]}/"
    url = _checkout(code, lang, body.email, body.product, "gift", body.product, "", _track(body.track, request),
                    success_url=page + "?paid={CHECKOUT_SESSION_ID}", cancel_url=page + "?cancel=1")
    return {"checkout": url}


@app.get("/api/gift/{code}")
def gift_card(code: str, request: Request):
    """Details for the printable gift card (the code itself is the key)."""
    guard.per_ip(DB_PATH, request, "giftcard", 60, 600)
    with db() as con:
        g = gifts.info(con, code)
    if not g or g["status"] == "unpaid":
        raise HTTPException(404, "unknown gift")
    return g


@app.get("/api/social/{day}/{lang}/{name}")
def social_media(day: str, lang: str, name: str):
    """Images and reels made by social.py, fetched by Meta when publishing (public, like any posted image)."""
    from fastapi.responses import FileResponse
    if not (re.fullmatch(r"20\d\d-\d\d-\d\d", day) and lang in report.LANG_NAME and re.fullmatch(r"(h\d\d|post)\.jpg|horoscope\.mp4", name)):
        raise HTTPException(404, "not found")
    path = os.path.join(os.environ.get("SOCIAL_DIR", "/var/lib/mirastela/social"), day, lang, name)
    if not os.path.isfile(path):
        raise HTTPException(404, "not found")
    return FileResponse(path, media_type="video/mp4" if name.endswith(".mp4") else "image/jpeg")


@app.get("/api/checkout/confirm")
def checkout_confirm(session: str, bg: BackgroundTasks):
    """The return page after Stripe: confirm the payment directly, without waiting for the webhook."""
    with db() as con:
        if not con.execute("select 1 from payments where session=?", (session,)).fetchone():
            raise HTTPException(404, "unknown session")
    s = pay.retrieve_session(session)
    if not s["paid"]:
        raise HTTPException(402, "not paid")
    return _fulfil(s["id"], s["metadata"], bg, s["customer"], s["subscription"])


@app.post("/api/stripe/webhook")
async def stripe_webhook(request: Request, bg: BackgroundTasks):
    try:
        event = pay.parse_webhook(await request.body(), request.headers.get("stripe-signature", ""))
    except Exception:
        raise HTTPException(400, "bad signature")
    obj = event["data"]["object"]
    kind = event["type"]
    if kind in ("checkout.session.completed", "checkout.session.async_payment_succeeded"):
        if obj.get("payment_status") in ("paid", "no_payment_required"):
            _fulfil(obj["id"], dict(obj.get("metadata") or {}), bg, obj.get("customer"), obj.get("subscription"))
    elif kind == "invoice.paid" and obj.get("billing_reason") == "subscription_cycle":
        # a subscription renewal: the first payment came through Checkout and is recorded there
        with db() as con:
            row = con.execute("select email from subs where stripe_sub=?", (obj.get("subscription") or "",)).fetchone()
            email = row[0] if row else (obj.get("customer_email") or "")
            affiliates.record(con, obj["id"], email, "renew", "sub", (obj.get("amount_paid") or 0) / 100, obj.get("currency") or "")
    elif kind == "customer.subscription.deleted":
        with db() as con:
            con.execute("update subs set status='cancelled' where stripe_sub=?", (obj["id"],))
    return {"ok": True}


@app.get("/api/billing/{sub_token}")
def billing_portal(sub_token: str):
    """Stripe customer portal for a paid subscription (cancel, card, invoices)."""
    from fastapi.responses import RedirectResponse
    with db() as con:
        row = con.execute("select stripe_customer, lang from subs where token=?", (sub_token,)).fetchone()
    if not row or not row[0]:
        raise HTTPException(404, "no paid subscription")
    return RedirectResponse(pay.portal_url(row[0], f"{emails.SITE}/{_lang(row[1])}/"), status_code=303)


@app.api_route("/api/unsub/{token}", methods=["GET", "POST"])
def unsubscribe(token: str, request: Request):
    from fastapi.responses import HTMLResponse
    with db() as con:
        row = con.execute("select lang, stripe_sub from subs where token=?", (token,)).fetchone()
        lead = None if row else con.execute("select lang, lower(email) from leads where token=?", (token,)).fetchone()
        if lead:  # a lead (summary or reminder e-mail): no more marketing e-mails to this address
            if request.method == "POST":
                con.execute("insert or ignore into optout(email, created, via) values(?,?,?)",
                            (lead[1], datetime.now(timezone.utc).isoformat(), "email"))
                con.execute("update leads set marketing_consent=0 where lower(email)=?", (lead[1],))
            return HTMLResponse(emails.optout_page(_lang(lead[0]), request.method == "POST"))
        if request.method == "POST" and row:
            if row[1] and pay.enabled():
                pay.cancel_subscription(row[1])  # access runs to the end of the paid period; the webhook ends it
            else:
                con.execute("update subs set status='cancelled' where token=?", (token,))
    return HTMLResponse(emails.unsub_page(_lang(row[0]) if row else "en", request.method == "POST"))


# ---------------------------------------------------------------- free daily horoscope
import threading

_daily_locks: dict[str, threading.Lock] = {}


def _daily_cached(lang: str, key: str) -> dict | None:
    with db() as con:
        row = con.execute("select data, model from daily where lang=? and day=?", (lang, key)).fetchone()
    return {"day": key, "model": row[1], **json.loads(row[0])} if row else None


def daily_sky(day: date) -> tuple[dict, str]:
    facts = sky.day_sky(day)
    return facts, sky.sky_text(facts)


def daily_parts(lang: str, key: str) -> dict[int, list]:
    with db() as con:
        return {f: json.loads(d) for f, d in con.execute("select first, data from daily_parts where lang=? and day=?", (lang, key))}


def save_daily_half(lang: str, day: date, first: int, signs: list, model: str):
    """Store one half; when both halves are there, publish the day and drop the parts."""
    key = day.isoformat()
    with db() as con:
        con.execute("insert or replace into daily_parts values(?,?,?,?,?)", (lang, key, first, json.dumps(signs, ensure_ascii=False), model))
    parts = daily_parts(lang, key)
    if 0 in parts and 6 in parts:
        facts = sky.day_sky(day)
        data = {"signs": parts[0] + parts[6], "sky": {"planets": [{k: p[k] for k in ("id", "signIndex", "deg", "retro")} for p in facts["planets"]],
                                                      "moonIngress": facts["moonIngress"]}}
        with db() as con:
            con.execute("insert or replace into daily values(?,?,?,?,?)",
                        (lang, key, json.dumps(data, ensure_ascii=False), model, datetime.now(timezone.utc).isoformat()))
            con.execute("delete from daily_parts where lang=? and day=?", (lang, key))


def daily_for(lang: str, day: date) -> dict:
    """Twelve sign horoscopes for one language and day. Normally prepared ahead by the batch job;
    whatever is still missing is generated here with direct calls (blocking)."""
    key = day.isoformat()
    hit = _daily_cached(lang, key)
    if hit:
        return hit
    lock = _daily_locks.setdefault(lang, threading.Lock())
    with lock:
        hit = _daily_cached(lang, key)
        if hit:
            return hit
        facts, txt = daily_sky(day)
        if not report.has_key():  # test mode: instant placeholder text, nothing stored
            signs = [{"general": f"TEST MODE ({chart.SIGNS[i]}). " + ", ".join(f"{p['id']} {p['sign']}" for p in facts["planets"][:5]),
                      "love": "TEST MODE", "work": "TEST MODE"} for i in range(12)]
            return {"day": key, "model": "test", "signs": signs,
                    "sky": {"planets": [{k: p[k] for k in ("id", "signIndex", "deg", "retro")} for p in facts["planets"]],
                            "moonIngress": facts["moonIngress"]}}
        for first in (0, 6):
            if first in daily_parts(lang, key):
                continue
            for attempt in range(4):
                try:
                    params = report.daily_params(lang, key, txt, first)
                    out = report.tool_input(report.client().messages.create(**params))
                    signs, why = report.daily_half(lang, out, first)
                    if signs:
                        save_daily_half(lang, day, first, signs, params["model"])
                        break
                    print("daily", lang, key, first, why, attempt, flush=True)
                except Exception as e:
                    print("daily", lang, key, first, "error", attempt, repr(e)[:300], flush=True)
            else:
                raise HTTPException(503, "generation failed")
        hit = _daily_cached(lang, key)
        if not hit:
            raise HTTPException(503, "generation failed")
        return hit


@app.get("/api/daily")
def daily(lang: str = "en", day: date | None = None):
    """Cached text right away; otherwise 202 while it is generated in the background (the cron job
    normally generates today and tomorrow shortly after midnight)."""
    lang = _lang(lang)
    d = day or sky.today()
    if abs((d - sky.today()).days) > 1:
        raise HTTPException(422, "only yesterday, today or tomorrow")
    hit = _daily_cached(lang, d.isoformat())
    if hit:
        return hit
    if not report.has_key():
        return daily_for(lang, d)  # test mode is instant
    lock = _daily_locks.setdefault(lang, threading.Lock())
    if not lock.locked():
        threading.Thread(target=lambda: _safe_daily(lang, d), daemon=True).start()
    return JSONResponse({"pending": True}, status_code=202)


def _safe_daily(lang: str, d: date):
    try:
        daily_for(lang, d)
    except Exception as e:
        print("daily", lang, d, "error", e)


# ---------------------------------------------------------------- account ("my reports"), magic link
LOGIN_TTL = timedelta(minutes=30)
ACCOUNT_TTL = timedelta(days=90)
ADD_ONS = ("partner", "forecast", "child")


def _account_tables(con):
    con.execute("create table if not exists logins(token text primary key, email text, lang text, created text, used text)")
    con.execute("create table if not exists accounts(key text primary key, email text, created text)")


def _known(con, email: str) -> bool:
    return any(con.execute(f"select 1 from {t} where lower(email)=? limit 1", (email,)).fetchone()
               for t in ("orders", "subs", "leads"))


class LoginIn(BaseModel):
    email: str = Field(max_length=200)
    lang: str = "en"
    captcha: str | None = Field(None, max_length=4000)


@app.post("/api/account/login")
def account_login(body: LoginIn, request: Request, bg: BackgroundTasks):
    """Email a one-time sign-in link. Same answer whether or not the address is known."""
    email = body.email.strip().lower()
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        raise HTTPException(422, "invalid email")
    guard.per_ip(DB_PATH, request, "login", 5, 600)
    guard.limit(DB_PATH, f"login-mail:{email}", 3, 900)
    guard.turnstile(body.captcha, request)
    lang = _lang(body.lang)
    with db() as con:
        _account_tables(con)
        if not _known(con, email):
            return {"ok": True}
        token = secrets.token_urlsafe(24)
        con.execute("insert into logins(token, email, lang, created) values(?,?,?,?)",
                    (token, email, lang, datetime.now(timezone.utc).isoformat()))
    subject, html = emails.login(lang, f"{emails.SITE}/{lang}/account/?t={token}")
    bg.add_task(mailer.send, DB_PATH, email, "login", subject, html)
    return {"ok": True}


class SessionIn(BaseModel):
    t: str = Field(max_length=100)


@app.post("/api/account/session")
def account_session(body: SessionIn, request: Request):
    """Exchange the one-time link for an account key the browser keeps (90 days)."""
    guard.per_ip(DB_PATH, request, "session", 20, 600)
    now = datetime.now(timezone.utc)
    with db() as con:
        _account_tables(con)
        row = con.execute("select email, created, used from logins where token=?", (body.t,)).fetchone()
        if not row or row[2] or now - datetime.fromisoformat(row[1]) > LOGIN_TTL:
            raise HTTPException(410, "link expired")
        con.execute("update logins set used=? where token=?", (now.isoformat(), body.t))
        key = secrets.token_urlsafe(32)
        con.execute("insert into accounts(key, email, created) values(?,?,?)", (key, row[0], now.isoformat()))
    return {"key": key}


class KeyIn(BaseModel):
    key: str = Field(max_length=100)


def _account_email(key: str) -> str:
    with db() as con:
        _account_tables(con)
        row = con.execute("select email, created from accounts where key=?", (key,)).fetchone()
    if not row or datetime.now(timezone.utc) - datetime.fromisoformat(row[1]) > ACCOUNT_TTL:
        raise HTTPException(401, "signed out")
    return row[0]


@app.post("/api/account/me")
def account_me(body: KeyIn):
    email = _account_email(body.key)
    with db() as con:
        orders = con.execute("select token, created, lang, name, input, coupon from orders"
                             " where lower(email)=? and paid=1 order by created desc", (email,)).fetchall()
        subs = con.execute("select token, order_token, status, cal, stripe_customer, created from subs"
                           " where lower(email)=? order by created desc", (email,)).fetchall()
        items = {}
        for tok, *_ in orders:
            items[tok] = {p: s for p, s in con.execute("select product, status from items where token=? order by id", (tok,))}
    sub_by_order = {s[1]: s for s in subs}
    out = []
    for tok, created, lang, name, inp, coupon in orders:
        have = items.get(tok, {})
        owned = [{"product": p, "status": s} for p, s in have.items() if s != "unpaid"]
        bundle = bool(json.loads(inp).get("bundle"))
        missing = [p for p in ADD_ONS if have.get(p, "unpaid") == "unpaid"]
        s = sub_by_order.get(tok)
        out.append({"token": tok, "created": created[:10], "lang": _lang(lang), "name": name, "bundle": bundle,
                    "free": _coupon_ok(coupon or ""), "discount": _coupon_pct(coupon or "") % 100, "owned": owned, "missing": missing,
                    "sub": {"status": s[2], "cal": cal_url(s[3]) if s[3] and s[2] == "active" else None,
                            "billing": f"/api/billing/{s[0]}" if s[4] else None,
                            "unsub": f"/api/unsub/{s[0]}" if s[2] == "active" else None} if s else None})
    return {"email": email, "orders": out}


def export_data(email: str) -> dict:
    """Everything stored about one email address (GDPR access request)."""
    email = email.strip().lower()
    with db() as con:
        _account_tables(con)
        con.row_factory = sqlite3.Row
        q = lambda sql, *a: [dict(r) for r in con.execute(sql, a)]
        orders = q("select * from orders where lower(email)=?", email)
        toks = [o["token"] for o in orders]
        subs = q("select * from subs where lower(email)=?", email)
        ph = ",".join("?" * len(toks)) or "''"
        sph = ",".join("?" * len(subs)) or "''"
        data = {
            "email": email,
            "leads": q("select * from leads where lower(email)=?", email),
            "orders": orders,
            "items": q(f"select token, product, input, status, markdown, created from items where token in ({ph})", *toks),
            "subscriptions": subs,
            "calendar": q(f"select * from caldays where sub in ({sph})", *[s["token"] for s in subs]),
            "payments": q(f"select session, token, kind, product, status, created, done, consent from payments where token in ({ph})", *toks),
            "emails": q("select created, kind, subject, status from emails where lower(recipient)=?", email)
            if con.execute("select 1 from sqlite_master where name='emails'").fetchone() else [],
        }
    for k in ("orders", "subscriptions"):
        for row in data[k]:
            for f in ("input", "chart"):
                if isinstance(row.get(f), str):
                    try:
                        row[f] = json.loads(row[f])
                    except ValueError:
                        pass
    return data


def forget(email: str) -> dict:
    """Delete everything about one email address. Paid Stripe subscriptions are cancelled right away
    (Stripe keeps its own payment and tax records as the merchant of record)."""
    email = email.strip().lower()
    with db() as con:
        _account_tables(con)
        toks = [r[0] for r in con.execute("select token from orders where lower(email)=?", (email,))]
        subs = con.execute("select token, stripe_sub, status from subs where lower(email)=?", (email,)).fetchall()
    for _, stripe_sub, status in subs:
        if stripe_sub and status == "active" and pay.enabled():
            try:
                pay.cancel_subscription(stripe_sub, now=True)
            except Exception as e:
                print("forget: stripe cancel failed", e)
    counts = {}
    with db() as con:
        ph = ",".join("?" * len(toks)) or "''"
        sph = ",".join("?" * len(subs)) or "''"
        for name, sql, args in (
            ("items", f"delete from items where token in ({ph})", toks),
            ("payments", f"delete from payments where token in ({ph})", toks),
            ("caldays", f"delete from caldays where sub in ({sph})", [s[0] for s in subs]),
            ("subs", "delete from subs where lower(email)=?", [email]),
            ("orders", "delete from orders where lower(email)=?", [email]),
            ("leads", "delete from leads where lower(email)=?", [email]),
            ("logins", "delete from logins where lower(email)=?", [email]),
            ("accounts", "delete from accounts where lower(email)=?", [email]),
        ):
            counts[name] = con.execute(sql, args).rowcount
        if con.execute("select 1 from sqlite_master where name='emails'").fetchone():
            counts["emails"] = con.execute("delete from emails where lower(recipient)=?", (email,)).rowcount
    print("forget", email.split("@")[-1], counts, flush=True)
    return counts


@app.post("/api/account/export")
def account_export(body: KeyIn, request: Request):
    guard.per_ip(DB_PATH, request, "export", 10, 3600)
    return JSONResponse(export_data(_account_email(body.key)),
                        headers={"Content-Disposition": 'attachment; filename="mirastela-data.json"'})


class DeleteIn(KeyIn):
    confirm: bool = False


@app.post("/api/account/delete")
def account_delete(body: DeleteIn, request: Request):
    guard.per_ip(DB_PATH, request, "delete", 5, 3600)
    if not body.confirm:
        raise HTTPException(422, "confirm required")
    forget(_account_email(body.key))
    return {"ok": True}


@app.post("/api/account/logout")
def account_logout(body: KeyIn):
    with db() as con:
        _account_tables(con)
        con.execute("delete from accounts where key=?", (body.key,))
    return {"ok": True}
