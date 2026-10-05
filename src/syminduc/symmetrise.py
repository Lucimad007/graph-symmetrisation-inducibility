"""Zykov symmetrisation on explicit graphs.

A step replaces a vertex x by a clone of a non-adjacent vertex y: x loses
its old neighbourhood and gains exactly N(y). For the number of edges this
does not decrease the objective whenever deg(x) <= deg(y), which is Zykov's
argument for Turán's theorem.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Graph:
    """Undirected simple graph on vertices 0 .. n-1."""

    n: int
    edges: set[tuple[int, int]]

    def __post_init__(self) -> None:
        if self.n < 0:
            raise ValueError("n must be non-negative")
        norm: set[tuple[int, int]] = set()
        for a, b in self.edges:
            if a == b or not (0 <= a < self.n and 0 <= b < self.n):
                raise ValueError("invalid edge")
            norm.add((a, b) if a < b else (b, a))
        self.edges = norm

    @staticmethod
    def empty(n: int) -> Graph:
        return Graph(n, set())

    @staticmethod
    def from_parts(part_sizes: tuple[int, ...]) -> Graph:
        n = sum(part_sizes)
        edges: set[tuple[int, int]] = set()
        bounds = []
        cursor = 0
        for size in part_sizes:
            bounds.append((cursor, cursor + size))
            cursor += size
        for i in range(n):
            for j in range(i + 1, n):
                same = any(lo <= i < hi and lo <= j < hi for lo, hi in bounds)
                if not same:
                    edges.add((i, j))
        return Graph(n, edges)

    def neighbours(self, v: int) -> set[int]:
        out = set()
        for a, b in self.edges:
            if a == v:
                out.add(b)
            elif b == v:
                out.add(a)
        return out

    def degree(self, v: int) -> int:
        return len(self.neighbours(v))

    def clone(self, x: int, y: int) -> Graph:
        """Return the graph in which x is a clone of y. xy stays a non-edge."""
        if x == y:
            raise ValueError("a vertex is not a clone of itself")
        ny = self.neighbours(y)
        ny.discard(x)
        edges = set()
        for a, b in self.edges:
            if a != x and b != x:
                edges.add((a, b))
        for z in ny:
            edges.add((x, z) if x < z else (z, x))
        return Graph(self.n, edges)

    def is_complete_partite(self) -> bool:
        """True when non-adjacency is an equivalence relation."""
        parent = list(range(self.n))

        def find(v: int) -> int:
            while parent[v] != v:
                parent[v] = parent[parent[v]]
                v = parent[v]
            return v

        def union(a: int, b: int) -> None:
            ra, rb = find(a), find(b)
            if ra != rb:
                parent[rb] = ra

        adj = [self.neighbours(v) for v in range(self.n)]
        for i in range(self.n):
            for j in range(i + 1, self.n):
                if j not in adj[i]:
                    union(i, j)
        for i in range(self.n):
            for j in range(i + 1, self.n):
                same = find(i) == find(j)
                linked = j in adj[i]
                if same and linked:
                    return False
                if not same and not linked:
                    return False
        return True


def symmetrise_edges(graph: Graph, max_steps: int | None = None) -> tuple[Graph, int]:
    """Symmetrise until the graph is complete partite.

    At each step, among non-adjacent pairs, clone the higher-degree vertex
    onto the lower-degree one. Returns the final graph and the number of
    clone steps. The number of edges is non-decreasing.
    """
    current = graph
    steps = 0
    limit = max_steps if max_steps is not None else graph.n * graph.n
    while steps < limit:
        pair = _next_pair(current)
        if pair is None:
            break
        x, y = pair
        current = current.clone(x, y)
        steps += 1
    return current, steps


def _next_pair(graph: Graph) -> tuple[int, int] | None:
    """A non-adjacent pair (x, y) with deg(x) <= deg(y) and N(x) != N(y)."""
    degrees = [graph.degree(v) for v in range(graph.n)]
    neigh = [graph.neighbours(v) for v in range(graph.n)]
    best: tuple[int, int, int] | None = None
    for i in range(graph.n):
        for j in range(i + 1, graph.n):
            if j in neigh[i]:
                continue
            # Prefer to overwrite the poorer vertex.
            if degrees[i] <= degrees[j]:
                x, y = i, j
            else:
                x, y = j, i
            if neigh[x] - {y} == neigh[y] - {x}:
                continue
            gap = degrees[y] - degrees[x]
            if best is None or gap > best[0]:
                best = (gap, x, y)
    if best is None:
        return None
    return best[1], best[2]
