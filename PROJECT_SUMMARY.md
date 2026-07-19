# Walmart Forecasting Project Summary

## 1. Project Overview
This project is a retail forecasting solution built for Walmart-style demand prediction. It specifically models two targets:
- `trucks`: freight or distribution truck counts that feed the fulfillment network
- `cases`: product case volume sold or shipped by store–department–day

The workflow is department-aware: model development is performed separately for departments 6, 9, 41, 67, and 90.

## 2. Key Goals
- Build a robust demand forecasting pipeline with clearly separated historical, validation, test, and holdout windows
- Use external macro and event data to improve predictions
- Create leak-free time-series features that only use prior information
- Compare baseline models, tree-based models, and stacked ensembles
- Produce submission-ready holdout forecasts for cases and trucks

## 3. Data and Sources
### Included data
- `inbound_cases_team8.csv`: primary case volume history
- `trucks.csv`: primary truck count history
- `stores_data.xlsx`: store metadata and geography
- External sources under `data/external/`

### External and engineered inputs
The project enriches base data with:
- macro indicators: `state_unemployment_rate`, `CPI_All_Items`, `Consumer_Sentiment`, `Crude_Oil_Price`
- holiday/event flags, including back-to-school and Labor Day
- weather-related signals in external data
- time-derived features and categorical store/department context

## 4. Workflow Structure
The main workflow is organized in notebooks:
- `01_data_merge.ipynb`: merge and inspect raw inputs into a modeling dataset
- `02_data_preparation_pipeline.ipynb`: prepare and clean data, add external features
- `03_timeseries_splits.ipynb`: create train/validation/test/holdout partitions and generate lag/rolling features
- `04_dept*_modeling_suite.ipynb`: department-specific model training and selection
- `05_dept_model_summary.ipynb`: summarize best models and compare performance across departments
- `build_holdout_submissions.ipynb`: assemble final holdout predictions into submission files

## 5. Time-Series Splitting and Leakage Control
The project uses a strict time-series split strategy:
- Train: 2024-03-14 → 2025-05-31
- Validation: 2025-07-01 → 2025-07-28
- Test: 2025-07-29 → 2025-08-17
- Holdout/forecast: 2025-08-18 → 2025-09-14

Important design details:
- Holdout rows are held out completely from modeling and evaluation
- Lag and rolling features are computed per `(store_id, dept_id)` with only prior history
- Validation and test feature construction prepend earlier history to avoid lookahead bias
- Forecast period external signals are frozen to the last available historical values

## 6. Feature Engineering
The modeling dataset includes 70+ columns with these feature families:
- identifiers: `store_id`, `dept_id`, `dt`
- current targets: `cases`, `trucks`
- store/dept metadata: `state_name`, `market_area_nbr`, `region_nbr`, `dept_desc`, `gmm_name`, `dmm_name`
- macro/external features: CPI, unemployment, sentiment, oil price
- event/holiday signals: back-to-school, Labor Day, major holiday flags
- lag features: `cases_lag_1`, `cases_lag_7`, `cases_lag_14`, `trucks_lag_1`, `trucks_lag_7`
- rolling features: `cases_ma_7`, `cases_ma_14`, `cases_std_7`, `trucks_ma_7`

Key insight from feature analysis:
- Historical case lags are among the strongest predictors
- Truck volume is also a strong predictor for case demand
- Weekly seasonality and holiday timing are important for the forecast horizon

## 7. Modeling Strategy
Each department modeling suite explores an ensemble of regressors:
- linear models: `Ridge`, `ElasticNet`, `LinearRegression`
- tree-based models: `HistGradientBoostingRegressor`, `RandomForestRegressor`, `ExtraTreesRegressor`
- gradient boosting: `CatBoostRegressor`, `LGBMRegressor`, optional `XGBRegressor`
- stacked ensembles: top three models blended with `StackingRegressor` and a Ridge meta-learner

The department notebook for `dept 9` shows the general strategy:
- build candidate models for `cases` and `trucks`
- tune hyperparameters through grid search and optionally Optuna
- evaluate using validation and test MAPE/RMSE/MAE
- construct a stacker using the top 3 test models
- choose the final model candidate with the lowest test MAPE

## 8. Model Selection and Stacking
The final model selection process is:
1. rank all candidate models by test MAPE
2. consider Optuna-tuned models if available
3. build stackers from the top 3 test-performing models
4. select the model with the lowest test MAPE across single models and stackers

The stacking approach is notable because:
- it leverages multiple strong base learners
- it uses a linear Ridge meta-model tuned on validation
- it preserves out-of-sample evaluation via the test split

## 9. Evaluation Metrics
The project evaluates models with:
- MAPE: average percentage error, primary ranking metric
- RMSE: root mean squared error, captures large deviations
- MAE: mean absolute error, robust average error
- bias: mean error, especially in `model_bias_mape.ipynb`

Sample performance observations from the notebook outputs:
- dept 41 cases stacker test MAPE ≈ 0.068
- dept 41 trucks stacker test MAPE ≈ 0.044
- dept 9 cases stacker test MAPE ≈ 0.0684
- dept 9 trucks stacker test MAPE ≈ 0.0452
- dept 90 cases stacker test MAPE ≈ 0.0710
- dept 90 trucks stacker test MAPE ≈ 0.0455

These results show consistent forecast quality across departments with MAPE in the 5-7% range for cases and ~4.5% for trucks in test data.

## 10. Feature Importance Highlights
From `top_features_by_model.ipynb`, the most important features include:
- `cases_lag_7`
- `trucks`
- `cases_lag_14`
- `cases_lag_1`
- `cases_ma_7`

For trucks models, the project also shows external/weather variables as influential:
- `precip_in`
- `temp_avg_f`
- `gas_price_usd_per_gallon`
- `market_area_nbr`
- `Initial_Jobless_Claims`

## 11. Output and Submission
The final submission pipeline is implemented in `build_holdout_submissions.ipynb`.
It assembles department-level forecast CSVs into:
- `submissions/submission_cases_holdout.csv`
- `submissions/submission_trucks_holdout.csv`
- `submissions/submission_cases_trucks_holdout.csv`

This notebook also performs:
- validation that all 14,000 holdout rows are covered
- an integrity check that the holdout merge matches the expected `merged_data` horizon

## 12. Strengths of the Project
- solid end-to-end pipeline from raw ingestion to submission-ready forecasts
- strong focus on leakage-free time-series feature engineering
- disciplined train/validation/test/holdout split design
- department-specific modeling, which respects heterogeneity across product groups
- pragmatic use of external macro features and holiday/event signals
- evidence of model comparison and ensemble improvement

## 13. How to Talk About This in an Interview
### Problem framing
- "This was a multi-target retail forecasting project for Walmart, predicting both truck counts and case volume across store-department pairs."
- "The goal was to produce reliable short-term forecasts and a submission-ready holdout forecast window."

### Technical approach
- "I merged sales, truck, store, and external macro/event data into a single modeling dataset."
- "I engineered time-series features like 1/7/14-day lags and rolling averages, while ensuring no future leakage into validation/test."
- "I built separate models per department, then chose the best candidate using test MAPE."
- "I also built stacking ensembles that blended the top-performing base learners with a linear meta-model."

### Metrics and validation
- "I used MAPE as the primary ranking metric, along with RMSE and MAE."
- "I reserved an unobserved holdout window for final scoring and carefully verified coverage."

### Results
- "The top models achieved test MAPEs around 6-7% for case forecasts and around 4.5% for truck forecasts."
- "Key predictors included recent case history, truck volume, weekly seasonality, and holiday/back-to-school effects."

### Lessons/impact
- "The project balance between statistical models and tree-based learners was important because different departments had different signal strengths."
- "I learned that careful time-series splitting and feature construction are more impactful than simply adding more external data."

## 14. Recommended talking points if asked about weaknesses
- Some inputs are very macro and may not improve short-horizon forecasts much (e.g. Fed Funds Rate).
- The holdout forecast still relies on a frozen snapshot of external features, which is a pragmatic choice but could be improved with explicit forecasting of those signals.
- The project would benefit from additional cross-validation folds or store-level hierarchical treatment if scaled further.

## 15. Files to review before the interview
- `MODELING_DATA_README.md` — dataset summary and split rationale
- `03_timeseries_splits.ipynb` — leak-free feature engineering and time-series split logic
- `04_dept9_modeling_suite.ipynb` — representative modeling pipeline, stacking, and final model selection
- `05_dept_model_summary.ipynb` — cross-department evaluation
- `build_holdout_submissions.ipynb` — final submission assembly
- `data/external/EXTERNAL_DATA_SUMMARY.md` — external feature evaluation

---

This summary is based on the shared project workspace and the notebooks/data that are included in the reduced sendable package.