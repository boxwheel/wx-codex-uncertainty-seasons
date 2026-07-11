#!/usr/bin/env python3
"""Preregistered C01 analysis; see PREREGISTRATION.md."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ENTITY = ["City", "Country", "Latitude", "Longitude"]
SEED = 2859


def split_for(values: tuple[str, ...]) -> str:
    key = "|".join(values)
    return "development" if int(hashlib.sha256(key.encode()).hexdigest()[0], 16) < 8 else "confirmation"


def circular(a: int, b: int) -> int:
    d = abs(a - b)
    return min(d, 12 - d)


def make_entities(path: Path, start: int, end: int, min_years: int,
                  uncertainty_stat: str = "median", detrend: bool = True) -> pd.DataFrame:
    use = ["dt", "AverageTemperature", "AverageTemperatureUncertainty", *ENTITY]
    df = pd.read_csv(path, usecols=use, parse_dates=["dt"])
    df = df[df.dt.dt.year.between(start, end)].copy()
    df["year"] = df.dt.dt.year
    df["month"] = df.dt.dt.month
    df["valid"] = df.AverageTemperature.notna() & df.AverageTemperatureUncertainty.notna()

    # A balanced year has exactly one valid observation in every calendar month.
    yc = df.groupby(ENTITY + ["year"], observed=True).agg(
        valid=("valid", "sum"), rows=("month", "size"), distinct_months=("month", "nunique")
    ).reset_index()
    complete = yc[(yc.valid == 12) & (yc.rows == 12) & (yc.distinct_months == 12)]
    eligible = complete.groupby(ENTITY, observed=True).size().rename("complete_years").reset_index()
    eligible = eligible[eligible.complete_years >= min_years]
    bal = df.merge(complete[ENTITY + ["year"]], on=ENTITY + ["year"], how="inner")
    bal = bal.merge(eligible, on=ENTITY, how="inner")

    rows = []
    for key, g in bal.groupby(ENTITY, sort=True, observed=True):
        unc, var = {}, {}
        for month, m in g.groupby("month", observed=True):
            unc[int(month)] = float(getattr(m.AverageTemperatureUncertainty, uncertainty_stat)())
            y = m.year.to_numpy(float)
            t = m.AverageTemperature.to_numpy(float)
            if detrend:
                t = t - np.polyval(np.polyfit(y, t, 1), y)
            var[int(month)] = float(np.std(t, ddof=1))
        umax = max(unc.values()); vmax = max(var.values())
        uset = tuple(m for m, v in unc.items() if np.isclose(v, umax, rtol=0, atol=1e-12))
        vset = tuple(m for m, v in var.items() if np.isclose(v, vmax, rtol=0, atol=1e-12))
        dist = min(circular(a, b) for a in uset for b in vset)
        overlap = bool(set(uset) & set(vset))
        row = dict(zip(ENTITY, key))
        row.update(complete_years=int(g.complete_years.iloc[0]), uncertainty_max_months=",".join(map(str, uset)),
                   variability_max_months=",".join(map(str, vset)), exact_match=overlap,
                   circular_distance=dist, uncertainty_tie=len(uset) > 1, variability_tie=len(vset) > 1,
                   split=split_for(tuple(map(str, key))))
        rows.append(row)
    return pd.DataFrame(rows)


def summarize(x: pd.DataFrame, draws: int = 20_000) -> dict:
    rng = np.random.default_rng(SEED)
    n = len(x)
    match = x.exact_match.to_numpy(float)
    dist = x.circular_distance.to_numpy(float)
    boot_idx = rng.integers(0, n, size=(draws, n))
    bm = match[boot_idx].mean(axis=1)
    bd = dist[boot_idx].mean(axis=1)

    # Randomly relabel each entity's variability maximum month. Ties are rare;
    # simulation preserves each entity's number of maximizing months.
    u_sets = [tuple(map(int, s.split(","))) for s in x.uncertainty_max_months]
    v_sizes = np.array([len(s.split(",")) for s in x.variability_max_months])
    null_match = np.empty(draws); null_dist = np.empty(draws)
    months = np.arange(1, 13)
    # Lookup tables make the overwhelmingly common singleton-maximum case fast.
    membership = np.zeros((n, 12), dtype=bool)
    distance = np.zeros((n, 12), dtype=np.int8)
    for i, us in enumerate(u_sets):
        membership[i, np.array(us) - 1] = True
        distance[i] = [min(circular(a, int(b)) for a in us) for b in months]
    singleton = v_sizes == 1
    multi = np.flatnonzero(~singleton)
    for lo in range(0, draws, 1000):
        hi = min(lo + 1000, draws); size = hi - lo
        chosen = rng.integers(0, 12, size=(size, n))
        ms = membership[np.arange(n)[None, :], chosen]
        ds = distance[np.arange(n)[None, :], chosen]
        # Preserve the null set size if a variability maximum is tied.
        for i in multi:
            for j in range(size):
                vs = rng.choice(months, size=v_sizes[i], replace=False)
                ms[j, i] = bool(set(u_sets[i]) & set(vs.tolist()))
                ds[j, i] = min(circular(a, int(b)) for a in u_sets[i] for b in vs)
        null_match[lo:hi] = ms.mean(axis=1)
        null_dist[lo:hi] = ds.mean(axis=1)

    obs_m, obs_d = float(match.mean()), float(dist.mean())
    return {
        "n_entities": n,
        "complete_years_min": int(x.complete_years.min()),
        "complete_years_median": float(x.complete_years.median()),
        "complete_years_max": int(x.complete_years.max()),
        "exact_matches": int(match.sum()),
        "exact_match_fraction": obs_m,
        "exact_match_bootstrap_95_ci": np.quantile(bm, [0.025, 0.975]).tolist(),
        "mean_circular_distance_months": obs_d,
        "distance_bootstrap_95_ci": np.quantile(bd, [0.025, 0.975]).tolist(),
        "null_match_mean": float(null_match.mean()),
        "null_distance_mean": float(null_dist.mean()),
        "p_fewer_matches": float((1 + np.sum(null_match <= obs_m)) / (draws + 1)),
        "p_larger_distance": float((1 + np.sum(null_dist >= obs_d)) / (draws + 1)),
        "uncertainty_ties": int(x.uncertainty_tie.sum()),
        "variability_ties": int(x.variability_tie.sum()),
        "seed": SEED,
        "draws": draws,
    }


def plot_result(x: pd.DataFrame, out: Path, title: str) -> None:
    counts = x.circular_distance.value_counts().reindex(range(7), fill_value=0)
    fig, ax = plt.subplots(figsize=(8, 4.8))
    ax.bar(counts.index, counts.values, color="#3b82f6")
    ax.set(xlabel="Circular distance between maximizing months", ylabel="Entities", title=title)
    ax.set_xticks(range(7)); ax.grid(axis="y", alpha=.25)
    fig.tight_layout(); fig.savefig(out, dpi=180); plt.close(fig)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--csv", type=Path, required=True)
    p.add_argument("--split", choices=["development", "confirmation"], required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--draws", type=int, default=20_000)
    a = p.parse_args(); a.out.mkdir(parents=True, exist_ok=True)
    entities = make_entities(a.csv, 1750, 1849, 20)
    selected = entities[entities.split == a.split].reset_index(drop=True)
    result = summarize(selected, a.draws)
    result.update(split=a.split, window="1750-1849", min_complete_years=20,
                  input_sha256=hashlib.sha256(a.csv.read_bytes()).hexdigest())
    selected.to_csv(a.out / f"entities_{a.split}.csv", index=False)
    (a.out / f"results_{a.split}.json").write_text(json.dumps(result, indent=2) + "\n")
    plot_result(selected, a.out / f"distance_{a.split}.png",
                f"Early-city uncertainty vs variability maxima ({a.split}, n={len(selected)})")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
