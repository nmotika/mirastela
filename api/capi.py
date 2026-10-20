"""Meta Conversions API: server-side copies of Lead and Purchase, deduplicated with the browser pixel
by event_id. Sent only for visitors who accepted marketing cookies on the site.

Env: META_PIXEL_ID, META_CAPI_TOKEN (secret, from Events Manager), META_GRAPH_VERSION (default v23.0),
     META_TEST_EVENT_CODE (optional, for the Test events tab).
"""
from __future__ import annotations

import hashlib
import json
import os
import time
import urllib.request


def enabled() -> bool:
    return bool(os.environ.get("META_PIXEL_ID") and os.environ.get("META_CAPI_TOKEN"))


def _h(v: str) -> str:
    return hashlib.sha256(v.strip().lower().encode()).hexdigest()


# Country of the language version (ISO 3166 alpha-2, Meta wants it lowercase and hashed); English has none.
COUNTRY = {"pl": "pl", "hr": "hr", "sl": "si", "ro": "ro", "cs": "cz", "hu": "hu", "de": "de", "fr": "fr", "it": "it"}


def _first_name(name: str) -> str:
    """Meta's fn format: lowercase, first word only, letters only (diacritics kept, as UTF-8)."""
    word = (name or "").strip().split(" ")[0].lower()
    return "".join(ch for ch in word if ch.isalpha())


def send(event: str, event_id: str, url: str, email: str = "", track: dict | None = None,
         value: float | None = None, currency: str | None = None, content: str | None = None,
         name: str = "", lang: str = ""):
    """Fire and forget; errors are printed, never raised (tracking must not break a purchase)."""
    track = track or {}
    if not enabled() or not track.get("consent"):
        return
    user = {"client_ip_address": track.get("ip") or None, "client_user_agent": track.get("ua") or None,
            "fbp": track.get("fbp") or None, "fbc": track.get("fbc") or None}
    if email:
        user["em"] = [_h(email)]
        user["external_id"] = [_h(_h(email))]  # anonymous customer id: same person, same id, on every event
    if _first_name(name):
        user["fn"] = [_h(_first_name(name))]
    if COUNTRY.get(lang):
        user["country"] = [_h(COUNTRY[lang])]
    custom = {}
    if value is not None:
        custom.update(value=round(value, 2), currency=(currency or "EUR").upper())
    if content:
        custom.update(content_name=content, content_type="product")
    payload = {"data": [{"event_name": event, "event_time": int(time.time()), "event_id": event_id,
                         "action_source": "website", "event_source_url": url,
                         "user_data": {k: v for k, v in user.items() if v}, "custom_data": custom}]}
    if os.environ.get("META_TEST_EVENT_CODE"):
        payload["test_event_code"] = os.environ["META_TEST_EVENT_CODE"]
    ver = os.environ.get("META_GRAPH_VERSION", "v23.0")
    req = urllib.request.Request(
        f"https://graph.facebook.com/{ver}/{os.environ['META_PIXEL_ID']}/events?access_token={os.environ['META_CAPI_TOKEN']}",
        data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            r.read()
    except Exception as e:  # noqa: BLE001
        print("capi", event, "error", e)
