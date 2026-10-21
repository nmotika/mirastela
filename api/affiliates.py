"""Partners (affiliates): a partner link https://mirastela.com/<lang>/start/?p=CODE applies the partner's
discount and ties the visitor's e-mail to the partner for 2 years (first partner wins). Every payment from
that e-mail in those 2 years (first order, add-ons, gifts, subscription renewals) is recorded in `sales`.

Env: MIRASTELA_AFFILIATES=MOJZAGREB:20,OTHER:15   (code:percent off; the code also works as a coupon)
Report: python affiliates.py [CODE] [YYYY-MM]
"""
from __future__ import annotations

import os
import sqlite3
from datetime import datetime, timedelta, timezone

YEARS = 2


def parse(raw: str) -> dict[str, int]:
    out = {}
    for part in (raw or "").split(","):
        code, _, pct = part.strip().partition(":")
        code, pct = code.strip().upper(), pct.strip()
        if code and pct.isdigit() and 0 <= int(pct) < 100:  # a partner code is never a free-access code
            out[code] = int(pct)
    return out


AFFILIATES = parse(os.environ.get("MIRASTELA_AFFILIATES", ""))


def valid(code: str | None) -> str:
    c = (code or "").strip().upper()
    return c if c in AFFILIATES else ""


def schema(con: sqlite3.Connection):
    con.execute("create table if not exists aff_customers(email text primary key, aff text, created text, via text)")
    con.execute("""create table if not exists sales(
        id text primary key, created text, email text, aff text, kind text, product text, amount real, currency text)""")


def attribute(con: sqlite3.Connection, email: str, code: str | None, via: str):
    """Tie an e-mail to a partner. The first partner keeps the customer."""
    c, e = valid(code), (email or "").strip().lower()
    if c and e:
        con.execute("insert or ignore into aff_customers(email, aff, created, via) values(?,?,?,?)",
                    (e, c, datetime.now(timezone.utc).isoformat(), via))


def owner(con: sqlite3.Connection, email: str) -> str:
    """The partner this e-mail belongs to, while the 2 years run."""
    row = con.execute("select aff, created from aff_customers where email=?", ((email or "").strip().lower(),)).fetchone()
    if not row:
        return ""
    since = datetime.fromisoformat(row[1])
    return row[0] if datetime.now(timezone.utc) - since <= timedelta(days=365 * YEARS) else ""


def record(con: sqlite3.Connection, sale_id: str, email: str, kind: str, product: str, amount: float, currency: str):
    """Every payment, with the partner (if any) it counts for. Safe to call twice for the same id."""
    con.execute("insert or ignore into sales(id, created, email, aff, kind, product, amount, currency) values(?,?,?,?,?,?,?,?)",
                (sale_id, datetime.now(timezone.utc).isoformat(), (email or "").strip().lower(), owner(con, email),
                 kind, product, round(amount, 2), (currency or "").upper()))


# ---------------------------------------------------------------- report
def report(con: sqlite3.Connection, code: str = "", month: str = "") -> str:
    where, args = "aff != ''", []
    if code:
        where += " and aff = ?"; args.append(code.upper())
    lines = []
    codes = [code.upper()] if code else sorted({r[0] for r in con.execute("select aff from aff_customers")} | set(AFFILIATES))
    for c in codes:
        leads = con.execute("select count(*) from aff_customers where aff=?", (c,)).fetchone()[0]
        buyers = con.execute("select count(distinct email) from sales where aff=?", (c,)).fetchone()[0]
        lines.append(f"\n{c}  (popust {AFFILIATES.get(c, '?')}%)  kontakti: {leads}  kupci: {buyers}")
        q = "select substr(created,1,7) m, currency, count(*), sum(amount) from sales where aff=?"
        a = [c]
        if month:
            q += " and substr(created,1,7)=?"; a.append(month)
        q += " group by m, currency order by m"
        rows = con.execute(q, a).fetchall()
        if not rows:
            lines.append("  još nema prodaja")
        for m, cur, n, total in rows:
            lines.append(f"  {m}  {n:>4} plaćanja  {total:>10.2f} {cur}  (bruto, s PDV-om)")
        if month:
            for created, email, kind, product, amount, cur in con.execute(
                    "select created, email, kind, product, amount, currency from sales where aff=? and substr(created,1,7)=? order by created",
                    (c, month)):
                masked = email[:2] + "***@" + email.split("@")[-1] if "@" in email else email
                lines.append(f"    {created[:16].replace('T', ' ')}  {masked:<28} {kind:<6} {product:<10} {amount:>8.2f} {cur}")
    return "\n".join(lines).lstrip("\n")


if __name__ == "__main__":
    import sys
    db = sqlite3.connect(os.environ.get("MIRASTELA_DB", "/var/lib/mirastela/mirastela.db"))
    schema(db)
    args = [a for a in sys.argv[1:]]
    month = next((a for a in args if len(a) == 7 and a[4] == "-"), "")
    code = next((a for a in args if a != month), "")
    print(report(db, code, month))
