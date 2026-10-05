from graph.multipartite import complete_multipartite, multipartite_defect, part_ratios, realise


def test_balanced_ratios_realise_equal_parts():
    singletons, sizes = realise(12, (1 / 3, 1 / 3, 1 / 3))
    assert singletons == 0
    assert sizes == (4, 4, 4)
    graph = complete_multipartite(sizes)
    assert multipartite_defect(graph) == 0.0
    assert part_ratios(graph) == (1 / 3, 1 / 3, 1 / 3)


def test_singleton_mass_is_residual():
    singletons, sizes = realise(10, (3 / 5,))
    assert sizes == (6,)
    assert singletons == 4
    graph = complete_multipartite(sizes, singletons)
    assert part_ratios(graph) == (0.6,)
    assert multipartite_defect(graph) == 0.0


def test_one_extra_edge_inside_a_part_has_positive_defect():
    graph = complete_multipartite((4, 4))
    graph.add_edge(0, 1)
    assert multipartite_defect(graph) > 0
    assert part_ratios(graph) is None
