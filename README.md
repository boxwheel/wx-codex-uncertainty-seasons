# Seasonal uncertainty–variability mismatch

This repository tests the frozen Berkeley Earth record-level claim that, within
early city records, the calendar month of greatest reported uncertainty differs
systematically from the month of greatest interannual temperature variability.

The design was registered in `PREREGISTRATION.md` before any dataset rows were
downloaded or inspected. The frozen development split (781 coordinate entities)
points opposite the candidate: maxima matched in 432/781 entities (55.31%, 95%
bootstrap CI 51.86–58.77%) versus a random-relabeling mean of 8.39%; mean circular
distance was only 0.720 months (95% CI 0.644–0.796) versus null 2.997. Confirmation
had not been opened when this checkpoint was committed.

Reproduce the development checkpoint:

```bash
python -m venv .venv
.venv/bin/pip install pandas numpy scipy matplotlib kaggle
.venv/bin/kaggle datasets download -d berkeleyearth/climate-change-earth-surface-temperature-data -p data
unzip data/climate-change-earth-surface-temperature-data.zip -d data/raw
.venv/bin/python analyze.py --csv data/raw/GlobalLandTemperaturesByCity.csv \
  --split development --out artifacts
```
