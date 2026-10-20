import copy
import unittest
from atlas.risk import tail_loss, stress_loss, monitor
from atlas.engine import backtest
from atlas.data import demo
class RiskTests(unittest.TestCase):
    def test_known_tail(self):
        self.assertEqual(tail_loss([-.1,-.05]+[0.]*18),(.05,.1))
    def test_gain_only(self):
        self.assertEqual(tail_loss([.01]*63),(0.,0.))
    def test_stress(self):
        self.assertAlmostEqual(stress_loss({'A':.6,'B':.4},{'A':-.2,'B':.05}),.1)
    def test_missing_coverage(self):
        with self.assertRaises(ValueError): stress_loss({'A':1.},{'B':-.2})
    def test_invalid_limits(self):
        with self.assertRaises(ValueError): monitor(backtest(demo()[:200]),{'drawdown':.1})
    def test_future_isolation(self):
        rows=demo()[:300]; other=copy.deepcopy(rows)
        for row in other[220:]: row['SPY']*=.5
        a=monitor(backtest(rows)); b=monitor(backtest(other))
        self.assertEqual([d for d in a['daily'] if d['date']<rows[220]['date']],[d for d in b['daily'] if d['date']<rows[220]['date']])
    def test_current_return_excluded_from_forecast(self):
        run=backtest(demo()[:300]); other=copy.deepcopy(run);other['equity'][-1]*=.5
        self.assertEqual(monitor(run)['latest']['prior_var_95'],monitor(other)['latest']['prior_var_95'])
    def test_warmup_and_breach(self):
        risk=monitor(backtest(demo()[:200],strategy='balanced'))
        self.assertIn('max_asset_weight',risk['daily'][0]['breaches'])
        self.assertIsNone(risk['daily'][0]['daily_var_95'])
        self.assertEqual(risk['var_forecast_days'],len(risk['daily'])-63)
        self.assertEqual(len(risk['stress']),3)
    def test_nonmutation(self):
        run=backtest(demo()[:200]); before=copy.deepcopy(run);monitor(run);self.assertEqual(run,before)
