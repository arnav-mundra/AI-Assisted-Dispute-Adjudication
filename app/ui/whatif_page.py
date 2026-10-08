"""What-if explorer — change one fact of a pilot case and watch the ruling respond.

Edits are applied to a copy of the case's evidence (timestamps, PoD photo,
logs, amounts), then the whole pipeline re-runs: extraction, retrieval, and
the rules engine instantly; the LLM on request.
"""

import copy
from typing import Any, Dict

import streamlit as st

from app.ui import theme
from app.ui.adjudication_page import case_label
from app.ui.settings import Settings
from src.evaluation.counterfactuals import add_delivery_log, drop, report_after, set_order, set_recon
from src.evidence_extraction.case_loader import get_case, load_cases
from src.evidence_extraction.extractor import extract_facts
from src.reasoning_engine.adjudicator import adjudicate
from src.reasoning_engine.rules_engine import adjudicate_rules

POD_TEXT = {
    "Shows damage": ("clear", "Carton photographed at the door; one corner is visibly crushed and a side flap is torn."),
    "Shows intact": ("clear", "Sealed carton photographed at the door; edges square, tape intact, no dents or staining."),
    "Blurry / unusable": ("blurry", "Low-light, motion-blurred image of a carton; condition cannot be assessed."),
}


def _set_pod(case: Dict[str, Any], state: str) -> None:
    pod = next(i for i in case["delivery_evidence"] if i["type"] == "POD")
    quality, text = POD_TEXT[state]
    pod["image_quality"], pod["photo_description"] = quality, text
    if quality == "blurry":
        pod["reliability_note"] = "Image flagged as blurry by the PoD quality check; not usable for assessing condition."
    else:
        pod.pop("reliability_note", None)


def _set_unboxing(case: Dict[str, Any], on: bool) -> None:
    existing = [i for i in case["customer_evidence"] if "unbox" in (i.get("text") or "").lower()
                and i.get("type") == "PHOTO"]
    if on and not existing:
        first = case["customer_evidence"][0]
        case["customer_evidence"].append({
            "evidence_id": "CUSTOMER-990", "type": "PHOTO", "channel": "support_chat",
            "timestamp_ist": first["timestamp_ist"],
            "text": "Customer-uploaded unboxing video attached to the chat.",
            "photo_description": "Unboxing video: sealed carton opened on camera; the product is visibly damaged inside.",
        })
    if not on:
        case["customer_evidence"] = [i for i in case["customer_evidence"] if i not in existing]


def _set_hub_exception(case: Dict[str, Any], on: bool) -> None:
    logs = [i for i in case["delivery_evidence"] if i["type"] == "DELIVERY_LOG"]
    has = any("exception scanned" in (l.get("note") or "").lower() and "no exception" not in
              (l.get("note") or "").lower() for l in logs)
    if on and not has:
        add_delivery_log("DELIVERY-990", "Hub exception scanned: crushed and wet consignments in this batch, "
                                         "batch flagged.")(case)
    if not on and has:
        for log in logs:
            if "no exception" not in (log.get("note") or "").lower():
                log["note"] = "Route log. No exception scanned on the route."


def _set_claim(case: Dict[str, Any], total: float, claimed: float) -> None:
    first = case["customer_evidence"][0]
    first["text"] = (f"The invoice for this order is {total:,.0f} but the agent took {claimed:,.0f} from me in "
                     f"cash. Please refund the difference.")


def render(settings: Settings) -> None:
    theme.page_header(
        "What-if explorer",
        "Change one fact of a pilot case — when it was reported, what the delivery photo shows, what the "
        "cash log says — and see whether the ruling changes, and which clause takes over.",
    )
    cases = load_cases()
    labels = {case_label(c): c["case_id"] for c in cases}
    choice = st.selectbox("Start from", list(labels), key="wi_case")
    base = get_case(labels[choice])
    base_facts = extract_facts(base)
    edited = copy.deepcopy(base)

    knobs, view = st.columns([1, 1.35], gap="large")
    with knobs:
        theme.subhead("Change the facts")
        hours = st.slider("Hours from delivery to first report", 0.0, 240.0,
                          float(base_facts.get("hours_to_report") or 0.0), 0.5, key=f"wi_h::{base['case_id']}")
        if abs(hours - (base_facts.get("hours_to_report") or 0.0)) > 0.01:
            report_after(hours)(edited)

        if base["dispute_type"] == "DAMAGED_GOODS":
            current = {"DAMAGED": "Shows damage", "INTACT": "Shows intact"}.get(base_facts.get("pod_condition"),
                                                                                "Blurry / unusable")
            options = list(POD_TEXT)
            pod = st.radio("Delivery (PoD) photo", options, index=options.index(current), horizontal=True,
                           key=f"wi_pod::{base['case_id']}")
            if pod != current:
                _set_pod(edited, pod)
            value = st.number_input("Order value (₹)", 0.0, 100000.0, float(base["order"]["order_value_inr"]),
                                    500.0, key=f"wi_v::{base['case_id']}")
            if value != base["order"]["order_value_inr"]:
                set_order(order_value_inr=value)(edited)
            unboxing = st.toggle("Customer sent an unboxing video", value=bool(base_facts.get("unboxing_evidence")),
                                 key=f"wi_u::{base['case_id']}")
            _set_unboxing(edited, unboxing)
            hub = st.toggle("Hub logged a damage exception", value=bool(base_facts.get("hub_damage_exception")),
                            key=f"wi_x::{base['case_id']}")
            _set_hub_exception(edited, hub)
            prior = st.number_input("Prior damage claims in 90 days", 0, 10, 0, key=f"wi_p::{base['case_id']}")
            if prior:
                add_delivery_log("DELIVERY-991", f"Account history: {prior} prior damaged-goods claim(s) from "
                                                 "this customer in the rolling 90-day window.")(edited)
        else:
            total = float(base["order"]["order_total_cod_inr"])
            st.caption(f"Invoice total: {theme.money(total)}")
            claimed0 = base_facts.get("claimed_collected_inr") or total
            claimed = st.number_input("Customer says the agent took (₹)", 0.0, 100000.0, float(claimed0), 10.0,
                                      key=f"wi_c::{base['case_id']}")
            if claimed != claimed0:
                _set_claim(edited, total, claimed)
            has_log = base_facts.get("recon_status") == "RECORDED"
            log = st.toggle("Reconciliation log has an entry", value=has_log, key=f"wi_l::{base['case_id']}")
            recon0 = float(base_facts.get("recon_amount_inr") or total)
            recon = st.number_input("Amount in the log (₹)", 0.0, 100000.0, recon0, 10.0, disabled=not log,
                                    key=f"wi_r::{base['case_id']}")
            if log and (not has_log or recon != recon0):
                set_recon(recon)(edited)
            if not log and has_log:
                entry = next(i for i in edited["delivery_evidence"] if i["type"] == "RECONCILIATION_LOG")
                entry.update(status="UNAVAILABLE", amount_collected_inr=None,
                             note="No entry — reconciliation system outage on this route.")
            photos = [i for i in base["customer_evidence"] if i.get("type") == "PHOTO"]
            corroborate = st.toggle("Customer sent a photo of the cash handed over", value=bool(photos),
                                    key=f"wi_ph::{base['case_id']}")
            if photos and not corroborate:
                for p in photos:
                    drop("customer_evidence", p["evidence_id"])(edited)
            if corroborate and not photos:
                edited["customer_evidence"].append({
                    "evidence_id": "CUSTOMER-990", "type": "PHOTO", "channel": "support_chat",
                    "timestamp_ist": edited["customer_evidence"][0]["timestamp_ist"],
                    "text": "Customer-uploaded photo attached to the chat.",
                    "photo_description": "Currency notes on a table; no person, parcel or timestamp visible; "
                                         "no verifiable capture metadata."})

    original = adjudicate_rules(base)
    new_facts = extract_facts(edited)
    changed = adjudicate_rules(edited, facts=new_facts)

    with view:
        a, b = st.columns(2)
        with a:
            theme.mini_ruling(original, "As recorded")
        with b:
            theme.mini_ruling(changed, "With your changes")

        if changed.decision != original.decision or changed.primary_clause_id != original.primary_clause_id:
            theme.note(f"The ruling moves from <b>{theme.esc(original.decision.lower())}</b> under "
                       f"{theme.esc(original.primary_clause_id)} to <b>{theme.esc(changed.decision.lower())}</b> "
                       f"under <span class='cite'>{theme.esc(changed.primary_clause_id)}</span>.")
        else:
            theme.note("Same ruling. Try moving the report past the window, or changing what the PoD photo shows.")

        diffs = [row for key, row in zip(new_facts.facts, new_facts.rows())
                 if key in base_facts.facts and base_facts.facts[key].display_value() != row["value"]]
        if diffs:
            theme.subhead("Facts that changed")
            for row in diffs:
                old = next(r["value"] for k, r in zip(base_facts.facts, base_facts.rows()) if r["fact"] == row["fact"])
                row["detail"] = f"was {old}"
            theme.facts_table(diffs)

        theme.subhead("How the rules engine reached it")
        theme.trace_list(changed.trace)
        theme.md(f'<div class="rationale" style="border:none;padding-top:6px">'
                 f'{theme.linkify_clauses(changed.rationale)}</div>')

        if settings.llm_ready and settings.engine != "rules":
            if st.button(f"Ask {settings.model} about the changed case"):
                with st.spinner("Adjudicating…"):
                    try:
                        result = adjudicate(edited, model=settings.model, top_k=settings.top_k,
                                            prompt_style=settings.prompt_style, retrieval=settings.retrieval,
                                            guard=settings.guard, min_confidence=settings.min_confidence)
                        theme.ruling_card(result)
                        theme.cross_check(result)
                    except Exception as exc:
                        st.error(f"The model call failed: {exc}")
