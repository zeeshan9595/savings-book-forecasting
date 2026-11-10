"""Reproducible analysis for the illustrative retail savings-book case study.

Run from the repository root with: python run_analysis.py
All outputs are descriptive/illustrative; no causal or production forecast claims.
"""
from __future__ import annotations

import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.holtwinters import ExponentialSmoothing

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
OUTPUT = ROOT / "outputs"
PRODUCTS = ["EASY_ACCESS", "FIXED_1YR", "FIXED_2YR", "FIXED_5YR"]
MODELS = ["Naive", "Drift", "ARIMA(1,1,1)", "Damped Holt-Winters"]


def load_data():
    """Load the four source tables and derive total balances and net flows."""
    balances = pd.read_csv(DATA / "monthly_balances.csv", parse_dates=["month"])
    rates = pd.read_csv(DATA / "market_rates.csv", parse_dates=["rate_date"])
    flows = pd.read_csv(DATA / "monthly_flows.csv", parse_dates=["month"])
    cohorts = pd.read_csv(DATA / "cohort_retention.csv", parse_dates=["cohort_month"])
    balances["total_balance"] = balances[PRODUCTS].sum(axis=1)
    flows["net_flows"] = flows["gross_inflows"] - flows["gross_outflows"]
    return balances, rates, flows, cohorts


def validate_inputs(balances, rates, flows, cohorts):
    """Fail fast on schema, missing-value, chronology and range errors."""
    schemas = {
        "balances": (balances, {"month", *PRODUCTS}),
        "rates": (rates, {
            "rate_date", "EASY_ACCESS_ours", "EASY_ACCESS_competitor",
            "FIXED_1YR_ours", "FIXED_1YR_competitor", "boe_base_rate"
        }),
        "flows": (flows, {"month", "gross_inflows", "gross_outflows"}),
        "cohorts": (cohorts, {"cohort_month", "months_since_acq", "retention_rate"}),
    }
    for name, (frame, required) in schemas.items():
        missing = required.difference(frame.columns)
        if missing:
            raise ValueError(f"{name} is missing required columns: {sorted(missing)}")
        if frame.empty or frame[list(required)].isna().any().any():
            raise ValueError(f"{name} contains no rows or missing required values.")

    if balances["month"].duplicated().any() or not balances["month"].is_monotonic_increasing:
        raise ValueError("Balance months must be unique and chronological.")
    periods = balances["month"].dt.to_period("M")
    if not periods.diff().dropna().eq(1).all():
        raise ValueError("Balance observations must form a continuous monthly series.")
    if len(balances) < 12:
        raise ValueError("At least 12 monthly balance observations are required.")
    if not np.isfinite(balances[PRODUCTS].to_numpy(dtype=float)).all():
        raise ValueError("Product balances must be finite numeric values.")
    if (balances[PRODUCTS] < 0).any().any():
        raise ValueError("Product balances cannot be negative.")

    for name, frame in (("flows", flows), ("rates", rates)):
        date_col = "month" if name == "flows" else "rate_date"
        if frame[date_col].duplicated().any() or not frame[date_col].is_monotonic_increasing:
            raise ValueError(f"{name} dates must be unique and chronological.")
    if not flows["month"].dt.to_period("M").reset_index(drop=True).equals(
        balances["month"].dt.to_period("M").reset_index(drop=True)
    ):
        raise ValueError("Flow months must align one-to-one with balance months.")
    if (flows[["gross_inflows", "gross_outflows"]] < 0).any().any():
        raise ValueError("Gross inflows and outflows cannot be negative.")
    if not cohorts["retention_rate"].between(0, 100).all():
        raise ValueError("Cohort retention rates must be between 0 and 100.")
    if (cohorts["months_since_acq"] < 0).any():
        raise ValueError("Months since acquisition cannot be negative.")

    return {
        "balance_months": len(balances),
        "rate_snapshots": len(rates),
        "cohort_observations": len(cohorts),
        "cohort_retention_min_pct": float(cohorts["retention_rate"].min()),
        "cohort_retention_max_pct": float(cohorts["retention_rate"].max()),
        "closing_total_balance": float(balances[PRODUCTS].iloc[-1].sum()),
    }


def forecast_values(train: pd.Series, horizon: int, model: str) -> np.ndarray:
    """Forecast a fold using training observations only."""
    if horizon < 1 or len(train) < 2:
        raise ValueError("Forecast horizon must be positive and training data needs 2+ points.")
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
    """Expanding-window validation with pooled metrics for overlapping windows."""
    if not series.index.is_monotonic_increasing or series.index.has_duplicates:
        raise ValueError("Forecast series index must be unique and chronological.")
    if series.isna().any() or not np.isfinite(series.to_numpy(dtype=float)).all():
        raise ValueError("Forecast series must contain finite, non-missing values.")
    if min_train < 2 or min_train >= len(series):
        raise ValueError("min_train must be >=2 and smaller than the series length.")

    records = []
    for horizon in horizons:
        if horizon < 1:
            raise ValueError("All forecast horizons must be positive.")
        for origin in range(min_train, len(series) - horizon + 1):
            train = series.iloc[:origin]
            actual = series.iloc[origin:origin + horizon]
            for model in MODELS:
                forecast = forecast_values(train, horizon, model)
                for step, (date, observed, estimate) in enumerate(
                    zip(actual.index, actual.to_numpy(), forecast), start=1
                ):
                    records.append({
                        "horizon": horizon, "origin_n": origin, "step": step,
                        "target_month": date, "model": model,
                        "actual": float(observed), "forecast": float(estimate),
                        "error": float(observed - estimate),
                    })

    predictions = pd.DataFrame(records)
    summary_rows = []
    for (horizon, model), group in predictions.groupby(["horizon", "model"]):
        summary_rows.append({
            "horizon": int(horizon),
            "model": model,
            "origins": int(group["origin_n"].nunique()),
            "predictions": int(len(group)),
            "MAE": float(mean_absolute_error(group["actual"], group["forecast"])),
            "RMSE": float(mean_squared_error(group["actual"], group["forecast"]) ** 0.5),
            "MAPE_pct": float(np.mean(np.abs(group["error"] / group["actual"])) * 100),
            "mean_error_bias": float(group["error"].mean()),
        })
    return predictions, pd.DataFrame(summary_rows)


def reconcile_flows(balances: pd.DataFrame, flows: pd.DataFrame) -> pd.DataFrame:
    """Compare net flows with balance movements; never allocate the residual."""
    movement = balances[["month", "total_balance"]].copy()
    movement["month"] = movement["month"].dt.to_period("M").dt.to_timestamp()
    movement["balance_change"] = movement["total_balance"].diff()
    flow = flows[["month", "gross_inflows", "gross_outflows", "net_flows"]].copy()
    flow["month"] = flow["month"].dt.to_period("M").dt.to_timestamp()
    result = flow.merge(movement[["month", "balance_change"]], on="month", how="left")
    result["unexplained_residual"] = result["balance_change"] - result["net_flows"]
    return result


def deposit_beta(rates: pd.DataFrame) -> pd.DataFrame:
    """Descriptive adjacent-snapshot pass-through where the BoE rate changes."""
    r = rates.sort_values("rate_date").copy()
    r["d_boe"] = r["boe_base_rate"].diff()
    r["d_ours"] = r["EASY_ACCESS_ours"].diff()
    r["d_competitor"] = r["EASY_ACCESS_competitor"].diff()
    valid = r["d_boe"].abs() > 1e-12
    r["ours_interval_beta"] = np.divide(
        r["d_ours"], r["d_boe"], out=np.full(len(r), np.nan), where=valid
    )
    r["competitor_interval_beta"] = np.divide(
        r["d_competitor"], r["d_boe"], out=np.full(len(r), np.nan), where=valid
    )
    return r[[
        "rate_date", "d_boe", "d_ours", "d_competitor",
        "ours_interval_beta", "competitor_interval_beta"
    ]]


def cohort_observed_summary(cohorts: pd.DataFrame) -> pd.DataFrame:
    """Summarise the supplied cohort observations without imputing churn."""
    return (
        cohorts.groupby("months_since_acq")["retention_rate"]
        .agg(observations="count", mean_retention_pct="mean",
             min_retention_pct="min", max_retention_pct="max")
        .reset_index()
        .sort_values("months_since_acq")
    )


def cohort_scenarios(initial_balance=47000.0, months=24):
    """Scenario indices; no customer counts or observed average balances are invented."""
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
    """Even-allocation sensitivity proxy, not an account-level maturity ladder."""
    closing = balances.iloc[-1]
    terms = {"FIXED_1YR": 12, "FIXED_2YR": 24, "FIXED_5YR": 60}
    rows = []
    for month in range(1, months + 1):
        row = {"month_ahead": month}
        for product, term in terms.items():
            balance = float(closing[product])
            row[f"{product}_assumed_maturity"] = balance / term if month <= term else 0.0
        row["total_assumed_maturity"] = sum(
            row[f"{product}_assumed_maturity"] for product in terms
        )
        rows.append(row)
    return pd.DataFrame(rows)


def main():
    warnings.filterwarnings("ignore")
    OUTPUT.mkdir(exist_ok=True)
    balances, rates, flows, cohorts = load_data()
    checks = validate_inputs(balances, rates, flows, cohorts)
    balances["total_balance"] = balances[PRODUCTS].sum(axis=1)

    series = balances.set_index("month")["total_balance"].asfreq("ME")
    if series.isna().any():
        raise ValueError("Monthly balance series contains missing month-end observations.")

    predictions, backtest = rolling_origin_backtest(series)
    reconciliation = reconcile_flows(balances, flows)
    beta = deposit_beta(rates)
    observed_cohorts = cohort_observed_summary(cohorts)
    cohort = cohort_scenarios()
    maturity = maturity_runoff_scenarios(balances)

    predictions.to_csv(OUTPUT / "rolling_origin_predictions.csv", index=False)
    backtest.to_csv(OUTPUT / "rolling_origin_summary.csv", index=False)
    reconciliation.to_csv(OUTPUT / "flow_reconciliation.csv", index=False)
    beta.to_csv(OUTPUT / "deposit_beta_intervals.csv", index=False)
    observed_cohorts.to_csv(OUTPUT / "observed_cohort_retention_summary.csv", index=False)
    cohort.to_csv(OUTPUT / "cohort_scenarios.csv", index=False)
    maturity.to_csv(OUTPUT / "maturity_runoff_proxy.csv", index=False)
    pd.DataFrame([checks]).to_csv(OUTPUT / "data_quality_checks.csv", index=False)

    residual = reconciliation["unexplained_residual"].dropna()
    print("DATA CHECKS: PASS")
    print(f"Months: {checks['balance_months']} | Closing book: £{checks['closing_total_balance']:,.0f}")
    print(f"Observed cohort retention range: {checks['cohort_retention_min_pct']:.1f}%–"
          f"{checks['cohort_retention_max_pct']:.1f}% across {checks['cohort_observations']} rows")
    print(f"Flow reconciliation: cumulative residual £{residual.sum():,.0f}; "
          f"mean absolute monthly residual £{residual.abs().mean():,.0f}; "
          f"maximum £{residual.abs().max():,.0f}")
    print("\nROLLING-ORIGIN RESULTS (overlapping expanding-window forecasts):")
    print(backtest.round(2).to_string(index=False))
    print("\nOutputs written to ./outputs/")
    print("Maturity schedule is an evenly allocated proxy, not an account-level ladder.")


if __name__ == "__main__":
    main()
