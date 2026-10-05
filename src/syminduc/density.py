"""Induced densities of complete partite graphs in complete partite hosts.

The limit density is the probability that k i.i.d. samples from the partite
graphon induce a graph isomorphic to the target. That is the limit of
p(F, Gn,x).
"""

from __future__ import annotations

from functools import lru_cache
from math import comb

from syminduc.partite import PartiteVector


def _as_parts(target: tuple[int, ...]) -> tuple[int, ...]:
    parts = tuple(sorted((int(p) for p in target if int(p) > 0), reverse=True))
    if not parts:
        raise ValueError("target must have at least one vertex")
    return parts


def bipartite_polynomial(s: int, t: int, alpha: float) -> float:
    """f_{s,t}(alpha) = alpha^s (1-alpha)^t + alpha^t (1-alpha)^s."""
    if s < 1 or t < 1:
        raise ValueError("s and t must be positive")
    a = float(alpha)
    one = 1.0 - a
    return (a**s) * (one**t) + (a**t) * (one**s)


def bipartite_inducibility_from_alpha(s: int, t: int, alpha: float) -> float:
    """Induced density attached to f_{s,t} by Theorem 1.6.

    When s = t the two summands of f are the same split, so M_{s,s} uses a
    factor 1/2. When s ≠ t each summand is a distinct assignment.
    """
    factor = 0.5 if s == t else 1.0
    return comb(s + t, s) * factor * bipartite_polynomial(s, t, alpha)


def limit_induced_density(target: tuple[int, ...], host: PartiteVector) -> float:
    """Asymptotic induced density of a complete partite graph in host x."""
    parts = _as_parts(target)
    k = sum(parts)
    masses = [m for m in host.parts if m > 1e-15]
    x0 = max(0.0, host.x0)
    total = 0.0
    for counts in _compositions(k, len(masses) + 1):
        if _induced_type(counts[:-1], counts[-1]) != parts:
            continue
        total += _multinomial_prob(counts, masses, x0)
    return total


def finite_induced_count(
    target: tuple[int, ...],
    part_sizes: tuple[int, ...],
    singletons: int = 0,
) -> int:
    """Number of induced copies of the target in a finite complete partite graph."""
    parts = _as_parts(target)
    k = sum(parts)
    sizes = tuple(int(s) for s in part_sizes if int(s) > 0)
    singletons = int(singletons)
    if singletons < 0 or any(s < 1 for s in sizes):
        raise ValueError("part sizes must be positive")
    total = 0
    for counts in _compositions(k, len(sizes) + 1):
        taken = counts[:-1]
        s_take = counts[-1]
        if s_take > singletons or any(c > n_i for c, n_i in zip(taken, sizes)):
            continue
        if _induced_type(taken, s_take) != parts:
            continue
        ways = comb(singletons, s_take)
        for c, n_i in zip(taken, sizes):
            ways *= comb(n_i, c)
        total += ways
    return total


def finite_induced_density(
    target: tuple[int, ...],
    part_sizes: tuple[int, ...],
    singletons: int = 0,
) -> float:
    parts = _as_parts(target)
    n = sum(int(s) for s in part_sizes) + int(singletons)
    k = sum(parts)
    if n < k:
        return 0.0
    return finite_induced_count(target, part_sizes, singletons) / comb(n, k)


def pair_edit_drop(
    target: tuple[int, ...],
    part_sizes: tuple[int, ...],
    singletons: int,
    slot_a: int,
    slot_b: int,
) -> int:
    """How many induced copies disappear when one pair is toggled.

    Slots ``0 .. m-1`` are the large parts and slot ``-1`` is the singleton
    pool. The two endpoints are distinct vertices of those slots. The return
    value is Λ(G) - Λ(G ⊕ xy). Positive means the edit hurts the objective.

    A one-edge edit of a complete partite graph stays complete partite only
    in two situations that can still realise a complete partite target:

    * adding an edge inside a part, and the k-set meets that part in exactly
      those two vertices (the part splits into two singletons);
    * deleting an edge between two singleton vertices (they merge into a
      part of size 2).

    Every other k-set that contains the edited pair induces a non-complete
    partite graph afterwards, so it contributes only on the original side.
    """
    parts = _as_parts(target)
    k = sum(parts)
    sizes = [int(s) for s in part_sizes if int(s) > 0]
    singletons = int(singletons)
    _check_slot(slot_a, sizes, singletons)
    _check_slot(slot_b, sizes, singletons)
    if slot_a == slot_b == -1 and singletons < 2:
        raise ValueError("need two distinct singleton vertices")
    if slot_a == slot_b and slot_a >= 0 and sizes[slot_a] < 2:
        raise ValueError("need two distinct vertices in that part")

    original = 0
    edited = 0
    # Occupancy of the other k-2 vertices.
    for counts in _compositions(k - 2, len(sizes) + 1):
        taken = list(counts[:-1])
        s_take = counts[-1]
        if not _fits(taken, s_take, sizes, singletons, slot_a, slot_b):
            continue
        ways = _ways(taken, s_take, sizes, singletons, slot_a, slot_b)
        if ways == 0:
            continue
        before = _type_with_pair(taken, s_take, slot_a, slot_b, edited=False)
        after = _type_with_pair(taken, s_take, slot_a, slot_b, edited=True)
        if before == parts:
            original += ways
        if after == parts:
            edited += ways
    return original - edited


def _check_slot(slot: int, sizes: list[int], singletons: int) -> None:
    if slot == -1:
        if singletons < 1:
            raise ValueError("no singleton vertex")
        return
    if slot < 0 or slot >= len(sizes):
        raise ValueError("part slot out of range")


def _fits(
    taken: list[int],
    s_take: int,
    sizes: list[int],
    singletons: int,
    slot_a: int,
    slot_b: int,
) -> bool:
    need_s = s_take + (slot_a == -1) + (slot_b == -1)
    if need_s > singletons:
        return False
    for i, n_i in enumerate(sizes):
        extra = (slot_a == i) + (slot_b == i)
        if taken[i] + extra > n_i:
            return False
    return True


def _ways(
    taken: list[int],
    s_take: int,
    sizes: list[int],
    singletons: int,
    slot_a: int,
    slot_b: int,
) -> int:
    ways = 1
    for i, n_i in enumerate(sizes):
        extra = (slot_a == i) + (slot_b == i)
        ways *= comb(n_i - extra, taken[i])
    used_s = (slot_a == -1) + (slot_b == -1)
    ways *= comb(singletons - used_s, s_take)
    return ways


def _type_with_pair(
    taken: list[int],
    s_take: int,
    slot_a: int,
    slot_b: int,
    edited: bool,
) -> tuple[int, ...] | None:
    """Return the induced part type, or None if the graph is not complete partite."""
    same_slot = slot_a == slot_b
    if not edited:
        if same_slot and slot_a == -1:
            # Two distinct singleton parts.
            return _induced_type(taken, s_take + 2)
        if same_slot:
            body = list(taken)
            body[slot_a] += 2
            return _induced_type(body, s_take + (0 if slot_a >= 0 else 0))
        body = list(taken)
        extra_singletons = 0
        if slot_a == -1:
            extra_singletons += 1
        else:
            body[slot_a] += 1
        if slot_b == -1:
            extra_singletons += 1
        else:
            body[slot_b] += 1
        return _induced_type(body, s_take + extra_singletons)

    # Edited graph.
    if same_slot:
        # Added an edge inside a part. Stays complete partite precisely when
        # that part contributes no further vertex, in which case the two
        # endpoints become singleton parts.
        if slot_a >= 0 and taken[slot_a] != 0:
            return None
        return _induced_type(taken, s_take + 2)
    # Deleted a cross edge. Stays complete partite precisely when both
    # endpoints are singletons (their parts have size 1), and then they
    # merge into one part of size 2.
    if slot_a != -1 or slot_b != -1:
        return None
    chunks = [c for c in taken if c > 0]
    chunks.append(2)
    chunks.extend([1] * s_take)
    chunks.sort(reverse=True)
    return tuple(chunks)


def _induced_type(body: tuple[int, ...] | list[int], singletons: int) -> tuple[int, ...]:
    chunks = [c for c in body if c > 0]
    chunks.extend([1] * singletons)
    chunks.sort(reverse=True)
    return tuple(chunks)


def _multinomial_prob(counts: tuple[int, ...], masses: list[float], x0: float) -> float:
    k = sum(counts)
    coeff = _factorial(k)
    prob = 1.0
    for c, mass in zip(counts[:-1], masses):
        coeff //= _factorial(c)
        prob *= mass**c
    s_take = counts[-1]
    coeff //= _factorial(s_take)
    prob *= x0**s_take
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


@lru_cache(maxsize=None)
def _factorial(n: int) -> int:
    out = 1
    for i in range(2, n + 1):
        out *= i
    return out
