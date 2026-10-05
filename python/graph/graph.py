"""Simple undirected graphs.

The representation is an adjacency set for each vertex. Matrix conversion is
provided for experiments that want a dense array. Vertices are always
relabelled to ``0 .. n-1`` after a deletion so that later code can index
them directly.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np


@dataclass
class Graph:
    """Undirected simple graph on vertices ``0 .. n-1``."""

    n: int
    adj: list[set[int]] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.n < 0:
            raise ValueError("n must be non-negative")
        if not self.adj:
            self.adj = [set() for _ in range(self.n)]
        if len(self.adj) != self.n:
            raise ValueError("adjacency list length must equal n")
        for v, neigh in enumerate(self.adj):
            if v in neigh:
                raise ValueError("loops are not allowed")
            for u in neigh:
                if not 0 <= u < self.n:
                    raise ValueError("neighbour out of range")
                if v not in self.adj[u]:
                    raise ValueError("adjacency must be symmetric")

    @staticmethod
    def empty(n: int) -> Graph:
        return Graph(n)

    def copy(self) -> Graph:
        return Graph(self.n, [set(neigh) for neigh in self.adj])

    @property
    def number_of_edges(self) -> int:
        return sum(len(neigh) for neigh in self.adj) // 2

    def degree(self, v: int) -> int:
        self._check_vertex(v)
        return len(self.adj[v])

    def has_edge(self, u: int, v: int) -> bool:
        self._check_vertex(u)
        self._check_vertex(v)
        return v in self.adj[u]

    def add_edge(self, u: int, v: int) -> None:
        if u == v:
            raise ValueError("loops are not allowed")
        self._check_vertex(u)
        self._check_vertex(v)
        self.adj[u].add(v)
        self.adj[v].add(u)

    def remove_edge(self, u: int, v: int) -> None:
        self._check_vertex(u)
        self._check_vertex(v)
        self.adj[u].discard(v)
        self.adj[v].discard(u)

    def add_vertex(self) -> int:
        self.adj.append(set())
        self.n += 1
        return self.n - 1

    def remove_vertex(self, v: int) -> None:
        """Delete ``v`` and renumber the surviving vertices in increasing order."""
        self._check_vertex(v)
        new_adj: list[set[int]] = []
        for u in range(self.n):
            if u == v:
                continue
            new_adj.append({w if w < v else w - 1 for w in self.adj[u] if w != v})
        self.adj = new_adj
        self.n -= 1

    def non_adjacent_pairs(self) -> list[tuple[int, int]]:
        pairs: list[tuple[int, int]] = []
        for u in range(self.n):
            for v in range(u + 1, self.n):
                if v not in self.adj[u]:
                    pairs.append((u, v))
        return pairs

    def adjacency_matrix(self) -> np.ndarray:
        matrix = np.zeros((self.n, self.n), dtype=np.int8)
        for u, neigh in enumerate(self.adj):
            for v in neigh:
                matrix[u, v] = 1
        return matrix

    def clone_neighborhood(self, x: int, y: int) -> None:
        """Replace the neighbourhood of ``x`` by the neighbourhood of ``y``.

        This is Zykov's clone step from the first paragraph of the
        introduction: ``x`` becomes a twin of the non-adjacent vertex ``y``.
        The pair ``xy`` stays a non-edge, because ``y`` is not adjacent to
        itself and was not adjacent to ``x``.
        """
        if x == y:
            raise ValueError("a vertex is not a clone of itself")
        self._check_vertex(x)
        self._check_vertex(y)
        if y in self.adj[x]:
            raise ValueError("clone step is defined for a non-adjacent pair")
        new_neighbours = set(self.adj[y])
        new_neighbours.discard(x)
        for u in list(self.adj[x]):
            self.adj[u].discard(x)
        self.adj[x] = new_neighbours
        for u in new_neighbours:
            self.adj[u].add(x)

    def _check_vertex(self, v: int) -> None:
        if not 0 <= v < self.n:
            raise ValueError(f"vertex {v} is not in 0..{self.n - 1}")
