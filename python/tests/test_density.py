from math import comb

from graph.multipartite import complete_multipartite
from inducibility.density import (
    combinatorial_count_in_host,
    exact_induced_count,
    exact_induced_density,
    limit_induced_density,
    sample_induced_density,
)
from inducibility.motifs import MOTIFS

import numpy as np


def test_c4_in_balanced_complete_bipartite_is_exact():
    graph = complete_multipartite((3, 3))
    assert exact_induced_count(graph, MOTIFS["K22"]) == comb(3, 2) * comb(3, 2)
    assert combinatorial_count_in_host(MOTIFS["K22"], (3, 3)) == exact_induced_count(graph, MOTIFS["K22"])


def test_limit_densities_of_the_two_section6_constructions():
    eight = limit_induced_density(MOTIFS["K2111"], (1 / 8,) * 8)
    clique_plus_singletons = limit_induced_density(MOTIFS["K311"], (3 / 5,))
    assert abs(eight - 525 / 1024) < 1e-12
    assert abs(clique_plus_singletons - 216 / 625) < 1e-12


def test_empty_graph_has_no_induced_c4():
    from graph.graph import Graph

    assert exact_induced_density(Graph.empty(6), MOTIFS["K22"]) == 0.0


def test_sample_is_labelled_and_close_on_a_deterministic_host():
    graph = complete_multipartite((6, 6))
    exact = exact_induced_density(graph, MOTIFS["K22"])
    estimate = sample_induced_density(graph, MOTIFS["K22"], samples=400, rng=np.random.default_rng(0))
    assert estimate.method.startswith("uniform")
    assert abs(estimate.estimate - exact) < 0.08
