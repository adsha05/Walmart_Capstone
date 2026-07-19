# WMT Project Sendable Core

This folder is a reduced copy of the project meant for sharing without the heaviest artifacts.

## Included
- Core workflow notebooks: `01` through `05`, plus `build_holdout_submissions.ipynb`
- Supporting analysis notebooks: external feature summary, top-features, and bias/MAPE review
- Small/raw input files: `inbound_cases_team8.csv`, `trucks.csv`, `stores_data.xlsx`
- External-source files under `data/external/`
- Model result CSVs and holdout prediction CSVs under `models/`
- Final submission CSVs under `submissions/`
- Visualization PNGs under `visualizations/`
- Project readme and final presentation PDF

## Intentionally Excluded
- Large trained model binaries such as `models/dept*/final_*.pkl`
- Large processed datasets under `data/processed/`
- Training logs under `catboost_info/`
- Side material not central to the final project package

## Notes
- Some notebooks reference excluded large files, so they are best treated as documented analysis notebooks with outputs preserved.
- No environment or dependency file was present in the project root.
