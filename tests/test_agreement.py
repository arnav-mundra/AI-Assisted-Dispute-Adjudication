import csv

from src.evaluation.datasets import load_dataset
from src.validation.agreement import (
    TEMPLATE_COLUMNS,
    cohens_kappa,
    compare,
    export_template,
    load_second_labels,
)


def test_kappa_perfect_and_chance():
    assert cohens_kappa(["A", "B", "C"], ["A", "B", "C"]) == 1.0
    # Every rating identical on both sides: observed == expected, defined as perfect.
    assert cohens_kappa(["A", "A"], ["A", "A"]) == 1.0
    assert abs(cohens_kappa(["A", "A", "B", "B"], ["A", "B", "A", "B"])) < 1e-9


def test_template_is_blind(tmp_path):
    path = export_template("pilot", tmp_path / "t.csv")
    with path.open(encoding="utf-8-sig", newline="") as file:
        rows = list(csv.DictReader(file))
    assert tuple(rows[0].keys()) == TEMPLATE_COLUMNS
    assert len(rows) == 10
    assert all(not row["decision"] and not row["governing_clause_ids"] for row in rows)


def test_compare_records_disagreements(tmp_path):
    _, first = load_dataset("pilot")
    path = export_template("pilot", tmp_path / "t.csv")
    with path.open(encoding="utf-8-sig", newline="") as file:
        rows = list(csv.DictReader(file))
    by_id = {l["case_id"]: l for l in first}
    for row in rows:
        row["decision"] = by_id[row["case_id"]]["decision"]
        row["governing_clause_ids"] = "; ".join(by_id[row["case_id"]]["governing_clause_ids"])
    rows[0]["decision"] = "ESCALATE" if rows[0]["decision"] != "ESCALATE" else "APPROVE"
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=TEMPLATE_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)

    result = compare(first, load_second_labels(path))
    assert result["n"] == 10
    assert result["raw_agreement"] == 0.9
    assert 0 < result["kappa"] < 1
    assert [r["case_id"] for r in result["rows"] if not r["agree"]] == [rows[0]["case_id"]]
    assert result["clause_jaccard"] == 1.0
