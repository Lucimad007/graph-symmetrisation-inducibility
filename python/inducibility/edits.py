"""Change in the induced-copy count when one pair of a complete partite host is toggled.

This is the finite form of condition (i) in Theorem 1.4: on an extremal
complete partite graph, editing one pair should destroy induced copies.
The count is exact for a complete multipartite host. It is not a proof of
the Omega(n^{-2}) inequality.
"""

from __future__ import annotations

from math import comb

from inducibility.motifs import Motif


def pair_edit_drop(
    motif: Motif,
    part_sizes: tuple[int, ...],
    singletons: int,
    slot_a: int,
    slot_b: int,
) -> int:
    """Return Lambda(G) - Lambda(G with the pair toggled).

    Slots ``0 .. m-1`` are the large parts. Slot ``-1`` is the singleton pool.
    A positive value means the edit removes more induced copies than it creates.
    """
    sizes = [int(s) for s in part_sizes if int(s) > 0]
    singletons = int(singletons)
    k = motif.order
    original = 0
    edited = 0
    for counts in _compositions(k - 2, len(sizes) + 1):
        taken = list(counts[:-1])
        s_take = counts[-1]
        if not _fits(taken, s_take, sizes, singletons, slot_a, slot_b):
            continue
        ways = _ways(taken, s_take, sizes, singletons, slot_a, slot_b)
        before = _type(taken, s_take, slot_a, slot_b, edited=False)
        after = _type(taken, s_take, slot_a, slot_b, edited=True)
        if before == motif.parts:
            original += ways
        if after == motif.parts:
            edited += ways
    return original - edited


def _fits(taken, s_take, sizes, singletons, slot_a, slot_b) -> bool:
    if s_take + (slot_a == -1) + (slot_b == -1) > singletons:
        return False
    return all(taken[i] + (slot_a == i) + (slot_b == i) <= n_i for i, n_i in enumerate(sizes))


def _ways(taken, s_take, sizes, singletons, slot_a, slot_b) -> int:
    ways = comb(singletons - (slot_a == -1) - (slot_b == -1), s_take)
    for i, n_i in enumerate(sizes):
        ways *= comb(n_i - (slot_a == i) - (slot_b == i), taken[i])
    return ways


def _type(taken, s_take, slot_a, slot_b, edited: bool):
    same = slot_a == slot_b
    if not edited:
        body = list(taken)
        extra = 0
        if same and slot_a == -1:
            extra = 2
        elif same:
            body[slot_a] += 2
        else:
            for slot in (slot_a, slot_b):
                if slot == -1:
                    extra += 1
                else:
                    body[slot] += 1
        return _parts(body, s_take + extra)
    if same:
        if slot_a >= 0 and taken[slot_a] != 0:
            return None
        return _parts(taken, s_take + 2)
    if slot_a != -1 or slot_b != -1:
        return None
    chunks = [c for c in taken if c > 0]
    chunks.append(2)
    chunks.extend([1] * s_take)
    chunks.sort(reverse=True)
    return tuple(chunks)


def _parts(body, singletons: int):
    chunks = [c for c in body if c > 0]
    chunks.extend([1] * singletons)
    chunks.sort(reverse=True)
    return tuple(chunks)


def _compositions(total: int, bins: int):
    if bins == 1:
        yield (total,)
        return
    for c in range(total + 1):
        for rest in _compositions(total - c, bins - 1):
            yield (c, *rest)
