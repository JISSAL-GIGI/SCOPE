# All-Weather Monitoring & False-Alarm Suppression (v2.1)

SCOPE v2.1 closes the two costliest gaps in operational Earth-observation monitoring.

## Gap 1 — Optical monitoring goes blind in clouds

During monsoon seasons, cloud cover over tropical sites reaches 90%+; peer-reviewed
assessments show optical-only pipelines lose ~25% of surface-water observations in
these periods, and operational services (UNOSAT, Copernicus EMS) only activate
per-event, leaving systematic gaps.

**SCOPE's answer: Sentinel-1 C-band SAR corroboration, fused into every scan.**

- Multi-image median composites (speckle suppression) for baseline & current epochs
- dB log-ratio change detection (±3 dB threshold)
- Radar water extent via VV < −17 dB open-water backscatter
- Cross-sensor verdict on every report: radar **confirms** or **contradicts** the
  optical signal — clouds cannot stop the analysis

## Gap 2 — Alert fatigue from seasonal false alarms

The dominant operational cost in monitoring is humans reviewing alerts that are
"expected, benign, repetitive." Most platforms alert on raw change magnitude.

**SCOPE's answer: per-site seasonal anomaly triage.**

Every detected change is tested against the site's *own* multi-year, same-season
statistical baseline (per-index z-scores across NDVI/NDBI/NDWI/NDMI):

| Alert level | Meaning |
|---|---|
| 🟢 `quiet` | Below alerting threshold |
| 🟡 `seasonal_normal` | Matches multi-year seasonal baseline — **alert suppressed** |
| 🟠 `low_trust` | Sensors disagree — verify before acting |
| 🟠 `watch` | Moderate anomaly evidence — monitor next pass |
| 🔴 `anomaly_alert` | Statistically abnormal vs. site history (|z| ≥ 2), radar-corroborated |

## Gap 3 — Uncalibrated confidence numbers

Confidence scores are now data-quality weighted (cloud %, temporal gap, season match,
multi-index agreement) and adjusted by independent SAR corroboration: agreement raises
confidence, disagreement on a cloudy scene lowers it. Reported to one decimal, with an
honest band (high/medium/low). No fabricated precision.

## Methodology sources

Statistical change detection, error matrices and seasonal analysis follow
Lillesand & Kiefer (*Remote Sensing and Image Interpretation*) and Richards & Jia
(*Remote Sensing Digital Image Analysis*); SAR practice follows ESA Sentinel-1
GRD processing conventions.
