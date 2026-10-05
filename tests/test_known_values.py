"""Recover the constants computed in the paper."""

from math import comb

from syminduc.density import (
    bipartite_inducibility_from_alpha,
    finite_induced_count,
    finite_induced_density,
    limit_induced_density,
    pair_edit_drop,
)
from syminduc.optimize import maximise_bipartite
from syminduc.partite import PartiteVector, complete_partite_edges, realise
from syminduc.symmetrise import Graph, symmetrise_edges


def test_c4_balanced_bipartite():
    # C4 = K_{2,2}, lambda_max = 3/8.
    host = PartiteVector.balanced(2)
    assert abs(limit_induced_density((2, 2), host) - 3 / 8) < 1e-12


def test_k41_at_four_fifths():
    host = PartiteVector.bipartite(4 / 5)
    density = limit_induced_density((4, 1), host)
    expected = bipartite_inducibility_from_alpha(4, 1, 4 / 5)
    assert abs(density - expected) < 1e-12
    found = maximise_bipartite(4, 1)
    # The paper records 4/5, the critical point of the leading term
    # alpha^4 (1-alpha). The second term shifts the true maximum slightly.
    assert abs(found.vector.parts[0] - 0.8) < 0.02
    assert found.value + 1e-12 >= expected


def test_k311_value():
    # Theorem 1.9: i(K_{3,1,1}) = 216/625 at (3/5, 0, ...) with x0 = 2/5.
    host = PartiteVector((3 / 5,))
    assert abs(host.x0 - 2 / 5) < 1e-12
    assert abs(limit_induced_density((3, 1, 1), host) - 216 / 625) < 1e-12


def test_k2111_value():
    # Theorem 1.8: i(K_{2,1,1,1}) = 525/1024 on eight equal parts.
    host = PartiteVector.balanced(8)
    assert abs(limit_induced_density((2, 1, 1, 1), host) - 525 / 1024) < 1e-12


def test_balanced_complete_equipartite_formula():
    # On r equal parts the only occupancy that induces K_r(t) is t vertices
    # in every part, so the density is k! / ((t!)^r r^k). For r = t = 2 this
    # is 3/8, matching the C4 value stated in the paper. The displayed
    # formula in Theorem 1.7 has an extra r! in the denominator.
    r, t = 3, 2
    host = PartiteVector.balanced(r)
    k = r * t
    factorial_k = 1
    for i in range(2, k + 1):
        factorial_k *= i
    t_fact = 1
    for i in range(2, t + 1):
        t_fact *= i
    expected = factorial_k / ((t_fact**r) * (r**k))
    assert abs(limit_induced_density(tuple(t for _ in range(r)), host) - expected) < 1e-12


def test_finite_count_matches_limit_shape():
    # K_{2,2} in K_{3,3}: the only induced C4s are 4-sets with 2+2 vertices.
    assert finite_induced_count((2, 2), (3, 3)) == comb(3, 2) * comb(3, 2)
    small = finite_induced_density((2, 2), (5, 5))
    large = finite_induced_density((2, 2), (40, 40))
    assert abs(large - 3 / 8) < abs(small - 3 / 8)
    assert abs(large - 3 / 8) < 0.02


def test_realisation_balanced():
    sizes = realise(10, PartiteVector.balanced(2))
    assert sizes == (0, 5, 5)
    assert complete_partite_edges((5, 5)) == 25


def test_edit_inside_a_part_of_c4_hurts():
    # Balanced complete bipartite on 6+6 vertices. Adding an edge inside a
    # part destroys every C4 that used that pair as one side of the 2+2 split
    # and creates none.
    drop = pair_edit_drop((2, 2), (6, 6), 0, 0, 0)
    assert drop > 0


def test_symmetrisation_reaches_turan():
    # A triangle-free graph that is not complete bipartite: C5.
    # Vertices of a 5-cycle.
    edges = {(0, 1), (1, 2), (2, 3), (3, 4), (4, 0)}
    final, steps = symmetrise_edges(Graph(5, edges))
    assert steps >= 1
    assert final.is_complete_partite()
    assert len(final.edges) >= len(edges)
