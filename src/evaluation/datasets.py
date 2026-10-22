"""Named evaluation datasets: case file + frozen label file."""

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

from src.config.paths import (
    COUNTERFACTUAL_CASES_FILE,
    COUNTERFACTUAL_LABELS_FILE,
    HELDOUT_CASES_FILE,
    HELDOUT_GROUND_TRUTH_FILE,
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
    "heldout": {
        "label": "Held-out (34 blind-labelled cases)",
        "cases": HELDOUT_CASES_FILE,
        "labels": HELDOUT_GROUND_TRUTH_FILE,
        "note": "New disputes written after the rules engine was frozen (tag rules-engine-frozen-v1). "
                "Labels come from two blind annotators plus third-person adjudication; available "
                "only once data/labeled/heldout/heldout_ground_truth.json is finalised.",
    },
}


def _load(path: Path) -> List[Dict[str, Any]]:
    with Path(path).open("r", encoding="utf-8") as file:
        return json.load(file)


def available_datasets() -> List[str]:
    """Datasets that can be scored: both the cases and the final labels exist."""
    return [name for name, spec in DATASETS.items()
            if Path(spec["cases"]).exists() and Path(spec["labels"]).exists()]


def load_cases(name: str) -> List[Dict[str, Any]]:
    """Cases only — for labelling tools, which must work before labels exist."""
    if name not in DATASETS:
        raise KeyError(f"unknown dataset '{name}'; known: {sorted(DATASETS)}")
    return _load(DATASETS[name]["cases"])


def load_dataset(name: str) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Cases and labels. Refuses a dataset whose labels are not final, so no model is run
    on held-out cases before the reference labels are fixed (GROUND_TRUTH_SCHEMA.md)."""
    cases = load_cases(name)
    labels_file = Path(DATASETS[name]["labels"])
    if not labels_file.exists():
        raise FileNotFoundError(
            f"dataset '{name}' has no final labels yet ({labels_file}). Finish annotation first: "
            "python -m src.validation.heldout_labels compare / finalize")
    return cases, _load(labels_file)
