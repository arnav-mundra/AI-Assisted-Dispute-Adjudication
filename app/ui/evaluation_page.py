"""Evaluation — the only view that reads reference labels.

Runs are produced by `src.evaluation.experiment` (from here or the command
line), saved under results/runs/, and compared side by side against the
majority-class and random baselines.
"""

from typing import Any, Dict, List

import altair as alt
import pandas as pd
import streamlit as st

from app.ui import theme
from app.ui.settings import Settings
from src.clause_matching.clause_retrieval import dense_available, governing_recall
from src.evaluation.datasets import DATASETS, available_datasets, load_dataset
from src.evaluation.experiment import list_runs, run_experiment

PERCENT_METRICS = [
    ("decision_accuracy", "Decision accuracy"),
    ("macro_f1", "Macro-F1"),
    ("escalation_recall", "Escalation recall"),
    ("clause_f1", "Clause F1"),
    ("primary_clause_accuracy", "Primary clause correct"),
    ("refund_accuracy", "Refund correct"),
    ("evidence_recall", "Evidence recall"),
    ("grounding_issue_rate", "Grounding violations"),
]
DECISIONS = ["APPROVE", "REJECT", "ESCALATE"]


def _pct(value: Any) -> str:
    return "—" if value is None else f"{value:.0%}"


def _latest_per_label(runs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen, out = set(), []
    for run in runs:
        if run["label"] not in seen:
            seen.add(run["label"])
            out.append(run)
    return out


def render(settings: Settings) -> None:
    theme.page_header(
        "Evaluation",
        "Every configuration is run over a labelled dataset and scored against the reference rulings: the "
        "decision, the clauses cited, the refund amount and the evidence relied on.",
    )

    names = available_datasets()
    dataset = st.radio("Dataset", names, format_func=lambda n: DATASETS[n]["label"], horizontal=True,
                       key="ev_dataset")
    theme.note(theme.esc(DATASETS[dataset]["note"]))

    # ---- run controls --------------------------------------------------
    c1, c2, c3 = st.columns([1, 1.3, 1.6])
    with c1:
        if st.button("Run the rules engine", width="stretch"):
            run_experiment(engine="rules", dataset=dataset, retrieval=settings.retrieval, top_k=settings.top_k)
            st.rerun()
    with c2:
        label = f"Run {settings.model} ({settings.prompt_style.replace('_', '-')})"
        if st.button(label, type="primary", width="stretch", disabled=not settings.llm_ready):
            bar = st.progress(0.0, text="Starting…")
            run_experiment(engine="llm", model=settings.model, prompt_style=settings.prompt_style,
                           retrieval=settings.retrieval, top_k=settings.top_k, dataset=dataset, delay=1.0,
                           progress=lambda i, n, cid: bar.progress(i / n, text=f"Adjudicating {cid}…"))
            bar.empty()
            st.rerun()
    with c3:
        if not settings.llm_ready:
            st.caption("LLM runs need a provider key. They can also be made from a terminal with "
                       "`python -m src.evaluation.experiment --engine llm --all-styles` and appear here.")

    runs = list_runs(dataset)
    if not runs:
        theme.note("No runs saved for this dataset yet. Run the rules engine above to create the first one.")
        _retrieval_panel()
        return

    options = {f"{r['label']}  ({r['created_at'][5:16].replace('T', ' ')})": r for r in runs}
    defaults = [k for k, r in options.items() if r in _latest_per_label(runs)][:5]
    picked = st.multiselect("Runs to compare", list(options), default=defaults, key=f"ev_runs::{dataset}")
    chosen = [options[k] for k in picked]
    if not chosen:
        return

    _, labels = load_dataset(dataset)
    base = chosen[0]["baselines"]

    # ---- comparison table ------------------------------------------------
    theme.subhead("How each configuration scores")
    rows = []
    for run in chosen:
        m = run["metrics"]
        rows.append({"Configuration": run["label"], **{name: _pct(m.get(key)) for key, name in PERCENT_METRICS},
                     "Brier": f"{m.get('brier_score', 0):.3f}", "Cases": str(m.get("n"))})
    rows.append({"Configuration": f"Baseline: always {base['majority_class']['label'].lower()}",
                 "Decision accuracy": _pct(base["majority_class"]["decision_accuracy"]),
                 "Escalation recall": _pct(base["majority_class"]["escalation_recall"])})
    rows.append({"Configuration": "Baseline: random", "Decision accuracy": _pct(1 / 3),
                 "Escalation recall": _pct(1 / 3)})
    st.dataframe(pd.DataFrame(rows).fillna("—"), hide_index=True, width="stretch")

    chart_rows = []
    for run in chosen:
        for key, name in PERCENT_METRICS[:5]:
            chart_rows.append({"run": run["label"], "metric": name, "value": run["metrics"].get(key) or 0})
    order = [name for _, name in PERCENT_METRICS[:5]]
    bars = alt.Chart(pd.DataFrame(chart_rows)).mark_bar(cornerRadiusTopLeft=2, cornerRadiusTopRight=2).encode(
        x=alt.X("metric:N", sort=order, title=None, axis=alt.Axis(labelAngle=0, labelLimit=160)),
        xOffset=alt.XOffset("run:N"),
        y=alt.Y("value:Q", title=None, axis=alt.Axis(format="%"), scale=alt.Scale(domain=[0, 1])),
        color=alt.Color("run:N", title=None, legend=alt.Legend(orient="top"),
                        scale=alt.Scale(range=["#16233F", "#2747A6", "#6B86C9", "#A8671A", "#9AA6BF"])),
        tooltip=["run", "metric", alt.Tooltip("value:Q", format=".0%")])
    majority = alt.Chart(pd.DataFrame([{"metric": "Decision accuracy",
                                        "value": base["majority_class"]["decision_accuracy"]}])).mark_tick(
        color="#9B2335", thickness=2, size=60).encode(x=alt.X("metric:N", sort=order), y="value:Q",
                                                       tooltip=[alt.Tooltip("value:Q", format=".0%",
                                                                            title="majority baseline")])
    st.altair_chart((bars + majority).properties(height=280), width="stretch")
    st.caption("The red tick on decision accuracy marks the majority-class baseline.")

    # ---- one run in depth -------------------------------------------------
    theme.subhead("One run in detail")
    focus_key = st.selectbox("Run", picked, key=f"ev_focus::{dataset}")
    run = options[focus_key]
    m = run["metrics"]
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Decisions correct", f"{sum(1 for r in m['per_case'] if r['correct'])}/{m['n']}")
    k2.metric("Escalation recall", _pct(m.get("escalation_recall")))
    k3.metric("Refunds correct", _pct(m.get("refund_accuracy")))
    k4.metric("Agrees with rules engine", _pct(m.get("cross_check_agreement")) if run["config"]["engine"] == "llm"
              else "n/a")

    left, right = st.columns([1, 1.6], gap="large")
    with left:
        cells = [{"reference": g, "predicted": p, "count": (m["confusion"].get(g) or {}).get(p, 0)}
                 for g in DECISIONS for p in DECISIONS + (["UNPARSED"] if any(
                     "UNPARSED" in (m["confusion"].get(x) or {}) for x in DECISIONS) else [])]
        heat = alt.Chart(pd.DataFrame(cells)).encode(
            x=alt.X("predicted:N", sort=DECISIONS, title="Predicted", axis=alt.Axis(labelAngle=0, orient="top")),
            y=alt.Y("reference:N", sort=DECISIONS, title="Reference"))
        st.altair_chart(
            heat.mark_rect().encode(color=alt.Color("count:Q", legend=None,
                                                    scale=alt.Scale(range=["#F6F8FB", "#2747A6"])))
            .properties(height=260) + heat.mark_text(fontSize=15, fontWeight="bold").encode(
                text="count:Q", color=alt.condition("datum.count > 1", alt.value("white"), alt.value("#16233F"))),
            width="stretch")
    with right:
        table = pd.DataFrame([{
            "Case": r["case_id"], "Predicted": r["predicted"], "Reference": r["reference"],
            "Correct": "✓" if r["correct"] else "✗",
            "Primary clause": r["primary_clause"],
            "Clauses missed": ", ".join(sorted(set(r["reference_clauses"]) - set(r["predicted_clauses"]))) or "",
            "Refund": "" if r["refund_ok"] is None else ("✓" if r["refund_ok"] else
                                                       f"✗ {r['predicted_refund']} vs {r['reference_refund']}"),
            "Confidence": f"{r['confidence']:.2f}",
        } for r in m["per_case"]])
        st.dataframe(table, hide_index=True, width="stretch", height=min(35 * len(table) + 38, 460))

    wrong = [r for r in m["per_case"] if not r["correct"]]
    label_by_id = {l["case_id"]: l for l in labels}
    if wrong:
        theme.subhead("Where it diverged from the reference")
        preds = {p["case_id"]: p for p in run["predictions"]}
        for r in wrong:
            with st.expander(f"{r['case_id']}: predicted {r['predicted']}, reference {r['reference']}"):
                st.markdown("**System rationale**")
                theme.md(f'<div class="rationale" style="border:none">'
                         f'{theme.linkify_clauses(preds[r["case_id"]].get("rationale", ""))}</div>')
                st.markdown("**Reference rationale**")
                theme.md(f'<div class="rationale" style="border:none">'
                         f'{theme.linkify_clauses(label_by_id[r["case_id"]]["rationale"])}</div>')
    if run.get("failures"):
        st.warning("Cases that failed to run: " + ", ".join(f["case_id"] for f in run["failures"]))

    _retrieval_panel()


@st.cache_data(show_spinner=False)
def _recall_curve() -> pd.DataFrame:
    rows = []
    variants = [("lexical", False, "Lexical"), ("bm25", False, "BM25"), ("hybrid", False, "Hybrid rank fusion"),
                ("hybrid", True, "Hybrid + fact triggers")]
    if dense_available():
        variants.insert(2, ("dense", False, "Dense embeddings"))
    for method, facts, name in variants:
        for k in range(1, 15):
            r = governing_recall(method, k, use_facts=facts)
            rows.append({"retriever": name, "k": k, "recall": r["recall"], "context": r["mean_context_size"]})
    return pd.DataFrame(rows)


def _retrieval_panel() -> None:
    theme.subhead("Clause retrieval: share of governing clauses that reach the model")
    st.caption("Pilot set. k is the number of ranked clauses; priority rules, eligibility gates and "
               "cross-references are added on top of every method.")
    data = _recall_curve()
    line = (alt.Chart(data).mark_line(point=True, strokeWidth=2)
            .encode(x=alt.X("k:Q", title="Ranked clauses (k)", axis=alt.Axis(format="d", tickMinStep=1)),
                    y=alt.Y("recall:Q", title="Governing-clause recall", axis=alt.Axis(format="%"),
                            scale=alt.Scale(domain=[0.4, 1.02])),
                    color=alt.Color("retriever:N", title=None, legend=alt.Legend(orient="top"),
                                    scale=alt.Scale(domain=["Lexical", "BM25", "Dense embeddings",
                                                            "Hybrid rank fusion", "Hybrid + fact triggers"],
                                                    range=["#9AA6BF", "#6B86C9", "#A8671A", "#5A6B91", "#16233F"])),
                    tooltip=["retriever", "k", alt.Tooltip("recall:Q", format=".1%"),
                             alt.Tooltip("context:Q", format=".1f", title="clauses in context")])
            .properties(height=300))
    st.altair_chart(line, width="stretch")
