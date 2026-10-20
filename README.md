# Atlas ETF Lab

**A transparent portfolio research workbench: allocation, drawdowns, and the cost of rebalancing.**

Python · SQLite · SQL window functions · interactive HTML · tested accounting

> **Status: working research prototype. The bundled report uses SYNTHETIC data.**
> No historical performance claim is made. Real-data acquisition and GitHub publication
> have not yet been verified in the development environment.

## Research question

How do equal-weight, 60/40 and trailing inverse-volatility allocations differ when
we account for weight drift, rebalance schedules and trading friction?

The five-ETF universe is SPY, QQQ, IEF, GLD and VNQ. This is a deliberately small,
fixed universe selected today: it is not a point-in-time universe and carries
selection bias. SPY and QQQ overlap materially; five tickers do not mean five
independent risk sources.

## Run in 30 seconds

Python 3.9+; no dependencies for the engine, synthetic fixture or report.

```bash
python -m unittest test_engine -v
python -m atlas.build
python -m http.server 8000 --directory docs --bind 127.0.0.1
```

Open http://127.0.0.1:8000. Alternatively, open `docs/index.html` directly.
The report has strategy, cost and rebalance controls, equity/drawdown charts,
benchmark comparison, JSON export, and a source fingerprint. Nothing is sent
from the report to a server. No API key is embedded.

## Real data

Supply a wide CSV with strictly increasing ISO dates and finite, positive,
dividend/split-adjusted prices:

```csv
date,SPY,QQQ,IEF,GLD,VNQ
2024-01-02,100,100,100,100,100
2024-01-03,101,102,100.1,99,100.5
```

The example above is schema illustration only. At least 65 observations are
needed for the default 63-day trailing window.

```bash
python -m atlas.build --csv data/adjusted.csv \
  --source "Provider name; download date; adjustment convention" \
  --adjusted-confirmed --output reports/historical
```

No missing-value forward fill or silent invalid-row deletion is performed.
The caller must verify adjustment conventions, exchange calendars and coverage.
An optional downloader is provided in `fetch_prices.py`; its live provider path
has not been exercised here. It requires `pip install -r requirements-data.txt`.
Provider access and redistribution rights are separate from this code's license.
Do not commit third-party prices unless their license permits it.
Yahoo describes adjusted close here:
https://in.help.yahoo.com/kb/adjusted-close-sln28256.html

## Accounting contract

- Signals use only returns ending at the prior close; no full-sample volatility.
- At the close preceding the first observation of a new month/quarter, rebalance
  to the chosen weights. Execution at the signal close is **idealized**: a real
  implementation needs a delay or next-open execution model.
- Apply the next close-to-close adjusted-price return. Weights drift naturally.
- Costs are `NAV × sum(abs(target - drifted_weights)) × bps / 10,000`.
  Both bought and sold notional are charged. Initial investment is charged;
  final liquidation is not. Post-cost wealth is allocated to target weights.
  This is a proportional NAV haircut approximation, not an exact trade solver.
- Inverse-volatility uses a 63-return sample standard deviation, floored at 1e-6,
  then normalizes reciprocals. It is not covariance-aware risk parity.
- All strategies share a warm-up and evaluation window; no optimized parameters
  are selected by an unseen test set. These are descriptive comparisons, not
  a validated predictive strategy or a claimed out-of-sample discovery.
- CAGR uses elapsed calendar years. Volatility and Sharpe use 252 observations/year.
  Sharpe assumes a constant 0% risk-free rate. CVaR is the empirical mean of the
  worst ceil(5% × n) daily returns. Drawdown includes entry costs.

## Structure

| Path | Purpose |
| --- | --- |
| `atlas/engine.py` | validation, targets, drift, fees, risk metrics |
| `atlas/data.py` | deterministic synthetic generator and CSV loader |
| `atlas/build.py` | 18-scenario sweep, fingerprint, HTML and SQLite export |
| `atlas/template.html` | responsive self-contained research dashboard |
| `research.sql` | daily returns, cost sensitivity, coverage audit |
| `test_engine.py` | accounting invariants and future-data perturbation |
| `index.html` | ready-to-open synthetic demonstration |

Generated SQLite data is ignored by Git. Rebuild it and run:

```bash
sqlite3 docs/research.sqlite < research.sql
```

## What is tested

Buy-and-hold arithmetic between rebalances, initial entry costs on flat prices,
weight normalization, no change to earlier results when future prices change,
known-path drawdown, invalid observations, invalid strategies, common sample
windows and cost monotonicity. CI configuration is included in the archive but has not run on GitHub yet.

## What would make this investment-grade

Real-data reconciliation against an independent source; live calendar checks;
next-open execution; time-varying risk-free rates; cash flows and tax accounting;
transaction-cost estimation; configurable point-in-time universes; missing-data
policy; pre-specified holdout windows and uncertainty intervals. No trading or
brokerage integration is included.

## Publication

Repository: https://github.com/huanziwei-boop/atlas-etf-lab

For GitHub Pages, the root `index.html` is a synthetic demo. Locally rebuilt
reports are written to `docs` by default. Keep the synthetic
banner until you intentionally generate and review a licensed historical report.

## Interview discussion

Be prepared to explain why weights drift, why turnover costs count buys and sells,
why inverse volatility differs from risk parity, how future leakage is tested,
and why a strong synthetic backtest says nothing about real investment returns.
This implementation was developed with AI assistance. Review and understand the
code before presenting it as a personal portfolio project.
