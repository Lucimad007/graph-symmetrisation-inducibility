"""Complete partite motifs named in Section 1.2 and Section 6.

A motif is the complete multipartite graph with the given part sizes, up to
isomorphism. Part sizes are stored non-increasing. Adding a motif is a new
entry in ``MOTIFS``; the counters do not special-case the names.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Motif:
    name: str
    parts: tuple[int, ...]
    paper_ref: str

    def __post_init__(self) -> None:
        if not self.parts or any(p < 1 for p in self.parts):
            raise ValueError("part sizes must be positive")
        ordered = tuple(sorted(self.parts, reverse=True))
        if ordered != self.parts:
            raise ValueError("part sizes must be non-increasing")

    @property
    def order(self) -> int:
        return sum(self.parts)


MOTIFS: dict[str, Motif] = {
    "K22": Motif("K22", (2, 2), "C4 = K_{2,2}; introduction and Theorem 1.6"),
    "K32": Motif("K32", (3, 2), "Theorem 1.6, the case (s, t) = (3, 2)"),
    "K311": Motif("K311", (3, 1, 1), "Theorem 1.9"),
    "K2111": Motif("K2111", (2, 1, 1, 1), "Theorem 1.8"),
}
