"""Run the reproducibility suite: Section 6, symmetrisation, stability scan."""

from __future__ import annotations

from experiments.near_extremal import run as run_near
from experiments.section6 import run as run_section6
from experiments.stability_scan import run as run_scan
from experiments.symmetrisation_run import run as run_symmetrisation


def main() -> None:
    section6 = run_section6()
    symmetrisation = run_symmetrisation()
    scan = run_scan()
    near = run_near()
    print("section6 absolute errors:")
    for row in section6["rows"]:
        print(" ", row["theorem"], row["absolute_error"])
    print("symmetrisation trajectories:", len(symmetrisation["trajectories"]))
    print("stability rows:", len(scan["rows"]))
    print("near-extremal rows:", len(near["rows"]))
    for item in near["one_edge"]:
        print(" ", item["motif"], "inside", item["copies_lost_adding_an_edge_inside_the_largest_part"], "cross", item["copies_lost_deleting_a_cross_edge"])


if __name__ == "__main__":
    main()
