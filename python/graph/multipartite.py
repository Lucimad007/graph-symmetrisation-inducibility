"""Complete multipartite graphs and a candidate edit distance.

Definition 1.3 realises a vector ``x in P`` by large parts of relative size
``x_i`` and, when ``sum x_i < 1``, a pool of singleton parts of total mass
``x_0``. Singleton parts are pairwise adjacent.

The defect used in experiments is not the minimum of ``hat Delta_1(G, H)``
over all complete partite ``H`` (Definition 1.2). Computing that minimum is
a search over partitions. The candidate used here takes the connected
components of the *non-edge* graph as parts, then counts pairs that violate
the complete partite rule for that partition:

* an edge inside a component, or
* a non-edge between different components.

Those pairs are exactly the edits that turn ``G`` into the complete
multipartite graph with those parts. The returned fraction is that edit
count divided by ``binom(n, 2)``.
"""

from __future__ import annotations

from math import comb

from graph.graph import Graph


def complete_multipartite(part_sizes: tuple[int, ...], singletons: int = 0) -> Graph:
    """Complete multipartite graph with the given part sizes.

    ``singletons`` adds that many parts of size 1. Parts of size 0 are ignored.
    """
    sizes = [int(s) for s in part_sizes if int(s) > 0]
    if singletons < 0 or any(s < 0 for s in part_sizes):
        raise ValueError("part sizes must be non-negative")
    sizes.extend([1] * singletons)
    n = sum(sizes)
    graph = Graph.empty(n)
    bounds: list[tuple[int, int]] = []
    cursor = 0
    for size in sizes:
        bounds.append((cursor, cursor + size))
        cursor += size
    for u in range(n):
        for v in range(u + 1, n):
            same = any(lo <= u < hi and lo <= v < hi for lo, hi in bounds)
            if not same:
                graph.add_edge(u, v)
    return graph


def realise(n: int, ratios: tuple[float, ...]) -> tuple[int, tuple[int, ...]]:
    """Integer realisation of a ratio vector, in the sense of Definition 1.3.

    ``ratios`` is ``(x_1, x_2, ...)`` with non-increasing non-negative entries
    summing to at most 1. Returns ``(singletons, large_part_sizes)``.
    When the residual mass is 0, part sizes are the largest-remainder rounding
    of ``x_i n`` and there is no singleton pool. When the residual mass is
    positive, each part with ``x_i n >= 2`` gets ``floor(x_i n)`` vertices and
    the rest of ``[n]`` becomes singleton parts.
    """
    if n < 1:
        raise ValueError("n must be positive")
    if any(r < -1e-12 for r in ratios):
        raise ValueError("ratios must be non-negative")
    if any(ratios[i] + 1e-12 < ratios[i + 1] for i in range(len(ratios) - 1)):
        raise ValueError("ratios must be non-increasing")
    total = float(sum(ratios))
    if total > 1 + 1e-9:
        raise ValueError("ratios sum to more than 1")
    residual = 1.0 - total
    positive = [r for r in ratios if r > 1e-15]
    if residual <= 1e-12:
        if not positive:
            return n, ()
        floors = [int(r * n) for r in positive]
        deficit = n - sum(floors)
        order = sorted(
            ((r * n - int(r * n), i) for i, r in enumerate(positive)),
            reverse=True,
        )
        for k in range(deficit):
            floors[order[k % len(floors)][1]] += 1
        sizes = tuple(sorted((s for s in floors if s > 0), reverse=True))
        return 0, sizes
    large = [int(r * n) for r in positive if r * n >= 2]
    singletons = n - sum(large)
    if singletons < 0:
        raise ValueError("realisation overflowed n")
    return singletons, tuple(sorted((s for s in large if s > 0), reverse=True))


def part_ratios(graph: Graph) -> tuple[float, ...] | None:
    """Part ratios if ``graph`` is complete multipartite, otherwise ``None``.

    The first entries are the large parts in non-increasing order. A tail of
    singleton parts is reported as residual mass only through omission: the
    returned tuple sums to ``1 - s/n`` when there are ``s`` singleton parts,
    matching ``x_0`` in the paper. If every part has size at least 2, the
    tuple sums to 1.
    """
    if graph.n == 0:
        return ()
    parts = _nonedge_components(graph)
    if not _respects(graph, parts):
        return None
    sizes = sorted((len(part) for part in parts if len(part) >= 2), reverse=True)
    return tuple(size / graph.n for size in sizes)


def multipartite_defect(graph: Graph) -> float:
    """Fraction of pairs that violate the candidate complete partite graph.

    See the module docstring. The value lies in ``[0, 1]`` and is 0 precisely
    when ``graph`` is complete multipartite.
    """
    if graph.n < 2:
        return 0.0
    parts = _nonedge_components(graph)
    edits = 0
    index = [-1] * graph.n
    for label, part in enumerate(parts):
        for v in part:
            index[v] = label
    for u in range(graph.n):
        for v in range(u + 1, graph.n):
            same = index[u] == index[v]
            linked = graph.has_edge(u, v)
            if same == linked:
                edits += 1
    return edits / comb(graph.n, 2)


def _nonedge_components(graph: Graph) -> list[list[int]]:
    parent = list(range(graph.n))

    def find(v: int) -> int:
        while parent[v] != v:
            parent[v] = parent[parent[v]]
            v = parent[v]
        return v

    def union(a: int, b: int) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    for u, v in graph.non_adjacent_pairs():
        union(u, v)
    groups: dict[int, list[int]] = {}
    for v in range(graph.n):
        groups.setdefault(find(v), []).append(v)
    return list(groups.values())


def _respects(graph: Graph, parts: list[list[int]]) -> bool:
    index = [-1] * graph.n
    for label, part in enumerate(parts):
        for v in part:
            index[v] = label
    for u in range(graph.n):
        for v in range(u + 1, graph.n):
            same = index[u] == index[v]
            linked = graph.has_edge(u, v)
            if same == linked:
                return False
    return True
