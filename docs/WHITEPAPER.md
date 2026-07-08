# SiteWatch AI 2.0 — Scientific Methodology Whitepaper

**Statistically validated Earth intelligence.** Version 2.0 — July 2026.

## 1. The problem we solve

The Earth-observation industry has a trust problem. Monitoring products routinely
over-alert because single-date optical comparisons confuse *seasonal phenology*
(leaf drop, dry seasons, snow) with *real change*, and go blind whenever clouds
cover a site. Published false-positive rates for global change products reach 13%,
and buyers now demand decision-ready intelligence rather than raw imagery.
SiteWatch AI 2.0 addresses this directly: **every alert ships with a statistical
confidence score and a full, auditable evidence trail.**

## 2. Methodology

All methods are grounded in the standard scientific literature: Lillesand, Kiefer &
Chipman, *Remote Sensing and Image Interpretation*, 7th ed. (Wiley, 2015) [L&K];
Richards & Jia, *Remote Sensing Digital Image Analysis*, 4th ed. (Springer) [R&J];
Vyas et al. (eds.), *Application of Machine Learning in Earth Sciences* (Springer)
[MLES]; Zhang et al., *Dive into Deep Learning* [D2L].

### 2.1 Pixel-level preprocessing (L&K §7.2)

Sentinel-2 L2A surface reflectance is masked per pixel using the s2cloudless cloud
*probability* layer joined with the Scene Classification Layer (clouds, cirrus,
shadows), plus a dark-NIR shadow test — replacing v1's scene-level cloud
percentage filter. This alone removes a major source of spurious deltas.

### 2.2 Harmonic seasonal baseline (L&K §7.19)

For each pixel we fit a harmonic regression over a multi-year baseline:

`NDVI(t) = a₀ + a₁t + Σₖ [bₖ cos(2πkt) + cₖ sin(2πkt)]`, k = 1..2

New observations are scored as standardized anomalies
`z = (observed − predicted) / RMSE`. A winter NDVI dip that the model predicts
produces z ≈ 0 — **seasonal change is expected, not alerted.** |z| ≥ 2
corresponds to ~95% statistical confidence of a real departure.

### 2.3 Change Vector Analysis with adaptive thresholds (L&K §7.18)

Bi-temporal deltas are computed across 8 spectral indices (NDVI, NDBI, NDWI,
NDMI, BSI, SAVI, EVI, NBR). Change magnitude is the CVA norm in index space;
change *direction* is classified against physical archetypes (construction,
vegetation loss/gain, water gain/loss) by cosine similarity. Thresholds are
scene-adaptive (μ + kσ of the change image) — no hard-coded magic numbers.

### 2.4 Multi-evidence confirmation

An alert requires: (1) CVA magnitude above the adaptive threshold, (2) agreement
of ≥ 2 independent indices, each exceeding its own μ + kσ, and — where
configured — (3) confirmation on consecutive acquisitions (the practice used by
RADD/GFW deforestation alerting to suppress false positives).

### 2.5 All-weather SAR corroboration (L&K §6)

Sentinel-1 C-band SAR (VV, IW mode) is speckle-filtered and compared by
log-ratio between epochs. SAR sees through cloud and darkness; agreement between
optical and radar evidence raises alert confidence, disagreement lowers it. This
removes the optical-blindness failure mode in tropical and monsoon regions.

### 2.6 Machine-learning land cover with *published* accuracy (L&K §7.17, MLES)

Land-use/land-cover maps use a Random Forest (100 trees) trained on ESA
WorldCover strata with a leakage-safe 70/30 hold-out split. Every classification
returns its **error matrix, overall accuracy, Cohen's kappa, and per-class
producer's/user's accuracies** — the formal accuracy-assessment protocol.
We report accuracy with every product because unvalidated maps are marketing,
not science.

### 2.7 Per-alert confidence fusion

Independent evidence — anomaly |z|, CVA magnitude percentile, index agreement,
temporal confirmations, SAR corroboration — is fused by a monotone logistic
model into a single 0–1 confidence score with an evidence trail. Users can
filter alerts by confidence; auditors can inspect exactly why an alert fired.

### 2.8 Grounded AI analyst

The LLM layer answers questions **only from verified numeric analysis facts**
(deterministic engine + validation harness), with contradiction checks — an AI
analyst, not a chatbot. Natural-language in, auditable intelligence out.

## 3. Verification

The mathematical core (harmonic fitting, CVA, thresholds, error matrices, kappa,
confidence fusion) is implemented dependency-free and covered by a 20-test unit
suite (`tests/test_science_engine.py`), including the key property tests:
*a model-predicted seasonal dip yields z ≈ 0 (no alert)* and *a genuine clearing
event yields z < −2 (alert)*.

## 4. Why this wins

| Industry pain | SiteWatch AI 2.0 answer |
|---|---|
| Seasonal false positives erode trust | Harmonic baseline: phenology is modeled, not alerted |
| Clouds blind optical monitoring | Sentinel-1 SAR corroboration, all-weather |
| Unvalidated "black-box" analytics | Error matrix + kappa published with every map |
| Raw data ≠ decisions | Grounded AI analyst over verified facts |
| No way to triage alerts | Calibrated per-alert confidence scores |
