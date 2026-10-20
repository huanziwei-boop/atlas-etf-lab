"""Optional live-data adapter. Provider availability must be verified by the caller."""
import argparse
import hashlib
import json
from pathlib import Path
from datetime import datetime, timezone


def main():
    import yfinance as yf
    p=argparse.ArgumentParser()
    p.add_argument('--start',default='2015-01-01')
    p.add_argument('--end',required=True,help='Exclusive end date; choose a completed trading period')
    p.add_argument('--output',type=Path,default=Path('data/adjusted.csv'))
    a=p.parse_args()
    tickers=['SPY','QQQ','IEF','GLD','VNQ']
    raw=yf.download(tickers,start=a.start,end=a.end,auto_adjust=False,progress=False)
    if raw.empty or 'Adj Close' not in raw:
        raise RuntimeError('No adjusted data returned; no synthetic fallback is allowed')
    frame=raw['Adj Close'][tickers]
    if frame.isna().any().any():
        raise ValueError('Missing observations; inspect provider coverage before proceeding')
    frame.index.name='date'
    a.output.parent.mkdir(parents=True,exist_ok=True)
    frame.to_csv(a.output,date_format='%Y-%m-%d')
    manifest={'provider':'Yahoo Finance via yfinance','yfinance_version':yf.__version__,
              'retrieved_utc':datetime.now(timezone.utc).isoformat(),'start':a.start,
              'end_exclusive':a.end,'tickers':tickers,'field':'Adj Close',
              'sha256':hashlib.sha256(a.output.read_bytes()).hexdigest()}
    a.output.with_suffix('.manifest.json').write_text(json.dumps(manifest,indent=2))
    print('Saved',len(frame),'observations to',a.output)

if __name__=='__main__': main()
