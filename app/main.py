"""AI Dispute Adjudicator — application entry point.

    python -m streamlit run app/main.py

Architecture (each stage is replaceable without touching this file):

    pilot case  ──►  evidence preparation   src/evidence_extraction/   (Phase 2)
                ──►  SLA clause retrieval   src/clause_matching/       (Phase 3)
                ──►  LLM adjudication       src/reasoning_engine/ + src/llm/ (Phase 4)
                ──►  structured JSON
                ──►  validation             src/reasoning_engine/adjudicator.py
                ──►  UI result              app/ui/

Phase 2 will supply `case_loader`'s output from raw documents; nothing above it
needs to change.
"""

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

st.set_page_config(
    page_title="AI Dispute Adjudicator",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

from app.ui import theme  # noqa: E402
from app.ui import adjudication_page, evaluation_page, new_dispute_page  # noqa: E402
from src.clause_matching.sla_clauses import load_clauses, sla_version  # noqa: E402
from src.evidence_extraction.case_loader import load_cases  # noqa: E402
from src.llm import all_models, available_models, provider_status  # noqa: E402
from src.reasoning_engine.adjudicator import default_model  # noqa: E402

theme.inject_css()


def case_option_label(case) -> str:
    kind = "Damaged goods" if case["dispute_type"] == "DAMAGED_GOODS" else "COD mismatch"
    return f"{case['case_id']} · {kind} · ₹{case['order']['order_value_inr']:,.0f}"


with st.sidebar:
    theme.brand()

    view = st.radio(
        "View",
        ["Adjudication", "New Dispute", "Evaluation"],
        label_visibility="collapsed",
    )

    usable = set(available_models())
    options = all_models()
    preferred = default_model()

    model = st.selectbox(
        "Model",
        options,
        index=options.index(preferred) if preferred in options else 0,
        format_func=lambda name: name if name in usable else f"{name}  ·  unavailable",
        help="Models whose provider key is missing are listed but cannot run.",
    )

    cases = load_cases()
    case_labels = {case_option_label(case): case["case_id"] for case in cases}
    selected_case_label = st.selectbox(
        "Dispute case",
        list(case_labels),
        disabled=view != "Adjudication",
        help="The 10-case pilot dataset.",
    )
    case_id = case_labels[selected_case_label]

    top_k = st.slider(
        "Clauses in context", min_value=6, max_value=20, value=14,
        help="How many SLA clauses the retriever puts in front of the model.",
    )

    st.markdown('<div class="section-label">Provider status</div>', unsafe_allow_html=True)
    for row in provider_status():
        theme.status_row(row["label"], bool(row["available"]), str(row["status"]))

    st.markdown('<div class="section-label">System</div>', unsafe_allow_html=True)
    theme.status_row(f"SLA policy v{sla_version()}", True, f"{len(load_clauses())} clauses")
    theme.status_row("Pilot dataset", True, f"{len(cases)} cases")

    if not usable:
        st.error(
            "No provider is configured. Add ANTHROPIC_API_KEY or GROQ_API_KEY to `.env` "
            "in the project root and restart.",
            icon="⚠️",
        )


if view == "Adjudication":
    adjudication_page.render(case_id=case_id, model=model, top_k=top_k)
elif view == "New Dispute":
    new_dispute_page.render(model=model, top_k=top_k)
else:
    evaluation_page.render(model=model, top_k=top_k)
