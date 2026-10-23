#!/usr/bin/env python3
"""Chip Gazer news monitor: ONE poll cycle per run, then exit. Zero AI, stdlib only.

Designed for GitHub Actions cron. Fetches RSS/Atom + SEC submissions JSON, scores
headlines with keyword rules, clusters near-duplicate stories, dedupes against
state.json and POSTs new passing items as one JSON batch to CHIP_WEBHOOK_URL.

Env:
  CHIP_WEBHOOK_URL / CHIP_WEBHOOK_KEY  webhook target + key (either missing -> dry run)
  SEC_USER_AGENT     "ChipGazer you@example.com" (SEC feeds skipped if missing)
  CHIP_DRY_RUN=1     force dry run;  CHIP_SEED=1 force seeding (mark seen, send nothing)
  CHIP_GN_WHEN       Google News window, default from config (e.g. 1d); CHIP_TEST_REPORT=path -> filter test mode
"""
import email.utils, gzip, hashlib, html, json, os, re, sys, time, urllib.parse, urllib.request, urllib.error
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone

try:
    from zoneinfo import ZoneInfo
except ImportError:  # pragma: no cover
    ZoneInfo = None

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG, STATE = os.path.join(HERE, "config.json"), os.path.join(HERE, "state.json")
MATCHES_LOG = os.path.join(HERE, "matches.log")
DEFAULT_UA = "Mozilla/5.0 (compatible; ChipGazerMonitor/1.0)"
MAX_SEEN = 8000
UTC = timezone.utc


def log(*a):
    print(datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"), *a, flush=True)


def iso(d):
    return d.strftime("%Y-%m-%dT%H:%M:%SZ") if d else None


# ---------------------------------------------------------------- HTTP (conditional GET)
def fetch(url, ua, timeout, cache):
    """Returns bytes, or None on 304 Not Modified. cache: dict url -> {etag, lm}."""
    hdr = {"User-Agent": ua, "Accept-Encoding": "gzip"}
    c = cache.get(url) or {}
    if c.get("etag"):
        hdr["If-None-Match"] = c["etag"]
    if c.get("lm"):
        hdr["If-Modified-Since"] = c["lm"]
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=hdr), timeout=timeout) as r:
            data = r.read()
            if r.headers.get("Content-Encoding") == "gzip":
                data = gzip.decompress(data)
            et, lm = r.headers.get("ETag"), r.headers.get("Last-Modified")
            if et or lm:
                cache[url] = {"etag": et, "lm": lm}
            else:
                cache.pop(url, None)
            return data
    except urllib.error.HTTPError as e:
        if e.code == 304:
            return None
        raise


# ---------------------------------------------------------------- parsing
def strip_ns(tag):
    return tag.split("}", 1)[-1]


def child_text(el, name):
    for c in el:
        if strip_ns(c.tag) == name:
            return (c.text or "").strip()
    return ""


def parse_date(s, tz=None):
    """tz: optional "+09:00" style offset applied to naive dates (feeds that omit their zone)."""
    if not s:
        return None
    s = re.sub(r"([+-]\d\d):(\d\d)$", r"\1\2", s.strip()) if re.match(r"[A-Z][a-z]{2}, ", s.strip()) else s.strip()
    d = None
    try:
        d = email.utils.parsedate_to_datetime(s)
    except Exception:
        try:
            d = datetime.fromisoformat(s.replace("Z", "+00:00"))
        except Exception:
            return None
    if d.tzinfo is None:
        d = d.replace(tzinfo=datetime.strptime(tz, "%z").tzinfo if tz else UTC)
    return d.astimezone(UTC)


def clean(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s or ""))).strip()


def xml_root(data):
    try:
        return ET.fromstring(data)
    except ET.ParseError:  # some feeds (e.g. DigiTimes) ship broken UTF-8 bytes / control chars
        txt = data.decode("utf-8", errors="replace") if isinstance(data, bytes) else data
        txt = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", txt.replace("\ufffd", ""))
        txt = re.sub(r"^\s*<\?xml[^>]*\?>", "", txt)
        return ET.fromstring(txt)


def parse_feed(data, tz=None):
    items = []
    for el in xml_root(data).iter():
        if strip_ns(el.tag) not in ("item", "entry"):
            continue
        link, publisher = "", ""
        for c in el:
            n = strip_ns(c.tag)
            if n == "link":
                link = (c.get("href") or c.text or "").strip() or link
            elif n == "source":
                publisher = clean(c.text)
        pub = child_text(el, "pubDate") or child_text(el, "updated") or child_text(el, "published") or child_text(el, "date")
        items.append({"title": clean(child_text(el, "title")), "link": link,
                      "guid": child_text(el, "guid") or child_text(el, "id") or link,
                      "published_dt": parse_date(pub, tz), "publisher": publisher})
    return items


def parse_sec(data, tk, cik, sec_cfg):
    j = json.loads(data)
    r = j["filings"]["recent"]
    always = {f.upper() for f in sec_cfg.get("always_forms", [])}
    items8k = set(sec_cfg.get("form_8k_items", []))
    out = []
    for i in range(min(len(r["form"]), 60)):
        form, acc = r["form"][i].upper(), r["accessionNumber"][i]
        its = [x for x in (r["items"][i] or "").split(",") if x]
        if form in ("8-K", "8-K/A"):
            ok = bool(set(its) & items8k)
            why = "8-K items %s" % (",".join(its) or "-")
        else:
            ok, why = form in always, form
        desc = r["primaryDocDescription"][i] or form
        link = "https://www.sec.gov/Archives/edgar/data/%s/%s/%s" % (int(cik), acc.replace("-", ""), r["primaryDocument"][i])
        title = "$%s SEC %s%s: %s" % (tk, form, (" (items " + ",".join(its) + ")") if its else "", desc)
        out.append({"title": title, "link": link, "guid": "sec:" + acc, "publisher": "SEC EDGAR",
                    "published_dt": parse_date(r["acceptanceDateTime"][i]), "_sec_ok": ok, "_tk": tk, "_sec_why": why})
    return out


# ---------------------------------------------------------------- text utils
def norm_title(t):
    t = re.sub(r"\s+[-|–—]\s+[^-|–—]{2,60}$", "", t)  # drop " - Publisher"
    t = re.sub(r"[^a-z0-9$ ]+", " ", t.lower())
    return re.sub(r"\s+", " ", t).strip()


STOP = set("the a an to of in on for and as with at by is its it from after new says said say will be are was has have than over into amid about more up down this that their his her report reports".split())


def tokens(t):
    out = set()
    for w in norm_title(t).split():
        if w in STOP or len(w) < 2:
            continue
        out.add(w[:-1] if w.endswith("s") and len(w) > 3 else w)  # crude plural stemming
    return out


def similar(a, b, cl):
    if not a or not b:
        return False
    inter = len(a & b)
    if inter / len(a | b) >= cl.get("jaccard", 0.5):
        return True
    return inter >= cl.get("overlap_min_shared", 4) and inter / min(len(a), len(b)) >= cl.get("overlap", 0.75)


def h(s):
    return hashlib.sha1(s.encode("utf-8")).hexdigest()[:16]


# ---------------------------------------------------------------- scoring
SEC_CANON = {"NVDA": "nvidia", "TSM": "tsmc", "AVGO": "broadcom", "AMD": "amd", "MU": "micron", "ASML": "asml",
             "AMKR": "amkor", "INTC": "intel", "ARM": "arm holdings", "SMCI": "super micro"}


class Scorer:
    def __init__(self, cfg):
        f = cfg["filters"]
        c = lambda xs: [re.compile(x, re.I) for x in xs]
        self.core, self.events, self.strong, self.exclude = c(f["core_entities"]), c(f["material_events"]), c(f["strong_terms"]), c(f["exclude"])
        self.whitelist = {p.lower() for p in f["publisher_whitelist"]}
        self.ex_pub = {p.lower() for p in f.get("exclude_publishers", [])}
        self.threshold = cfg.get("score_threshold", 4)
        self.canon = {k.lower(): v for k, v in f.get("canonical", {}).items()}

    def canonical(self, m):
        m = re.sub(r"\s+", " ", (m or "").lower()).strip()
        return self.canon.get(m, m.split(" (")[0])

    @staticmethod
    def first(rx, s):
        for r in rx:
            m = r.search(s)
            if m:
                return m.group(0)
        return None

    def evaluate(self, it, tier):
        """Returns (passed: bool, score: int, reason: str)."""
        if tier == "sec":
            it["_ent"] = SEC_CANON.get(it["_tk"], it["_tk"].lower())
            return (it["_sec_ok"], 10 if it["_sec_ok"] else 0, "sec ok: " + it["_sec_why"] if it["_sec_ok"] else "routine filing: " + it["_sec_why"])
        title = re.sub(r"\s+-\s+[^-]{2,60}$", "", it["title"]) if tier == "gnews" else it["title"]
        if tier == "bis":
            ok = re.search(r"semiconductor|advanced computing|integrated circuit|entity list|supercomputer|artificial intelligence|\bAI\b|foundry|chip", title, re.I)
            return (bool(ok), 5 if ok else 0, "bis ok" if ok else "bis: not chip-related")
        pub = (it.get("publisher") or "").strip().lower()
        if tier == "gnews":
            if pub in self.ex_pub or pub not in self.whitelist:
                return False, 0, "untrusted source: %s" % (it.get("publisher") or "?")
        x = self.first(self.exclude, title)
        if x:
            return False, 0, "clickbait/noise pattern: '%s'" % x
        ent, ev, st = self.first(self.core, title), self.first(self.events, title), self.first(self.strong, title)
        it["_ent"] = self.canonical(ent) if ent else None
        score = (3 if tier == "primary" else 2) + (1 if ent else 0) + (1 if ev else 0) + (2 if st else 0)
        if tier == "primary" and re.search(r"nvidia", title, re.I) is None and it.get("_src", "").startswith("NVIDIA"):
            ent = ent or "nvidia(feed)"
            score += 1
        if not (ent or st):
            return False, score, "no core company/ticker"
        if not (ev or st):
            return False, score, "no material event"
        if score < self.threshold:
            return False, score, "score %d < %d" % (score, self.threshold)
        return True, score, "entity=%s event=%s strong=%s" % (ent, ev, st)


# ---------------------------------------------------------------- collection
def gnews_url(q, when):
    return "https://news.google.com/rss/search?" + urllib.parse.urlencode(
        {"q": "%s when:%s" % (q, when), "hl": "en-US", "gl": "US", "ceid": "US:en"})


def collect(cfg, state, test_mode=False):
    timeout = cfg.get("http_timeout_sec", 10)
    cache = state.setdefault("http_cache", {})
    if test_mode:
        cache = {}
    when = os.environ.get("CHIP_GN_WHEN") or cfg.get("gnews_when", "1d")
    jobs = []
    for fd in cfg["feeds"]:
        url = gnews_url(fd["url"][6:], when) if fd["url"].startswith("gnews:") else fd["url"]
        jobs.append(fd | {"_url": url})

    def run(fd):
        t0 = time.time()
        try:
            data = fetch(fd["_url"], DEFAULT_UA, timeout, cache)
            return fd, (None if data is None else parse_feed(data, fd.get("tz"))), None, time.time() - t0
        except Exception as e:
            return fd, [], str(e)[:80], time.time() - t0

    def run_sec():  # sequential, ~4 req/s max (SEC limit is 10 req/s)
        res = []
        sec = cfg.get("sec", {})
        ua = os.environ.get("SEC_USER_AGENT", "").strip()
        if not ua:
            return [({"name": "SEC EDGAR", "tier": "sec"}, [], "skipped (SEC_USER_AGENT not set)", 0.0)]
        every = sec.get("poll_every_minutes", 10)
        last = parse_date(state.get("last_sec_poll"))
        if not test_mode and last and datetime.now(UTC) - last < timedelta(minutes=every) - timedelta(seconds=30):
            return [({"name": "SEC EDGAR", "tier": "sec"}, None, None, 0.0)]
        for tk, cik in sec.get("companies", {}).items():
            fd = {"name": "SEC " + tk, "tier": "sec"}
            url = "https://data.sec.gov/submissions/CIK%010d.json" % int(cik)
            t0 = time.time()
            try:
                data = fetch(url, ua, timeout, cache)
                res.append((fd, None if data is None else parse_sec(data, tk, cik, sec), None, time.time() - t0))
            except Exception as e:
                res.append((fd, [], str(e)[:80], time.time() - t0))
            time.sleep(0.25)
        state["last_sec_poll"] = iso(datetime.now(UTC))
        return res

    with ThreadPoolExecutor(max_workers=8) as ex:
        sec_future = ex.submit(run_sec)
        results = list(ex.map(run, jobs)) + sec_future.result()

    items, stats = [], []
    for fd, its, err, dt in results:
        if its is None:
            stats.append((fd["name"], "304/not polled", 0, dt))
            continue
        stats.append((fd["name"], "ERR " + err if err else "ok", len(its), dt))
        for it in its:
            it["_src"], it["_tier"] = fd["name"], fd["tier"]
            if fd.get("publisher") and not it.get("publisher"):
                it["publisher"] = fd["publisher"]
            items.append(it)
    return stats, items


# ---------------------------------------------------------------- state
def load_state():
    try:
        with open(STATE) as f:
            s = json.load(f)
    except Exception:
        s = {}
    s.setdefault("seen", {})
    s.setdefault("clusters", [])  # [{"t": iso, "tok": "a b c"}]
    return s


def save_state(s):
    s["seen"] = dict(sorted(s["seen"].items(), key=lambda kv: kv[1], reverse=True)[:MAX_SEEN])
    with open(STATE + ".tmp", "w") as f:
        json.dump(s, f, separators=(",", ":"), sort_keys=True)
    os.replace(STATE + ".tmp", STATE)


def flag_important():
    """Tell the GitHub workflow that state must be committed (something was sent or seeded)."""
    out = os.environ.get("GITHUB_OUTPUT")
    if out:
        with open(out, "a") as f:
            f.write("important=1\n")


def item_keys(it):
    keys = ["t:" + h(norm_title(it["title"]))]
    for k in ("link", "guid"):
        if it.get(k):
            keys.append(k[0] + ":" + h(it[k]))
    return keys


def in_quiet_hours(q):
    if not q or not q.get("enabled") or ZoneInfo is None:
        return False
    now = datetime.now(ZoneInfo(q.get("timezone", "America/New_York")))
    cur = now.weekday() * 1440 + now.hour * 60 + now.minute
    for w in q.get("windows", []):
        a = w["from_weekday"] * 1440 + int(w["from_time"][:2]) * 60 + int(w["from_time"][3:])
        b = w["to_weekday"] * 1440 + int(w["to_time"][:2]) * 60 + int(w["to_time"][3:])
        if (a <= cur < b) if a <= b else (cur >= a or cur < b):
            return True
    return False


def post(url, key, payload, cfg):
    headers = {"Content-Type": "application/json", "User-Agent": "ChipGazerMonitor/1.0"}
    for name, tmpl in cfg.get("auth_headers", {}).items():
        headers[name] = tmpl.replace("{key}", key)
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.status


# ---------------------------------------------------------------- pipeline
def entity_class(it, cl):
    if not it.get("_ent"):
        return None
    for name, rx in cl.get("entity_classes", {}).items():
        if re.search(rx, it["title"], re.I):
            return it["_ent"] + "|" + name
    return None


def classify(cfg, items, cluster_memory, max_age_h, now):
    """Annotates items with _pass/_score/_reason; applies age + cluster dedupe. Returns passed list.
    cluster_memory: [{"t": iso, "tok": "...", "ek": "entity|class" or None}] from previous runs."""
    sc = Scorer(cfg)
    cl = cfg.get("cluster", {})
    ek_win = timedelta(hours=cl.get("entity_class_window_hours", 12))
    memory = [set(c["tok"].split()) for c in cluster_memory if c.get("tok")]
    ek_mem = {}  # "entity|class" -> [datetimes]
    for c in cluster_memory:
        if c.get("ek"):
            ek_mem.setdefault(c["ek"], []).append(parse_date(c["t"]) or now)
    passed, seen_norm = [], set()
    order = sorted(items, key=lambda it: ({"sec": 0, "bis": 0, "primary": 1, "top": 2}.get(it["_tier"], 3),
                                          it["published_dt"] or now))  # primary sources & earliest first win clusters
    for it in order:
        ok, score, reason = sc.evaluate(it, it["_tier"])
        it["_score"] = score
        if ok and it["published_dt"] and now - it["published_dt"] > timedelta(hours=max_age_h):
            ok, reason = False, "older than %dh" % max_age_h
        if ok:
            n = norm_title(it["title"])
            tk = tokens(it["title"]) if it["_tier"] != "sec" else set()
            ek = entity_class(it, cl)
            if n in seen_norm:
                ok, reason = False, "duplicate (same headline)"
            elif tk and any(similar(tk, m, cl) for m in memory):
                ok, reason = False, "duplicate cluster (similar headline)"
            elif ek and any(abs((it["published_dt"] or now) - t) < ek_win for t in ek_mem.get(ek, [])):
                ok, reason = False, "duplicate cluster (same company+topic: %s)" % ek
            else:
                seen_norm.add(n)
                if tk:
                    memory.append(tk)
                if ek:
                    ek_mem.setdefault(ek, []).append(it["published_dt"] or now)
                it["_tok"], it["_ek"] = " ".join(sorted(tk)), ek
        it["_pass"], it["_reason"] = ok, reason
        if ok:
            passed.append(it)
    return passed


def payload_of(batch):
    return {"items": [{"title": it["title"], "link": it["link"],
                       "source": it["_src"] + ((" / " + it["publisher"]) if it.get("publisher") and it["publisher"] not in it["_src"] else ""),
                       "published": iso(it["published_dt"]), "score": it["_score"]} for it in batch],
            "count": len(batch)}


def main():
    with open(CONFIG) as f:
        cfg = json.load(f)
    t_start = time.time()
    url, key = os.environ.get("CHIP_WEBHOOK_URL", "").strip(), os.environ.get("CHIP_WEBHOOK_KEY", "").strip()
    dry = os.environ.get("CHIP_DRY_RUN") == "1" or not url or not key
    if os.environ.get("CHIP_TEST_PING") == "1":  # manual connectivity test: one tiny payload, no state changes
        if not url or not key:
            log("TEST PING: CHIP_WEBHOOK_URL/KEY secrets are missing")
            return 1
        try:
            log("TEST PING POST ok status=%s" % post(url, key, {"test": True, "count": 0, "items": [],
                "note": "Connectivity test from chip-gazer-monitor. Not news."}, cfg))
            return 0
        except Exception as e:
            log("TEST PING POST failed: %s" % str(e)[:300])
            return 1
    state = load_state()
    seeding = os.environ.get("CHIP_SEED") == "1" or not state.get("seeded")
    now = datetime.now(UTC)
    win = timedelta(hours=cfg.get("cluster", {}).get("window_hours", 24))
    state["clusters"] = [c for c in state["clusters"] if (parse_date(c["t"]) or now) > now - win]

    stats, items = collect(cfg, state)
    for name, st, n, dt in stats:
        log("feed %-24s %-16s items=%-3d %.1fs" % (name, st, n, dt))

    seen = state["seen"]
    fresh = [it for it in items if not any(k in seen for k in item_keys(it))]
    passed = classify(cfg, fresh, state["clusters"], cfg.get("max_age_hours", 36), now)
    stamp = iso(now)

    def mark(it):
        for k in item_keys(it):
            seen[k] = stamp

    for it in fresh:  # rejected items are remembered so they are never re-evaluated
        if not it["_pass"]:
            mark(it)

    if seeding:
        for it in passed:
            mark(it)
            state["clusters"].append({"t": stamp, "tok": it["_tok"], "ek": it["_ek"]})
        state["seeded"] = stamp
        save_state(state)
        flag_important()
        log("SEED run: fetched %d, %d would pass; all marked seen, nothing sent (%.1fs)" % (len(items), len(passed), time.time() - t_start))
        return 0

    cap = cfg.get("max_items_per_payload", 15)
    passed.sort(key=lambda it: -it["_score"])
    batch = passed[:cap]
    log("fetched=%d new=%d passed=%d sending=%d" % (len(items), len(fresh), len(passed), len(batch)))
    if not batch:  # only wake the webhook when something passes
        state["last_run"] = stamp
        save_state(state)
        return 0
    if in_quiet_hours(cfg.get("quiet_hours")):
        log("quiet hours: holding %d items" % len(batch))
        save_state(state)
        return 0
    payload = payload_of(batch)
    if dry:
        with open(MATCHES_LOG, "a") as f:
            f.write(json.dumps({"ts": stamp, **payload}, ensure_ascii=False) + "\n")
        log("DRY RUN (CHIP_WEBHOOK_URL/KEY not set): would POST %d items" % len(batch))
    else:
        try:
            log("POST ok status=%s" % post(url, key, payload, cfg))
        except Exception as e:
            log("POST failed: %s (items stay unsent, retried next run)" % str(e)[:200])
            save_state(state)
            return 1
    for it in batch:
        mark(it)
        state["clusters"].append({"t": stamp, "tok": it["_tok"], "ek": it["_ek"]})
        log("  SENT [%s] (%d) %s" % (it["_src"], it["_score"], it["title"][:150]))
    state["last_run"] = stamp
    save_state(state)
    flag_important()
    log("done in %.1fs" % (time.time() - t_start))
    return 0


if __name__ == "__main__":
    sys.exit(main())
