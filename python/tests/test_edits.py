from inducibility.edits import pair_edit_drop
from inducibility.motifs import MOTIFS


def test_adding_an_edge_inside_a_part_of_k22_removes_copies():
    drop = pair_edit_drop(MOTIFS["K22"], (8, 8), 0, 0, 0)
    assert drop > 0


def test_deleting_a_cross_edge_of_k311_removes_copies():
    drop = pair_edit_drop(MOTIFS["K311"], (12,), 8, 0, -1)
    assert drop > 0
