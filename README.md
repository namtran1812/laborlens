# LaborLens

**Revision-aware, point-in-time labor-market intelligence.**

[Live Demo](https://laborlens-eosin.vercel.app) ·
[API](https://laborlens.onrender.com/docs) ·
[Replay Explorer](https://laborlens-eosin.vercel.app/replay) ·
[Methodology](https://laborlens-eosin.vercel.app/methodology)

LaborLens is an autonomous economic-research system for discovering, validating, replaying, and explaining labor-market regime changes.

The central problem it addresses is subtle:

> **Would an economic conclusion have been detectable using only the information that was actually available at the time?**

Most historical analysis accidentally uses revised data. A model evaluated against today's version of a labor-market series can therefore appear to identify a signal earlier, more confidently, or more consistently than a researcher operating in real time actually could have.

LaborLens reconstructs historical information states from release vintages, detects multivariate labor-market regimes, groups them into research episodes, validates supporting and opposing evidence, tracks how conclusions evolve under later revisions, and exposes the resulting research through a public API, interactive frontend, deterministic article generator, and grounded AI interface.

---

## Live Product

**Frontend**

https://laborlens-eosin.vercel.app

**Public API**

https://laborlens.onrender.com

**Interactive API documentation**

https://laborlens.onrender.com/docs

The hosted version runs in a zero-cost demo configuration backed by validated research snapshots. The complete repository contains the ingestion, vintage storage, point-in-time reconstruction, research, replay, backtesting, writing, and local AI implementation.

Because the API is hosted on a free instance, the first request after inactivity may take additional time while the service wakes.

---

## Why LaborLens?

Suppose a historical dataset currently shows:

```text
May 2024 → weakening
June 2024 → contraction
July 2024 → contraction
```

It is tempting to conclude:

> "The labor market entered contraction in June 2024."

But that does not answer when a researcher could actually have known this.

The June observation may have been released weeks later. Other indicators may not yet have been published. Initial estimates may have differed from their revised values. A signal visible in today's dataset may not have existed in the information set available in June.

LaborLens therefore separates two concepts:

```text
observation date
    ≠
information availability date
```

Instead of only asking:

```text
What does the historical dataset say now?
```

LaborLens also asks:

```text
What could the system have concluded
using only data released by date t?
```

That distinction drives the architecture of the project.

---

## Example Result

For the June 2024 labor-market contraction episode, LaborLens reconstructs the following final research state:

```text
Episode:
2024-06-01 → 2024-06-01

Type:
broad_contraction

Final regime score:
-0.461

Confidence:
84.3%

Skeptic verdict:
supported
```

The strongest standardized supporting contributions were:

| Series | Signal | Standardized contribution |
|---|---|---:|
| PAYEMS | Total nonfarm payroll employment | -0.850 |
| UNRATE | Unemployment rate | -0.659 |
| ICSA | Initial unemployment claims | -0.622 |
| JTSHIR | Hires rate | -0.326 |

These values are standardized directional contributions to the regime signal, **not percentage changes in the underlying economic series**.

---

## The More Interesting Question: When Was It Knowable?

A conventional backtest can identify the June 2024 episode using the final historical dataset.

LaborLens's release-aware replay asks when the same conclusion first became detectable in real time.

For this episode:

```text
target observation:
2024-06-01

previous information state:
2024-07-25

first detected:
2024-07-30

detection latency:
59 days

release attribution:
JTSHIR, JTSJOL

initial score:
-0.446

final score:
-0.461

absolute score revision:
0.0147

survival rate after detection:
100%

claim-type flips:
0
```

The episode was **not detectable through the July 25 information state**.

When additional JOLTS information became available on July 30, the reconstructed information set crossed LaborLens's detection criteria.

This lets the system distinguish:

```text
when an economic condition occurred
```

from:

```text
when sufficient evidence existed to detect it
```

---

# Architecture

```text
                         ┌─────────────────────┐
                         │      FRED / ALFRED  │
                         │ releases + vintages │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │     Ingestion       │
                         │ vintage backfilling │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │     ClickHouse      │
                         │ observations        │
                         │ release vintages    │
                         │ provenance          │
                         └──────────┬──────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │ Point-in-Time Reconstruction  │
                    │       data known as of t      │
                    └───────────────┬───────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │     Research Engine           │
                    │                               │
                    │ features → regimes → claims   │
                    │ → episodes → evidence         │
                    │ → skeptic validation          │
                    └───────────────┬───────────────┘
                                    │
                    ┌───────────────┼────────────────┐
                    │               │                │
                    ▼               ▼                ▼
             ┌────────────┐  ┌────────────┐  ┌─────────────┐
             │   Replay   │  │ Backtesting│  │   Writer /  │
             │   Engine   │  │ + revision │  │ Grounded AI │
             └──────┬─────┘  │ analysis   │  └──────┬──────┘
                    │        └──────┬─────┘         │
                    └───────────────┼───────────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │      FastAPI        │
                         │  public research API│
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │      Next.js        │
                         │ research workspace  │
                         └─────────────────────┘
```

---

# Research Pipeline

LaborLens treats an economic conclusion as a research object rather than immediately turning an anomaly into prose.

The pipeline is approximately:

```text
raw observations
      ↓
point-in-time reconstruction
      ↓
feature engineering
      ↓
direction normalization
      ↓
rolling standardization
      ↓
smoothed regime score
      ↓
candidate claims
      ↓
episode clustering
      ↓
supporting evidence
      ↓
counter-evidence
      ↓
skeptic validation
      ↓
historical context
      ↓
research bundle
      ↓
article / grounded answer
```

This separation matters because the writer does not decide what the evidence means.

The research engine does.

---

## 1. Vintage-Aware Data

LaborLens stores observations together with their release vintages.

Conceptually:

```text
series_id
observation_date
vintage_date
value
```

This allows queries of the form:

```text
What value for PAYEMS would have been
known on 2024-07-01?
```

rather than simply:

```text
What is the current historical PAYEMS value
for that observation?
```

That makes point-in-time reconstruction possible.

---

## 2. Feature Engineering

For each labor-market series, LaborLens derives features such as:

```text
level
first difference
acceleration
rolling mean
rolling variance
rolling z-score
```

Signals are direction-normalized so that economically different series can contribute consistently to a composite regime.

For example, an increase in unemployment and a decrease in hiring can both represent weakening even though their raw numerical directions differ.

---

## 3. Regime Detection

Standardized signals are aggregated into a composite labor-market regime score.

The system looks for coordinated movements across indicators rather than relying on a single series.

Conceptually:

```text
PAYEMS ─────┐
UNRATE ─────┤
ICSA ───────┼──► standardized directional signals
JTSHIR ─────┤
JTSJOL ─────┘
                 │
                 ▼
            regime score
                 │
                 ▼
          candidate claim
```

Candidate claims include states such as broad contraction when sufficiently strong cross-series evidence is present.

---

## 4. Episode Construction

Adjacent candidate claims are clustered into episodes.

Instead of emitting:

```text
May → contraction
June → contraction
July → contraction
August → contraction
```

the system can represent the sequence as a research episode:

```text
May → August
broad_contraction
```

Each episode records its time range, representative score, confidence, claim type, and headline.

---

## 5. Evidence and Counter-Evidence

Every episode is converted into a structured evidence bundle.

The engine identifies:

```text
supporting indicators
counter-signals
standardized contributions
historical comparisons
provenance
```

This prevents the narrative layer from selecting evidence after deciding what story it wants to tell.

---

## 6. Deterministic Skeptic

Before publication, candidate research is passed through a skeptic stage.

The skeptic evaluates whether the evidence actually supports the claim and produces a structured verdict.

Example:

```json
{
  "verdict": "supported",
  "score": 0.8374
}
```

The goal is not to make an LLM responsible for factual validation.

Validation remains part of the deterministic research pipeline.

---

# Release-Aware Replay

Replay is one of the central features of LaborLens.

Given:

```text
target episode
start information date
end information date
```

the system repeatedly reconstructs the data available at each historical information state and reruns the research pipeline.

For example:

```text
2024-07-03     not detected
2024-07-05     not detected
2024-07-11     not detected
2024-07-18     not detected
2024-07-25     not detected
2024-07-30     FIRST DETECTED
2024-08-01     detected
2024-08-02     detected
...
2024-09-01     detected
```

The replay engine measures:

```text
first detection date
previous information state
release attribution
detection latency
survival rate
claim-type flips
score revision
confidence revision
mean score drift
maximum score drift
start-date drift
end-date drift
```

This provides a direct view of **research stability under information arrival and revision**.

---

# Anti-Survivorship Backtesting

There is another problem with evaluating only today's historical dataset.

Suppose a real-time information state produced a contraction signal, but later revisions caused that signal to disappear.

A conventional final-state backtest never sees it.

That creates survivorship bias in the evaluation itself.

LaborLens therefore tracks **real-time episode families** in addition to final-state episodes.

For a historical experiment from 2019 through September 2024 with a 24-month window:

```text
realtime episode families:       3
persistent families:             2
disappeared families:            1

persistence rate:             66.7%
revision disappearance rate:  33.3%
```

The `revision_disappearance_rate` measures the fraction of real-time episode families that appeared historically but were absent from the final revised state.

It is deliberately **not** called a false-discovery rate: disappearance under revision does not prove that the original economic inference was statistically false.

---

## Window-Sensitivity Experiment

LaborLens also exposes how regime definitions affect stability.

Using the same 2019–2024 evaluation horizon:

| Window | Final Episodes | Real-Time Families | Persistence | Revision Disappearance | Median Detection Latency |
|---:|---:|---:|---:|---:|---:|
| 12 months | 7 | 11 | 63.6% | 36.4% | 75 days |
| 24 months | 2 | 3 | 66.7% | 33.3% | 62.5 days |
| 36 months | 3 | 3 | 100.0% | 0.0% | 61 days |

The shorter window produces more candidate episodes but substantially more revision-sensitive signals.

The longer window is much more stable in this experiment.

These results are descriptive for the evaluated historical period; they are not evidence that a 36-month window is universally optimal.

---

# Grounded AI

LaborLens includes an AI interface, but the language model is deliberately placed **after** the research pipeline.

The intended architecture is:

```text
User question
      │
      ▼
Structured research state
      │
      ├── episode
      ├── evidence
      ├── skeptic verdict
      ├── replay metrics
      ├── revision history
      └── provenance
      │
      ▼
Grounded response layer
      │
      ▼
Natural-language explanation
```

The model is not asked to independently infer what happened in the labor market.

Instead, it explains research objects that have already been constructed and validated by LaborLens.

Example question:

```text
Why was this episode first detected on July 30?
```

Example answer:

> The June 2024 contraction was not detectable through the July 25 information state. On July 30, new JOLTS information for JTSHIR and JTSJOL entered the available information set. With those releases included, the episode crossed LaborLens's detection criteria with an initial regime score of -0.446 and confidence of 84.2%.

The response is grounded in replay states and release attribution rather than unconstrained model knowledge.

---

## Hosted AI vs. Local AI

The public deployment is designed to remain free.

Therefore the hosted demo uses **validated deterministic research answers** for supported questions.

Example API response:

```json
{
  "mode": "grounded-demo",
  "model": "validated-research-snapshot",
  "sources": [
    "Replay state: 2024-07-25",
    "Replay state: 2024-07-30",
    "Release attribution: JTSHIR, JTSJOL"
  ]
}
```

For local research, LaborLens also contains an Ollama-backed writer path, allowing local model inference without making the public application dependent on a paid model API.

This preserves the same architectural principle:

```text
research engine → validated context → language model
```

rather than:

```text
raw data → language model → trust the answer
```

---

# Public Product

LaborLens is exposed as both an API and an interactive research workspace.

## Overview

The home page surfaces detected labor-market episodes and provides entry points into the underlying research.

Users can move from:

```text
episode
  ↓
evidence
  ↓
historical context
  ↓
replay
  ↓
grounded explanation
```

rather than only reading a generated article.

---

## Episode Workspace

Each episode exposes:

- claim type
- start and end dates
- regime score
- confidence
- skeptic verdict
- supporting evidence
- counter-evidence
- historical percentile
- provenance
- generated research article
- grounded questions

Example:

https://laborlens-eosin.vercel.app/episodes/2024-06-01

---

## Replay Explorer

The replay interface visualizes the episode across historical information states.

https://laborlens-eosin.vercel.app/replay

It makes the difference between occurrence and detectability visible:

```text
NOT DETECTED
NOT DETECTED
NOT DETECTED
...
FIRST DETECTED
DETECTED
DETECTED
```

Users can inspect when a conclusion appeared and how its score changed as additional releases and revisions became available.

---

## Methodology

The public methodology page explains the research assumptions and system architecture.

https://laborlens-eosin.vercel.app/methodology

This is intentionally part of the product: economic conclusions should be inspectable rather than presented as opaque AI output.

---

# API

The backend is implemented with FastAPI.

Interactive documentation:

https://laborlens.onrender.com/docs

Core endpoints include:

```text
GET  /health
GET  /meta
GET  /episodes
GET  /episodes/{start_date}
GET  /article/{start_date}
GET  /replay
POST /ask
```

---

## Health

```bash
curl https://laborlens.onrender.com/health
```

Example:

```json
{
  "status": "ok",
  "service": "laborlens",
  "mode": "demo"
}
```

---

## Episodes

```bash
curl \
  "https://laborlens.onrender.com/episodes"
```

Example:

```json
{
  "count": 1,
  "episodes": [
    {
      "episode_id": "broad_contraction-2024-06-01-2024-06-01",
      "claim_type": "broad_contraction",
      "start_date": "2024-06-01",
      "end_date": "2024-06-01",
      "duration_months": 1,
      "peak_confidence": 0.8430936516010492,
      "score": -0.4606394461100772,
      "headline": "Labor-market indicators are weakening broadly"
    }
  ]
}
```

---

## Episode Research Bundle

```bash
curl \
  "https://laborlens.onrender.com/episodes/2024-06-01"
```

This returns the episode together with its skeptic result, supporting and counter-evidence, historical context, and provenance metadata.

---

## Replay

```bash
curl \
  "https://laborlens.onrender.com/replay?from=2024-06-01&to=2024-09-01&target=2024-06-01&schedule=releases"
```

The response contains every reconstructed information state plus summary metrics.

---

## Ask LaborLens

```bash
curl \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Which indicators contributed most?",
    "start_date": "2024-06-01"
  }' \
  https://laborlens.onrender.com/ask
```

Example:

```json
{
  "answer": "The strongest standardized supporting contribution was PAYEMS at -0.85, followed by UNRATE at -0.66, ICSA at -0.62, and JTSHIR at -0.33. These are standardized directional contributions, not percentage changes in the underlying economic series.",
  "mode": "grounded-demo",
  "model": "validated-research-snapshot",
  "sources": [
    "PAYEMS contribution: -0.850",
    "UNRATE contribution: -0.659",
    "ICSA contribution: -0.622",
    "JTSHIR contribution: -0.326"
  ]
}
```

---

# CLI

LaborLens can also be used directly from the command line.

## Ingest a Series

```bash
laborlens ingest UNRATE \
  --from 2024-01-01
```

---

## Analyze a Series

```bash
laborlens analyze UNRATE \
  --latest \
  --window 12 \
  --threshold 2.0
```

---

## Backfill Historical Vintages

```bash
laborlens backfill-vintages PAYEMS \
  --from 2024-01-01 \
  --to 2024-08-31 \
  --vintage-start 2024-01-01 \
  --vintage-end 2024-09-01 \
  --batch-size 100
```

---

## Run a Revision-Aware Backtest

```bash
laborlens backtest \
  --from 2019-01-01 \
  --to 2024-09-01 \
  --window 24 \
  --min-confidence 0.55 \
  --show-episodes \
  --show-families
```

The backtest reports both final-state evaluation and anti-survivorship metrics.

---

# Running Locally

## Requirements

- Python 3.11+
- Docker
- Node.js
- npm
- a FRED API key for live ingestion

Clone the repository:

```bash
git clone https://github.com/namtran1812/laborlens.git
cd laborlens
```

Create a Python environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install LaborLens:

```bash
pip install -e ".[dev]"
```

---

## Environment

Create `.env` locally.

```env
FRED_API_KEY=your_key_here
CLICKHOUSE_HOST=localhost
CLICKHOUSE_PORT=8123
CLICKHOUSE_DATABASE=laborlens
CLICKHOUSE_USER=default
CLICKHOUSE_PASSWORD=laborlens
```

`.env` is ignored by Git and should never be committed.

---

## Start ClickHouse

```bash
docker compose up -d
```

Check the service:

```bash
docker compose ps
```

The initialization migration creates the core tables:

```text
series
observations
ingestion_runs
```

---

## Run the API

Activate the environment:

```bash
source .venv/bin/activate
```

Then run the FastAPI application using the project's configured entry point.

The local API is available at:

```text
http://localhost:8000
```

and its OpenAPI documentation at:

```text
http://localhost:8000/docs
```

---

## Run the Frontend

```bash
cd frontend
npm install
npm run dev
```

Then open:

```text
http://localhost:3000
```

Configure the frontend's API base URL for the environment in which it is running.

---

# Testing

Backend:

```bash
ruff format --check .
ruff check .
pytest -q
```

Current suite:

```text
74 passed
```

Frontend:

```bash
cd frontend
npm run lint
npm run build
```

The production build covers:

```text
/
 /episodes/[startDate]
 /methodology
 /replay
 /robots.txt
 /sitemap.xml
```

---

# Continuous Integration

GitHub Actions validates both sides of the application on pushes and pull requests.

### Backend

```text
install
  ↓
ruff format --check
  ↓
ruff check
  ↓
pytest
```

### Frontend

```text
npm ci
  ↓
eslint
  ↓
next build
```

This keeps the public research product, API, and frontend build reproducible from the repository.

---

# Project Structure

```text
laborlens/
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── frontend/
│   └── src/
│       ├── app/
│       │   ├── episodes/
│       │   ├── methodology/
│       │   ├── replay/
│       │   ├── error.tsx
│       │   ├── loading.tsx
│       │   ├── not-found.tsx
│       │   ├── robots.ts
│       │   └── sitemap.ts
│       │
│       ├── components/
│       └── lib/
│
├── laborlens/
│   ├── analysis/
│   │   ├── divergence.py
│   │   ├── features.py
│   │   └── regime.py
│   │
│   ├── api/
│   │   ├── app.py
│   │   ├── demo.py
│   │   └── run.py
│   │
│   ├── data/
│   │   └── fred.py
│   │
│   ├── evaluation/
│   │   ├── backtest.py
│   │   └── replay.py
│   │
│   ├── research/
│   │   ├── claims.py
│   │   ├── episodes.py
│   │   ├── evidence.py
│   │   ├── research_bundle.py
│   │   ├── series_catalog.py
│   │   └── skeptic.py
│   │
│   ├── services/
│   │   ├── ingestion.py
│   │   ├── research_pipeline.py
│   │   └── vintage_backfill.py
│   │
│   ├── storage/
│   │   └── clickhouse.py
│   │
│   └── writer/
│       ├── deterministic_writer.py
│       ├── ollama_writer.py
│       ├── prompt.py
│       └── verifier.py
│
├── migrations/
├── tests/
├── docker-compose.yml
├── pyproject.toml
└── README.md
```

---

# Design Principles

### 1. Respect the information set

Historical analysis should not silently use information unavailable at the time being evaluated.

### 2. Separate detection from explanation

Statistical logic determines the research state. Natural-language systems explain it.

### 3. Preserve counter-evidence

A useful research system should make contradictory evidence visible rather than optimize only for a compelling narrative.

### 4. Measure revisions explicitly

Changing historical data is part of the problem, not preprocessing noise to be discarded.

### 5. Evaluate disappearing conclusions

Signals that vanish after revisions are still part of the historical behavior of a real-time research system.

### 6. Keep claims inspectable

Episodes expose evidence, replay history, skeptic judgments, and provenance so conclusions can be audited.

---

# What LaborLens Is Not

LaborLens is not intended to establish causal economic relationships.

A detected episode represents statistical co-movement across selected labor-market indicators under the project's regime methodology.

It does **not** by itself establish:

- causation
- a particular policy mechanism
- recession classification
- trading profitability
- equivalence between historically similar episodes
- that a revised-away real-time signal was necessarily "wrong"

The system is designed for **revision-aware descriptive economic research and information-state analysis**.

---

# Research Questions

LaborLens currently provides infrastructure for studying questions including:

1. **How early can multivariate labor-market regime changes be detected using only information available in real time?**
2. **How much do later revisions change the strength, timing, duration, or classification of those signals?**
3. **How often do apparently meaningful real-time episodes disappear from the final revised historical record?**
4. **Which data releases cause a candidate regime to cross a detection threshold?**
5. **How does rolling-window choice affect detection latency and revision stability?**
6. **Can a grounded language interface explain point-in-time economic research without delegating the underlying inference to the language model?**

These are intentionally separated from claims of causal inference or forecasting performance.

---

# Technology

**Research / Backend**

- Python
- FastAPI
- Pydantic
- HTTPX
- FRED / ALFRED
- ClickHouse
- Typer

**Evaluation**

- point-in-time replay
- release-aware evaluation
- episode-family tracking
- revision analysis
- anti-survivorship backtesting

**AI**

- deterministic grounded demo responses
- local Ollama integration
- evidence-constrained prompting
- numeric verification

**Frontend**

- Next.js
- React
- TypeScript
- Tailwind CSS

**Infrastructure**

- Docker Compose
- GitHub Actions
- Render
- Vercel

---

# Deployment

The public architecture intentionally separates the product layer from the full research environment.

```text
                 Public deployment

Browser
   │
   ▼
Vercel
Next.js frontend
   │
   ▼
Render
FastAPI demo service
   │
   ▼
Validated research snapshot
```

The full local research architecture additionally supports:

```text
FRED / ALFRED
      │
      ▼
ClickHouse
      │
      ▼
point-in-time research engine
      │
      ├── replay
      ├── backtesting
      ├── deterministic writer
      └── local AI
```

This allows the public application to remain accessible without requiring paid database or model infrastructure while keeping the complete research implementation reproducible in the repository.

---

# Status

**LaborLens V1**

- [x] FRED ingestion
- [x] ALFRED/vintage-aware ingestion
- [x] ClickHouse storage
- [x] point-in-time reconstruction
- [x] feature engineering
- [x] multivariate regime detection
- [x] claim generation
- [x] episode clustering
- [x] evidence extraction
- [x] counter-evidence
- [x] skeptic validation
- [x] historical context
- [x] provenance
- [x] deterministic research writing
- [x] local AI writer
- [x] release-aware replay
- [x] release attribution
- [x] revision metrics
- [x] anti-survivorship backtesting
- [x] FastAPI research API
- [x] grounded question answering
- [x] public demo mode
- [x] Next.js research workspace
- [x] episode explorer
- [x] replay visualization
- [x] methodology interface
- [x] production error/loading states
- [x] public frontend deployment
- [x] public backend deployment
- [x] backend CI
- [x] frontend CI

---

## Author

**Nam Tran**

Built as an exploration of economic-data revisions, real-time information constraints, autonomous research systems, and grounded AI.

---

## Disclaimer

LaborLens is a research and educational project.

Its outputs are not financial, investment, employment, or policy advice.
