"""New Dispute — build a case live and adjudicate it.

The form assembles the same case dict shape the pilot dataset uses, then hands
it to `adjudication_page.render_case`. There is no second adjudication path and
no ground truth for a case entered here.
"""

import streamlit as st

from app.ui import adjudication_page, theme
from src.evidence_extraction.manual_case import (
    COD_MISMATCH,
    DAMAGED_GOODS,
    build_manual_case,
)

STATE_KEY = "manual_case"

DISPUTE_LABELS = {
    "Damaged Goods": DAMAGED_GOODS,
    "COD Mismatch": COD_MISMATCH,
}


def _form() -> None:
    theme.page_header(
        "New Dispute",
        "Enter a dispute as a support agent would receive it. On submission it is assembled "
        "into the same case structure as the pilot dataset and adjudicated by the same "
        "pipeline — evidence preparation, SLA clause retrieval, model, validation.",
    )

    dispute_label = st.radio(
        "Dispute type",
        list(DISPUTE_LABELS),
        horizontal=True,
    )
    dispute_type = DISPUTE_LABELS[dispute_label]

    with st.form("new_dispute", clear_on_submit=False):
        theme.section_label("Customer claim")
        narrative = st.text_area(
            "Chat / email from the customer",
            height=150,
            placeholder=(
                "My order arrived this morning. The box was crushed on one side and the "
                "ceramic base is cracked across the bottom rim..."
            ),
            help="The claim in the customer's own words. This is the unstructured evidence.",
        )

        agent_statement = st.text_area(
            "Delivery agent statement (optional)",
            height=80,
            placeholder="Handed the parcel to the customer at the door. Box looked fine.",
        )

        theme.section_label("Order and delivery")
        col_a, col_b, col_c = st.columns(3)

        with col_a:
            order_id = st.text_input("Order ID (optional)", placeholder="ORD-2026-40118")
            hours_since_pod = st.number_input(
                "Hours since delivery (PoD)", min_value=0.0, max_value=720.0,
                value=8.0, step=0.5,
                help="Drives the reporting-window test. The model computes the interval "
                     "itself from the timestamps this produces.",
            )

        if dispute_type == DAMAGED_GOODS:
            with col_b:
                order_value = st.number_input(
                    "Order value (₹)", min_value=0.0, value=2499.0, step=100.0,
                    help="The ₹5,000 threshold in SLA-DG-03 turns on this value.",
                )
                prior_claims = st.number_input(
                    "Prior damaged-goods claims (90 days)", min_value=0, max_value=20, value=0,
                )
            with col_c:
                pod_shows_damage = st.checkbox("PoD photo shows external package damage")
                unboxing_evidence = st.checkbox("Customer provided unboxing photo/video")
                unboxing_description = st.text_input(
                    "What the unboxing image shows",
                    placeholder="Cracked ceramic base, carton corner crushed",
                    disabled=not unboxing_evidence,
                )

            cod_fields = {}
            dg_fields = {
                "order_value_inr": order_value,
                "pod_shows_damage": pod_shows_damage,
                "unboxing_evidence": unboxing_evidence,
                "unboxing_description": unboxing_description,
                "prior_claims_90d": int(prior_claims),
            }
        else:
            with col_b:
                order_total = st.number_input(
                    "Order total per invoice (₹)", min_value=0.0, value=1500.0, step=50.0,
                )
                claimed_amount = st.number_input(
                    "Amount the customer says was collected (₹)",
                    min_value=0.0, value=1700.0, step=50.0,
                )
            with col_c:
                reconciliation_available = st.checkbox(
                    "Reconciliation log exists", value=True,
                    help="Unchecked means the delivery partner has no record — SLA-COD-06.",
                )
                reconciliation_amount = st.number_input(
                    "Reconciliation log amount (₹)",
                    min_value=0.0, value=1700.0, step=50.0,
                    disabled=not reconciliation_available,
                )
                reconciliation_note = st.text_input(
                    "Reconciliation note / reliability flag (optional)",
                    placeholder="Batch re-keyed manually after terminal sync failure",
                )

            dg_fields = {"order_value_inr": order_total}
            cod_fields = {
                "order_total_cod_inr": order_total,
                "claimed_amount_inr": claimed_amount,
                "reconciliation_amount_inr": reconciliation_amount,
                "reconciliation_available": reconciliation_available,
                "reconciliation_note": reconciliation_note,
            }

        submitted = st.form_submit_button(
            "Build case and adjudicate", type="primary", use_container_width=True
        )

    if submitted:
        try:
            case = build_manual_case(
                dispute_type=dispute_type,
                customer_narrative=narrative,
                hours_since_pod=hours_since_pod,
                order_id=order_id or None,
                agent_statement=agent_statement,
                **dg_fields,
                **cod_fields,
            )
        except ValueError as exc:
            st.error(str(exc))
            return

        st.session_state[STATE_KEY] = case
        st.rerun()


def render(model: str, top_k: int) -> None:
    case = st.session_state.get(STATE_KEY)

    if case is None:
        _form()
        return

    controls = st.columns([1, 3])
    with controls[0]:
        if st.button("← Enter another dispute", use_container_width=True):
            del st.session_state[STATE_KEY]
            st.rerun()

    adjudication_page.render_case(
        case,
        model=model,
        top_k=top_k,
        title="New Dispute",
        subtitle=(
            "Manually entered case, assembled into the pilot case structure and adjudicated "
            "by the same pipeline. No reference label exists for a case entered here."
        ),
    )
