"""SLA policy — the rulebook every ruling cites."""

import streamlit as st

from app.ui import theme
from app.ui.settings import Settings
from src.clause_matching.sla_clauses import load_clauses, sla_version


def render(settings: Settings) -> None:
    clauses = load_clauses()
    theme.page_header(
        f"SLA policy, version {sla_version()}",
        f"The {len(clauses)} clauses the system adjudicates against. Each clause is a retrievable unit with a "
        "stable ID, so every ruling can point to the exact rule it applied.",
    )
    query = st.text_input("Search the policy", placeholder="refund, 48 hours, unboxing, reconciliation…")
    sections = {}
    for clause in clauses.values():
        sections.setdefault(clause.section, []).append(clause)
    for section, items in sections.items():
        shown = [c for c in items if not query or query.lower() in c.text.lower() or query.upper() in c.clause_id]
        if not shown:
            continue
        theme.subhead(section)
        theme.md("".join(
            f'<div class="cl"><div class="cl-head"><span class="cl-id">{theme.esc(c.clause_id)}</span></div>'
            f'<div class="cl-text">{theme.esc(theme.clause_body(c.text))}</div></div>' for c in shown))
