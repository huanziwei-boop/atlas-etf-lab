# Portfolio positioning and acceptance gates

This is an engineering/research prototype, not a claim to meet every employer's
requirements. The groups below are a presentation strategy based on the user's
applications, not a statement of each employer's hiring preferences.

| Audience | Evidence to emphasize | Evidence still missing |
| --- | --- | --- |
| Amazon BIE/BA, Intuit business data | SQL joins/window functions, repeatable pipeline, cost/turnover metrics, scenario CSV | Real source reconciliation, business decision memo, dashboard user study |
| CRA, Analysis Group, valuation/research roles | Explicit assumptions, cash accounting, holdout selection, audit trail | Real evidence, independent replication, uncertainty intervals, valuation-specific case |
| Jabil systems, Adobe enterprise architecture/solutions | Input contract, layered code, tests, warehouse, reproducible commands | Documented REST API, integration tests, CI execution, cloud deployment, user requirements |
| Adobe strategy/consulting | Explain sensitivity and limitations to a nontechnical reader | Customer discovery, trade-off memo, presentation tested with a reader |
| Investment/quantitative roles | Execution delay, turnover costs, holdout discipline | Point-in-time universe, delistings, factor IC/Rank IC, broader cross-section, robust inference |
| Google TPM | Testable acceptance criteria and traceable deliveries | Actual coordination, stakeholder communication and project-management experience |

An ETF project does not directly demonstrate pricing experimentation, credit
underwriting, enterprise architecture delivery, or research publications. Keep
Home Credit for credit/risk and add a focused business case rather than forcing
all domains into this project.

## Next gates, in order

1. **Real data:** complete a licensed adjusted-price ingestion; archive provider,
   download timestamp, adjustment definition and checksum; reconcile sampled
   returns against a second source. Do not republish provider data without rights.
2. **Research design:** freeze hypothesis, strategy rules, costs and split before
   new data is revealed. Use a broader point-in-time universe for stock factors;
   include removed/delisted securities and point-in-time fundamental publication
   timestamps. If unavailable, narrow claims instead of hiding the limitation.
3. **Research evidence:** implement IC/Rank IC and quantile return diagnostics with
   explicit signal/label timing, turnover/costs, blocked inference and rolling
   evaluation. Do not optimize for a spectacular Sharpe.
4. **Business decision:** one-page memo answering whether additional rebalancing
   is worth its cost, who uses the result, alternatives and uncertainty. Report
   negative findings. Synthetic data cannot substantiate a market recommendation.
5. **Systems delivery:** read-only versioned API, schema validation, API tests,
   reproducible environment, CI execution and a deployment that can be verified.
6. **Personal ownership:** explain one accounting test and one design trade-off
   without assistance, then reproduce the result. Disclose AI assistance honestly.

## Verified v2 changes

- One complete observation between signal close and execution close.
- Self-financing transaction-cost solver and trade-level cash reconciliation.
- Training-only strategy selection with chronological holdout report.
- Daily NAV and trade tables plus SQL audit queries and scenario CSV.
- 18 local tests, including holdout perturbation and execution-price isolation.

Live market ingestion was attempted on 2026-10-20 but DNS resolution failed in
the execution environment. Bundled reports therefore remain synthetic. Local
success does not imply remote CI success.

## Primary role references reviewed

- CRA: https://job-boards.greenhouse.io/charlesriverassociates/jobs/8160288
- Jabil: https://jobs.jabil.com/en/job/st-petersburg/computer-systems-analyst-intern/626/101579517376
- yfinance data-use documentation: https://ranaroussi.github.io/yfinance/
