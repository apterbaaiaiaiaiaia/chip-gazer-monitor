#!/usr/bin/env python3
"""Offline filter test on live feed data (no state, nothing sent).
Usage: CHIP_GN_WHEN=3d SEC_USER_AGENT="ChipGazer you@example.com" python filter_test.py [hours] [label] > out.md
Also dumps the raw fetched items to /tmp/chip_items.json for re-scoring with CHIP_REUSE=1."""
import json, os, pickle, sys, collections
from datetime import datetime, timedelta, timezone
import monitor as M

hours = int(sys.argv[1]) if len(sys.argv) > 1 else 72
label = sys.argv[2] if len(sys.argv) > 2 else "run"
cfg = json.load(open(M.CONFIG))
now = datetime.now(timezone.utc)
cache_file = "/tmp/chip_items.pkl"
if os.environ.get("CHIP_REUSE") == "1" and os.path.exists(cache_file):
    stats, items = pickle.load(open(cache_file, "rb"))
else:
    stats, items = M.collect(cfg, {}, test_mode=True)
    pickle.dump((stats, items), open(cache_file, "wb"))
items = [it for it in items if not it["published_dt"] or now - it["published_dt"] <= timedelta(hours=hours)]
for it in items:
    it.pop("_pass", None)
passed = M.classify(cfg, items, [], hours, now)
rej = [it for it in items if not it["_pass"]]

def bucket(r):
    for k in ("untrusted source", "clickbait", "no material event", "no core company", "duplicate", "routine filing", "bis:", "score"):
        if r.startswith(k):
            return k
    return r

print("# Filter test (%s) — %s, window %dh\n" % (label, now.strftime("%Y-%m-%d %H:%M UTC"), hours))
print("## Feeds\n\n| feed | status | items in window |\n|---|---|---|")
per = collections.Counter(it["_src"] for it in items)
for name, st, n, dt in stats:
    print("| %s | %s | %d |" % (name, st, per.get(name, 0)))
print("\n## Totals\n\nfetched (in window): **%d**, passed: **%d**, rejected: **%d**\n" % (len(items), len(passed), len(rej)))
c = collections.Counter(bucket(it["_reason"]) for it in rej)
print("Rejections by reason: " + ", ".join("%s=%d" % kv for kv in c.most_common()) + "\n")
print("## Passed items (%d)\n" % len(passed))
for it in sorted(passed, key=lambda x: x["published_dt"] or now, reverse=True):
    print("- [%s] (score %d) **%s** — %s | %s  \n  %s" % (it["published_dt"].strftime("%m-%d %H:%MZ") if it["published_dt"] else "?", it["_score"], it["title"], it["_src"], it.get("publisher") or "", it["link"]))
print("\n## Rejected samples by reason\n")
groups = collections.defaultdict(list)
for it in rej:
    groups[bucket(it["_reason"])].append(it)
for k, lst in groups.items():
    print("### %s (%d)\n" % (k, len(lst)))
    for it in lst[:6]:
        print("- %s — %s | %s → _%s_" % (it["title"][:150], it["_src"], it.get("publisher") or "", it["_reason"]))
    print()
# per-day estimate: distinct passing stories / days
days = hours / 24
print("## Estimate\n\npassed per day ≈ %.1f stories (upper bound on webhook wakes/day at */5 cron)" % (len(passed) / days))
