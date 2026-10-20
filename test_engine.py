import unittest
from atlas.engine import backtest, validate, metrics
from atlas.data import demo

class AccountingTests(unittest.TestCase):
    def setUp(self):
        self.rows = demo()[:180]
    def test_future_cannot_change_past(self):
        before = backtest(self.rows, 'inverse_vol')
        altered = [dict(r) for r in self.rows]
        for r in altered[150:]:
            r['SPY'] *= 5
        after = backtest(altered, 'inverse_vol')
        self.assertEqual(before['equity'][:86], after['equity'][:86])
    def test_cost_reduces_wealth(self):
        free = backtest(self.rows, cost_bps=0)
        paid = backtest(self.rows, cost_bps=25)
        self.assertLess(paid['equity'][-1], free['equity'][-1])
    def test_weights_sum_to_one(self):
        r = backtest(self.rows, 'inverse_vol')
        for w in r['weights']:
            self.assertAlmostEqual(sum(w.values()), 1)
    def test_flat_prices_initial_cost(self):
        rows = [{'date': r['date'], 'SPY':100.,'IEF':100.} for r in self.rows]
        result = backtest(rows, cost_bps=10)
        self.assertAlmostEqual(result['equity'][-1], .999)
    def test_buy_and_hold_between_rebalances(self):
        rows=[{'date':'2024-01-%02d'%i,'A':100.+i,'B':200.-i} for i in range(1,25)]
        r=backtest(rows,lookback=2,cost_bps=0)
        expected=.5*rows[-1]['A']/rows[2]['A']+.5*rows[-1]['B']/rows[2]['B']
        self.assertAlmostEqual(r['equity'][-1],expected)
    def test_duplicate_rejected(self):
        with self.assertRaises(ValueError): validate([self.rows[0]]*3)
    def test_nan_rejected(self):
        self.rows[2]['SPY']=float('nan')
        with self.assertRaises(ValueError): validate(self.rows)
    def test_drawdown_known_path(self):
        m,d=metrics([1,2,1,3],['2020-01-01','2020-01-02','2020-01-03','2020-01-04'])
        self.assertEqual(m['max_drawdown'],-.5)
    def test_same_evaluation_window(self):
        runs=[backtest(self.rows,s) for s in ['equal','balanced','inverse_vol']]
        self.assertTrue(all(r['dates']==runs[0]['dates'] for r in runs))
    def test_invalid_strategy_rejected(self):
        with self.assertRaises(ValueError): backtest(self.rows,'unknown')

if __name__=='__main__': unittest.main()
