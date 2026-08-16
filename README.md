# LaborLens

**Revision-aware, point-in-time labor-market research with grounded AI.**

LaborLens is a research system for studying labor-market regime changes under the information constraints that actually existed at the time.

Its central question is:

> **Would an economic conclusion have been detectable using only information that was actually available at that point in history?**

Historical economic datasets are revised. Looking backward with today's values can make a signal appear earlier, stronger, or more stable than it would have appeared to a researcher operating in real time.

LaborLens addresses this by reconstructing historical information states from release vintages, detecting multivariate labor-market regimes, validating evidence, adding geographically specific QCEW context, replaying conclusions through successive information states, and exposing the resulting research through deterministic and grounded language interfaces.

The language model is deliberately downstream of the research engine: it explains validated research objects rather than independently deciding what happened in the labor market.

---

## Core Idea

Economic time series have at least two relevant notions of time:

```text
observation date
      ≠
information availability date
```

A payroll observation describing June may be published in July and revised again later.

A conventional historical analysis often asks:

```text
What does the historical dataset say now?
```

LaborLens instead asks:

```text
What could a researcher have concluded
using only information available by date t?
```

That distinction drives the architecture of the project.

---

## Example: June 2024

For a detected June 2024 labor-market contraction episode, the research engine produced a final regime score of approximately:

```text
-0.461
```

with confidence around:

```text
84.3%
```

The strongest standardized supporting contributions included:

| Series | Indicator | Standardized contribution |
|---|---|---:|
| PAYEMS | Total nonfarm payroll employment | -0.850 |
| UNRATE | Unemployment rate | -0.659 |
| ICSA | Initial unemployment claims | -0.622 |
| JTSHIR | Hires rate | -0.326 |

These are **standardized directional contributions**, not percentage changes in employment or the underlying series.

The more interesting result comes from replaying the episode through historical information states.

```text
target observation     2024-06-01
previous state         2024-07-25
first detected         2024-07-30
detection latency      59 days
release attribution    JTSHIR, JTSJOL

initial score          -0.446
final score            -0.461
absolute revision      0.0147

survival after detection
                       100%

claim-type flips       0
```

The system therefore distinguishes:

```text
when an economic condition occurred
```

from:

```text
when enough evidence existed to detect it
```

---

# Architecture

```text
                 FRED / ALFRED
              observations + vintages
                       |
                       v
              Vintage-Aware Ingestion
                       |
                       v
                   ClickHouse
             observations / releases
                  / provenance
                       |
                       v
            Point-in-Time Reconstruction
                data known as of t
                       |
                       v
                 Research Engine
                       |
        +--------------+--------------+
        |              |              |
        v              v              v
     Regimes          QCEW          Evidence
     Episodes        Context        + Skeptic
        |              |              |
        +--------------+--------------+
                       |
                       v
                 Research Bundle
                       |
          +------------+------------+
          |            |            |
          v            v            v
       Replay      Backtesting    Grounded
       Engine       + Revision     Answers
                     Analysis
                       |
                       v
               CLI / Minimal API
```

The architecture intentionally separates:

```text
data
  |
  v
research inference
  |
  v
validation
  |
  v
language generation
```

The writer does not decide what the evidence means.

The research engine does.

---

# Research Pipeline

A typical research path is:

```text
raw observations
      |
      v
point-in-time reconstruction
      |
      v
feature engineering
      |
      v
direction normalization
      |
      v
rolling standardization
      |
      v
multivariate regime score
      |
      v
candidate claims
      |
      v
episode construction
      |
      v
supporting + opposing evidence
      |
      v
skeptic validation
      |
      v
QCEW cross-sectional context
      |
      v
historical context
      |
      v
provenance
      |
      v
research bundle
      |
      v
deterministic / grounded answer
```

---

## 1. Vintage-Aware Economic Data

LaborLens stores economic observations together with release-vintage information.

Conceptually:

```text
series_id
observation_date
vintage_date
value
```

This permits questions such as:

```text
What PAYEMS value was available
to a researcher on 2024-07-01?
```

rather than only:

```text
What value does the current
historical dataset report?
```

This is the foundation for point-in-time reconstruction.

---

## 2. Feature Engineering and Regime Detection

LaborLens derives features such as:

```text
level
first difference
acceleration
rolling mean
rolling variance
rolling z-score
```

Signals are direction-normalized before aggregation.

For example, increasing unemployment and decreasing hiring can both indicate weakening even though their numerical directions differ.

The system then searches for coordinated movement across multiple labor-market indicators rather than treating any single series as sufficient evidence.

```text
PAYEMS -----+
UNRATE -----|
ICSA -------+---> normalized signals
JTSHIR -----|
JTSJOL -----+
                  |
                  v
              regime score
                  |
                  v
            candidate claim
```

---

## 3. Episode Construction

Adjacent candidate states can be grouped into research episodes.

Instead of treating:

```text
May     contraction
June    contraction
July    contraction
August  contraction
```

as four unrelated observations, LaborLens can represent them as a single evolving episode.

Each episode records structured information including its temporal range, representative score, confidence, claim type, evidence, and provenance.

---

## 4. Evidence and Skeptic Validation

Research conclusions are converted into structured evidence bundles before natural-language generation.

The engine preserves:

```text
supporting indicators
counter-signals
standardized contributions
historical comparisons
provenance
```

Candidate research then passes through deterministic skeptic logic.

This design prevents the narrative layer from first choosing a story and then selecting evidence that supports it.

---

# QCEW Cross-Sectional Research

LaborLens extends the macro time-series analysis with BLS Quarterly Census of Employment and Wages context.

This provides geographically specific industry evidence such as:

```text
local employment
local year-over-year growth
national year-over-year growth
relative growth gap
location quotient
industry strength
```

The QCEW pipeline includes:

```text
QCEW ingestion
      |
      v
dimension resolution
      |
      v
release availability
      |
      v
local / national comparison
      |
      v
candidate industry claims
      |
      v
QCEW skeptic
      |
      v
cross-sectional research context
```

Release availability matters here as well.

For a historical `as_of` query, LaborLens selects a QCEW quarter that was actually available by that information date rather than leaking later quarterly releases into the analysis.

This lets macro regime evidence and industry-level context share the same point-in-time principle.

---

# Release-Aware Replay

Replay repeatedly reconstructs the information available at historical dates and reruns the research process.

For example:

```text
2024-07-03    not detected
2024-07-05    not detected
2024-07-11    not detected
2024-07-18    not detected
2024-07-25    not detected
2024-07-30    FIRST DETECTED
2024-08-01    detected
2024-08-02    detected
...
2024-09-01    detected
```

The replay system can measure:

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

The result is an empirical view of **research stability under information arrival and revision**.

---

# Anti-Survivorship Backtesting

Final revised datasets create another evaluation problem.

Suppose a signal appeared in real time but disappeared after later revisions.

A backtest performed only against the final historical dataset cannot observe that signal.

LaborLens therefore tracks real-time episode families in addition to final-state episodes.

In one historical experiment covering 2019 through September 2024 with a 24-month window:

```text
real-time episode families       3
persistent families              2
disappeared families             1

persistence rate              66.7%
revision disappearance rate   33.3%
```

The revision disappearance rate is intentionally **not** called a false-discovery rate.

A signal disappearing after data revisions does not prove that the original real-time inference was statistically false.

---

## Window Sensitivity

A historical window experiment produced:

| Window | Final Episodes | Real-Time Families | Persistence | Revision Disappearance | Median Detection Latency |
|---:|---:|---:|---:|---:|---:|
| 12 months | 7 | 11 | 63.6% | 36.4% | 75 days |
| 24 months | 2 | 3 | 66.7% | 33.3% | 62.5 days |
| 36 months | 3 | 3 | 100.0% | 0.0% | 61 days |

The shorter window generated more candidate episodes but also more revision-sensitive signals in this experiment.

These results are descriptive for the evaluated period and do not establish that one window is universally optimal.

---

# Grounded Research Assistant

LaborLens includes a natural-language research interface, but its architecture is intentionally different from a generic data chatbot.

```text
User question
      |
      v
Intent + safety routing
      |
      v
Required research context
      |
      v
Research pipeline
      |
      v
Structured research bundle
      |
      +-- episode
      +-- macro evidence
      +-- QCEW context
      +-- skeptic verdicts
      +-- historical state
      +-- provenance
      |
      v
Grounded answer layer
```

The model is not given raw economic data and asked to invent an interpretation.

Instead:

```text
research engine
      |
      v
validated context
      |
      v
language model
```

---

## Intent Routing

Research questions are routed across intents including:

```text
causal attribution
episode summary
macro evidence
industry weakness
industry strength
industry context
point-in-time analysis
methodology
general research
```

The routing system combines learned semantic classification with deterministic structural rules where mistakes would have larger consequences.

Geographic requirements are also planned before running the research pipeline so QCEW-backed questions cannot silently execute without the necessary geographic context.

---

# Causal Safety

LaborLens is a descriptive research system, not a causal inference engine.

Questions such as:

```text
Did hurricanes cause roofing employment to fall?
```

must therefore not be silently converted into causal conclusions merely because correlated industry or macro evidence exists.

A dedicated causal classifier acts as a safety boundary before ordinary research-intent routing.

Cross-corpus evaluation of the calibrated causal classifier achieved:

```text
Holdout V1
recall       1.000
precision    0.909

Holdout V2
recall       1.000
precision    1.000

Holdout V3
recall       1.000
precision    1.000

dangerous misroute rate
             0.000 across V1-V3
```

The goal is asymmetric: incorrectly refusing to make a causal claim is preferable to presenting descriptive co-movement as established causation.

---

# Production Routing Benchmark

The frozen production holdout contains 99 questions separate from the router-development corpora.

Measured performance:

```text
cases                    99

intent accuracy          0.980
area accuracy            1.000
routing accuracy         1.000
```

Safety subset:

```text
safety cases             15
causal safety recall     1.000
dangerous misroute rate  0.000
```

General-research subset:

```text
cases                    11
accuracy                 1.000
```

Router latency:

```text
p50    10.11 ms
p95    19.66 ms
p99    33.15 ms
```

The two intent errors were:

```text
episode_summary -> methodology
episode_summary -> point_in_time
```

Both preserved deterministic research execution, so neither produced an unsafe or ungrounded route.

---

# Grounding Benchmark

LaborLens evaluates the final answer layer end to end rather than evaluating only intent classification.

Current grounding benchmark:

```text
cases                              30

request success rate             1.000
answer guard pass rate           1.000
unsupported causal assertion     0.000
numeric misrepresentation rate   0.000
provenance coverage rate         1.000
```

Answer modes:

```text
deterministic research    22
local AI                   8
```

Only questions requiring synthesis are sent through the language model.

In this benchmark:

```text
AI generation rate        0.267
```

Most supported research questions can therefore be answered deterministically from structured research state, while the model is reserved for questions where natural-language synthesis adds value.

Local AI inference is substantially more expensive than routing:

```text
end-to-end
p50     234.57 ms
p95    5545.11 ms
p99   13873.10 ms

AI-only generation
p50    4717.54 ms
p95   13873.10 ms
```

This reinforces the design choice to avoid invoking the model unnecessarily.

---

# Answer Guard

Generated answers pass through a grounding guard designed to catch unsupported output before it reaches the caller.

The evaluation explicitly checks for failure modes including:

```text
unsupported causal assertions
numeric misrepresentation
missing provenance
ungrounded generation
```

If local model generation fails, the system can fall back to deterministic research output rather than returning an unconstrained answer.

---

# Learned Routing Experiments

The repository retains evaluation scripts used to compare routing approaches.

Experiments include:

```text
logistic regression
linear SVM
cosine k-NN
two-stage routing
dedicated causal classification
non-causal multiclass routing
```

Across the non-causal router evaluation, mean performance was:

```text
accuracy    0.877
macro F1    0.881
```

These experiments motivated the final hybrid architecture rather than selecting a classifier based only on aggregate accuracy.

---

# Minimal API

LaborLens retains a small FastAPI boundary for programmatic research queries.

The API is intentionally not treated as a separate product layer.

Core routes:

```text
GET  /health
POST /ask
```

Example request:

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Which indicators contributed most?",
    "start_date": "2024-06-01"
  }' \
  http://localhost:8000/ask
```

The response contains:

```text
answer
mode
model
sources
caveat
```

The API is an interface to the research engine, not the core of the project.

---

# CLI

Most research functionality is available directly through the `laborlens` CLI.

Commands include:

```text
ingest
vintage
as-of
analyze
compare
regime
claims
episodes
review
bundle
article
backfill-vintages
replay-eval
backtest
ingest-qcew
compare-qcew
qcew-claims
```

## Ingest economic data

```bash
laborlens ingest UNRATE \
  --from 2024-01-01
```

## Backfill vintages

```bash
laborlens backfill-vintages PAYEMS \
  --from 2024-01-01 \
  --to 2024-08-31 \
  --vintage-start 2024-01-01 \
  --vintage-end 2024-09-01 \
  --batch-size 100
```

## Run revision-aware backtesting

```bash
laborlens backtest \
  --from 2019-01-01 \
  --to 2024-09-01 \
  --window 24 \
  --min-confidence 0.55 \
  --show-episodes \
  --show-families
```

## Work with QCEW

```bash
laborlens ingest-qcew --help
laborlens compare-qcew --help
laborlens qcew-claims --help
```

---

# Running Locally

## Requirements

- Python 3.11+
- Docker
- FRED API key for live FRED/ALFRED ingestion
- Ollama only if local language-model synthesis is desired

## Installation

```bash
git clone <repository-url>
cd laborlens

python3 -m venv .venv
source .venv/bin/activate

pip install -e .
```

Create an environment file:

```bash
cp .env.example .env
```

Configure at minimum:

```text
FRED_API_KEY=...
```

For local AI synthesis:

```text
LABORLENS_LLM_PROVIDER=ollama
LABORLENS_MODEL=qwen3:8b
OLLAMA_HOST=http://localhost:11434
```

Start the required storage infrastructure according to the repository's Docker configuration, then apply the ClickHouse migrations.

---

# Testing

Run the complete test suite:

```bash
ruff check .
pytest -q
git diff --check
```

Current repository state:

```text
121 passed
```

The project also contains dedicated research evaluations and frozen holdouts rather than relying solely on unit tests.

Examples:

```bash
PYTHONPATH=. python scripts/benchmark_holdout_v4.py
PYTHONPATH=. python scripts/benchmark_grounding.py
PYTHONPATH=. python scripts/evaluate_causal_classifier.py
PYTHONPATH=. python scripts/evaluate_noncausal_router.py
```

---

# Research Principles

LaborLens is built around several constraints.

### 1. Point-in-time correctness

Historical analysis must use information available at the requested information date.

### 2. No revision leakage

Later revisions should not silently improve historical conclusions.

### 3. Release-aware cross-sectional context

QCEW evidence must also respect publication availability.

### 4. Evidence before narrative

Research objects are constructed before natural-language explanation.

### 5. Descriptive evidence is not causal evidence

Correlated labor-market signals do not establish why an event occurred.

### 6. Preserve counter-evidence

Opposing signals are part of the research state rather than discarded because they complicate a narrative.

### 7. Provenance is part of the result

A conclusion without traceable evidence is incomplete.

### 8. Evaluate the system, not just the model

Routing accuracy alone is insufficient. LaborLens separately evaluates causal safety, grounding, provenance, numerical fidelity, replay stability, revision sensitivity, and end-to-end behavior.

---

# What LaborLens Is Not

LaborLens is not:

- a causal inference engine;
- a forecasting model claiming to predict recessions;
- a generic RAG chatbot over economic documents;
- a dashboard built around current revised data;
- an LLM that independently interprets raw macroeconomic series;
- a production trading signal.

It is a **revision-aware research system for reconstructing, testing, and explaining what labor-market evidence supported at a particular information state**.

---

# Current Status

The core research system currently includes:

```text
FRED / ALFRED ingestion
historical vintage storage
point-in-time reconstruction
feature engineering
multivariate regime detection
claim construction
episode construction
evidence extraction
skeptic validation
QCEW ingestion and comparison
release-aware QCEW context
research bundles
release-aware replay
revision analysis
anti-survivorship backtesting
window sensitivity analysis
learned intent routing
causal safety classification
grounded deterministic answers
optional local-LLM synthesis
answer grounding guards
frozen routing holdouts
grounding benchmarks
CLI research workflows
minimal FastAPI interface
```

The project intentionally does not require a frontend or public demo application. Its primary artifact is the research engine and the reproducible evaluation around it.

---

# Why This Matters

Macroeconomic research is often evaluated with information that was not actually available when the event occurred.

That can introduce a subtle form of look-ahead bias.

LaborLens treats the historical information set itself as part of the experiment.

Instead of asking only:

> What happened?

it asks:

> What evidence existed at the time?

> When did that evidence become sufficient?

> Which releases changed the conclusion?

> Did the conclusion survive later revisions?

> Which local industries strengthened or contradicted the aggregate signal?

> Which parts of the conclusion are descriptive, and which would require causal evidence that the system does not have?

That turns a historical labor-market analysis into a reproducible **point-in-time research problem** rather than a retrospective narrative.

---

## License

See the repository license for usage terms.
