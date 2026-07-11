# Maximum uncertainty and variability months align, not separate

**Frozen claim verdict: REFUTED.** In the untouched confirmation split, the month
with greatest median reported uncertainty overlapped the month with greatest
detrended interannual temperature variability for **438/792 coordinate-defined
city series (55.303%)**, compared with a random-relabeling mean of **8.371%**.
The entity-bootstrap 95% interval was **51.768%–58.712%**. Mean circular distance
was **0.717 months** (95% CI **0.643–0.795**) versus random-label mean **2.998
months**. Both preregistered tests of separation reversed (`p_fewer_matches=1.0`,
`p_larger_distance=1.0`; 20,000 relabelings).

The development split independently showed essentially the same values: 432/781
(55.314%, 95% CI 51.857%–58.771%) and 0.720 months (95% CI 0.644–0.796).
This landed far outside the registered 65%-confidence prior of weak/no separation,
but in the opposite direction from the gated hypothesis.

## Definitions and coverage

Input is Kaggle's Berkeley Earth `GlobalLandTemperaturesByCity.csv`, SHA-256
`9be86b51487f10e811a0ab43a75946739dfe7bea2342ddcd1f6bc48d51b8c493`.
An entity is an exact `(City, Country, Latitude, Longitude)` tuple. Eligible series
had at least 20 complete 12-month calendar years from 1750–1849; confirmation
entities had 20–97 complete years (median 72). Only balanced complete years entered
all monthly summaries. Variability is residual SD after a month-specific linear
trend on year; uncertainty is the monthly median of Berkeley's reported uncertainty.
Three confirmation entities tied for maximum uncertainty; none tied for maximum
variability, and the analysis retained set-valued ties as preregistered.

## Falsification and robustness

Every prespecified check remained strongly aligned: mean uncertainty (56.1% match),
raw rather than detrended SD (53.7%), 10-year minimum (44.4%, n=1,099), 30-year
minimum (55.8%, n=684), tie exclusion (55.3%, n=789), and the non-confirmatory
1850–1899 transport window (34.1%, n=1,707). All had `p=1.0` in both originally
claimed separation directions. The later window weakens the magnitude but not the
direction.

## Honest scope and caveats

These are rough city-level reconstruction series, not independent thermometers.
Nearby cities may share source observations and gridded reconstruction behavior;
the entity bootstrap therefore quantifies dispersion across listed coordinate
series but may overstate effective independent sample size. Eligibility selects
the comparatively well-covered early record, and changing the 20-year threshold
changes the effect magnitude. The result describes the supplied records and their
reported uncertainty, not a physical law relating weather variance to measurement
error. Spatial dependence and upstream reconstruction mechanics remain plausible
explanations for the alignment.

## Novelty check

Three public-web searches on Berkeley Earth seasonal uncertainty, city variability,
and maximizing-month alignment found dataset documentation and general seasonal
variability discussions but no source stating this exact early-city record fact.
That is a limited negative search, not proof of novelty.

