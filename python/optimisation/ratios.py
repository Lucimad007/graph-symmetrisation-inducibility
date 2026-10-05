"""Numerical maximisation of the limit induced density over part ratios.

The decision variable is a point of the partite limit space from Section 2:

    x_1 >= x_2 >= ... >= x_r >= 0,  sum_{i=1}^r x_i <= 1.

The residual ``1 - sum x_i`` is singleton mass. The objective is
``limit_induced_density``, which the optimiser evaluates. Theorem values are
not inserted as return values.

Two methods are available.

* ``grid`` evaluates every balanced vector and a non-increasing grid in at
  most three coordinates. It is deterministic. It can miss a maximiser that
  uses four or more unequal parts and sits off the balanced rays.
* ``slsqp`` runs SciPy SLSQP from several feasible starts, including the best
  grid point. Success flags and iteration counts are returned. SLSQP can
  stop at a local maximum; the experiment reports the best value found, not
  a certificate of uniqueness.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from scipy.optimize import OptimizeResult, minimize

from inducibility.density import limit_induced_density
from inducibility.motifs import Motif


@dataclass(frozen=True)
class OptimisationResult:
    motif: str
    value: float
    ratios: tuple[float, ...]
    parts_used: int
    singleton_mass: float
    method: str
    success: bool
    message: str
    evaluations: int
    starts: int
    grid_resolution: int | None = None
    notes: tuple[str, ...] = field(default_factory=tuple)


def maximise_induced_density(
    motif: Motif,
    *,
    max_parts: int,
    method: str = "slsqp",
    grid: int = 12,
    seed: int = 0,
) -> OptimisationResult:
    if max_parts < 1:
        raise ValueError("max_parts must be positive")
    if method not in {"grid", "slsqp"}:
        raise ValueError("method must be 'grid' or 'slsqp'")
    best_point, best_value, grid_evals = _grid_search(motif, max_parts, grid)
    if method == "grid":
        return _pack(motif, best_point, best_value, "grid", True, "best grid point", grid_evals, 1, grid)
    rng = np.random.default_rng(seed)
    starts = [best_point]
    for _ in range(max(4, max_parts)):
        starts.append(_random_start(max_parts, rng))
    starts.append(tuple(1.0 / max_parts for _ in range(max_parts)))
    champion = best_point
    champion_value = best_value
    evaluations = grid_evals
    successes = 0
    messages: list[str] = []
    for start in starts:
        result, count = _slsqp(motif, start)
        evaluations += count
        if result.success:
            successes += 1
        messages.append(str(result.message))
        candidate = _project(tuple(float(v) for v in result.x))
        value = float(limit_induced_density(motif, candidate))
        if value > champion_value + 1e-15:
            champion = candidate
            champion_value = value
    return _pack(
        motif,
        champion,
        champion_value,
        "slsqp",
        successes > 0,
        messages[-1] if messages else "",
        evaluations,
        len(starts),
        grid,
        notes=(f"{successes}/{len(starts)} SLSQP starts reported success",),
    )


def _pack(
    motif: Motif,
    point: tuple[float, ...],
    value: float,
    method: str,
    success: bool,
    message: str,
    evaluations: int,
    starts: int,
    grid: int,
    notes: tuple[str, ...] = (),
) -> OptimisationResult:
    # SLSQP leaves coordinates around 1e-7 that do not change the density
    # at the reported precision. They are dropped from the displayed vector.
    cleaned = tuple(p for p in point if p > 1e-5)
    return OptimisationResult(
        motif=motif.name,
        value=value,
        ratios=cleaned,
        parts_used=len(cleaned),
        singleton_mass=max(0.0, 1.0 - sum(cleaned)),
        method=method,
        success=success,
        message=message,
        evaluations=evaluations,
        starts=starts,
        grid_resolution=grid,
        notes=notes,
    )


def _grid_search(motif: Motif, max_parts: int, grid: int) -> tuple[tuple[float, ...], float, int]:
    """Budgeted search on the ordered simplex.

    A complete grid in ``max_parts`` dimensions is not feasible (the number of
    non-increasing nodes grows like a polynomial of degree ``max_parts``).
    The search therefore evaluates:

    * the balanced vector with ``r`` equal parts, for every ``r <= max_parts``;
    * a full non-increasing grid in the first ``min(3, max_parts)`` coordinates,
      at the requested resolution, with every further coordinate set to 0.

    Both families are feasible points of the same simplex the solver uses.
    """
    best: tuple[float, ...] = (1.0,)
    best_value = float(limit_induced_density(motif, best))
    evaluations = 1

    def consider(point: tuple[float, ...]) -> None:
        nonlocal best, best_value, evaluations
        projected = _project(point)
        value = float(limit_induced_density(motif, projected))
        evaluations += 1
        if value > best_value:
            best = projected
            best_value = value

    for parts in range(1, max_parts + 1):
        consider(tuple(1.0 / parts for _ in range(parts)))

    free = min(3, max_parts)

    def rec(remaining: int, left: float, cap: float, acc: list[float]) -> None:
        if remaining == 0:
            consider(tuple(acc))
            return
        for i in range(grid + 1):
            piece = cap * i / grid
            if piece > left + 1e-15:
                break
            rec(remaining - 1, left - piece, piece, [*acc, piece])

    rec(free, 1.0, 1.0, [])
    return best, best_value, evaluations


def _slsqp(motif: Motif, start: tuple[float, ...]) -> tuple[OptimizeResult, int]:
    dimension = len(start)
    calls = {"n": 0}

    def objective(vector: np.ndarray) -> float:
        calls["n"] += 1
        return -float(limit_induced_density(motif, _project(tuple(float(v) for v in vector))))

    constraints = {"type": "ineq", "fun": lambda vector: 1.0 - float(np.sum(vector))}
    bounds = [(0.0, 1.0)] * dimension
    result = minimize(
        objective,
        np.array(start, dtype=float),
        method="SLSQP",
        bounds=bounds,
        constraints=constraints,
        options={"maxiter": 200, "ftol": 1e-12},
    )
    return result, calls["n"]


def _project(ratios: tuple[float, ...]) -> tuple[float, ...]:
    """Sort into the ordered simplex and clip numerical noise."""
    clipped = [0.0 if r < 1e-12 else float(r) for r in ratios]
    total = sum(clipped)
    if total > 1:
        clipped = [r / total for r in clipped]
    clipped.sort(reverse=True)
    return tuple(clipped)


def _random_start(parts: int, rng: np.random.Generator) -> tuple[float, ...]:
    raw = rng.dirichlet(np.ones(parts + 1))
    return _project(tuple(float(v) for v in raw[:-1]))
