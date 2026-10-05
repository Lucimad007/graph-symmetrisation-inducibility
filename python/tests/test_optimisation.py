from inducibility.motifs import MOTIFS
from optimisation.ratios import maximise_induced_density


def test_result_lies_in_the_ordered_simplex():
    found = maximise_induced_density(MOTIFS["K22"], max_parts=2, method="slsqp", grid=6, seed=1)
    assert found.success
    assert abs(sum(found.ratios) + found.singleton_mass - 1) < 1e-8
    assert list(found.ratios) == sorted(found.ratios, reverse=True)
    assert found.parts_used <= 2
    assert found.value > 0.3


def test_grid_method_does_not_invent_a_value():
    found = maximise_induced_density(MOTIFS["K311"], max_parts=2, method="grid", grid=5, seed=0)
    assert found.method == "grid"
    assert 0 <= found.value <= 1
