import unittest

import numpy as np
import pandas as pd

from analysis import (
    cohort_observed_summary,
    cohort_scenarios,
    deposit_beta,
    forecast_values,
    load_data,
    maturity_runoff_scenarios,
    reconcile_flows,
    rolling_origin_backtest,
    validate_inputs,
)


class SavingsAnalysisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.balances, cls.rates, cls.flows, cls.cohorts = load_data()

    def test_source_data_and_balance_totals(self):
        checks = validate_inputs(self.balances, self.rates, self.flows, self.cohorts)
        self.assertEqual(checks["balance_months"], 18)
        self.assertEqual(checks["rate_snapshots"], 7)
        self.assertEqual(checks["cohort_observations"], 45)
        self.assertAlmostEqual(checks["closing_total_balance"], 816808.0)

    def test_validation_rejects_duplicate_months(self):
        broken = self.balances.copy()
        broken.loc[1, "month"] = broken.loc[0, "month"]
        with self.assertRaisesRegex(ValueError, "unique and chronological"):
            validate_inputs(broken, self.rates, self.flows, self.cohorts)

    def test_validation_rejects_monthly_gaps(self):
        broken = self.balances.copy()
        broken.loc[5, "month"] = pd.Timestamp("2023-06-15")
        with self.assertRaisesRegex(ValueError, "continuous monthly series"):
            validate_inputs(broken, self.rates, self.flows, self.cohorts)

    def test_validation_rejects_nonfinite_market_rates(self):
        broken = self.rates.copy()
        broken.loc[0, "boe_base_rate"] = np.inf
        with self.assertRaisesRegex(ValueError, "finite numeric values"):
            validate_inputs(self.balances, broken, self.flows, self.cohorts)

    def test_validation_rejects_negative_product_balance(self):
        broken = self.balances.copy()
        broken.loc[0, "EASY_ACCESS"] = -1
        with self.assertRaisesRegex(ValueError, "cannot be negative"):
            validate_inputs(broken, self.rates, self.flows, self.cohorts)

    def test_naive_and_drift_forecasts(self):
        series = pd.Series([10.0, 12.0, 14.0, 16.0])
        np.testing.assert_allclose(forecast_values(series, 2, "Naive"), [16, 16])
        np.testing.assert_allclose(forecast_values(series, 2, "Drift"), [18, 20])

    def test_forecast_rejects_invalid_horizon(self):
        with self.assertRaises(ValueError):
            forecast_values(pd.Series([1.0, 2.0]), 0, "Naive")

    def test_rolling_origin_has_all_models_and_horizons(self):
        series = self.balances.set_index("month").total_balance.asfreq("ME")
        predictions, summary = rolling_origin_backtest(series)
        self.assertEqual(set(summary.model), {
            "Naive", "Drift", "ARIMA(1,1,1)", "Damped Holt-Winters"
        })
        self.assertEqual(set(summary.horizon), {1, 3, 6})
        self.assertTrue(np.isfinite(predictions[["actual", "forecast", "error"]]).all().all())
        self.assertTrue((summary["predictions"] > 0).all())

    def test_flow_reconciliation_retains_unexplained_residual(self):
        result = reconcile_flows(self.balances, self.flows)
        residual = result.unexplained_residual.dropna()
        self.assertAlmostEqual(float(residual.sum()), 250808.0)
        self.assertAlmostEqual(float(residual.abs().max()), 82000.0)
        self.assertEqual(len(residual), 17)

    def test_deposit_beta_skips_unchanged_base_rate_intervals(self):
        result = deposit_beta(self.rates)
        self.assertTrue(result.loc[result.d_boe.abs() <= 1e-12,
                                   "ours_interval_beta"].isna().all())
        self.assertTrue(result.loc[result.d_boe.abs() <= 1e-12,
                                   "competitor_interval_beta"].isna().all())
        self.assertTrue(result.loc[result.d_boe.abs() > 1e-12,
                                   "ours_interval_beta"].notna().all())

    def test_cohort_source_shows_no_observed_churn(self):
        summary = cohort_observed_summary(self.cohorts)
        self.assertEqual(int(summary.observations.sum()), 45)
        self.assertAlmostEqual(float(summary.min_retention_pct.min()), 100.0)
        self.assertAlmostEqual(float(summary.max_retention_pct.max()), 100.0)

    def test_cohort_observed_summary_does_not_invent_churn(self):
        summary = cohort_observed_summary(self.cohorts)
        self.assertEqual(int(summary.observations.sum()), 45)
        self.assertTrue((summary.min_retention_pct == 100).all())
        self.assertTrue((summary.max_retention_pct == 100).all())

    def test_cohort_scenarios_keep_components_separate(self):
        result = cohort_scenarios(initial_balance=47000, months=24)
        base_end = result[(result.scenario == "Base") & (result.month == 24)].iloc[0]
        self.assertLess(base_end.customer_retention_index, 1.0)
        self.assertGreater(base_end.average_balance_per_retained_customer_index, 1.0)
        self.assertGreater(base_end.projected_cohort_balance, 0)

    def test_maturity_proxy_is_nonnegative_and_has_60_months(self):
        result = maturity_runoff_scenarios(self.balances)
        self.assertEqual(len(result), 60)
        self.assertTrue((result.total_assumed_maturity >= 0).all())
        self.assertEqual(result.loc[result.month_ahead == 13,
                                    "FIXED_1YR_assumed_maturity"].iloc[0], 0.0)


if __name__ == "__main__":
    unittest.main()
