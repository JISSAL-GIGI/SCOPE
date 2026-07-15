# Live End-to-End Verification (2026-07-15)

Real production run against the full stack (React UI → FastAPI → Google Earth Engine
→ local LLaMA via Ollama). Nothing simulated.

## Scan: Kochi, Kerala, India (9.9711 N, 76.2846 E)

| Item | Value |
|---|---|
| Sensor | Sentinel-2 MSI, 10 m |
| Baseline | 2026-04-20 (cloud 3.6%) |
| Current | 2026-07-14 (cloud 26.8% — monsoon) |
| Surface change | 20.06% of area (13,479 / 67,195 pixels) |
| Dominant signal | Water increase (NDWI +0.096) — consistent with monsoon onset |
| Processing time | 125.7 s |

Imagery produced by the scan (see `docs/proof/`):
true-color pairs, NIR & SWIR false-color pairs, NDWI water masks + gain/loss map,
NDVI change map, binary change mask.

## Live LLM check

The in-app assistant (local LLaMA via Ollama, no canned answers) was asked a novel
operational question about monsoon-season monitoring; it recommended SAR-based
change detection with correct physical reasoning (cloud penetration, day/night
operation, multimodal fusion) and asked sensible follow-ups — verified in the
running UI.

## Geofencing check

Site creation with geocoded location resolution and GeoJSON boundary polygon
verified in the running UI (grid + map views).

## v2.1 live run — SAR + alert triage (2026-07-15, background scan pipeline)

First fully verified end-to-end run of the production "Scan Now" pipeline
(previously broken infrastructure: missing celery, database split-brain — both fixed):

| Item | Value |
|---|---|
| Scan | `cefc603b` on site "Kochi Port Monitor" (geofenced, GeoJSON boundary) |
| Optical change | 18.8% (Sentinel-2) |
| SAR change | 16.5% (Sentinel-1, 6 images, ±3 dB log-ratio) |
| Cross-sensor verdict | **Radar CONFIRMS optical** |
| Radar water extent | decrease, −1.5 pct points |
| Calibrated confidence | 92.6% (SAR-boosted, 1-decimal honest reporting) |

SAR proof imagery in `docs/proof/`: `kochi_sar_baseline.jpg`,
`kochi_sar_current.jpg`, `kochi_sar_change_map.png` (green = backscatter
increase, red = decrease), `kochi_sar_water_current.png`.

Known limitation: the legacy compiled API whitelists response fields, so the
chat UI shows SAR results in report text (not as a dedicated image grid);
the full SAR payload is stored in the scan record and available to the v2 API.
