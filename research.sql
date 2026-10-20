-- SQLite 3.25+. Explicit daily adjusted-close returns (no implicit forward fill).
WITH lagged AS (
 SELECT date, ticker, adjusted_close,
 LAG(adjusted_close) OVER (PARTITION BY ticker ORDER BY date) AS prior
 FROM prices
)
SELECT date, ticker, adjusted_close / prior - 1 AS daily_return
FROM lagged WHERE prior IS NOT NULL ORDER BY date, ticker;

-- Cost sensitivity: same strategy, frequency, and input sample.
SELECT a.strategy, a.frequency, a.cagr AS no_cost_cagr, b.cagr AS costly_cagr,
 a.cagr-b.cagr AS annualized_cost_drag
FROM runs a JOIN runs b ON a.strategy=b.strategy AND a.frequency=b.frequency
WHERE a.cost_bps=0 AND b.cost_bps=25;

-- Coverage audit; equal counts alone do not prove aligned dates.
SELECT ticker, COUNT(*) AS observations, MIN(date) AS first_date,
 MAX(date) AS last_date, MIN(adjusted_close) AS minimum_price
FROM prices GROUP BY ticker;
