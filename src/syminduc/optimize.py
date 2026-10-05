"""Numerical search for inducibility maximisers on the partite simplex."""

from __future__ import annotations

from dataclasses import dataclass

from syminduc.density import (
    bipartite_inducibility_from_alpha,
    bipartite_polynomial,
    limit_induced_density,
)
from syminduc.partite import PartiteVector


@dataclass(frozen=True)
class Maximiser:
    value: float
    vector: PartiteVector


def maximise_bipartite(s: int, t: int, grid: int = 4001) -> Maximiser:
    """Maximise f_{s,t} on [1/2, 1] and return the induced density at the max.

    Theorem 1.6: the unique bipartite maximiser is the alpha in [1/2, 1]
    maximising f_{s,t}, and the inducibility is C(s+t, s) * M_{s,t}.
    """
    if grid < 2:
        raise ValueError("grid must be at least 2")
    best_a = 0.5
    best_f = bipartite_polynomial(s, t, best_a)
    for i in range(grid):
        alpha = 0.5 + 0.5 * i / (grid - 1)
        value = bipartite_polynomial(s, t, alpha)
        if value > best_f:
            best_f = value
            best_a = alpha
    # Newton steps on a symmetric stencil, kept only while the point stays
    # far enough from the boundary that the stencil is valid.
    alpha = best_a
    step = 1e-5
    for _ in range(12):
        if alpha - step < 0.5 or alpha + step > 1.0:
            break
        lo, hi = alpha - step, alpha + step
        mid = bipartite_polynomial(s, t, alpha)
        left = bipartite_polynomial(s, t, lo)
        right = bipartite_polynomial(s, t, hi)
        derivative = (right - left) / (2 * step)
        second = (right - 2 * mid + left) / (step * step)
        if abs(second) < 1e-14:
            break
        alpha = min(1.0, max(0.5, alpha - derivative / second))
    if bipartite_polynomial(s, t, alpha) + 1e-15 < best_f:
        alpha = best_a
    density = bipartite_inducibility_from_alpha(s, t, alpha)
    return Maximiser(density, PartiteVector.bipartite(alpha))


def maximise_over_parts(
    target: tuple[int, ...],
    max_parts: int,
    grid: int = 25,
) -> Maximiser:
    """Grid search for the partite vector with the largest induced density.

    ``max_parts`` is the number of coordinates searched on the simplex
    x1 >= ... >= xr >= 0, sum xi <= 1. Residual mass is singleton weight.
    The search does not certify a global maximum.
    """
    if max_parts < 0:
        raise ValueError("max_parts must be non-negative")
    best = Maximiser(-1.0, PartiteVector(()))

    def consider(raw: tuple[float, ...]) -> None:
        nonlocal best
        ordered = tuple(sorted((p for p in raw if p > 1e-12), reverse=True))
        if sum(ordered) > 1 + 1e-9:
            return
        host = PartiteVector(ordered)
        value = limit_induced_density(target, host)
        if value > best.value:
            best = Maximiser(value, host)

    if max_parts == 0:
        consider(())
        return best

    def rec_parts(remaining: int, left: float, cap: float, acc: list[float]) -> None:
        if remaining == 0:
            consider(tuple(acc))
            return
        for i in range(grid + 1):
            piece = cap * i / grid
            if piece > left + 1e-15:
                break
            rec_parts(remaining - 1, left - piece, piece, [*acc, piece])

    rec_parts(max_parts, 1.0, 1.0, [])
    return best
