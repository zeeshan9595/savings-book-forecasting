# Contributing

Thanks for taking an interest in this independent savings-book analytics case study.

## Local setup

Use Python 3.11 and create an isolated environment:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
python -m pip install -r requirements.txt
```

## Before opening a pull request

1. Keep all illustrative values clearly identified as illustrative.
2. Do not add real customer, account or confidential banking data.
3. Do not describe scenario assumptions as observed behaviour.
4. Preserve chronological separation between training and test observations.
5. Add or update unit tests when changing calculations or validation.
6. Run the complete checks:

```bash
python -m compileall -q analysis.py run_analysis.py tests
python -m unittest discover -s tests -v
python run_analysis.py
```

## Modelling principles

- Compare complex forecasts with simple benchmarks.
- Report the forecast horizon, training window and evaluation sample.
- Keep overlapping-fold dependence and small-sample limitations visible.
- Do not interpret correlation as causation.
- Do not allocate reconciliation residuals without supporting source records.
- Distinguish mechanical interest-cost arithmetic from behavioural balance responses.
- Keep contractual maturity analysis separate from assumption-led proxies.

## Changes to data

If source data is changed, update the data dictionary, model card and project report where relevant. Add tests for schema, date alignment, units and expected data-quality conditions. Never replace a missing observation with an invented value merely to make a reconciliation pass.
