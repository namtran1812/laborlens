# LaborLens

**Revision-aware, point-in-time labor-market intelligence.**

LaborLens is a full-stack economic research system for detecting labor-market regimes, grounding them in structured evidence, reconstructing what was knowable at historical information dates, and measuring how conclusions change as official economic data are released and revised.

**Live demo:** https://laborlens-eosin.vercel.app

**Public API:** https://laborlens.onrender.com

---

## Why LaborLens?

Most historical economic analysis quietly benefits from hindsight.

Official data such as payroll employment, unemployment, job openings, hires, and unemployment claims are released over time and may later be revised. If a model is evaluated only against today's final dataset, it can accidentally use information that was unavailable when the event actually occurred.

LaborLens asks a stricter question:

> **What could an analyst have concluded using only the information available at that point in time, and would that conclusion survive subsequent revisions?**

Instead of treating revisions as noise to discard, LaborLens models them explicitly.

Each observation can be represented by:

```text
series_id
observation_date
value
realtime_start
realtime_end
```

This enables historical reconstruction of the information set that existed on any supported `as_of` date.

---

## Live Demo

The hosted application provides a zero-cost public demonstration of the research system.

### Frontend

https://laborlens-eosin.vercel.app

Built with:

```text
Next.js
React
TypeScript
Tailwind CSS
Vercel
```

### API

https://laborlens.onrender.com

Built with:

```text
FastAPI
Python
Uvicorn
Render
```

### Public demo mode

The hosted backend intentionally serves a **frozen, validated historical research snapshot** rather than requiring a persistent hosted ClickHouse cluster.

This keeps the public demo free while preserving the full research architecture in the repository.

The public demo includes:

- episode discovery
- evidence attribution
- skeptic validation
- historical episode inspection
- deterministic research summaries
- point-in-time release replay
- detection latency
- score revision
- revision stability
- release attribution

The full local system additionally supports:

- FRED/ALFRED ingestion
- revision-aware historical backfills
- ClickHouse vintage storage
- arbitrary point-in-time reconstruction
- historical regime discovery
- release-aware replay evaluation
- anti-survivorship backtesting
- sensitivity analysis

---

## Architecture

### Public deployment

```text
┌──────────────────────────────────────────┐
│                 Vercel                   │
│                                          │
│        Next.js + TypeScript UI           │
│                                          │
│   laborlens-eosin.vercel.app             │
└────────────────────┬─────────────────────┘
                     │
                     │ HTTPS / JSON
                     ▼
┌──────────────────────────────────────────┐
│                 Render                   │
│                                          │
│            FastAPI Backend               │
│                                          │
│        laborlens.onrender.com            │
└────────────────────┬─────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────┐
│       Validated Historical Snapshot      │
│                                          │
│ Episodes                                 │
│ Evidence                                 │
│ Replay states                            │
│ Revision metrics                         │
│ Research article                         │
└──────────────────────────────────────────┘
```

### Full research architecture

```text
                       FRED / ALFRED
                            │
                            │ releases + revisions
                            ▼
                 ┌────────────────────┐
                 │   Ingestion Layer  │
                 │                    │
                 │ FRED client        │
                 │ vintage discovery  │
                 │ vintage backfill   │
                 └─────────┬──────────┘
                           │
                           ▼
                 ┌────────────────────┐
                 │     ClickHouse     │
                 │                    │
                 │ observations       │
                 │ vintage intervals  │
                 │ release history    │
                 └─────────┬──────────┘
                           │
              ┌────────────┴────────────┐
              │                         │
              ▼                         ▼
     latest information set     historical as-of state
              │                         │
              └────────────┬────────────┘
                           ▼
                 ┌────────────────────┐
                 │ Statistical Engine │
                 │                    │
                 │ features           │
                 │ normalization      │
                 │ direction alignment│
                 │ regime score       │
                 │ smoothing          │
                 │ divergence         │
                 └─────────┬──────────┘
                           │
                           ▼
                 ┌────────────────────┐
                 │ Research Pipeline  │
                 │                    │
                 │ claim discovery    │
                 │ episode clustering │
                 │ evidence ranking   │
                 │ skeptic review     │
                 │ historical context │
                 │ provenance         │
                 └──────┬────────┬────┘
                        │        │
              ┌─────────┘        └──────────┐
              ▼                             ▼
   ┌────────────────────┐        ┌────────────────────┐
   │ Grounded Writer    │        │ Evaluation Engine  │
   │                    │        │                    │
   │ deterministic text │        │ release replay     │
   │ number verification│        │ revision metrics   │
   │ provenance-aware   │        │ anti-survivorship  │
   └────────────────────┘        │ backtesting        │
                                 └────────────────────┘
```

---

## Core Research Pipeline

### 1. FRED/ALFRED ingestion

LaborLens retrieves economic series and stores both observations and their historical vintages.

The ingestion layer supports:

```text
current observations
historical vintages
release-date discovery
revision-aware backfilling
```

Example:

```bash
laborlens backfill-vintages PAYEMS \
  --from 2019-01-01 \
  --to 2024-08-31 \
  --vintage-start 2019-01-01 \
  --vintage-end 2024-09-01 \
  --batch-size 100
```

Release-aware backfilling uses actual information dates reported by FRED rather than arbitrary calendar snapshots.

---

## Point-in-Time Reconstruction

For a historical date `t`, LaborLens reconstructs the values that were valid at that information state.

Conceptually:

```sql
realtime_start <= t
AND realtime_end >= t
```

For each observation date, the appropriate historical vintage is selected.

This allows:

```bash
laborlens article \
  --start 2024-06-01 \
  --as-of 2024-09-01
```

to behave differently from an analysis using today's revised information.

That distinction is central to LaborLens.

---

## Signal Universe

The current labor-market model includes:

| Series | Meaning |
|---|---|
| `PAYEMS` | Total nonfarm payroll employment |
| `UNRATE` | Unemployment rate |
| `ICSA` | Initial unemployment claims |
| `JTSHIR` | Hires rate |
| `JTSJOL` | Job openings level |

The indicators have different economic interpretations and units, so LaborLens transforms them into comparable standardized directional signals before aggregation.

---

## Regime Detection

The regime pipeline is:

```text
raw observations
      │
      ▼
feature construction
      │
      ▼
rolling normalization
      │
      ▼
direction alignment
      │
      ▼
cross-series composite
      │
      ▼
temporal smoothing
      │
      ▼
dispersion / breadth
      │
      ▼
regime classification
```

Possible research claims include:

```text
broad_contraction
broad_expansion
signal_divergence
```

A low-coverage state is prevented from becoming a strong research claim.

---

## Claims and Episodes

LaborLens first detects candidate claims at individual observation dates.

Adjacent compatible claims are then clustered into **episodes**.

An episode contains information such as:

```text
episode_id
claim_type
start_date
end_date
duration_months
peak_confidence
representative observation
```

This makes the system reason about persistent economic regimes rather than disconnected monthly anomalies.

---

## Evidence Layer

A regime detection does not automatically become a publishable conclusion.

For each episode, LaborLens constructs an evidence bundle containing:

```text
supporting indicators
opposing indicators
standardized contributions
breadth
dispersion
coverage
confidence
historical context
provenance
```

For a contraction episode, negative aligned contributions count as supporting evidence.

Example:

```text
PAYEMS   -0.85
UNRATE   -0.66
ICSA     -0.62
JTSHIR   -0.33
```

---

## Deterministic Skeptic

After evidence construction, a second deterministic layer evaluates whether the proposed claim is actually supported.

This deliberately separates:

```text
signal detection
```

from:

```text
research interpretation
```

A detected statistical pattern therefore does not automatically become a narrative conclusion.

---

## Grounded Research Writer

The default writer is deterministic.

It converts a structured `ResearchBundle` into an article containing:

```text
Direct answer
What changed?
Evidence
Historical context
What this does not establish
Methodology
```

The writer does not independently invent numerical facts.

A verifier checks generated numbers and dates against the research bundle before accepting the draft.

Conceptually:

```text
ResearchBundle
     │
     ▼
deterministic writer
     │
     ▼
draft
     │
     ▼
number/date verifier
     │
     ├── PASSED
     │
     └── REJECTED
```

An experimental Ollama integration remains in the repository, but the deterministic writer is the default grounded path.

---

## Release-Aware Replay

One of the central features of LaborLens is historical replay across actual economic information updates.

Instead of evaluating every arbitrary N days, LaborLens can evaluate the system whenever one of the tracked series releases or revises information.

Example:

```bash
laborlens replay-eval \
  --from 2024-06-01 \
  --to 2024-09-01 \
  --target 2024-06-01 \
  --schedule releases \
  --window 24 \
  --min-confidence 0.55
```

For the June 2024 contraction example, the replay produced 20 historical information states.

The episode was not detected through:

```text
2024-07-25
```

It first became detectable on:

```text
2024-07-30
```

The information update on that date included:

```text
JTSHIR
JTSJOL
```

The initial detected score was approximately:

```text
-0.446
```

After subsequent information arrived, it became approximately:

```text
-0.461
```

and remained detected through the final replay state.

---

## Replay Explorer

The public frontend visualizes the release-aware reconstruction directly.

Open:

https://laborlens-eosin.vercel.app/replay

The June 2024 example shows:

```text
2024-07-25    NOT DETECTED
2024-07-30    FIRST DETECTED     -0.446
2024-08-01    DETECTED           -0.446
2024-08-02    DETECTED           -0.461
...
2024-09-01    DETECTED           -0.461
```

Associated revision metrics include:

```text
detection latency          59 days
survival rate              100%
claim-type flips           0
absolute score revision    ~0.015
start-boundary drift       0 months
end-boundary drift         0 months
```

This distinguishes:

```text
when an economic state occurred
```

from:

```text
when enough official information existed to identify it
```

---

## Revision Metrics

LaborLens evaluates several dimensions of point-in-time stability.

### Detection latency

```text
first detection information date
-
episode observation date
```

Measures how long it took before the released information made the episode detectable.

### Survival rate

Measures how frequently the episode remains detected after first appearing.

### Score revision

```text
|final score - initial detected score|
```

Measures how much later information changed the estimated episode severity.

### Claim-type flips

Measures whether later vintages change the qualitative interpretation of an episode.

### Boundary drift

Measures whether later information moves the estimated beginning or end of the episode.

---

## Anti-Survivorship Backtesting

Looking only at episodes visible in today's final revised history introduces survivorship bias.

LaborLens therefore reconstructs **every episode family that appeared in real time**.

A family can:

```text
appear
persist
change boundaries
change type
disappear after revision
```

Example:

```bash
laborlens backtest \
  --from 2019-01-01 \
  --to 2024-09-01 \
  --window 24 \
  --min-confidence 0.55 \
  --show-episodes \
  --show-families
```

Baseline results:

| Metric | Result |
|---|---:|
| Final-state episodes evaluated | 2 |
| Detected historically | 2 / 2 |
| Median detection latency | 62.5 days |
| Mean survival after detection | 100% |
| Claim-type flip rate | 0% |
| Median absolute score revision | 0.134 |
| Real-time episode families | 3 |
| Persistent families | 2 |
| Disappeared families | 1 |
| Persistence rate | 66.7% |
| Revision disappearance rate | 33.3% |
| Mean start drift | 0 months |
| Mean family end drift | 7 months |

`revision_disappearance_rate` means that an episode family appeared in historical real-time states but was absent from the final reconstructed state.

It is **not** a conventional statistical false-discovery rate.

The small number of final-state episodes is also important: `2/2 detected` should not be interpreted as broad evidence of universal 100% detection performance.

---

## Sensitivity Analysis

LaborLens was evaluated under several normalization windows.

| Window | Final episodes | Median latency | Mean survival | Type flip rate | Revision disappearance | Median score revision |
|---:|---:|---:|---:|---:|---:|---:|
| 12 months | 7 | 75 d | 91.2% | 14.3% | 36.4% | 0.097 |
| **24 months** | **2** | **62.5 d** | **100%** | **0%** | **33.3%** | **0.134** |
| 36 months | 3 | 61 d | 100% | 0% | 0% | 0.054 |

The experiments expose a responsiveness/stability tradeoff.

```text
shorter window
      │
      ▼
more responsive
      │
      ▼
more episodes
      │
      ▼
more revision instability
```

versus:

```text
longer window
      │
      ▼
more smoothing
      │
      ▼
fewer unstable episodes
      │
      ▼
greater historical persistence
```

The 24-month configuration is used as the primary demonstration configuration, not because it is proven optimal, but because it provides a reasonable middle point for the evaluated sample.

---

## Confidence Sensitivity

At a 24-month normalization window, the evaluated results were unchanged for:

```text
min_confidence = 0.50
min_confidence = 0.55
min_confidence = 0.60
```

Within this historical sample, the normalization horizon therefore affected the resulting episodes more strongly than moderate changes to the confidence threshold.

This is an empirical observation for the evaluated data range, not a universal model property.

---

## REST API

The FastAPI service exposes public research endpoints.

### Health

```http
GET /health
```

Example:

```json
{
  "status": "ok",
  "service": "laborlens",
  "mode": "demo"
}
```

### Episodes

```http
GET /episodes
```

Optional parameters include:

```text
window
min_confidence
as_of
```

### Episode detail

```http
GET /episodes/{start_date}
```

Example:

```http
GET /episodes/2024-06-01?as_of=2024-09-01
```

### Article

```http
GET /article/{start_date}
```

### Replay

```http
GET /replay
```

Example:

```text
/replay
?from=2024-06-01
&to=2024-09-01
&target=2024-06-01
&schedule=releases
&window=24
&min_confidence=0.55
```

Interactive OpenAPI documentation is available through FastAPI when the service is running.

---

## CLI

LaborLens also exposes the full research workflow through a Typer CLI.

```text
laborlens ingest
laborlens vintage
laborlens as-of
laborlens analyze
laborlens compare
laborlens regime
laborlens claims
laborlens episodes
laborlens review
laborlens bundle
laborlens article
laborlens backfill-vintages
laborlens replay-eval
laborlens backtest
```

Use:

```bash
laborlens --help
```

or:

```bash
laborlens <command> --help
```

for command-specific options.

---

## Local Installation

### Requirements

```text
Python 3.11+
Docker
FRED API key
```

Clone:

```bash
git clone https://github.com/namtran1812/laborlens.git
cd laborlens
```

Create a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install:

```bash
pip install -e ".[dev]"
```

---

## Configuration

Create a local `.env` file.

Example:

```env
FRED_API_KEY=YOUR_FRED_API_KEY

CLICKHOUSE_HOST=localhost
CLICKHOUSE_PORT=8123
CLICKHOUSE_USER=default
CLICKHOUSE_PASSWORD=laborlens
CLICKHOUSE_DATABASE=laborlens

LABORLENS_DEMO_MODE=false
LABORLENS_CORS_ORIGINS=http://localhost:3000
```

`.env` is ignored by Git and should never be committed.

---

## Start ClickHouse

```bash
docker compose up -d
```

Verify:

```bash
docker compose ps
```

The default local configuration exposes:

```text
ClickHouse HTTP     localhost:8123
ClickHouse native   localhost:9000

database             laborlens
user                 default
```

The schema is initialized from:

```text
migrations/001_init.sql
```

---

## Run the API

```bash
laborlens-api
```

or:

```bash
python -m uvicorn \
  laborlens.api.app:app \
  --host 0.0.0.0 \
  --port 8000
```

Then:

```bash
curl http://localhost:8000/health
```

---

## Run the Frontend

```bash
cd frontend
npm install
npm run dev
```

Open:

```text
http://localhost:3000
```

The frontend communicates with:

```text
NEXT_PUBLIC_LABORLENS_API_URL
```

which defaults to:

```text
http://localhost:8000
```

during local development.

---

## Zero-Cost Demo Mode

The hosted API can run with no ClickHouse instance and no FRED credentials.

Start it locally with:

```bash
LABORLENS_DEMO_MODE=true \
python -m uvicorn \
  laborlens.api.app:app \
  --host 127.0.0.1 \
  --port 8001
```

Then:

```bash
curl http://localhost:8001/health
```

returns:

```json
{
  "status": "ok",
  "service": "laborlens",
  "mode": "demo"
}
```

Demo mode intentionally returns the validated frozen historical example used by the public site.

It does not replace the full ClickHouse-backed research engine.

---

## Development

Backend validation:

```bash
ruff format .
ruff check .
pytest -q
```

Frontend validation:

```bash
cd frontend
npm run lint
npm run build
```

The clean-clone reproducibility test verified:

```text
editable Python installation
Ruff
full pytest suite
fresh ClickHouse initialization
fresh FRED ingestion
release-aware vintage backfill
clean Git working tree
```

---

## Repository Structure

```text
laborlens/
├── analysis/
│   ├── divergence.py
│   ├── features.py
│   └── regime.py
│
├── api/
│   ├── app.py
│   ├── demo.py
│   └── run.py
│
├── data/
│   └── fred.py
│
├── evaluation/
│   ├── backtest.py
│   └── replay.py
│
├── research/
│   ├── claims.py
│   ├── episodes.py
│   ├── evidence.py
│   ├── research_bundle.py
│   ├── series_catalog.py
│   └── skeptic.py
│
├── services/
│   ├── ingestion.py
│   ├── research_pipeline.py
│   └── vintage_backfill.py
│
├── storage/
│   └── clickhouse.py
│
├── writer/
│   ├── deterministic_writer.py
│   ├── ollama_writer.py
│   ├── prompt.py
│   └── verifier.py
│
├── cli.py
├── config.py
└── models.py

frontend/
└── src/
    ├── app/
    │   ├── episodes/
    │   ├── replay/
    │   └── page.tsx
    │
    ├── components/
    │   ├── EvidenceBars.tsx
    │   ├── MetricCard.tsx
    │   ├── RegimeBadge.tsx
    │   └── ReplayTimeline.tsx
    │
    └── lib/
        └── api.ts

migrations/
└── 001_init.sql

tests/
```

---

## Design Principles

**Point-in-time correctness over retrospective convenience**

Historical analysis should use the information actually available at the time.

**Revisions are part of the data**

Economic revisions are explicitly modeled rather than discarded.

**Structured evidence before prose**

The research engine determines what is supported before the writer generates text.

**Deterministic numerical grounding**

Numbers and dates in generated research are checked against structured evidence.

**Evaluate disappearing conclusions**

Backtesting includes real-time episodes that later vanish instead of evaluating only final survivors.

**Detection is not causation**

LaborLens identifies statistical regimes and co-movement. It does not claim that those relationships establish causal economic mechanisms.

**Hosted demo is not the research database**

The public zero-cost deployment uses a frozen validated snapshot. The full ClickHouse-backed system remains available in the repository and local research workflow.

---

## Limitations

LaborLens is an experimental research and engineering system.

Current limitations include:

- a relatively small labor-market signal universe;
- dependence on available FRED/ALFRED vintage history;
- detection latency that partially reflects official publication schedules;
- episode-family matching based on an analytical similarity definition rather than economic ground truth;
- a small number of final-state episodes under some configurations;
- standardized regime scores that do not directly represent natural economic units;
- no claim that historical regime detection implies forecasting ability;
- no causal inference from cross-series co-movement;
- a hosted demo that intentionally serves a frozen snapshot rather than a continuously updated production database.

The backtests measure **historical revision robustness**, not investment performance.

---

## Research Questions

LaborLens makes questions like these experimentally testable:

1. How early can broad labor-market regimes be detected using only contemporaneously available information?
2. How strongly do later data revisions change those conclusions?
3. Which releases cause a regime to cross the detection threshold?
4. How frequently do real-time episodes disappear from final revised history?
5. How does normalization horizon affect responsiveness versus stability?
6. Which episode boundaries remain stable under revision?
7. Which conclusions survive both data revisions and model-parameter changes?

---

## Tech Stack

### Research / backend

```text
Python
FastAPI
Typer
Pydantic
HTTPX
ClickHouse
FRED / ALFRED
Docker
Pytest
Ruff
```

### Frontend

```text
Next.js
React
TypeScript
Tailwind CSS
```

### Deployment

```text
Vercel
Render
```

### Experimental local generation

```text
Ollama
Qwen
```

---

## Disclaimer

LaborLens is a research and engineering project.

Its outputs are statistical analyses of public economic data and should not be interpreted as financial, investment, employment, or policy advice.
