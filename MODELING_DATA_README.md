# Modeling Dataset - Ready for Forecasting

## Files produced
- `data/processed/merged_data_model_ready_interactions.csv` — 275,000 rows × 62 columns. Base store–dept–day dataset with external, weather, tax, sports, and trend features (no lags).
- `data/processed/merged_data_model_ready.csv` — same rows with interaction/flag features removed (45 columns).
- `data/processed/merged_data_model_ready_minimal.csv` — lean slice with ids, dt, target, trucks, geo, and key macro features for compact modeling.
- `data/processed/timeseries_splits/train_timeseries.csv` — 222,000 rows, 71 columns.
- `data/processed/timeseries_splits/val_timeseries.csv` — 15,000 rows.
- `data/processed/timeseries_splits/test_timeseries.csv` — 24,000 rows.
- `data/processed/timeseries_splits/holdout_forecast_window.csv` — 14,000 rows (forecast window Aug 18–Sep 14, 2025).

## Date ranges
- Train: 2024-03-14 → 2025-05-31
- Validation: 2025-06-01 → 2025-06-30
- Test: 2025-07-01 → 2025-08-17
- Holdout/forecast: 2025-08-18 → 2025-09-14

## Feature groups in the split files (71 cols)
- Identifiers: `dept_id`, `store_id`, `dt`
- Targets: `cases` (stage 2), `trucks` (stage 1)
- Core store/dept context: `trucks`, `state_name`, `market_area_nbr`, `region_nbr`, `dept_desc`, `gmm_name`, `dmm_name`
- External, weather, event, and trend signals: `CPI_*` columns, `Consumer_Sentiment`, `Fed_Funds_Rate`, `Initial_Jobless_Claims`, `Crude_Oil_Price`, `state_unemployment_rate`, `temp_*` and `precip_*` fields, cooling/heating degree days, `sports_event_*` flags, `sales_tax_*` fields, `trends_*_scaled`, `cdd_*`/`hdd_*` fields, `bts_*` flags, `cpi_food_gap`, etc.
- Engineered time-series features (computed with `shift(1)` to avoid leakage): `cases_lag_1/7/14`, `cases_ma_7/14`, `cases_std_7`, `trucks_lag_1/7`, `trucks_ma_7`.

## Missing values
- Forecast window: `cases`/`trucks` are empty by design. Lag features are populated for the first forecast day using history; later forecast days stay NaN until you roll predictions forward.
- Train warm-up: first 14 days per store/dept have expected lag NaNs.
- `sports_event_name`/`sports_event_category` are sparse and can be label-encoded or dropped.

## How to use
- Stage 1 (trucks): train on train/val/test splits; feature set = all numeric columns except `cases`; forecast on holdout iteratively if you need truck lags for later days.
- Stage 2 (cases): use train/val/test with numeric columns excluding `cases`; when scoring the holdout, feed predicted trucks and predicted cases forward to fill lag features across the 28-day horizon.
- Splits are time-ordered; keep validation/test windows separate for honest evaluation.

## Notes
- Rolling features now use only prior days, and holdout splits include lag values seeded from the history up to 2025-08-17.
- External signals (macro, trends, weather, unemployment) are frozen to their last historical values for the forecast window to avoid future-data leakage.
- Use the minimal file if you want the high-signal subset only; full/interactions remain for feature exploration.
- The base 62-column dataset is preserved separately in case you want to regenerate splits with different cutoffs.
