"""Canonical filesystem locations for the project.

Every module resolves data and policy files through here, so a dataset or
document move is a one-line change rather than a search across packages.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
LABELED_DIR = DATA_DIR / "labeled"
SYNTHETIC_DIR = DATA_DIR / "synthetic"

DOCS_DIR = ROOT / "docs"
SLA_FILE = DOCS_DIR / "sla_policy.md"
CASE_SCHEMA_FILE = DOCS_DIR / "phase0" / "case_schema.json"

# Phase 1 pilot dataset
PILOT_CASES_FILE = RAW_DIR / "pilot" / "pilot_cases.json"
PILOT_GROUND_TRUTH_FILE = LABELED_DIR / "pilot" / "pilot_ground_truth.json"

RUNS_DIR = ROOT / "runs"

ENV_FILE = ROOT / ".env"
