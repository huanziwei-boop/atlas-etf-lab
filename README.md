# Atlas ETF Lab

**A transparent portfolio research workbench: allocation, drawdowns, and the cost of rebalancing.**

Python · SQLite · SQL window functions · interactive HTML · tested accounting

> **Status: working research prototype. The bundled report uses SYNTHETIC data.**
> No historical performance claim is made. Real-data acquisition remains unverified.
> Version 2 adds delayed execution, exact proportional-cost accounting, and chronological holdout evaluation.

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
python -m unittest discover -s tests -v
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

The example above is schema illustration only. At least 66 observations are
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

- With the default lag, signals use prices through t-2 close, execute at t-1
  close, and first earn the return into t. Zero signal delay is rejected. This
  uses observation offsets, not a verified exchange calendar. Adjusted-close
  execution remains an approximation: no bid/ask spread, market impact, or fills.
- Rebalance at the close preceding a new month/quarter; weights drift otherwise.
- Costs solve `post_NAV + rate * sum(abs(post_NAV*target - pre_NAV*weights)) = pre_NAV`.
  Both bought and sold actual dollar notional are charged. Initial entry is
  charged; terminal liquidation is not. This is self-financing under proportional
  fees, not a model of actual brokerage execution.
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
windows and cost monotonicity. CI configuration is provided; local test results do not imply a successful remote CI run.

## What would make this investment-grade

Real-data reconciliation against an independent source; live calendar checks;
next-open execution; time-varying risk-free rates; cash flows and tax accounting;
transaction-cost estimation; configurable point-in-time universes; missing-data
policy; prospectively locked research protocols and uncertainty intervals. No trading or
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

## Chronological holdout protocol (v2)

```bash
python -m atlas.evaluate --split-date 2022-12-30 --output docs/holdout.json
```

This example is a **synthetic protocol demonstration**, not genuine unseen market
validation. Choose and freeze the split before inspecting a real test set. At
10 bps/monthly, select one of three fixed strategies by training Sharpe only.
Report every candidate's training and holdout metrics; carry positions across
split with no free reset. Boundary-close NAV is shared but return intervals do
not overlap. Include two-way turnover/year and fees/start NAV. The test suite
perturbs future holdout data and verifies training metrics and selection stay
unchanged. Subsequent strategy redesign after reading a test set invalidates
its unseen status. Rolling evaluation and uncertainty intervals are not yet built.

## Queryable evidence (v2)

`docs/research.sqlite` contains prices, runs, daily_nav, and trades. Run IDs in
`daily_nav` and `trades` reference the freshly generated `runs.rowid` (1-based).
Signal, execution, return dates, actual traded value, fees, and pre/post NAV are
available for audit. `docs/scenario_summary.csv` is an Excel-readable summary.
See `sql/audit.sql` for timing, budget reconciliation, turnover, and fee queries.
All bundled figures remain synthetic.

## Scope boundaries

No point-in-time membership or delisted-security database; do not claim survivor-
bias elimination. No factor IC/Rank IC, quintile portfolios, fundamentals or
value factor yet. Five heterogeneous ETFs are too small for convincing stock-
factor inference. No REST service or cloud deployment yet. Do not claim these
features on a resume until implemented and verified. See `ROLE_FIT.md` for the
portfolio positioning and next acceptance gates.
