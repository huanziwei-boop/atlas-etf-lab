"""Close-to-close accounting with observable signals and explicit trading costs."""
import math
import statistics as st
from datetime import date


def validate(rows):
    if len(rows) < 3:
        raise ValueError('At least three observations are required')
    names = sorted(k for k in rows[0] if k != 'date')
    if not names:
        raise ValueError('No assets')
    last = ''
    for row in rows:
        date.fromisoformat(row['date'])
        if row['date'] <= last:
            raise ValueError('Dates must be strictly increasing and unique')
        if sorted(k for k in row if k != 'date') != names:
            raise ValueError('Asset columns changed')
        for name in names:
            if not math.isfinite(float(row[name])) or float(row[name]) <= 0:
                raise ValueError('Prices must be finite and positive')
        last = row['date']
    return names


def targets(rows, i, names, strategy, lookback):
    if strategy == 'equal':
        return [1 / len(names)] * len(names)
    if strategy == 'balanced':
        allocation = {'SPY': .6, 'IEF': .4}
        if not set(allocation) <= set(names):
            raise ValueError('Balanced benchmark requires SPY and IEF')
        return [allocation.get(n, 0) for n in names]
    if strategy != 'inverse_vol':
        raise ValueError('Unknown strategy')
    # Uses returns ending at the prior close only. No full-sample fitting.
    vols = [st.stdev([rows[j][n] / rows[j-1][n] - 1
                     for j in range(i-lookback, i)]) for n in names]
    scores = [1 / max(v, 1e-6) for v in vols]
    return [s / sum(scores) for s in scores]


def metrics(equity, dates, rf=0.0):
    returns = [b / a - 1 for a, b in zip(equity, equity[1:])]
    years = (date.fromisoformat(dates[-1]) - date.fromisoformat(dates[0])).days / 365.25
    vol = st.stdev(returns) if len(returns) > 1 else 0
    excess = [r - ((1 + rf) ** (1/252) - 1) for r in returns]
    peak, drawdown = equity[0], []
    for e in equity:
        peak = max(peak, e)
        drawdown.append(e / peak - 1)
    tail = sorted(returns)[:max(1, math.ceil(.05 * len(returns)))]
    return {'total_return': equity[-1] / equity[0] - 1,
            'cagr': (equity[-1] / equity[0]) ** (1/years) - 1 if years else None,
            'volatility': vol * math.sqrt(252),
            'sharpe': st.mean(excess) / vol * math.sqrt(252) if vol else None,
            'max_drawdown': min(drawdown), 'daily_cvar_95': st.mean(tail)}, drawdown


def backtest(rows, strategy='equal', lookback=63, cost_bps=10, rf=0, frequency='monthly'):
    names = validate(rows)
    if lookback < 2 or len(rows) <= lookback + 1:
        raise ValueError('Insufficient history for lookback')
    if not 0 <= cost_bps <= 1000 or not -1 < rf < 1:
        raise ValueError('Invalid cost or risk-free assumption')
    if frequency not in ('monthly', 'quarterly'):
        raise ValueError('Invalid rebalance frequency')
    start = lookback + 1
    value, weights = 1., [0.] * len(names)
    equity, dates, trades, weight_history = [1.], [rows[start-1]['date']], [], []
    for i in range(start, len(rows)):
        # Signal at t-1 close; execution modeled at that close, before t return.
        month_changed = rows[i]['date'][:7] != rows[i-1]['date'][:7]
        quarter_start = int(rows[i]['date'][5:7]) in (1, 4, 7, 10)
        rebalance = i == start or (month_changed and (frequency == 'monthly' or quarter_start))
        if rebalance:
            target = targets(rows, i, names, strategy, lookback)
            traded = sum(abs(a-b) for a,b in zip(target, weights))
            fee = value * traded * cost_bps / 10000
            value -= fee
            weights = target
            trades.append({'signal_date': rows[i-1]['date'], 'return_date': rows[i]['date'],
                           'traded_notional': traded, 'cost_nav': fee,
                           'weights': dict(zip(names, target))})
        growth = [rows[i][n] / rows[i-1][n] for n in names]
        gross = sum(w*g for w,g in zip(weights, growth))
        value *= gross
        weights = [w*g/gross for w,g in zip(weights, growth)]
        equity.append(value)
        dates.append(rows[i]['date'])
        weight_history.append(dict(zip(names, weights)))
    stats, dd = metrics(equity, dates, rf)
    return {'strategy': strategy, 'dates': dates, 'equity': equity, 'drawdown': dd,
            'metrics': stats, 'trades': trades, 'weights': weight_history,
            'cost_bps': cost_bps, 'lookback': lookback, 'frequency': frequency}
