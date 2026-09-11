import json
import re
from pathlib import Path


from src.config.paths import (  # noqa: E402
    PILOT_CASES_FILE,
    PILOT_GROUND_TRUTH_FILE,
    ROOT,
    SLA_FILE,
)

RAW_CASES_FILE = PILOT_CASES_FILE
GROUND_TRUTH_FILE = PILOT_GROUND_TRUTH_FILE


VALID_DISPUTE_TYPES = {
    "DAMAGED_GOODS",
    "COD_MISMATCH",
}

VALID_DECISIONS = {
    "APPROVE",
    "REJECT",
    "ESCALATE",
}


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def extract_sla_clause_ids():
    text = SLA_FILE.read_text(encoding="utf-8")

    return set(
        re.findall(
            r"\bSLA-(?:GEN|DEF|DG|COD|PRI)-\d{2}\b",
            text,
        )
    )


def collect_case_evidence_ids(case):
    evidence_ids = set()

    for section in (
        "customer_evidence",
        "agent_evidence",
        "delivery_evidence",
    ):
        for evidence in case.get(section, []):
            evidence_id = evidence.get("evidence_id")

            if evidence_id:
                evidence_ids.add(evidence_id)

    return evidence_ids


def validate():
    errors = []

    # ---------------------------------------------------------
    # 1. Check required files
    # ---------------------------------------------------------

    for path in (
        RAW_CASES_FILE,
        GROUND_TRUTH_FILE,
        SLA_FILE,
    ):
        if not path.exists():
            errors.append(f"Missing required file: {path}")

    if errors:
        return errors

    # ---------------------------------------------------------
    # 2. Load data
    # ---------------------------------------------------------

    try:
        raw_cases = load_json(RAW_CASES_FILE)
    except Exception as exc:
        return [f"Could not load raw cases: {exc}"]

    try:
        ground_truth = load_json(GROUND_TRUTH_FILE)
    except Exception as exc:
        return [f"Could not load ground truth: {exc}"]

    # ---------------------------------------------------------
    # 3. Basic structure
    # ---------------------------------------------------------

    if not isinstance(raw_cases, list):
        errors.append("pilot_cases.json must contain a JSON list.")

    if not isinstance(ground_truth, list):
        errors.append("pilot_ground_truth.json must contain a JSON list.")

    if errors:
        return errors

    # ---------------------------------------------------------
    # 4. Case count
    # ---------------------------------------------------------

    if len(raw_cases) != 10:
        errors.append(
            f"Expected exactly 10 raw cases, found {len(raw_cases)}."
        )

    if len(ground_truth) != 10:
        errors.append(
            f"Expected exactly 10 ground-truth records, found {len(ground_truth)}."
        )

    # ---------------------------------------------------------
    # 5. Duplicate IDs
    # ---------------------------------------------------------

    raw_ids = [case.get("case_id") for case in raw_cases]
    gt_ids = [label.get("case_id") for label in ground_truth]

    duplicate_raw_ids = {
        case_id
        for case_id in raw_ids
        if case_id is not None and raw_ids.count(case_id) > 1
    }

    duplicate_gt_ids = {
        case_id
        for case_id in gt_ids
        if case_id is not None and gt_ids.count(case_id) > 1
    }

    if duplicate_raw_ids:
        errors.append(
            f"Duplicate raw case IDs: {sorted(duplicate_raw_ids)}"
        )

    if duplicate_gt_ids:
        errors.append(
            f"Duplicate ground-truth case IDs: {sorted(duplicate_gt_ids)}"
        )

    # ---------------------------------------------------------
    # 6. Raw case validation
    # ---------------------------------------------------------

    raw_case_map = {}

    for case in raw_cases:
        case_id = case.get("case_id")

        if not case_id:
            errors.append("Raw case is missing case_id.")
            continue

        raw_case_map[case_id] = case

        dispute_type = case.get("dispute_type")

        if dispute_type not in VALID_DISPUTE_TYPES:
            errors.append(
                f"{case_id}: invalid dispute_type '{dispute_type}'."
            )

        if "ground_truth" in case:
            errors.append(
                f"{case_id}: ground_truth leaked into raw case."
            )

        required_fields = {
            "case_id",
            "dispute_type",
            "order",
            "customer_evidence",
            "agent_evidence",
            "delivery_evidence",
            "sla_version",
        }

        missing_fields = required_fields - set(case.keys())

        if missing_fields:
            errors.append(
                f"{case_id}: missing required fields: "
                f"{sorted(missing_fields)}"
            )

        evidence_ids = collect_case_evidence_ids(case)

        if len(evidence_ids) == 0:
            errors.append(
                f"{case_id}: no evidence IDs found."
            )

        if case.get("sla_version") != "0.1":
            errors.append(
                f"{case_id}: unexpected SLA version "
                f"'{case.get('sla_version')}'."
            )

    # ---------------------------------------------------------
    # 7. Ground-truth validation
    # ---------------------------------------------------------

    sla_clause_ids = extract_sla_clause_ids()

    for label in ground_truth:
        case_id = label.get("case_id")

        if not case_id:
            errors.append(
                "Ground-truth record is missing case_id."
            )
            continue

        if case_id not in raw_case_map:
            errors.append(
                f"{case_id}: ground-truth record has no matching raw case."
            )
            continue

        case = raw_case_map[case_id]

        # Decision

        decision = label.get("decision")

        if decision not in VALID_DECISIONS:
            errors.append(
                f"{case_id}: invalid decision '{decision}'."
            )

        # Required ground-truth fields

        required_gt_fields = {
            "case_id",
            "decision",
            "governing_clause_ids",
            "decisive_evidence_ids",
            "contradictory_evidence_ids",
            "missing_evidence_ids",
            "rationale",
            "sub_decisions",
            "labeler_id",
            "label_timestamp",
            "policy_version",
        }

        missing_gt_fields = required_gt_fields - set(label.keys())

        if missing_gt_fields:
            errors.append(
                f"{case_id}: missing ground-truth fields: "
                f"{sorted(missing_gt_fields)}"
            )

        # Policy version

        if label.get("policy_version") != case.get("sla_version"):
            errors.append(
                f"{case_id}: ground-truth policy_version does not "
                f"match case sla_version."
            )

        # Evidence references

        case_evidence_ids = collect_case_evidence_ids(case)

        referenced_evidence_ids = set()

        for field in (
            "decisive_evidence_ids",
            "contradictory_evidence_ids",
            "missing_evidence_ids",
        ):
            for evidence_id in label.get(field, []):
                referenced_evidence_ids.add(evidence_id)

                if evidence_id not in case_evidence_ids:
                    errors.append(
                        f"{case_id}: {field} references "
                        f"unknown evidence ID '{evidence_id}'."
                    )

        # Clause references

        for clause_id in label.get("governing_clause_ids", []):
            if clause_id not in sla_clause_ids:
                errors.append(
                    f"{case_id}: unknown SLA clause '{clause_id}'."
                )

    # ---------------------------------------------------------
    # 8. One-to-one case/ground-truth matching
    # ---------------------------------------------------------

    raw_id_set = set(raw_ids)
    gt_id_set = set(gt_ids)

    missing_ground_truth = raw_id_set - gt_id_set
    missing_raw_cases = gt_id_set - raw_id_set

    if missing_ground_truth:
        errors.append(
            "Raw cases without ground truth: "
            f"{sorted(missing_ground_truth)}"
        )

    if missing_raw_cases:
        errors.append(
            "Ground-truth records without raw cases: "
            f"{sorted(missing_raw_cases)}"
        )

    return errors


def main():
    print("Running Phase 1 pilot dataset validation...")
    print()

    errors = validate()

    if errors:
        print("VALIDATION FAILED")
        print("-" * 60)

        for error in errors:
            print(f"[ERROR] {error}")

        print()
        print(f"{len(errors)} error(s) found.")
        raise SystemExit(1)

    print("VALIDATION PASSED")
    print("-" * 60)
    print("Raw cases:       10")
    print("Ground truths:   10")
    print("Leakage check:   PASS")
    print("Evidence refs:   PASS")
    print("SLA clause refs: PASS")
    print("Case ID matching: PASS")
    print("Policy versions: PASS")
    print()
    print("Phase 1 pilot dataset is structurally consistent.")


if __name__ == "__main__":
    main()