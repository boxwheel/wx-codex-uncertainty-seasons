#!/usr/bin/env python3
"""Prespecified robustness checks for the confirmed C01 result."""

import argparse
import json
from pathlib import Path

from analyze import make_entities, summarize


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--csv", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--draws", type=int, default=5000)
    a = p.parse_args(); a.out.mkdir(parents=True, exist_ok=True)
    specs = {
        "primary": (1750, 1849, 20, "median", True),
        "mean_uncertainty": (1750, 1849, 20, "mean", True),
        "raw_sd": (1750, 1849, 20, "median", False),
        "min_10_years": (1750, 1849, 10, "median", True),
        "min_30_years": (1750, 1849, 30, "median", True),
        "transport_1850_1899": (1850, 1899, 20, "median", True),
    }
    output = {}
    primary = None
    for name, spec in specs.items():
        e = make_entities(a.csv, *spec)
        x = e[e.split == "confirmation"].reset_index(drop=True)
        output[name] = summarize(x, a.draws)
        if name == "primary": primary = x
    untied = primary[~primary.uncertainty_tie & ~primary.variability_tie].reset_index(drop=True)
    output["exclude_ties"] = summarize(untied, a.draws)
    (a.out / "robustness_confirmation.json").write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
