"""Named evaluation datasets: case file + frozen label file."""

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

from src.config.paths import (
    COUNTERFACTUAL_CASES_FILE,
    COUNTERFACTUAL_LABELS_FILE,
    PILOT_CASES_FILE,
    PILOT_GROUND_TRUTH_FILE,
)

DATASETS: Dict[str, Dict[str, Any]] = {
    "pilot": {
        "label": "Pilot (10 hand-built cases)",
        "cases": PILOT_CASES_FILE,
        "labels": PILOT_GROUND_TRUTH_FILE,
        "note": "Hand-labelled reference set. The rules engine and fact triggers were "
                "written with these cases visible, so scores on it are in-sample.",
    },
    "counterfactual": {
        "label": "Counterfactual stress set",
        "cases": COUNTERFACTUAL_CASES_FILE,
        "labels": COUNTERFACTUAL_LABELS_FILE,
        "note": "Pilot cases with one SLA-relevant fact changed (timing, PoD state, amounts, "
                "evidence). Labels follow from the edited fact by an explicit, documented rule "
                "per perturbation — not from the rules engine.",
    },
}


def _load(path: Path) -> List[Dict[str, Any]]:
    with Path(path).open("r", encoding="utf-8") as file:
        return json.load(file)


def available_datasets() -> List[str]:
    return [name for name, spec in DATASETS.items() if Path(spec["cases"]).exists()]


def load_dataset(name: str) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    if name not in DATASETS:
        raise KeyError(f"unknown dataset '{name}'; known: {sorted(DATASETS)}")
    spec = DATASETS[name]
    return _load(spec["cases"]), _load(spec["labels"])
