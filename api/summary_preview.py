"""Preview the free summary for the latest leads, without sending or saving anything.
Run on the server: /opt/mirastela/deploy/summary-preview.sh [N] [LANG]
"""
from __future__ import annotations

import sys

import app
import report

n = int(next((a for a in sys.argv[1:] if a.isdigit()), "3"))
lang = next((a for a in sys.argv[1:] if not a.isdigit()), "")
q = "select name, lang, birth_date, birth_time, city_id, focus, status from leads where birth_date != '' and city_id is not null"
args: list = []
if lang:
    q += " and lang=?"; args.append(lang)
q += " order by created desc limit ?"; args.append(n)
with app.db() as con:
    rows = con.execute(q, args).fetchall()
for name, lg, d, t, city, focus, status in rows:
    lg = app._lang(lg)
    natal = app.birth_chart(d, t, city)
    out, model = report.generate_json(report.prompt_summary(lg, name, natal, [f for f in (focus or "").split(",") if f], status or ""),
                                      report.SUMMARY_SCHEMA, max_tokens=2500)
    out = out or {}
    print(f"\n===== {name or '(bez imena)'} · {lg} · {d} {t or '?'} · fokus: {focus or '-'} · {model}")
    for p in out.get("paragraphs") or []:
        print("\n" + p)
    for q_ in out.get("questions") or []:
        print("  ✦ " + q_)
