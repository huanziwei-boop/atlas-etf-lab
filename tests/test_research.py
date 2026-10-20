import unittest
from atlas.data import demo
from atlas.engine import backtest, rebalance_cost
from atlas.evaluate import evaluate

class ResearchTests(unittest.TestCase):
    def test_entry_cost_exact_solution(self):
        post, traded, cost=rebalance_cost(100,[0,0],[.6,.4],.025)
        self.assertAlmostEqual(post,100/1.025)
        self.assertAlmostEqual(traded,post)
        self.assertAlmostEqual(post+cost,100)

    def test_rebalance_budget_and_actual_notional(self):
        post,traded,cost=rebalance_cost(100,[.8,.2],[.3,.7],.01)
        self.assertAlmostEqual(traded,abs(post*.3-80)+abs(post*.7-20))
        self.assertAlmostEqual(cost,.01*traded)
        self.assertAlmostEqual(post+cost,100)

    def test_zero_turnover_zero_cost(self):
        post,traded,cost=rebalance_cost(100,[.6,.4],[.6,.4],.01)
        self.assertAlmostEqual(post,100)
        self.assertAlmostEqual(traded,0)
        self.assertAlmostEqual(cost,0)

    def test_signal_execution_return_strict_order(self):
        run=backtest(demo()[:180],'inverse_vol')
        for trade in run['trades']:
            self.assertLess(trade['signal_date'],trade['execution_date'])
            self.assertLess(trade['execution_date'],trade['return_date'])
            self.assertAlmostEqual(trade['pre_trade_nav'],trade['post_trade_nav']+trade['cost_nav'])

    def test_execution_price_cannot_change_signal(self):
        rows=demo()[:180]
        before=backtest(rows,'inverse_vol')
        execution=before['trades'][0]['execution_date']
        modified=[dict(r) for r in rows]
        for r in modified:
            if r['date']==execution: r['SPY']*=3
        after=backtest(modified,'inverse_vol')
        self.assertEqual(before['trades'][0]['weights'],after['trades'][0]['weights'])

    def test_future_test_data_cannot_change_selection(self):
        rows=demo()[:400]; split=rows[240]['date']
        before=evaluate(rows,split)
        modified=[dict(r) for r in rows]
        for i,r in enumerate(modified[241:]):
            r['SPY']*=1+.01*i
        after=evaluate(modified,split)
        self.assertEqual(before['selected_strategy'],after['selected_strategy'])
        self.assertEqual([r['training'] for r in before['candidates']],
                         [r['training'] for r in after['candidates']])
        self.assertNotEqual(before['candidates'][0]['holdout'],after['candidates'][0]['holdout'])

    def test_holdout_boundary_and_counts(self):
        rows=demo()[:400]; result=evaluate(rows,rows[240]['date'])
        for item in result['candidates']:
            self.assertEqual(item['training']['end'],item['holdout']['start'])
            self.assertEqual(item['holdout']['return_observations'],159)

    def test_invalid_split_and_zero_delay_rejected(self):
        rows=demo()[:400]
        for split in ['2010-01-01','2030-01-01',rows[70]['date']]:
            with self.assertRaises(ValueError): evaluate(rows,split)
        with self.assertRaises(ValueError): backtest(rows,signal_lag=0)

if __name__=='__main__': unittest.main()
