"""Visual system and presentation components.

Direction: a case docket. Ink-navy text on cool paper, ruled-line blue for
structure, citation blue for clause references, and three ruling colours.
Clause text and rationales are set in a serif so legal text reads as such.
The one loud element is the verdict stamp; everything else stays quiet.
"""

from __future__ import annotations

import html
from datetime import datetime, timedelta
from typing import Any, Dict, Iterable, List, Optional, Sequence

import streamlit as st

INK = "#16233F"
INK_SOFT = "#4A5672"
INK_FAINT = "#8590A8"
PAPER = "#F6F8FB"
RULE = "#D5DDEA"
CITE = "#2747A6"

RULING = {
    "APPROVE": {"ink": "#1E7A4E", "wash": "#E8F3EC", "word": "Approved",
                "sub": "Claim upheld under the SLA"},
    "REJECT": {"ink": "#9B2335", "wash": "#F7E9EB", "word": "Rejected",
               "sub": "Claim not upheld under the SLA"},
    "ESCALATE": {"ink": "#A8671A", "wash": "#F8EFE2", "word": "Escalated",
                 "sub": "Sent to a human reviewer"},
}

RESOLUTION_WORDS = {
    "REPLACEMENT_DEFAULT": "Free replacement",
    "REFUND": "Refund",
    "PARTIAL_REFUND": "Partial refund",
    "NO_CUSTOMER_ACTION": "No customer action",
    "NO_STANDARD_RESOLUTION": "No standard resolution",
    "MANUAL_REVIEW": "Manual review",
}

SECTION_NAMES = {
    "customer_evidence": "Customer",
    "agent_evidence": "Delivery agent",
    "delivery_evidence": "Delivery records",
}

CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&display=swap');

html, body, [class*="css"], .stMarkdown, .stText, button, input, textarea, select {{
  font-family: 'IBM Plex Sans', system-ui, sans-serif;
}}
.stApp {{ background: {PAPER}; color: {INK}; }}
.block-container {{ padding-top: 3.6rem; padding-bottom: 4rem; max-width: 1360px; }}
#MainMenu, footer {{ visibility: hidden; }}
h1, h2, h3 {{ color: {INK}; letter-spacing: -0.01em; }}

/* Sidebar */
section[data-testid="stSidebar"] {{ background: {INK}; min-width: 300px; }}
section[data-testid="stSidebar"] * {{ color: #E6EBF4; }}
section[data-testid="stSidebar"] label p {{ color: #A9B4CB !important; font-size: .84rem; font-weight: 500; }}
/* BaseWeb select (Streamlit < 1.5x) and react-aria ComboBox (newer) */
section[data-testid="stSidebar"] div[data-baseweb="select"] > div,
section[data-testid="stSidebar"] [data-testid="stSelectbox"] [role="group"] {{
  background: #FFFFFF !important; border-color: #33456B; }}
section[data-testid="stSidebar"] div[data-baseweb="select"] * {{ color: {INK} !important; }}
section[data-testid="stSidebar"] div[data-baseweb="select"] svg {{ fill: {INK_SOFT} !important; }}
section[data-testid="stSidebar"] [data-testid="stSelectbox"] input,
section[data-testid="stSidebar"] [data-testid="stSelectbox"] div[value] {{
  color: {INK} !important; -webkit-text-fill-color: {INK} !important; }}
section[data-testid="stSidebar"] [data-testid="stSelectbox"] button svg,
section[data-testid="stSidebar"] [data-testid="stSelectbox"] input ~ button {{ color: {INK_SOFT} !important; }}
section[data-testid="stSidebar"] hr {{ border-color: #2A3A5C; }}
.brand {{ padding: 2px 0 16px 0; margin-bottom: 14px; border-bottom: 1px solid #2A3A5C; }}
.brand-name {{ font-size: 1.12rem; font-weight: 700; color: #FFFFFF; line-height: 1.2; }}
.brand-sub {{ font-size: .8rem; color: #A9B4CB; margin-top: 2px; }}
.side-note {{ font-size: .78rem; color: #A9B4CB; line-height: 1.45; margin-top: 4px; }}
.status {{ display:flex; align-items:center; gap:8px; font-size:.82rem; padding:3px 0; }}
.status i {{ width:8px; height:8px; border-radius:50%; display:inline-block; }}

/* Headings */
.page-title {{ font-size: 2.05rem; font-weight: 700; color: {INK}; letter-spacing: -0.02em;
  line-height: 1.15; margin: 0 0 .35rem 0; }}
.page-lede {{ color: {INK_SOFT}; font-size: 1rem; line-height: 1.55; max-width: 72ch; margin-bottom: 1.2rem; }}
.subhead {{ font-size: 1.02rem; font-weight: 600; color: {INK}; margin: 1.4rem 0 .5rem 0; }}
.muted {{ color: {INK_FAINT}; font-size: .84rem; }}

.stage {{ display:flex; align-items:baseline; gap:12px; margin: 1.8rem 0 .7rem 0;
  padding-bottom: .45rem; border-bottom: 1px solid {RULE}; }}
.stage-n {{ font-size: .9rem; font-weight: 700; color: {CITE}; min-width: 1.2rem; }}
.stage-t {{ font-size: 1.12rem; font-weight: 600; color: {INK}; }}
.stage-note {{ color: {INK_FAINT}; font-size: .85rem; margin-left: auto; text-align:right; }}

/* Case header */
.case-head {{ display:flex; flex-wrap:wrap; gap: 28px; align-items:flex-end;
  padding: 0 0 14px 0; border-bottom: 2px solid {INK}; margin-bottom: 14px; }}
.case-id {{ font-size: 2.1rem; font-weight: 700; letter-spacing: -0.02em; color: {INK}; line-height:1; }}
.case-kv {{ display:flex; flex-direction:column; gap:2px; }}
.case-k {{ font-size: .76rem; color: {INK_FAINT}; }}
.case-v {{ font-size: .98rem; font-weight: 600; color: {INK}; font-variant-numeric: tabular-nums; }}

/* Timeline */
.tl {{ position: relative; height: 112px; margin: 6px 6px 4px 6px; }}
.tl-axis {{ position:absolute; left:0; right:0; top:52px; height:2px; background:{RULE}; }}
.tl-window {{ position:absolute; top:46px; height:14px; border-radius:3px;
  background: repeating-linear-gradient(135deg, #DCE5F3 0 6px, #EAF0F8 6px 12px);
  border: 1px solid #B9C7DE; }}
.tl-mark {{ position:absolute; top:38px; transform: translateX(-50%); text-align:center; width: 150px; }}
.tl-mark.up {{ top:0; display:flex; flex-direction:column-reverse; }}
.tl-mark.up .tl-dot {{ margin: 6px auto 0 auto; }}
.tl-dot {{ width:12px; height:12px; border-radius:50%; margin: 8px auto 6px auto; border: 2px solid {PAPER}; }}
.tl-lab {{ font-size:.78rem; font-weight:600; color:{INK}; line-height:1.2; }}
.tl-sub {{ font-size:.72rem; color:{INK_FAINT}; font-variant-numeric: tabular-nums; }}
.tl-top {{ position:absolute; top:0; transform: translateX(-50%); font-size:.74rem; color:{INK_SOFT};
  white-space:nowrap; }}
.tl-caption {{ font-size: .88rem; color: {INK_SOFT}; margin: 2px 0 6px 0; }}

/* Evidence */
.ev {{ background:#FFFFFF; border:1px solid {RULE}; border-radius:6px; padding: 12px 15px;
  margin-bottom: 8px; }}
.ev.cited {{ border-color: {CITE}; box-shadow: inset 3px 0 0 {CITE}; }}
.ev-head {{ display:flex; gap:10px; align-items:baseline; margin-bottom:4px; flex-wrap: wrap; }}
.ev-id {{ font-weight:700; font-size:.84rem; color:{INK}; }}
.ev-type {{ font-size:.76rem; color:{INK_FAINT}; }}
.ev-when {{ font-size:.76rem; color:{INK_FAINT}; margin-left:auto; font-variant-numeric: tabular-nums; }}
.ev-cited {{ font-size:.72rem; font-weight:600; color:{CITE}; }}
.ev-body {{ font-size:.9rem; line-height:1.55; color:{INK}; }}
.ev-img {{ font-size:.84rem; color:{INK_SOFT}; margin-top:6px; padding-left:10px; border-left:2px solid {RULE}; }}
.ev-meta {{ font-size:.78rem; color:{INK_SOFT}; margin-top:6px; }}
.ev-flag {{ font-size:.8rem; color:#7A4A0E; background:#FBF3E6; padding:6px 10px; border-radius:4px; margin-top:8px; }}

/* Facts */
table.facts {{ width:100%; border-collapse: collapse; font-size:.88rem; background:#FFFFFF;
  border:1px solid {RULE}; border-radius:6px; overflow:hidden; }}
table.facts td {{ padding: 8px 12px; border-bottom: 1px solid #E7ECF4; vertical-align: top; }}
table.facts tr:last-child td {{ border-bottom: none; }}
table.facts td.fk {{ color:{INK}; width: 50%; }}
table.facts td.fk small {{ display:block; color:{INK_FAINT}; font-size:.78rem; line-height:1.4; margin-top:2px; }}
table.facts td.fv {{ font-weight:600; color:{INK}; font-variant-numeric: tabular-nums; width: 24%; }}
table.facts td.fs {{ color:{CITE}; font-size:.78rem; width: 26%; line-height:1.5; }}
.fv-yes {{ color:#1E7A4E !important; }} .fv-no {{ color:#9B2335 !important; }}

/* Clauses */
.cl {{ background:#FFFFFF; border:1px solid {RULE}; border-radius:6px; padding: 10px 14px; margin-bottom:7px; }}
.cl.cited {{ border-color:{CITE}; }}
.cl-head {{ display:flex; gap:10px; align-items:center; }}
.cl-id {{ font-weight:700; color:{CITE}; font-size:.88rem; }}
.cl-why {{ font-size:.78rem; color:{INK_FAINT}; }}
.cl-bar {{ margin-left:auto; width:90px; height:5px; background:#E7ECF4; border-radius:3px; overflow:hidden; }}
.cl-bar span {{ display:block; height:100%; background:{CITE}; }}
.cl-text {{ font-family:'Source Serif 4', Georgia, serif; font-size:.92rem; line-height:1.6; color:{INK};
  margin-top:6px; }}
.cl-tag {{ font-size:.72rem; font-weight:600; color:#FFFFFF; background:{CITE}; border-radius:3px; padding:1px 6px; }}

/* Ruling */
.ruling {{ background:#FFFFFF; border:1px solid {RULE}; border-radius:8px; padding: 22px 24px 18px 24px; }}
.stamp {{ display:inline-block; transform: rotate(-3deg); border: 3px double currentColor; border-radius: 6px;
  padding: 8px 18px 6px 18px; margin: 4px 0 14px 2px; }}
.stamp-word {{ font-size: 2.2rem; font-weight: 700; letter-spacing: .02em; line-height: 1; }}
.stamp-cite {{ font-size: .86rem; font-weight: 600; margin-top: 4px; }}
.ruling-sub {{ font-size:.92rem; color:{INK_SOFT}; margin-bottom: 12px; }}
.ruling-grid {{ display:grid; grid-template-columns: repeat(3, minmax(0,1fr)); gap: 14px; margin: 6px 0 14px 0; }}
.rk {{ font-size:.76rem; color:{INK_FAINT}; }}
.rv {{ font-size:1rem; font-weight:600; color:{INK}; font-variant-numeric: tabular-nums; }}
.conf {{ height:6px; background:#E7ECF4; border-radius:3px; margin-top:6px; overflow:hidden; }}
.conf span {{ display:block; height:100%; }}
.rationale {{ font-family:'Source Serif 4', Georgia, serif; font-size:1rem; line-height:1.7; color:{INK};
  border-top: 1px solid {RULE}; padding-top: 12px; margin-top: 4px; }}
.cite {{ color:{CITE}; font-weight:600; }}
.chips span {{ display:inline-block; font-size:.78rem; font-weight:600; padding:2px 8px; border-radius:4px;
  margin: 2px 4px 2px 0; background:#EEF2FA; color:{CITE}; border:1px solid #CFD9EE; }}
.chips span.ev {{ background:#F1F3F6; color:{INK}; border-color:{RULE}; padding:2px 8px; box-shadow:none; }}
.check {{ font-size:.86rem; padding: 9px 12px; border-radius: 6px; margin-top: 12px; }}

/* Trace */
.trace {{ counter-reset: step; margin: 0; padding: 0; list-style: none; }}
.trace li {{ position: relative; padding: 8px 0 8px 34px; border-bottom: 1px solid #E7ECF4; font-size:.88rem; }}
.trace li:before {{ counter-increment: step; content: counter(step); position:absolute; left:0; top:8px;
  width:22px; height:22px; border-radius:50%; background:#EEF2FA; color:{CITE}; font-size:.75rem;
  font-weight:700; display:flex; align-items:center; justify-content:center; }}
.trace li.stop:before {{ background:{CITE}; color:#FFFFFF; }}
.trace .tq {{ color:{INK}; }} .trace .ta {{ color:{INK_SOFT}; }} .trace .tc {{ color:{CITE}; font-weight:600; }}

/* Overview */
.pipe {{ display:grid; grid-template-columns: repeat(5, minmax(0,1fr)); gap: 0; margin: 10px 0 8px 0;
  border:1px solid {RULE}; border-radius:8px; overflow:hidden; background:#FFFFFF; }}
.pipe div {{ padding: 14px 14px 16px 14px; border-right: 1px solid {RULE}; }}
.pipe div:last-child {{ border-right: none; }}
.pipe b {{ display:block; color:{CITE}; font-size:.82rem; margin-bottom:4px; }}
.pipe strong {{ display:block; font-size:.98rem; color:{INK}; margin-bottom:4px; }}
.pipe span {{ font-size:.82rem; color:{INK_SOFT}; line-height:1.45; }}
.big {{ font-size: 2.4rem; font-weight: 700; color:{INK}; letter-spacing:-.02em; line-height:1; font-variant-numeric: tabular-nums; }}
.big-l {{ font-size: .85rem; color:{INK_SOFT}; margin-top: 4px; }}
.note {{ font-size:.86rem; color:{INK_SOFT}; background:#FFFFFF; border:1px solid {RULE}; border-left:3px solid {CITE};
  padding: 10px 14px; border-radius: 4px; line-height:1.5; }}

.main [data-baseweb="input"], .main [data-baseweb="textarea"], .main [data-baseweb="base-input"],
section.main [data-testid="stTextArea"] textarea, [data-testid="stMain"] [data-baseweb="input"],
[data-testid="stMain"] [data-baseweb="textarea"], [data-testid="stMain"] [data-baseweb="select"] > div,
[data-testid="stMain"] [data-testid="stSelectbox"] [role="group"] {{
  background:#FFFFFF !important; border-color:{RULE} !important; }}
[data-testid="stMain"] [data-testid="stSelectbox"] input {{
  color:{INK} !important; -webkit-text-fill-color:{INK} !important; }}
[data-testid="stMain"] [data-testid="stSelectbox"] [role="group"] button {{ color:{INK_SOFT} !important; }}
[data-testid="stMain"] [data-baseweb="input"] input, [data-testid="stMain"] textarea {{ background:#FFFFFF !important; }}
div[data-testid="stMetricValue"] {{ font-size: 1.5rem; color:{INK}; }}
div[data-testid="stMetricLabel"] p {{ color:{INK_SOFT}; }}
button[kind="primary"] {{ background:{INK} !important; border-color:{INK} !important; }}
button[kind="primary"]:hover {{ background:#22345C !important; }}
button[kind="primary"]:disabled {{ background:#E3E8F1 !important; border-color:{RULE} !important; }}
button[kind="primary"]:disabled p {{ color:{INK_FAINT} !important; }}
.stTabs [data-baseweb="tab"] p {{ font-weight: 500; }}
@media (max-width: 900px) {{
  .ruling-grid {{ grid-template-columns: 1fr 1fr; }}
  .pipe {{ grid-template-columns: 1fr; }} .pipe div {{ border-right:none; border-bottom:1px solid {RULE}; }}
  .tl-mark {{ width: 100px; }}
}}
</style>
"""


def inject_css() -> None:
    st.markdown(CSS, unsafe_allow_html=True)


def esc(value: Any) -> str:
    return html.escape(str(value if value is not None else ""))


def md(markup: str) -> None:
    st.markdown(markup, unsafe_allow_html=True)


# ---------------------------------------------------------------- chrome

def brand() -> None:
    md('<div class="brand"><div class="brand-name">Dispute Adjudicator</div>'
       '<div class="brand-sub">SLA-grounded rulings for D2C delivery disputes</div></div>')


def status(label: str, ok: bool, note: str = "") -> None:
    colour = "#4CC38A" if ok else "#5D6B88"
    md(f'<div class="status"><i style="background:{colour}"></i>{esc(label)}'
       f'<span style="margin-left:auto;color:#A9B4CB">{esc(note)}</span></div>')


def page_header(title: str, lede: str = "") -> None:
    md(f'<div class="page-title">{esc(title)}</div>')
    if lede:
        md(f'<div class="page-lede">{esc(lede)}</div>')


def stage(number: int, title: str, note: str = "") -> None:
    md(f'<div class="stage"><span class="stage-n">{number}</span><span class="stage-t">{esc(title)}</span>'
       f'<span class="stage-note">{esc(note)}</span></div>')


def subhead(text: str) -> None:
    md(f'<div class="subhead">{esc(text)}</div>')


def note(text: str) -> None:
    md(f'<div class="note">{text}</div>')


# ---------------------------------------------------------------- helpers

def parse_ts(value: Optional[str]) -> Optional[datetime]:
    try:
        return datetime.fromisoformat(value) if value else None
    except (TypeError, ValueError):
        return None


def when(value: Optional[str]) -> str:
    moment = parse_ts(value)
    return moment.strftime("%d %b, %H:%M") if moment else ""


def money(value: Optional[float]) -> str:
    return "—" if value is None else f"₹{value:,.0f}" if float(value).is_integer() else f"₹{value:,.2f}"


def linkify_clauses(text: str) -> str:
    import re
    return re.sub(r"(SLA-(?:GEN|DEF|DG|COD|PRI)-\d{2})", r'<span class="cite">\1</span>', esc(text))


def chips(values: Iterable[str], kind: str = "") -> str:
    values = [v for v in values if v]
    if not values:
        return '<span class="muted">none</span>'
    return '<div class="chips">' + "".join(f'<span class="{kind}">{esc(v)}</span>' for v in values) + "</div>"


# ---------------------------------------------------------------- case

def case_header(case: Dict[str, Any]) -> None:
    order = case.get("order", {})
    kind = "Damaged goods" if case.get("dispute_type") == "DAMAGED_GOODS" else "COD mismatch"
    cells = [
        ("Dispute", kind),
        ("Product", order.get("product_name") or "—"),
        ("Order value", money(order.get("order_value_inr"))),
    ]
    if order.get("order_total_cod_inr") is not None:
        cells.append(("COD due", money(order.get("order_total_cod_inr"))))
    if order.get("city"):
        cells.append(("City", order["city"]))
    body = "".join(f'<div class="case-kv"><span class="case-k">{esc(k)}</span>'
                   f'<span class="case-v">{esc(v)}</span></div>' for k, v in cells)
    md(f'<div class="case-head"><div class="case-id">{esc(case.get("case_id"))}</div>{body}</div>')


def timeline(case: Dict[str, Any], facts: Dict[str, Any]) -> None:
    """Pickup → delivery → first report, against the applicable reporting window."""
    from src.evidence_extraction.case_loader import evidence_items

    items = evidence_items(case)
    pod = next((i for i in items if i.get("type") == "POD"), None)
    pod_ts = parse_ts(pod.get("timestamp_ist")) if pod else None
    customer = [parse_ts(i.get("timestamp_ist")) for i in items if i.get("_section") == "customer_evidence"]
    customer = [t for t in customer if t]
    claim_ts = min(customer) if customer else None
    pickup_ts = None
    for item in items:
        if item.get("pickup_timestamp_ist"):
            pickup_ts = parse_ts(item["pickup_timestamp_ist"])
    window_h = (facts.get("reporting_window_h") or {}).get("value")
    hours = (facts.get("hours_to_report") or {}).get("value")

    if not pod_ts or not claim_ts or not window_h:
        return

    deadline = pod_ts + timedelta(hours=window_h)
    start = pickup_ts or pod_ts - timedelta(hours=12)
    end = max(claim_ts, deadline)
    span = (end - start).total_seconds() or 1.0
    pad = 0.07

    def x(moment: datetime) -> float:
        return round(100 * (pad + (1 - 2 * pad) * (moment - start).total_seconds() / span), 2)

    within = claim_ts <= deadline
    claim_colour = RULING["APPROVE"]["ink"] if within else RULING["REJECT"]["ink"]
    window_label = f"{window_h / 24:.0f}-day window" if window_h > 48 else f"{window_h:.0f}-hour window"

    parts = ['<div class="tl"><div class="tl-axis"></div>',
             f'<div class="tl-window" style="left:{x(pod_ts)}%;width:{x(deadline) - x(pod_ts)}%"></div>']

    def mark(moment: datetime, label: str, colour: str, up: bool = False) -> None:
        parts.append(f'<div class="tl-mark{" up" if up else ""}" style="left:{x(moment)}%">'
                     f'<div class="tl-dot" style="background:{colour}"></div>'
                     f'<div><div class="tl-lab">{esc(label)}</div>'
                     f'<div class="tl-sub">{esc(moment.strftime("%d %b %H:%M"))}</div></div></div>')

    if pickup_ts:
        mark(pickup_ts, "Picked up", INK_FAINT)
    mark(pod_ts, "Delivered", INK)
    mark(deadline, f"{window_label[0].upper()}{window_label[1:]} closes", INK_FAINT)
    mark(claim_ts, "Customer reports", claim_colour, up=True)
    parts.append("</div>")
    md("".join(parts))
    verdict = "inside" if within else "outside"
    md(f'<div class="tl-caption">Reported <b>{hours:.1f} hours</b> after delivery, <b style="color:{claim_colour}">'
       f'{verdict}</b> the {esc(window_label)}.</div>')


def evidence_card(item: Dict[str, Any], cited: Sequence[str] = ()) -> str:
    is_cited = item.get("evidence_id") in set(cited)
    body = item.get("text") or item.get("note") or ""
    meta = []
    if item.get("status"):
        meta.append(f"Status {item['status'].lower()}")
    if item.get("amount_collected_inr") is not None:
        meta.append(f"Amount recorded {money(item['amount_collected_inr'])}")
    if item.get("image_quality"):
        meta.append(f"Image {item['image_quality']}")
    if item.get("otp_confirmed") is not None:
        meta.append("OTP confirmed" if item["otp_confirmed"] else "No OTP")
    if item.get("pickup_timestamp_ist"):
        meta.append(f"Picked up {when(item['pickup_timestamp_ist'])}")

    out = [f'<div class="ev{" cited" if is_cited else ""}"><div class="ev-head">',
           f'<span class="ev-id">{esc(item.get("evidence_id"))}</span>',
           f'<span class="ev-type">{esc(str(item.get("type", "")).replace("_", " ").capitalize())}</span>',
           '<span class="ev-cited">relied on</span>' if is_cited else "",
           f'<span class="ev-when">{esc(when(item.get("timestamp_ist")))}</span></div>']
    if body:
        out.append(f'<div class="ev-body">{esc(body)}</div>')
    if item.get("photo_description"):
        out.append(f'<div class="ev-img">Photo shows: {esc(item["photo_description"])}</div>')
    if meta:
        out.append(f'<div class="ev-meta">{esc("; ".join(meta))}</div>')
    if item.get("reliability_note"):
        out.append(f'<div class="ev-flag">{esc(item["reliability_note"])}</div>')
    out.append("</div>")
    return "".join(out)


def facts_table(rows: List[Dict[str, Any]]) -> None:
    body = []
    for row in rows:
        value = row["value"]
        cls = "fv-yes" if value == "yes" else "fv-no" if value == "no" else ""
        detail = f'<small>{esc(row["detail"])}</small>' if row["detail"] else ""
        sources = "<br>".join(esc(x.strip()) for x in row["sources"].split(",")) if row["sources"] != "—" else ""
        body.append(f'<tr><td class="fk">{esc(row["fact"])}{detail}</td><td class="fv {cls}">{esc(value)}</td>'
                    f'<td class="fs">{sources}</td></tr>')
    md(f'<table class="facts">{"".join(body)}</table>')


def clause_body(text: str) -> str:
    import re
    text = re.sub(r"^\*\*SLA-[A-Z]+-\d+\.\*\*\s*", "", text.strip())
    return re.sub(r"\*\*?([^*]+)\*\*?", r"\1", text).strip()


def clause_card(item,cited_ids: Sequence[str], max_score: float, primary: str = "") -> str:
    cid = item.clause_id
    width = 0 if not max_score else max(4, int(100 * item.score / max_score))
    tag = '<span class="cl-tag">governing</span>' if cid == primary else (
        '<span class="cl-tag" style="background:#5A6B91">cited</span>' if cid in cited_ids else "")
    text = clause_body(item.clause.text)
    return (f'<div class="cl{" cited" if cid in cited_ids else ""}"><div class="cl-head">'
            f'<span class="cl-id">{esc(cid)}</span>{tag}<span class="cl-why">{esc(item.reason)}</span>'
            f'<span class="cl-bar"><span style="width:{width}%"></span></span></div>'
            f'<div class="cl-text">{esc(text[:420])}{"…" if len(text) > 420 else ""}</div></div>')


def ruling_card(result, show_engine: bool = True) -> None:
    style = RULING.get(result.decision, {"ink": INK_SOFT, "wash": "#EEF0F4", "word": result.decision,
                                         "sub": "Unrecognised decision"})
    resolution = RESOLUTION_WORDS.get(result.resolution_type, result.resolution_type or "—")
    refund = money(result.refund_amount_inr) if result.refund_amount_inr else "—"
    conf = max(0.0, min(1.0, float(result.confidence or 0)))
    engine = "Rules engine" if result.engine == "rules" else result.model
    md(f'''<div class="ruling">
<div class="stamp" style="color:{style["ink"]};background:{style["wash"]}">
  <div class="stamp-word">{esc(style["word"])}</div>
  <div class="stamp-cite">under {esc(result.primary_clause_id or "—")}</div></div>
<div class="ruling-sub">{esc(style["sub"])}{f" — decided by {esc(engine)}" if show_engine else ""}</div>
<div class="ruling-grid">
  <div><div class="rk">Resolution</div><div class="rv">{esc(resolution)}</div></div>
  <div><div class="rk">Refund</div><div class="rv">{esc(refund)}</div></div>
  <div><div class="rk">Confidence</div><div class="rv">{conf:.0%}</div>
    <div class="conf"><span style="width:{conf * 100:.0f}%;background:{style["ink"]}"></span></div></div>
</div>
<div class="rk">Also relied on</div>{chips(result.supporting_clause_ids)}
<div class="rk" style="margin-top:8px">Evidence cited</div>{chips(result.evidence_ids_used, "ev")}
<div class="rationale">{linkify_clauses(result.rationale)}</div>
</div>''')


def cross_check(result) -> None:
    check = result.cross_check or {}
    if not check:
        return
    if check.get("agrees"):
        md(f'<div class="check" style="background:#E8F3EC;color:#1E5C3C">The rules engine reaches the same '
           f'decision ({esc(check.get("rules_decision"))} under {esc(check.get("rules_primary_clause_id"))}).</div>')
    else:
        md(f'<div class="check" style="background:#F8EFE2;color:#7A4A0E"><b>Needs a second look.</b> The rules '
           f'engine decides {esc(check.get("rules_decision"))} under {esc(check.get("rules_primary_clause_id"))}; '
           f'the model decided {esc(result.decision)}. Disagreements are where human review adds the most.</div>')


def trace_list(trace: List[Dict[str, str]]) -> None:
    if not trace:
        md('<div class="muted">No reasoning steps recorded.</div>')
        return
    rows = []
    for step in trace:
        clause = f'<span class="tc">{esc(step.get("clause"))}</span> ' if step.get("clause") else ""
        stop = " stop" if step.get("outcome") == "stop" else ""
        rows.append(f'<li class="{stop}">{clause}<span class="tq">{esc(step.get("question"))}</span><br>'
                    f'<span class="ta">{esc(step.get("answer"))}</span></li>')
    md(f'<ol class="trace">{"".join(rows)}</ol>')


def big_number(value: str, label: str) -> None:
    md(f'<div class="big">{esc(value)}</div><div class="big-l">{esc(label)}</div>')


def mini_ruling(result, title: str) -> None:
    style = RULING.get(result.decision, {"ink": INK_SOFT, "wash": "#EEF0F4", "word": result.decision})
    refund = f", refund {money(result.refund_amount_inr)}" if result.refund_amount_inr else ""
    md(f'<div class="ruling" style="padding:16px 18px"><div class="rk">{esc(title)}</div>'
       f'<div class="stamp" style="color:{style["ink"]};background:{style["wash"]};margin:8px 0 8px 2px">'
       f'<div class="stamp-word" style="font-size:1.6rem">{esc(style["word"])}</div>'
       f'<div class="stamp-cite">under {esc(result.primary_clause_id)}</div></div>'
       f'<div class="muted">{esc(RESOLUTION_WORDS.get(result.resolution_type, result.resolution_type))}'
       f'{esc(refund)}</div></div>')
