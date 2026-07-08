"""Quickstart: detect and score change at a location."""
import sys
sys.path.insert(0, "../sdk")
from sitewatch_client import SiteWatch

sw = SiteWatch("http://localhost:8001")
print(sw.health())
r = sw.analyze_change(
    lat=12.7974, lon=80.2232,
    before=("2025-01-01", "2025-03-01"),
    after=("2026-01-01", "2026-03-01"),
)
print(f"{r['change_label']} | confidence {r['confidence']} ({r['confidence_label']})")
print("evidence:", r["scene_stats"], r["sar"])
