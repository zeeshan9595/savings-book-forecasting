# Retail savings book analytics: forecasting, rate sensitivity and funding scenarios

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/zeeshan9595/savings-book-forecasting/blob/main/savings_book_forecasting.ipynb) [![Live dashboard](https://img.shields.io/badge/Live-dashboard-003366)](https://zeeshan9595.github.io/savings-book-forecasting/)

**[Interactive dashboard](https://zeeshan9595.github.io/savings-book-forecasting/)** · **[Repository](https://github.com/zeeshan9595/savings-book-forecasting)**

An independent retail savings analytics case study covering total-book forecasting, product mix, deposit-rate pass-through, funding-cost sensitivity, cohort assumptions and fixed-term maturity scenarios.

> **Data integrity statement:** The project uses 18 hand-built monthly observations (January 2023–June 2024), seven market-rate snapshots and illustrative transaction/cohort records. These are not bank data. No actual customer-level, account-level or contractual maturity records are supplied. All model outputs and scenarios are illustrative.

## Project scope

| Workstream | Implementation |
|---|---|
| Savings book MI | Monthly balances for Easy Access, 1-year, 2-year and 5-year fixed products |
| Forecasting | ARIMA(1,1,1), damped Holt-Winters, naïve and drift benchmarks |
| Validation | Chronological three-month holdout plus expanding-window validation at 1-, 3- and 6-month horizons |
| Diagnostics | ADF tests, training-sample VIF and first-difference regression |
| Deposit beta | Cumulative hiking-cycle pass-through plus adjacent-snapshot interval ratios |
| Interest cost | Mechanical annualised cost sensitivities at a constant balance |
| Cohort modelling | Separate customer-retention and average-balance-per-retained-customer indices |
| Maturity analysis | Explicitly assumption-led runoff proxy plus a contractual maturity input template |
| Data quality | Product-balance checks and transaction-flow-to-balance movement reconciliation |
| Reproducibility | CSV source data, Python analysis module, requirements, runner and unit tests |

## Key findings

### 1. Savings book and product composition

The illustrative closing book in June 2024 is **£816,808**. The notebook charts the monthly balances and product mix across the four savings products. The balance series is intentionally retained as supplied; no missing customer or account activity has been fabricated to force a reconciliation.

### 2. Forecasting: a short holdout is not enough

The original chronological holdout contains 15 training months and three test months:

| Model | MAPE | MAE | RMSE |
|---|---:|---:|---:|
| ARIMA(1,1,1) | 8.30% | £65.4k | £68.4k |
| Damped Holt-Winters | 10.53% | £82.9k | £85.6k |

This result is specific to three months and should not be treated as model selection evidence.

The second validation layer uses expanding windows, a minimum of nine training months, and forecast horizons of 1, 3 and 6 months. Windows overlap; therefore pooled predictions are dependent and the results are indicative rather than a formal statistical comparison.

| Horizon | Model | Forecasts | MAPE | MAE | RMSE |
|---:|---|---:|---:|---:|---:|
| 1 month | Naïve | 9 | 7.21% | £45.6k | £55.2k |
| 1 month | Drift | 9 | **4.55%** | **£30.0k** | **£34.2k** |
| 1 month | ARIMA | 9 | 4.67% | £31.0k | £36.2k |
| 1 month | Damped Holt-Winters | 9 | 5.40% | £36.6k | £42.2k |
| 3 months | Naïve | 21 | 14.28% | £95.6k | £118.7k |
| 3 months | Drift | 21 | **7.93%** | **£56.5k** | **£66.9k** |
| 3 months | ARIMA | 21 | 8.83% | £63.0k | £77.4k |
| 3 months | Damped Holt-Winters | 21 | 9.25% | £65.8k | £74.0k |
| 6 months | Naïve | 24 | 27.84% | £198.9k | £217.4k |
| 6 months | Drift | 24 | **7.45%** | **£52.9k** | **£62.3k** |
| 6 months | ARIMA | 24 | 8.99% | £64.5k | £79.5k |
| 6 months | Damped Holt-Winters | 24 | 8.20% | £57.5k | £67.5k |

**Interpretation:** The drift benchmark has the lowest pooled MAPE, MAE and RMSE at all three horizons in this illustrative backtest. This is an important finding: more complex models do not automatically outperform a transparent benchmark. The small dataset, overlapping folds and synthetic observations limit generalisation.

### 3. Rate sensitivity and econometric diagnostics

The initial levels regression included a time trend, Easy Access rate spread versus the competitor, and the Bank of England base rate. Its spread coefficient was approximately **−£116k per percentage point**. This should not be used as a behavioural or causal estimate.

The ADF test cannot reject a unit root in the Easy Access balance level (p approximately 0.67), although the sample is too short for a strong conclusion. Training-sample VIFs indicate substantial overlap among predictors (trend approximately 17.2; spread approximately 7.4; base rate approximately 7.0).

The first-difference model estimates a positive spread coefficient of approximately **£65.6k per percentage point**, but it is statistically weak (p approximately 0.25; 17 observations; R² approximately 0.10). The lagged specification does not establish a reliable effect. No upside/base/downside balance forecast is now generated from the confounded levels regression.

### 4. Deposit beta: cumulative and interval views

Across the January–October 2023 endpoints, the Bank of England base rate increased from 3.50% to 5.25%; the Easy Access rate increased from 3.00% to 4.75%. The cumulative pass-through ratio is therefore **1.00**. The competitor series gives approximately **1.09**.

Version 2 also calculates adjacent-snapshot interval ratios only where the Bank of England rate changes. These are descriptive ratios based on seven sparse observations, not stable marginal deposit betas. A production analysis would need more frequent observations, product-specific pricing histories, balance-weighted deposit rates and both hiking and easing periods.

### 5. Interest-cost scenarios: mechanical, not behavioural

The rate-shock grid now calculates the annualised interest-cost impact from the assumed rate movement and the current Easy Access balance. It no longer converts the weakly identified regression coefficient into a customer-balance response.

For example, a parallel +100bp shock at a 1.00 pass-through assumption on a £170,433 balance implies approximately **£1,704 additional annual interest cost**, holding the balance constant. This is arithmetic under an explicit assumption, not a forecast of actual funding cost or customer response.

### 6. Cohort scenarios: retention separated from average balance

The supplied cohort file has 45 observations, all with 100% retention. It cannot estimate observed churn. Version 2 therefore models two separate indices:
- customer-retention index under an assumed monthly churn rate;
- average-balance-per-retained-customer index under an assumed monthly growth rate.

The projected cohort balance is the initial balance multiplied by these two indices. No customer count or observed average balance per customer is invented. The scenarios are sensitivities, not fitted retention forecasts.

### 7. Fixed-term maturity runoff: proxy and data requirement

The source has product-level closing balances but no account origination dates, contractual maturity dates, balances by vintage, or renewal instructions. A true maturity ladder cannot be built from these fields.

The notebook and Python module include a clearly labelled proxy that spreads each closing fixed-term balance evenly over its nominal term (12, 24 or 60 months). It is an assumption-led runoff illustration, not a contractual maturity schedule.

A blank template is included at `templates/fixed_term_maturity_template.csv`. Populate it with account or vintage-level opening balance, origination date, maturity date, rate, product and renewal/runoff assumption to build a real ladder.

### 8. Transaction-flow reconciliation: unresolved £250,808 residual

The transaction net-flow series does not reconcile to month-on-month changes in product balances. From February 2023 to June 2024:
- cumulative unexplained movement: **£250,808**;
- mean absolute monthly residual: approximately **£23,209**;
- largest absolute monthly residual: **£82,000**.

The residual is not assigned to interest, transfers, product migrations or other causes because those records are not provided. The chart is labelled as illustrative activity, not a ledger movement bridge. A blank movement-bridge template is provided at `templates/balance_movement_bridge_template.csv`.

## Repository structure

```text
.
├── README.md
├── index.html
├── savings_book_forecasting.ipynb
├── analysis.py
├── run_analysis.py
├── requirements.txt
├── data/
│   ├── monthly_balances.csv
│   ├── market_rates.csv
│   ├── monthly_flows.csv
│   └── cohort_retention.csv
├── templates/
│   ├── balance_movement_bridge_template.csv
│   └── fixed_term_maturity_template.csv
└── tests/
    └── test_analysis.py
```

## Run the reproducible analysis

Python 3.10+ is recommended.

```bash
python -m pip install -r requirements.txt
python run_analysis.py
python -m unittest discover -s tests -v
```

The runner writes rolling-origin predictions and summary metrics, the reconciliation residuals, interval deposit-beta calculations, cohort scenarios and the maturity proxy to `outputs/`.

## Limitations and next data requirements

- Eighteen monthly observations are insufficient for robust model selection or production forecasting.
- Expanding-window folds overlap and are not independent; results are descriptive.
- No account-level maturity dates, customer-level migrations, actual churn events or renewal decisions are available.
- The balance-flow bridge is unresolved; missing movements must be sourced rather than estimated.
- No asset-side data is available; NIM, liquidity coverage and full ALM measures are out of scope.
- Market-rate snapshots are sparse and do not support a robust dynamic deposit-beta model.

For a production-grade extension, obtain daily/monthly account balances, transaction-level movement categories, customer IDs with privacy-safe cohort keys, account origination/maturity dates, renewal outcomes, product pricing history, competitor panels and relevant asset-side funding data.

## Tools

Python, pandas, NumPy, statsmodels, scikit-learn, matplotlib, Google Colab and Chart.js.

---

Zeeshan Azeem Khalid · [LinkedIn](https://linkedin.com/in/zeeshan-azeem-khalid-9bb14098)
