"""One Zykov clone step and a record of a sequence of steps.

Reference: introduction of arXiv:2012.10731, and the edit condition in
Definition 1.1. A single call replaces ``x`` by a clone of ``y``. It does
not claim that the chosen objective is non-decreasing; the history stores
both values so an experiment can see the sign of the change.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field

from graph.graph import Graph

Objective = Callable[[Graph], float]


@dataclass(frozen=True)
class SymmetrisationStep:
    iteration: int
    source: int
    target: int
    operation: str
    objective_before: float
    objective_after: float
    vertices: int
    edges_before: int
    edges_after: int
    defect_before: float
    defect_after: float

    @property
    def objective_delta(self) -> float:
        return self.objective_after - self.objective_before

    @property
    def direction(self) -> str:
        if self.objective_delta > 1e-12:
            return "increased"
        if self.objective_delta < -1e-12:
            return "decreased"
        return "unchanged"


@dataclass
class SymmetrisationHistory:
    steps: list[SymmetrisationStep] = field(default_factory=list)

    def record(self, step: SymmetrisationStep) -> None:
        self.steps.append(step)


def symmetrise_pair(
    graph: Graph,
    x: int,
    y: int,
    *,
    objective: Objective,
    defect: Callable[[Graph], float],
    iteration: int,
    history: SymmetrisationHistory | None = None,
) -> SymmetrisationStep:
    """Clone ``x`` onto ``y`` and record the objective change.

    ``y`` is the vertex whose neighbourhood is copied. ``x`` is overwritten.
    """
    before = objective(graph)
    edges_before = graph.number_of_edges
    defect_before = defect(graph)
    graph.clone_neighborhood(x, y)
    step = SymmetrisationStep(
        iteration=iteration,
        source=x,
        target=y,
        operation="clone_neighborhood",
        objective_before=before,
        objective_after=objective(graph),
        vertices=graph.n,
        edges_before=edges_before,
        edges_after=graph.number_of_edges,
        defect_before=defect_before,
        defect_after=defect(graph),
    )
    if history is not None:
        history.record(step)
    return step
