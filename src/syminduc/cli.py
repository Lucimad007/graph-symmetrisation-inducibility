"""Print a few inducibility numbers from the partite model."""

from __future__ import annotations

from syminduc.optimize import maximise_bipartite


def main() -> None:
    samples = [(2, 2), (3, 1), (3, 2), (4, 1), (2, 1)]
    print(f"{'F':<10}{'alpha':>12}{'density':>16}")
    for s, t in samples:
        found = maximise_bipartite(s, t)
        alpha = found.vector.parts[0] if found.vector.parts else 0.0
        name = f"K{s},{t}"
        print(f"{name:<10}{alpha:12.6f}{found.value:16.8f}")


if __name__ == "__main__":
    main()
