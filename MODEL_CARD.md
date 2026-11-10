# Model card — retail savings book case study

## Model purpose

This repository demonstrates a reproducible workflow for analysing a small, illustrative retail savings book. It is intended for learning, portfolio review and discussion of forecasting and savings analytics methods.

It is **not** designed or validated for production funding decisions, customer pricing, treasury limits, liquidity management, regulatory reporting or financial advice.

## Data and provenance

- 18 month-end balance observations, January 2023–June 2024.
- Seven market-rate snapshots.
- 18 monthly gross-flow observations.
- 45 cohort-retention observations; all supplied retention values are 100%.
- Hand-built illustrative data, not sourced from a bank or real customers.

No account-level maturity dates, customer-level churn events, contractual repricing dates or asset-side balances are supplied.

## Forecasting methods

The expanding-window backtest compares:
1. Naïve last-observation forecast.
2. Linear drift forecast.
3. ARIMA(1,1,1).
4. Damped Holt-Winters with additive trend and no seasonal component.

The first nine observations form the minimum training window. Forecast horizons are 1, 3 and 6 months. Pooled MAE, RMSE, MAPE and mean error are reported.

## Validation results

The drift benchmark has the lowest pooled error at each tested horizon in the supplied illustrative sample:

| Horizon | Drift MAPE | Drift MAE | Drift RMSE |
|---:|---:|---:|---:|
| 1 month | 4.55% | £30.0k | £34.2k |
| 3 months | 7.93% | £56.5k | £66.9k |
| 6 months | 7.45% | £52.9k | £62.3k |

The expanding windows overlap. Their predictions are therefore dependent, and the small sample makes these figures descriptive rather than statistically conclusive. The original 15-month/3-month holdout is retained as a separate, very small chronological comparison.

## Key assumptions and non-model calculations

- Deposit beta is a descriptive endpoint or adjacent-snapshot pass-through ratio, not a stable marginal estimate.
- Rate shocks calculate mechanical annualised interest-cost changes at a constant balance. No behavioural balance response is estimated.
- Cohort projections apply explicit monthly churn and average-balance-growth assumptions separately. The source cohort observations cannot estimate churn.
- The fixed-term maturity runoff proxy spreads closing balances evenly over nominal product terms. It is not a contractual maturity ladder.
- Flow reconciliation residuals remain unexplained; they are not assigned to interest, migration, transfers or adjustments without source evidence.

## Known limitations and risks

- Short, illustrative time series; no seasonal cycle can be reliably identified.
- Overlapping backtest folds; pooled errors are not independent.
- Structural changes and macroeconomic drivers are not modelled.
- Rate snapshots are sparse and lack balance-weighted realised customer rates.
- Cohort records contain no observed attrition.
- Product balances and net flows do not reconcile.
- No asset-side data, so NIM, liquidity coverage and full asset-liability management metrics are out of scope.

## Appropriate interpretation

Use the outputs to demonstrate analytical process, data-quality discipline and model benchmarking. Do not describe the results as actual bank performance, causal rate elasticity, a contractual maturity profile or production-grade forecasts.
