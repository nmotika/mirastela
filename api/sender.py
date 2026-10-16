"""Scheduled jobs (systemd timer, every morning):
  python sender.py pages   pre-generate today's free sign horoscopes in every language
  python sender.py subs    send personal daily horoscopes (and weekly ones on Mondays)
  python sender.py all     both
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
    for lang in report.LANG_NAME:
        try:
            app.daily_for(lang, sky.today())
            print("pages", lang, "ok")
        except Exception as e:
            print("pages", lang, "error", e)


def subs():
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
