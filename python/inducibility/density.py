"""Exact and approximate induced densities.

``p(F, G)`` is the fraction of ``k``-subsets that induce a graph isomorphic
to ``F`` (Section 1.2). For a complete partite ``F`` this is decided by the
part sizes of the induced subgraph.

``limit_induced_density`` is the graphon limit ``lim p(F, G_{n,x})`` when the
host is complete partite with part masses ``ratios`` and singleton mass
``1 - sum(ratios)``. It expands the multinomial distribution of ``k`` i.i.d.
samples. That expansion is exact arithmetic in floating point; it is not a
Monte Carlo estimate.

``sample_induced_density`` draws ``k``-subsets uniformly. Its return value is
an estimate and must be reported as one.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from math import comb

import numpy as np

from graph.graph import Graph
from inducibility.motifs import Motif


@dataclass(frozen=True)
class SampleEstimate:
    """Monte Carlo estimate of an induced density. Not an exact value."""

    estimate: float
    samples: int
    standard_error: float
    method: str = "uniform k-subset sampling"


def exact_induced_count(graph: Graph, motif: Motif) -> int:
    """Number of induced copies of ``motif`` in ``graph``."""
    k = motif.order
    if graph.n < k:
        return 0
    count = 0
    for subset in _combinations(range(graph.n), k):
        if _induced_parts(graph, subset) == motif.parts:
            count += 1
    return count


def exact_induced_density(graph: Graph, motif: Motif) -> float:
    k = motif.order
    if graph.n < k:
        return 0.0
    return exact_induced_count(graph, motif) / comb(graph.n, k)


def sample_induced_density(graph: Graph, motif: Motif, samples: int, rng: np.random.Generator) -> SampleEstimate:
    """Approximate ``p(F, G)`` by sampling ``k``-subsets without replacement inside each draw.

    The sample standard error is ``sqrt(p_hat (1 - p_hat) / samples)``, the
    usual binomial error. It is not a confidence interval.
    """
    if samples < 1:
        raise ValueError("samples must be positive")
    k = motif.order
    if graph.n < k:
        return SampleEstimate(0.0, samples, 0.0)
    hits = 0
    vertices = np.arange(graph.n)
    for _ in range(samples):
        subset = tuple(int(v) for v in rng.choice(vertices, size=k, replace=False))
        if _induced_parts(graph, subset) == motif.parts:
            hits += 1
    estimate = hits / samples
    standard_error = float(np.sqrt(estimate * (1.0 - estimate) / samples))
    return SampleEstimate(estimate, samples, standard_error)


def limit_induced_density(motif: Motif, ratios: tuple[float, ...]) -> float:
    """Limit induced density of ``motif`` in the complete partite graphon of ``ratios``.

    ``ratios`` lists the masses of the non-singleton parts. Residual mass
    ``1 - sum(ratios)`` is a pool of singleton parts (Definition 1.3).
    """
    if any(r < -1e-12 for r in ratios):
        raise ValueError("ratios must be non-negative")
    total = float(sum(ratios))
    if total > 1 + 1e-8:
        raise ValueError("ratios sum to more than 1")
    masses = [float(r) for r in ratios if r > 1e-15]
    x0 = max(0.0, 1.0 - sum(masses))
    k = motif.order
    target = motif.parts
    accumulated = 0.0
    for counts in _compositions(k, len(masses) + 1):
        if _type_from_occupancy(counts[:-1], counts[-1]) != target:
            continue
        accumulated += _multinomial(counts, masses, x0)
    return accumulated


def combinatorial_count_in_host(
    motif: Motif,
    part_sizes: tuple[int, ...],
    singletons: int = 0,
) -> int:
    """Exact induced-copy count when the host itself is complete multipartite.

    This is the closed count behind ``limit_induced_density``, evaluated at
    integer part sizes. It is exact, and it is only valid for a complete
    multipartite host with those parts.
    """
    sizes = [int(s) for s in part_sizes if int(s) > 0]
    if singletons < 0 or any(s < 1 for s in sizes):
        raise ValueError("part sizes must be positive")
    k = motif.order
    total = 0
    for counts in _compositions(k, len(sizes) + 1):
        taken, s_take = counts[:-1], counts[-1]
        if s_take > singletons or any(c > n_i for c, n_i in zip(taken, sizes)):
            continue
        if _type_from_occupancy(taken, s_take) != motif.parts:
            continue
        ways = comb(singletons, s_take)
        for c, n_i in zip(taken, sizes):
            ways *= comb(n_i, c)
        total += ways
    return total


def _induced_parts(graph: Graph, vertices: tuple[int, ...]) -> tuple[int, ...]:
    """Part sizes of ``graph[vertices]`` when it is complete multipartite.

    Non-adjacency is joined by union-find. The induced subgraph is complete
    multipartite exactly when each part is an independent set and every cross
    pair is an edge. Otherwise the returned marker ``()`` matches no motif.
    """
    index = {v: i for i, v in enumerate(vertices)}
    parent = list(range(len(vertices)))

    def find(i: int) -> int:
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def union(a: int, b: int) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    for a in vertices:
        for b in vertices:
            if a < b and b not in graph.adj[a]:
                union(index[a], index[b])
    for a in vertices:
        for b in vertices:
            if a >= b:
                continue
            same = find(index[a]) == find(index[b])
            linked = b in graph.adj[a]
            if same == linked:
                return ()
    sizes: dict[int, int] = {}
    for i in range(len(vertices)):
        root = find(i)
        sizes[root] = sizes.get(root, 0) + 1
    return tuple(sorted(sizes.values(), reverse=True))


def _type_from_occupancy(body: tuple[int, ...] | list[int], singletons: int) -> tuple[int, ...]:
    chunks = [c for c in body if c > 0]
    chunks.extend([1] * singletons)
    chunks.sort(reverse=True)
    return tuple(chunks)


def _multinomial(counts: tuple[int, ...], masses: list[float], x0: float) -> float:
    k = sum(counts)
    coeff = _factorial(k)
    prob = 1.0
    for c, mass in zip(counts[:-1], masses):
        coeff //= _factorial(c)
        prob *= mass**c
    coeff //= _factorial(counts[-1])
    prob *= x0 ** counts[-1]
    return coeff * prob


def _compositions(total: int, bins: int):
    if bins < 1:
        raise ValueError("need at least one bin")
    if bins == 1:
        yield (total,)
        return
    for c in range(total + 1):
        for rest in _compositions(total - c, bins - 1):
            yield (c, *rest)


def _combinations(items, k: int):
    pool = tuple(items)
    if k == 0:
        yield ()
        return
    for i in range(len(pool)):
        for tail in _combinations(pool[i + 1 :], k - 1):
            yield (pool[i], *tail)


@lru_cache(maxsize=None)
def _factorial(n: int) -> int:
    out = 1
    for i in range(2, n + 1):
        out *= i
    return out
