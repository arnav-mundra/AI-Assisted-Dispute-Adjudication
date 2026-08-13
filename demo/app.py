"""
Bare-bones progress-check demo for AI-Assisted Dispute Adjudication.

WHAT THIS IS:
    A minimal Streamlit UI that lets you paste in a dispute case (chat/email
    evidence + structured delivery evidence) and get back an LLM-generated
    resolution, grounded in the full SLA document (docs/sla_policy.md).

WHAT THIS IS NOT:
    This is NOT the final pipeline. It skips the Evidence Extraction module
    (Phase 2) and the Clause-Matching/RAG module (Phase 3) by stuffing the
    entire SLA doc into the prompt directly (it's short enough to fit).
    Once Phases 2-3 are built, replace `load_sla_text()` and the prompt
    construction below with calls into src/evidence_extraction and
    src/clause_matching, and this UI will keep working unchanged.

RUN:
    cd d2c-dispute-adjudication
    pip install -r requirements.txt
    cp .env.example .env   # fill in OPENAI_API_KEY and/or ANTHROPIC_API_KEY
    streamlit run demo/app.py
"""

import json
import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parent.parent
SLA_PATH = ROOT / "docs" / "sla_policy.md"

st.set_page_config(page_title="D2C Dispute Adjudication — Demo", layout="wide")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

@st.cache_data
def load_sla_text() -> str:
    if not SLA_PATH.exists():
        return ""
    return SLA_PATH.read_text(encoding="utf-8")


def build_prompt(dispute_type: str, chat_evidence: str, structured_evidence: dict, sla_text: str) -> str:
    return f"""You are an SLA-grounded dispute adjudicator for a D2C e-commerce company.

You must resolve the dispute below using ONLY the SLA document provided. Every
resolution must cite the specific clause_id(s) relied upon (e.g., "SLA-DG-06").
If the evidence is genuinely insufficient or contradictory under the SLA, you
must say so explicitly and recommend escalation rather than forcing a decision.

--- SLA DOCUMENT ---
{sla_text}
--- END SLA DOCUMENT ---

--- DISPUTE CASE ---
Dispute type: {dispute_type}

Chat/email evidence (unstructured, customer-submitted):
{chat_evidence or "(none provided)"}

Structured evidence (delivery logs / order data):
{json.dumps(structured_evidence, indent=2)}
--- END DISPUTE CASE ---

Respond in this exact JSON format, nothing else:
{{
  "decision": "approve" | "reject" | "escalate",
  "cited_clauses": ["SLA-XX-NN", ...],
  "reasoning": "2-4 sentences explaining the decision by reference to the cited clauses and evidence",
  "resolution_action": "e.g. free replacement, refund amount, escalate to manual review",
  "confidence": "high" | "medium" | "low"
}}"""


def call_anthropic(prompt: str, model: str) -> str:
    import anthropic
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    resp = client.messages.create(
        model=model,
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}],
    )
    return "".join(block.text for block in resp.content if block.type == "text")


def call_openai(prompt: str, model: str) -> str:
    from openai import OpenAI
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    return resp.choices[0].message.content


# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------

st.title("D2C Dispute Adjudication — Progress-Check Demo")
st.caption(
    "Bare-bones demo. Skips Evidence Extraction (Phase 2) and Clause Matching "
    "(Phase 3) — the full SLA doc is passed directly to the reasoning model. "
    "For progress-check / professor demo purposes only."
)

sla_text = load_sla_text()
if not sla_text:
    st.error(f"Could not find SLA document at {SLA_PATH}. Run this from the repo root.")
    st.stop()

with st.expander("View SLA document being used"):
    st.markdown(sla_text)

st.divider()

col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Case Input")

    dispute_type = st.selectbox("Dispute type", ["Damaged Goods", "COD Mismatch"])

    chat_evidence = st.text_area(
        "Chat / email evidence (paste customer's message thread)",
        height=150,
        placeholder="Customer: My order arrived with a cracked screen...\nAgent: Can you share a photo?\n...",
    )

    st.markdown("**Structured evidence**")

    if dispute_type == "Damaged Goods":
        order_value = st.number_input("Order value (₹)", min_value=0, value=2500)
        pod_shows_damage = st.selectbox("PoD photo shows external package damage?", ["No", "Yes"])
        unboxing_evidence = st.selectbox("Unboxing photo/video provided?", ["No", "Yes"])
        hours_since_delivery = st.number_input("Hours since PoD timestamp", min_value=0, value=20)
        prior_claims_90d = st.number_input("Prior damaged-goods claims (last 90 days)", min_value=0, value=0)

        structured_evidence = {
            "order_value_inr": order_value,
            "pod_shows_external_damage": pod_shows_damage == "Yes",
            "unboxing_evidence_provided": unboxing_evidence == "Yes",
            "hours_since_pod": hours_since_delivery,
            "prior_damaged_goods_claims_90d": prior_claims_90d,
        }
    else:
        order_total = st.number_input("Order total per invoice (₹)", min_value=0, value=1200)
        amount_customer_claims_paid = st.number_input("Amount customer says they paid (₹)", min_value=0, value=1400)
        reconciliation_log_amount = st.number_input(
            "Delivery partner reconciliation log amount (₹, 0 = no log found)", min_value=0, value=1200
        )
        hours_since_delivery = st.number_input("Hours since PoD timestamp", min_value=0, value=10)

        structured_evidence = {
            "order_total_inr": order_total,
            "customer_claimed_amount_paid_inr": amount_customer_claims_paid,
            "reconciliation_log_amount_inr": reconciliation_log_amount if reconciliation_log_amount > 0 else None,
            "hours_since_pod": hours_since_delivery,
        }

    st.markdown("**Model**")
    provider = st.radio("Provider", ["Anthropic", "OpenAI"], horizontal=True)
    if provider == "Anthropic":
        model = st.selectbox("Model", ["claude-sonnet-4-6", "claude-opus-4-1"])
    else:
        model = st.selectbox("Model", ["gpt-4o-mini", "gpt-4o"])

    run = st.button("Run Adjudication", type="primary")

with col_right:
    st.subheader("Resolution Output")

    if run:
        api_key_present = (
            os.environ.get("ANTHROPIC_API_KEY") if provider == "Anthropic"
            else os.environ.get("OPENAI_API_KEY")
        )
        if not api_key_present:
            st.error(
                f"No API key found for {provider}. Set it in your .env file "
                f"(see .env.example) and restart the app."
            )
        else:
            with st.spinner("Reasoning against SLA document..."):
                prompt = build_prompt(dispute_type, chat_evidence, structured_evidence, sla_text)
                try:
                    raw = (
                        call_anthropic(prompt, model) if provider == "Anthropic"
                        else call_openai(prompt, model)
                    )
                    cleaned = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
                    result = json.loads(cleaned)

                    decision_color = {"approve": "green", "reject": "red", "escalate": "orange"}.get(
                        result.get("decision", ""), "gray"
                    )
                    st.markdown(f"### Decision: :{decision_color}[{result.get('decision', '?').upper()}]")
                    st.markdown(f"**Cited clauses:** {', '.join(result.get('cited_clauses', [])) or '(none)'}")
                    st.markdown(f"**Confidence:** {result.get('confidence', '?')}")
                    st.markdown("**Reasoning:**")
                    st.write(result.get("reasoning", ""))
                    st.markdown("**Resolution action:**")
                    st.write(result.get("resolution_action", ""))

                    with st.expander("Raw model output"):
                        st.code(raw)

                except json.JSONDecodeError:
                    st.warning("Model did not return valid JSON. Showing raw output:")
                    st.code(raw)
                except Exception as e:
                    st.error(f"Error calling {provider} API: {e}")
    else:
        st.info("Fill in the case details on the left and click **Run Adjudication**.")

st.divider()
st.caption(
    "Roadmap note: this demo will be superseded by the full pipeline output "
    "(Evidence Extraction -> Clause Matching -> Reasoning Engine -> Evaluation) "
    "in Phase 8. Ground-truth labels and baseline comparison are handled "
    "separately in src/evaluation, not in this demo."
)
