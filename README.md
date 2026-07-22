# AI Pricing Observatory

**An open, longitudinal dataset of how AI-native companies actually price and package their products.**

Maintained by [Ananya Pradhan](https://www.linkedin.com/in/ananyapradhan) · Data licensed CC-BY-4.0 · Code licensed MIT

## Why this exists

The most consequential GTM debate in AI — seats vs. usage vs. outcomes — is being argued almost entirely without open data. Model *token* prices are tracked publicly; product *pricing and packaging* is not. The serious surveys are closed-source and annual. Meanwhile pricing is moving fast: per-resolution pricing, credit systems, hybrid models, outcome guarantees.

This repo tracks it in the open: a versioned, source-cited record of pricing and packaging decisions across AI-native companies, snapshotted over time, so anyone can see not just *what* companies charge today but *how pricing is evolving*.

## What's in the dataset

Each company is one JSON file in `data/companies/`, validated against `data/schema.json`. Every record captures:

- **Pricing model type(s):** seat, usage, credit, outcome, hybrid, flat
- **Plans:** tiers, prices, billing units, what's gated
- **Usage meters:** what is metered (tokens, resolutions, minutes, credits) and at what rates
- **Outcome pricing:** if present, what counts as the outcome and its price
- **Free tier / trial mechanics**
- **Enterprise signals:** custom pricing, minimums, platform fees
- **Snapshots:** every record is dated; changes over time accumulate as new snapshots
- **Change events (first-class):** every observed pricing/packaging change — effective date, silent vs. announced, notice period, grandfathering terms, documented user reaction. The most demanded record in the dataset: top SaaS/AI companies reportedly made 1,800+ pricing changes in 2025 alone, and nobody keeps the log.
- **Credit dictionary:** what one credit actually buys, credit-to-compute mapping (where "opaque" is valid and important data), and whether failed agent actions consume credits
- **Limits as pricing:** per-plan quotas, what "unlimited" actually means, throttle behavior
- **Predictability:** spend caps, usage alerts, refund-on-failure policy — the bill-shock record
- **Sources:** every claim carries a URL and an `as_of` date. No source, no claim.

## Methodology (v0.1 — under open review)

1. **Inclusion:** AI-native companies (product's core value depends on AI) with public pricing pages or well-documented reported pricing. Target: 200+ companies by v1.0.
2. **Collection:** manual collection first (accuracy over automation), scrapers second (drift detection), community PRs third.
3. **Confidence levels:** `public_page` (read directly from pricing page) > `reported` (credible press/analyst) > `inferred`. Recorded per snapshot.
4. **Snapshots:** quarterly minimum; event-driven when a company changes pricing.
5. **No editorializing in data.** Analysis lives in the quarterly *State of AI Pricing* report, not in the dataset.

Methodology critiques welcome — open an issue. The schema is expected to break and improve in v0.x.

## Quarterly report

Findings are published quarterly as **State of AI Pricing** (first edition: Q4 2026), released openly in this repository. Analysis lives in the reports; the dataset stays neutral.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). The fastest way to help: add a company (copy `data/companies/_template.json`), or open an issue on the schema.

## Validation & panel export

```bash
python scripts/validate.py          # validates all company files against the schema
python scripts/export_panel.py     # derives econometrics-ready CSVs into data/panels/
```

### Panel data (for analysts and researchers)

The JSON files are the source of truth; `export_panel.py` derives **tidy long-format panels** from them, structured the way economics does it:

- `data/panels/sku_panel.csv` — one row per company × SKU × snapshot date: list price, billing unit/period, what's gated, pricing-model flags. Packaging analysis lives here.
- `data/panels/meter_panel.csv` — one row per company × usage meter × snapshot date, with rates **normalized to canonical units** (`usd_per_1m_tokens`, `usd_per_resolution`, `usd_per_credit`, `usd_per_minute`) so prices are comparable across companies and over time.

This makes the dataset directly usable for price-dispersion studies, hedonic comparisons ("what does a resolution cost across vendors?"), and survival analysis of pricing models — load the CSV into R/Stata/pandas and go. Never hand-edit the CSVs; regenerate them.

## Roadmap

- [x] v0.1 — schema + first 5 hand-collected companies + validator
- [ ] v0.2 — 25 companies, first schema revision after external methodology review
- [ ] v0.3 — pricing-page snapshot scraper with change detection
- [ ] v0.5 — 100 companies, first public analysis thread
- [ ] v1.0 — 200+ companies, State of AI Pricing Q4 2026
