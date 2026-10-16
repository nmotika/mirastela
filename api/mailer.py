"""Email sending through Resend. Every send is logged in the emails table.

Without RESEND_API_KEY nothing is sent: the email is only logged (status "skipped"),
so the flow can be tested locally and the content checked in the database.
"""
from __future__ import annotations

import json
import os
import sqlite3
import urllib.error
import urllib.request
from datetime import datetime, timezone

API = "https://api.resend.com/emails"


def _log(db_path: str, to: str, kind: str, subject: str, html: str, status: str, info: str = ""):
    con = sqlite3.connect(db_path)
    with con:
        con.execute("""create table if not exists emails(
            id integer primary key, created text, recipient text, kind text, subject text,
            html text, status text, info text)""")
        con.execute("insert into emails(created, recipient, kind, subject, html, status, info) values(?,?,?,?,?,?,?)",
                    (datetime.now(timezone.utc).isoformat(), to, kind, subject, html, status, info[:500]))
    con.close()


def send(db_path: str, to: str, kind: str, subject: str, html: str, text: str = "",
         unsubscribe_url: str | None = None) -> bool:
    key = os.environ.get("RESEND_API_KEY", "")
    if not key:
        _log(db_path, to, kind, subject, html, "skipped", "RESEND_API_KEY not set")
        return False
    payload = {"from": os.environ.get("MAIL_FROM", "Mirastela <hello@mirastela.com>"),
               "to": [to], "subject": subject, "html": html, "tags": [{"name": "kind", "value": kind}]}
    if text:
        payload["text"] = text
    reply_to = os.environ.get("MAIL_REPLY_TO")
    if reply_to:
        payload["reply_to"] = reply_to
    if unsubscribe_url:
        payload["headers"] = {"List-Unsubscribe": f"<{unsubscribe_url}>",
                              "List-Unsubscribe-Post": "List-Unsubscribe=One-Click"}
    req = urllib.request.Request(API, data=json.dumps(payload).encode(), method="POST", headers={
        "Authorization": f"Bearer {key}", "Content-Type": "application/json", "User-Agent": "mirastela/1"})
    try:
        with urllib.request.urlopen(req, timeout=20) as res:
            _log(db_path, to, kind, subject, html, "sent", res.read().decode()[:200])
            return True
    except urllib.error.HTTPError as e:
        _log(db_path, to, kind, subject, html, "error", f"{e.code} {e.read().decode()[:300]}")
    except Exception as e:  # network errors must never break the request that triggered the email
        _log(db_path, to, kind, subject, html, "error", str(e))
    return False
