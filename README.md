# Retail Savings Book Analytics

[![Python CI](https://github.com/zeeshan9595/savings-book-forecasting/actions/workflows/tests.yml/badge.svg?branch=review%2Fforecasting-quality-fixes)](https://github.com/zeeshan9595/savings-book-forecasting/actions/workflows/tests.yml)
[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/zeeshan9595/savings-book-forecasting/blob/review/forecasting-quality-fixes/savings_book_forecasting.ipynb)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)

**An independent retail banking analytics case study** covering savings-book forecasting, deposit-rate pass-through, funding-cost sensitivity, cohort assumptions, fixed-term runoff and data-quality reconciliation.

**[Interactive dashboard](https://zeeshan9595.github.io/savings-book-forecasting/)** · **[Detailed project report](PROJECT_REPORT.md)** · **[Model card](MODEL_CARD.md)** · **[Data dictionary](DATA_DICTIONARY.md)** · **[Pull request #1](https://github.com/zeeshan9595/savings-book-forecasting/pull/1)**

> **Data integrity:** all source values are illustrative and hand-built. They are not actual bank, customer or account records. The project contains 18 monthly balance observations, seven market-rate snapshots and 45 cohort-retention observations. No contractual maturity dates or asset-side data are available.

## Executive snapshot

| Measure | Result | Interpretation |
|---|---:|---|
| Closing savings book | **£816,808** | June 2024; four products |
| 1-month rolling MAPE | **4.55%** | Drift benchmark |
| 3-month rolling MAPE | **7.93%** | Drift benchmark |
| 6-month rolling MAPE | **7.45%** | Drift benchmark |
| Cumulative flow residual | **£250,808** | Unexplained; not allocated to unsupported causes |
| Deposit beta | **1.00** | Cumulative Jan–Oct 2023 endpoint ratio |
| +100bp annualised cost sensitivity | **~£1,704** | Static balance and 1.00 pass-through assumption |

The drift benchmark outperformed naïve, ARIMA(1,1,1) and damped Holt-Winters on pooled MAPE, MAE and RMSE at all three expanding-window horizons in this small illustrative dataset. Overlapping windows and the short series mean the results are descriptive, not statistically conclusive.

## What the project does

| Workstream | Method / deliverable |
|---|---|
| Savings MI | Monthly balances and product composition across Easy Access, 1-year, 2-year and 5-year fixed products |
| Forecasting | Naïve, drift, ARIMA(1,1,1) and damped Holt-Winters |
| Backtesting | 15/3 chronological holdout and expanding windows at 1-, 3- and 6-month horizons |
| Model diagnostics | ADF, training-sample VIF and first-difference regression |
| Deposit pricing | Cumulative and adjacent-snapshot deposit-beta ratios |
| Funding-cost sensitivity | Mechanical annualised interest-cost grid; no behavioural balance response |
| Cohort analysis | Observed-retention summary plus separate retention and average-balance scenario indices |
| Maturity analysis | Explicitly assumption-led fixed-term runoff proxy and account-level input template |
| Data quality | Flow-to-balance reconciliation and input validation |
| Engineering | Reusable Python module, CLI runner, CSV inputs, unit tests and GitHub Actions |

## Key analytical decisions

### Forecasts are benchmarked, not selected by complexity

The 15-month training / three-month holdout remains in the original notebook, but it is too small to establish superiority. The expanding-window backtest uses a minimum of nine months of training data and compares four methods at three horizons. The drift benchmark is the best performer in the supplied data.

### Weak regression coefficients are not converted into balance forecasts

The levels regression has trend and rate predictors that overlap materially. The first-difference spread coefficient is statistically weak (p approximately 0.25; n=17). Version 2 therefore removes balance-response scenarios derived from the levels regression.

### Cost shocks are mechanical sensitivities

A +100bp shock at 1.00 pass-through on a £170,433 Easy Access balance implies approximately £1,704 of additional annualised interest cost if the balance is held constant. This is not a forecast of customer behaviour or realised expense.

### Missing data is made visible

The transaction net-flow series does not reconcile to month-on-month balance movements. The cumulative residual is £250,808, the mean absolute monthly residual is approximately £23,209 and the largest monthly residual is £82,000. No unsupported allocation is made.

### Maturity and cohort assumptions are labelled

The source does not contain account-level contractual maturity dates or observed churn. The maturity schedule is an even-allocation proxy, and cohort scenarios use separate assumed customer-retention and average-balance indices.

## Repository map

```text
.
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
├── tests/
│   └── test_analysis.py
├── .github/
│   ├── workflows/tests.yml
│   └── dependabot.yml
├── PROJECT_REPORT.md
├── MODEL_CARD.md
├── DATA_DICTIONARY.md
├── CITATION.cff
└── index.html
```

## Run locally

Python 3.11 is used in continuous integration. From the repository root:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
python -m pip install -r requirements.txt
python run_analysis.py
python -m unittest discover -s tests -v
```

The runner validates source schemas, date continuity, missing values and numeric ranges before writing reproducible CSV outputs to `outputs/`. The GitHub Actions workflow compiles the Python modules, runs the unit tests and executes the analysis.

## Technical stack

Python · pandas · NumPy · statsmodels · scikit-learn · matplotlib · seaborn · Google Colab · GitHub Actions · Chart.js

## Limitations

- 18 monthly observations are insufficient for robust production forecasting.
- Expanding-window folds overlap; pooled forecasts are not independent.
- Seven rate snapshots do not support a stable dynamic deposit-beta model.
- Cohort data records 100% retention throughout; empirical churn cannot be estimated.
- Account-level maturity dates, product vintages and renewal outcomes are absent.
- The flow-to-balance residual remains unexplained pending source ledger components.
- No asset-side data is available for NIM, liquidity or full ALM analysis.

See the [detailed project report](PROJECT_REPORT.md) and [model card](MODEL_CARD.md) for methods, assumptions, validation and data requirements.

---

**Author:** Zeeshan Azeem Khalid · [LinkedIn](https://linkedin.com/in/zeeshan-azeem-khalid-9bb14098)
