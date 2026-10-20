"""Chronological holdout evaluation; select on training Sharpe only.

This is a software protocol demonstration on the bundled synthetic fixture.
A split chosen after seeing data is not a genuinely unseen experiment.
"""
import argparse
import json
import math
from datetime import date
from pathlib import Path
from .data import demo, load_csv
from .engine import backtest, metrics, validate


def segment(run, lo, hi):
    if hi-lo < 21:
        raise ValueError('Each segment needs at least 21 return observations')
    values, dates = run['equity'][lo:hi+1], run['dates'][lo:hi+1]
    stats, _ = metrics(values, dates)
    trades = [t for t in run['trades'] if dates[0] < t['return_date'] <= dates[-1]]
    years = (date.fromisoformat(dates[-1])-date.fromisoformat(dates[0])).days/365.25
    stats.update({'start':dates[0], 'end':dates[-1], 'return_observations':hi-lo,
                  'two_way_turnover_per_year':sum(t['traded_notional'] for t in trades)/years,
                  'cost_value_per_start_nav':sum(t['cost_nav'] for t in trades)/values[0]})
    return stats


def evaluate(rows, split_date, cost_bps=10, frequency='monthly'):
    validate(rows)
    date.fromisoformat(split_date)
    runs = [backtest(rows, strategy=s, cost_bps=cost_bps, frequency=frequency)
            for s in ['equal', 'balanced', 'inverse_vol']]
    dates = runs[0]['dates']
    # Baseline closes on/before split; all subsequent returns are holdout.
    before = [i for i,d in enumerate(dates) if d <= split_date]
    if not before or split_date >= dates[-1]:
        raise ValueError('Split must be inside evaluation window')
    boundary = before[-1]
    train = [segment(r, 0, boundary) for r in runs]
    def score(i):
        value=train[i]['sharpe']
        return value if value is not None and math.isfinite(value) else float('-inf')
    winner=max(range(len(runs)), key=score)
    if score(winner)==float('-inf'):
        raise ValueError('Training Sharpe undefined for all candidates')
    return {'requested_split_date':split_date, 'actual_split_close':dates[boundary],
            'selection_rule':'Highest training Sharpe; ties use equal, balanced, inverse_vol order',
            'selected_strategy':runs[winner]['strategy'],
            'assumptions':{'signal_lag_observations':1, 'cost_bps':cost_bps, 'frequency':frequency,
                           'holdout_positions':'Carry existing positions; no free reset at split',
                           'universe':'Fixed ex-post universe, NOT survivorship-bias-free',
                           'risk_free_rate':0},
            'candidates':[{'strategy':r['strategy'], 'training':tr,
                           'holdout':segment(r,boundary,len(dates)-1)}
                          for r,tr in zip(runs,train)]}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--csv',type=Path)
    p.add_argument('--source',default='')
    p.add_argument('--adjusted-confirmed',action='store_true')
    p.add_argument('--split-date',required=True)
    p.add_argument('--output',type=Path,default=Path('docs/holdout.json'))
    a=p.parse_args()
    if a.csv and (not a.source or not a.adjusted_confirmed):
        p.error('CSV requires --source and --adjusted-confirmed')
    result=evaluate(load_csv(a.csv) if a.csv else demo(), a.split_date)
    result.update({'synthetic':not bool(a.csv),
                   'source':a.source if a.csv else 'Seeded synthetic fixture; NOT market history',
                   'interpretation':'Descriptive holdout protocol; no claim of unseen real-world validation'})
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2,allow_nan=False))
    print('Wrote',a.output)

if __name__=='__main__': main()
