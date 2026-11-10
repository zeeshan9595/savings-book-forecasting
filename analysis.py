"""Reproducible analysis for the illustrative savings-book case study.

Run from the repository root:
    python run_analysis.py

All outputs are descriptive/illustrative. No causal or production forecast claims.
"""
from __future__ import annotations
from pathlib import Path
import warnings
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.holtwinters import ExponentialSmoothing

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
OUTPUT = ROOT / "outputs"
PRODUCTS = ["EASY_ACCESS", "FIXED_1YR", "FIXED_2YR", "FIXED_5YR"]


def load_data():
    balances = pd.read_csv(DATA / "monthly_balances.csv", parse_dates=["month"])
    rates = pd.read_csv(DATA / "market_rates.csv", parse_dates=["rate_date"])
    flows = pd.read_csv(DATA / "monthly_flows.csv", parse_dates=["month"])
    cohorts = pd.read_csv(DATA / "cohort_retention.csv", parse_dates=["cohort_month"])
    balances["total_balance"] = balances[PRODUCTS].sum(axis=1)
    flows["net_flows"] = flows["gross_inflows"] - flows["gross_outflows"]
    return balances, rates, flows, cohorts


def forecast_values(train: pd.Series, horizon: int, model: str) -> np.ndarray:
    """Forecast one expanding-window fold without accessing future observations."""
    if model == "Naive":
        return np.repeat(float(train.iloc[-1]), horizon)
    if model == "Drift":
        slope = (float(train.iloc[-1]) - float(train.iloc[0])) / (len(train) - 1)
        return float(train.iloc[-1]) + slope * np.arange(1, horizon + 1)
    if model == "ARIMA(1,1,1)":
        fitted = ARIMA(train, order=(1, 1, 1)).fit()
        return np.asarray(fitted.forecast(horizon), dtype=float)
    if model == "Damped Holt-Winters":
        fitted = ExponentialSmoothing(
            train, trend="add", seasonal=None, damped_trend=True
        ).fit(optimized=True)
        return np.asarray(fitted.forecast(horizon), dtype=float)
    raise ValueError(f"Unknown model: {model}")


def rolling_origin_backtest(series: pd.Series, horizons=(1, 3, 6), min_train=9):
    """Expanding-window backtest; overlapping forecast windows are retained.

    Metrics are pooled across all origin/step predictions for each horizon.
    Predictions are not independent because windows can overlap.
    """
    models = ["Naive", "Drift", "ARIMA(1,1,1)", "Damped Holt-Winters"]
    records = []
    for horizon in horizons:
        for origin in range(min_train, len(series) - horizon + 1):
            train = series.iloc[:origin]
            actual = series.iloc[origin:origin + horizon]
            for model in models:
                pred = forecast_values(train, horizon, model)
                for step, (date, observed, estimate) in enumerate(
                    zip(actual.index, actual.to_numpy(), pred), start=1
                ):
                    records.append({
                        "horizon": horizon, "origin_n": origin, "step": step,
                        "target_month": date, "model": model,
                        "actual": float(observed), "forecast": float(estimate),
                        "error": float(observed - estimate),
                    })
    predictions = pd.DataFrame(records)
    summary = (
        predictions.groupby(["horizon", "model"])
        .apply(lambda g: pd.Series({
            "origins": g["origin_n"].nunique(),
            "predictions": len(g),
            "MAE": mean_absolute_error(g["actual"], g["forecast"]),
            "RMSE": mean_squared_error(g["actual"], g["forecast"]) ** 0.5,
            "MAPE_pct": np.mean(np.abs(g["error"] / g["actual"])) * 100,
            "mean_error_bias": g["error"].mean(),
        }), include_groups=False)
        .reset_index()
    )
    return predictions, summary


def reconcile_flows(balances: pd.DataFrame, flows: pd.DataFrame) -> pd.DataFrame:
    """Compare net flows with balance movements; residual is unexplained, not assigned."""
    movement = balances[["month", "total_balance"]].copy()
    movement["month"] = movement["month"].dt.to_period("M").dt.to_timestamp()
    movement["balance_change"] = movement["total_balance"].diff()
    flow = flows[["month", "gross_inflows", "gross_outflows", "net_flows"]].copy()
    flow["month"] = flow["month"].dt.to_period("M").dt.to_timestamp()
    result = flow.merge(movement[["month", "balance_change"]], on="month", how="left")
    result["unexplained_residual"] = result["balance_change"] - result["net_flows"]
    return result


def deposit_beta(rates: pd.DataFrame) -> pd.DataFrame:
    """Calculate descriptive adjacent-snapshot pass-through only where BoE moves."""
    r = rates.sort_values("rate_date").copy()
    r["d_boe"] = r["boe_base_rate"].diff()
    r["d_ours"] = r["EASY_ACCESS_ours"].diff()
    r["d_competitor"] = r["EASY_ACCESS_competitor"].diff()
    r["ours_interval_beta"] = np.where(r["d_boe"].abs() > 1e-12, r["d_ours"] / r["d_boe"], np.nan)
    r["competitor_interval_beta"] = np.where(r["d_boe"].abs() > 1e-12, r["d_competitor"] / r["d_boe"], np.nan)
    return r[["rate_date", "d_boe", "d_ours", "d_competitor",
              "ours_interval_beta", "competitor_interval_beta"]]


def cohort_scenarios(initial_balance=47000.0, months=24):
    """Separate customer-retention index from average-balance-per-retained-customer index.

    A starting customer count is not present in the source data, so this uses indices,
    not fabricated customer counts or observed average balances.
    """
    assumptions = {
        "Low churn": (0.010, 0.005),
        "Base": (0.015, 0.003),
        "High churn": (0.030, 0.002),
    }
    rows = []
    for name, (monthly_churn, monthly_avg_balance_growth) in assumptions.items():
        for month in range(months + 1):
            retention_index = (1 - monthly_churn) ** month
            avg_balance_index = (1 + monthly_avg_balance_growth) ** month
            rows.append({
                "scenario": name, "month": month,
                "assumed_monthly_churn": monthly_churn,
                "assumed_monthly_avg_balance_growth": monthly_avg_balance_growth,
                "customer_retention_index": retention_index,
                "average_balance_per_retained_customer_index": avg_balance_index,
                "projected_cohort_balance": initial_balance * retention_index * avg_balance_index,
            })
    return pd.DataFrame(rows)


def maturity_runoff_scenarios(balances: pd.DataFrame, months=60):
    """Assumption-led proxy only; product balances do not contain account maturity dates.

    Spreads each closing fixed-term product balance evenly across its nominal term.
    This is not an actual contractual maturity ladder.
    """
    closing = balances.iloc[-1]
    terms = {"FIXED_1YR": 12, "FIXED_2YR": 24, "FIXED_5YR": 60}
    rows = []
    for month in range(1, months + 1):
        row = {"month_ahead": month}
        for product, term in terms.items():
            balance = float(closing[product])
            row[f"{product}_assumed_maturity"] = balance / term if month <= term else 0.0
        row["total_assumed_maturity"] = sum(
            row[f"{p}_assumed_maturity"] for p in terms
        )
        rows.append(row)
    return pd.DataFrame(rows)


def main():
    warnings.filterwarnings("ignore")
    OUTPUT.mkdir(exist_ok=True)
    balances, rates, flows, cohorts = load_data()
    if len(balances) != 18 or balances["month"].duplicated().any():
        raise ValueError("Expected 18 unique monthly balance observations.")
    if balances[PRODUCTS].isna().any().any() or (balances[PRODUCTS] < 0).any().any():
        raise ValueError("Product balances must be present and non-negative.")
    if not np.allclose(balances["total_balance"], balances[PRODUCTS].sum(axis=1)):
        raise ValueError("Total balance does not equal the sum of product balances.")

    series = balances.set_index("month")["total_balance"].asfreq("ME")
    predictions, backtest = rolling_origin_backtest(series)
    reconciliation = reconcile_flows(balances, flows)
    beta = deposit_beta(rates)
    cohort = cohort_scenarios()
    maturity = maturity_runoff_scenarios(balances)

    predictions.to_csv(OUTPUT / "rolling_origin_predictions.csv", index=False)
    backtest.to_csv(OUTPUT / "rolling_origin_summary.csv", index=False)
    reconciliation.to_csv(OUTPUT / "flow_reconciliation.csv", index=False)
    beta.to_csv(OUTPUT / "deposit_beta_intervals.csv", index=False)
    cohort.to_csv(OUTPUT / "cohort_scenarios.csv", index=False)
    maturity.to_csv(OUTPUT / "maturity_runoff_proxy.csv", index=False)

    residual = reconciliation["unexplained_residual"].dropna()
    print("DATA CHECKS: PASS")
    print(f"Months: {len(balances)} | Closing book: £{series.iloc[-1]:,.0f}")
    print(f"Flow reconciliation: cumulative residual £{residual.sum():,.0f}; "
          f"mean absolute monthly residual £{residual.abs().mean():,.0f}; "
          f"maximum £{residual.abs().max():,.0f}")
    print("\nROLLING-ORIGIN RESULTS (overlapping expanding-window forecasts):")
    print(backtest.round(2).to_string(index=False))
    print("\nOutputs written to ./outputs/")
    print("Maturity schedule is an evenly allocated proxy, not an account-level ladder.")


if __name__ == "__main__":
    main()
