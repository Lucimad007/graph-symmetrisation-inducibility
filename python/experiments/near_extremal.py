"""Edit a known extremal host and watch the induced density fall.

Random graphs at n = 10 never get near the extremal density, so they cannot
show the stability shape. This run starts from the complete multipartite
graph that realises a high-density construction and toggles a controlled
number of pairs. Densities are exact enumerations. The candidate defect is
the same edit fraction used elsewhere. The plot is descriptive: it is not
Theorem 1.4.
"""

from __future__ import annotations

import numpy as np

from experiments.common import FIGURES, write_json
from graph.graph import Graph
from graph.multipartite import complete_multipartite, multipartite_defect, realise
from inducibility.density import exact_induced_density
from inducibility.edits import pair_edit_drop
from inducibility.motifs import MOTIFS


HOSTS = (
    {"name": "balanced K_{n/2,n/2}", "motif": "K22", "ratios": (0.5, 0.5), "n": 20},
    {"name": "part 3/5 plus singletons", "motif": "K311", "ratios": (0.6,), "n": 15},
)


def _toggle_random(graph: Graph, count: int, rng: np.random.Generator) -> None:
    if count == 0 or graph.n < 2:
        return
    pairs = [(u, v) for u in range(graph.n) for v in range(u + 1, graph.n)]
    chosen = rng.choice(len(pairs), size=min(count, len(pairs)), replace=False)
    for index in chosen:
        u, v = pairs[int(index)]
        if graph.has_edge(u, v):
            graph.remove_edge(u, v)
        else:
            graph.add_edge(u, v)


def _host(ratios: tuple[float, ...], n: int) -> Graph:
    singletons, sizes = realise(n, ratios)
    return complete_multipartite(sizes, singletons)


def run(seed: int = 11, budgets: tuple[int, ...] = (0, 1, 2, 4, 8, 12, 20, 30), replicates: int = 4) -> dict:
    rng = np.random.default_rng(seed)
    rows = []
    one_edge = []
    for host in HOSTS:
        motif = MOTIFS[host["motif"]]
        clean = _host(host["ratios"], host["n"])
        base = exact_induced_density(clean, motif)
        singletons, sizes = realise(host["n"], host["ratios"])
        inside = pair_edit_drop(motif, sizes, singletons, 0, 0) if sizes and sizes[0] >= 2 else None
        across = None
        if len(sizes) >= 2:
            across = pair_edit_drop(motif, sizes, singletons, 0, 1)
        elif singletons >= 1 and sizes:
            across = pair_edit_drop(motif, sizes, singletons, 0, -1)
        one_edge.append(
            {
                "host": host["name"],
                "motif": host["motif"],
                "n": host["n"],
                "copies_lost_adding_an_edge_inside_the_largest_part": inside,
                "copies_lost_deleting_a_cross_edge": across,
                "paper": "Theorem 1.4 (i), finite count only",
            }
        )
        for budget in budgets:
            for replicate in range(replicates):
                graph = clean.copy()
                _toggle_random(graph, budget, rng)
                density = exact_induced_density(graph, motif)
                rows.append(
                    {
                        "host": host["name"],
                        "motif": host["motif"],
                        "n": host["n"],
                        "toggles": budget,
                        "replicate": replicate,
                        "density": density,
                        "density_drop": base - density,
                        "clean_density": base,
                        "defect": multipartite_defect(graph),
                    }
                )
    payload = {
        "seed": seed,
        "density_is": "exact enumeration",
        "operation": "toggle a uniform random set of pairs, starting from the extremal host",
        "one_edge": one_edge,
        "rows": rows,
    }
    write_json("near_extremal.json", payload)
    _figure(payload)
    return payload


def _figure(payload: dict) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    FIGURES.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update(
        {
            "axes.spines.top": False,
            "axes.spines.right": False,
            "font.size": 11,
            "axes.titlesize": 12,
        }
    )
    figure, axes = plt.subplots(1, 2, figsize=(9.4, 3.8))
    colors = {"K22": "#9a3412", "K311": "#1d4e89"}
    for motif, color in colors.items():
        subset = [row for row in payload["rows"] if row["motif"] == motif]
        axes[0].scatter(
            [row["toggles"] for row in subset],
            [row["density"] for row in subset],
            s=22,
            alpha=0.85,
            c=color,
            label=motif,
        )
        by_budget: dict[int, list[float]] = {}
        for row in subset:
            by_budget.setdefault(row["toggles"], []).append(row["density_drop"])
        budgets = sorted(by_budget)
        means = [float(np.mean(by_budget[b])) for b in budgets]
        axes[1].plot(budgets, means, marker="o", color=color, label=motif)
    axes[0].set_xlabel("pairs toggled")
    axes[0].set_ylabel("exact induced density")
    axes[0].set_title("After random edits of an extremal host")
    axes[0].legend(frameon=False)
    axes[1].set_xlabel("pairs toggled")
    axes[1].set_ylabel("mean density drop from the host")
    axes[1].set_title("Same runs, against the edit budget")
    axes[1].legend(frameon=False)
    figure.tight_layout()
    figure.savefig(FIGURES / "near_extremal.png", dpi=160)
    plt.close(figure)


if __name__ == "__main__":
    run()
