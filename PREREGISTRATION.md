# Frozen hypothesis and analysis plan

## Hypothesis

Among Berkeley Earth city-coordinate series with at least 20 complete calendar
years in 1750–1849, the month having the largest median reported temperature
uncertainty is seasonally separated from the month having the largest detrended
interannual temperature variability.

## Registered prior (before inspecting rows)

Inherited from gated candidate C01: expect weak or no consistent separation,
with 65% confidence; any standardized separation should be smaller than a
modest effect. Concretely, I expect the confirmation-set exact-match rate not to
be detectably below the random-label value 1/12 and the mean circular month
distance not to be detectably above the random-label value 3 months.

## Frozen cohort and estimands

- Input: `GlobalLandTemperaturesByCity.csv` from Kaggle dataset
  `berkeleyearth/climate-change-earth-surface-temperature-data`.
- An entity is the exact `(City, Country, Latitude, Longitude)` tuple. This avoids
  silently pooling distinct coordinate series with the same city label.
- Early window: 1750-01-01 through 1849-12-31 inclusive.
- A complete year has 12 non-null temperatures and 12 non-null uncertainty
  values. An entity is eligible with at least 20 complete years. Only those same
  complete years enter all twelve monthly summaries.
- For each entity and calendar month, uncertainty is the median reported
  `AverageTemperatureUncertainty`. Variability is the sample standard deviation
  of residuals after an OLS regression of that month's temperature on year.
- The two entity-level outcomes are exact equality of the maximizing months and
  their circular distance `min(|a-b|, 12-|a-b|)` (0–6 months).
- Ties are retained as sets. Exact match means the two maximizing sets overlap;
  distance is the minimum pairwise circular distance. A sensitivity analysis
  excludes any entity tied under either measure.

## Exploration, confirmation, uncertainty, and decision

Entities are assigned by SHA-256 of their canonical tuple: first hexadecimal
nibble 0–7 is development and 8–f is confirmation. The confirmation set is
opened only after the code and development output are frozen. The headline uses
the confirmation set. Entity bootstrap (20,000 resamples, seed 2859) gives 95%
percentile intervals for the exact-match fraction and mean circular distance.
A within-entity random relabeling test (20,000 draws, seed 2859) supplies null
distributions whose expectations are 1/12 and 3 months.

GREEN requires the confirmation result to show separation in both directions:
the one-sided randomization p-value is below 0.025 for fewer exact matches and
below 0.025 for larger mean circular distance. REFUTED means both directions
fail or reverse. Otherwise the verdict is RED. No tuning or cohort changes after
the development split is inspected; robustness analyses may only weaken the
headline.

Robustness checks: tied-maxima exclusion; mean rather than median uncertainty;
raw rather than detrended temperature SD; minimum 10 and 30 complete years;
and the later 1850–1899 window as an explicitly non-confirmatory transport check.

