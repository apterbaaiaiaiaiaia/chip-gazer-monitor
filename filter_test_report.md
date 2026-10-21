# Chip Gazer monitor — filter test report

Generated 2026-10-21 ~23:15 Israel time (20:15 UTC) on live feed data. Nothing was sent anywhere.
Note: 21 Oct is a heavy news day (NVIDIA GTC Berlin keynote + Super Micro earnings), so volumes are on the high side.
Google News returns at most 100 items per query, so busy 72h queries are truncated (24h numbers are the more accurate volume estimate).

## Summary: before vs after tuning

| | before (first strict version) | after tuning |
|---|---|---|
| 72h window: fetched / passed / rejected | 861 / 17 / 844 | 861 / 19 / 842 |
| 24h window (when:1d): passed | — | 9 |
| est. stories (≈ max webhook wakes) per day | ~5.7 | ~6–9 on a heavy day, likely 3–6 on a normal day |

### Sanity check of the "before" run and fixes applied

Noise that passed before → fixed:
- Super Micro earnings came through 4 times (8-K + 3 Reuters/WSJ articles) → added **company+topic clustering** (same company + "earnings" or "capacity/fab/suppliers" topic within 18h = one story).
- Intel Ohio fab: CNBC + Bloomberg wrote the same story with different wording → clustered by company+topic.
- NVIDIA newsroom "supply-chain capacity" press release + The Information "Nvidia expands deals with six component suppliers" → clustered.

Important items that were rejected before (false negatives) → fixed:
- "TSMC says four construction workers killed at Taiwan site, halting work" (Reuters): no event word → added halt/suspend/pause/killed/fire/earthquake/outage/strike.
- "Samsung, SK Hynix upgrading China plants to make more advanced chips" (Reuters exclusive): `plant` didn't match plural → `plants?`.
- "Musk says ASML and others are expediting chipmaking gear for Terafab" (Bloomberg) → added shipments/expedite.
- "Nvidia wins AI startup Modal for new central processors" (Reuters) → added wins/won.
- "Nvidia tells suppliers to tap TSMC process for next-gen memory chips" (The Information) → added suppliers.
- Micron Taiwan union strike (Reuters) → added strike/walkout.
- Google News "chips site:reuters.com" query was returning general Reuters news → narrowed to chip terms.

Remaining borderline items still passing (left in on purpose, low cost): two German-politics stories about Nvidia's Germany investment (CNBC + Reuters, different angle), "Analysis:" piece from DigiTimes on China export controls.
Known gaps (deliberately not covered, to keep wakes low): macro chip stories without a named company (e.g. "South Korea exports surge on record chip sales" passes only via the strong-term rule; "Lutnick announces semiconductor investment in North Carolina" is rejected), and outlets outside the whitelist (Axios, Tom's Hardware, Yahoo Finance, Investing.com, Korean press) are rejected entirely.

---

# Filter test (after tuning, 24h (Google News when:1d)) — 2026-10-21 20:16 UTC, window 24h

## Feeds

| feed | status | items in window |
|---|---|---|
| NVIDIA Newsroom | ok | 17 |
| NVIDIA Blog | ok | 9 |
| Federal Register BIS | ok | 0 |
| CNBC Technology | ok | 13 |
| GN: Nvidia | ok | 100 |
| GN: TSMC | ok | 64 |
| GN: AI chip | ok | 100 |
| GN: chip export rules | ok | 14 |
| GN: HBM / memory | ok | 49 |
| GN: Broadcom / AMD | ok | 100 |
| GN: ASML / equipment | ok | 80 |
| GN: Intel / Arm / SMCI | ok | 100 |
| GN: packaging | ok | 29 |
| GN: Reuters chips | ok | 98 |
| SEC NVDA | ok | 0 |
| SEC TSM | ok | 0 |
| SEC AVGO | ok | 0 |
| SEC AMD | ok | 0 |
| SEC MU | ok | 1 |
| SEC ASML | ok | 0 |
| SEC AMKR | ok | 0 |
| SEC INTC | ok | 0 |
| SEC ARM | ok | 0 |
| SEC SMCI | ok | 2 |

## Totals

fetched (in window): **776**, passed: **9**, rejected: **767**

Rejections by reason: untrusted source=615, no core company=90, no material event=32, clickbait=15, duplicate=13, routine filing=2

## Passed items (9)

- [10-21 16:55Z] (score 4) **Intel hits construction milestone at Ohio chip fab that’s at least 5 years behind schedule** — CNBC Technology | CNBC  
  https://www.cnbc.com/2026/10/21/intel-hits-construction-milestone-at-delayed-ohio-chip-fab-.html
- [10-21 12:43Z] (score 5) **Nvidia announces plug and play Vera Rubin racks that can be shipped on a truck** — CNBC Technology | CNBC  
  https://www.cnbc.com/2026/10/21/nvidia-announces-vera-rubin-racks-that-can-be-shipped-on-a-truck-.html
- [10-21 10:45Z] (score 6) **Google Cloud and NVIDIA Announce General Availability of NVIDIA Vera Rubin Infrastructure** — NVIDIA Newsroom |   
  https://blogs.nvidia.com/blog/google-cloud-vera-rubin-infrastructure/
- [10-21 10:33Z] (score 5) **NVIDIA and Supply Chain Partners Expand Capacity to Accelerate AI Infrastructure Buildout** — NVIDIA Newsroom |   
  https://nvidianews.nvidia.com/news/nvidia-and-supply-chain-partners-expand-capacity-to-accelerate-ai-infrastructure-buildout
- [10-21 07:21Z] (score 4) **Musk Says ASML and Others Are Expediting Chipmaking Gear for Terafab - Bloomberg.com** — GN: ASML / equipment | Bloomberg.com  
  https://news.google.com/rss/articles/CBMiuwFBVV95cUxQQnY5a1ZSd3JrVDdZT0lVamFreWRjNW5MRTRtd1d1bVVNUGNvOGRHdENuSEp5TG5FZGRtd0FoV2xwU09mRHhiQlJ5bzYyQTBDdkkxZlQwVzlUa1dwM1dyWEtMdW1PQW00YUgxejlidTRoQ2plV2NyTnZqNWNHdFFQOGxfOUl2ZkNLQkVUV3VJLVdHUzNxdF9lMk9LeHVZZndCWUVIb1hLVWlQaENVZlRrMXI3MDJ2ZU5RYXJr?oc=5
- [10-21 06:23Z] (score 4) **Micron faces strike from one Taiwan union after deal with another - Reuters** — GN: Reuters chips | Reuters  
  https://news.google.com/rss/articles/CBMiswFBVV95cUxOV193bUJ6bXZZcHp1Q0tId1ZUdU90Um9BR09QOU0wZ0pxNmJtVFhSbVhBMi1hdXY5ajVReHFJSVVseXY2V2Z4N3hEcTEzenJJSVAwRnNCWXVnV1NudWdqalpwenc5eDhBSTVVaUZYZ1kxaTlpcEh4NWRSSkdrMUVZeDhlQTZXU2RFQ3oyZDVwU0tsbFFRRzRIMGpiODVjM0otVUJlVEZRSmV5UGtpYXJBY3B1aw?oc=5
- [10-21 04:49Z] (score 4) **EXCLUSIVE: Samsung, SK Hynix upgrading China plants to make more advanced chips, people say - Reuters** — GN: HBM / memory | Reuters  
  https://news.google.com/rss/articles/CBMiwAFBVV95cUxPNmZxYjhQQjhXcUZzRnh3dHJIMWQzWUxyNDFMLTM1b1R3d3NFMEFycFpkQkx5NW5sQjBNdVJldDNhakRYcUMxRERYRnR3ZWdoVDBZUmljM2VENTdmRzFVdVY4eUMxTDk3VmtCWk1jQ1dvZmY0cnVCQ1FpTl9uZ3lrWWU4MGp0aDRsbG9jNTBvUDBadXpoZVAwOUFYRUlITXVUMUMxakpMVGc3QXJmQjJxeWZoWWJlTHNDSHNmZGprUVY?oc=5
- [10-21 02:40Z] (score 4) **TSMC says four construction workers killed at Taiwan site, halting work - Reuters** — GN: TSMC | Reuters  
  https://news.google.com/rss/articles/CBMivwFBVV95cUxPQXhBdDJleHE3cU1rZmExdmZwX0szZENmbkYwODFUeXJYcnBrMFZSSmRnMFptVUpiSjFYNko2QUttaEVaTlRhVUo5eVpTU1NVNGE2WVFOSWFPQTlaYXVYOXR5UTdYN0FfTlNQSTJYYU5lV2RxOFlXbDUwdWZ0b1RhemNsLW9EOWpFVUh6N1NLeW80Z25JYjBwbDhDanpySzA0MVhfdlR3UldSYXZzbWU3VUIwdWtYY2tocng1Vm5Gaw?oc=5
- [10-21 00:44Z] (score 10) **$SMCI SEC 8-K (items 2.02,9.01): 8-K** — SEC SMCI | SEC EDGAR  
  https://www.sec.gov/Archives/edgar/data/1375365/000137536526000025/smci-20261020.htm

## Rejected samples by reason

### no material event (32)

- Bringing the Spark to Europe: Local Intelligence Powers Next Wave of Agents — NVIDIA Newsroom |  → _no material event_
- NVIDIA Cloud Partners Scale Across Europe — Sovereign, Open and Built for Safe AI Agents — NVIDIA Newsroom |  → _no material event_
- Europe’s Industrial Leaders Reinvent Engineering and Manufacturing With NVIDIA — NVIDIA Newsroom |  → _no material event_
- NVIDIA cuDSS Now Generally Available to Accelerate Engineering and Scientific Simulations — NVIDIA Newsroom |  → _no material event_
- NVIDIA Confidential Computing Expands, Enabling Frontier Model Builders to Securely Scale Across Global Infrastructure — NVIDIA Newsroom |  → _no material event_
- NVIDIA Advances Isaac Platform for General-Purpose Robotics With New Reference Humanoid, Frameworks, Simulation Pipelines and Data — NVIDIA Newsroom |  → _no material event_

### clickbait (15)

- GTC Berlin 2026: Live Updates From NVIDIA CEO Jensen Huang’s Keynote — NVIDIA Newsroom |  → _clickbait/noise pattern: 'Live Updates'_
- GTC Berlin 2026: Live Updates From NVIDIA CEO Jensen Huang’s Keynote — NVIDIA Blog |  → _clickbait/noise pattern: 'Live Updates'_
- Futures orbit around SpaceX as Tesla merger talk cheers investors — CNBC Technology | CNBC → _clickbait/noise pattern: 'Futures'_
- SpaceX stock jumps 10% after earnings beat and Musk hints at Tesla tie-up — CNBC Technology | CNBC → _clickbait/noise pattern: 'stock jumps'_
- COMMENTARY: Five AI quirks and conundrums to watch this earnings season - Reuters — GN: Reuters chips | Reuters → _clickbait/noise pattern: 'COMMENTARY'_
- PODCAST: SpaceX-Tesla merger, Witkoff in Russia and Kansas voters - Reuters — GN: Reuters chips | Reuters → _clickbait/noise pattern: 'PODCAST'_

### duplicate (13)

- Google Cloud and NVIDIA Announce General Availability of NVIDIA Vera Rubin Infrastructure — NVIDIA Blog |  → _duplicate (same headline)_
- Nvidia announces plug and play Vera Rubin racks that can be shipped on a truck - CNBC — GN: Nvidia | CNBC → _duplicate (same headline)_
- Nvidia Expands Deals with Six Chip Component Suppliers - The Information — GN: Nvidia | The Information → _duplicate cluster (same company+topic: nvidia|capacity)_
- TSMC Pauses Some Taiwan Construction After Mishap Kills Four - Bloomberg.com — GN: TSMC | Bloomberg.com → _duplicate cluster (same company+topic: tsmc|capacity)_
- TSMC says four construction workers killed at Taiwan site, halting work - Reuters — GN: AI chip | Reuters → _duplicate (same headline)_
- Samsung, SK Hynix upgrading China plants to make more advanced chips, people say: Reuters - CNBC — GN: chip export rules | CNBC → _duplicate cluster (similar headline)_

### no core company (90)

- Meta ordered to pay $25 billion penalty in New Mexico Cambridge Analytica case — CNBC Technology | CNBC → _no core company/ticker_
- Tesla beats on earnings and sales even as auto revenue declines — CNBC Technology | CNBC → _no core company/ticker_
- Tokenized stock trading takes off overseas as Goldman, other U.S. companies object — CNBC Technology | CNBC → _no core company/ticker_
- Investors are questioning neoclouds' business model but Nebius says AI computing prices are rising — CNBC Technology | CNBC → _no core company/ticker_
- OpenAI to bring AI models to Google's cloud, in further expansion beyond Microsoft — CNBC Technology | CNBC → _no core company/ticker_
- OpenAI's most powerful AI models disabled their own safety monitoring — and one lied about it — CNBC Technology | CNBC → _no core company/ticker_

### untrusted source (615)

- NVIDIA Launches OpenShell Reference Architecture for Safe AI Agents - NVIDIA Newsroom — GN: Nvidia | NVIDIA Newsroom → _untrusted source: NVIDIA Newsroom_
- Nvidia Stock Rises in Wednesday Premarket as Elon Musk Says SpaceX Is Adding 200,000 Chips a Month — Daniel Newman Says NVDA Is 'Ripping' (UPDATED) -  — GN: Nvidia | Yahoo Finance → _untrusted source: Yahoo Finance_
- Scaling Graph ML with NVIDIA Kumo on Snowflake ML - Snowflake — GN: Nvidia | Snowflake → _untrusted source: Snowflake_
- "I am giving you money!" Nvidia's CEO wants every country to build its own AI - Axios — GN: Nvidia | Axios → _untrusted source: Axios_
- European Ecosystem Builds World’s Most Efficient AI Factories With NVIDIA DSX - NVIDIA Newsroom — GN: Nvidia | NVIDIA Newsroom → _untrusted source: NVIDIA Newsroom_
- Nvidia reveals plans for 'an AI factory in a shipping container' to build data centers in weeks, not months - Yahoo Finance — GN: Nvidia | Yahoo Finance → _untrusted source: Yahoo Finance_

### routine filing (2)

- $MU SEC 4: PRIMARY DOCUMENT — SEC MU | SEC EDGAR → _routine filing: 4_
- $SMCI SEC 3/A: FORM 3/A — SEC SMCI | SEC EDGAR → _routine filing: 3/A_

## Estimate

passed per day ≈ 9.0 stories (upper bound on webhook wakes/day at */5 cron)

---

# Filter test (after tuning, 72h) — 2026-10-21 20:16 UTC, window 72h

## Feeds

| feed | status | items in window |
|---|---|---|
| NVIDIA Newsroom | ok | 20 |
| NVIDIA Blog | ok | 13 |
| Federal Register BIS | ok | 0 |
| CNBC Technology | ok | 30 |
| GN: Nvidia | ok | 100 |
| GN: TSMC | ok | 100 |
| GN: AI chip | ok | 100 |
| GN: chip export rules | ok | 25 |
| GN: HBM / memory | ok | 0 |
| GN: Broadcom / AMD | ok | 100 |
| GN: ASML / equipment | ok | 100 |
| GN: Intel / Arm / SMCI | ok | 100 |
| GN: packaging | ok | 68 |
| GN: Reuters chips | ok | 100 |
| SEC NVDA | ok | 0 |
| SEC TSM | ok | 0 |
| SEC AVGO | ok | 0 |
| SEC AMD | ok | 1 |
| SEC MU | ok | 1 |
| SEC ASML | ok | 0 |
| SEC AMKR | ok | 0 |
| SEC INTC | ok | 0 |
| SEC ARM | ok | 0 |
| SEC SMCI | ok | 3 |

## Totals

fetched (in window): **861**, passed: **19**, rejected: **842**

Rejections by reason: untrusted source=671, no core company=97, no material event=37, clickbait=20, duplicate=13, routine filing=4

## Passed items (19)

- [10-21 16:55Z] (score 4) **Intel hits construction milestone at Ohio chip fab that’s at least 5 years behind schedule** — CNBC Technology | CNBC  
  https://www.cnbc.com/2026/10/21/intel-hits-construction-milestone-at-delayed-ohio-chip-fab-.html
- [10-21 12:43Z] (score 5) **Nvidia announces plug and play Vera Rubin racks that can be shipped on a truck** — CNBC Technology | CNBC  
  https://www.cnbc.com/2026/10/21/nvidia-announces-vera-rubin-racks-that-can-be-shipped-on-a-truck-.html
- [10-21 10:45Z] (score 6) **Google Cloud and NVIDIA Announce General Availability of NVIDIA Vera Rubin Infrastructure** — NVIDIA Newsroom |   
  https://blogs.nvidia.com/blog/google-cloud-vera-rubin-infrastructure/
- [10-21 10:33Z] (score 5) **NVIDIA and Supply Chain Partners Expand Capacity to Accelerate AI Infrastructure Buildout** — NVIDIA Newsroom |   
  https://nvidianews.nvidia.com/news/nvidia-and-supply-chain-partners-expand-capacity-to-accelerate-ai-infrastructure-buildout
- [10-21 07:21Z] (score 4) **Musk Says ASML and Others Are Expediting Chipmaking Gear for Terafab - Bloomberg.com** — GN: ASML / equipment | Bloomberg.com  
  https://news.google.com/rss/articles/CBMiuwFBVV95cUxQQnY5a1ZSd3JrVDdZT0lVamFreWRjNW5MRTRtd1d1bVVNUGNvOGRHdENuSEp5TG5FZGRtd0FoV2xwU09mRHhiQlJ5bzYyQTBDdkkxZlQwVzlUa1dwM1dyWEtMdW1PQW00YUgxejlidTRoQ2plV2NyTnZqNWNHdFFQOGxfOUl2ZkNLQkVUV3VJLVdHUzNxdF9lMk9LeHVZZndCWUVIb1hLVWlQaENVZlRrMXI3MDJ2ZU5RYXJr?oc=5
- [10-21 06:23Z] (score 4) **Micron faces strike from one Taiwan union after deal with another - Reuters** — GN: Reuters chips | Reuters  
  https://news.google.com/rss/articles/CBMiswFBVV95cUxOV193bUJ6bXZZcHp1Q0tId1ZUdU90Um9BR09QOU0wZ0pxNmJtVFhSbVhBMi1hdXY5ajVReHFJSVVseXY2V2Z4N3hEcTEzenJJSVAwRnNCWXVnV1NudWdqalpwenc5eDhBSTVVaUZYZ1kxaTlpcEh4NWRSSkdrMUVZeDhlQTZXU2RFQ3oyZDVwU0tsbFFRRzRIMGpiODVjM0otVUJlVEZRSmV5UGtpYXJBY3B1aw?oc=5
- [10-21 04:49Z] (score 4) **EXCLUSIVE: Samsung, SK Hynix upgrading China plants to make more advanced chips, people say - Reuters** — GN: Reuters chips | Reuters  
  https://news.google.com/rss/articles/CBMiwAFBVV95cUxPNmZxYjhQQjhXcUZzRnh3dHJIMWQzWUxyNDFMLTM1b1R3d3NFMEFycFpkQkx5NW5sQjBNdVJldDNhakRYcUMxRERYRnR3ZWdoVDBZUmljM2VENTdmRzFVdVY4eUMxTDk3VmtCWk1jQ1dvZmY0cnVCQ1FpTl9uZ3lrWWU4MGp0aDRsbG9jNTBvUDBadXpoZVAwOUFYRUlITXVUMUMxakpMVGc3QXJmQjJxeWZoWWJlTHNDSHNmZGprUVY?oc=5
- [10-21 02:40Z] (score 4) **TSMC says four construction workers killed at Taiwan site, halting work - Reuters** — GN: TSMC | Reuters  
  https://news.google.com/rss/articles/CBMivwFBVV95cUxPQXhBdDJleHE3cU1rZmExdmZwX0szZENmbkYwODFUeXJYcnBrMFZSSmRnMFptVUpiSjFYNko2QUttaEVaTlRhVUo5eVpTU1NVNGE2WVFOSWFPQTlaYXVYOXR5UTdYN0FfTlNQSTJYYU5lV2RxOFlXbDUwdWZ0b1RhemNsLW9EOWpFVUh6N1NLeW80Z25JYjBwbDhDanpySzA0MVhfdlR3UldSYXZzbWU3VUIwdWtYY2tocng1Vm5Gaw?oc=5
- [10-21 00:44Z] (score 10) **$SMCI SEC 8-K (items 2.02,9.01): 8-K** — SEC SMCI | SEC EDGAR  
  https://www.sec.gov/Archives/edgar/data/1375365/000137536526000025/smci-20261020.htm
- [10-20 16:29Z] (score 4) **EXCLUSIVE: Qualcomm to cut jobs worldwide in performance-focused layoffs, internal memo shows - Reuters** — GN: Reuters chips | Reuters  
  https://news.google.com/rss/articles/CBMivAFBVV95cUxNUndSd0N2Um9RWGtEUDU1MHBGUm1LU3RkT2RpRFVDbVNzRHdNTGVGYnk1MU1pSUFCQklWMnZERzc0bEJ0VDVUWUp5N3JHV3M0eVFMaGRFOEdwcjU0WlUxOG55enFWb09Id3AySlhLenVTT0k4Zk51WUhuQ05oVlBSWmg3d3NmLTFzOVBJTHVsc3RSN21WaGdwYjNCa19RSTRGWUhIXzQ1a25mSDhxQ0JwdzNJRUZiaHdXZTREOQ?oc=5
- [10-20 15:51Z] (score 4) **EXCLUSIVE: ByteDance, Alibaba, Tencent place over $35 billion worth of Nvidia chip orders - Reuters** — GN: chip export rules | Reuters  
  https://news.google.com/rss/articles/CBMizgFBVV95cUxQOXBuUld1bXhxNWlQNktuUmYxOWpVRFlnN0dialpvZlhYM1JLVzE1N0VBSUVNbUlCNmwtN2RVWXRkd1VUV3BRSV9aMGJGMkpxQUk4VWZ1dUt5YjZpdmthQVZ3REFHUzBmV3B0SFJwOFFsMl9fb3l0Y3F0Z1FXbDAxSFhTbV9peVVDQ3FKRnp3NjVDdEpRVHdIOG04SjctLWRRTzN2bDM1a2QxaGdZMHlJV0hGS1FObHFKTVNiS3hvXzZsUzdvMktteFBvSGNEZw?oc=5
- [10-20 15:10Z] (score 4) **Micron union in Taiwan to launch one-day strike as bonus dispute escalates - Reuters** — GN: Reuters chips | Reuters  
  https://news.google.com/rss/articles/CBMitwFBVV95cUxNdW84LTY4WGZuakNjaU5mZ1I5TEd3RXZRYmdBWlFYUkVoTHQyX0xSYkhidnhGTFN6SjBsdGp6eE9aN3M1VE03V09mNWtjYnFYWWRtN0J3NUk2ZVEzVGhxRFFMNEZqRW94Y1h0OHpyX0tOWTMzNDdhcmFJN2dUSUtwN1FtTXpFNFVITG9LT3JNMFdWLVdQRklxZzU0aE9TUmxXUjRNY0NEN0hLMjZFYTRJQXVJQTNZY0k?oc=5
- [10-20 03:25Z] (score 4) **Amkor triples Gwangju investment as AI packaging demand grows - digitimes** — GN: packaging | digitimes  
  https://news.google.com/rss/articles/CBMiogFBVV95cUxQQkNKQlNnOFJ5Qkt5NGlNZjZJLWI3T0NDUXZJZmR2ZlhSOGswQWo0NFlEMGwzWnZNYzBVX2lFbzc4S2tNamtib0lrcVp3RmJuS1NrRW5SQkJ6SEZocUdOMkdMc2ZwMVVjV2QtRGllcDktUDNUOGlWMFdFMmlFWnFFd0hUei01RmlwcmNNOUNVNGwwQzB3OTZJTTBjZWVkUVlaNGc?oc=5
- [10-20 02:16Z] (score 4) **‘Open your doors for AI’: German chancellor urges businesses to embrace AI as Nvidia announces new investments** — CNBC Technology | CNBC  
  https://www.cnbc.com/2026/10/20/german-chancellor-urges-businesses-to-embrace-ai.html
- [10-20 01:51Z] (score 5) **Analysis: China's proposed AI export controls reach beyond chips to design IP, computing infrastructure - digitimes** — GN: chip export rules | digitimes  
  https://news.google.com/rss/articles/CBMijwFBVV95cUxNSV94VmRtNHA2WXNSTWNLRFVJcFF5dHNJZERCdlhaWktBVURTRXRCQVM3S3RPRDBEMm43NzNkcS10d2xwWEx0aUtWbUpiLTFjdEdrZnprNGhLMFRTT2kwNTZfVUMzZWw0SDVDczlJNXZ6SE1PR1VlUFNwU0Rna1E0UFdhRDNSMkQ3T1A3cVN6UQ?oc=5
- [10-19 23:21Z] (score 4) **Nvidia-backed Nscale, Anthropic in talks for new $45 billion AI cloud deal, source says - Reuters** — GN: Reuters chips | Reuters  
  https://news.google.com/rss/articles/CBMiwgFBVV95cUxPcGMyclR5X0JrXzBKem90Uk1sZnBQNkcyRnlyc3ZnWTM4Q0ZoUWtKUzRrd1Y3aHlqaDRjT1pfaFdmV0pHYUFROFI3TFhTWVhtczJsM01PSF8tSEtXejB4emlhVjZGMmQzeWh0RXJoaS0tNDQ1SDhlZDRJZU5hZG5ibE85N3dxU21DS2ZKYm1NV2pVUUF4ZjF3XzQ1ZncwaHVMdXlWZ2FsWjRtQ1d0eFN2YUVQc2x4cTd6YjNwSTVuVUFQZw?oc=5
- [10-19 21:11Z] (score 4) **Germany's Merz urges AI investment ahead of Nvidia deal - Reuters** — GN: Reuters chips | Reuters  
  https://news.google.com/rss/articles/CBMirgFBVV95cUxOT09KR2R3TjktZGltSk9PMGtKcGVMeFBuSmR5eTVkMERSbkVuc0d5bGhnanJ2WloyWUtULU1PTkFVQlNhaklmWmJESHF2cEV0Q01YQ3NBb3RxWklLQlNLelBEMzVBSF9nZ09Uc0FjLUhHUmhOeUF1Z0pObndUclVjT0s2Q3Fka2Z6dWltWC1MQ0g5cmo0V1dUeFY0M3hEOE5aSzV3RjdZZ2JFUTU4TEE?oc=5
- [10-19 14:12Z] (score 4) **Nvidia wins fast-growing AI startup Modal for new central processors - Reuters** — GN: Reuters chips | Reuters  
  https://news.google.com/rss/articles/CBMirgFBVV95cUxNUklvMHh4T2thUkdNSndrQ3BVOTZjalQwRnJ2ZFdhb3Q4aC1NT2k2LTBLX1AxZmlHdTdheHp1ZDF1ZGVSd2JLc3VFUU1ycWRndnRmS2ZyYVpGeU52OU9IQU5qVHdJb1BXNjJ1MlN4MF9aajQ5QXhmQnhYTXowWEFUa29BQkYySzBxeG1CU0Z0MHB6U3psLU1EcTB4Z3N2dkVYSFM3cEgtNlQ4Uk5VTlE?oc=5
- [10-19 04:55Z] (score 4) **Nvidia Tells Suppliers to Tap TSMC Process for Next-Generation Memory Chips - The Information** — GN: TSMC | The Information  
  https://news.google.com/rss/articles/CBMirgFBVV95cUxPcENpWHJUV2Z2SS1SbWYwbWVuaWZsMzc2NVBqMkpBbjViZ1dNaklBY1JMRXVjS2VoNzZ5LUVGZkM1aktLV3ZHb2pxQ3pyTnYzYXpSaERMZzFaN0U0dHBrQkYxUWNKWDZwejBuMEJsTW55R2Z1d0JMejNmdUNnSklBMDBKS0lpN3d4SWg0VHJDZWFhZG5EVVR3dlJyaXNnZDBCR0NIQjJUWTluMnc1U1E?oc=5

## Rejected samples by reason

### no material event (37)

- Bringing the Spark to Europe: Local Intelligence Powers Next Wave of Agents — NVIDIA Newsroom |  → _no material event_
- NVIDIA Cloud Partners Scale Across Europe — Sovereign, Open and Built for Safe AI Agents — NVIDIA Newsroom |  → _no material event_
- Europe’s Industrial Leaders Reinvent Engineering and Manufacturing With NVIDIA — NVIDIA Newsroom |  → _no material event_
- NVIDIA cuDSS Now Generally Available to Accelerate Engineering and Scientific Simulations — NVIDIA Newsroom |  → _no material event_
- NVIDIA Confidential Computing Expands, Enabling Frontier Model Builders to Securely Scale Across Global Infrastructure — NVIDIA Newsroom |  → _no material event_
- NVIDIA Advances Isaac Platform for General-Purpose Robotics With New Reference Humanoid, Frameworks, Simulation Pipelines and Data — NVIDIA Newsroom |  → _no material event_

### clickbait (20)

- GTC Berlin 2026: Live Updates From NVIDIA CEO Jensen Huang’s Keynote — NVIDIA Newsroom |  → _clickbait/noise pattern: 'Live Updates'_
- GTC Berlin 2026: Live Updates From NVIDIA CEO Jensen Huang’s Keynote — NVIDIA Blog |  → _clickbait/noise pattern: 'Live Updates'_
- Futures orbit around SpaceX as Tesla merger talk cheers investors — CNBC Technology | CNBC → _clickbait/noise pattern: 'Futures'_
- SpaceX stock jumps 10% after earnings beat and Musk hints at Tesla tie-up — CNBC Technology | CNBC → _clickbait/noise pattern: 'stock jumps'_
- Apple adds U.S. titanium supplier for iPhone Duo as supply stays tight — CNBC Technology | CNBC → _clickbait/noise pattern: 'iPhone'_
- Jim Cramer says don't chase the AI rebound just yet. Here's what needs to happen first — CNBC Technology | CNBC → _clickbait/noise pattern: 'Here's what'_

### duplicate (13)

- Google Cloud and NVIDIA Announce General Availability of NVIDIA Vera Rubin Infrastructure — NVIDIA Blog |  → _duplicate (same headline)_
- Nvidia announces plug and play Vera Rubin racks that can be shipped on a truck - CNBC — GN: Nvidia | CNBC → _duplicate (same headline)_
- TSMC Pauses Some Taiwan Construction After Mishap Kills Four - Bloomberg.com — GN: TSMC | Bloomberg.com → _duplicate cluster (same company+topic: tsmc|capacity)_
- TSMC says four construction workers killed at Taiwan site, halting work - Reuters — GN: AI chip | Reuters → _duplicate (same headline)_
- Intel hits construction milestone at Ohio chip fab that’s at least 5 years behind schedule - CNBC — GN: Intel / Arm / SMCI | CNBC → _duplicate (same headline)_
- Super Micro climbs after upbeat forecast shows robust AI demand - Reuters — GN: Intel / Arm / SMCI | Reuters → _duplicate cluster (same company+topic: super micro|earnings)_

### no core company (97)

- Meta ordered to pay $25 billion penalty in New Mexico Cambridge Analytica case — CNBC Technology | CNBC → _no core company/ticker_
- Tesla beats on earnings and sales even as auto revenue declines — CNBC Technology | CNBC → _no core company/ticker_
- Tokenized stock trading takes off overseas as Goldman, other U.S. companies object — CNBC Technology | CNBC → _no core company/ticker_
- Investors are questioning neoclouds' business model but Nebius says AI computing prices are rising — CNBC Technology | CNBC → _no core company/ticker_
- OpenAI to bring AI models to Google's cloud, in further expansion beyond Microsoft — CNBC Technology | CNBC → _no core company/ticker_
- OpenAI's most powerful AI models disabled their own safety monitoring — and one lied about it — CNBC Technology | CNBC → _no core company/ticker_

### untrusted source (671)

- NVIDIA Launches OpenShell Reference Architecture for Safe AI Agents - NVIDIA Newsroom — GN: Nvidia | NVIDIA Newsroom → _untrusted source: NVIDIA Newsroom_
- Nvidia Stock Rises in Wednesday Premarket as Elon Musk Says SpaceX Is Adding 200,000 Chips a Month — Daniel Newman Says NVDA Is 'Ripping' (UPDATED) -  — GN: Nvidia | Yahoo Finance → _untrusted source: Yahoo Finance_
- Scaling Graph ML with NVIDIA Kumo on Snowflake ML - Snowflake — GN: Nvidia | Snowflake → _untrusted source: Snowflake_
- European Ecosystem Builds World’s Most Efficient AI Factories With NVIDIA DSX - NVIDIA Newsroom — GN: Nvidia | NVIDIA Newsroom → _untrusted source: NVIDIA Newsroom_
- Nvidia reveals plans for 'an AI factory in a shipping container' to build data centers in weeks, not months - Yahoo Finance — GN: Nvidia | Yahoo Finance → _untrusted source: Yahoo Finance_
- NVIDIA Advances Isaac Platform for General-Purpose Robotics With New Reference Humanoid, Frameworks, Simulation Pipelines and Data - NVIDIA Newsroom — GN: Nvidia | NVIDIA Newsroom → _untrusted source: NVIDIA Newsroom_

### routine filing (4)

- $AMD SEC 4: FORM 4 — SEC AMD | SEC EDGAR → _routine filing: 4_
- $MU SEC 4: PRIMARY DOCUMENT — SEC MU | SEC EDGAR → _routine filing: 4_
- $SMCI SEC 3/A: FORM 3/A — SEC SMCI | SEC EDGAR → _routine filing: 3/A_
- $SMCI SEC 3: FORM 3 — SEC SMCI | SEC EDGAR → _routine filing: 3_

## Estimate

passed per day ≈ 6.3 stories (upper bound on webhook wakes/day at */5 cron)

---

# BEFORE tuning: Filter test (before) — 2026-10-21 20:10 UTC, window 72h

## Feeds

| feed | status | items in window |
|---|---|---|
| NVIDIA Newsroom | ok | 20 |
| NVIDIA Blog | ok | 13 |
| Federal Register BIS | ok | 0 |
| CNBC Technology | ok | 30 |
| GN: Nvidia | ok | 0 |
| GN: TSMC | ok | 100 |
| GN: AI chip | ok | 100 |
| GN: chip export rules | ok | 25 |
| GN: HBM / memory | ok | 100 |
| GN: Broadcom / AMD | ok | 100 |
| GN: ASML / equipment | ok | 100 |
| GN: Intel / Arm / SMCI | ok | 100 |
| GN: packaging | ok | 68 |
| GN: Reuters chips | ok | 100 |
| SEC NVDA | ok | 0 |
| SEC TSM | ok | 0 |
| SEC AVGO | ok | 0 |
| SEC AMD | ok | 1 |
| SEC MU | ok | 1 |
| SEC ASML | ok | 0 |
| SEC AMKR | ok | 0 |
| SEC INTC | ok | 0 |
| SEC ARM | ok | 0 |
| SEC SMCI | ok | 3 |

## Totals

fetched (in window): **861**, passed: **17**, rejected: **844**

Rejections by reason: untrusted source=670, no core company=103, no material event=45, clickbait=18, duplicate=4, routine filing=4

## Passed items (17)

- [10-21 16:55Z] (score 4) **Intel hits construction milestone at Ohio chip fab that’s at least 5 years behind schedule** — CNBC Technology | CNBC  
  https://www.cnbc.com/2026/10/21/intel-hits-construction-milestone-at-delayed-ohio-chip-fab-.html
- [10-21 15:00Z] (score 4) **Intel Touts Factory Expansion Progress in Sign of Growing Demand - Bloomberg.com** — GN: Intel / Arm / SMCI | Bloomberg.com  
  https://news.google.com/rss/articles/CBMitgFBVV95cUxOdU1zVWdGNlJHdkhLblN3NkJrSHVPQ0lTNnN5ZTVQNkpEZ1ZlOWdkak1TVHRBNW1UZ0taWDBiMnU2RGYyTjFnODdLa2hKcGJPSG03TGFEWEN2RTZ2aGs4SG1qUkltM0N0OFRad2FfQk9QNDh3b2tZTWRhUElJaUVKOWxzZzlydWExT21YdUNHS2RSZjZpZXRjNFZYM0lxS0FNd3pnMkZEZk1qbm1lZ3NmT3p1VTVZUQ?oc=5
- [10-21 14:01Z] (score 4) **Super Micro climbs after upbeat forecast shows robust AI demand - Reuters** — GN: Intel / Arm / SMCI | Reuters  
  https://news.google.com/rss/articles/CBMirAFBVV95cUxPUEFHMHlEUHh1eC1kVDZtTVVJdnJNamlzUDBWVUtlbHd4RGFrbEM0MURQbUEtX0toNkIxTy1fNVBIMGdCeHlOcWVTUUJDaGtHWlRtZW9YeGZybFFKaGFTdXpLSm1zMk1MZS1aa0cxSl9jVlpXWnRCNndlcTQyWmliTVEybmc5SDVXRGdpd0VneThCRlV0YXZnbGpvbFo2d05BUF91UC1odHdCVDFM?oc=5
- [10-21 12:43Z] (score 5) **Nvidia announces plug and play Vera Rubin racks that can be shipped on a truck** — CNBC Technology | CNBC  
  https://www.cnbc.com/2026/10/21/nvidia-announces-vera-rubin-racks-that-can-be-shipped-on-a-truck-.html
- [10-21 10:45Z] (score 6) **Google Cloud and NVIDIA Announce General Availability of NVIDIA Vera Rubin Infrastructure** — NVIDIA Newsroom |   
  https://blogs.nvidia.com/blog/google-cloud-vera-rubin-infrastructure/
- [10-21 10:33Z] (score 5) **NVIDIA and Supply Chain Partners Expand Capacity to Accelerate AI Infrastructure Buildout** — NVIDIA Newsroom |   
  https://nvidianews.nvidia.com/news/nvidia-and-supply-chain-partners-expand-capacity-to-accelerate-ai-infrastructure-buildout
- [10-21 06:23Z] (score 4) **Micron faces strike from one Taiwan union after deal with another - Reuters** — GN: Reuters chips | Reuters  
  https://news.google.com/rss/articles/CBMiswFBVV95cUxOV193bUJ6bXZZcHp1Q0tId1ZUdU90Um9BR09QOU0wZ0pxNmJtVFhSbVhBMi1hdXY5ajVReHFJSVVseXY2V2Z4N3hEcTEzenJJSVAwRnNCWXVnV1NudWdqalpwenc5eDhBSTVVaUZYZ1kxaTlpcEh4NWRSSkdrMUVZeDhlQTZXU2RFQ3oyZDVwU0tsbFFRRzRIMGpiODVjM0otVUJlVEZRSmV5UGtpYXJBY3B1aw?oc=5
- [10-21 00:44Z] (score 10) **$SMCI SEC 8-K (items 2.02,9.01): 8-K** — SEC SMCI | SEC EDGAR  
  https://www.sec.gov/Archives/edgar/data/1375365/000137536526000025/smci-20261020.htm
- [10-20 22:40Z] (score 4) **Super Micro sees quarterly revenue soaring on AI server boom - Reuters** — GN: Intel / Arm / SMCI | Reuters  
  https://news.google.com/rss/articles/CBMipwFBVV95cUxNbi1LQllxYlpia2VlTmhXMzFCUVRoZ0NESFFaSFVkTkJJR1kxRkVYa1BYWkVWLXJvS1UwdHk2UnJHVnQxS2NQNnU2bVdSWW4tY1JfSGdFNlNpcjZjRjZDX3ZuSklSaHdPazdsVzlWVzMxcWY4d1pic2dwLXhOdEdiRHdpZlJsOWIxeUpVTDFfOG4tbVp0UEFXeXczaDJseW9BZks4aU13WQ?oc=5
- [10-20 22:05Z] (score 4) **Super Micro Computer Shares Up as Preliminary Revenue Tops Guidance - WSJ** — GN: Intel / Arm / SMCI | WSJ  
  https://news.google.com/rss/articles/CBMitAFBVV95cUxQZmVYTXA1OU5xU3A2b3JfUFo1VTZvcXJfM3RFZFgwYmdqZEwtUHFvSjdMTTJWbGw1RmNBejlEemlRN2E3cTBMcUZIc3kzYzBNTDNnUWdPYWVXTkQzTnFSMUtScjNTWV9xSGhOVW1KVnZkeUVrU1lTUkpEVFAxUHZ5VFRQdndKMklFLVpseVdOMzFwRGJhRGcwMEl5Mnl3T2NsbklCcGo4UWJWZk91ZkMtMnk2d2I?oc=5
- [10-20 16:29Z] (score 4) **EXCLUSIVE: Qualcomm to cut jobs worldwide in performance-focused layoffs, internal memo shows - Reuters** — GN: Reuters chips | Reuters  
  https://news.google.com/rss/articles/CBMivAFBVV95cUxNUndSd0N2Um9RWGtEUDU1MHBGUm1LU3RkT2RpRFVDbVNzRHdNTGVGYnk1MU1pSUFCQklWMnZERzc0bEJ0VDVUWUp5N3JHV3M0eVFMaGRFOEdwcjU0WlUxOG55enFWb09Id3AySlhLenVTT0k4Zk51WUhuQ05oVlBSWmg3d3NmLTFzOVBJTHVsc3RSN21WaGdwYjNCa19RSTRGWUhIXzQ1a25mSDhxQ0JwdzNJRUZiaHdXZTREOQ?oc=5
- [10-20 15:51Z] (score 4) **EXCLUSIVE: ByteDance, Alibaba, Tencent place over $35 billion worth of Nvidia chip orders - Reuters** — GN: chip export rules | Reuters  
  https://news.google.com/rss/articles/CBMizgFBVV95cUxQOXBuUld1bXhxNWlQNktuUmYxOWpVRFlnN0dialpvZlhYM1JLVzE1N0VBSUVNbUlCNmwtN2RVWXRkd1VUV3BRSV9aMGJGMkpxQUk4VWZ1dUt5YjZpdmthQVZ3REFHUzBmV3B0SFJwOFFsMl9fb3l0Y3F0Z1FXbDAxSFhTbV9peVVDQ3FKRnp3NjVDdEpRVHdIOG04SjctLWRRTzN2bDM1a2QxaGdZMHlJV0hGS1FObHFKTVNiS3hvXzZsUzdvMktteFBvSGNEZw?oc=5
- [10-20 03:25Z] (score 4) **Amkor triples Gwangju investment as AI packaging demand grows - digitimes** — GN: packaging | digitimes  
  https://news.google.com/rss/articles/CBMiogFBVV95cUxQQkNKQlNnOFJ5Qkt5NGlNZjZJLWI3T0NDUXZJZmR2ZlhSOGswQWo0NFlEMGwzWnZNYzBVX2lFbzc4S2tNamtib0lrcVp3RmJuS1NrRW5SQkJ6SEZocUdOMkdMc2ZwMVVjV2QtRGllcDktUDNUOGlWMFdFMmlFWnFFd0hUei01RmlwcmNNOUNVNGwwQzB3OTZJTTBjZWVkUVlaNGc?oc=5
- [10-20 02:16Z] (score 4) **‘Open your doors for AI’: German chancellor urges businesses to embrace AI as Nvidia announces new investments** — CNBC Technology | CNBC  
  https://www.cnbc.com/2026/10/20/german-chancellor-urges-businesses-to-embrace-ai.html
- [10-20 01:51Z] (score 5) **Analysis: China's proposed AI export controls reach beyond chips to design IP, computing infrastructure - digitimes** — GN: chip export rules | digitimes  
  https://news.google.com/rss/articles/CBMijwFBVV95cUxNSV94VmRtNHA2WXNSTWNLRFVJcFF5dHNJZERCdlhaWktBVURTRXRCQVM3S3RPRDBEMm43NzNkcS10d2xwWEx0aUtWbUpiLTFjdEdrZnprNGhLMFRTT2kwNTZfVUMzZWw0SDVDczlJNXZ6SE1PR1VlUFNwU0Rna1E0UFdhRDNSMkQ3T1A3cVN6UQ?oc=5
- [10-19 23:21Z] (score 4) **Nvidia-backed Nscale, Anthropic in talks for new $45 billion AI cloud deal, source says - Reuters** — GN: Reuters chips | Reuters  
  https://news.google.com/rss/articles/CBMiwgFBVV95cUxPcGMyclR5X0JrXzBKem90Uk1sZnBQNkcyRnlyc3ZnWTM4Q0ZoUWtKUzRrd1Y3aHlqaDRjT1pfaFdmV0pHYUFROFI3TFhTWVhtczJsM01PSF8tSEtXejB4emlhVjZGMmQzeWh0RXJoaS0tNDQ1SDhlZDRJZU5hZG5ibE85N3dxU21DS2ZKYm1NV2pVUUF4ZjF3XzQ1ZncwaHVMdXlWZ2FsWjRtQ1d0eFN2YUVQc2x4cTd6YjNwSTVuVUFQZw?oc=5
- [10-19 21:11Z] (score 4) **Germany's Merz urges AI investment ahead of Nvidia deal - Reuters** — GN: Reuters chips | Reuters  
  https://news.google.com/rss/articles/CBMirgFBVV95cUxOT09KR2R3TjktZGltSk9PMGtKcGVMeFBuSmR5eTVkMERSbkVuc0d5bGhnanJ2WloyWUtULU1PTkFVQlNhaklmWmJESHF2cEV0Q01YQ3NBb3RxWklLQlNLelBEMzVBSF9nZ09Uc0FjLUhHUmhOeUF1Z0pObndUclVjT0s2Q3Fka2Z6dWltWC1MQ0g5cmo0V1dUeFY0M3hEOE5aSzV3RjdZZ2JFUTU4TEE?oc=5

## Rejected samples by reason

### no material event (45)

- Bringing the Spark to Europe: Local Intelligence Powers Next Wave of Agents — NVIDIA Newsroom |  → _no material event_
- NVIDIA Cloud Partners Scale Across Europe — Sovereign, Open and Built for Safe AI Agents — NVIDIA Newsroom |  → _no material event_
- Europe’s Industrial Leaders Reinvent Engineering and Manufacturing With NVIDIA — NVIDIA Newsroom |  → _no material event_
- NVIDIA cuDSS Now Generally Available to Accelerate Engineering and Scientific Simulations — NVIDIA Newsroom |  → _no material event_
- NVIDIA Confidential Computing Expands, Enabling Frontier Model Builders to Securely Scale Across Global Infrastructure — NVIDIA Newsroom |  → _no material event_
- NVIDIA Advances Isaac Platform for General-Purpose Robotics With New Reference Humanoid, Frameworks, Simulation Pipelines and Data — NVIDIA Newsroom |  → _no material event_

### clickbait (18)

- GTC Berlin 2026: Live Updates From NVIDIA CEO Jensen Huang’s Keynote — NVIDIA Newsroom |  → _clickbait/noise pattern: 'Live Updates'_
- GTC Berlin 2026: Live Updates From NVIDIA CEO Jensen Huang’s Keynote — NVIDIA Blog |  → _clickbait/noise pattern: 'Live Updates'_
- Futures orbit around SpaceX as Tesla merger talk cheers investors — CNBC Technology | CNBC → _clickbait/noise pattern: 'Futures'_
- SpaceX stock jumps 10% after earnings beat and Musk hints at Tesla tie-up — CNBC Technology | CNBC → _clickbait/noise pattern: 'stock jumps'_
- Apple adds U.S. titanium supplier for iPhone Duo as supply stays tight — CNBC Technology | CNBC → _clickbait/noise pattern: 'iPhone'_
- Jim Cramer says don't chase the AI rebound just yet. Here's what needs to happen first — CNBC Technology | CNBC → _clickbait/noise pattern: 'Here's what'_

### duplicate (4)

- Google Cloud and NVIDIA Announce General Availability of NVIDIA Vera Rubin Infrastructure — NVIDIA Blog |  → _duplicate (same headline)_
- Intel hits construction milestone at Ohio chip fab that’s at least 5 years behind schedule - CNBC — GN: Intel / Arm / SMCI | CNBC → _duplicate (same headline)_
- EXCLUSIVE: ByteDance, Alibaba, Tencent place over $35 billion worth of Nvidia chip orders - Reuters — GN: Reuters chips | Reuters → _duplicate (same headline)_
- Super Micro sees quarterly revenue soaring on AI server boom - Reuters — GN: Reuters chips | Reuters → _duplicate (same headline)_

### no core company (103)

- Meta ordered to pay $25 billion penalty in New Mexico Cambridge Analytica case — CNBC Technology | CNBC → _no core company/ticker_
- Tesla beats on earnings and revenue — CNBC Technology | CNBC → _no core company/ticker_
- Tokenized stock trading takes off overseas as Goldman, other U.S. companies object — CNBC Technology | CNBC → _no core company/ticker_
- Investors are questioning neoclouds' business model but Nebius says AI computing prices are rising — CNBC Technology | CNBC → _no core company/ticker_
- OpenAI to bring AI models to Google's cloud, in further expansion beyond Microsoft — CNBC Technology | CNBC → _no core company/ticker_
- OpenAI's most powerful AI models disabled their own safety monitoring — and one lied about it — CNBC Technology | CNBC → _no core company/ticker_

### untrusted source (670)

- Prediction: TSMC Stock Is Going to $1,200 by 2030 - The Motley Fool — GN: TSMC | The Motley Fool → _untrusted source: The Motley Fool_
- Prediction: TSMC Stock Is Going to $1,200 by 2030 - Yahoo Finance — GN: TSMC | Yahoo Finance → _untrusted source: Yahoo Finance_
- Taiwan Semiconductor Owns The Tollbooth and Helps Me Ignore The AI Financing Noise - 24/7 Wall St. — GN: TSMC | 24/7 Wall St. → _untrusted source: 24/7 Wall St._
- TSMC: Q3 Earnings Reveal The Coiled Spring For 2027 Profits (NYSE:TSM) - Seeking Alpha — GN: TSMC | Seeking Alpha → _untrusted source: Seeking Alpha_
- Moody’s upgrades TSMC rating to Aa2 on booming AI demand and market dominance - Investing.com — GN: TSMC | Investing.com → _untrusted source: Investing.com_
- Zacks Investment Ideas feature highlights: Taiwan Semiconductor Manufacturing, ASML and BWX Technologies - The Globe and Mail — GN: TSMC | The Globe and Mail → _untrusted source: The Globe and Mail_

### routine filing (4)

- $AMD SEC 4: FORM 4 — SEC AMD | SEC EDGAR → _routine filing: 4_
- $MU SEC 4: PRIMARY DOCUMENT — SEC MU | SEC EDGAR → _routine filing: 4_
- $SMCI SEC 3/A: FORM 3/A — SEC SMCI | SEC EDGAR → _routine filing: 3/A_
- $SMCI SEC 3: FORM 3 — SEC SMCI | SEC EDGAR → _routine filing: 3_

## Estimate

passed per day ≈ 5.7 stories (upper bound on webhook wakes/day at */5 cron)
