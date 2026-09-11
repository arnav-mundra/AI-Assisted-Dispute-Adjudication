"""Evaluation view — research/debugging only.

This is the only page that reads the frozen reference labels, which keeps the
live adjudication view free of the answer.
"""

import time

import pandas as pd
import streamlit as st

from app.ui import theme
from src.evidence_extraction.case_loader import get_ground_truth, load_cases
from src.llm import provider_for_model
from src.reasoning_engine.adjudicator import adjudicate


def render(model: str, top_k: int) -> None:
    theme.page_header(
        "Evaluation",
        "Runs the adjudicator across the 10-case pilot set and compares each decision with "
        "the frozen human reference label. Research view — the reference labels shown here "
        "are never sent to the model and never appear in the adjudication workspace.",
    )

    cases = load_cases()

    try:
        provider = provider_for_model(model)
        ready = provider.is_available()
        note = f"{provider.label} · {provider.status()}"
    except KeyError:
        ready = False
        note = f"No provider serves '{model}'"

    controls = st.columns([1, 1, 2])
    with controls[0]:
        run = st.button(
            f"Run all {len(cases)} cases", type="primary", use_container_width=True,
            disabled=not ready,
        )
    with controls[1]:
        delay = st.number_input(
            "Pause between cases (s)", min_value=0.0, max_value=15.0, value=1.0, step=0.5,
            help="Free-tier providers throttle rapid sequential calls.",
        )
    with controls[2]:
        st.caption(f"Model: `{model}` · {note}")

    if not ready:
        st.error(f"This model cannot run: {note}. Choose another model in the sidebar.")

    key = f"eval::{model}"

    if run:
        results = []
        progress = st.progress(0.0, text="Starting…")

        for index, case in enumerate(cases):
            case_id = case["case_id"]
            progress.progress(index / len(cases), text=f"Adjudicating {case_id}…")
            label = get_ground_truth(case_id)

            try:
                result = adjudicate(case, model=model, top_k=top_k)
                decision = result.decision
                confidence = result.confidence
                warnings = result.warnings
                primary = result.primary_clause_id
                latency = result.latency_seconds
            except Exception as exc:  # a failed case must not lose the run
                decision, confidence, warnings = "ERROR", 0.0, [str(exc)[:160]]
                primary, latency = "—", 0.0

            results.append(
                {
                    "Case": case_id,
                    "Type": "Damaged" if case["dispute_type"] == "DAMAGED_GOODS" else "COD",
                    "AI Decision": decision,
                    "Ground Truth": label["decision"] if label else "—",
                    "Match": "match" if label and label["decision"] == decision else "differs",
                    "AI Primary Clause": primary,
                    "Reference Clauses": ", ".join(label["governing_clause_ids"]) if label else "—",
                    "Confidence": round(confidence, 2),
                    "Latency (s)": latency,
                    "Notes": "; ".join(warnings) if warnings else "",
                }
            )

            if index < len(cases) - 1 and delay:
                time.sleep(delay)

        progress.progress(1.0, text="Complete")
        progress.empty()
        st.session_state[key] = results

    results = st.session_state.get(key)

    if not results:
        st.info(
            "No evaluation run yet for this model. Running all 10 cases makes 10 live "
            "model calls."
        )
        return

    matches = sum(1 for row in results if row["Match"] == "match")
    errors = sum(1 for row in results if row["AI Decision"] == "ERROR")

    theme.section_label("Aggregate")
    metrics = st.columns(4)
    metrics[0].metric(
        "Decision accuracy", f"{matches / len(results):.0%}", f"{matches}/{len(results)}"
    )
    metrics[1].metric("Cases run", len(results))
    metrics[2].metric("Failed calls", errors)
    metrics[3].metric(
        "Mean latency",
        f"{sum(row['Latency (s)'] for row in results) / len(results):.1f}s",
    )

    theme.section_label("Per-case comparison")
    st.dataframe(pd.DataFrame(results), use_container_width=True, hide_index=True)

    divergent = [row for row in results if row["Match"] == "differs"]
    if divergent:
        theme.section_label("Divergences")
        for row in divergent:
            st.markdown(
                f"**{row['Case']}** — system said **{row['AI Decision']}** "
                f"(primary {row['AI Primary Clause']}), reference says "
                f"**{row['Ground Truth']}** (clauses {row['Reference Clauses']})."
            )
        st.caption(
            "Divergence is a research signal, not necessarily an error: where the SLA leaves "
            "a consequence unstated, a defensible reading may differ from the reference label."
        )
