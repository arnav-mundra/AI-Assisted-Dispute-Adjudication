"""Keep data/raw/pilot/pilot_cases.json and docs/phase0/case_schema.json in sync.

validate_pilot.py checks cross-file consistency (IDs, clauses, leakage); this
module checks that each case conforms to the declared JSON Schema.
"""

import json

import pytest

from src.validation.validate_pilot import (
    ROOT,
    RAW_CASES_FILE,
    collect_case_evidence_ids,
    load_json,
)

SCHEMA_FILE = ROOT / "docs" / "phase0" / "case_schema.json"


@pytest.fixture(scope="module")
def cases():
    return load_json(RAW_CASES_FILE)


def test_cases_conform_to_case_schema(cases):
    jsonschema = pytest.importorskip("jsonschema")

    schema = json.loads(SCHEMA_FILE.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)

    failures = []

    for case in cases:
        for error in validator.iter_errors(case):
            path = "/".join(str(part) for part in error.absolute_path)
            failures.append(f"{case.get('case_id')}: {path}: {error.message}")

    assert not failures, "\n".join(failures)


def test_evidence_ids_are_unique_across_the_dataset(cases):
    seen = {}
    duplicates = []

    for case in cases:
        for evidence_id in collect_case_evidence_ids(case):
            if evidence_id in seen:
                duplicates.append(
                    f"{evidence_id} appears in both {seen[evidence_id]} "
                    f"and {case.get('case_id')}"
                )
            else:
                seen[evidence_id] = case.get("case_id")

    assert not duplicates, "\n".join(duplicates)
