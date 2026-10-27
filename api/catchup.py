"""One-off e-mail for leads from before summary v2: a fresh summary with open questions, sent once to
leads who opted in to marketing e-mails, never bought and never opted out (latest lead per address).

  python catchup.py count                 how many, per language
  python catchup.py preview [N] [LANG]    write N sample e-mails to /tmp/catchup-*.html and print the texts; sends nothing
  python catchup.py send [LIMIT]          generate, save and send (marks each lead, so a rerun never sends twice)
"""
from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timezone

import app
import emails
import mailer

Q = """select token, lower(email), lang, name, birth_date, birth_time, city_id, focus, status, src from leads l
       where marketing_consent=1 and summary is null and reminded is null
         and birth_date != '' and city_id is not null
         and lower(email) not in (select email from optout)
         and lower(email) not in (select lower(email) from orders where paid=1)
         and lower(email) not in (select lower(email) from leads where reminded is not null)
         and created = (select max(created) from leads x where lower(x.email) = lower(l.email))
       order by created"""


def rows(lang: str = "") -> list[tuple]:
    with app.db() as con:
        out = con.execute(Q).fetchall()
    return [r for r in out if not lang or r[2] == lang]


def build(r: tuple) -> tuple[str, str, str, dict]:
    token, email, lang, name, d, t, city, focus, status, src = r
    lang = app._lang(lang)
    natal = app.birth_chart(d, t, city)
    paras, qs = app.make_summary(lang, name, natal, focus, status, token)
    price, aff = app._lead_offer(lang, src)
    optout = f"{emails.SITE}/api/unsub/{token}"
    subject, html = emails.summary2(lang, name, natal, paras, qs, price, app._resume_url(lang, token, aff, "catchup"),
                                    catchup=True, optout_url=optout)
    return subject, html, optout, {"paragraphs": paras, "questions": qs}


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "count"
    if cmd == "count":
        rs = rows()
        per: dict[str, int] = {}
        for r in rs:
            per[r[2]] = per.get(r[2], 0) + 1
        print(f"{len(rs)} leads:", ", ".join(f"{k} {v}" for k, v in sorted(per.items())) or "-")
    elif cmd == "preview":
        n = int(next((a for a in sys.argv[2:] if a.isdigit()), "2"))
        lang = next((a for a in sys.argv[2:] if not a.isdigit()), "")
        for i, r in enumerate(rows(lang)[:n]):
            subject, html, _, summ = build(r)
            path = f"/tmp/catchup-{i + 1}.html"
            open(path, "w").write(html)
            print(f"\n===== {r[2]} · {subject}  ({path})")
            for p in summ["paragraphs"]:
                print("\n" + p)
            for q in summ["questions"]:
                print("  ✦ " + q)
    elif cmd == "send":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10**6
        sent = 0
        for r in rows()[:limit]:
            token, email = r[0], r[1]
            now = datetime.now(timezone.utc).isoformat()
            with app.db() as con:  # mark first: a crash must never send twice
                con.execute("update leads set reminded=? where lower(email)=?", (now, email))
            subject, html, optout, summ = build(r)
            if not summ["paragraphs"]:
                print("skip (no text)", email, flush=True)
                continue
            with app.db() as con:
                con.execute("update leads set summary=? where token=?", (json.dumps(summ, ensure_ascii=False), token))
            mailer.send(app.DB_PATH, email, "catchup", subject, html, unsubscribe_url=optout)
            sent += 1
            print("sent", r[2], email[:2] + "***@" + email.split("@")[-1], flush=True)
            time.sleep(1)
        print("done:", sent, "sent")
