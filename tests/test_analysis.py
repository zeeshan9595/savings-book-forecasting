import unittest
import numpy as np
import pandas as pd
from analysis import (
    load_data, forecast_values, rolling_origin_backtest,
    reconcile_flows, deposit_beta, cohort_scenarios, maturity_runoff_scenarios
)

class SavingsAnalysisTests(unittest.TestCase):
    def test_source_data_and_balance_totals(self):
        balances, rates, flows, cohorts = load_data()
        self.assertEqual(len(balances), 18)
        self.assertEqual(len(rates), 7)
        self.assertEqual(len(flows), 18)
        self.assertTrue((balances[["EASY_ACCESS","FIXED_1YR","FIXED_2YR","FIXED_5YR"]] >= 0).all().all())
        self.assertAlmostEqual(float(balances.total_balance.iloc[-1]), 816808.0)

    def test_naive_and_drift_forecasts(self):
        s = pd.Series([10.0, 12.0, 14.0, 16.0])
        np.testing.assert_allclose(forecast_values(s, 2, "Naive"), [16, 16])
        np.testing.assert_allclose(forecast_values(s, 2, "Drift"), [18, 20])

    def test_reconciliation_flags_nonzero_residual(self):
        b, _, f, _ = load_data()
        result = reconcile_flows(b, f)
        self.assertAlmostEqual(float(result.unexplained_residual.dropna().sum()), 250808.0)
        self.assertAlmostEqual(float(result.unexplained_residual.abs().max()), 82000.0)

    def test_cohort_indices_separate_retention_and_balance(self):
        result = cohort_scenarios(initial_balance=47000, months=24)
        base_end = result[(result.scenario == "Base") & (result.month == 24)].iloc[0]
        self.assertLess(base_end.customer_retention_index, 1.0)
        self.assertGreater(base_end.average_balance_per_retained_customer_index, 1.0)
        self.assertGreater(base_end.projected_cohort_balance, 0)

    def test_maturity_proxy_is_labelled_and_nonnegative(self):
        b, _, _, _ = load_data()
        result = maturity_runoff_scenarios(b)
        self.assertEqual(len(result), 60)
        self.assertTrue((result.total_assumed_maturity >= 0).all())
        self.assertAlmostEqual(result.loc[result.month_ahead == 1, "total_assumed_maturity"].iloc[0],
                               316141/12 + 277484/24 + 52750/60)

    def test_rolling_origin_covers_all_benchmarks(self):
        b, _, _, _ = load_data()
        s = b.set_index("month").total_balance.asfreq("ME")
        preds, summary = rolling_origin_backtest(s)
        self.assertEqual(set(summary.model), {"Naive","Drift","ARIMA(1,1,1)","Damped Holt-Winters"})
        self.assertEqual(set(summary.horizon), {1,3,6})
        self.assertGreater(len(preds), 0)

if __name__ == "__main__":
    unittest.main()
