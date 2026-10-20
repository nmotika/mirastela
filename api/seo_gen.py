"""Evergreen SEO pages in every language, written by the model from computed facts:
  year    the yearly forecast per sign (12 per language)
  signs   a profile of each sign (12 per language)
  compat  compatibility of every pair of signs (78 per language)

Results are JSON files in web/src/data/seo/<kind>/<lang>.json, which the static site reads at build
time. Requests go through the Batch API (half price); what is missing or fails validation is sent again.

  python seo_gen.py run [kinds...]     submit, wait, collect, retry failed items (up to 3 rounds)
  python seo_gen.py status             what is done per kind and language
  python seo_gen.py redo KIND [LANG]   drop one kind (or one language of it) so it is written again
  python seo_gen.py publish            commit and push the JSON files (deploy key); run does it too with MIRASTELA_PUBLISH=1

Env: ANTHROPIC_API_KEY, MIRASTELA_SEO_DIR (default ../web/src/data/seo next to this file).
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import report
import yearsky
from chart import SIGNS

YEAR = int(os.environ.get("MIRASTELA_SEO_YEAR", "2027"))
OUT = Path(os.environ.get("MIRASTELA_SEO_DIR", Path(__file__).resolve().parent.parent / "web/src/data/seo"))
KINDS = ("year", "signs", "compat")

ELEMENT = ["fire", "earth", "air", "water"] * 3
MODALITY = ["cardinal", "fixed", "mutable"] * 4
RULER = ["Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury", "Venus", "Mars (traditional) and Pluto (modern)",
         "Jupiter", "Saturn", "Saturn (traditional) and Uranus (modern)", "Jupiter (traditional) and Neptune (modern)"]
RELATION = {0: "the same sign", 1: "neighbouring signs (semi-sextile)", 2: "sextile (compatible elements, easy flow)",
            3: "square (same modality, friction and drive)", 4: "trine (same element, natural harmony)",
            5: "quincunx (nothing in common, constant adjustment)", 6: "opposite signs (attraction and polarity)"}


def sign_facts(i: int) -> str:
    return (f"{SIGNS[i]}: element {ELEMENT[i]}, modality {MODALITY[i]}, ruler {RULER[i]}, "
            f"{'masculine/yang' if i % 2 == 0 else 'feminine/yin'}, opposite sign {SIGNS[(i + 6) % 12]}, natural house {i + 1}")


def pairs() -> list[tuple[int, int]]:
    return [(a, b) for a in range(12) for b in range(a, 12)]


def _s(props: list[str], extra: dict | None = None) -> dict:
    p = {k: {"type": "string"} for k in props}
    p.update(extra or {})
    return {"type": "object", "required": list(p), "properties": p}


# The FAQ as flat text fields (q1, a1, ...): models skip nested arrays more often than plain strings.
FAQ_KEYS = ["q1", "a1", "q2", "a2", "q3", "a3"]
SCHEMAS = {
    "year": _s(["summary", "overview", "love", "work", "money", "growth", "dates", "advice"] + FAQ_KEYS),
    "signs": _s(["summary", "personality", "strengths", "challenges", "love", "work", "friendship", "advice"] + FAQ_KEYS),
    "compat": _s(["summary", "overall", "love", "sex", "friendship", "work", "challenges", "advice"] + FAQ_KEYS),
}
TEXT_KEYS = {k: [x for x in v["required"] if x not in FAQ_KEYS] for k, v in SCHEMAS.items()}
# Minimum length (characters) of the longest fields, so a lazy or cut-off answer is retried.
MIN_LEN = {"year": ("overview", 600), "signs": ("personality", 600), "compat": ("overall", 500)}

COMMON = """Write entirely in {language} with its correct alphabet and all diacritics, addressing the reader informally ({address}).
Use exactly this vocabulary for signs: {signs}.
Plain, warm, specific language for people who know little about astrology; explain any term in passing. No filler, no clichés repeated across sections, vary sentence openings.
Tendencies and possibilities, never certainties. No predictions of illness, death, accidents, pregnancy, lottery wins or breakups. No medical, legal or financial advice.
Do not use em dashes or en dashes as punctuation. Do not use Markdown, headings or lists inside the fields: plain paragraphs only (separate paragraphs with a blank line).
Never mention that you are an AI, and never mention this website's name.
Save the result with the save tool."""


def prompt(kind: str, lang: str, item) -> str:
    v = report.VOCAB[lang]
    head = COMMON.format(language=report.LANG_NAME[lang], address=report.ADDRESS[lang], signs=v["signs"])
    if kind == "year":
        i = item
        return f"""Task: the yearly horoscope {YEAR} for {report.SIGNS_EN[i]}, for a website page that people find through search.
{head}
Fields:
- summary: 2 sentences (max 300 characters) that sum up {YEAR} for this sign; used as the page description.
- overview: 3 paragraphs, about 250 words: the big themes of the year from the slow planets, in order of importance.
- love: about 150 words. work: about 150 words. money: about 100 words (general tendencies only). growth: about 120 words (personal growth and wellbeing in general, no health predictions).
- dates: about 150 words on the key periods of the year with their dates written out in {report.LANG_NAME[lang]} (Mercury retrogrades, eclipses, Jupiter's sign change, Mars periods that matter most for this sign).
- advice: 2 or 3 sentences, the one thing to remember for {YEAR}.
- q1/a1, q2/a2, q3/a3: 3 short questions people search for about {report.SIGNS_EN[i]} in {YEAR} (love, money, best months, luck), each answered in 2 or 3 sentences.
Base everything on these computed facts and the areas of life given for each (never invent other positions or dates):
{yearsky.year_text(_year_facts(), i)}
Sign facts: {sign_facts(i)}
"""
    if kind == "signs":
        i = item
        return f"""Task: a profile of the zodiac sign {report.SIGNS_EN[i]} (Sun sign), for a website page that people find through search.
{head}
Fields:
- summary: 2 sentences (max 300 characters); used as the page description.
- personality: 3 paragraphs, about 280 words: core nature, how element, modality and ruler shape it, how it shows in everyday life.
- strengths: about 120 words. challenges: about 120 words, kind but honest. love: about 160 words (as a partner, what they need, what they give). work: about 140 words (working style, environments where they thrive, not specific job guarantees). friendship: about 100 words.
- advice: 2 or 3 sentences.
- q1/a1, q2/a2, q3/a3: 3 short questions people search for about this sign (dates, best match, character, element), each answered in 2 or 3 sentences. The Sun is in {report.SIGNS_EN[i]} roughly {_dates(i)} (exact dates shift by a day in some years).
Mention once, naturally, that the Sun sign is only one part of the birth chart, and that the Moon sign and Ascendant (which need the birth time and place) complete the picture.
Sign facts: {sign_facts(i)}
"""
    a, b = item
    rel = RELATION[min((b - a) % 12, (a - b) % 12)]
    return f"""Task: compatibility of {report.SIGNS_EN[a]} and {report.SIGNS_EN[b]} (Sun signs), for a website page that people find through search.
{head}
Fields:
- summary: 2 sentences (max 300 characters); used as the page description.
- overall: 3 paragraphs, about 230 words: what draws them together, how their elements and modalities interact, the overall dynamic.
- love: about 150 words. sex: about 80 words, tasteful, about intimacy and closeness, nothing explicit. friendship: about 90 words. work: about 90 words (as colleagues). challenges: about 120 words, honest. advice: 3 sentences for this couple.
- q1/a1, q2/a2, q3/a3: 3 short questions people search for about this pair (are they a good match, in marriage, in bed, who adapts more), each answered in 2 or 3 sentences.
Be balanced: no pair is doomed and none is perfect. Say clearly, once, that real compatibility depends on the whole birth charts of both people (Moon, Venus, Mars, Ascendant), not only the Sun signs.
Facts: {sign_facts(a)}. {sign_facts(b)}. Relationship between the signs: {rel}.
"""


_YF: dict | None = None


def _year_facts() -> dict:
    global _YF
    if _YF is None:
        _YF = yearsky.year_facts(YEAR)
    return _YF


SUN_DATES = ["21.03.-19.04.", "20.04.-20.05.", "21.05.-20.06.", "21.06.-22.07.", "23.07.-22.08.", "23.08.-22.09.",
             "23.09.-22.10.", "23.10.-21.11.", "22.11.-21.12.", "22.12.-19.01.", "20.01.-18.02.", "19.02.-20.03."]


def _dates(i: int) -> str:
    return f"from {SUN_DATES[i].split('-')[0]} to {SUN_DATES[i].split('-')[1]} (day.month.)"


def items(kind: str) -> list:
    return pairs() if kind == "compat" else list(range(12))


def key(kind: str, item) -> str:
    return f"{SIGNS[item[0]]}-{SIGNS[item[1]]}" if kind == "compat" else SIGNS[item]


def path(kind: str, lang: str) -> Path:
    return OUT / kind / f"{lang}.json"


def load(kind: str, lang: str) -> dict:
    p = path(kind, lang)
    return json.loads(p.read_text()) if p.exists() else {}


def save(kind: str, lang: str, data: dict):
    p = path(kind, lang)
    p.parent.mkdir(parents=True, exist_ok=True)
    order = [key(kind, it) for it in items(kind)]
    p.write_text(json.dumps({k: data[k] for k in order if k in data}, ensure_ascii=False, indent=1) + "\n")


def check(kind: str, lang: str, out) -> tuple[dict | None, str | None]:
    if not isinstance(out, dict):
        return None, "no object"
    for k in TEXT_KEYS[kind]:
        if not isinstance(out.get(k), str) or len(out[k].strip()) < 40:
            return None, f"missing {k}"
    faq = [{"q": str(out.get(f"q{n}", "")).strip(), "a": str(out.get(f"a{n}", "")).strip()} for n in (1, 2, 3)]
    faq = [f for f in faq if len(f["q"]) > 5 and len(f["a"]) > 20]
    if len(faq) < 2:
        return None, "faq"
    field, n = MIN_LEN[kind]
    if len(out[field]) < n:
        return None, f"{field} too short"
    text = " ".join(str(out[k]) for k in TEXT_KEYS[kind])
    why = report.daily_problem(lang, {"general": text})
    if why:
        return None, why
    if "—" in text or "–" in text:
        for k in out:
            if isinstance(out[k], str):
                out[k] = out[k].replace(" — ", ", ").replace(" – ", ", ").replace("—", ", ").replace("–", "-")
    clean = {k: out[k].strip() for k in TEXT_KEYS[kind]}
    clean["faq"] = faq
    return clean, None


def missing(kinds) -> list[tuple[str, str, object]]:
    out = []
    for kind in kinds:
        for lang in report.LANG_NAME:
            have = load(kind, lang)
            out += [(kind, lang, it) for it in items(kind) if key(kind, it) not in have]
    return out


def run(kinds):
    client = report.client()
    model = report._model(False)
    for rnd in range(3):
        todo = missing(kinds)
        print(f"round {rnd + 1}: {len(todo)} pages to write", flush=True)
        if not todo:
            break
        reqs, index = [], {}
        for n, (kind, lang, it) in enumerate(todo):
            cid = f"r{n}"
            index[cid] = (kind, lang, it)
            reqs.append({"custom_id": cid, "params": report.json_params(prompt(kind, lang, it), SCHEMAS[kind], model, 6000)})
        batch = client.messages.batches.create(requests=reqs)
        print("batch", batch.id, "submitted", flush=True)
        while True:
            b = client.messages.batches.retrieve(batch.id)
            if b.processing_status == "ended":
                break
            c = b.request_counts
            print(f"  waiting: {c.succeeded} done, {c.processing} processing, {c.errored} errors", flush=True)
            time.sleep(60)
        results: dict[tuple[str, str], dict] = {}
        bad = 0
        for r in client.messages.batches.results(batch.id):
            kind, lang, it = index[r.custom_id]
            clean, why = (None, r.result.type)
            if r.result.type == "errored":
                err = getattr(r.result, "error", None)
                why = f"errored: {getattr(getattr(err, 'error', err), 'message', err)}"
            if r.result.type == "succeeded":
                try:
                    clean, why = check(kind, lang, report.tool_input(r.result.message))
                except Exception as e:
                    why = repr(e)[:200]
            if clean:
                results.setdefault((kind, lang), {})[key(kind, it)] = clean
            else:
                bad += 1
                print("  rejected", kind, lang, key(kind, it), why, flush=True)
        for (kind, lang), new in results.items():
            data = load(kind, lang)
            data.update(new)
            save(kind, lang, data)
        saved = sum(len(v) for v in results.values())
        print(f"round {rnd + 1}: saved {saved}, rejected {bad}", flush=True)
        if not saved:  # every request failed: the same request would fail again, so stop and show why
            print("nothing was saved in this round, stopping (see the reasons above)", flush=True)
            break
    status(kinds)


def publish():
    """Commit the generated pages and push them (Cloudflare then builds the site). Uses a GitHub deploy
    key with write access: MIRASTELA_DEPLOY_KEY (default /etc/mirastela-deploy-key)."""
    import subprocess
    keyfile = os.environ.get("MIRASTELA_DEPLOY_KEY", "/etc/mirastela-deploy-key")
    repo = OUT.parents[3]
    known = os.environ.get("MIRASTELA_KNOWN_HOSTS", "/var/lib/mirastela/known_hosts")
    env = {**os.environ, "GIT_SSH_COMMAND": f"ssh -i {keyfile} -o IdentitiesOnly=yes -o StrictHostKeyChecking=accept-new -o UserKnownHostsFile={known}"}
    git = lambda *a, **k: subprocess.run(["git", "-C", str(repo), *a], env=env, text=True, **k)
    if not OUT.exists() or not any(OUT.glob("*/*.json")):
        print("nothing generated yet, nothing to publish")
        return
    git("add", str(OUT), check=True)
    if git("diff", "--cached", "--quiet").returncode == 0:
        print("nothing new to publish")
        return
    git("-c", "user.name=Mirastela server", "-c", "user.email=hello@mirastela.com", "commit", "-q", "-m", "SEO pages: generated content", check=True)
    remote = os.environ.get("MIRASTELA_GIT_REMOTE", "git@github.com:nmotika/mirastela.git")
    git("pull", "-q", "--rebase", remote, "main", check=True)
    git("push", "-q", remote, "HEAD:main", check=True)
    print("published: Cloudflare is building the site")


def status(kinds=KINDS):
    for kind in kinds:
        row = " ".join(f"{lang}:{len(load(kind, lang))}" for lang in report.LANG_NAME)
        print(f"{kind:7} ({len(items(kind))} per language)  {row}")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    args = sys.argv[2:]
    if cmd == "run":
        kinds = [k for k in args if k in KINDS] or list(KINDS)
        if not report.has_key():
            sys.exit("ANTHROPIC_API_KEY is not set")
        run(kinds)
        if os.environ.get("MIRASTELA_PUBLISH") == "1":
            publish()
    elif cmd == "test":  # one direct request with the same parameters, to see an error message at once
        kind = args[0] if args else "signs"
        it = items(kind)[0]
        out = report.tool_input(report.client().messages.create(**report.json_params(prompt(kind, "pl", it), SCHEMAS[kind], report._model(False), 6000)))
        print(check(kind, "pl", out)[1] or "ok", "| keys:", sorted(out), "| q1:", str(out.get("q1"))[:120])
    elif cmd == "publish":
        publish()
    elif cmd == "redo":
        kind, langs = args[0], args[1:] or list(report.LANG_NAME)
        for lang in langs:
            path(kind, lang).unlink(missing_ok=True)
        status([kind])
    else:
        status()
