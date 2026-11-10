# Data dictionary

All values are illustrative. Currency fields are GBP unless stated otherwise. Dates are month-end or snapshot dates as indicated.

## `data/monthly_balances.csv`

| Field | Type | Definition |
|---|---|---|
| `month` | Date | Month-end observation date |
| `EASY_ACCESS` | Numeric | Illustrative Easy Access closing balance |
| `FIXED_1YR` | Numeric | Illustrative 1-year fixed closing balance |
| `FIXED_2YR` | Numeric | Illustrative 2-year fixed closing balance |
| `FIXED_5YR` | Numeric | Illustrative 5-year fixed closing balance |

The analysis derives `total_balance` as the sum of the four product balances.

## `data/market_rates.csv`

| Field | Type | Definition |
|---|---|---|
| `rate_date` | Date | Market-rate snapshot date |
| `EASY_ACCESS_ours` | Percentage | Illustrative institution Easy Access rate |
| `EASY_ACCESS_competitor` | Percentage | Illustrative competitor Easy Access rate |
| `FIXED_1YR_ours` | Percentage | Illustrative institution 1-year fixed rate |
| `FIXED_1YR_competitor` | Percentage | Illustrative competitor 1-year fixed rate |
| `boe_base_rate` | Percentage | Bank of England base-rate snapshot |

Rate changes and spreads are expressed in percentage points, not decimal fractions.

## `data/monthly_flows.csv`

| Field | Type | Definition |
|---|---|---|
| `month` | Date | Flow observation month |
| `gross_inflows` | GBP | Illustrative gross deposits |
| `gross_outflows` | GBP | Illustrative gross withdrawals |
| `new_customers` | Count | Illustrative new-customer count |

The analysis derives `net_flows = gross_inflows - gross_outflows`. This is not a complete ledger bridge.

## `data/cohort_retention.csv`

| Field | Type | Definition |
|---|---|---|
| `cohort_month` | Date | Cohort acquisition month |
| `months_since_acq` | Integer | Months elapsed since acquisition |
| `retention_rate` | Percentage | Supplied cohort retention percentage |

All 45 supplied retention observations equal 100%; they do not provide observed churn evidence.

## Generated outputs

The runner writes CSV files under `outputs/`: rolling-origin predictions and metrics, flow reconciliation, deposit-beta intervals, observed cohort-retention summary, cohort scenario indices, maturity runoff proxy and data-quality checks. Generated outputs are excluded from version control.
