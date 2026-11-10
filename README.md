# Savings book forecasting: an independent case study

Forecasting a retail savings book at total (macro) and product (micro) level: easy access, 1-year, 2-year and 5-year fixed-rate products. Built as a practice exercise for savings MI and forecasting work.

**The data is illustrative.** It is 18 months of hand-built practice data (Jan 2023 to Jun 2024, total book about £817k), mirroring a small SQL Server practice database. It is not data from any bank.

Notebook: [savings_book_forecasting.ipynb](savings_book_forecasting.ipynb), runnable in Google Colab with no downloads.

## What it does

| Step | Method |
|---|---|
| Balance trends by product | Monthly balances, product mix and net flows |
| Macro forecast | Holt-Winters (damped additive trend) vs ARIMA(1,1,1), trained on 15 months, tested on the last 3 |
| Micro forecast | Easy access balance regressed on trend, our rate vs competitor, and the Bank of England base rate |
| Scenarios | Upside, base and downside rate positioning; 25bp rate-sensitivity table |
| Cohort projection | Retention and balance curves under three assumed churn rates |
| Executive dashboard | Six-panel summary for leadership |

## Results on the 3-month holdout

| Model | Holdout MAPE |
|---|---|
| ARIMA(1,1,1) | 8.3% |
| Holt-Winters | 10.5% |

Easy access regression: in-sample R² 0.979 on the first 15 months; holdout MAE about £36k.

## Honest caveats

- **18 monthly points.** With three predictors, the regression fits easily and its coefficients are unstable. The rate-differential coefficient has a counter-intuitive negative sign, so treat sensitivities as illustrative.
- **The 6-month forecast extends the trend** (about +50%). It shows the method, not a credible outlook.
- **ARIMA scored better on the holdout**, but the summary and dashboard use the Holt-Winters forecast. A next step is to report both, or switch to the better model.
- **No churn in the practice data.** Every cohort kept 100% retention, so the cohort heatmap was removed. Cohort projections use assumed churn rates.

## Stack

Python, pandas, statsmodels, scikit-learn, matplotlib, seaborn, Google Colab.

---
Zeeshan Azeem Khalid · [LinkedIn](https://linkedin.com/in/zeeshan-azeem-khalid) · See also: [Lending Club credit decisions](https://github.com/zeeshan9595/lending-club-credit-decisions) · [Fraud detection leakage audit](https://github.com/zeeshan9595/Fraud-Detection-using-AI-and-ML)
