"""Scheduled jobs (systemd timers): pages at 00:15, subs at 06:00, Europe/Zagreb.
  python sender.py pages   pre-generate today's free sign horoscopes in every language
  python sender.py subs    fill personal calendars, send personal horoscopes (weekly ones on Mondays)
  python sender.py all     both
  python sender.py recal   regenerate future calendar days for everyone (after changing cal.py)
"""
from __future__ import annotations

import json
import sys
from datetime import timedelta

import app
import emails
import mailer
import report
import sky


def pages():
    """Free sign horoscopes for yesterday, today and tomorrow in every language (run shortly after
    midnight). Days already in the database are skipped, so normally only tomorrow is generated."""
    for day in (sky.today() - timedelta(days=1), sky.today(), sky.today() + timedelta(days=1)):
        for lang in report.LANG_NAME:
            try:
                app.daily_for(lang, day)
                print("pages", lang, day, "ok")
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


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    if what in ("pages", "all"):
        pages()
    if what in ("subs", "all"):
        subs()
    if what == "recal":
        recal()
