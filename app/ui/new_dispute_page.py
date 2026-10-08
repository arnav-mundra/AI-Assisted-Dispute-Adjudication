"""New dispute — enter a case the way a support agent receives it.

The customer's own message is the primary input; amounts, damage type and
location, and unboxing statements are read out of it by the evidence
extractor, exactly as for the pilot cases. The form only asks for what a
support agent would look up in their systems (PoD, logs, order value).
"""

import streamlit as st

from app.ui import adjudication_page, theme
from app.ui.settings import Settings
from src.evidence_extraction.extractor import claimed_amount
from src.evidence_extraction.manual_case import COD_MISMATCH, DAMAGED_GOODS, build_manual_case

STATE_KEY = "manual_case"

EXAMPLES = {
    DAMAGED_GOODS: {
        "Crushed box, cracked lamp": dict(
            narrative="Got my order this morning. The box was squashed on one corner and the glass shade of "
                      "the lamp has a crack running down the left side. Photo attached.",
            agent="Left it with the customer at the door, did not check the box.",
            hours=6.0, value=2899.0, pod="Shows damage", unboxing=False, note="", prior=0),
        "Expensive phone, no unboxing video": dict(
            narrative="The phone I ordered has a dead pixel line across the top of the screen. The outer box "
                      "looked perfect. I didn't record an unboxing video.",
            agent="Box sealed, handed over with OTP.",
            hours=20.0, value=18999.0, pod="Shows intact", unboxing=False, note="", prior=0),
    },
    COD_MISMATCH: {
        "Overcharged ₹300": dict(
            narrative="My invoice says 1,200 but the delivery person took ₹1,500 cash and said there was a "
                      "COD fee. Please refund the extra.",
            agent="", hours=3.0, total=1200.0, recon=True, recon_amount=1500.0, note=""),
        "Log missing after outage": dict(
            narrative="Invoice total was 2,640 but the agent collected 2,700 from me yesterday evening.",
            agent="", hours=14.0, total=2640.0, recon=False, recon_amount=0.0,
            note="No entry — cash reconciliation system outage on this route."),
    },
}


def _example_buttons(dispute_type: str) -> None:
    cols = st.columns(len(EXAMPLES[dispute_type]) + 1)
    cols[0].caption("Start from an example")
    for col, (name, values) in zip(cols[1:], EXAMPLES[dispute_type].items()):
        if col.button(name, width="stretch", key=f"ex::{name}"):
            st.session_state["nd_example"] = values
            st.rerun()


def _form(settings: Settings) -> None:
    theme.page_header(
        "New dispute",
        "Paste the customer's message and fill in what you would look up in the order and delivery "
        "systems. The extractor reads the message; the same pipeline then rules on it.",
    )
    kind = st.radio("Dispute type", ["Damaged goods", "COD mismatch"], horizontal=True, key="nd_kind")
    dispute_type = DAMAGED_GOODS if kind == "Damaged goods" else COD_MISMATCH
    _example_buttons(dispute_type)
    ex = st.session_state.get("nd_example") or {}
    if ex and ("pod" in ex) != (dispute_type == DAMAGED_GOODS):
        ex = {}

    with st.form("new_dispute"):
        example_message = ("The box was crushed and the ceramic base is cracked across the rim…"
                           if dispute_type == DAMAGED_GOODS else
                           "The invoice for my order was ₹1,500 but the agent collected ₹1,700 in cash…")
        narrative = st.text_area("Customer's message", value=ex.get("narrative", ""), height=120,
                                 placeholder=example_message)
        agent = st.text_input("Delivery agent's statement (optional)", value=ex.get("agent", ""))
        hours = st.slider("Hours between delivery and the customer's first message", 0.0, 240.0,
                          float(ex.get("hours", 8.0)), 0.5)

        if dispute_type == DAMAGED_GOODS:
            a, b = st.columns(2)
            with a:
                value = st.number_input("Order value (₹)", 0.0, 500000.0, float(ex.get("value", 2499.0)), 100.0)
                pod_options = ["Shows intact", "Shows damage", "Blurry / unusable"]
                pod = st.radio("Delivery (PoD) photo", pod_options,
                               index=pod_options.index(ex.get("pod", "Shows intact")), horizontal=True)
                prior = st.number_input("Prior damage claims by this customer (90 days)", 0, 20,
                                        int(ex.get("prior", 0)))
            with b:
                unboxing = st.checkbox("Customer sent an unboxing photo or video", value=ex.get("unboxing", False))
                unboxing_desc = st.text_input("What the unboxing media shows (optional)")
                note = st.text_input("Delivery or hub log note (optional)", value=ex.get("note", ""),
                                     placeholder="Hub exception: wet consignments, batch flagged")
            fields = dict(order_value_inr=value, pod_shows_damage=pod == "Shows damage",
                          pod_unusable=pod.startswith("Blurry"), unboxing_evidence=unboxing,
                          unboxing_description=unboxing_desc, prior_claims_90d=int(prior), delivery_note=note)
        else:
            a, b = st.columns(2)
            with a:
                total = st.number_input("Invoice total (₹)", 0.0, 500000.0, float(ex.get("total", 1500.0)), 10.0)
                claimed = st.number_input("Amount customer says was taken (₹, 0 = read from message)", 0.0,
                                          500000.0, 0.0, 10.0)
            with b:
                recon = st.checkbox("Reconciliation log has an entry", value=ex.get("recon", True))
                recon_amount = st.number_input("Amount in the reconciliation log (₹)", 0.0, 500000.0,
                                               float(ex.get("recon_amount", 1500.0)), 10.0, disabled=not recon)
                note = st.text_input("Reconciliation note (optional)", value=ex.get("note", ""))
            fields = dict(order_value_inr=total, order_total_cod_inr=total, claimed_amount_inr=claimed or None,
                          reconciliation_available=recon, reconciliation_amount_inr=recon_amount if recon else None,
                          reconciliation_note=note)

        submitted = st.form_submit_button("Build the case and open it", type="primary", width="stretch")

    if dispute_type == COD_MISMATCH and narrative.strip():
        read = claimed_amount(narrative, fields.get("order_total_cod_inr"))
        st.caption(f"Amount the extractor reads from this message: "
                   f"{theme.money(read) if read is not None else 'none stated'}.")

    if submitted:
        try:
            case = build_manual_case(dispute_type=dispute_type, customer_narrative=narrative,
                                     hours_since_pod=hours, agent_statement=agent, **fields)
        except ValueError as exc:
            st.error(str(exc))
            return
        st.session_state[STATE_KEY] = case
        st.session_state.pop("nd_example", None)
        st.rerun()


def render(settings: Settings) -> None:
    case = st.session_state.get(STATE_KEY)
    if case is None:
        _form(settings)
        return
    theme.page_header("New dispute", "Entered by hand and assembled into the same case structure as the "
                                     "pilot set. There is no reference label for a case entered here.")
    if st.button("Enter another dispute"):
        del st.session_state[STATE_KEY]
        st.rerun()
    adjudication_page.render_case(case, settings)
