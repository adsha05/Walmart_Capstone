"""
Quick EDA for data/processed/merged_data.csv.

Run:
    python merged_data_quick_eda.py
"""

from pathlib import Path

import pandas as pd


def main():
    path = Path("data/processed/merged_data.csv")
    df = pd.read_csv(path, parse_dates=["dt"], low_memory=False)

    print(f"File: {path} | Shape: {df.shape}")
    print(f"Date range: {df['dt'].min().date()} → {df['dt'].max().date()}")

    print("\nColumns (dtype):")
    for col, dtype in df.dtypes.items():
        print(f"  - {col}: {dtype}")

    print("\nDuplicate checks:")
    dup_cases = df.duplicated(["store_id", "dept_id", "dt"]).sum()
    dup_trucks = df[["store_id", "dt"]].duplicated().sum()
    print(f"  - store_id/dept_id/dt duplicates: {dup_cases}")
    print(f"  - store_id/dt duplicates (trucks): {dup_trucks}")

    print("\nPer-department summary:")
    per_dept = (
        df.groupby("dept_id")
        .agg(
            rows=("cases", "size"),
            stores=("store_id", "nunique"),
            start=("dt", "min"),
            end=("dt", "max"),
            days=("dt", "nunique"),
            missing_cases=("cases", lambda s: s.isna().sum()),
            missing_trucks=("trucks", lambda s: s.isna().sum()),
        )
        .sort_index()
    )
    print(per_dept)

    print("\nMissing values (non-zero):")
    missing = df.isnull().sum()
    missing = missing[missing > 0].sort_values(ascending=False)
    if missing.empty:
        print("  None")
    else:
        for col, count in missing.items():
            pct = count / len(df) * 100
            print(f"  - {col}: {count} ({pct:.2f}%)")

    print("\nTarget distributions (non-null):")
    for target in ["cases", "trucks"]:
        series = df[target].dropna()
        print(
            f"  {target}: mean={series.mean():.2f}, std={series.std():.2f}, "
            f"min={series.min():.2f}, median={series.median():.2f}, max={series.max():.2f}"
        )


if __name__ == "__main__":
    main()
