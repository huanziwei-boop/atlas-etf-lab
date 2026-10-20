"""Synthetic fixture and explicit adjusted-price CSV ingestion."""
import csv
import random
import math
from datetime import date, timedelta
from .engine import validate


def demo():
    rng = random.Random(42)
    prices = dict.fromkeys(['SPY', 'QQQ', 'IEF', 'GLD', 'VNQ'], 100.)
    rows, day = [], date(2016, 1, 4)
    for i in range(2520):
        while day.weekday() > 4:
            day += timedelta(days=1)
        common = rng.gauss(0, 1)
        crisis = 1040 <= i < 1100 or 1600 <= i < 1790
        for n, beta, vol, drift in [('SPY', .85, .009, .0003), ('QQQ', 1., .013, .0004),
                                     ('IEF', -.15, .004, .0001), ('GLD', .1, .008, .0002),
                                     ('VNQ', .7, .012, .0002)]:
            shock = (beta * common + math.sqrt(max(0, 1-beta*beta))*rng.gauss(0, 1)) * vol
            prices[n] *= math.exp(drift + shock * (2 if crisis else 1) - (.001 if crisis else 0))
        rows.append({'date': day.isoformat(), **prices})
        day += timedelta(days=1)
    return rows


def load_csv(path):
    with open(path, newline='') as f:
        rows = [{'date': r['date'], **{k: float(v) for k,v in r.items() if k != 'date'}}
                for r in csv.DictReader(f)]
    validate(rows)
    return rows
