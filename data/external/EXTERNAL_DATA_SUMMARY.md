# External Data Summary

## Date: Analysis completed
## Purpose: Evaluate external data additions for Walmart forecasting project

---

## ✅ WHAT IS USEFUL (KEEP)

### From `merged_data_with_external.csv`:

| Feature | Rating | Why Keep | Use Case |
|---------|--------|----------|----------|
| **state_unemployment_rate** | ⭐⭐⭐⭐⭐ | State-level economic indicator, varies by location | Best external feature - directly impacts local retail demand |
| **CPI_All_Items** | ⭐⭐⭐⭐ | General inflation indicator | Affects purchasing power across all departments |
| **Consumer_Sentiment** | ⭐⭐⭐⭐ | Consumer confidence index | Drives discretionary spending (Cameras, Sporting Goods, Team Sports) |
| **Crude_Oil_Price** | ⭐⭐⭐ | Transportation costs + consumer spending | Supply chain costs and consumer gas budget |

**Total to keep: 4 features**

---

## ⚠️ MAYBE KEEP

| Feature | Rating | Why Maybe | Decision |
|---------|--------|-----------|----------|
| **CPI_FoodAtHome** | ⭐⭐ | Food-specific inflation | Only useful for Dairy dept (90), marginal for others |

**Recommendation:** Keep only if you're doing department-specific models. Otherwise drop.

---

## ❌ WHAT IS NOT USEFUL (DROP)

| Feature | Rating | Why Drop |
|---------|--------|----------|
| **Fed_Funds_Rate** | ⭐ | Only 6 unique values in your data, changes quarterly, too macro for 4-week forecast |
| **Initial_Jobless_Claims** | ⭐⭐ | Weekly noise, doesn't align with daily/monthly retail patterns |
| **student_group** | ❌ | Always equals 8, zero variance, useless |

**Total to drop: 3 features**

---

## 🎯 WHAT COULD BE USEFUL (NEED TO ADD)

### Priority 1: CRITICAL (Add Immediately)

#### 1. **Holiday/Event Calendar** ✅ CREATED!
- **File:** `data/external/holiday_calendar.csv`
- **Features included:**
  - `is_holiday` - Major holidays (17 days)
  - `is_pre_holiday` - 3 days before major holidays
  - `is_back_to_school` - Aug 10 - Sep 10 (64 days) **← CRITICAL for your forecast!**
  - `is_labor_day` - Sep 1, 2025 **← IN YOUR FORECAST PERIOD!**
  - `is_christmas_season` - All of December
  - `is_thanksgiving_week` - Thu-Sun around Thanksgiving
  - `is_black_friday_week` - Black Friday weekend
  - `is_summer` - June-August
  - `holiday_name` - Specific holiday names

**Why critical:**
- Your forecast period (Aug 18 - Sep 14) includes:
  - 24 days of back-to-school period
  - Labor Day (Sep 1)
  - End of summer season
- Celebration dept (67) is heavily driven by holidays/events
- Back-to-school drives Sporting Goods, Team Sports

#### 2. **Temporal Features** (Easy to create from `dt`)
Create from date column:
- `year` (2024, 2025)
- `month` (1-12)
- `day_of_week` (0=Mon, 6=Sun)
- `week_of_year` (1-52)
- `day_of_month` (1-31)
- `is_weekend` (Sat/Sun)
- `quarter` (1-4)

**Why critical:** Captures weekly/monthly patterns, weekday vs weekend

#### 3. **Lag Features** (Historical momentum)
For CASES (by store-dept):
- `cases_lag_1` - Yesterday's cases
- `cases_lag_7` - 1 week ago
- `cases_lag_14` - 2 weeks ago
- `cases_lag_28` - 4 weeks ago

For TRUCKS (by store):
- `trucks_lag_1`
- `trucks_lag_7`
- `trucks_lag_14`

**Why critical:** Recent history is the strongest predictor for short-term forecasts

#### 4. **Rolling/Moving Average Features**
For CASES (by store-dept):
- `cases_ma_7` - 7-day moving average
- `cases_ma_14` - 14-day moving average
- `cases_ma_28` - 28-day moving average
- `cases_std_7` - 7-day rolling standard deviation (volatility)

For TRUCKS (by store):
- `trucks_ma_7`
- `trucks_ma_14`

**Why critical:** Smooths noise, captures trends

---

### Priority 2: USEFUL (Add if Time Permits)

#### 5. **Aggregated Statistics**
- `store_dept_avg_cases` - Historical average for this store-dept combo
- `dept_avg_cases` - Department average across all stores
- `store_dow_avg_cases` - This store-dept's average for this day-of-week

**Why useful:** Captures baseline performance levels

#### 6. **Interaction Features**
- `trucks_x_dow` - Trucks × Day of week
- `dept_x_month` - Department × Month (seasonality by dept)

**Why useful:** Captures non-linear relationships

---

### Priority 3: ADVANCED (Only if Time/Resources Allow)

#### 7. **Weather Data**
- Daily temperature (state/city level)
- Precipitation
- Extreme weather flags

**Why useful but hard:**
- Relevant for Sporting Goods (weather affects outdoor activities)
- Relevant for Dairy (temperature affects consumption)
- BUT: Requires API calls, complex to get forecast data for Aug-Sep 2025

#### 8. **Store Clustering Features**
- Cluster stores by behavior patterns
- Add cluster ID as feature

**Why useful:** Captures store similarities beyond geography

---

## 📊 FINAL RECOMMENDED FEATURE SET

### Keep from External Data (4):
1. state_unemployment_rate ⭐
2. CPI_All_Items
3. Consumer_Sentiment
4. Crude_Oil_Price

### Must Add (4 categories):
1. Holiday calendar ✅ (already created)
2. Temporal features (7 features)
3. Lag features (7 features)
4. Rolling features (8 features)

### Total Feature Count: ~35-40 features
- Identifiers: 3 (store_id, dept_id, dt)
- Target: 1 (cases)
- Original: 6 (trucks, state, market, region, dept_desc, gmm)
- External: 4 (unemployment, CPI, sentiment, oil)
- Holidays: 8 features
- Temporal: 7 features
- Lags: 7 features
- Rolling: 8 features

---

## 🎯 NEXT STEPS

1. ✅ **Holiday calendar created** → `data/external/holiday_calendar.csv`
2. **Create feature engineering notebook** to add:
   - Temporal features
   - Lag features
   - Rolling features
   - Aggregates
3. **Drop unnecessary features:**
   - student_group
   - Fed_Funds_Rate
   - Initial_Jobless_Claims
   - (optionally) CPI_FoodAtHome
4. **Save final modeling dataset** → `data/processed/modeling_data.csv`

---

## 📈 EXPECTED IMPACT ON MODEL

### Your Current External Data (4 features):
- **Expected MAPE improvement:** 2-5%
- **Value:** Shows data sourcing skills, captures macro trends

### With All Recommended Features:
- **Expected MAPE improvement:** 15-25%
- **Value:** Core forecasting features that capture patterns, trends, seasonality

### Bottom Line:
External macro data is **academically interesting** but **secondary**.
Time series features (lags, rolling, holidays) are **essential** for good performance.

---

## 📁 FILES CREATED

- `data/external/holiday_calendar.csv` - Holiday/event calendar (550 days)
- `data/external/EXTERNAL_DATA_SUMMARY.md` - This file

## 📁 FILES TO USE

- `data/processed/merged_data.csv` - Original merged data (use this as base)
- `data/processed/merged_data_with_external.csv` - Your version with macro data

**Recommendation:** Start from `merged_data.csv`, add the 4 useful external features + holidays + engineered features
