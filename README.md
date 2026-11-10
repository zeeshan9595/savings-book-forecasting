# Savings book forecasting: model comparison, deposit beta and rate-shock scenarios

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/zeeshan9595/savings-book-forecasting/blob/main/savings_book_forecasting.ipynb) [![Live dashboard](https://img.shields.io/badge/Live-dashboard-003366)](https://zeeshan9595.github.io/savings-book-forecasting/)

**[Open the interactive dashboard](https://zeeshan9595.github.io/savings-book-forecasting/)** for the total-book forecast, product mix, illustrative net flows, market-rate comparison and interest-cost sensitivities.

This independent case study examines a retail savings book at total (macro) and product (micro) level: easy access, 1-year, 2-year and 5-year fixed-rate products. It demonstrates selected techniques used in savings MI, forecasting and rate-sensitivity analysis.

> **Data and scope:** All figures are illustrative. The dataset contains 18 hand-built monthly observations from January 2023 to June 2024, with a closing book of approximately £817k. It is not bank data and should not be interpreted as a forecast or analysis of an actual institution.

## What the analysis covers

| Area | Method |
|---|---|
| Balance trends | Month-end balances by product and product mix |
| Macro forecasting | Damped Holt-Winters and ARIMA(1,1,1), using a 15-month training sample and 3-month holdout |
| Diagnostics | Augmented Dickey-Fuller tests and training-sample variance inflation factors |
| Rate sensitivity | Easy-access balance changes against changes in our rate spread and the Bank of England base rate |
| Deposit beta | Cumulative pass-through over the January–October 2023 hiking period |
| Rate shocks | Parallel rate changes and competitor-only rate moves |
| Cohort projections | Retention and balance paths under explicitly assumed churn and balance-growth rates |
| Dashboard | Interactive summary of the illustrative dataset and selected outputs |

## Results and interpretation

### Macro forecast: three-month holdout

| Model | MAPE | MAE | RMSE |
|---|---:|---:|---:|
| ARIMA(1,1,1) | 8.3% | £65.1k | £68.2k |
| Holt-Winters (damped) | 10.5% | £82.8k | £85.6k |

ARIMA had the lower error on this particular three-month holdout. This is a small test window, not evidence that ARIMA will outperform in production. The models are refitted on all 18 observations for the six-month illustrative projections: approximately £993k for ARIMA and £1.06m for Holt-Winters, compared with £817k at the final observed month.

Both projections extend the recent upward trend. They do not incorporate a forecast of market rates, customer behaviour, maturities or management actions. The notebook reports AIC and BIC for reference but does not compare those values across the two model families.

### Rate sensitivity: why the levels coefficient is not used as a decision rule

The initial levels regression included a time trend, the difference between our easy-access rate and the competitor rate, and the Bank of England base rate. The rate-spread coefficient was approximately **−£116k per percentage point**. Interpreting that coefficient directly would imply that improving our rate relative to the competitor reduces balances.

The diagnostics give reasons not to rely on that interpretation:

- The ADF test cannot reject a unit root in the easy-access balance level (p = 0.67). With such a short series, this test has low power.
- Training-sample VIFs are approximately **17.2 for trend**, **7.4 for rate spread** and **7.0 for the base rate**, indicating substantial predictor overlap.

A first-difference specification,

```text
Δ Balance = α + β₁ Δ Rate Spread + β₂ Δ Bank of England Rate + error
```

produces a positive spread coefficient of approximately **£65.6k per percentage point**, but it is not statistically significant (p = 0.25; n = 17; R² = 0.10). Adding a one-month lag does not provide convincing evidence of a relationship. The spread changes in only a small number of months, so the coefficient is weakly identified.

The notebook therefore retains the levels model as a diagnostic comparison but does **not** use its confounded coefficients to label upside, base and downside balance forecasts.

### Deposit beta and rate shocks

Across the four rate snapshots from January to October 2023, the Bank of England base rate increased from 3.50% to 5.25%. Over the same endpoints, our easy-access rate increased from 3.00% to 4.75%, giving a cumulative pass-through ratio of **1.00**. The competitor series gives **1.09**.

```text
Cumulative deposit beta = change in savings rate / change in Bank of England base rate
```

This is a descriptive endpoint ratio over one hiking period, not a stable marginal beta estimate. The sparse snapshots do not support conclusions about the timing or consistency of pass-through.

| Scenario | Annual easy-access interest cost change | Illustrative balance effect |
|---|---:|---:|
| Parallel +25bp | +£426 | −£1.4k |
| Parallel +100bp | +£1,704 | −£5.6k |
| Parallel −100bp | −£1,704 | +£5.6k |
| Competitors +25bp, base fixed | £0 | −£16.4k |
| Competitors +50bp, base fixed | £0 | −£32.8k |

The interest-cost changes are mechanical calculations using the closing easy-access balance and the assumed pass-through. The balance effects use the weakly identified differenced coefficient and are highly uncertain; they are directional illustrations, not behavioural forecasts.

### Cohort projections

The cohort source data contains 45 observations, all with 100% recorded retention. It therefore cannot estimate actual churn. The notebook omits a misleading all-100% historical heatmap and instead shows scenarios using assumed monthly churn and average-balance growth. These are assumptions for sensitivity analysis, not fitted customer-retention estimates.

### Transaction-flow reconciliation

The illustrative monthly net-flow series does **not** reconcile to month-on-month changes in the savings balances. From February 2023 to June 2024, the cumulative difference between balance movements and recorded net flows is approximately **£250.8k**; the largest monthly absolute gap is **£82.0k**. No movement bridge is supplied to explain the difference.

The flow chart is therefore a separate illustrative activity series. It must not be read as a reconciled cash-flow or ledger bridge. A production analysis would require consistent opening and closing balances and a complete movement bridge covering all relevant balance changes.

## Limitations

- Only 18 monthly balance observations and seven market-rate snapshots are available.
- The macro comparison uses one three-month holdout; rolling-origin validation and simple benchmark models are not included.
- The time series and regression coefficients are illustrative and highly sensitive to the short sample.
- No account-level maturity dates, customer-level product migrations or reliable churn events are available.
- The transaction-flow series does not reconcile to balance movements.
- No asset-side data is provided, so net interest margin, liquidity coverage and full asset-liability management measures are outside scope.

## Further development

A stronger second version would add rolling-origin forecast evaluation against naïve and drift benchmarks, account-level maturity ladders, customer-level product migration, a reconciled balance movement bridge and a more defensible deposit-beta analysis across both hiking and easing periods.

## Tools

Python, pandas, statsmodels, scikit-learn, matplotlib, seaborn, Google Colab and Chart.js.

---

Zeeshan Azeem Khalid · [LinkedIn](https://linkedin.com/in/zeeshan-azeem-khalid) · Related projects: [Lending Club credit decisions](https://github.com/zeeshan9595/lending-club-credit-decisions) · [Fraud detection leakage audit](https://github.com/zeeshan9595/Fraud-Detection-using-AI-and-ML)
