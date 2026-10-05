from graph.graph import Graph


def test_edge_roundtrip_and_degree():
    graph = Graph.empty(4)
    graph.add_edge(0, 1)
    graph.add_edge(1, 2)
    assert graph.has_edge(0, 1)
    assert graph.degree(1) == 2
    assert graph.number_of_edges == 2
    assert graph.adjacency_matrix()[0, 1] == 1
    graph.remove_edge(0, 1)
    assert (0, 1) in graph.non_adjacent_pairs()


def test_add_and_remove_vertex_renumbers():
    graph = Graph.empty(3)
    graph.add_edge(1, 2)
    fresh = graph.add_vertex()
    assert fresh == 3
    graph.remove_vertex(0)
    assert graph.n == 3
    assert graph.has_edge(0, 1)


def test_clone_copies_neighbourhood_and_keeps_nonedge():
    graph = Graph.empty(4)
    graph.add_edge(1, 2)
    graph.add_edge(1, 3)
    graph.add_edge(0, 2)
    graph.clone_neighborhood(0, 1)
    assert graph.adj[0] == {2, 3}
    assert not graph.has_edge(0, 1)
    assert graph.has_edge(1, 2) and graph.has_edge(1, 3)


def test_copy_is_independent():
    graph = Graph.empty(2)
    other = graph.copy()
    other.add_edge(0, 1)
    assert graph.number_of_edges == 0
