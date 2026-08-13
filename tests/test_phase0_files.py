from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_phase0_artifacts_exist():
    required = [
        ROOT / "docs" / "sla_policy.md",
        ROOT / "docs" / "phase0" / "case_schema.json",
        ROOT / "docs" / "phase0" / "GROUND_TRUTH_SCHEMA.md",
        ROOT / "docs" / "phase0" / "evaluation_protocol.md",
        ROOT / "docs" / "phase0" / "REPRODUCIBILITY.md",
        ROOT / "requirements.txt",
        ROOT / ".env.example",
    ]
    missing = [str(p.relative_to(ROOT)) for p in required if not p.exists()]
    assert not missing, f"Missing Phase 0 artifacts: {missing}"


def test_sla_has_stable_clause_ids():
    text = (ROOT / "docs" / "sla_policy.md").read_text(encoding="utf-8")
    for clause in ["SLA-DG-01", "SLA-DG-08", "SLA-COD-03", "SLA-COD-06", "SLA-PRI-02"]:
        assert clause in text
