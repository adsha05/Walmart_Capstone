# McKinsey Interview Prep Report

## 1. Executive Take

This repository is best described as an end-to-end retail forecasting pipeline for Walmart-style demand planning. It predicts:

- `cases`: store-department-day case volume
- `trucks`: store-day truck demand that is carried through a department-based workflow

The strongest part of the project is the `cases` forecasting pipeline:

- clear time-series feature engineering
- sensible external data enrichment
- department-specific modeling
- reproducible saved outputs
- final holdout submission files

The project is interview-worthy, but it should be described honestly. The repo also contains a few documentation and methodology inconsistencies that you should be ready to acknowledge if asked.

## 2. What The Project Actually Contains

### Core raw data

- `inbound_cases_team8.csv`: 275,000 rows, 5 columns, 100 stores, 5 departments, date range `2024-03-14` to `2025-09-14`
- `trucks.csv`: 52,200 rows, 3 columns, 100 stores, date range `2024-03-14` to `2025-08-17`
- `stores_data.xlsx`: 100 rows of store geography metadata with `state_name`, `market_area_nbr`, and `region_nbr`

### Department scope

The modeling notebooks work separately on departments:

- `6`
- `9`
- `41`
- `67`
- `90`

### External data used

The repo includes macro, weather, event, tax-holiday, sports, gas price, unemployment, and Google Trends data under `data/external/`.

### Final delivered outputs

The project ships final holdout CSVs:

- `submissions/submission_cases_holdout.csv`
- `submissions/submission_trucks_holdout.csv`
- `submissions/submission_cases_trucks_holdout.csv`

Each submission covers exactly 14,000 holdout rows for `2025-08-18` through `2025-09-14`.

## 3. End-To-End Pipeline

The repo follows a coherent notebook workflow:

1. `01_data_merge.ipynb`
   Merges base operational data and store attributes.
2. `02_data_preparation_pipeline.ipynb`
   Adds external signals and produces model-ready data.
3. `03_timeseries_splits.ipynb`
   Creates time-based splits and leak-aware lag/rolling features.
4. `04_dept*_modeling_suite.ipynb`
   Trains department-level models for cases and trucks.
5. `05_dept_model_summary.ipynb`
   Aggregates saved model metrics across departments.
6. `build_holdout_submissions.ipynb`
   Assembles department outputs into final submission files and checks holdout coverage.

In an interview, the simplest accurate description is:

"I built a forecasting pipeline that merged internal demand data with store metadata and external signals, engineered leak-aware time-series features, trained department-level models, and produced final holdout forecasts for a 28-day future window."

## 4. Data Design And Why It Matters

### Business framing

`cases` is the commercial target. It directly supports inventory and demand planning.

`trucks` is the operational target. It relates to freight and capacity planning.

### Why department-specific modeling makes sense

Departments have different demand patterns, seasonality, and event sensitivity. A department-specific case model is defensible and likely better than one pooled model.

### Important structural nuance on trucks

Raw `trucks.csv` is at `store_id, dt` granularity, not `store_id, dept_id, dt`.

In practice, the repo duplicates truck forecasting inside each department notebook and emits truck forecasts at department level in the final submissions. That means the same store-date can receive different truck predictions from different department models.

This is the cleanest way to talk about it:

"The case pipeline is truly department-specific. The truck pipeline was implemented inside the same department-based framework for submission consistency, but in a production redesign I would model trucks once at the store-day level and then reconcile or broadcast that forecast downstream."

## 5. Feature Engineering

The modeling setup uses strong short-horizon time-series features:

- `cases_lag_1`, `cases_lag_7`, `cases_lag_14`
- `cases_ma_7`, `cases_ma_14`
- `cases_std_7`
- `trucks_lag_1`, `trucks_lag_7`
- `trucks_ma_7`

It also brings in external and contextual variables such as:

- inflation and macro indicators
- consumer sentiment
- unemployment
- crude oil price
- weather
- back-to-school and holiday indicators
- market and region fields

### What the repo evidence says

The top features across departments show a clear pattern:

- cases models are dominated by autoregressive demand features like `cases_lag_7`, `cases_lag_14`, `cases_lag_1`, and moving averages
- trucks or truck-derived features are also useful for case prediction
- truck models are influenced by weekly truck history plus weather and energy-cost variables such as `Crude_Oil_Price`, `temp_max_f`, `temp_min_f`, and `precip_in`

This is a strong interview point because it shows a realistic tabular forecasting pattern:

"The biggest gains came from getting the temporal structure right. External data helped, but lagged demand and weekly seasonality were the real backbone of accuracy."

## 6. Time Splits And Leakage Control

### What the current modeling notebooks actually use

The active split constants in `03_timeseries_splits.ipynb` and the department modeling notebooks are:

- Train: `2024-03-14` to `2025-06-30`
- Validation: `2025-07-01` to `2025-07-28`
- Test: `2025-07-29` to `2025-08-17`
- Holdout: `2025-08-18` to `2025-09-14`

That corresponds to:

- train: 237,000 rows
- validation: 14,000 rows
- test: 10,000 rows
- holdout: 14,000 rows

### What is good here

- the holdout window is truly in the future
- lag and rolling features are created with shifts to avoid direct future leakage
- holdout external values are frozen rather than using unavailable future information
- holdout forecasting is iterative: trucks are predicted first, then cases are predicted using updated truck and case history

### What you should acknowledge if asked

The documentation is not perfectly synchronized. Some repo markdown still describes an older split:

- train through `2025-05-31`
- validation in June
- test from `2025-07-01` to `2025-08-17`

Use the active notebook constants, not the older markdown, when speaking about the final modeling flow.

## 7. Modeling Strategy

Each department notebook evaluates several model families:

- baselines: naive and 7-day seasonal
- linear models: Ridge, ElasticNet, LinearRegression
- tree ensembles: RandomForest, ExtraTrees, HistGradientBoosting
- boosting libraries: CatBoost, LightGBM, optional XGBoost
- stacked ensembles with a Ridge meta-model
- optional Optuna tuning for the best single model

### How final selection works

The notebooks compare candidate models on validation and test metrics, then choose the final model by the lowest saved `test` MAPE.

This is the correct interview framing:

"I treated the workflow as a practical model bake-off with disciplined time ordering. I compared simple baselines, regularized linear models, tree ensembles, and stacked models, then took the strongest performer into holdout forecasting."

## 8. Actual Saved Results

### Best test MAPE by department

| Dept | Cases best model | Cases test MAPE | Trucks best model | Trucks test MAPE |
|------|------------------|-----------------|-------------------|------------------|
| 6 | `cat_test` | `0.069147` | `stacker_trucks_test` | `0.045357` |
| 9 | `stacker_cases_test` | `0.068418` | `stacker_trucks_test` | `0.045187` |
| 41 | `stacker_cases_test` | `0.068079` | `stacker_trucks_test` | `0.044258` |
| 67 | `cat_test` | `0.069187` | `stacker_trucks_test` | `0.045066` |
| 90 | `stacker_cases_test` | `0.071001` | `stacker_trucks_test` | `0.045522` |

### Aggregate view

- average case test MAPE across departments: `0.069167`
- average truck test MAPE across departments: `0.045078`

This lets you say:

"The saved test results were fairly consistent: case forecasts landed around 6.8% to 7.1% MAPE, while truck forecasts were around 4.4% to 4.6%."

## 9. What Is Strong About The Project

### Strong points to emphasize

- It is an end-to-end pipeline, not just a single model notebook.
- It uses realistic time-series feature engineering rather than random train-test splitting.
- It includes external data integration, which shows broader data-engineering thinking.
- It compares multiple model families instead of assuming one algorithm will win.
- It preserves a future holdout forecast window and generates submission-ready outputs.
- It includes interpretation artifacts such as feature-importance exports and visualizations.

### Best technical story

If you need one technical theme to center the conversation around, use this:

"The main value I added was turning a messy retail forecasting problem into a reliable supervised-learning pipeline with leak-aware temporal features and a disciplined evaluation structure."

## 10. What Is Weak Or Potentially Challengeable

You should know these cold so you can answer with maturity.

### 1. Repo documentation is inconsistent

`PROJECT_SUMMARY.md`, `MODELING_DATA_README.md`, and the active modeling notebooks do not all agree on the split boundaries.

### 2. The final model is chosen using `test` MAPE

That means the saved `test` set is functioning more like a model-selection set than a fully untouched final benchmark.

### 3. The stacker tuning is not methodologically pristine

The stacker code fits on `train + val` and then uses validation predictions to tune the Ridge meta parameter. That makes the validation score optimistic for the stacker.

### 4. Truck modeling is less conceptually clean than case modeling

Since the raw truck target is store-day level, building separate truck models for each department is more of a packaging choice than a clean business decomposition.

### 5. Only numeric columns are directly modeled

The modeling code selects numeric columns only. Text metadata like `dept_desc`, `gmm_name`, and `dmm_name` appear in the dataset, but they are not directly encoded into the model matrices in the shown notebook logic.

### 6. Missing-value handling is simple

Feature matrices use a generic forward-fill then zero-fill approach. That is pragmatic, but not the most careful grouped-imputation strategy.

## 11. How To Talk About Limitations Without Sounding Defensive

Use language like this:

"The pipeline was strong on feature engineering, time-ordering, and comparative modeling, but if I were productionizing it I would tighten the evaluation protocol, unify truck forecasting at the store-day level, and clean up the documentation so the data splits were perfectly traceable."

That answer works well because it shows:

- ownership
- honesty
- good modeling judgment
- a clear sense of next steps

## 12. Best Interview Narrative

### 30-second version

"I built a retail forecasting pipeline that predicted case demand and truck demand for Walmart-style store operations. I merged internal demand history with store attributes and external signals, engineered leakage-aware lag and rolling features, trained department-level models, and generated final 28-day holdout forecasts. The strongest results were around 6.8% to 7.1% test MAPE for cases and about 4.5% for trucks."

### 90-second version

"The project started as a tabular retail forecasting problem with two operational targets: cases and trucks. I first merged the historical case data, truck data, store geography, and external data like weather, unemployment, oil price, and holiday effects. Then I built a time-series preparation step that created lag, moving-average, and volatility features while keeping the holdout period untouched. After that, I trained separate department-level model suites across five departments and compared baselines, linear models, tree ensembles, boosting models, and stacked ensembles. The key insight was that short-horizon case forecasting was driven mostly by recent demand history and weekly seasonality, while trucks also responded to weather and energy-cost variables. The final pipeline produced submission-ready forecasts for a 28-day future window, and the saved test results were consistently around 6.9% MAPE for cases and 4.5% for trucks."

## 13. Questions You Are Likely To Get

### Why not just use a simple baseline?

"I did use naive and 7-day seasonal baselines. They were important sanity checks. Cases improved materially once I added lag structure, rolling features, and stronger tabular models. Trucks were tougher because weekly seasonality is already very strong, which made the baseline harder to beat."

### Why separate models by department?

"Because department behavior is heterogeneous. Weekly pattern, holiday sensitivity, and volatility differ across product groups. A pooled model would blur those patterns."

### Why add external data if lags dominate?

"Lags captured the bulk of short-term predictability, but external features helped explain deviations from recent history, especially for trucks and event-sensitive periods like back-to-school and Labor Day."

### What would you improve next?

"I would formalize rolling backtests, clean up the split documentation, model trucks once at the store-day level, and then feed that reconciled truck forecast into the case models."

### What did you learn?

"The biggest lesson was that in retail forecasting, getting the temporal setup right matters more than chasing model complexity. Leakage control, lag design, and the forecast-generation logic mattered more than adding many exotic features."

## 14. What To Fix In Your Existing `PROJECT_SUMMARY.md`

The current summary is directionally good, but I would correct these points before treating it as your source of truth:

- update the split section to match the active notebook constants
- explicitly distinguish strong case forecasting from the less clean truck setup
- state that final model selection uses lowest `test` MAPE
- mention that truck forecasts are generated separately inside each department workflow even though raw trucks are store-day level
- avoid implying that text metadata fields were directly modeled

## 15. Best Way To Position The Project At McKinsey

The consulting-friendly framing is:

"This project combined business framing, data integration, forecasting methodology, and decision-oriented evaluation. The technical work was not just training a model. It was defining the forecasting unit, designing a leak-resistant pipeline, comparing alternatives, interpreting drivers, and generating outputs that an operations team could actually use."

That positioning is stronger than presenting it as just a machine-learning exercise.
