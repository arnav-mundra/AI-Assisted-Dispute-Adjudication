"""Parse docs/sla_policy.md into individually addressable clauses.

Each clause is bounded by its bold marker (``**SLA-DG-06.**``) and the next
marker, so trailing paragraphs that qualify a clause (for example the
reporting-window note under SLA-DG-03) stay attached to it.
"""

import re
from dataclasses import dataclass
from typing import Dict, List

from src.evidence_extraction.case_loader import SLA_FILE

CLAUSE_MARKER = re.compile(r"\*\*(SLA-(?:GEN|DEF|DG|COD|PRI)-\d{2})\.\*\*")
HEADING = re.compile(r"^#{2,3}\s+(.*)$", re.MULTILINE)


@dataclass(frozen=True)
class Clause:
    clause_id: str
    family: str          # GEN | DEF | DG | COD | PRI
    section: str
    text: str

    @property
    def label(self) -> str:
        return f"{self.clause_id} — {self.section}"


def _section_for(text: str, position: int) -> str:
    section = "Unsectioned"
    for match in HEADING.finditer(text):
        if match.start() > position:
            break
        section = match.group(1).strip()
    return section


def parse_clauses(sla_text: str) -> Dict[str, Clause]:
    markers = list(CLAUSE_MARKER.finditer(sla_text))
    clauses: Dict[str, Clause] = {}

    for index, match in enumerate(markers):
        clause_id = match.group(1)
        start = match.start()
        end = markers[index + 1].start() if index + 1 < len(markers) else len(sla_text)

        body = sla_text[start:end].strip()
        # Trim a trailing section heading that belongs to the next section.
        body = re.split(r"\n#{2,3}\s+", body)[0].strip()

        clauses[clause_id] = Clause(
            clause_id=clause_id,
            family=clause_id.split("-")[1],
            section=_section_for(sla_text, start),
            text=body,
        )

    return clauses


def load_clauses() -> Dict[str, Clause]:
    return parse_clauses(SLA_FILE.read_text(encoding="utf-8"))


def sla_version() -> str:
    text = SLA_FILE.read_text(encoding="utf-8")
    match = re.search(r"^\*\*Version:\*\*\s*([0-9.]+)", text, re.MULTILINE)
    return match.group(1) if match else "unknown"


def clause_ids() -> List[str]:
    return sorted(load_clauses())
