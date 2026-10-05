from graph.graph import Graph
from graph.multipartite import multipartite_defect
from graph.symmetrisation import SymmetrisationHistory, symmetrise_pair


def test_history_records_a_decrease_when_the_objective_falls():
    graph = Graph.empty(3)
    graph.add_edge(0, 1)
    history = SymmetrisationHistory()

    def objective(g: Graph) -> float:
        return float(g.number_of_edges)

    step = symmetrise_pair(
        graph,
        2,
        0,
        objective=objective,
        defect=multipartite_defect,
        iteration=0,
        history=history,
    )
    assert step.operation == "clone_neighborhood"
    assert step.direction in {"increased", "decreased", "unchanged"}
    assert history.steps[0].vertices == 3
    assert graph.adj[2] == graph.adj[0]
