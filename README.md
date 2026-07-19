# Walmart Capstone Forecasting Project

This repository contains a sendable version of a Walmart-style retail forecasting capstone project. The project forecasts two operational demand targets across store, department, and date:

- `trucks`: freight or distribution truck counts
- `cases`: product case volume sold or shipped

The modeling workflow is department-aware and focuses on departments 6, 9, 41, 67, and 90.

## Project Goals

- Build a leak-free time-series forecasting pipeline
- Merge retail demand, truck, store, macroeconomic, holiday, weather, and event data
- Engineer lag and rolling-window features using only prior information
- Compare baseline, linear, tree-based, boosting, and stacked ensemble models
- Produce holdout forecasts for submission-ready case and truck predictions

## Repository Structure

```text
.
├── 01_data_merge.ipynb
├── 02_data_preparation_pipeline.ipynb
├── 03_timeseries_splits.ipynb
├── 04_dept*_modeling_suite.ipynb
├── 05_dept_model_summary.ipynb
├── build_holdout_submissions.ipynb
├── data/external/
├── models/
├── submissions/
├── visualizations/
├── inbound_cases_team8.csv
├── trucks.csv
├── stores_data.xlsx
└── WMT_Team8_Final Presentation (1).pdf
```

## Workflow

1. `01_data_merge.ipynb` merges primary case, truck, and store data.
2. `02_data_preparation_pipeline.ipynb` cleans inputs and adds external signals.
3. `03_timeseries_splits.ipynb` creates train, validation, test, and holdout windows with lag and rolling features.
4. `04_dept*_modeling_suite.ipynb` trains department-specific models for cases and trucks.
5. `05_dept_model_summary.ipynb` compares model results across departments.
6. `build_holdout_submissions.ipynb` assembles final holdout prediction files.

## Data

Primary inputs:

- `inbound_cases_team8.csv`: case volume history
- `trucks.csv`: truck count history
- `stores_data.xlsx`: store metadata and geography

External inputs under `data/external/` include macroeconomic indicators, gas prices, Google Trends signals, weather, holidays, school calendar estimates, tax holiday data, and major sports event flags.

## Modeling Approach

The project uses separate department-level modeling pipelines and evaluates multiple candidate regressors, including:

- Ridge, ElasticNet, and LinearRegression
- RandomForestRegressor and ExtraTreesRegressor
- HistGradientBoostingRegressor
- CatBoost, LightGBM, and optional XGBoost models
- Stacked ensembles using the top-performing base models with a Ridge meta-learner

Models are ranked primarily by MAPE, with RMSE, MAE, and bias checks used for additional evaluation.

## Time-Series Validation

The project uses chronological splits to avoid lookahead bias:

- Train: 2024-03-14 to 2025-05-31
- Validation: 2025-06-01 to 2025-06-30
- Test: 2025-07-01 to 2025-08-17
- Holdout forecast: 2025-08-18 to 2025-09-14

Lag and rolling features are generated per store and department using shifted historical values. Holdout features are seeded from the latest available history, and external signals are frozen when future observations are unavailable.

## Outputs

Final forecast files are stored in `submissions/`:

- `submission_cases_holdout.csv`
- `submission_trucks_holdout.csv`
- `submission_cases_trucks_holdout.csv`

Model comparison outputs are stored under `models/`, and visual analysis outputs are stored under `visualizations/`.

## Results Summary

The strongest models generally achieved test MAPE around:

- 6% to 7% for case forecasts
- About 4.5% for truck forecasts

Important predictors included recent case lags, truck volume, weekly seasonality, holiday timing, weather signals, and select macroeconomic indicators.

## Packaging Notes

This repository is a reduced sendable package. Large trained model binaries, processed datasets, and training logs were intentionally excluded. Some notebooks may reference excluded local artifacts, but their outputs and summary files are preserved for review.

Additional project context is available in:

- `PROJECT_SUMMARY.md`
- `PROJECT_INTERVIEW_DETAIL.md`
- `MODELING_DATA_README.md`
- `data/external/EXTERNAL_DATA_SUMMARY.md`
