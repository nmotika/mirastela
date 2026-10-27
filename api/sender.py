"""Scheduled jobs (systemd timers): pages every hour at :15, subs at 06:00, Europe/Zagreb.
  python sender.py pages   free sign horoscopes in every language (batch two days ahead, direct fallback)
  python sender.py subs    fill personal calendars, send personal horoscopes (weekly ones on Mondays)
  python sender.py all     both
  python sender.py recal   regenerate future calendar days for everyone (after changing cal.py)
  python sender.py prune   retention clean-up (also runs after subs)
  python sender.py repages regenerate yesterday's, today's and tomorrow's free horoscopes (after changing the prompt)
"""
from __future__ import annotations

import json
import sys
from datetime import date, datetime, timedelta, timezone

import app
import emails
import mailer
import report
import sky


BATCH_GRACE = timedelta(hours=6)  # after this, a day still waiting for its batch is generated directly


def _open_batches() -> list[tuple[str, str, list[str]]]:
    with app.db() as con:
        return [(b, c, json.loads(i)) for b, c, i in con.execute("select id, created, items from daily_batches where status='open'")]


def collect_batches():
    """Store the results of finished batches (each request is one half of one language and day)."""
    if not report.has_key():
        return
    client = report.client()
    for bid, _, _ in _open_batches():
        b = client.messages.batches.retrieve(bid)
        if b.processing_status != "ended":
            continue
        ok = bad = 0
        for r in client.messages.batches.results(bid):
            lang, key, first = r.custom_id.split("_")
            day = date.fromisoformat(f"{key[:4]}-{key[4:6]}-{key[6:]}")
            if app._daily_cached(lang, day.isoformat()):
                continue
            signs, why = (None, r.result.type)
            if r.result.type == "succeeded":
                try:
                    signs, why = report.daily_half(lang, report.tool_input(r.result.message), int(first))
                except Exception as e:
                    why = repr(e)[:200]
            if signs:
                app.save_daily_half(lang, day, int(first), signs, r.result.message.model)
                ok += 1
            else:
                bad += 1
                print("batch", bid, r.custom_id, why, flush=True)
        with app.db() as con:
            con.execute("update daily_batches set status='done' where id=?", (bid,))
        print("batch", bid, "collected", ok, "ok", bad, "failed", flush=True)


def submit_batch(days: list[date]):
    """One batch with every half that is missing and not already waiting in an open batch."""
    if not report.has_key():
        return
    pending = {i for _, _, items in _open_batches() for i in items}
    requests = []
    for day in days:
        key = day.isoformat()
        _, txt = app.daily_sky(day)
        for lang in report.LANG_NAME:
            if app._daily_cached(lang, key):
                continue
            have = app.daily_parts(lang, key)
            for first in (0, 6):
                cid = f"{lang}_{key.replace('-', '')}_{first}"
                if first not in have and cid not in pending:
                    requests.append({"custom_id": cid, "params": report.daily_params(lang, key, txt, first)})
    if not requests:
        return
    b = report.client().messages.batches.create(requests=requests)
    with app.db() as con:
        con.execute("insert into daily_batches values(?,?,?,?)", (b.id, datetime.now(timezone.utc).isoformat(), "open",
                                                                  json.dumps([r["custom_id"] for r in requests])))
    print("batch", b.id, "submitted", len(requests), "requests", flush=True)


def pages():
    """Free sign horoscopes in every language (runs every hour). Days two ahead go through the Batch
    API at half price; yesterday, today and tomorrow are generated directly only if still missing
    (tomorrow only once its batch is late)."""
    today = sky.today()
    try:
        collect_batches()
        submit_batch([today + timedelta(days=1), today + timedelta(days=2)])
    except Exception as e:
        print("batch error", repr(e)[:300], flush=True)
    waiting = {}
    for _, created, items in _open_batches():
        for i in items:
            waiting[i] = min(waiting.get(i, created), created)
    now = datetime.now(timezone.utc)
    for day in (today - timedelta(days=1), today, today + timedelta(days=1)):
        for lang in report.LANG_NAME:
            if app._daily_cached(lang, day.isoformat()):
                continue
            ids = [f"{lang}_{day.isoformat().replace('-', '')}_{f}" for f in (0, 6)]
            since = [datetime.fromisoformat(waiting[i]) for i in ids if i in waiting]
            if day > today and since and now - min(since) < BATCH_GRACE:
                continue  # its batch should arrive soon
            try:
                app.daily_for(lang, day)
                print("pages", lang, day, "ok (direct)")
            except Exception as e:
                print("pages", lang, day, "error", e)


def calendars():
    """Keep two weeks of personal calendar days ready for every active subscriber."""
    with app.db() as con:
        rows = con.execute("select token from subs where status='active' and cal is not null").fetchall()
    for (token,) in rows:
        try:
            app.fill_calendar(token)
            print("calendar", token[:6], "ok")
        except Exception as e:
            print("calendar", token[:6], "error", e)


def recal():
    """After a change to labels or texts: drop future calendar days and generate them again."""
    with app.db() as con:
        con.execute("delete from caldays where day>=?", (sky.today().isoformat(),))
    calendars()


def subs():
    calendars()
    day = sky.today()
    monday = day.weekday() == 0
    with app.db() as con:
        rows = con.execute("select token, email, lang, name, chart, freq, last_sent from subs where status='active'").fetchall()
    for token, email, lang, name, natal, freq, last in rows:
        if last == day.isoformat() or (freq == "weekly" and not monday):
            continue
        natal = json.loads(natal)
        days = 7 if freq == "weekly" else 1
        try:
            md, _ = report.generate(report.prompt_personal(lang, name, natal, sky.personal_text(natal, day, days), freq == "weekly"),
                                    fast=True, max_tokens=2500, fallback="## TEST MODE\n\n" + sky.personal_text(natal, day, days))
            unsub = f"{emails.SITE}/api/unsub/{token}"
            subject, html = emails.horoscope(lang, name, freq, day, md, unsub)
            mailer.send(app.DB_PATH, email, f"horoscope-{freq}", subject, html, unsubscribe_url=unsub)
            with app.db() as con:
                con.execute("update subs set last_sent=? where token=?", (day.isoformat(), token))
            print("sub", token[:6], freq, "sent")
        except Exception as e:
            print("sub", token[:6], "error", e)


def prune():
    """Retention: leads that never bought go after 12 months, the email log after 12 months,
    sign-in links after a day, account sessions after 90 days, rate-limit hits after a day."""
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    ago = lambda **kw: (now - timedelta(**kw)).isoformat()
    with app.db() as con:
        app._account_tables(con)
        con.execute("create table if not exists hits(key text, ts real)")
        n = {
            "leads": con.execute("delete from leads where created<? and lower(email) not in (select lower(email) from orders)"
                                 " and lower(email) not in (select lower(email) from subs)", (ago(days=365),)).rowcount,
            "logins": con.execute("delete from logins where created<?", (ago(days=1),)).rowcount,
            "accounts": con.execute("delete from accounts where created<?", (ago(days=90),)).rowcount,
            "hits": con.execute("delete from hits where ts<?", (now.timestamp() - 86400,)).rowcount,
        }
        if con.execute("select 1 from sqlite_master where name='emails'").fetchone():
            n["emails"] = con.execute("delete from emails where created<?", (ago(days=365),)).rowcount
            con.execute("update emails set html='' where created<? and html!=''", (ago(days=30),))
    print("prune", n)


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    if what in ("pages", "all", "reminders"):
        try:  # the hourly run also sends the 24 h reminders; a failure there must not stop the pages
            print("reminders sent:", app.send_reminders(), flush=True)
        except Exception as e:  # noqa: BLE001
            print("reminders error", repr(e)[:300], flush=True)
    if what in ("pages", "all"):
        pages()
    if what in ("subs", "all"):
        subs()
        prune()
    if what == "recal":
        recal()
    if what == "prune":
        prune()
    if what == "repages":
        since = (sky.today() - timedelta(days=1)).isoformat()
        with app.db() as con:
            con.execute("delete from daily where day>=?", (since,))
            con.execute("delete from daily_parts where day>=?", (since,))
            con.execute("update daily_batches set status='dropped' where status='open'")
        pages()
