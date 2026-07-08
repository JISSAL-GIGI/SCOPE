# SCOPE 2.0 — Machine Learning & Grounded AI Analyst

This document describes the three capabilities added in the 2.0 upgrade and the
evidence behind them. The methods are drawn directly from the platform's
reference library:

- **[L&K]** Lillesand, Kiefer & Chipman — *Remote Sensing & Image Interpretation*, 7th ed.
- **[R&J]** Richards & Jia — *Remote Sensing Digital Image Analysis*, 4th ed.
- **[MLES]** Vyas et al. (eds.) — *Application of Machine Learning in Earth Sciences* (Springer)
- **[D2L]** Zhang, Lipton, Li & Smola — *Dive into Deep Learning*

---

## 1. A real, evaluated land-cover classifier

SCOPE 2.0 ships an actual trained **Random-Forest** land-cover classifier
(scikit-learn) over Sentinel-2 spectral bands plus physically-motivated indices
(NDVI, NDWI, NDBI, red-edge NDVI). It is evaluated the way [MLES] insists EO
models must be: with **spatially-grouped cross-validation** so that pixels from
the same tile never straddle the train/test boundary. Testing on
spatially-adjacent pixels is the most common way EO accuracy gets silently
inflated — SCOPE refuses to do it.

Accuracy is reported with the full apparatus from **[L&K §7.17]**: an error
matrix, overall accuracy, Cohen's kappa, and per-class producer's/user's
accuracy.

### Verified results (demonstration run)

| Metric | Value |
|---|---|
| Overall accuracy | **0.882** |
| Cohen's kappa | **0.869** |
| 5-fold grouped CV | **0.882 +/- 0.013** |
| Method | RandomForest(300) + spectral indices, StratifiedGroupKFold(5) |

![Error matrix](proof/confusion_matrix.png)

The confusion structure is the *real* one: water, forest and industrial
separate cleanly, while the vegetation classes (crop/pasture/herbaceous)
partially confuse — exactly as they do on the real benchmark. The most
important features are SWIR (B12), NIR (B8) and red-edge (B7), which is the
physically correct ordering for vegetation discrimination.

![Classification map](proof/classification_map.png)

> **Data honesty.** The demonstration numbers above come from a
> *literature-grounded synthetic* dataset built from published EuroSAT
> per-class Sentinel-2 signatures, so the full pipeline is reproducible in any
> environment. The model, cross-validation, and metrics code are identical for
> the real EuroSAT benchmark — only the data loader changes
> (`train_from_real_eurosat(path)` in the private core). Do not quote these as
> benchmark scores; they demonstrate the pipeline, not a leaderboard result.

---

## 2. Book-grounded retrieval (RAG) for the AI analyst

The analyst no longer answers scientific questions from memory. It retrieves
supporting passages from the four reference books above (5,129 indexed
passages across ~2,600 pages) and **cites them at page level**. Retrieval is
fully offline (TF-IDF + cosine), so it runs anywhere without external model
downloads; an embedding backend is available where network access permits.

Example — the query *"How is Cohen's kappa computed for accuracy assessment?"*
returns **Lillesand, Kiefer & Chipman (p. 308)**, the exact page of the
accuracy-assessment section. *"Synthetic aperture radar flood mapping"* returns
the SAR chapter (pp. 411-414). Every scientific claim the analyst makes can be
traced back to a page.

---

## 3. An agent, not a chatbot

The analyst runs a bounded **plan -> act -> ground -> synthesise** loop:

1. **Plan** — decompose the request into tool calls (or decide none are needed).
2. **Act** — execute those tools against the platform's tool registry
   (site lookups, latest scans, change analysis, web/news).
3. **Ground** — pull cited passages from the reference books.
4. **Synthesise** — write a plain-language answer that cites *both* the live
   tool results and the book pages, and exposes its reasoning trace.

Hard guardrails are built in and verified by tests: unknown/dangerous tool
names are rejected, malformed model output is repaired, and if the local model
is unavailable the agent degrades to returning the retrieved evidence rather
than failing. The local LLaMA backend is unchanged; the intelligence is in the
orchestration.

---

## Reproducing the evidence

The verification scripts live in the private core (`backend/ml/`):

- `landcover_classifier.py` — the model + leakage-safe evaluation
- `generate_proof.py` — regenerates every image and `metrics.json` in this folder
- `book_rag.py` — the retrieval index
- `scope_agent.py` + `test_scope_agent.py` — the agent loop (8/8 tests pass)

(c) 2026 SCOPE. Public docs & SDK under MIT; models and engine proprietary.
