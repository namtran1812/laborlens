# LaborLens

**Point-in-time labor-market intelligence from revision-aware economic data.**

LaborLens is an economic research engine that detects unusual labor-market regimes, constructs evidence-backed research claims, evaluates how those claims behave as economic data are released and revised, and produces deterministic, numerically verified research summaries.

The central question is not simply:

> What does the labor market look like in the final revised dataset?

It is:

> **What could an analyst actually have concluded using only the information available at that point in time, and would that conclusion survive later revisions?**

LaborLens combines FRED/ALFRED economic data, ClickHouse, statistical regime detection, evidence and skeptic layers, point-in-time replay, anti-survivorship backtesting, and deterministic article generation into a reproducible research pipeline.

---

## Why LaborLens?

Economic data are revised.

A model evaluated against today's historical dataset can accidentally use information that was unavailable when the event occurred. This creates a form of **look-ahead bias**.

For example, a payroll observation for June may have:

- an initial release,
- subsequent revisions,
- benchmark revisions,
- and a different value in today's dataset.

A conventional historical analysis may unknowingly reason from the final value.

LaborLens instead stores economic observations together with their real-time validity intervals:

```text
observation_date
value
realtime_start
realtime_end
```

This makes it possible to reconstruct the information set available on a historical date and ask:

```text
What would LaborLens have detected then?
```

rather than:

```text
What does the fully revised dataset tell us now?
```

---

## Architecture

```text
                         FRED / ALFRED
                              │
                              │ releases + revisions
                              ▼
                    ┌───────────────────┐
                    │   Ingestion Layer │
                    │                   │
                    │ FRED client       │
                    │ vintage backfill  │
                    └─────────┬─────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │    ClickHouse     │
                    │                   │
                    │ observations      │
                    │ real-time ranges  │
                    │ vintage history   │
                    └─────────┬─────────┘
                              │
                 ┌────────────┴────────────┐
                 │                         │
                 ▼                         ▼
       ┌──────────────────┐      ┌──────────────────┐
       │ Latest Snapshot  │      │ Point-in-Time    │
       │ Analysis         │      │ Reconstruction   │
       └────────┬─────────┘      └────────┬─────────┘
                │                         │
                └────────────┬────────────┘
                             ▼
                  ┌─────────────────────┐
                  │ Statistical Engine  │
                  │                     │
                  │ normalization       │
                  │ directional signals │
                  │ regime scoring      │
                  │ smoothing           │
                  │ divergence          │
                  └──────────┬──────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │ Research Pipeline   │
                  │                     │
                  │ claims              │
                  │ episode clustering  │
                  │ evidence ranking    │
                  │ skeptic review      │
                  │ historical context  │
                  │ provenance          │
                  └───────┬─────────────┘
                          │
             ┌────────────┴─────────────┐
             │                          │
             ▼                          ▼
   ┌───────────────────┐      ┌────────────────────┐
   │ Grounded Writer   │      │ Evaluation Engine  │
   │                   │      │                    │
   │ deterministic     │      │ release replay     │
   │ numerical verify  │      │ revision metrics   │
   │ research article  │      │ backtesting        │
   └───────────────────┘      │ anti-survivorship  │
                              └────────────────────┘
```

---

## Core Pipeline

### 1. Revision-aware data ingestion

LaborLens retrieves economic series from FRED/ALFRED and stores both observations and their historical vintages.

The ingestion layer supports:

- current observations,
- explicit historical vintages,
- release-date discovery,
- revision-aware vintage backfills.

Release-aware backfilling uses actual FRED information dates instead of arbitrary calendar snapshots.

Example:

```bash
laborlens backfill-vintages PAYEMS \
  --from 2019-01-01 \
  --to 2024-08-31 \
  --vintage-start 2019-01-01 \
  --vintage-end 2024-09-01 \
  --batch-size 100
```

The same process can be applied to other indicators used by the regime model.

---

### 2. Point-in-time reconstruction

For a requested historical date `t`, LaborLens reconstructs the observations that were valid at `t`.

Conceptually:

```sql
realtime_start <= t
AND realtime_end >= t
```

with the appropriate vintage selected for each observation date.

This provides the foundation for genuine historical replay.

For example:

```bash
laborlens article \
  --start 2024-06-01 \
  --as-of 2024-09-01 \
  --window 24 \
  --min-confidence 0.55
```

The resulting research pipeline only uses information available by the specified `--as-of` date.

---

### 3. Statistical regime detection

LaborLens transforms heterogeneous labor-market indicators into comparable directional signals.

The analysis pipeline includes:

```text
raw observations
      ↓
feature construction
      ↓
rolling normalization
      ↓
direction alignment
      ↓
cross-series composite
      ↓
temporal smoothing
      ↓
regime classification
```

The current labor-market signal set includes indicators such as:

| Series | Interpretation |
|---|---|
| `PAYEMS` | Total nonfarm payroll employment |
| `UNRATE` | Unemployment rate |
| `ICSA` | Initial unemployment claims |
| `JTSHIR` | Hires rate |
| `JTSJOL` | Job openings level |

Indicators are directionally aligned before aggregation so that movements can contribute consistently to expansion or contraction regimes.

---

### 4. Claim and episode construction

Individual regime observations are transformed into research claims.

Adjacent compatible claims are clustered into **episodes**, allowing LaborLens to reason about persistent labor-market regimes rather than isolated monthly observations.

An episode records information such as:

```text
start date
end date
claim type
representative score
peak confidence
```

Example claim:

```text
Labor-market indicators are weakening broadly
```

---

### 5. Evidence and skeptic layers

A detected regime is not automatically treated as a publishable conclusion.

LaborLens constructs an evidence bundle containing:

- supporting indicators,
- opposing indicators,
- standardized contributions,
- historical comparisons,
- provenance,
- regime statistics.

A deterministic skeptic then evaluates whether the evidence actually supports the proposed claim.

This separates:

```text
signal detection
```

from:

```text
research conclusion
```

and prevents the writer from independently deciding what the data mean.

---

## Deterministic Grounded Writing

The default article writer does not require a local LLM.

Research bundles are converted into deterministic articles whose numerical claims are checked against the underlying structured evidence.

Example:

```bash
laborlens article \
  --start 2024-06-01 \
  --as-of 2024-09-01
```

Example output:

```text
# Labor-market indicators are weakening broadly

LaborLens identified a broad contraction episode...

Evidence

- Total nonfarm payroll employment (PAYEMS)
- Unemployment rate (UNRATE)
- Initial unemployment claims (ICSA)
- Hires rate (JTSHIR)
```

Before publication, the verifier checks numerical and date claims against the research bundle.

```text
writer
   ↓
draft
   ↓
numeric/date verifier
   ↓
PASSED / REJECTED
```

This design avoids making an LLM responsible for numerical truth.

An Ollama writer remains available experimentally, but deterministic generation is the primary grounded path.

---

## Release-Aware Historical Replay

A major feature of LaborLens is the ability to replay an episode across actual economic information updates.

Instead of evaluating only every 30 days, release-aware replay obtains dates on which tracked series actually released or revised information.

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

For the June 2024 contraction episode, LaborLens reconstructed 20 historical information states.

The episode first appeared on:

```text
2024-07-30
```

The previous information state was:

```text
2024-07-25
```

The information arriving on the detection date came from:

```text
JTSHIR
JTSJOL
```

The detected episode then remained present through the final replay state.

Example revision metrics:

```text
first_detected_as_of=2024-07-30
previous_information_state=2024-07-25
detection_release_series=JTSHIR,JTSJOL

detection_latency_days=59
survival_rate=100.0%
claim_type_flips=0

initial_score=-0.446
final_score=-0.461
absolute_score_revision=0.015

start_drift_months=0
end_drift_months=0
```

This allows LaborLens to distinguish between:

- when an economic condition occurred,
- when enough information existed to detect it,
- and how much the conclusion changed afterward.

---

## Revision Metrics

Replay evaluation measures several forms of historical stability.

### Detection latency

```text
first detection date - episode observation date
```

This measures how long it took for released economic data to make an episode detectable.

### Survival rate

Measures how often an episode remains detected after its first appearance.

### Score revision

```text
|final score - initial score|
```

Measures how strongly later data revisions change the estimated severity of an episode.

### Claim-type flips

Tracks whether later information changes the qualitative interpretation of an episode.

### Boundary drift

Tracks whether later information moves the estimated beginning or end of an episode.

Together, these metrics measure not only whether the system eventually finds an event, but whether its conclusions are stable under data revision.

---

## Anti-Survivorship Backtesting

Evaluating only episodes visible in the final revised dataset introduces survivorship bias.

LaborLens therefore reconstructs **real-time episode families** across historical information states.

A family tracks the same evolving episode through successive vintages:

```text
first appearance
      ↓
subsequent releases
      ↓
revisions
      ↓
boundary changes
      ↓
final state or disappearance
```

This reveals episodes that appeared plausible in real time but disappeared after later revisions.

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

For one evaluated configuration:

```text
realtime_episode_families=3
persistent_families=2
disappeared_families=1

persistence_rate=66.7%
revision_disappearance_rate=33.3%
```

`revision_disappearance_rate` specifically means that an episode family detected from historical vintages was no longer represented in the final reconstructed state.

It is **not** a conventional predictive false-positive rate.

---

## Sensitivity Analysis

The model was evaluated under multiple rolling normalization windows.

### 12-month window

```text
final episodes:                7
real-time episode families:   11
persistence rate:             63.6%
revision disappearance rate: 36.4%
median detection latency:     75 days
mean survival rate:           91.2%
```

This configuration is more responsive but produces more revision-sensitive episodes.

### 24-month window

```text
final episodes:                2
real-time episode families:    3
persistence rate:             66.7%
revision disappearance rate: 33.3%
median detection latency:     62.5 days
mean survival rate:           100%
```

### 36-month window

```text
final episodes:                3
real-time episode families:    3
persistence rate:             100%
revision disappearance rate:   0%
median detection latency:     61 days
mean survival rate:           100%
```

These results expose an important tradeoff:

```text
shorter normalization window
        ↓
greater responsiveness
        ↓
more detected episodes
        ↓
greater revision sensitivity


longer normalization window
        ↓
greater smoothing
        ↓
fewer unstable episodes
        ↓
greater historical persistence
```

The goal is therefore not simply to maximize the number of detected events.

The evaluation framework makes the responsiveness/stability tradeoff measurable.

---

## Confidence Sensitivity

For the tested 24-month configuration, changing the minimum confidence threshold from:

```text
0.50
```

to:

```text
0.55
```

to:

```text
0.60
```

did not change the evaluated episode set.

This suggests that, within that range and historical sample, the normalization window was a more important sensitivity parameter than the confidence cutoff.

This observation is empirical and specific to the evaluated data range; it should not be interpreted as a universal property of the model.

---

## Historical Example: June 2024

Using information available through September 1, 2024, LaborLens identified:

```text
episode:
    2024-06-01 .. 2024-06-01

type:
    broad_contraction

score:
    -0.461

confidence:
    0.843
```

Supporting signals included:

```text
PAYEMS   -0.85
UNRATE   -0.66
ICSA     -0.62
JTSHIR   -0.33
```

Release-aware replay showed that the episode was not detectable through July 25.

On July 30, new JOLTS information associated with `JTSHIR` and `JTSJOL` entered the information set and the episode became detectable.

Its score subsequently moved from approximately:

```text
-0.446
```

to:

```text
-0.461
```

while the claim type and episode boundaries remained unchanged.

This is the type of distinction that final-vintage-only analysis cannot recover.

---

## CLI

LaborLens exposes the research pipeline through a Typer CLI.

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

## Installation

### Requirements

- Python 3.11+
- Docker
- FRED API key

Clone the repository and create a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install LaborLens with development dependencies:

```bash
pip install -e ".[dev]"
```

---

## Configuration

Create a `.env` file containing the configuration required by `laborlens/config.py`, including your FRED API key and ClickHouse connection settings.

Do not commit API keys.

The repository `.gitignore` should keep `.env` outside version control.

---

## Start ClickHouse

```bash
docker compose up -d
```

Check the container:

```bash
docker ps
```

The included Compose configuration exposes:

```text
HTTP:   localhost:8123
Native: localhost:9000

Database: laborlens
User:     default
```

The schema in:

```text
migrations/001_init.sql
```

is loaded through the ClickHouse initialization directory.

---

## Development

Run the test suite:

```bash
pytest -q
```

Run static checks:

```bash
ruff check .
```

Format the repository:

```bash
ruff format .
```

Run the complete validation sequence:

```bash
ruff format .
ruff check .
pytest -q
```

At the current development checkpoint:

```text
64 tests passed
```

covering the statistical pipeline, research layer, writer verification, vintage handling, replay evaluation, and historical backtesting.

---

## Repository Structure

```text
laborlens/
│
├── analysis/
│   ├── divergence.py
│   ├── features.py
│   └── regime.py
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

migrations/
└── 001_init.sql

tests/
├── test_backtest.py
├── test_claims.py
├── test_divergence.py
├── test_episodes.py
├── test_evidence.py
├── test_features.py
├── test_fred.py
├── test_regime.py
├── test_replay.py
├── test_research_bundle.py
├── test_research_pipeline.py
├── test_vintage_backfill.py
└── test_writer.py
```

---

## Design Principles

LaborLens follows several constraints intentionally.

**Point-in-time correctness over retrospective convenience.**  
Historical analysis should use the information that actually existed at the time.

**Structured evidence before prose.**  
The research pipeline decides what is supported before the writer generates an article.

**Deterministic numerical grounding.**  
Numbers and dates in generated research are checked against structured evidence.

**Revisions are part of the problem.**  
Economic revisions are modeled rather than discarded.

**Evaluate disappearing conclusions.**  
Backtests include real-time episode families that later vanish instead of evaluating only surviving final-state episodes.

**Separate detection from causation.**  
LaborLens identifies statistical co-movement and regimes. It does not infer economic causality from those relationships alone.

---

## Limitations

LaborLens is an experimental research system, not a forecasting or trading model.

Several limitations remain:

- the current signal universe contains a small set of labor-market indicators;
- historical results depend on available FRED/ALFRED vintage coverage;
- episode-family matching is an analytical definition rather than economic ground truth;
- detection latency partly reflects official publication schedules;
- the regime score measures standardized statistical movement rather than economic magnitude in natural units;
- historical persistence does not establish predictive validity;
- detected co-movement does not establish causality;
- the current evaluation sample contains relatively few final-state episodes under some parameter configurations.

Backtest statistics should therefore be interpreted as diagnostics of **revision robustness and historical behavior**, not estimates of investment performance or forecasting accuracy.

---

## Research Questions

LaborLens is designed to make several questions experimentally testable:

1. How early can broad labor-market regime changes be detected using only contemporaneously available information?
2. How strongly do later economic revisions alter those conclusions?
3. Which indicators cause a regime to cross the detection threshold?
4. How frequently do real-time episodes disappear from the final revised historical record?
5. How does normalization horizon affect responsiveness versus revision stability?
6. Which conclusions remain stable across both data vintages and model configurations?

---

## Future Work

Potential extensions include:

- expanding the economic indicator universe;
- automated parameter sweeps;
- rolling out-of-sample evaluation;
- richer episode-family matching;
- release-specific attribution and ablation analysis;
- uncertainty calibration;
- additional regime definitions;
- structured JSON research exports;
- visualization of vintage trajectories;
- automated research reports and dashboards.

---

## Tech Stack

**Python · ClickHouse · FRED/ALFRED · Docker · Typer · Pydantic · HTTPX · Pytest · Ruff**

Optional experimental generation:

**Ollama / local language models**

---

## Disclaimer

LaborLens is a research and engineering project.

Its outputs are statistical analyses of economic data and should not be interpreted as financial, investment, policy, or employment advice.
