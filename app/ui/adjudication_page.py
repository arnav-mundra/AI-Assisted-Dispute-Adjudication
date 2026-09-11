"""Adjudication workspace — the live demonstration view.

Ground truth is never read on this page. The reference labels exist only in the
evaluation view.
"""

import json

import streamlit as st

from app.ui import theme
from src.llm import ProviderUnavailable, provider_for_model
from src.reasoning_engine.adjudicator import adjudicate
from src.evidence_extraction.case_loader import evidence_items, get_case
from src.clause_matching.clause_retrieval import retrieve
from src.clause_matching.sla_clauses import load_clauses, sla_version

RECONCILIATION_TYPES = {"RECONCILIATION_LOG"}


def _reporting_gap(case):
    pods = [i for i in evidence_items(case) if i.get("type") == "POD"]
    customer = [i for i in evidence_items(case) if i["_section"] == "customer_evidence"]
    pod_ts = theme.parse_ts(pods[0]["timestamp_ist"]) if pods else None
    first_ts = min(
        (ts for ts in (theme.parse_ts(i["timestamp_ist"]) for i in customer) if ts),
        default=None,
    )
    if not pod_ts or not first_ts:
        return None, None, None
    return pod_ts, first_ts, (first_ts - pod_ts).total_seconds() / 3600


DEFAULT_TITLE = "Dispute Adjudication"
DEFAULT_SUBTITLE = (
    "Resolves damaged-goods and cash-on-delivery disputes against the company SLA. "
    "The system reads the case evidence, retrieves the governing clauses, and returns "
    "a decision with the clause and evidence it relied on."
)


def render(case_id: str, model: str, top_k: int) -> None:
    """Render a pilot case selected by ID."""
    render_case(get_case(case_id), model=model, top_k=top_k)


def render_case(
    case: dict,
    model: str,
    top_k: int,
    title: str = DEFAULT_TITLE,
    subtitle: str = DEFAULT_SUBTITLE,
) -> None:
    """Render any case dict — pilot or manually entered — through one path."""
    pod_ts, first_ts, gap_hours = _reporting_gap(case)

    theme.page_header(title, subtitle)

    # -- Case summary ------------------------------------------------------
    theme.section_label("Case summary")

    dispute = "Damaged goods" if case["dispute_type"] == "DAMAGED_GOODS" else "COD mismatch"
    cod_total = case["order"].get("order_total_cod_inr")

    theme.summary_card([
        ("Case", theme.esc(case["case_id"])),
        ("Dispute type", theme.esc(dispute)),
        ("Order ID", f'<small>{theme.esc(case["order"]["order_id"])}</small>'),
        ("Order value", f'₹{case["order"]["order_value_inr"]:,.0f}'),
        ("COD amount due", f'₹{cod_total:,.0f}' if cod_total is not None else "<small>n/a</small>"),
        ("Delivered (PoD)", f'<small>{theme.esc(pod_ts.strftime("%d %b %Y, %H:%M IST")) if pod_ts else "—"}</small>'),
        ("Claim reported", f'<small>{theme.esc(first_ts.strftime("%d %b %Y, %H:%M IST")) if first_ts else "—"}</small>'),
        ("Reported after", f'{gap_hours:.1f} h' if gap_hours is not None else "—"),
        ("SLA version", f'v{theme.esc(case["sla_version"])}'),
    ])

    left, right = st.columns([1.06, 1], gap="large")

    # -- Evidence ----------------------------------------------------------
    with left:
        theme.section_label("Evidence on file")

        items = evidence_items(case)
        customer = [i for i in items if i["_section"] == "customer_evidence"]
        agent = [i for i in items if i["_section"] == "agent_evidence"]
        delivery = [
            i for i in items
            if i["_section"] == "delivery_evidence" and i.get("type") not in RECONCILIATION_TYPES
        ]
        reconciliation = [i for i in items if i.get("type") in RECONCILIATION_TYPES]

        tab_specs = [
            (f"Customer ({len(customer)})", customer, "customer_evidence"),
            (f"Agent ({len(agent)})", agent, "agent_evidence"),
            (f"Delivery / PoD ({len(delivery)})", delivery, "delivery_evidence"),
        ]
        if reconciliation:
            tab_specs.append(
                (f"Reconciliation ({len(reconciliation)})", reconciliation, "reconciliation")
            )

        for tab, (_, section_items, key) in zip(
            st.tabs([label for label, _, _ in tab_specs]), tab_specs
        ):
            with tab:
                st.caption(theme.SECTION_META[key][1])
                if not section_items:
                    st.info("No evidence of this type on file for this case.")
                for item in section_items:
                    st.markdown(theme.evidence_card(item), unsafe_allow_html=True)

        retrieved = retrieve(case, top_k=top_k)
        with st.expander(f"SLA clauses retrieved into context ({len(retrieved)})"):
            st.caption(
                f"Lexically ranked against SLA v{sla_version()}, plus the priority rules and "
                "eligibility gates that apply to every case and any clause they cross-reference."
            )
            for item in retrieved:
                st.markdown(f"**{item.clause_id}** · score {item.score:.2f} · _{item.reason}_")
                st.caption(item.clause.text[:340] + ("…" if len(item.clause.text) > 340 else ""))

    # -- Adjudication ------------------------------------------------------
    with right:
        theme.section_label("Adjudication")

        try:
            provider = provider_for_model(model)
            provider_ready = provider.is_available()
            provider_note = f"{provider.label} · {provider.status()}"
        except KeyError:
            provider = None
            provider_ready = False
            provider_note = f"No provider serves '{model}'"

        run = st.button(
            f"⚖  Run AI Adjudication — {case['case_id']}",
            type="primary",
            use_container_width=True,
            disabled=not provider_ready,
        )
        st.caption(f"Model: `{model}` · {provider_note}")

        if not provider_ready:
            st.error(
                f"This model cannot run: {provider_note}. "
                f"Set the provider's API key in `.env` and restart, or pick another model "
                f"in the sidebar."
            )

        result_key = f"result::{case['case_id']}::{model}"

        if run:
            progress = st.progress(0, text="Preparing evidence…")
            try:
                progress.progress(25, text=f"Retrieving SLA clauses (v{sla_version()})…")
                progress.progress(50, text=f"{model} is adjudicating against the SLA…")
                st.session_state[result_key] = adjudicate(case, model=model, top_k=top_k)
                progress.progress(90, text="Validating clause and evidence citations…")
                progress.progress(100, text="Done")
            except ProviderUnavailable as exc:
                st.session_state[result_key] = None
                st.error(str(exc))
            except Exception as exc:  # surfaced, never swallowed
                st.session_state[result_key] = None
                st.error(f"Adjudication failed: {exc}")
            finally:
                progress.empty()

        result = st.session_state.get(result_key)

        if result is None:
            st.info(
                "Run the adjudicator to produce a decision. The model receives the case "
                "evidence and the retrieved SLA clauses only — never the reference label."
            )
            return

        theme.verdict_banner(result.decision)

        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown('<div class="panel-key">Confidence</div>', unsafe_allow_html=True)
            st.progress(min(max(result.confidence, 0.0), 1.0))
            st.caption(f"{result.confidence:.0%} — model's self-reported calibration")
        with col_b:
            st.markdown('<div class="panel-key">Resolution action</div>', unsafe_allow_html=True)
            st.markdown(f"**{result.resolution_type.replace('_', ' ').title()}**")
            if result.refund_amount_inr is not None:
                st.markdown(f"Refund payable: **₹{result.refund_amount_inr:,.2f}**")

        st.markdown('<div class="panel-key">Primary SLA clause</div>', unsafe_allow_html=True)
        st.markdown(theme.chip(result.primary_clause_id), unsafe_allow_html=True)

        clauses = load_clauses()
        if result.primary_clause_id in clauses:
            with st.expander(f"Read {result.primary_clause_id}"):
                st.markdown(clauses[result.primary_clause_id].text)

        st.markdown('<div class="panel-key">Supporting clauses</div>', unsafe_allow_html=True)
        st.markdown(theme.chips(result.supporting_clause_ids), unsafe_allow_html=True)

        st.markdown('<div class="panel-key">Evidence relied upon</div>', unsafe_allow_html=True)
        st.markdown(theme.chips(result.evidence_ids_used, "chip-ev"), unsafe_allow_html=True)

        st.markdown('<div class="panel-key">Rationale</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="rationale">{theme.esc(result.rationale)}</div>',
            unsafe_allow_html=True,
        )

        if result.warnings:
            st.warning("Validation notes: " + "; ".join(result.warnings))

        st.markdown(
            f'<div class="meta-line">{theme.esc(result.model)} · SLA v{result.sla_version} · '
            f"{result.latency_seconds}s · {result.usage.get('input_tokens', 0):,} in / "
            f"{result.usage.get('output_tokens', 0):,} out tokens · "
            f"{len(result.retrieved_clause_ids)} clauses in context</div>",
            unsafe_allow_html=True,
        )

        with st.expander("View AI output / technical details"):
            st.markdown("**Validated structured response**")
            st.json(result.to_dict())
            st.markdown("**Raw model output**")
            st.code(result.raw_response, language="json")
