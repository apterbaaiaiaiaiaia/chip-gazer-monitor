# Chip Gazer news monitor

Zero-AI news filter for the **Chip Gazer** X account (AI chip stocks). Runs on **GitHub Actions** every 5 minutes,
one poll cycle per run (~5 s), then exits. Pure Python standard library — no pip install, no AI tokens.
It only wakes the webhook (= the AI agent) when at least one headline passes a strict keyword filter.

## How it works

1. Fetch feeds in parallel (conditional GET with ETag / Last-Modified where the server supports it):
   - NVIDIA Newsroom RSS, NVIDIA Blog RSS
   - Federal Register — Bureau of Industry and Security (export-control rules)
   - CNBC Technology RSS
   - Google News RSS searches (Nvidia, TSMC, AI chips, export controls, HBM/memory, Broadcom/AMD, ASML/equipment,
     Intel/Arm/SMCI, packaging, Reuters chips), 1-day window
   - SEC EDGAR (`data.sec.gov/submissions/CIK….json`) for NVDA TSM AVGO AMD MU ASML AMKR INTC ARM SMCI —
     polled at most every 10 min, sequentially (~4 req/s, SEC limit is 10 req/s), descriptive User-Agent.
   - Reuters' and BIS' own RSS feeds no longer exist; Reuters/Bloomberg/WSJ/FT/Nikkei/DigiTimes/The Information/AP
     are covered through Google News, filtered by the publisher field.
2. Score each headline (`config.json → filters`):
   - Google News items: publisher must be on `publisher_whitelist`, otherwise rejected.
   - Clickbait / noise regexes (`exclude`): stock-to-buy, price targets, "should you buy", "here's why", Motley Fool,
     Zacks, gaming GPU deals, live blogs, market wraps, commentary, rumors…
   - Must contain a **core company/ticker** AND a **material event** term (earnings, guidance, deal, order, export,
     ban, tariff, lawsuit, probe, CEO change, buyback, layoff, plant/fab, capacity, halt, strike…), or a "strong
     term" (export controls, entity list, CoWoS, HBM3E/HBM4, Blackwell, Rubin, H20…).
   - Score = source tier (primary 3, top outlet 2) + entity 1 + event 1 + strong 2; must be ≥ `score_threshold` (4).
   - SEC: 6-K/10-Q/10-K/20-F and 8-Ks with material item codes always pass; S-8, 424B, SC 13G, Form 3/4/5, 144,
     8-K with only 5.07/9.01 etc. are skipped.
3. Dedupe: URL/guid/normalized title seen-set + **story clustering** (token similarity within 24h, or same company +
   same topic — earnings, capacity/fab/suppliers — within 18h), so one story wakes the webhook once.
4. If ≥1 item passes: one POST (max 15 items; overflow carries to the next run). Otherwise nothing is sent.
5. `state.json` is committed back to the repo whenever something was sent/seeded (plus hourly), so restarts never resend.

Expected volume (tested on live data 21 Oct 2026, see `filter_test_report.md`): ~3–10 stories/day,
i.e. at most that many webhook wakes per day (usually fewer, because stories found in the same run are batched).

## Webhook payload

```json
POST $CHIP_WEBHOOK_URL
Authorization: Bearer <CHIP_WEBHOOK_KEY>
X-Webhook-Key: <CHIP_WEBHOOK_KEY>
Content-Type: application/json

{"items": [{"title": "...", "link": "...", "source": "GN: TSMC / Reuters", "published": "2026-10-21T02:40:00Z", "score": 4}],
 "count": 1}
```

Which auth headers are sent is configurable in `config.json → auth_headers` (`{key}` is replaced by the key);
delete the one your webhook doesn't need.

## Setup

1. Push this folder to `https://github.com/apterbaaiaiaiaiaia/chip-gazer-monitor` (branch `main`).
2. Repo → Settings → Secrets and variables → Actions → **New repository secret**:
   - `CHIP_WEBHOOK_URL` — webhook URL
   - `CHIP_WEBHOOK_KEY` — webhook key
   - `SEC_USER_AGENT` — e.g. `ChipGazer yourname@gmail.com` (SEC blocks noreply/undeclared addresses; without this
     secret the SEC feeds are skipped, everything else still works)
3. Repo → Settings → Actions → General → Workflow permissions: **Read and write** (needed to commit `state.json`).
4. Actions tab → enable workflows → run **chip-news-monitor** manually once (optionally with `seed = true`).
   `state.json` is already seeded; items older than 36h are never sent.

Dry run: if `CHIP_WEBHOOK_URL` or `CHIP_WEBHOOK_KEY` is missing, nothing is posted; would-be payloads are printed in the
Actions log (and appended to `matches.log` locally). Go live simply by adding both secrets — no code change.

Notes: GitHub may delay or skip scheduled runs under load (5-min cron often fires every 5–15 min). GitHub disables
scheduled workflows after 60 days without repository activity; the bot's state commits keep the repo active.
The concurrency group guarantees runs never overlap.

## Local use

```bash
python3 monitor.py                       # one cycle (dry run without webhook env vars)
CHIP_SEED=1 python3 monitor.py           # re-seed: mark everything current as seen, send nothing
CHIP_GN_WHEN=3d SEC_USER_AGENT="ChipGazer you@example.com" python3 filter_test.py 72 label > report.md   # filter test
```

Tuning: edit `config.json` (whitelist, exclude, core_entities, material_events, strong_terms, score_threshold,
cluster windows, quiet_hours — default off).
