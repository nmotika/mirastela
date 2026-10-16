"""Tester progress: one row per e-mail address.
Run on the server: /opt/mirastela/deploy/status.sh
"""
from __future__ import annotations

import os
import sqlite3

DB = os.environ.get("MIRASTELA_DB", "/var/lib/mirastela/mirastela.db")
con = sqlite3.connect(DB)
q = lambda sql: con.execute(sql).fetchall()

people: dict[str, dict] = {}
def row(email: str) -> dict:
    return people.setdefault((email or "").strip().lower(), {"lead": "", "natal": "", "partner": "", "forecast": "", "sub": "", "upitnik": ""})

for email, created in q("select email, min(created) from leads group by lower(email)"):
    row(email)["lead"] = created[5:16].replace("T", " ")
for email, product, status in q("select o.email, i.product, i.status from items i join orders o on o.token = i.token"):
    r = row(email)
    if r.get(product) != "gotovo":
        r[product] = {"ready": "gotovo", "pending": "u izradi", "error": "greška"}.get(status, status)
for email, freq, status in q("select email, freq, status from subs"):
    row(email)["sub"] = f"{freq}" if status == "active" else status
for (email,) in q("select distinct email from feedback"):
    row(email)["upitnik"] = "da"

cols = ["email", "lead", "natal", "partner", "forecast", "sub", "upitnik"]
head = ["E-mail", "Lead (UTC)", "Karta", "Partner", "Prognoza", "Pretplata", "Upitnik"]
rows = [[e] + [v[c] for c in cols[1:]] for e, v in sorted(people.items(), key=lambda kv: kv[1]["lead"] or "~")]
w = [max(len(str(x)) for x in col) for col in zip(head, *rows)] if rows else [len(h) for h in head]
line = lambda r: "  ".join(str(x).ljust(n) for x, n in zip(r, w))
print(line(head)); print("  ".join("-" * n for n in w))
for r in rows:
    print(line(r))
n = len(rows)
cnt = lambda k: sum(1 for v in people.values() if v[k])
print(f"\nUkupno: {n} osoba | lead {cnt('lead')} | karta {sum(1 for v in people.values() if v['natal']=='gotovo')} | "
      f"partner {cnt('partner')} | prognoza {cnt('forecast')} | pretplata {cnt('sub')} | upitnik {cnt('upitnik')}")
