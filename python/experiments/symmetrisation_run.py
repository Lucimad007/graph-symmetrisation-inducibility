"""Flagship symmetrisation trajectories.

Each run starts from an Erdős–Rényi graph G(n, p) with a fixed seed. At every
step the algorithm looks at non-adjacent pairs whose neighbourhoods differ
and clones the lower-degree endpoint onto the higher-degree one. That is the
edge-non-decreasing rule from the introduction's proof of Turán's theorem.
It is not claimed to be monotone for induced density.

For every motif the exact induced density and the candidate multipartite
defect are recorded after each step. The figure is a plot of those series.
"""

from __future__ import annotations

from graph.graph import Graph
from graph.multipartite import multipartite_defect
from graph.symmetrisation import SymmetrisationHistory, symmetrise_pair
from inducibility.density import exact_induced_density
from inducibility.motifs import MOTIFS

import numpy as np

from experiments.common import FIGURES, write_json


def random_graph(n: int, probability: float, rng: np.random.Generator) -> Graph:
    graph = Graph.empty(n)
    for u in range(n):
        for v in range(u + 1, n):
            if rng.random() < probability:
                graph.add_edge(u, v)
    return graph


def _next_pair(graph: Graph) -> tuple[int, int] | None:
    best: tuple[int, int, int] | None = None
    degrees = [graph.degree(v) for v in range(graph.n)]
    for u, v in graph.non_adjacent_pairs():
        if degrees[u] <= degrees[v]:
            source, target = u, v
        else:
            source, target = v, u
        if graph.adj[source] == graph.adj[target]:
            continue
        gap = degrees[target] - degrees[source]
        if best is None or gap > best[0]:
            best = (gap, source, target)
    if best is None:
        return None
    return best[1], best[2]


def run_trajectory(n: int, probability: float, seed: int, max_steps: int = 40) -> dict:
    rng = np.random.default_rng(seed)
    graph = random_graph(n, probability, rng)
    history = SymmetrisationHistory()
    series: dict[str, list[float]] = {name: [exact_induced_density(graph, motif)] for name, motif in MOTIFS.items()}
    defects = [multipartite_defect(graph)]
    edges = [graph.number_of_edges]
    iteration = 0
    while iteration < max_steps:
        pair = _next_pair(graph)
        if pair is None:
            break
        # The recorded objective is the edge count, matching the Turán rule
        # that selected the pair. Motif densities are measured separately.
        symmetrise_pair(
            graph,
            pair[0],
            pair[1],
            objective=lambda g: float(g.number_of_edges),
            defect=multipartite_defect,
            iteration=iteration,
            history=history,
        )
        for name, motif in MOTIFS.items():
            series[name].append(exact_induced_density(graph, motif))
        defects.append(multipartite_defect(graph))
        edges.append(graph.number_of_edges)
        iteration += 1
    return {
        "seed": seed,
        "n": n,
        "edge_probability": probability,
        "steps": iteration,
        "selection_rule": "clone the lower-degree endpoint of a non-edge onto the higher-degree endpoint",
        "densities_are": "exact enumeration",
        "defect_is": "candidate multipartite edit fraction from non-edge components",
        "density": series,
        "defect": defects,
        "edges": edges,
        "directions_of_edge_count": [step.direction for step in history.steps],
        "final_defect": defects[-1],
    }


def run(seeds: tuple[int, ...] = (0, 1, 2), n: int = 11, probability: float = 0.35) -> dict:
    trajectories = [run_trajectory(n, probability, seed) for seed in seeds]
    payload = {
        "n": n,
        "edge_probability": probability,
        "seeds": list(seeds),
        "note": (
            "Edge count is the objective used to choose the pair. "
            "Induced densities are measurements, not the selection criterion."
        ),
        "trajectories": trajectories,
    }
    write_json("symmetrisation.json", payload)
    _figure(payload)
    return payload


def _figure(payload: dict) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    FIGURES.mkdir(parents=True, exist_ok=True)
    trajectory = payload["trajectories"][0]
    figure, axes = plt.subplots(1, 2, figsize=(9.2, 3.6))
    for name, values in trajectory["density"].items():
        axes[0].plot(range(len(values)), values, marker="o", markersize=3, label=name)
    axes[0].set_xlabel("clone step")
    axes[0].set_ylabel("exact induced density")
    axes[0].set_title(f"G({trajectory['n']}, {trajectory['edge_probability']}), seed {trajectory['seed']}")
    axes[0].legend(frameon=False, fontsize=8)
    axes[1].plot(range(len(trajectory["defect"])), trajectory["defect"], color="#9a3412", marker="o", markersize=3)
    axes[1].set_xlabel("clone step")
    axes[1].set_ylabel("candidate edit fraction")
    axes[1].set_title("Distance to the candidate multipartite graph")
    figure.tight_layout()
    figure.savefig(FIGURES / "symmetrisation.png", dpi=140)
    plt.close(figure)


if __name__ == "__main__":
    run()
