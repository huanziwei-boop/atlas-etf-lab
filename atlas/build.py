"""Build a portable report and a SQLite research warehouse."""
import argparse
import hashlib
import json
import sqlite3
from pathlib import Path
from datetime import datetime, timezone
from .data import demo, load_csv
from .engine import backtest, validate


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--csv', type=Path)
    p.add_argument('--source', default='')
    p.add_argument('--adjusted-confirmed', action='store_true')
    p.add_argument('--output', type=Path, default=Path('docs'))
    a = p.parse_args()
    if a.csv and (not a.source or not a.adjusted_confirmed):
        p.error('Real data requires --source and --adjusted-confirmed')
    rows = load_csv(a.csv) if a.csv else demo()
    names = validate(rows)
    source = a.source if a.csv else 'Seeded synthetic fixture; NOT market history'
    runs = [backtest(rows, strategy=s, cost_bps=c, frequency=f)
            for s in ['equal', 'balanced', 'inverse_vol']
            for c in [0, 10, 25] for f in ['monthly', 'quarterly']]
    digest = hashlib.sha256(json.dumps(rows, sort_keys=True).encode()).hexdigest()
    payload = {'synthetic': not bool(a.csv), 'source': source, 'assets': names,
               'observations': len(rows), 'sha256': digest,
               'built_utc': datetime.now(timezone.utc).isoformat(), 'runs': runs}
    a.output.mkdir(parents=True, exist_ok=True)
    template = Path(__file__).with_name('template.html').read_text()
    # Escape HTML-sensitive JSON so an untrusted source string cannot end the script.
    embedded = json.dumps(payload, allow_nan=False).replace('<', '\\u003c')
    (a.output / 'index.html').write_text(template.replace('__PAYLOAD__', embedded))
    (a.output / 'results.json').write_text(json.dumps(payload, indent=2, allow_nan=False))
    db = sqlite3.connect(a.output / 'research.sqlite')
    db.executescript('DROP TABLE IF EXISTS prices; DROP TABLE IF EXISTS runs; CREATE TABLE prices(date TEXT, ticker TEXT, adjusted_close REAL CHECK(adjusted_close>0), PRIMARY KEY(date,ticker)); CREATE TABLE runs(strategy TEXT, cost_bps REAL, frequency TEXT, cagr REAL, volatility REAL, sharpe REAL, max_drawdown REAL);')
    db.executemany('INSERT INTO prices VALUES(?,?,?)', [(r['date'], n, r[n]) for r in rows for n in names])
    db.executemany('INSERT INTO runs VALUES(?,?,?,?,?,?,?)', [(r['strategy'], r['cost_bps'], r['frequency'], *[r['metrics'][k] for k in ['cagr','volatility','sharpe','max_drawdown']]) for r in runs])
    db.commit()
    db.close()
    print('Built', a.output / 'index.html', '|', source, '|', len(runs), 'scenarios')

if __name__ == '__main__':
    main()
