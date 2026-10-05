"""Numerical recovery of the limit densities in Theorems 1.8 and 1.9.

The optimiser evaluates ``limit_induced_density`` on the simplex. The
fractions 525/1024 and 216/625 are stored only as the paper's stated values,
so the report can show the absolute error. They are not returned in place of
the computed objective.

Search range: up to 8 parts, which is enough to represent both stated
maximisers (eight equal parts, and one part plus singleton mass). A maximiser
with more than 8 positive parts would be invisible to this run.
"""

from __future__ import annotations

from dataclasses import asdict

from experiments.common import write_json
from inducibility.motifs import MOTIFS
from optimisation.ratios import maximise_induced_density

PAPER = {
    "K2111": {
        "theorem": "Theorem 1.8",
        "stated_value": 525 / 1024,
        "stated_ratios": (1 / 8,) * 8,
        "stated_singleton_mass": 0.0,
    },
    "K311": {
        "theorem": "Theorem 1.9",
        "stated_value": 216 / 625,
        "stated_ratios": (3 / 5,),
        "stated_singleton_mass": 2 / 5,
    },
}


def run(grid: int = 8, seed: int = 0) -> dict:
    rows = []
    for name, paper in PAPER.items():
        found = maximise_induced_density(MOTIFS[name], max_parts=8, method="slsqp", grid=grid, seed=seed)
        rows.append(
            {
                "theorem": paper["theorem"],
                "paper_value": paper["stated_value"],
                "paper_ratios": list(paper["stated_ratios"]),
                "paper_singleton_mass": paper["stated_singleton_mass"],
                "computed": asdict(found),
                "absolute_error": abs(found.value - paper["stated_value"]),
                "exact_arithmetic_label": "limit polynomial evaluated in float64",
            }
        )
    payload = {
        "seed": seed,
        "grid": grid,
        "max_parts": 8,
        "method": "slsqp",
        "claim": (
            "These are numerical values of the limit induced density. "
            "They are not a proof of Theorems 1.8 or 1.9."
        ),
        "rows": rows,
    }
    write_json("section6.json", payload)
    return payload


if __name__ == "__main__":
    report = run()
    for row in report["rows"]:
        computed = row["computed"]
        print(
            row["theorem"],
            "computed",
            computed["value"],
            "paper",
            row["paper_value"],
            "abs",
            row["absolute_error"],
            "ratios",
            computed["ratios"],
        )
