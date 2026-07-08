"""
SiteWatch AI — Public Python SDK
================================
Thin client for the SiteWatch AI API. The analytics engine itself is
proprietary; this SDK gives you full programmatic access to results.

    pip install requests

    from sitewatch_client import SiteWatch
    sw = SiteWatch("https://api.sitewatch.ai", token="...")
    r = sw.analyze_change(lat=12.7974, lon=80.2232,
                          before=("2025-01-01", "2025-03-01"),
                          after=("2026-01-01", "2026-03-01"))
    print(r["change_label"], r["confidence_label"], r["confidence"])

License: MIT (this SDK only).
"""

from __future__ import annotations

from typing import Dict, Optional, Tuple

import requests

__version__ = "2.0.0"


class SiteWatchError(RuntimeError):
    pass


class SiteWatch:
    """Client for SiteWatch AI v2 endpoints."""

    def __init__(self, base_url: str, token: Optional[str] = None, timeout: int = 300):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._session = requests.Session()
        if token:
            self._session.headers["Authorization"] = f"Bearer {token}"

    def _post(self, path: str, payload: Dict) -> Dict:
        r = self._session.post(f"{self.base_url}{path}", json=payload, timeout=self.timeout)
        if r.status_code >= 400:
            raise SiteWatchError(f"{r.status_code}: {r.text[:300]}")
        return r.json()

    def health(self) -> Dict:
        r = self._session.get(f"{self.base_url}/v2/health", timeout=30)
        return r.json()

    def analyze_change(
        self,
        lat: float,
        lon: float,
        before: Tuple[str, str],
        after: Tuple[str, str],
        buffer_km: float = 2.0,
        k_sigma: float = 2.0,
        use_sar: bool = True,
        geojson: Optional[Dict] = None,
    ) -> Dict:
        """Statistically validated change detection.

        Returns change label, CVA magnitude, z-score, changed area (ha),
        SAR corroboration, and a calibrated 0-1 confidence score with the
        full evidence trail.
        """
        return self._post("/v2/analyze/change", {
            "latitude": lat, "longitude": lon, "buffer_km": buffer_km,
            "geojson": geojson,
            "before_start": before[0], "before_end": before[1],
            "after_start": after[0], "after_end": after[1],
            "k_sigma": k_sigma, "use_sar": use_sar,
        })

    def classify_landcover(self, lat: float, lon: float, start: str, end: str,
                           buffer_km: float = 2.0, n_trees: int = 100) -> Dict:
        """Random-Forest land cover with published error matrix and kappa."""
        return self._post("/v2/analyze/lulc", {
            "latitude": lat, "longitude": lon, "buffer_km": buffer_km,
            "start": start, "end": end, "n_trees": n_trees,
        })

    def fit_baseline(self, lat: float, lon: float, band: str = "NDVI",
                     years_back: int = 2, buffer_km: float = 2.0) -> Dict:
        """Fit the harmonic seasonal baseline for an area of interest."""
        return self._post("/v2/analyze/baseline", {
            "latitude": lat, "longitude": lon, "buffer_km": buffer_km,
            "band": band, "years_back": years_back,
        })

    def ask(self, question: str, user_id: str = "me") -> Dict:
        """Ask the grounded AI analyst.

        Runs the plan -> act -> ground -> synthesise loop server-side and
        returns a structured result:

            {
              "answer": str,               # plain-language, cites its sources
              "citations": [str, ...],     # page-level book citations
              "tools_used": [str, ...],    # live tools the agent invoked
              "reasoning": [str, ...],     # transparent step trace
              "grounded": bool             # True if book evidence was used
            }
        """
        return self._post("/v2/agent/ask", {"question": question, "user_id": user_id})
