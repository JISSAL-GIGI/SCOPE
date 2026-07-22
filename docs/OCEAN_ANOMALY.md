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
