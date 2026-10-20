"""Transparent portfolio risk monitoring, not an order execution system."""
import math
import statistics

DEFAULT_LIMITS = dict(drawdown=.15, annualized_volatility=.20,
                      max_asset_weight=.40, daily_es_95=.025)
STRESSES = {
    'Equity selloff (hypothetical)': dict(SPY=-.20, QQQ=-.30, IEF=.05, GLD=.05, VNQ=-.25),
    'Rates and inflation shock (hypothetical)': dict(SPY=-.15, QQQ=-.20, IEF=-.12, GLD=-.05, VNQ=-.20),
    'Broad liquidation (hypothetical)': dict(SPY=-.25, QQQ=-.30, IEF=-.10, GLD=-.15, VNQ=-.30),
}


def tail_loss(returns, confidence=.95):
    """Nearest-rank empirical loss VaR; ES is mean of worst ceil(alpha*n)."""
    if not returns or not 0 < confidence < 1 or not all(math.isfinite(x) for x in returns):
        raise ValueError('Finite nonempty returns and valid confidence required')
    losses = sorted(-r for r in returns)
    k = max(1, math.ceil(round((1-confidence)*len(losses), 12)))
    return max(0., losses[math.ceil(confidence*len(losses))-1]), max(0., statistics.mean(losses[-k:]))


def stress_loss(weights, shocks):
    if set(weights) - set(shocks):
        raise ValueError('Stress scenario must cover every held asset')
    if not all(math.isfinite(x) for x in list(weights.values())+list(shocks.values())):
        raise ValueError('Nonfinite scenario input')
    if any(w < 0 for w in weights.values()) or not math.isclose(sum(weights.values()), 1., abs_tol=1e-8):
        raise ValueError('Long-only fully invested weights required')
    if any(s < -1 for s in shocks.values()):
        raise ValueError('Asset price cannot fall below zero')
    return -sum(w*shocks[n] for n,w in weights.items())


def monitor(run, limits=None, window=63):
    limits = dict(DEFAULT_LIMITS if limits is None else limits)
    if set(limits) != set(DEFAULT_LIMITS) or any(not math.isfinite(v) or not 0 < v <= 1 for v in limits.values()):
        raise ValueError('Provide all four positive fractional risk limits')
    if not isinstance(window, int) or window < 20:
        raise ValueError('Risk window must be at least 20 observations')
    returns = [b/a-1 for a,b in zip(run['equity'],run['equity'][1:])]
    daily, exceptions = [], []
    for i,r in enumerate(returns):
        weights = run['weights'][i]
        # The current return is excluded from the forecast used to test it.
        prior = returns[max(0,i-window):i]
        forecast = tail_loss(prior)[0] if len(prior) == window else None
        sample = returns[max(0,i-window+1):i+1]
        ready = len(sample) == window
        var, es = tail_loss(sample) if ready else (None,None)
        vol = statistics.stdev(sample)*math.sqrt(252) if ready else None
        values = dict(drawdown=-run['drawdown'][i+1], annualized_volatility=vol,
                      max_asset_weight=max(weights.values()), daily_es_95=es)
        breaches = [k for k,v in values.items() if v is not None and v > limits[k]]
        item = dict(date=run['dates'][i+1], **values, daily_var_95=var,
                    prior_var_95=forecast, var_exception=forecast is not None and -r > forecast,
                    status='BREACH' if breaches else ('WITHIN_LIMITS' if ready else 'WARMUP'), breaches=breaches)
        daily.append(item)
        exceptions.extend(dict(date=item['date'], metric=k, value=values[k], limit=limits[k]) for k in breaches)
    weights = run['weights'][-1]
    stress = [dict(scenario=n, loss=stress_loss(weights,s)) for n,s in STRESSES.items() if set(weights)<=set(s)]
    forecasts = [d for d in daily if d['prior_var_95'] is not None]
    return dict(limits=limits, window=window, latest=daily[-1], daily=daily, exceptions=exceptions,
                breach_days=sum(bool(d['breaches']) for d in daily),
                var_forecast_days=len(forecasts), var_exception_count=sum(d['var_exception'] for d in forecasts),
                effective_holdings=1/sum(w*w for w in weights.values()), stress=stress,
                stress_unavailable=not bool(stress),
                action='Review exposure and risk budget; no automatic orders or guaranteed loss cap.')
