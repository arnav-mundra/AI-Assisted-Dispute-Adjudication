"""Adjudicate a case — the main demonstration view.

Left: what the system read (evidence, extracted facts, retrieved clauses,
reasoning). Right: the ruling. Reference labels are never read on this page;
they live only in the Evaluation view.
"""

from typing import Any, Dict

import streamlit as st

from app.ui import theme
from app.ui.settings import Settings
from src.clause_matching.clause_retrieval import retrieve
from src.evidence_extraction.case_loader import evidence_items, get_case, load_cases
from src.evidence_extraction.extractor import extract_facts
from src.reasoning_engine.adjudicator import adjudicate, build_user_prompt

PRODUCT_SHORT = 34


def case_label(case: Dict[str, Any]) -> str:
    kind = "Damaged goods" if case["dispute_type"] == "DAMAGED_GOODS" else "COD mismatch"
    product = (case["order"].get("product_name") or "").split(",")[0][:PRODUCT_SHORT]
    return f"{case['case_id']}  —  {kind}, {product}"


def render(settings: Settings) -> None:
    cases = load_cases()
    labels = {case_label(c): c["case_id"] for c in cases}
    theme.page_header(
        "Adjudicate a case",
        "Pick a dispute from the pilot set. The system reads the evidence, extracts the facts the SLA "
        "turns on, retrieves the governing clauses, and returns a ruling that cites both.",
    )
    choice = st.selectbox("Dispute", list(labels), key="adj_case")
    render_case(get_case(labels[choice]), settings)


def _run(case: Dict[str, Any], settings: Settings):
    return adjudicate(case, model=settings.model, top_k=settings.top_k, prompt_style=settings.prompt_style,
                      retrieval=settings.retrieval, engine=settings.engine, guard=settings.guard,
                      min_confidence=settings.min_confidence)


def render_case(case: Dict[str, Any], settings: Settings) -> None:
    facts = extract_facts(case)
    clauses = retrieve(case, top_k=settings.top_k, method=settings.retrieval)
    result_key = f"ruling::{case['case_id']}::{settings.key}"
    result = st.session_state.get(result_key)

    theme.case_header(case)
    theme.timeline(case, facts.to_dict())

    left, right = st.columns([1.15, 1], gap="large")

    with right:
        theme.subhead("Ruling")
        engine_note = settings.describe()
        if st.button("Rule on this case", type="primary", width="stretch", key=f"run::{result_key}"):
            with st.spinner(f"Adjudicating with {engine_note}…"):
                try:
                    st.session_state[result_key] = result = _run(case, settings)
                except Exception as exc:  # surfaced, never swallowed
                    st.error(f"The ruling could not be produced: {exc}")
                    result = None
        st.caption(f"Engine: {engine_note}. Top-{settings.top_k} {settings.retrieval} retrieval.")

        if result is None:
            theme.note("No ruling yet. Press <b>Rule on this case</b>. The engine sees the evidence, the "
                       "extracted facts and the retrieved clauses — never the reference label.")
        else:
            theme.ruling_card(result)
            theme.cross_check(result)
            for warning in result.warnings:
                st.warning(warning)

    with left:
        cited = result.evidence_ids_used if result else []
        cited_clauses = result.cited_clause_ids if result else []
        tabs = st.tabs(["Evidence", f"Facts ({len(facts.facts)})", f"Clauses ({len(clauses)})",
                        "Reasoning", "Details"])

        with tabs[0]:
            items = evidence_items(case)
            for section, name in theme.SECTION_NAMES.items():
                group = [i for i in items if i["_section"] == section]
                if group:
                    theme.md(f'<div class="muted" style="margin:8px 0 4px 0">{name}</div>')
                    theme.md("".join(theme.evidence_card(i, cited) for i in group))

        with tabs[1]:
            st.caption("Read deterministically from the evidence text. Each fact names the evidence it came from.")
            theme.facts_table(facts.rows())

        with tabs[2]:
            st.caption("Ranked clauses plus the clauses every case needs: priority rules, the eligibility gate, "
                       "clauses whose condition an extracted fact triggers, and cross-references.")
            top = max((c.score for c in clauses), default=0.0)
            primary = result.primary_clause_id if result else ""
            theme.md("".join(theme.clause_card(c, cited_clauses, top, primary) for c in clauses))

        with tabs[3]:
            if result is None:
                st.caption("Rule on the case to see how the decision was reached.")
            else:
                st.caption("The SLA decision procedure, step by step." if result.engine == "rules" else
                           "The model's own analysis steps (structured-reasoning prompt only).")
                theme.trace_list(result.trace)
                if result.engine == "llm" and not result.trace:
                    st.caption("Switch the prompt style to 'Fact-grounded + reasoning steps' to record them.")

        with tabs[4]:
            if settings.effective_engine == "llm":
                st.code(build_user_prompt(case, clauses, settings.prompt_style, facts), language="text")
            else:
                st.caption("The rules engine does not use a prompt. Its input is the extracted facts.")
            if result is not None:
                st.json(result.to_dict(), expanded=False)
                if result.raw_response:
                    st.code(result.raw_response, language="json")
