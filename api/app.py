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
import chart
import pay
import cities
import emails
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
    sub_cols = {r[1] for r in con.execute("pragma table_info(subs)")}
    for col in ("cal", "stripe_customer", "stripe_sub"):
        if col not in sub_cols:
            con.execute(f"alter table subs add column {col} text")
    if "paid" not in {r[1] for r in con.execute("pragma table_info(orders)")}:
        con.execute("alter table orders add column paid integer default 1")  # rows before payments existed were coupon orders
    con.execute("""create table if not exists payments(
        session text primary key, token text, kind text, product text, status text, created text, done text)""")
    return con


COUPONS = {c.strip().upper() for c in os.environ.get("MIRASTELA_COUPONS", "MIRATEST").split(",") if c.strip()}
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
def make_chart(body: ChartIn):
    city = cities.get(body.cityId)
    if not city:
        raise HTTPException(404, "city not found")
    if not (date(1900, 1, 1) <= body.date <= datetime.now(timezone.utc).date()):
        raise HTTPException(422, "date out of range")
    clock = time.fromisoformat(body.time) if body.time else None
    res = chart.calculate(chart.BirthData(body.date, clock, city["lat"], city["lon"], city["tz"]))
    res["city"] = {k: city[k] for k in ("id", "name", "country", "tz")}
    return res


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


@app.post("/api/lead")
def lead(body: LeadIn, bg: BackgroundTasks):
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", body.email):
        raise HTTPException(422, "invalid email")
    token = secrets.token_urlsafe(12)
    with db() as con:
        con.execute("insert into leads(created,email,lang,name,birth_date,birth_time,city_id,focus,status,marketing_consent,token)"
                    " values(?,?,?,?,?,?,?,?,?,?,?)",
                    (datetime.now(timezone.utc).isoformat(), body.email.lower(), body.lang, body.name[:80],
                     body.date, body.time, body.cityId, ",".join(body.focus), body.status,
                     int(body.marketingConsent), token))
    if body.date and body.cityId:
        bg.add_task(_send_summary, token)
    return {"ok": True, "token": token}


def _lang(x: str) -> str:
    return x if x in report.LANG_NAME else "en"


def _send_summary(token: str):
    """Short free summary of the chart, written by the fast model, with a link back to the offer."""
    with db() as con:
        email, lang, name, d, t, city_id, focus = con.execute(
            "select email, lang, name, birth_date, birth_time, city_id, focus from leads where token=?", (token,)).fetchone()
    lang = _lang(lang)
    natal = birth_chart(d, t, city_id)
    focus_l = [f for f in (focus or "").split(",") if f]
    sun, moon = natal["planets"][0], natal["planets"][1]
    fallback = f"TEST MODE: sun {sun['sign']} {sun['deg']}°, moon {moon['sign']} {moon['deg']}°."
    text = ""
    for attempt in range(2):
        try:
            out, _ = report.generate_json(report.prompt_summary(lang, name, natal, focus_l), report.PARAGRAPHS_SCHEMA,
                                          max_tokens=2000, fallback={"paragraphs": [fallback]})
            paras = (out or {}).get("paragraphs")
            if isinstance(paras, str):
                paras = [paras]
            text = "\n".join(p.strip() for p in (paras or []) if isinstance(p, str) and p.strip())
            if text:
                break
            print("summary", token[:6], "empty", attempt, str(out)[:300], flush=True)
        except Exception as e:
            print("summary", token[:6], "error", attempt, repr(e)[:300], flush=True)
    subject, html = emails.summary(lang, name, natal, text, f"{emails.SITE}/{lang}/start/?r={token}")
    mailer.send(DB_PATH, email, "summary", subject, html)


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
    bundle: bool = False


class AddIn(BaseModel):
    product: str
    partner: PartnerIn | None = None


def _coupon_ok(code: str) -> bool:
    return code.strip().upper() in COUPONS


def _build(token: str, product: str):
    """Compute the product's data and write the report (runs in the background)."""
    with db() as con:
        lang, name, inp, natal = con.execute(
            "select lang, name, input, chart from orders where token=?", (token,)).fetchone()
        item_input = con.execute("select input from items where token=? and product=?", (token, product)).fetchone()[0]
    natal, inp = json.loads(natal), json.loads(inp)
    try:
        if product == "natal":
            bal = chart.balance(natal)
            data = {"balance": bal}
            prompt = report.prompt_natal(lang, name, natal, inp.get("focus", []), bal)
        elif product == "child":
            p = json.loads(item_input)
            cc = birth_chart(p["date"], p.get("time"), p["cityId"])
            bal = chart.balance(cc)
            data = {"child": p, "childChart": cc, "balance": bal}
            prompt = report.prompt_child(lang, name, p.get("name", ""), cc, bal)
        elif product == "partner":
            p = json.loads(item_input)
            pc = birth_chart(p["date"], p.get("time"), p["cityId"])
            syn = chart.synastry(natal, pc)
            data = {"partner": p, "partnerChart": pc, "synastry": syn}
            prompt = report.prompt_partner(lang, name, p.get("name", ""), natal, pc, syn)
        else:
            tr = chart.transits(natal, forecast_year())
            data = {"transits": tr}
            prompt = report.prompt_forecast(lang, name, natal, tr)
        md, model = report.generate(prompt)
        status = "ready"
    except Exception as exc:  # keep the error visible for debugging
        data, md, model, status = {"error": str(exc)}, "", "", "error"
    with db() as con:
        con.execute("update items set data=?, markdown=?, model=?, status=? where token=? and product=?",
                    (json.dumps(data), md, model, status, token, product))
        email = con.execute("select email from orders where token=?", (token,)).fetchone()[0]
    if status == "ready":
        lang = _lang(lang)
        subject, html = emails.report_ready(lang, name, product, forecast_year(),
                                            f"{emails.SITE}/{lang}/report/?o={token}&t={product}")
        mailer.send(DB_PATH, email, f"report-{product}", subject, html)


def _add_item(token: str, product: str, item_input: dict | None, bg: BackgroundTasks):
    with db() as con:
        con.execute("insert or ignore into items(token, product, input, status, created) values(?,?,?,?,?)",
                    (token, product, json.dumps(item_input or {}), "pending", datetime.now(timezone.utc).isoformat()))
    bg.add_task(_build, token, product)


@app.post("/api/order")
def create_order(body: OrderIn, bg: BackgroundTasks):
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", body.email):
        raise HTTPException(422, "invalid email")
    free = _coupon_ok(body.coupon)
    if not free and not pay.enabled():
        raise HTTPException(402, "payment required")
    natal = birth_chart(body.date.isoformat(), body.time, body.cityId)
    token = secrets.token_urlsafe(16)
    with db() as con:
        con.execute("insert into orders(token, created, lang, email, name, input, chart, coupon, paid) values(?,?,?,?,?,?,?,?,?)",
                    (token, datetime.now(timezone.utc).isoformat(), body.lang, body.email.lower(), body.name,
                     body.model_dump_json(exclude={"coupon"}), json.dumps(natal),
                     body.coupon.strip().upper() if free else "", 1 if free else 0))
    if not free:
        key = "bundle" if body.bundle else "natal"
        return {"token": token, "checkout": _checkout(token, _lang(body.lang), body.email, key, "order", key, "offer")}
    _fulfil_order(token, bg)
    return {"token": token}


def _fulfil_order(token: str, bg: BackgroundTasks):
    with db() as con:
        inp = json.loads(con.execute("select input from orders where token=?", (token,)).fetchone()[0])
    _add_item(token, "natal", None, bg)
    if inp.get("bundle"):  # natal + yearly forecast now; the partner report once their details are given
        _add_item(token, "forecast", None, bg)


def _checkout(token: str, lang: str, email: str, key: str, kind: str, product: str, cancel_step: str) -> str:
    s = pay.create_session(lang, email, key, forecast_year(), {"token": token, "kind": kind, "product": product}, cancel_step)
    with db() as con:
        con.execute("insert into payments(session, token, kind, product, status, created) values(?,?,?,?,?,?)",
                    (s["id"], token, kind, product, "open", datetime.now(timezone.utc).isoformat()))
    return s["url"]


@app.post("/api/coupon")
def check_coupon(body: dict):
    return {"valid": _coupon_ok(str(body.get("code", "")))}


@app.post("/api/order/{token}/add")
def add_product(token: str, body: AddIn, bg: BackgroundTasks):
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
    with db() as con:  # keep the birth data with the unpaid item; payment turns it on
        con.execute("insert into items(token, product, input, status, created) values(?,?,?,?,?)"
                    " on conflict(token, product) do update set input=excluded.input",
                    (token, body.product, json.dumps(item_input or {}), "unpaid", datetime.now(timezone.utc).isoformat()))
    return {"ok": False, "checkout": _checkout(token, _lang(lang), email, body.product, "add", body.product, "upsell")}


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


# ---------------------------------------------------------------- subscriptions
class SubIn(BaseModel):
    order: str
    freq: str = Field("weekly", pattern="^(daily|weekly)$")
    plan: str = Field("year", pattern="^(month|year)$")


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
def subscribe(body: SubIn, bg: BackgroundTasks):
    with db() as con:
        row = con.execute("select lang, email, name, chart, coupon from orders where token=?", (body.order,)).fetchone()
        if not row:
            raise HTTPException(404, "order not found")
        lang, email, name, natal, coupon = row
    if _coupon_ok(coupon or ""):
        return {"ok": True, "cal": _activate_sub(body.order, body.freq, bg)}
    if not pay.enabled():
        raise HTTPException(402, "payment required")
    return {"ok": False, "checkout": _checkout(body.order, _lang(lang), email, f"sub_{body.plan}", "sub", body.plan, "sub")}


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
        email = (con.execute("select email from orders where token=?", (token,)).fetchone() or [""])[0]
    out = {"token": token, "kind": kind, "product": product, "email": email}
    if kind == "sub":
        with db() as con:
            row = con.execute("select cal from subs where order_token=? and status='active'", (token,)).fetchone()
        out["cal"] = cal_url(row[0]) if row and row[0] else None
    if not claimed:
        return out
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


def daily_for(lang: str, day: date) -> dict:
    """Twelve sign horoscopes for one language and day, generated once and cached (blocking)."""
    key = day.isoformat()
    hit = _daily_cached(lang, key)
    if hit:
        return hit
    lock = _daily_locks.setdefault(lang, threading.Lock())
    with lock:
        hit = _daily_cached(lang, key)
        if hit:
            return hit
        facts = sky.day_sky(day)
        fallback = json.dumps([{"general": f"TEST MODE ({chart.SIGNS[i]}). " + ", ".join(
            f"{p['id']} {p['sign']}" for p in facts["planets"][:5]), "love": "TEST MODE", "work": "TEST MODE"} for i in range(12)])
        # Two halves of six signs: shorter outputs, and one bad half is retried without redoing the other.
        signs, model, txt = [], "test", sky.sky_text(facts)
        for first in (0, 6):
            fb = json.dumps(json.loads(fallback)[first:first + 6])
            for attempt in range(3):
                try:
                    out, model = report.generate_json(report.prompt_daily_signs(lang, key, txt, first, 6), report.SIGNS_SCHEMA,
                                                      max_tokens=6000, fallback={"signs": json.loads(fb)})
                    part = (out or {}).get("signs")
                    if isinstance(part, str):  # the model sometimes passes the list as a JSON string
                        part = report.parse_json(part)
                    if isinstance(part, list) and len(part) == 12:  # wrote all twelve: keep this half
                        part = part[first:first + 6]
                    if isinstance(part, list) and len(part) == 6 and all(isinstance(x, dict) and x.get("general") for x in part):
                        signs += part
                        break
                    print("daily", lang, key, first, "bad shape", attempt, type(part).__name__,
                          len(part) if isinstance(part, (list, str)) else "", str(out)[:200], flush=True)
                except Exception as e:
                    print("daily", lang, key, first, "error", attempt, repr(e)[:300], flush=True)
            else:
                raise HTTPException(503, "generation failed")
        data = {"signs": signs, "sky": {"planets": [{k: p[k] for k in ("id", "signIndex", "deg", "retro")} for p in facts["planets"]],
                                        "moonIngress": facts["moonIngress"]}}
        if model != "test":
            with db() as con:
                con.execute("insert or replace into daily values(?,?,?,?,?)",
                            (lang, key, json.dumps(data, ensure_ascii=False), model, datetime.now(timezone.utc).isoformat()))
        return {"day": key, "model": model, **data}


class FeedbackIn(BaseModel):
    email: str = Field("", max_length=200)
    answers: dict[str, str | int | None]


@app.post("/api/feedback")
def feedback(body: FeedbackIn, request: Request, tasks: BackgroundTasks):
    """Tester questionnaire. The email comes from Cloudflare Access when present."""
    answers = {k[:40]: (v[:3000] if isinstance(v, str) else v) for k, v in list(body.answers.items())[:40]}
    # Anonymous on purpose: no e-mail, only the kind of device.
    email = ""
    raw_ua = request.headers.get("user-agent", "")
    ua = "mobitel" if any(k in raw_ua for k in ("Mobile", "Android", "iPhone")) else "računalo"
    with db() as con:
        con.execute("insert into feedback(created, email, answers, ua) values(?,?,?,?)",
                    (datetime.now(timezone.utc).isoformat(), email, json.dumps(answers, ensure_ascii=False), ua))
    admin = os.environ.get("MIRASTELA_ADMIN_EMAIL", "").strip()
    if admin:
        rows = "".join(f"<p style='margin:0 0 10px;font:15px/1.5 Arial,sans-serif;color:#F3EEE3'><b>{emails.esc(k)}</b><br>"
                       f"{emails.esc(str(v if v is not None else ''))}</p>" for k, v in answers.items())
        html = emails.layout("hr", f"<p style='font:15px Arial,sans-serif;color:#A9B0C6'>{emails.esc(ua)}</p>{rows}")
        tasks.add_task(mailer.send, DB_PATH, admin, "feedback", "Mirastela: novi odgovor iz upitnika", html)
    return {"ok": True}


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
