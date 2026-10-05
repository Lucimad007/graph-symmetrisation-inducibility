"""Partite limit space P and finite realisations Gn,x (Definition 1.3)."""

from __future__ import annotations

from dataclasses import dataclass
from math import comb


@dataclass(frozen=True)
class PartiteVector:
    """A point x in the partite limit space.

    Coordinates ``parts`` are x1 >= x2 >= ... >= 0. The residual mass
    ``x0 = 1 - sum(parts)`` is the total weight of singleton parts
    (a clique of universal vertices in the realisation).
    """

    parts: tuple[float, ...]

    def __post_init__(self) -> None:
        if any(p < -1e-12 for p in self.parts):
            raise ValueError("part masses must be non-negative")
        if any(self.parts[i] + 1e-12 < self.parts[i + 1] for i in range(len(self.parts) - 1)):
            raise ValueError("parts must be nonincreasing")
        if sum(self.parts) > 1 + 1e-9:
            raise ValueError("part masses sum to more than 1")

    @property
    def x0(self) -> float:
        return 1.0 - sum(self.parts)

    @staticmethod
    def balanced(r: int) -> PartiteVector:
        if r < 1:
            raise ValueError("r must be positive")
        return PartiteVector(tuple(1.0 / r for _ in range(r)))

    @staticmethod
    def bipartite(alpha: float) -> PartiteVector:
        if not 0 <= alpha <= 1:
            raise ValueError("alpha must lie in [0, 1]")
        a, b = (alpha, 1 - alpha) if alpha >= 1 - alpha else (1 - alpha, alpha)
        parts = tuple(p for p in (a, b) if p > 0)
        return PartiteVector(parts)


def realise(n: int, x: PartiteVector) -> tuple[int, ...]:
    """Part sizes of the n-vertex realisation Gn,x.

    Returns ``(s, n1, n2, ...)`` where ``s = |V0|`` is the number of
    singleton parts and ``ni = |Vi|``.
    """
    if n < 1:
        raise ValueError("n must be positive")
    x0 = x.x0
    if x0 <= 1e-15:
        sizes = [int(xi * n) for xi in x.parts]
        # Largest-remainder method so the sizes sum to n.
        deficit = n - sum(sizes)
        fractional = sorted(
            ((xi * n - int(xi * n), i) for i, xi in enumerate(x.parts)),
            reverse=True,
        )
        for k in range(deficit):
            sizes[fractional[k % len(sizes)][1]] += 1
        sizes = [s for s in sizes if s > 0]
        sizes.sort(reverse=True)
        return (0, *sizes)

    large: list[int] = []
    for xi in x.parts:
        if xi * n >= 2:
            large.append(int(xi * n))  # floor
    used = sum(large)
    singletons = n - used
    if singletons < 0:
        raise ValueError("realisation overflowed n")
    large = [s for s in large if s > 0]
    large.sort(reverse=True)
    return (singletons, *large)


def complete_partite_edges(part_sizes: tuple[int, ...], singletons: int = 0) -> int:
    """Number of edges in a complete partite graph with the given parts."""
    n = sum(part_sizes) + singletons
    inside = sum(comb(s, 2) for s in part_sizes)
    return comb(n, 2) - inside
