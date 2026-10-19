"""Abuse protection for public endpoints: per-key rate limits kept in SQLite (shared by all uvicorn
workers) and Cloudflare Turnstile verification.

Env: TURNSTILE_SECRET (optional; without it the check is skipped, e.g. locally and in tests),
     RATE_LIMITS=0 switches the limits off (tests).
"""
from __future__ import annotations

import json
import os
import sqlite3
import time
import urllib.parse
import urllib.request

from fastapi import HTTPException, Request


def client_ip(request: Request) -> str:
    """Visitor IP. X-Client-IP is set by our Pages proxy (requests without the proxy secret never get here)."""
    return (request.headers.get("x-client-ip")
            or request.headers.get("cf-connecting-ip")
            or request.headers.get("x-forwarded-for", "").split(",")[0].strip()
            or (request.client.host if request.client else ""))


def limit(db_path: str, key: str, n: int, window: int):
    """Allow n hits per window seconds for this key, else 429. Old hits are pruned as we go."""
    if os.environ.get("RATE_LIMITS", "1") == "0" or not key:
        return
    now = time.time()
    con = sqlite3.connect(db_path, timeout=10)
    try:
        with con:
            con.execute("create table if not exists hits(key text, ts real)")
            con.execute("create index if not exists hits_key on hits(key, ts)")
            count = con.execute("select count(*) from hits where key=? and ts>?", (key, now - window)).fetchone()[0]
            if count >= n:
                raise HTTPException(429, "too many requests")
            con.execute("insert into hits(key, ts) values(?,?)", (key, now))
            if int(now) % 50 == 0:  # occasional cleanup; no limit window is longer than a day
                con.execute("delete from hits where ts<?", (now - 86400,))
    finally:
        con.close()


def per_ip(db_path: str, request: Request, bucket: str, n: int, window: int):
    limit(db_path, f"{bucket}:{client_ip(request)}", n, window)


def turnstile(token: str | None, request: Request):
    """Verify a Turnstile token from the browser. Skipped when no secret is configured."""
    secret = os.environ.get("TURNSTILE_SECRET", "")
    if not secret:
        return
    if not token:
        raise HTTPException(403, "captcha required")
    data = urllib.parse.urlencode({"secret": secret, "response": token, "remoteip": client_ip(request)}).encode()
    try:
        with urllib.request.urlopen("https://challenges.cloudflare.com/turnstile/v0/siteverify", data=data, timeout=10) as r:
            ok = json.loads(r.read()).get("success")
    except Exception as e:  # Cloudflare unreachable: do not lock real customers out, the rate limits still apply
        print("turnstile error", e)
        return
    if not ok:
        raise HTTPException(403, "captcha failed")
