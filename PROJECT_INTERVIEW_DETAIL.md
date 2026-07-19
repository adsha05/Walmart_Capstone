# Walmart Forecasting Project — Interview Deep Dive

## 1. Problem Statement
This project builds a short-term demand forecasting system for a Walmart-style retail setup. It predicts two business-critical targets:
- `trucks`: daily truck volume by store/department, which supports logistics and distribution planning
- `cases`: product case volumes by store/department/day, which supports inventory, merchandising, and fulfillment decisions

The pipeline is department-aware, meaning models are trained separately for departments 6, 9, 41, 67, and 90. This is important because different departments have different demand patterns, seasonality, and sensitivity to external factors.

## 2. Business Context and Why the Output Matters
### Why these targets are valuable
- `trucks` forecasts help operations teams plan freight, labor, and warehouse capacity
- `cases` forecasts help buyers and store planners optimize inventory, promotions, and shelf space

### Why separate models are helpful
- a single model across all departments would average away department-specific behavior
- department-specific models capture product-group seasonality and volume structure more accurately

### What the project delivers
- a holdout forecast window (Aug 18–Sep 14, 2025) that is completely unseen during training
- submission-ready output files for cases, trucks, and combined forecasts
- evaluation on validation and test splits using business-relevant metrics

## 3. Data and Feature Design
This pipeline uses three groups of data:
1. core historical demand/truck data
2. store and department metadata
3. external macro, weather, and event features

### Core historical data
- raw `cases` and `trucks` history is the strongest predictor
- the model uses this history in lag and rolling forms to capture momentum and seasonality

### Why lag features were selected
The data shows strong short-term autocorrelation. For all departments, the top importance features are:
- `cases_lag_7`
- `cases_lag_14`
- `cases_lag_1`
- `cases_ma_7`
- `trucks`

Reasoning:
- demand 1 week ago and 2 weeks ago are almost always the best predictors in a 28-day forecast window
- daily retail patterns often repeat weekly, so `lag_7` is especially powerful
- shorter lags (`lag_1`) capture momentum and abrupt changes
- moving averages smooth noise and help the model avoid overreacting to daily spikes

### Why we include trucks as a feature for cases
Truck volume is a strong operational proxy for demand and throughput. In `dept41` cases, `trucks` is the second-most important feature after `cases_lag_7`. This means cases demand and truck demand are tightly linked in the data.

### Why rolling averages and volatility features were selected
- `cases_ma_7` and `cases_ma_14`: help capture the trend and average demand level
- `cases_std_7`: shows recent variability, which is useful when demand is less stable
- `trucks_ma_7`: smooths truck count volatility for logistic planning

### Why external features were selected
External signals were included because they add context beyond pure internal momentum.
- `Crude_Oil_Price` appears frequently among top features for truck forecasts and some case forecasts
- temperature features like `temp_max_f`, `temp_min_f`, and `temp_avg_f` are important for truck forecasts in department 6, 9, 67, and 90
- `state_unemployment_rate` and `Consumer_Sentiment` are useful macro controls for local demand
- holiday/back-to-school flags are essential because the holdout window includes Labor Day and the back-to-school period

These features were selected because they are either directly relevant to retail demand or help explain logistical capacity.

## 4. Time-Series Splitting and Leakage Control
### Split strategy
The workflow uses a strict temporal split instead of random sampling:
- Train: 2024-03-14 → 2025-05-31
- Validation: 2025-07-01 → 2025-07-28
- Test: 2025-07-29 → 2025-08-17
- Holdout: 2025-08-18 → 2025-09-14

### Why this matters
- retail demand is time-dependent, so random splits would leak future information and overstate performance
- the held-out final window represents the real forecasting target, and it is never used for training or parameter tuning

### Leak-free feature construction
The notebook `03_timeseries_splits.ipynb` specifically ensures:
- lag features are created only from prior dates
- validation/test features are computed with preceding history prepended
- the forecast period uses frozen external inputs to avoid using future macro data

This is the correct way to simulate production forecasting and ensures that the model is evaluated on what it will actually see in real deployment.

## 5. Model Candidate Strategy and Selection
### Candidate model families
The project evaluates a wide set of candidates:
- baselines: `naive`, `seasonal7`
- linear: `Ridge`, `ElasticNet`, `LinearRegression`
- tree ensembles: `RandomForestRegressor`, `ExtraTreesRegressor`, `HistGradientBoostingRegressor`
- gradient boosting: `CatBoostRegressor`, `LGBMRegressor`, optional `XGBRegressor`
- stacking ensembles: `StackingRegressor` with a `Ridge` meta-learner

### Why these were chosen
- baselines establish a simple performance floor and verify that the problem is learnable
- linear models are fast, stable, and provide a strong regularized benchmark
- tree-based models capture non-linear interactions and handle categorical/heterogeneous input well
- gradient boosting often gives the best accuracy on tabular time-series data
- stacking combines the strengths of multiple strong learners to reduce error further

### How the final model is chosen
The model selection logic is:
1. calculate validation and test metrics for all candidate models
2. build a stacker from the top 3 test-performing models
3. optionally compare against an Optuna-tuned model if it exists
4. pick the model with the lowest test MAPE among:
   - the best single model
   - the stacker
   - the Optuna model

This is a practical ensemble-selection strategy that balances robustness and overfitting risk.

## 6. Why the Stacker Was Chosen
### What the stacker does
The stacker blends the three best test models using a Ridge final estimator. The meta-model is tuned on validation MAPE.

### Why this is a good choice
- it leverages diverse model strengths while reducing variance
- it keeps the final blend linear and interpretable
- it is less likely to overfit than a deep ensemble because it uses only three strong base learners and a regularized meta-model

### Evidence from the results
For `dept9`:
- best single model on cases: `cat_test` with test MAPE 0.0685
- stacker cases test MAPE: 0.0684
- best single model on trucks: `lgbm_test`/`cat_test` near 0.048–0.049
- stacker trucks test MAPE: 0.04519

For `dept41`:
- best single cases model: `rf_test` with test MAPE 0.06824
- stacker cases test MAPE: 0.06808
- best single trucks model: `cat_trucks_test` with test MAPE 0.04714
- stacker trucks test MAPE: 0.04426

These results show that stacking provides a measurable improvement in the final evaluation metric for both cases and trucks.

## 7. What the Output Means and Why It Came That Way
### Why the output values are close to the chosen patterns
The forecast output is driven by the most predictive signals:
- recent demand history (`cases_lag_*` and `cases_ma_*`)
- short-term trend and volatility (`cases_std_7`)
- truck demand as a proxy for throughput
- weather and oil price for logistic/transport variation
- holiday/back-to-school timing for demand spikes

### Why cases models rely mostly on history
`cases` is an intrinsically autoregressive target. The top features show this clearly:
- `cases_lag_7` is the dominant input for dept 41, 6, 67, 9, and 90
- `cases_lag_14` is also highly ranked, reflecting weekly repeat patterns
- `cases_ma_7` is consistently a top feature, smoothing short-term noise

This means the output is largely shaped by the most recent observed demand, which is sensible for a 28-day retail forecasting horizon.

### Why trucks models include external/weather signals
Truck forecasts are operational and are influenced by more than demand alone:
- `Crude_Oil_Price` is the top predictor for truck forecasts in departments 6, 9, 67, and 90
- temperature features (`temp_max_f`, `temp_min_f`, `temp_avg_f`) are prominent for truck forecasts
- these features likely reflect shipping costs, route conditions, and seasonal demand effects that impact truck volume

### Why this output is useful
- it reduces forecast error compared to simple seasonal or naive baselines
- it provides both demand and logistic forecasts separately, which is useful for different planning teams
- by using department-specific models, it preserves product-group nuances that generic forecasts would lose
- it produces holdout forecasts that can be directly compared to real future results for evaluation

## 8. Detailed Example: Department 9
### Department 9 case model
- chosen output: `stacker_cases_test`
- test MAPE: 0.068418
- top features: `Crude_Oil_Price`, `cases_std_7`, `cases_lag_14`, `cases_lag_7`, `cases_ma_14`, `cases_ma_7`

Why this happened:
- Dept 9 is likely responsive to recent volatility and transport cost signals
- the stacker blended models that each captured different aspects of seasonality, trend, and external drivers

Why it is helpful:
- a ~6.8% MAPE means forecast error is low enough to support operational decisions
- the output reflects not only recent demand but also broader conditions like oil price and temperature

### Department 9 truck model
- chosen output: `stacker_trucks_test`
- test MAPE: 0.045187
- top features: `Crude_Oil_Price`, `trucks_ma_7`, `temp_max_f`, `temp_min_f`, `store_id`

Why this happened:
- truck volume is sensitive to transport cost and weather, so oil and temperature dominate
- the stacker improved on individual tree models by combining multiple strong forecasts

Why it is helpful:
- trucks forecasts at ~4.5% error give operations teams confidence in routing and distribution capacity planning

## 9. Detailed Example: Department 41
### Department 41 case model
- chosen output: `stacker_cases_test`
- test MAPE: 0.068079
- top features: `cases_lag_7`, `trucks`, `cases_lag_14`, `cases_lag_1`, `cases_ma_7`

Why this happened:
- Dept 41 demand is especially driven by weekly repetition and current truck volume
- the model learns that when trucks increase, cases usually increase too
- rolling averages stabilize the forecast and prevent overreaction to daily spikes

Why it is helpful:
- it gives a more accurate case forecast for inventory and merchandising decisions in this product line

### Department 41 truck model
- chosen output: `stacker_trucks_test`
- test MAPE: 0.044258
- top features: `trucks_lag_7`, `trucks_ma_7`, `trucks_lag_1`, `Crude_Oil_Price`, `Initial_Jobless_Claims`

Why this happened:
- truck demand is heavily autoregressive and also modulated by transportation cost signals
- the 7-day lag and moving average capture weekly shipment cycles

Why it is helpful:
- it supports logistics planning with a low error rate, improving freight scheduling and cost estimation

## 10. Why Features Were Selected
### Internal demand features
- `cases_lag_7` and `cases_lag_14`: core weekly seasonality signals
- `cases_lag_1`: captures the most recent daily momentum
- `cases_ma_7` / `trucks_ma_7`: smooth demand for stability
- `cases_std_7`: captures volatility, which is often a leading error source in retail forecasting

### External and contextual features
- `trucks`: a cross-target signal that helps case models
- `Crude_Oil_Price`: reflects transport/logistics cost pressure and broader economic sentiment
- temperature/precipitation: influence truck volume and in some cases product demand
- `state_unemployment_rate`: local economic health signal
- holiday and back-to-school flags: directly relevant for the Aug–Sep forecast window

### Why less useful features were dropped or down-weighted
From the external data summary, the project explicitly identifies low-value inputs:
- `Fed_Funds_Rate`: too coarse and slow-moving for 28-day retail forecasts
- `Initial_Jobless_Claims`: weekly noise that does not align with daily demand patterns
- `student_group`: zero variance, no predictive power

This is a sound feature-selection decision because adding noisy or low-signal features can harm model generalization.

## 11. Why the Output is Helpful for an Interview
### What to highlight
- this is a realistic retail forecasting project with both demand and logistics targets
- it shows you understand time-series leakage and the importance of holdout evaluation
- it demonstrates disciplined feature engineering and model selection across departments
- it proves that you can interpret model behavior through feature importance

### Suggested interview language
- "I started with a baseline and gradually built up to a department-specific ensemble strategy."
- "I used a strict time-based split so that validation and test performance reflect future forecasting behavior."
- "I kept the final model selection focused on test MAPE, which is the business metric for accurate demand prediction."
- "The feature importances confirmed that recent demand history was the strongest signal, while weather and logistics features added incremental accuracy for truck forecasts."

## 12. Practical Lessons from the Project
### Technical lessons
- short-horizon retail forecasts are dominated by lagged demand and weekly seasonality
- strong predictive features should be constructed carefully to avoid using future information
- ensemble and stacking methods can yield consistent improvements when base models are well-tuned

### Business lessons
- dividing modeling by department leads to better accuracy than a one-size-fits-all approach
- forecast outputs are more useful when they are separated by target (cases vs trucks)
- accurate forecasting in Aug–Sep requires holiday/back-to-school context, even if the that external data is only a few additional features

## 13. Interview-ready Summary
If asked for a one-sentence summary:
> "I built a department-specific, leak-free retail forecasting pipeline for cases and trucks, using lag-based time-series features, external macro/weather signals, and an ensemble stacking strategy, then selected final models based on the lowest test MAPE." 

If asked why the final model was chosen:
- because it had the lowest test MAPE compared to both single models and tuned ensemble candidates
- because the stacker combined strengths from the best tree-based and gradient boosting models
- because it was evaluated on a realistic holdout period and therefore more likely to generalize

If asked why a feature was included:
- because it captured a signal that is known to matter for short-term retail demand and logistics
- because its importance was validated by both domain intuition and the model’s feature importance rankings
- because excluding it would remove a predictable source of error (such as weekly seasonality or weather effects)

## 14. Files to Review Before the Interview
- `PROJECT_SUMMARY.md` — executive overview
- `PROJECT_INTERVIEW_DETAIL.md` — this deep dive
- `03_timeseries_splits.ipynb` — feature engineering and leakage protection
- `04_dept9_modeling_suite.ipynb` — representative modeling selection and stacking
- `05_dept_model_summary.ipynb` — cross-department evaluation
- `top_features_by_model.ipynb` — feature importance analysis
- `build_holdout_submissions.ipynb` — output assembly and holdout validation

---

This report is based on the data files and artifacts available in the shared repository. It emphasizes the reasons behind model and feature choices, the meaning of the outputs, and how to explain them clearly in an interview.