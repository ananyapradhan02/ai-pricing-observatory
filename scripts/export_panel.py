#!/usr/bin/env python3
"""Export the company JSON files into tidy panel data (econometrics-ready CSVs).

Produces two long-format panels in data/panels/:

  sku_panel.csv    — one row per company x plan (SKU) x snapshot date
  meter_panel.csv  — one row per company x usage meter x snapshot date,
                     with normalized USD-per-unit where parseable
  events_panel.csv — one row per company x pricing change event

Design: JSON files are the source of truth (rich, source-cited, versioned).
These CSVs are derived artifacts — never edit them by hand; regenerate.

Usage: python scripts/export_panel.py
"""
import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COMPANIES = ROOT / "data" / "companies"
OUT = ROOT / "data" / "panels"

# Canonical units we try to normalize meter rates into.
# Maps regex on the rate/meter text -> (unit_name, multiplier_to_canonical)
# e.g. "$5 per 1M tokens" -> usd_per_1m_tokens = 5.0
RATE_RE = re.compile(r"\$\s*([0-9][0-9,]*\.?[0-9]*)\s*(?:per|/)\s*([0-9.,]*\s*[A-Za-z ]+)")

CANONICAL = [
    # (pattern on the "per X" side, canonical unit name, scale factor to canonical)
    (re.compile(r"1\s*m(illion)?\s*tokens?", re.I), "usd_per_1m_tokens", 1.0),
    (re.compile(r"1\s*k\s*tokens?", re.I), "usd_per_1m_tokens", 1000.0),
    (re.compile(r"\btokens?\b", re.I), "usd_per_1m_tokens", 1_000_000.0),
    (re.compile(r"\bresolutions?\b", re.I), "usd_per_resolution", 1.0),
    (re.compile(r"\bconversations?\b", re.I), "usd_per_conversation", 1.0),
    (re.compile(r"\bminutes?\b", re.I), "usd_per_minute", 1.0),
    (re.compile(r"1\s*k\s*credits?", re.I), "usd_per_credit", 0.001),
    (re.compile(r"\bcredits?\b", re.I), "usd_per_credit", 1.0),
    (re.compile(r"\btasks?\b", re.I), "usd_per_task", 1.0),
    (re.compile(r"\bwords?\b", re.I), "usd_per_word", 1.0),
]


def normalize_rate(rate_text: str):
    """Parse '$X per UNIT' into (canonical_unit, usd_per_canonical) or (None, None)."""
    if not rate_text:
        return None, None
    m = RATE_RE.search(rate_text)
    if not m:
        return None, None
    price = float(m.group(1).replace(",", ""))
    per = m.group(2)
    for pat, unit, scale in CANONICAL:
        if pat.search(per):
            return unit, price * scale
    return "usd_per_" + per.strip().lower().replace(" ", "_"), price


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    files = sorted(p for p in COMPANIES.glob("*.json") if not p.name.startswith("_"))
    if not files:
        print("No company files.")
        return 1

    sku_rows, meter_rows, event_rows = [], [], []
    for path in files:
        rec = json.loads(path.read_text())
        base = {
            "company": rec["company"],
            "slug": rec["slug"],
            "category": rec["category"],
            "hq_country": rec.get("hq_country", ""),
        }
        for ev in rec.get("change_events", []):
            event_rows.append({
                **base,
                "date": ev["date"],
                "change_type": ev["change_type"],
                "description": ev["description"],
                "announced": ev.get("announced", ""),
                "notice_period": ev.get("notice_period", ""),
                "grandfathering": ev.get("grandfathering", ""),
                "user_reaction": ev.get("user_reaction", ""),
            })
        for snap in rec["snapshots"]:
            s = {
                **base,
                "as_of": snap["as_of"],
                "confidence": snap["confidence"],
                "pricing_models": "|".join(snap["pricing_models"]),
                "free_tier": snap.get("free_tier", ""),
                "has_outcome_pricing": bool(snap.get("outcome_pricing")),
                "has_credits_system": bool(snap.get("credits_system")),
                "enterprise_custom": bool((snap.get("enterprise") or {}).get("custom_pricing")),
            }
            for plan in snap.get("plans", []):
                lim = plan.get("limits") or {}
                sku_rows.append({
                    **s,
                    "sku": plan.get("name", ""),
                    "price_usd": plan.get("price_usd", ""),
                    "billing_unit": plan.get("billing_unit", ""),
                    "billing_period": plan.get("billing_period", ""),
                    "whats_gated": plan.get("whats_gated", ""),
                    "quota": lim.get("quota", ""),
                    "unlimited_definition": lim.get("unlimited_definition", ""),
                    "throttle_behavior": lim.get("throttle_behavior", ""),
                })
            for meter in snap.get("usage_meters", []):
                unit, usd = normalize_rate(meter.get("rate", ""))
                meter_rows.append({
                    **s,
                    "meter": meter.get("meter", ""),
                    "rate_raw": meter.get("rate", ""),
                    "normalized_unit": unit or "",
                    "usd_per_unit": usd if usd is not None else "",
                    "overage_behavior": meter.get("overage_behavior", ""),
                })

    for name, rows in [("sku_panel.csv", sku_rows), ("meter_panel.csv", meter_rows), ("events_panel.csv", event_rows)]:
        if not rows:
            continue
        out = OUT / name
        with out.open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
        print(f"wrote {out.relative_to(ROOT)} ({len(rows)} rows)")

    print("Panels regenerated. JSON is the source of truth; do not hand-edit CSVs.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
