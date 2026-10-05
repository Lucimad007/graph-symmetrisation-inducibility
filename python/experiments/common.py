"""Paths and JSON helpers shared by the experiment scripts."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "experiments" / "results"
FIGURES = ROOT / "experiments" / "figures"


def write_json(name: str, payload: dict) -> Path:
    RESULTS.mkdir(parents=True, exist_ok=True)
    path = RESULTS / name
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path
