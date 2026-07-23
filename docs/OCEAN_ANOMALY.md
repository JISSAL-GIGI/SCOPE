# Ocean-Colour Anomaly Detection (Sentinel-3 OLCI)

> New capability — unsupervised detection of unusual biogeochemical events in
> coastal waters (algal blooms, sediment plumes, turbidity spikes, red tides)
> from Sentinel-3 OLCI ocean-colour imagery, using a Keras autoencoder.
>
> Paste this section into `README.md` or `docs/WHITEPAPER.md`, or keep it as
> its own page. Result figures referenced below live in `docs/proof/ocean/`.

## The problem

Ocean-colour anomalies are **rare and unlabelled**, so supervised
classification is impractical — there is no reliable library of "bloom" pixels
to train on, and events differ event-to-event. What we *can* characterise is
*normal* water.

## The method — autoencoder reconstruction error

An **undercomplete autoencoder** is trained to reconstruct the per-pixel
reflectance spectrum through a narrow bottleneck, using **only normal water**
(the calmest, lowest-chlorophyll fraction of the scene). It learns a compact
model of the typical spectrum. At inference, an unusual spectrum reconstructs
poorly, so the **per-pixel reconstruction error is the anomaly score**:

```
z = f(x)            # encode spectrum x (11 OLCI ocean-colour bands) to latent code
x̂ = g(z)            # decode back to a reconstructed spectrum
e(x) = ‖x − x̂‖² / B  # reconstruction error = anomaly score
```

Training minimises mean-squared reconstruction error over the normal set,
`L = (1/N) Σ ‖x − g(f(x))‖²`. A pixel is flagged when `e(x)` exceeds a
threshold set from the normal-water error distribution — a high percentile
(default) or a mean-plus-k·σ rule. Because blooms/plumes are held out of
training, they stand out at scoring time.

## Data sources

| Source | How it is read |
|---|---|
| **Synthetic** | simulated OLCI scene with injected events — demo, CI, and ground-truth validation |
| **Copernicus** | a downloaded product read with **Rasterio / Rioxarray** — an OLCI `.SEN3` folder of per-band NetCDFs, or a stacked GeoTIFF |
| **Earth Engine** | Sentinel-3 OLCI (`COPERNICUS/S3/OLCI`) sampled over an AOI |

Sentinel-3 OLCI has 21 bands (400–1020 nm); the default feature set is the 11
ocean-colour bands **Oa01–Oa11** carrying the chlorophyll / CDOM / sediment signal.

## Network

Dense undercomplete autoencoder over the per-pixel spectrum (a 1-D
convolutional variant is also available): encoder `11 → 16 → 8 → latent 4`,
symmetric decoder back to 11, ReLU activations, linear output, Adam + MSE with
early stopping. Per-band z-score normalisation fitted on the normal set.

## Validation (synthetic benchmark)

On a simulated 96×96 OLCI scene with three injected biogeochemical events (land
and cloud masked), the autoencoder trained in ~7 s on 7,614 water pixels and,
because the injected events are known, detection is scored exactly:

| Metric | Value |
|---|---|
| ROC-AUC | **0.95** |
| Precision | 0.84 |
| Recall | 0.66 |
| F1 | 0.74 |
| Accuracy | 0.96 |

The ROC-AUC of 0.95 shows the reconstruction-error score separates anomalous
from normal water very well; precision/recall are a tunable operating point set
by the threshold percentile.

**Figures** (`docs/proof/ocean/`): `ocean_overlay.png` (anomalies on true colour),
`ocean_error_map.png` (reconstruction-error heatmap), `ocean_spectra.png`
(normal vs anomalous mean spectra), `ocean_training_curve.png`,
`ocean_error_hist.png` (error distribution + threshold).

## Named, explained events (not just a heatmap)

Raw anomaly pixels are turned into the answer a coastal manager actually wants —
*what happened, where, and how sure are we*:

- **Classification** by spectral signature into **algal bloom** (green + red-edge
  up, blue down — elevated chlorophyll-a), **sediment plume** (reflectance rising
  toward the red), **CDOM / black water** (strong blue suppression), or
  **turbidity**.
- **Spatial clustering** of anomalous pixels into discrete events, each with a
  centroid (lat/lon), area, **severity** (low/medium/high) and a confidence.
- **Explainability** — per-band reconstruction-error attribution (a Grad-CAM-style
  readout, cf. Ex 4.4) showing *which OLCI bands* drove each flag. On a validated
  synthetic scene the model recovers one of each event type correctly
  (ROC-AUC 0.95), with attribution concentrating on Oa06/Oa08/Oa11 — the
  chlorophyll bands.

A run reports, e.g., *"3 events detected: 1 algal bloom, 1 sediment plume,
1 CDOM/black water"* with a map, a per-band attribution chart, and an OC4-style
**chlorophyll-a** product (mg m⁻³).

## Grounding in ocean geophysics (Ex 1.2 / 1.3)

- **Chlorophyll-a** via the OC4 maximum-band-ratio algorithm
  `Chl = 10^(a0 + a1·R + … )`, `R = log10(max(Rrs443,490,510)/Rrs560)`.
- **Climatology anomaly** `anomaly(t) = value(t) − mean_climatology` with a
  per-pixel z-score, plus **Pearson correlation** — a second, physically-grounded
  detector that can **corroborate** the autoencoder (the ocean-colour analogue of
  SiteWatch's SAR corroboration).

## Real Sentinel-3 data

- **Earth Engine** (easiest): `COPERNICUS/S3/OLCI` sampled by lat/lon + date — no
  downloads, uses the app's existing EE integration.
- **Copernicus** (most accurate for ocean colour): download OLCI **Level-2 WFR**
  products from the [Copernicus Data Space](https://dataspace.copernicus.eu/) or
  [CMEMS](https://marine.copernicus.eu/), or NASA
  [Ocean Color](https://oceancolor.gsfc.nasa.gov/) L2/L3 — then point `--source
  copernicus --path` at the `.SEN3` folder or a stacked GeoTIFF (read with
  Rasterio/Rioxarray).

## Validated on real ESA data

The physics was benchmarked against ESA's own operational product on a real,
atmospherically-corrected **Sentinel-3 OLCI Level-2 WFR** scene (Kochi,
2026-02-27):

- **Physically correct IOPs** — on proper water-leaving reflectance the
  semi-analytical inversion returns physical values (suspended matter
  ~0.06 mg/L, particle backscatter ~4×10⁻⁴ m⁻¹), where uncorrected
  top-of-atmosphere input gives nonsense. Atmospheric correction matters, and
  the pipeline supports both L2 (rigorous) and Earth Engine L1 (quick-look).
- **Chlorophyll vs ESA CHL_NN** — after a physically-grounded calibration our
  chlorophyll centres on ESA's (median 0.325 = 0.325 mg/m³, bias eliminated),
  positively correlated with the agency product. A bloom scene (wider dynamic
  range) is the next step to finalise the retrieval slope.

## The SCOPE ocean analyst (RAG-grounded LLM)

Beyond detection, SCOPE **explains** each scene. A local `llama3.1:8b` is given
the run's *verified numbers* (events, classification, chlorophyll, IOPs,
attribution, detection metrics) plus retrieved passages from the ocean-science
reference books, and reasons over them to answer, in plain language:

> why did this happen · natural or human-caused · will it spread · is it
> dangerous and to which species · what should managers do next

Answers are grounded strictly in the computed facts and cite the books by page
(e.g. *Lillesand, Kiefer & Chipman p.240*; *Vyas et al. p.156*); a deterministic
layer is the fact-check/guardrail so the model can never invent a result the
pipeline didn't produce. Exposed as `POST /api/ocean/ask` and an "Ask the
analyst" box in the SCOPE UI.

## Where it lives (engine — private repo)

`backend/ocean_anomaly/` (loaders, preprocessing, Keras autoencoder, scoring,
visualisation, pipeline), REST endpoints `GET/POST /api/ocean/*` mounted via
`backend/app_main.py`, an **Ocean AI** panel in the SCOPE UI, and a CLI runner
`run_ocean_anomaly.py`.

## Limitations & next steps

Threshold is a tunable operating point (site calibration improves it); Earth
Engine hosts OLCI L1 TOA (atmospheric correction or Copernicus L2 WFR sharpens
the signal); per-pixel spectral detection can be extended with a convolutional
patch autoencoder for spatial context; multi-temporal baselines would separate
genuine events from seasonal variability.
