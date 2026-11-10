# Savings Book Forecasting — Detailed Project Report

**Author:** Zeeshan Azeem Khalid  
**Project type:** Independent banking analytics case study  
**Data period:** January 2023 to June 2024  
**Currency:** GBP  
**Status:** Version 2 changes are in a draft pull request; Python tests and the reproducible analysis pass in GitHub Actions. The Colab notebook still needs a full interactive-runtime run.

## Executive summary

This project analyses an illustrative retail savings book across Easy Access, 1-year, 2-year and 5-year fixed products. It combines descriptive savings MI, total-book forecasting, rate pass-through, interest-cost sensitivities, cohort assumptions and a fixed-term maturity runoff proxy.

The second version addresses the main weaknesses identified in the initial review. Forecasts are evaluated against naïve and drift benchmarks using expanding windows at 1-, 3- and 6-month horizons. The rate-sensitivity analysis no longer converts a weakly identified regression coefficient into customer-balance forecasts. Cohort retention is separated from average balance per retained customer. Maturity analysis is explicitly marked as an assumption-led proxy because contractual maturity dates are absent. A reconciliation check quantifies the gap between transaction net flows and month-on-month balance movements.

The analysis remains a portfolio case study rather than a production banking model. Its 18 monthly observations, seven rate snapshots and hand-built inputs cannot establish reliable customer behaviour, causal rate elasticity or institution-level forecasting performance.

## 1. Dataset and scope

The project includes:
- 18 monthly product-balance observations from January 2023 to June 2024;
- seven market-rate snapshots, including the Bank of England base rate and illustrative competitor pricing;
- 18 months of gross inflow/outflow values;
- 45 cohort retention observations, all recorded at 100%.

The closing book is **£816,808** in June 2024.

All source values are illustrative. The data is not sourced from an actual bank and should not be presented as real customer or institution performance. The original hard-coded notebook data has been preserved, while equivalent CSV inputs are now provided for reproducible Python analysis.

## 2. Forecasting methodology

### Original chronological holdout

The original split uses the first 15 months for training and the final three months for testing. The reported results are:

| Model | MAPE | MAE | RMSE |
|---|---:|---:|---:|
| ARIMA(1,1,1) | 8.30% | £65.4k | £68.4k |
| Damped Holt-Winters | 10.53% | £82.9k | £85.6k |

This is a very small holdout and is retained as a reproducible comparison, not a definitive model-selection exercise.

### Expanding-window validation

Version 2 introduces a minimum training window of nine months and expanding-window origins. At each origin, the model is trained only on observations available at that point. Four models are compared:
- Naïve: carry forward the latest observed balance;
- Drift: extrapolate the average change between the first and last training observations;
- ARIMA(1,1,1);
- Damped Holt-Winters with additive trend and no seasonal component.

The test horizons are 1, 3 and 6 months. The pooled metrics are:

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

The drift benchmark has the lowest pooled error at each horizon in this illustrative sample. This is the central model-selection lesson: a transparent benchmark should be tested before adopting a more complex time-series model.

The folds overlap, so predictions are not independent. The sample is small, synthetic and structurally simple. The metrics should be treated as descriptive rather than statistically conclusive.

## 3. Rate sensitivity and econometric diagnostics

The initial levels regression related Easy Access balance to a time trend, our rate minus competitor rate, and the Bank of England base rate. Its rate-spread coefficient was approximately **−£116k per percentage point**. This coefficient is not used as a behavioural or causal estimate.

The short series has a non-stationary-looking balance level (ADF p-value approximately 0.67; low test power with this sample). Training-sample VIFs indicate substantial predictor overlap: trend approximately 17.2, rate spread approximately 7.4 and base rate approximately 7.0.

A first-difference model estimates a positive spread coefficient of approximately £65.6k per percentage point, but the estimate is statistically weak (p approximately 0.25, n = 17, R² approximately 0.10). The small number of months in which the spread changes makes the coefficient weakly identified. The one-month lag variant does not establish a robust relationship.

**Fix:** the project removes the upside/base/downside balance response scenarios that were previously generated from the levels regression. The differenced coefficient is retained as a diagnostic result only.

## 4. Deposit beta and rate pass-through

The cumulative endpoint calculation from January to October 2023 gives:
- Bank of England base rate: 3.50% to 5.25%;
- our Easy Access rate: 3.00% to 4.75%;
- cumulative pass-through ratio: 1.00;
- competitor series cumulative ratio: approximately 1.09.

Version 2 also calculates interval-by-interval pass-through ratios only when the Bank of England rate changes. This avoids division by zero during intervals where the base rate is unchanged.

These ratios remain descriptive. Seven sparse snapshots are not enough to estimate a stable marginal or dynamic deposit beta. A stronger model would need frequent product pricing histories, balance-weighted customer rates, market competitor panels and both rising and falling rate periods.

## 5. Rate-shock cost sensitivity

The original implementation used the differenced regression coefficient to estimate balance responses to rate shocks. That approach overstated the evidence available in the dataset.

**Fix:** the revised shock grid calculates only the mechanical annualised interest-cost impact at a constant balance, using the assumed deposit beta. For example, a +100bp parallel shock, 1.00 pass-through and £170,433 Easy Access balance imply approximately £1,704 additional annual interest cost.

This is a static arithmetic sensitivity. It does not forecast balance movements, customer attrition, repricing timing or the actual interest expense path.

## 6. Cohort modelling

The 45 source cohort observations all have 100% recorded retention. They do not contain actual churn events and therefore cannot estimate empirical churn.

**Fix:** the revised projection separates:
1. customer-retention index, driven by an assumed monthly churn rate;
2. average-balance-per-retained-customer index, driven by an assumed monthly balance-growth rate.

The projected cohort balance is the initial cohort balance multiplied by these two indices. Since customer counts and actual average balances are absent, the analysis does not fabricate either metric. Scenario rates are assumptions and are labelled as such.

## 7. Fixed-term maturity analysis

The source contains product-level closing balances but no account-level maturity dates, origination dates, term vintages, renewal decisions or contractual runoff instructions. It is not possible to create a true maturity ladder from product totals alone.

**Fix:** an illustrative runoff proxy spreads the closing fixed-term balance evenly across each nominal product term: 12 months for 1-year, 24 months for 2-year and 60 months for 5-year fixed products. The output is explicitly labelled an assumption-led proxy and must not be described as an account-level contractual maturity profile.

A blank template is included to capture the fields required for a proper ladder: account/vintage key, product, origination date, contractual maturity date, opening balance, rate, and renewal/runoff assumption.

## 8. Transaction-flow reconciliation

For each month after the first, the analysis compares:
- change in total product balances;
- gross inflows less gross outflows;
- unexplained residual = balance change minus net flows.

The source data produces:
- cumulative residual: **£250,808**;
- mean absolute monthly residual: approximately **£23,209**;
- maximum absolute monthly residual: **£82,000**.

The residual is left unexplained. It is not allocated to interest accruals, product migration, internal transfers, corrections or other balance movements because the supporting records are absent.

A balance-movement bridge template has been added. It includes the categories needed to reconcile opening balance to closing balance, including customer inflows, customer outflows, interest, product transfers, adjustments and other movements.

## 9. Reproducible project structure

```text
.
├── README.md
├── PROJECT_REPORT.md
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

Install and run from the repository root:

```bash
python -m pip install -r requirements.txt
python run_analysis.py
python -m unittest discover -s tests -v
```

The analysis writes rolling-origin predictions and metrics, reconciliation results, deposit-beta interval calculations, cohort scenarios and maturity proxy outputs to an `outputs/` directory. Generated outputs are excluded from version control.

A GitHub Actions workflow is included to install dependencies, run the unit tests and execute the analysis when the branch is pushed or the pull request is updated.

## 10. Files changed and why

| File | Purpose |
|---|---|
| `savings_book_forecasting.ipynb` | Original self-contained analysis plus Version 2 validation and scenario sections |
| `analysis.py` | Reusable functions for loading data, rolling validation, reconciliation, beta, cohorts and maturity proxy |
| `run_analysis.py` | Single command to reproduce the Python analysis outputs |
| `data/*.csv` | Transparent input tables separated from analysis code |
| `templates/balance_movement_bridge_template.csv` | Fields required to reconcile savings balances |
| `templates/fixed_term_maturity_template.csv` | Fields required to build an account/vintage-level maturity ladder |
| `tests/test_analysis.py` | Tests for data totals, forecast benchmarks, reconciliation, cohort assumptions and maturity proxy |
| `.github/workflows/tests.yml` | Automated test and analysis run |
| `.gitignore` | Excludes generated outputs, caches and local environments |
| `README.md` | Concise project overview, results and limitations |
| `index.html` | Dashboard updates, rolling-origin results and improved caveats |

## 11. Validation status and remaining work

The new notebook is valid JSON and its new cells contain the additional analysis logic. The Python module, tests and workflow have been added to the review branch. The rolling-origin calculations and reconciliation figures have been independently recalculated from the supplied illustrative data for this report.

**Previous GitHub Actions run:** the earlier six-test suite passed and the analysis runner completed with `DATA CHECKS: PASS`. The expanded 13-test suite and artifact-upload step have since been added; their result must be checked on the latest branch commit before claiming the new checks pass. The revised notebook itself has not yet been executed end-to-end in Google Colab. Its saved outputs were cleared to avoid leaving stale outputs beside changed code.

Before merging, check the pull request's Actions status and run the Colab notebook from the first cell through the final cell. If the notebook and Python package produce any different figures, investigate the difference and update the report before publishing.

## 12. Further data required for a production-grade version

1. Account-level daily/month-end balances with stable privacy-safe account identifiers.
2. Transaction-level inflows/outflows and all internal transfers, product migrations, interest credits, corrections and adjustments.
3. Account origination date, contractual maturity date, product term, rate, renewal instruction and actual maturity outcome.
4. Customer-level cohort keys, acquisition dates, closure/attrition events and balance histories.
5. Daily or weekly product pricing and competitor rate histories.
6. Asset-side balances, yields, repricing dates and liquidity classifications for full ALM/NIM analysis.

With these fields, the project could progress from illustrative savings MI into a defensible funding forecast, behavioural deposit beta model, maturity ladder and product migration analysis.

---

**Prepared as an independent case study using illustrative data.** All estimates are educational examples and are not actual bank results or production forecasts.
