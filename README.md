# Savings book forecasting: model comparison, deposit beta and rate-shock scenarios

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/zeeshan9595/savings-book-forecasting/blob/main/savings_book_forecasting.ipynb)

Forecasting a retail savings book at total (macro) and product (micro) level: easy access, 1-year, 2-year and 5-year fixed-rate products. Built as a practice exercise in savings MI, forecasting and rate-sensitivity work.

**The data is illustrative.** It is 18 months of hand-built practice data (Jan 2023 to Jun 2024, total book about £817k), mirroring a small SQL Server practice database. It is not data from any bank, and the numbers below show the method, not a real book.

## What the notebook does

| Section | Method |
|---|---|
| Balance trends | Monthly balances by product, product mix, net flows |
| Macro forecast | Damped Holt-Winters vs ARIMA(1,1,1); 15-month train, 3-month holdout; month-end dates throughout |
| Diagnostics | Augmented Dickey-Fuller stationarity tests, variance inflation factors |
| Micro elasticity | Easy access balance changes regressed on changes in our rate spread and the base rate, with a one-month lag |
| Deposit beta | Pass-through of Bank of England rate changes to the easy access rate |
| Rate shocks | Parallel ±25, 50, 100 and 200bp; competitor-only spread moves |
| Cohort projection | Retention and balance under three assumed churn rates |
| Dashboard | Six-panel summary for leadership |

## Results

### Macro forecast: 3-month holdout

| Model | MAPE | MAE | RMSE |
|---|---|---|---|
| ARIMA(1,1,1) | 8.3% | £65.1k | £68.2k |
| Holt-Winters (damped) | 10.5% | £82.8k | £85.6k |

The dashboard shows both paths: ARIMA as the baseline and Holt-Winters as a second view, with the gap between them shaded. Refitted on all 18 months, the 6-month forecasts are £993k (ARIMA) and £1.06m (Holt-Winters), against £817k today. Both extend the recent growth trend. AIC and BIC are reported in the notebook but are not comparable across the two model families.

### Why the original rate coefficient had the wrong sign

The first version regressed easy access balance *levels* on a trend, our rate minus competitors, and the base rate. The rate-spread coefficient came out at about -£116k per percentage point, which would mean paying more than competitors loses balances.

Two diagnostics explain why that result should not be trusted:

- **Non-stationary balances.** The ADF test cannot reject a unit root in the balance level (p = 0.67). Regressing one trending series on others can produce relationships that are really shared trends (spurious regression).
- **Collinear predictors.** VIFs are 17.8 for the trend and 9.4 for the rate spread, so the model cannot separate their effects.

Modelling month-on-month **changes** instead:

$$\Delta B_t = \alpha + \beta_1 \, \Delta \text{Spread}_t + \beta_2 \, \Delta \text{BoE}_t + \varepsilon_t$$

gives a spread coefficient of **+£65.6k per percentage point**, the expected direction, but with **p = 0.25** on 17 observations (R² 0.10). Adding a one-month lag on the spread does not change the picture. The sign is fixed without forcing it; the evidence is still weak because the spread only changes in a few months. Even differenced balances do not pass the ADF test here (p = 0.82), which says more about 17 points than about the data.

### Deposit beta and rate shocks

Over the 2023 hiking cycle (base rate 3.50% to 5.25%), our easy access rate moved one-for-one with the base rate (beta **1.00**); competitors averaged **1.09**.

$$\beta = \frac{\Delta \text{Rate}_{\text{easy access}}}{\Delta \text{Rate}_{\text{BoE}}}$$

| Scenario | Annual easy access interest cost | Balance effect via spread |
|---|---|---|
| Parallel +25bp | +£426 | -£1.4k |
| Parallel +100bp | +£1,704 | -£5.6k |
| Parallel -100bp | -£1,704 | +£5.6k |
| Competitors +25bp, base fixed | £0 | -£16.4k |
| Competitors +50bp, base fixed | £0 | -£32.8k |

Interest cost uses the £170k easy access balance and our beta. Balance effects use the weakly identified differenced elasticity, so read them as direction and rough size only. Because competitors pass on slightly more than we do, parallel rises widen their lead and cost us a little balance.

## Caveats

- 18 monthly points. Every estimate here has wide uncertainty.
- Forecasts extend the recent trend; they are not an outlook.
- No churn in the practice data: every cohort kept 100% retention, so the cohort heatmap was removed and projections use assumed churn.
- Net interest margin and liquidity metrics are out of scope: the data has no asset side.

## Stack

Python, pandas, statsmodels, scikit-learn, matplotlib, seaborn, Google Colab.

---
Zeeshan Azeem Khalid · [LinkedIn](https://linkedin.com/in/zeeshan-azeem-khalid) · See also: [Lending Club credit decisions](https://github.com/zeeshan9595/lending-club-credit-decisions) · [Fraud detection leakage audit](https://github.com/zeeshan9595/Fraud-Detection-using-AI-and-ML)
