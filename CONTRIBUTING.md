# Contributing

The fastest ways to help, in order of value:

1. **Add a company.** Copy `data/companies/_template.json`, fill it from the company's public pricing page, cite the URL with an access date, run `python scripts/validate.py`, open a PR. Rules: every claim needs a source; use `confidence: "reported"` (with the article URL) for anything not read directly off a pricing page; never guess.
2. **Update a snapshot.** Pricing changed? Add a NEW snapshot to the company's `snapshots` array (never edit historical ones) with a `change_note` describing what moved.
3. **Critique the methodology.** Open an issue. Schema and inclusion criteria are v0.x and expected to evolve — sharp criticism is a contribution.

## Ground rules

- Historical snapshots are immutable — this dataset's value is the time series.
- No editorializing in data files. Analysis belongs in the quarterly report.
- One company per PR keeps review fast.
