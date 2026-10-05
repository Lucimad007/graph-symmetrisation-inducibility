"""Compare induced density with the candidate multipartite defect.

For each random graph the script records the exact density of one motif and
the candidate edit fraction from ``multipartite_defect``. The plot is a
scatter. A downward trend would be consistent with the shape of perfect
stability and is not evidence for Theorem 1.4.
"""

from __future__ import annotations

import numpy as np

from experiments.common import FIGURES, write_json
from experiments.symmetrisation_run import random_graph
from graph.multipartite import multipartite_defect
from inducibility.density import exact_induced_density
from inducibility.motifs import MOTIFS


def run(n: int = 10, samples: int = 40, seed: int = 7, motif_name: str = "K22") -> dict:
    rng = np.random.default_rng(seed)
    motif = MOTIFS[motif_name]
    rows = []
    for probability in (0.2, 0.5, 0.8):
        for _ in range(samples):
            graph = random_graph(n, probability, rng)
            rows.append(
                {
                    "edge_probability": probability,
                    "density": exact_induced_density(graph, motif),
                    "defect": multipartite_defect(graph),
                    "edges": graph.number_of_edges,
                }
            )
    payload = {
        "n": n,
        "samples_per_probability": samples,
        "seed": seed,
        "motif": motif_name,
        "density_is": "exact enumeration",
        "rows": rows,
    }
    write_json("stability_scan.json", payload)
    _figure(payload)
    return payload


def _figure(payload: dict) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    FIGURES.mkdir(parents=True, exist_ok=True)
    figure, axis = plt.subplots(figsize=(5.2, 3.8))
    for probability in (0.2, 0.5, 0.8):
        subset = [row for row in payload["rows"] if row["edge_probability"] == probability]
        axis.scatter(
            [row["defect"] for row in subset],
            [row["density"] for row in subset],
            s=16,
            label=f"p = {probability}",
        )
    axis.set_xlabel("candidate edit fraction")
    axis.set_ylabel(f"exact induced density of {payload['motif']}")
    axis.set_title(f"n = {payload['n']}, seed {payload['seed']}")
    axis.legend(frameon=False, fontsize=8)
    figure.tight_layout()
    figure.savefig(FIGURES / "stability_scan.png", dpi=140)
    plt.close(figure)


if __name__ == "__main__":
    run()
