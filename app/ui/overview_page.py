"""Overview — what the system does, how well it does it, and where to look first."""

import streamlit as st

from app.ui import theme
from app.ui.adjudication_page import case_label
from app.ui.settings import Settings
from src.clause_matching.clause_retrieval import governing_recall
from src.evaluation.experiment import list_runs
from src.evidence_extraction.case_loader import get_case

PIPELINE = [
    ("Evidence", "Chat and email from the customer, the agent's statement, the delivery photo, route and cash logs."),
    ("Facts", "The extractor reads the timing, what the photo shows, the amounts and the evidence on file — "
              "each fact linked to its source."),
    ("Clauses", "A hybrid retriever picks the SLA clauses the case turns on, including those its facts trigger."),
    ("Ruling", "An LLM decides approve, reject or escalate, citing clauses and evidence. A rules engine "
               "checks it, or decides alone when offline."),
    ("Evaluation", "Every configuration is scored against reference rulings and simple baselines."),
]

SHOWCASE = [
    ("DG-005", "The delivery photo is too blurry to use. The hub's water-damage log and the agent's own words "
               "carry the claim instead."),
    ("COD-003", "The customer says ₹200 was overcharged; the cash log says ₹100. The refund follows the log."),
    ("DG-004", "A ₹7,499 claim with no unboxing video. The record cannot settle fault, so it goes to a person."),
]


def _go(case_id: str) -> None:
    st.session_state["page"] = "Adjudicate a case"
    st.session_state["adj_case"] = case_label(get_case(case_id))


def render(settings: Settings) -> None:
    theme.page_header(
        "Rulings on delivery disputes, grounded in the SLA",
        "Damaged-goods and cash-on-delivery complaints are decided the way a careful support lead would: "
        "read the evidence, find the clause that applies, and show the working. When the record cannot "
        "settle it, the case is escalated instead of guessed.",
    )

    theme.md('<div class="pipe">' + "".join(
        f"<div><b>{i}</b><strong>{name}</strong><span>{theme.esc(text)}</span></div>"
        for i, (name, text) in enumerate(PIPELINE, 1)) + "</div>")

    theme.subhead("Results so far")
    pilot = [r for r in list_runs("pilot")]
    stress = [r for r in list_runs("counterfactual")]
    llm = [r for r in pilot if r["config"]["engine"] == "llm"]
    rules_pilot = next((r for r in pilot if r["config"]["engine"] == "rules"), None)
    rules_stress = next((r for r in stress if r["config"]["engine"] == "rules"), None)

    cols = st.columns(4)
    with cols[0]:
        if llm:
            best = max(llm, key=lambda r: r["metrics"]["decision_accuracy"])
            theme.big_number(f"{best['metrics']['decision_accuracy']:.0%}",
                             f"LLM decision accuracy, pilot set ({best['label']})")
        else:
            theme.big_number("—", "LLM decision accuracy: no LLM run saved yet")
    with cols[1]:
        if rules_stress:
            m = rules_stress["metrics"]
            theme.big_number(f"{sum(1 for r in m['per_case'] if r['correct'])}/{m['n']}",
                             "Counterfactual cases ruled correctly by the rules engine")
    with cols[2]:
        r = governing_recall("hybrid", 4)
        theme.big_number(f"{r['recall']:.0%}", "Governing clauses retrieved at k=4 (hybrid + fact triggers)")
    with cols[3]:
        if rules_pilot:
            theme.big_number(f"{rules_pilot['baselines']['majority_class']['decision_accuracy']:.0%}",
                             "Majority-class baseline on the pilot set, for scale")

    theme.subhead("Three cases worth opening")
    cols = st.columns(3)
    for col, (case_id, blurb) in zip(cols, SHOWCASE):
        with col:
            theme.md(f'<div class="ruling" style="padding:16px 18px;min-height:150px">'
                     f'<div class="cl-id">{case_id}</div><div class="ev-body" style="margin-top:6px">'
                     f'{theme.esc(blurb)}</div></div>')
            st.button(f"Open {case_id}", key=f"go::{case_id}", on_click=_go, args=(case_id,),
                      width="stretch")

    if not settings.llm_ready:
        theme.subhead("Running without a model key")
        theme.note("No LLM provider is configured on this deployment, so every ruling comes from the rules "
                   "engine. Everything else — extraction, retrieval, the what-if explorer and evaluation — works "
                   "the same. Add <code>GROQ_API_KEY</code> to switch the model on.")
