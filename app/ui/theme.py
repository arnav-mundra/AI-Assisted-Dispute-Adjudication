"""Shared styling and presentation components for the adjudication application."""

import html
from datetime import datetime
from typing import Any, Dict, Optional

import streamlit as st

DECISION_STYLES = {
    "APPROVE": ("#0f7b46", "#e9f7ef", "#b7e4c9", "Claim approved"),
    "REJECT": ("#b3261e", "#fdecea", "#f5c6c2", "Claim rejected"),
    "ESCALATE": ("#a4620a", "#fdf4e5", "#f3dcb3", "Escalated to manual review"),
}

SECTION_META = {
    "customer_evidence": ("Customer", "Chat, email and customer-supplied images"),
    "agent_evidence": ("Delivery agent", "Statements recorded by the partner helpdesk"),
    "delivery_evidence": ("Delivery / PoD", "Proof of delivery and route records"),
    "reconciliation": ("Reconciliation", "Delivery-partner cash reconciliation records"),
}

CSS = """
<style>
  .block-container {padding-top: 2rem; padding-bottom: 3rem; max-width: 1480px;}
  #MainMenu, footer {visibility: hidden;}

  section[data-testid="stSidebar"] {min-width: 320px; background: #0f172a;}
  section[data-testid="stSidebar"] * {color: #e2e8f0;}
  section[data-testid="stSidebar"] .stSelectbox label,
  section[data-testid="stSidebar"] .stSlider label {color: #94a3b8 !important;
      font-size: .74rem; text-transform: uppercase; letter-spacing: .06em; font-weight: 600;}
  section[data-testid="stSidebar"] div[data-baseweb="select"] > div {background:#1e293b;
      border-color:#334155; color:#e2e8f0;}
  /* Streamlit >=1.4x nests the selected value deeper; force it legible on the
     dark sidebar regardless of the internal markup. */
  section[data-testid="stSidebar"] div[data-baseweb="select"] * {color:#e2e8f0 !important;}
  section[data-testid="stSidebar"] div[data-baseweb="select"] svg {fill:#94a3b8 !important;}

  .brand {display:flex; align-items:center; gap:11px; padding: 4px 0 18px 0;
          border-bottom:1px solid #1e293b; margin-bottom:18px;}
  .brand-mark {width:38px; height:38px; border-radius:10px; flex:none;
               background:linear-gradient(135deg,#4f46e5,#0ea5e9); color:#fff;
               display:flex; align-items:center; justify-content:center;
               font-size:1.15rem; font-weight:700;}
  .brand-name {font-size:1.02rem; font-weight:680; line-height:1.15; color:#f8fafc;}
  .brand-sub {font-size:.72rem; color:#94a3b8; letter-spacing:.04em;}

  .status-row {display:flex; align-items:center; gap:9px; padding:5px 0; font-size:.82rem;}
  .dot {width:8px; height:8px; border-radius:50%; flex:none;}
  .dot-on {background:#22c55e; box-shadow:0 0 0 3px rgba(34,197,94,.18);}
  .dot-off {background:#475569;}
  .status-name {color:#e2e8f0; font-weight:550;}
  .status-note {color:#64748b; font-size:.74rem; margin-left:auto;}

  .page-title {font-size:1.95rem; font-weight:680; letter-spacing:-.022em;
               color:#0f172a; margin-bottom:.2rem;}
  .page-sub {color:#64748b; font-size:.94rem; max-width:900px; line-height:1.55;}

  .section-label {font-size:.74rem; font-weight:700; letter-spacing:.08em;
                  text-transform:uppercase; color:#64748b; margin:22px 0 10px 0;}

  .summary {border:1px solid #e2e8f0; border-radius:14px; padding:18px 22px;
            background:linear-gradient(180deg,#ffffff,#fbfcfe);
            box-shadow:0 1px 2px rgba(15,23,42,.04);}
  .summary-grid {display:flex; flex-wrap:wrap; gap:30px;}
  .summary-item {min-width:120px;}
  .summary-key {font-size:.7rem; text-transform:uppercase; letter-spacing:.07em;
                color:#94a3b8; font-weight:650; margin-bottom:3px;}
  .summary-val {font-size:1.02rem; color:#0f172a; font-weight:600;}
  .summary-val small {font-weight:450; color:#64748b; font-size:.82rem;}

  .chip {display:inline-block; padding:3px 11px; margin:2px 5px 2px 0; border-radius:999px;
         font-size:.76rem; font-weight:650;
         font-family:ui-monospace,SFMono-Regular,Menlo,monospace;
         background:#eef2ff; color:#3730a3; border:1px solid #c7d2fe;}
  .chip-ev {background:#f1f5f9; color:#334155; border-color:#cbd5e1;}
  .chip-soft {background:#ffffff; color:#475569; border-color:#e2e8f0;}

  .ev-card {border:1px solid #e2e8f0; border-left:3px solid #cbd5e1; border-radius:10px;
            padding:13px 16px; margin-bottom:9px; background:#fff;}
  .ev-head {display:flex; justify-content:space-between; align-items:baseline; gap:10px;
            margin-bottom:5px;}
  .ev-id {font-family:ui-monospace,SFMono-Regular,Menlo,monospace; font-size:.77rem;
          font-weight:700; color:#1e293b;}
  .ev-meta {font-size:.71rem; color:#94a3b8; text-transform:uppercase; letter-spacing:.04em;}
  .ev-body {font-size:.885rem; color:#1f2937; line-height:1.55;}
  .ev-extra {font-size:.8rem; color:#475569; margin-top:6px;}
  .ev-flag {font-size:.79rem; color:#9a3412; background:#fff7ed; border-left:3px solid #fb923c;
            padding:7px 11px; margin-top:8px; border-radius:5px;}

  .verdict {border-radius:16px; padding:24px 28px; margin-bottom:16px;}
  .verdict-label {font-size:.72rem; letter-spacing:.1em; text-transform:uppercase;
                  font-weight:700; opacity:.75;}
  .verdict-decision {font-size:2.35rem; font-weight:750; letter-spacing:-.03em; line-height:1.1;}
  .verdict-sub {font-size:.95rem; opacity:.85;}

  .panel {border:1px solid #e2e8f0; border-radius:12px; padding:16px 18px; background:#fff;
          height:100%;}
  .panel-key {font-size:.7rem; text-transform:uppercase; letter-spacing:.07em;
              color:#94a3b8; font-weight:650; margin-bottom:7px;}
  .rationale {background:#f8fafc; border:1px solid #e2e8f0; border-left:4px solid #6366f1;
              padding:16px 20px; border-radius:8px; font-size:.94rem; line-height:1.7;
              color:#0f172a;}
  .meta-line {color:#94a3b8; font-size:.77rem; margin-top:10px;
              font-family:ui-monospace,SFMono-Regular,Menlo,monospace;}
  div[data-testid="stMetricValue"] {font-size:1.3rem;}
</style>
"""


def inject_css() -> None:
    st.markdown(CSS, unsafe_allow_html=True)


def esc(value: Any) -> str:
    return html.escape(str(value if value is not None else ""))


def chip(text: Any, kind: str = "") -> str:
    return f'<span class="chip {kind}">{esc(text)}</span>'


def chips(values, kind: str = "") -> str:
    return "".join(chip(value, kind) for value in values) or '<span class="ev-meta">—</span>'


def brand() -> None:
    st.markdown(
        '<div class="brand">'
        '<div class="brand-mark">§</div>'
        '<div><div class="brand-name">AI Dispute Adjudicator</div>'
        '<div class="brand-sub">SLA-grounded resolution engine</div></div>'
        "</div>",
        unsafe_allow_html=True,
    )


def status_row(label: str, ok: bool, note: str = "") -> None:
    st.markdown(
        f'<div class="status-row"><span class="dot {"dot-on" if ok else "dot-off"}"></span>'
        f'<span class="status-name">{esc(label)}</span>'
        f'<span class="status-note">{esc(note)}</span></div>',
        unsafe_allow_html=True,
    )


def page_header(title: str, subtitle: str) -> None:
    st.markdown(f'<div class="page-title">{esc(title)}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-sub">{esc(subtitle)}</div>', unsafe_allow_html=True)


def section_label(text: str) -> None:
    st.markdown(f'<div class="section-label">{esc(text)}</div>', unsafe_allow_html=True)


def parse_ts(value: Optional[str]) -> Optional[datetime]:
    try:
        return datetime.fromisoformat(value) if value else None
    except (TypeError, ValueError):
        return None


def summary_card(items) -> None:
    cells = "".join(
        f'<div class="summary-item"><div class="summary-key">{esc(key)}</div>'
        f'<div class="summary-val">{value}</div></div>'
        for key, value in items
    )
    st.markdown(
        f'<div class="summary"><div class="summary-grid">{cells}</div></div>',
        unsafe_allow_html=True,
    )


def evidence_card(item: Dict[str, Any]) -> str:
    body = item.get("text") or item.get("note") or ""
    photo = item.get("photo_description")

    extra = []
    if item.get("status"):
        extra.append(f"status: {item['status']}")
    if item.get("amount_collected_inr") is not None:
        extra.append(f"amount recorded: ₹{item['amount_collected_inr']:,.2f}")
    if item.get("image_quality"):
        extra.append(f"image quality: {item['image_quality']}")
    if item.get("otp_confirmed") is not None:
        extra.append(f"OTP confirmed: {'yes' if item['otp_confirmed'] else 'no'}")

    parts = [
        '<div class="ev-card">',
        '<div class="ev-head">',
        f'<span class="ev-id">{esc(item.get("evidence_id"))}</span>',
        f'<span class="ev-meta">{esc(item.get("type"))} &nbsp;·&nbsp; '
        f'{esc(item.get("timestamp_ist"))}</span>',
        "</div>",
    ]
    if body:
        parts.append(f'<div class="ev-body">{esc(body)}</div>')
    if photo:
        parts.append(
            f'<div class="ev-extra"><em>Image content:</em> {esc(photo)}</div>'
        )
    if extra:
        parts.append(f'<div class="ev-extra">{esc(" · ".join(extra))}</div>')
    if item.get("reliability_note"):
        parts.append(
            f'<div class="ev-flag"><strong>Reliability flag.</strong> '
            f'{esc(item["reliability_note"])}</div>'
        )
    parts.append("</div>")
    return "".join(parts)


def verdict_banner(decision: str) -> None:
    color, background, border, subtitle = DECISION_STYLES.get(
        decision, ("#475569", "#f1f5f9", "#cbd5e1", "Unrecognised decision")
    )
    st.markdown(
        f'<div class="verdict" style="background:{background};border:1px solid {border};">'
        f'<div class="verdict-label" style="color:{color};">Adjudication result</div>'
        f'<div class="verdict-decision" style="color:{color};">{esc(decision)}</div>'
        f'<div class="verdict-sub" style="color:{color};">{esc(subtitle)}</div>'
        "</div>",
        unsafe_allow_html=True,
    )
