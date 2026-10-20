-- All outputs are synthetic unless a licensed CSV was explicitly supplied.
-- Each of the following two audits should return 0 violations.
SELECT COUNT(*) AS timing_violations FROM trades
WHERE NOT (signal_date < execution_date AND execution_date < return_date);
SELECT COUNT(*) AS budget_violations FROM trades
WHERE ABS(pre_trade_nav-post_trade_nav-cost_nav)>1e-10;

-- Compare costs and gross traded notional; turnover counts both sides.
SELECT r.strategy,r.frequency,r.cost_bps,COUNT(*) AS rebalances,
       SUM(t.two_way_turnover) AS total_two_way_turnover,
       SUM(t.cost_nav) AS fee_value_per_initial_nav
FROM runs r JOIN trades t ON r.rowid=t.run_id
GROUP BY r.rowid ORDER BY r.strategy,r.frequency,r.cost_bps;

-- Daily net returns for downstream BI or independent reconciliation.
WITH lagged AS (
 SELECT run_id,date,nav,LAG(nav) OVER(PARTITION BY run_id ORDER BY date) AS prior_nav
 FROM daily_nav)
SELECT run_id,date,nav/prior_nav-1 AS net_return FROM lagged WHERE prior_nav IS NOT NULL;
