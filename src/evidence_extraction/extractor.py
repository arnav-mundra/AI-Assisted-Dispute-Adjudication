"""Phase 2 — evidence extraction.

Reads a case's raw evidence (customer chat/email text, agent statements, PoD
photo descriptions, delivery and reconciliation logs) and turns it into a set
of typed, source-linked facts that the SLA cares about:

    * when the item was delivered and when the claim was first raised,
      and therefore whether the reporting window was met (SLA-DG-01/02, SLA-COD-01)
    * what the PoD photo shows — damaged, intact, or unusable (SLA-DG-02/05/06, SLA-PRI-01)
    * whether the customer's damage description is specific (SLA-DG-04c)
    * whether unboxing or damage-photo evidence exists (SLA-DG-03/04)
    * hub exceptions and agent statements that corroborate or contest damage
    * COD amounts: invoice total, amount the customer says was taken,
      reconciliation status and amount, agent-stated amount (SLA-COD-03..09)

Every fact carries the evidence IDs it was read from, so the UI and the
prompt can show *where* each fact came from, and a downstream reviewer can
check it.

The extractor is deterministic and rule-based (regex + lexicons with negation
handling). It never sees the ground-truth label and contains no case IDs.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional

from src.evidence_extraction.case_loader import evidence_items

HIGH_VALUE_THRESHOLD_INR = 5000.0          # SLA-DG-03
DG_DEFAULT_WINDOW_H = 48.0                 # SLA-DG-01
DG_EXTENDED_WINDOW_H = 7 * 24.0            # SLA-DG-02
COD_WINDOW_H = 24.0                        # SLA-COD-01
COD_ROUNDING_TOLERANCE_INR = 10.0          # SLA-COD-07

# ---------------------------------------------------------------------------
# Lexicons
# ---------------------------------------------------------------------------

PACKAGE_DAMAGE = re.compile(
    r"\b(crush(?:ed|ing)?|torn|tear(?:s|ing)?|dent(?:s|ed)?|wet|damp|soak(?:ed|ing)?|"
    r"stain(?:s|ed|ing)?|sagg(?:ing|ed)|leak(?:ing|ed)?|punctur(?:e|ed)|crumpled|"
    r"damaged|broken open|ripped)\b",
    re.I,
)
PACKAGE_INTACT = re.compile(
    r"\b(intact|sealed|undamaged|unbroken|square|good condition|normal condition|"
    r"looked (?:fine|normal)|in normal condition)\b",
    re.I,
)
PRODUCT_DAMAGE = re.compile(
    r"\b(crack(?:ed|s)?|chip(?:ped|s)?|broken|break|snapped|split|shatter(?:ed)?|"
    r"dent(?:ed)?|scratch(?:ed|es)?|leak(?:ing|ed)?|bent|damaged|not working|dead pixels?|"
    r"stopped working|not charging|flicker(?:s|ing)?|torn|ripped|smashed|squashed|"
    r"does not (?:work|click|turn on|switch on)|won't (?:work|turn on)|will not hold)\b",
    re.I,
)
DAMAGE_LOCATION = re.compile(
    r"\b(rim|corner|base|side|hinge|neck|button|housing|top|bottom|left|right|edge|"
    r"screen|handle|lid|cup|arm|dial|panel|front|back|strap|seam|bottle|carafe|body|"
    r"display|lens|cord|cable|plug)\b",
    re.I,
)
UNBOXING = re.compile(r"\bunbox(?:ing|ed)?\b", re.I)
UNBOXING_ABSENT = re.compile(
    r"(?:did ?n[o']?t|do ?n[o']?t|don't|didn't|no|without|wasn't|was not)\b[^.]{0,40}?"
    r"\b(?:unbox(?:ing)?|recording|record)",
    re.I,
)
NEGATION_SPAN = re.compile(
    r"\b(?:no|not|never|without|nothing|none)\b[^.;:!?]*",
    re.I,
)
UNUSABLE_QUALITY = {"blurry", "poor", "unusable", "dark", "low", "low-light"}
UNUSABLE_NOTE = re.compile(r"\b(not usable|unusable|blurr?y|cannot be assessed|illegible)\b", re.I)
SYSTEM_FAILURE = re.compile(r"\b(outage|system failure|not written|not recorded|down)\b", re.I)
UNVERIFIABLE = re.compile(
    r"\b(no verifiable|not verifiable|unverifiable|no (?:capture )?metadata|cannot be verified)\b",
    re.I,
)
AGENT_UNRESPONSIVE = re.compile(r"\b(has not responded|did not respond|no response|unreachable)\b", re.I)
EXCEPTION_SCAN = re.compile(r"\bexception\b", re.I)
PRIOR_CLAIMS = re.compile(r"(\d+)\s+prior damaged-goods claim", re.I)

AMOUNT = re.compile(
    r"(?<![\w\-./])(?:₹|rs\.?\s?|inr\s?)?(\d{1,3}(?:,\d{3})+|\d+)(?:\.\d{1,2})?(?![\w\-%])",
    re.I,
)
NUMBER_WORDS = r"(?:one|two|three|four|five|six|seven|eight|nine|ten)"
INVOICE_BEFORE = re.compile(r"(invoice|order total|bill|mrp|price|total is|total of|amount due)[^0-9]{0,18}$", re.I)
DIFFERENCE_AFTER = re.compile(r"^\s*(?:rupees?|rs\.?|inr)?\s*(?:difference|more|extra|excess|less|change|short|back)\b", re.I)
DENOMINATION_AFTER = re.compile(r"^\s*(?:-?\s*rupees?)?[\s-]*(?:notes?|coins?)\b", re.I)
DENOMINATION_BEFORE = re.compile(rf"\b{NUMBER_WORDS}\s*$", re.I)
COLLECT_VERB_BEFORE = re.compile(
    r"\b(took|taken|collected|charged|paid|gave|handed|asked for|demanded|deducted|received)\b[^.0-9]{0,25}$",
    re.I,
)
COLLECT_VERB_AFTER = re.compile(r"^\s*(?:rupees?|rs\.?)?\s*(?:was|were)\s+(?:taken|collected|charged|paid)", re.I)
MANUAL_CLAIM_MARKER = re.compile(r"Amount stated by customer as collected:\s*₹?([\d,]+(?:\.\d+)?)", re.I)
AGENT_AMOUNT = re.compile(
    r"\b(remitted|deposited|collected(?: exactly)?|gave me|took|received)\s+(?:₹|rs\.?\s?)?(\d{1,3}(?:,\d{3})+|\d+)",
    re.I,
)


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class Fact:
    key: str
    label: str
    value: Any
    sources: List[str] = field(default_factory=list)
    detail: str = ""

    def display_value(self) -> str:
        v = self.value
        if v is None:
            return "—"
        if isinstance(v, bool):
            return "yes" if v else "no"
        if isinstance(v, float):
            if self.key.endswith("_inr"):
                return f"−₹{abs(v):,.2f}" if v < 0 else f"₹{v:,.2f}"
            return f"{v:,.1f}"
        return str(v)


@dataclass
class CaseFacts:
    case_id: str
    dispute_type: str
    facts: Dict[str, Fact] = field(default_factory=dict)

    def add(self, key: str, label: str, value: Any, sources: Iterable[str] = (), detail: str = "") -> None:
        self.facts[key] = Fact(key, label, value, sorted(set(s for s in sources if s)), detail)

    def get(self, key: str, default: Any = None) -> Any:
        fact = self.facts.get(key)
        return default if fact is None else fact.value

    def sources(self, *keys: str) -> List[str]:
        found: List[str] = []
        for key in keys:
            fact = self.facts.get(key)
            if fact:
                found.extend(fact.sources)
        return sorted(set(found))

    def rows(self) -> List[Dict[str, Any]]:
        return [
            {
                "fact": fact.label,
                "value": fact.display_value(),
                "sources": ", ".join(fact.sources) or "—",
                "detail": fact.detail,
            }
            for fact in self.facts.values()
        ]

    def to_dict(self) -> Dict[str, Any]:
        return {
            key: {"value": fact.value, "sources": fact.sources, "detail": fact.detail}
            for key, fact in self.facts.items()
        }

    def to_prompt_block(self) -> str:
        lines = []
        for fact in self.facts.values():
            source = f"  [from {', '.join(fact.sources)}]" if fact.sources else ""
            detail = f" — {fact.detail}" if fact.detail else ""
            lines.append(f"- {fact.label}: {fact.display_value()}{detail}{source}")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _ts(value: Optional[str]) -> Optional[datetime]:
    try:
        return datetime.fromisoformat(value) if value else None
    except (TypeError, ValueError):
        return None


def strip_negated(text: str) -> str:
    """Remove negated spans ('no dents, tears or staining') before matching damage terms."""
    return NEGATION_SPAN.sub(" ", text or "")


def _text_of(item: Dict[str, Any]) -> str:
    return " ".join(
        str(item.get(key) or "")
        for key in ("text", "photo_description", "note", "reliability_note")
    )


def _num(raw: str) -> float:
    return float(raw.replace(",", ""))


def classify_package(description: str) -> str:
    """DAMAGED | INTACT | UNKNOWN from a free-text package/photo description."""
    if PACKAGE_DAMAGE.search(strip_negated(description)):
        return "DAMAGED"
    if PACKAGE_INTACT.search(description) or re.search(r"\bno (?:dents|crushing|damage)", description, re.I):
        return "INTACT"
    return "UNKNOWN"


def claimed_amount(text: str, invoice_total: Optional[float]) -> Optional[float]:
    """The amount the customer says was collected, read from their own words."""
    marker = MANUAL_CLAIM_MARKER.search(text or "")
    if marker:
        return _num(marker.group(1))

    candidates: List[float] = []
    for match in AMOUNT.finditer(text or ""):
        value = _num(match.group(1))
        if value < 10:
            continue
        before = text[max(0, match.start() - 40):match.start()]
        after = text[match.end():match.end() + 25]

        if DENOMINATION_AFTER.search(after) or DENOMINATION_BEFORE.search(before):
            continue          # "two 1000-rupee notes", "one 500"
        if INVOICE_BEFORE.search(before):
            continue          # "invoice is 1800"
        if DIFFERENCE_AFTER.search(after):
            continue          # "the 200 rupees difference", "150 rupees more"
        if invoice_total and value < 0.5 * invoice_total:
            continue          # a difference, not a collected amount
        if COLLECT_VERB_BEFORE.search(before) or COLLECT_VERB_AFTER.search(after):
            candidates.append(value)

    return max(candidates) if candidates else None


def agent_amount(text: str) -> Optional[float]:
    """Amount the agent says they collected/remitted. 'remitted' beats 'collected'."""
    found: Dict[str, float] = {}
    for verb, raw in AGENT_AMOUNT.findall(text or ""):
        found.setdefault(verb.lower().split()[0], _num(raw))
    for verb in ("remitted", "deposited", "collected", "took", "received", "gave"):
        if verb in found:
            return found[verb]
    return None


# ---------------------------------------------------------------------------
# Extraction
# ---------------------------------------------------------------------------

def extract_facts(case: Dict[str, Any]) -> CaseFacts:
    dispute = case.get("dispute_type", "")
    facts = CaseFacts(case_id=case.get("case_id", ""), dispute_type=dispute)
    items = evidence_items(case)
    order = case.get("order", {})

    customer = [i for i in items if i.get("_section") == "customer_evidence"]
    agents = [i for i in items if i.get("_section") == "agent_evidence"]
    pods = [i for i in items if i.get("type") == "POD"]
    logs = [i for i in items if i.get("type") == "DELIVERY_LOG"]
    recons = [i for i in items if i.get("type") == "RECONCILIATION_LOG"]

    # -- Timing -------------------------------------------------------------
    pod = pods[0] if pods else None
    pod_ts = _ts(pod.get("timestamp_ist")) if pod else None
    claims = sorted(
        (i for i in customer if _ts(i.get("timestamp_ist"))),
        key=lambda i: _ts(i["timestamp_ist"]),
    )
    first_claim = claims[0] if claims else None
    claim_ts = _ts(first_claim["timestamp_ist"]) if first_claim else None
    hours = round((claim_ts - pod_ts).total_seconds() / 3600, 2) if pod_ts and claim_ts else None

    facts.add("pod_time", "Delivered (PoD timestamp)",
              pod_ts.strftime("%d %b %Y %H:%M IST") if pod_ts else None,
              [pod["evidence_id"]] if pod else [])
    facts.add("claim_time", "First customer report",
              claim_ts.strftime("%d %b %Y %H:%M IST") if claim_ts else None,
              [first_claim["evidence_id"]] if first_claim else [])
    facts.add("hours_to_report", "Hours from PoD to first report", hours,
              [s for s in (pod and pod["evidence_id"], first_claim and first_claim["evidence_id"])],
              "PoD → first customer message, IST (SLA-GEN-03)")

    order_value = float(order.get("order_value_inr") or 0.0)
    facts.add("order_value_inr", "Order value", order_value, [], f"order {order.get('order_id', '')}")

    if dispute == "DAMAGED_GOODS":
        _damaged_goods(facts, order_value, hours, pod, customer, agents, logs)
    elif dispute == "COD_MISMATCH":
        _cod(facts, order, hours, customer, agents, recons)

    return facts


def _damaged_goods(facts, order_value, hours, pod, customer, agents, logs) -> None:
    # PoD condition (SLA-DEF-01) and whether the record can be trusted (SLA-PRI-01)
    pod_condition, pod_detail = "UNKNOWN", "no PoD on file"
    pod_ids: List[str] = []
    if pod:
        pod_ids = [pod["evidence_id"]]
        quality = str(pod.get("image_quality") or "").lower()
        unusable = quality in UNUSABLE_QUALITY or bool(UNUSABLE_NOTE.search(pod.get("reliability_note") or ""))
        observed = classify_package(pod.get("photo_description") or "")
        if unusable:
            pod_condition = "UNUSABLE"
            pod_detail = f"image quality '{quality or 'flagged'}' — package condition cannot be assessed"
        else:
            pod_condition = observed
            pod_detail = (pod.get("photo_description") or "")[:140]
    facts.add("pod_condition", "PoD photo shows", pod_condition, pod_ids, pod_detail)

    # Hub exceptions in delivery logs
    hub_damage, hub_ids, hub_detail = False, [], ""
    prior = 0
    for log in logs:
        note = log.get("note") or ""
        if EXCEPTION_SCAN.search(strip_negated(note)) and PACKAGE_DAMAGE.search(strip_negated(note)):
            hub_damage, hub_ids, hub_detail = True, hub_ids + [log["evidence_id"]], note[:160]
        m = PRIOR_CLAIMS.search(note)
        if m:
            prior = max(prior, int(m.group(1)))
    facts.add("hub_damage_exception", "Hub/route damage exception logged", hub_damage, hub_ids, hub_detail)
    facts.add("prior_claims_90d", "Prior damaged-goods claims (90 days)", prior,
              [l["evidence_id"] for l in logs if PRIOR_CLAIMS.search(l.get("note") or "")])

    # Agent statements
    agent_ack, agent_intact, agent_ids = False, False, []
    for agent in agents:
        body = agent.get("text") or ""
        if PACKAGE_DAMAGE.search(strip_negated(body)):
            agent_ack = True
            agent_ids.append(agent["evidence_id"])
        elif PACKAGE_INTACT.search(body):
            agent_intact = True
            agent_ids.append(agent["evidence_id"])
    facts.add("agent_acknowledges_damage", "Agent acknowledges package damage", agent_ack,
              agent_ids if agent_ack else [])
    facts.add("agent_asserts_intact", "Agent asserts package intact", agent_intact,
              agent_ids if agent_intact else [])

    # Customer narrative and media
    narrative = " ".join(i.get("text") or "" for i in customer if i.get("type") != "PHOTO")
    narrative_ids = [i["evidence_id"] for i in customer if i.get("type") != "PHOTO"]
    clean = strip_negated(narrative)
    damage_terms = sorted({m.group(0).lower() for m in PRODUCT_DAMAGE.finditer(clean)})
    locations = sorted({m.group(0).lower() for m in DAMAGE_LOCATION.finditer(narrative)})
    specific = bool(damage_terms) and bool(locations)
    facts.add("customer_reports_damage", "Customer reports product damage", bool(damage_terms),
              narrative_ids, ", ".join(damage_terms))
    facts.add("damage_description_specific", "Damage description is specific (type + location)",
              specific, narrative_ids,
              f"type: {', '.join(damage_terms) or '—'}; location: {', '.join(locations) or '—'}")

    customer_pkg = classify_package(narrative) == "DAMAGED"
    facts.add("customer_reports_package_damage", "Customer reports outer package damage",
              customer_pkg, narrative_ids if customer_pkg else [])

    photos = [i for i in customer if i.get("type") in {"PHOTO", "VIDEO"}]
    unboxing_items = [p for p in photos if UNBOXING.search(_text_of(p))]
    damage_photos = [
        p for p in photos
        if PRODUCT_DAMAGE.search(strip_negated(p.get("photo_description") or ""))
        or PACKAGE_DAMAGE.search(strip_negated(p.get("photo_description") or ""))
    ]
    unboxing_absent = bool(UNBOXING_ABSENT.search(narrative)) and not unboxing_items
    facts.add("unboxing_evidence", "Unboxing photo/video provided", bool(unboxing_items),
              [p["evidence_id"] for p in unboxing_items],
              "customer states none was recorded" if unboxing_absent else "")
    facts.add("damage_photo", "Post-delivery photo of the damage", bool(damage_photos),
              [p["evidence_id"] for p in damage_photos])

    # Derived
    high_value = order_value >= HIGH_VALUE_THRESHOLD_INR
    facts.add("high_value", f"High-value order (≥ ₹{HIGH_VALUE_THRESHOLD_INR:,.0f})", high_value, [],
              "SLA-DG-03 requires unboxing evidence" if high_value else "")

    pod_doubt = pod_condition == "UNUSABLE"
    corroborated = hub_damage or agent_ack
    facts.add("pod_record_doubted", "Documented reason to doubt PoD (SLA-PRI-01)", pod_doubt, pod_ids,
              "PoD image flagged unusable" if pod_doubt else "")
    facts.add("independent_damage_corroboration", "Independent corroboration of transit damage",
              corroborated, hub_ids + (agent_ids if agent_ack else []),
              "hub exception and/or agent statement" if corroborated else "")

    window = DG_EXTENDED_WINDOW_H if pod_condition == "DAMAGED" else DG_DEFAULT_WINDOW_H
    window_basis = "7-day exception (PoD shows damage, SLA-DG-02)" if window > 48 else "48-hour default (SLA-DG-01)"
    facts.add("reporting_window_h", "Applicable reporting window (hours)", window, pod_ids, window_basis)
    facts.add("within_window", "Reported within window",
              None if hours is None else hours <= window,
              facts.sources("hours_to_report"),
              "" if hours is None else f"{hours:.1f} h vs {window:.0f} h")


def _cod(facts, order, hours, customer, agents, recons) -> None:
    total = order.get("order_total_cod_inr")
    total = float(total) if total is not None else float(order.get("order_value_inr") or 0.0)
    facts.add("invoice_total_inr", "Order total (invoice)", total, [], "COD amount due per invoice")

    narrative_items = [i for i in customer if i.get("type") != "PHOTO"]
    narrative = " ".join(i.get("text") or "" for i in narrative_items)
    claimed = claimed_amount(narrative, total)
    facts.add("claimed_collected_inr", "Amount customer says was collected", claimed,
              [i["evidence_id"] for i in narrative_items],
              "" if claimed is not None else "customer does not state a specific amount")
    if claimed is not None:
        facts.add("claimed_excess_inr", "Excess claimed by customer", round(claimed - total, 2),
                  [i["evidence_id"] for i in narrative_items])

    recon = recons[0] if recons else None
    status = str(recon.get("status") or "").upper() if recon else "MISSING"
    recon_amount = recon.get("amount_collected_inr") if recon else None
    available = status == "RECORDED" and recon_amount is not None
    recon_ids = [recon["evidence_id"]] if recon else []
    outage = bool(recon and SYSTEM_FAILURE.search(recon.get("note") or ""))
    facts.add("recon_status", "Reconciliation log", "RECORDED" if available else "UNAVAILABLE", recon_ids,
              "system outage reported" if outage else "")
    facts.add("recon_amount_inr", "Amount recorded in reconciliation", float(recon_amount) if available else None,
              recon_ids)

    if available:
        diff = round(float(recon_amount) - total, 2)
        direction = "HIGHER" if diff > 0 else "LOWER" if diff < 0 else "MATCH"
        facts.add("recon_vs_invoice", "Reconciliation vs invoice", direction, recon_ids,
                  f"{'+' if diff > 0 else '−' if diff < 0 else ''}₹{abs(diff):,.2f}")
        facts.add("recon_excess_inr", "Reconciliation − invoice", diff, recon_ids, "SLA-COD-04 formula")
    else:
        facts.add("recon_vs_invoice", "Reconciliation vs invoice", "NO_RECORD", recon_ids)

    # Agent
    agent_amt, agent_ids, unresponsive = None, [], False
    for agent in agents:
        body = agent.get("text") or ""
        if AGENT_UNRESPONSIVE.search(body):
            unresponsive = True
            agent_ids.append(agent["evidence_id"])
        amount = agent_amount(body)
        if amount is not None:
            agent_amt = amount
            agent_ids.append(agent["evidence_id"])
    facts.add("agent_stated_amount_inr", "Amount agent says was collected/remitted", agent_amt, agent_ids,
              "agent did not respond" if unresponsive else "")

    # Customer corroboration (SLA-COD-03)
    photos = [i for i in customer if i.get("type") in {"PHOTO", "SCREENSHOT", "VIDEO"}]
    verifiable = [p for p in photos if not UNVERIFIABLE.search(_text_of(p))]
    facts.add("customer_corroboration", "Customer corroborating evidence (photo/screenshot)", bool(photos),
              [p["evidence_id"] for p in photos])
    facts.add("corroboration_verifiable", "Corroborating evidence is verifiable",
              bool(verifiable) if photos else None, [p["evidence_id"] for p in photos],
              "no capture metadata / no link to the handover" if photos and not verifiable else "")

    # Independent sources saying the correct amount was paid (SLA-COD-09)
    confirming = []
    if available and abs(float(recon_amount) - total) < 0.01:
        confirming += recon_ids
    if agent_amt is not None and abs(agent_amt - total) < 0.01:
        confirming += [a["evidence_id"] for a in agents]
    facts.add("sources_confirming_correct_payment", "Independent sources showing correct amount paid",
              len(set(confirming)), confirming)

    facts.add("reporting_window_h", "Applicable reporting window (hours)", COD_WINDOW_H, [], "SLA-COD-01")
    facts.add("within_window", "Reported within window",
              None if hours is None else hours <= COD_WINDOW_H,
              facts.sources("hours_to_report"),
              "" if hours is None else f"{hours:.1f} h vs {COD_WINDOW_H:.0f} h")
