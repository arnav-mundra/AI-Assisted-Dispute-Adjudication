"""Build the PIC 2026 camera-ready (Paper 325) from a copy of the submitted Word file.

    <repo>/venv/Scripts/python paper/pic2026/build_camera_ready.py   then   paper/pic2026/to_pdf.ps1

Reads submitted_original.docx and author_emails.txt from WORK (the local "PIC 2026 camera-ready" folder
next to the repo) and writes the Word file there; nothing with personal data is kept in git.

Edits submitted_original.docx paragraph by paragraph, keeping its IEEE styles. Every number in
the new tables and prose is computed here from the saved runs in the repository; re-run after
new experiments. Text in «guillemets» is highlighted yellow: a value that is still pending.
"""

import copy
import re
import statistics
import sys
import subprocess
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent              # <repo>/paper/pic2026: scripts and notes (in git)
REPO = HERE.parents[1]
WORK = REPO.parent / "PIC 2026 camera-ready"         # inputs and outputs, outside git (author emails, paper files)
sys.path[:0] = [str(REPO), str(REPO / "scripts"), str(REPO.parent / "SN Computer Science submission" / ".pylib")]

import docx  # noqa: E402
from docx.enum.text import WD_COLOR_INDEX  # noqa: E402
from docx.oxml.ns import qn  # noqa: E402
from docx.shared import Inches, Pt  # noqa: E402
from docx.text.paragraph import Paragraph  # noqa: E402

from results_tables import FULL_CONTEXT_K, usable_runs  # noqa: E402
from run_audit import audit  # noqa: E402
from significance import holm, mcnemar_exact  # noqa: E402
from src.evaluation.analysis import (collect_errors, confidence_floor_sweep, consistency,  # noqa: E402
                                     guard_effect, wilson_interval)
from src.evaluation.datasets import load_dataset  # noqa: E402
from src.evaluation.experiment import list_runs  # noqa: E402

SRC = WORK / "submitted_original.docx"
OUT = WORK / "PIC2026_Paper325_camera_ready.docx"
MODELS = (("gpt-oss-120b", "gpt-oss-120b"), ("qwen3.8-27b", "qwen3.8-27b"), ("gpt-oss-20b", "gpt-oss-20b"))
STYLES = (("zero_shot", "zero-shot"), ("facts", "facts"), ("cot", "CoT"))
WORDS = {2: "Two", 3: "Three", 4: "Four", 5: "Five", 6: "Six"}

# ---------------------------------------------------------------------------
# Numbers from saved runs
# ---------------------------------------------------------------------------

RUNS = usable_runs(list_runs())
LLM = [r for r in RUNS if r["config"]["engine"] == "llm"]


def full(r):
    return int(r["config"].get("top_k") or 0) >= FULL_CONTEXT_K


def sel(ds, model=None, style=None, fullctx=False, engine="llm"):
    out = []
    for r in RUNS:
        c = r["config"]
        if c["dataset"] != ds or c["engine"] != engine:
            continue
        if engine == "llm" and (c["model"].split("/")[-1] != model or c["prompt_style"] != style
                                or full(r) != fullctx):
            continue
        out.append(r)
    return out


def mean(rs, key):
    vals = [r["metrics"][key] for r in rs if r["metrics"].get(key) is not None]
    return sum(vals) / len(vals) if vals else None


def pct(x, d=0):
    return "«pending»" if x is None else f"{x * 100:.{d}f}%"


def ci(rs):
    n = rs[0]["metrics"]["n"] * len(rs)
    k = sum(round(r["metrics"]["decision_accuracy"] * r["metrics"]["n"]) for r in rs)
    lo, hi = wilson_interval(k, n)
    return f"{lo * 100:.0f}–{hi * 100:.0f}"


def tokens_per_case(rs):
    return statistics.mean(r["metrics"]["total_tokens"] / r["metrics"]["n"] for r in rs)


V = {}
grid = {ds: {(m, s): sel(ds, m, s) for m, _ in MODELS for s, _ in STYLES} for ds in ("pilot", "counterfactual")}
for ds in grid:
    accs = [mean(rs, "decision_accuracy") for rs in grid[ds].values() if rs]
    V[ds + "_lo"], V[ds + "_hi"] = pct(min(accs)), pct(max(accs))
qf = ("qwen3.8-27b", "facts")
V["qwen_facts_p"], V["qwen_facts_cf"] = pct(mean(grid["pilot"][qf], "decision_accuracy")), pct(mean(grid["counterfactual"][qf], "decision_accuracy"))
f1s = [mean(rs, "clause_f1") for ds in grid for rs in grid[ds].values() if rs]
V["clf1_lo"], V["clf1_hi"] = pct(min(f1s)), pct(max(f1s))
refunds = [mean(rs, "refund_accuracy") for ds in grid for rs in grid[ds].values() if rs and mean(rs, "refund_accuracy") is not None]
V["refund_lo"], V["refund_hi"] = pct(min(refunds)), pct(max(refunds))

big = ("gpt-oss-120b", "cot")
fc = {ds: sel(ds, *big, fullctx=True) for ds in ("pilot", "counterfactual")}
V["fc_p"], V["fc_cf"] = pct(mean(fc["pilot"], "decision_accuracy")), pct(mean(fc["counterfactual"], "decision_accuracy"))
V["k12_p"], V["k12_cf"] = pct(mean(grid["pilot"][big], "decision_accuracy")), pct(mean(grid["counterfactual"][big], "decision_accuracy"))
V["tok_ratio"] = f"{tokens_per_case(fc['pilot']) / tokens_per_case(grid['pilot'][big]):.1f}"

stab = next(g for g in consistency(grid["pilot"][big]) if g["runs"] > 1)
V["rep_runs"], V["rep_mean"], V["rep_sd"] = stab["runs"], pct(stab["accuracy_mean"]), pct(stab["accuracy_sd"])
V["rep_agree"], V["rep_cases"] = pct(stab["pairwise_agreement"]), ", ".join(sorted(stab["unstable_cases"])) or "none"

sig = (REPO / "results" / "significance.md").read_text(encoding="utf-8")
V["p_rules"], V["p_styles"], V["p_models"] = re.findall(r"smallest Holm-adjusted p = ([0-9.]+)", sig)

# test count, from a real run of the suite (the paper says they all pass, so they must)
_t = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider"], cwd=REPO,
                    capture_output=True, text=True, encoding="utf-8")
_m = re.search(r"(\d+) passed", _t.stdout)
assert _t.returncode == 0 and _m, "test suite failed: " + _t.stdout[-2000:]
V["n_tests"] = int(_m.group(1))

# held-out
HO = [r for r in RUNS if r["config"]["dataset"] == "heldout"]
ho_rules = next(r for r in HO if r["config"]["engine"] == "rules")
ho_llm = [r for r in HO if r["config"]["engine"] == "llm"]
ids = [p["case_id"] for p in ho_rules["metrics"]["per_case"]]
rc = {p["case_id"]: p["correct"] for p in ho_rules["metrics"]["per_case"]}
raw = []
for r in ho_llm:
    c = {p["case_id"]: p["correct"] for p in r["metrics"]["per_case"]}
    raw.append(mcnemar_exact([c[k] for k in ids], [rc[k] for k in ids])[2])
adj = dict(zip([r["run_id"] for r in ho_llm], holm(raw)))
best = max(ho_llm, key=lambda r: r["metrics"]["decision_accuracy"])
V["ho_best_name"] = f"{best['config']['model'].split('/')[-1]} with {dict(STYLES)[best['config']['prompt_style']]} prompting"
V["ho_best"], V["ho_best_ci"], V["ho_best_p"] = pct(best["metrics"]["decision_accuracy"], 1), ci([best]), f"{adj[best['run_id']]:.2f}"
V["ho_rules"] = pct(ho_rules["metrics"]["decision_accuracy"], 1)
V["ho_rules_a2e"] = ho_rules["metrics"]["confusion"]["APPROVE"].get("ESCALATE", 0)
V["ho_n_app"] = ho_rules["metrics"]["per_class"]["APPROVE"]["support"]
V["ho_n_esc"] = ho_rules["metrics"]["per_class"]["ESCALATE"]["support"]
esc_caught = [r["metrics"]["confusion"]["ESCALATE"].get("ESCALATE", 0) for r in ho_llm]
V["ho_esc_max"], V["ho_esc_min"] = max(esc_caught), min(esc_caught)
_rmax = max(r["metrics"]["escalation_recall"] for r in ho_llm)
V["ho_esc_rmax"] = pct(_rmax, 1)
_tops = [r for r in ho_llm if r["metrics"]["escalation_recall"] == _rmax]  # ties share the top spot
others = sorted(r["metrics"]["escalation_recall"] for r in ho_llm if r not in _tops)
V["ho_esc_others"] = f"{others[0] * 100:.0f}–{others[-1] * 100:.0f}%"
V["ho_esc_n_others"] = f"{WORDS.get(len(others), len(others)).lower()} of {WORDS.get(len(ho_llm), len(ho_llm)).lower()}"
_top_models = {r["config"]["model"].split("/")[-1] for r in _tops}
V["ho_esc_top"] = (f"{_top_models.pop()} with "
                   + " or ".join(dict(STYLES)[r["config"]["prompt_style"]] for r in _tops) + " prompting"
                   if len(_top_models) == 1 else " and ".join(sorted(_top_models)))
V["ho_best_escaped"] = best["metrics"]["confusion"]["ESCALATE"].get("ESCALATE", 0)
# prompt-style comparisons on the held-out set (paired exact McNemar, unadjusted p)
_hk = {(r["config"]["model"].split("/")[-1], r["config"]["prompt_style"]): r for r in ho_llm}
QF, QZ, QC = ("qwen3.8-27b", "facts"), ("qwen3.8-27b", "zero_shot"), ("qwen3.8-27b", "cot")
GF, GC = ("gpt-oss-120b", "facts"), ("gpt-oss-120b", "cot")


def _ho_p(a, b):
    ca = {p["case_id"]: p["correct"] for p in _hk[a]["metrics"]["per_case"]}
    cb = {p["case_id"]: p["correct"] for p in _hk[b]["metrics"]["per_case"]}
    return mcnemar_exact([ca[k] for k in ids], [cb[k] for k in ids])[2]


_acc = {k: _hk[k]["metrics"]["decision_accuracy"] for k in (QF, QZ, QC, GF, GC)}
_escn = {k: _hk[k]["metrics"]["confusion"]["ESCALATE"].get("ESCALATE", 0) for k in _hk}
# the prose states these directions; fail loudly if new runs ever reverse them
assert _acc[QF] > max(_acc[QZ], _acc[QC]) and _acc[GF] < _acc[GC], _acc
assert _escn[QC] < min(_escn[QF], _escn[QZ]), _escn
V.update({f"{n}_acc": pct(_acc[k], 1) for n, k in (("qf", QF), ("qz", QZ), ("qc", QC), ("gf", GF), ("gc", GC))})
V.update({f"{n}_esc": _escn[k] for n, k in (("qf", QF), ("qz", QZ), ("qc", QC))})
V["p_qfz"], V["p_qfc"], V["p_gfc"] = (f"{_ho_p(a, b):.2f}" for a, b in ((QF, QZ), (QF, QC), (GF, GC)))
V["ho_extra"] = sorted({f"{r['config']['model'].split('/')[-1]} with {dict(STYLES)[r['config']['prompt_style']]}"
                        for r in ho_llm if r["config"]["prompt_style"] != "cot"})

# errors, safeguards, confidence
in_sample = [r for r in LLM if r["config"]["dataset"] in ("pilot", "counterfactual")]
kinds = Counter(e["kind"] for e in collect_errors(in_sample))
n_in = sum(len(r["predictions"]) for r in in_sample)
kinds_ho = Counter(e["kind"] for e in collect_errors(ho_llm))
V["err_n"], V["rul_n"] = sum(kinds.values()), n_in
for k in ("missed_escalation", "over_escalation", "polarity"):
    V[k], V[k + "_pc"] = kinds[k], pct(kinds[k] / sum(kinds.values()))
    V[k + "_ho"], V[k + "_ho_pc"] = kinds_ho[k], pct(kinds_ho[k] / sum(kinds_ho.values()))
V["err_ho"] = sum(kinds_ho.values())
g_in = guard_effect(in_sample)
V["guard_better"], V["guard_runs"] = sum(g["accuracy_after"] > g["accuracy_before"] for g in g_in), len(g_in)
g_ho = {g["run_id"]: g for g in guard_effect(ho_llm)}


def guard_text(model):
    r = next(x for x in ho_llm if x["config"]["model"].endswith(model) and x["config"]["prompt_style"] == "cot")
    g = g_ho[r["run_id"]]
    return g


g120, gq, g20 = guard_text("gpt-oss-120b"), guard_text("qwen3.8-27b"), guard_text("gpt-oss-20b")
floors = {row["floor"]: row for row in confidence_floor_sweep(in_sample)}
V["fl_fixed"], V["fl_sent"] = floors[0.95]["errors_fixed"], floors[0.95]["correct_sent_to_review"]
V["fl_before"], V["fl_after"] = pct(floors[0.95]["accuracy_before"]), pct(floors[0.95]["accuracy_after"])
ho_floor_gain = max(row["accuracy_after"] - row["accuracy_before"] for row in confidence_floor_sweep(ho_llm))
conf_c = [p["confidence"] for r in in_sample for p in r["metrics"]["per_case"] if p["correct"]]
conf_w = [p["confidence"] for r in in_sample for p in r["metrics"]["per_case"] if not p["correct"]]
V["conf_c"], V["conf_w"] = f"{statistics.mean(conf_c):.2f}", f"{statistics.mean(conf_w):.2f}"

cod5 = [p for r in LLM if r["config"]["dataset"] == "pilot" for p in r["predictions"] if p["case_id"] == "COD-005"]
V["cod5_n"] = len(cod5)
V["cod5_rej"] = sum(p["decision"] == "REJECT" for p in cod5)
V["cod5_esc"] = sum(p["decision"] == "ESCALATE" for p in cod5)
V["cod5_conf"] = f"{statistics.median(float(p['confidence']) for p in cod5 if p['decision'] == 'REJECT'):.2f}"
V["cod5_seen"] = sum("SLA-COD-09" in (p.get("retrieved_clause_ids") or []) for p in cod5)

aud = audit([r for r in LLM if not full(r)])
V["aud_n"], V["aud_in"], V["aud_cited"] = sum(aud["rulings"].values()), sum(aud["in_prompt"].values()), sum(aud["cited"].values())
V["rep_n"] = sum(aud["repaired"].values())
V["all_n"] = sum(len(r["predictions"]) for r in LLM)
V["all_rep"] = sum(any("repaired after" in w for w in p.get("warnings") or []) for r in LLM for p in r["predictions"])
V["all_rep_pc"] = pct(V["all_rep"] / V["all_n"])
V["viol"] = sum(1 for r in LLM for row in r["metrics"]["per_case"] if row["grounding_issue"])

splits = {}
for ds in ("pilot", "counterfactual", "heldout"):
    cases, labels = load_dataset(ds)
    t, d = Counter(c["dispute_type"] for c in cases), Counter(l["decision"] for l in labels)
    splits[ds] = (len(cases), f"{t['DAMAGED_GOODS']} / {t['COD_MISMATCH']}",
                  f"{d['APPROVE']} / {d['REJECT']} / {d['ESCALATE']}")

# retrieval table from the saved comparison
retr = {}
for block in re.split(r"^## ", (REPO / "results" / "retrieval_comparison.md").read_text(encoding="utf-8"), flags=re.M):
    name = block.split("\n", 1)[0].strip()
    for m in re.finditer(r"^\| (lexical|bm25|dense|hybrid) \| (\d+) \| (\d+%) \| (\d+%) \| ([0-9.]+) \|", block, re.M):
        retr[(name, m.group(1), m.group(2))] = m.groups()[2:]

# ---------------------------------------------------------------------------
# Document helpers
# ---------------------------------------------------------------------------

D = docx.Document(str(SRC))
ORIG = list(D.element.body.iterchildren())
TOKEN = re.compile(r"(\*\*.+?\*\*|\*.+?\*|~.+?~|«.+?»)")


def _first_run(p_el):
    return p_el.find(qn("w:r"))


def fill(p_el, text, size=None, keep_runs=0, strip=True):
    """Replace the text of p_el (after its first keep_runs runs) with markup text in the style of the next run."""
    runs = p_el.findall(qn("w:r"))
    base = copy.deepcopy(runs[min(keep_runs, len(runs) - 1)])
    for r in runs[keep_runs:]:
        p_el.remove(r)
    rpr = base.find(qn("w:rPr"))
    if strip and rpr is not None:
        for child in ("w:b", "w:bCs", "w:i", "w:iCs", "w:vertAlign", "w:highlight"):
            for el in rpr.findall(qn(child)):
                rpr.remove(el)
    para = Paragraph(p_el, D)
    for part in filter(None, TOKEN.split(text)):
        r_el = copy.deepcopy(base)
        for t in r_el.findall(qn("w:t")):
            r_el.remove(t)
        p_el.append(r_el)
        run = [x for x in para.runs if x._r is r_el][0]
        if part.startswith("**"):
            run.text, run.bold = part[2:-2], True
        elif part.startswith("*"):
            run.text, run.italic = part[1:-1], True
        elif part.startswith("~"):
            run.text, run.italic, run.font.subscript = part[1:-1], True, True
        elif part.startswith("«"):
            run.text = part[1:-1]
            run.font.highlight_color = WD_COLOR_INDEX.YELLOW
        else:
            run.text = part
        if size:
            run.font.size = Pt(size)
    return p_el


def clone(i, text, size=None):
    return fill(copy.deepcopy(ORIG[i]), text, size)


def truncate_from(p_el, marker):
    """Cut paragraph text from marker onward (marker must start inside one run)."""
    runs = p_el.findall(qn("w:r"))
    for k, r in enumerate(runs):
        t = r.find(qn("w:t"))
        if t is not None and marker in (t.text or ""):
            t.text = t.text.split(marker)[0]
            for later in runs[k + 1:]:
                p_el.remove(later)
            return p_el
    raise ValueError(marker)


def append_text(p_el, text):
    base = copy.deepcopy(p_el.findall(qn("w:r"))[-1])
    holder = copy.deepcopy(p_el)
    for r in holder.findall(qn("w:r")):
        holder.remove(r)
    holder.append(base)
    fill(holder, text)
    for r in holder.findall(qn("w:r")):
        p_el.append(r)


def after(i, *els):
    anchor = ORIG[i]
    for el in els:
        anchor.addnext(el)
        anchor = el


def replace(i, *els):
    after(i, *els)
    ORIG[i].getparent().remove(ORIG[i])


def delete(*idx):
    for i in idx:
        ORIG[i].getparent().remove(ORIG[i])


TABLE_TEMPLATE = ORIG[189]
COL_TWIPS = 5000


def table(header, rows, fracs):
    """A table in the paper's style (from Table XIII of the submission), fixed column widths."""
    t = copy.deepcopy(TABLE_TEMPLATE)
    trs = t.findall(qn("w:tr"))
    hdr, body = trs[0], trs[1]
    for tr in trs:
        t.remove(tr)
    widths = [round(COL_TWIPS * f / sum(fracs)) for f in fracs]
    grid = t.find(qn("w:tblGrid"))
    for g in list(grid):
        grid.remove(g)
    for w in widths:
        g = grid.makeelement(qn("w:gridCol"), {qn("w:w"): str(w)})
        grid.append(g)
    tblpr = t.find(qn("w:tblPr"))
    layout = tblpr.makeelement(qn("w:tblLayout"), {qn("w:type"): "fixed"})
    tblpr.append(layout)
    for k, cells in enumerate([header] + rows):
        tr = copy.deepcopy(hdr if k == 0 else body)
        tcs = tr.findall(qn("w:tc"))
        while len(tcs) < len(cells):
            tcs[-1].addnext(copy.deepcopy(tcs[-1]))
            tcs = tr.findall(qn("w:tc"))
        for extra in tcs[len(cells):]:
            tr.remove(extra)
        for tc, text, w in zip(tr.findall(qn("w:tc")), cells, widths):
            tc.find(qn("w:tcPr")).find(qn("w:tcW")).set(qn("w:w"), str(w))
            p = tc.find(qn("w:p"))
            fill(p, text, keep_runs=0)
            if k == 0:
                for r in Paragraph(p, D).runs:
                    r.bold = True
        t.append(tr)
    return t


def table_caption(label, title):
    return [clone(40, label), clone(41, title)]


def note(text):
    return clone(91, text)


def body(text):
    return clone(8, text)


def h1(text):
    return clone(7, text)


def h2(text):
    return clone(25, text)


def figure(path, width_in=3.35):
    p = copy.deepcopy(ORIG[171])
    for r in p.findall(qn("w:r")):
        p.remove(r)
    Paragraph(p, D).add_run().add_picture(str(path), width=Inches(width_in))
    return p


# ---------------------------------------------------------------------------
# Edits, in document order
# ---------------------------------------------------------------------------

# Authors (CMT order)
replace(1, clone(1, "Arnav Mundra, Pallavi Hiwarkar, Kartikey Bisen, Piyush Pariwakam, Ishwar Paradkar, Krunal Narad"))
replace(2, clone(2, "*Department of Computer Science and Engineering*", 10),
        clone(2, "*G. H. Raisoni College of Engineering and Management, Nagpur, India*", 10),
        clone(2, (WORK / "author_emails.txt").read_text(encoding="utf-8").strip(), 9),  # kept out of git
        clone(2, "Corresponding author: Pallavi Hiwarkar", 9))

ABSTRACT = (
    "—Brands that sell directly to consumers (D2C) handle a steady flow of last-mile delivery disputes, most of them "
    "damaged-goods claims or mismatches in the cash collected on cash-on-delivery (COD) orders. Settling one means "
    "reading the customer's complaint, checking records such as the proof-of-delivery (PoD) photo and the "
    "cash-reconciliation log, and applying the brand's service-level agreement (SLA). We present a pipeline in which "
    "a large language model (LLM) labels each dispute APPROVE, REJECT or ESCALATE and must cite the SLA clauses and "
    "evidence items behind its ruling. It combines a synthetic 29-clause SLA, a rule-based evidence extractor, a "
    "hybrid clause retriever (lexical, BM25 and dense ranking fused by reciprocal rank), a validator that rejects "
    "citations to clauses or evidence that do not exist, and a deterministic rules engine used as a baseline. We "
    f"evaluate three open-weight LLMs under three prompting styles on 60 cases: 10 pilot cases, 16 counterfactual "
    f"edits and 34 held-out cases written after the rules engine was frozen and labelled blind by two annotators "
    f"(Cohen's κ = 0.86). On the pilot and counterfactual sets LLM accuracy ranges from {V['pilot_lo']} to "
    f"{V['counterfactual_hi']}, against 100% for the in-sample rules engine. On the held-out set the best LLM reaches "
    f"{V['ho_best']} while the rules engine falls to {V['ho_rules']}, and no ruling kept a citation to a "
    f"non-existent clause. Escalation is the main weakness: most configurations decide cases that a human would refer (held-out "
    f"escalation recall {V['ho_esc_others']} for {V['ho_esc_n_others']} configurations, against "
    f"{V['ho_esc_rmax']} for {V['ho_esc_top']}), and neither self-reported confidence nor disagreement with the "
    f"rules engine reliably flags these cases.")
fill(ORIG[5], ABSTRACT, keep_runs=1, strip=False)

fill(ORIG[17], "This paper reports progress on all five objectives. Its contributions are as follows.")
fill(ORIG[19], "2) A 60-case dataset in three parts: 10 pilot cases built from a scenario matrix, 16 counterfactual "
               "cases that each change one decisive fact of a pilot case, and 34 held-out cases labelled blind by two "
               "independent annotators, with disagreements adjudicated by a third person (κ = 0.86).")
fill(ORIG[20], "3) An end-to-end pipeline with source-linked evidence extraction, hybrid clause retrieval, a "
               "constrained LLM adjudicator in three prompting styles, citation validation with one repair round, "
               "and a deterministic rules engine that serves as baseline and cross-check.")
fill(ORIG[21], "4) An evaluation of three open-weight LLMs and the rules engine on decision, escalation, clause and "
               "refund accuracy, with Wilson intervals, paired significance tests, repeated-run consistency, a "
               "full-context condition and a comparison of four retrievers.")
fill(ORIG[22], "5) An error analysis showing that forced decisions on cases that need escalation are the dominant "
               "failure, that the rules engine does not generalise beyond the cases it was written on, and that "
               "neither model confidence nor rules-engine disagreement is a reliable escalation trigger.")
fill(ORIG[23], "Sections II–IV cover background, related work and the problem; Sections V–VI the dataset and the "
               "system; Sections VII–VIII the evaluation and results; and Sections IX–X the discussion and "
               "conclusions.")

# 8-page cut (16 Nov): introduction, related work and architecture tightened; results untouched
fill(ORIG[8], "A D2C brand runs its own web store and relies on third-party partners for delivery. Two complaints "
              "dominate its helpdesk: damaged goods, where the product arrives damaged or tampered with, and COD "
              "mismatches, where the cash collected differs from the invoice. Because many customers in India pay "
              "cash on delivery, these disputes are routine, not exceptional.")
fill(ORIG[9], "Each dispute is a small investigation: the agent reads the complaint, checks the PoD record, the "
              "delivery log and, for COD, the reconciliation log, and applies the SLA. The work is repetitive, "
              "depends on timestamp arithmetic, and two agents can reach different outcomes on similar facts.")
delete(36, 38, 44, 46, 48)  # related-work subheadings: the paragraphs read on without them
fill(ORIG[102], "**3) Prompt Construction.** The system prompt requires the model to use only the provided clauses "
                "and evidence, never to invent IDs, to measure windows in IST from the PoD timestamp, to apply a "
                "clause's formula rather than either party's figure, to escalate only for a stated open factual "
                "question, to cite as primary the clause whose removal would change the decision, and to give "
                "confidence as the probability that an expert would agree. The user prompt holds the retrieved "
                "clauses, the case as JSON, and the closed lists of citable clause and evidence IDs.")
fill(ORIG[104], "**5) Grounding Validation and Repair.** The validator checks the parsed JSON: a valid label, a primary "
                "clause that exists and was retrieved, existing and non-overlapping supporting clauses, evidence IDs "
                "that belong to the case (at least one), a non-empty rationale and a confidence in [0, 1]. On "
                "failure the model sees the problems and may correct them once; anything still wrong is attached "
                "as a warning, never silently accepted.")
fill(ORIG[202], "Rejecting a valid claim harms the customer, while approving an invalid one costs the brand. The "
                "system should support human decisions, not replace them: ESCALATE hands a case to a person, and "
                "because every ruling lists its clauses and evidence a reviewer can check it quickly. Fraud findings "
                "need two independent sources under the SLA, and only synthetic data was used.")
fill(ORIG[45], "LegalBench [5] breaks legal reasoning into skills such as rule application, and surveys of legal LLM "
               "use [4] and of hallucination [6], [7] find invented authority to be common. This is why our design "
               "validates every citation and treats ESCALATE as a proper outcome.")
fill(ORIG[49], "Chain-of-thought prompting [12] elicits intermediate reasoning, and self-consistency [16] samples "
               "several reasoning paths, which also gives a measure of agreement between runs. Abstention relies on "
               "confidence tracking correctness; modern networks are often miscalibrated [18], although LLMs partly "
               "know what they know [19].")

truncate_from(ORIG[47], "Our retriever is currently lexical")
append_text(ORIG[47], "Our retriever fuses lexical, BM25 and dense rankings by reciprocal rank fusion [26], and we "
                      "also test a prompt that contains the whole policy.")

append_text(ORIG[57], " Photographs enter the system as the textual descriptions recorded in the case; interpreting "
                      "images is outside the scope of this work.")

fill(ORIG[26], "A customer usually opens a ticket by chat or email. The support agent gathers the delivery partner's "
               "PoD record (OTP, GPS-stamped photo and time), the delivery log, the delivery agent's statement and, "
               "for COD orders, the daily reconciliation report, then applies the SLA and resolves the case by "
               "replacement, refund or manual review. A damaged-goods claim turns on three questions: was it "
               "reported in time, is the damage evidenced, and can it be attributed to transit, where a crushed or "
               "wet carton in the PoD photo is the strongest sign. A COD mismatch turns on the amount actually "
               "collected, for which the reconciliation log is the most reliable source; the customer, the agent "
               "and the log often disagree, the log may be missing, and the refund must follow the records rather "
               "than the request. Missing parcels, wrong items, sizing and prepaid-payment problems need different "
               "evidence and are out of scope (SLA-GEN-02).")
delete(25, *range(27, 33))  # background subsections folded into one paragraph: 8-page limit
delete(33, 34)  # "why the task is hard": 10-page limit
delete(74)      # scenario-matrix generation rules: 10-page limit
fill(ORIG[66], "We wrote the policy to exercise particular reasoning skills: numeric limits (a 48-hour damage window "
               "in SLA-DG-01, stretched to 7 days when the PoD photo shows damage under SLA-DG-02; unboxing evidence "
               "for orders of ₹5,000 or more under SLA-DG-03; a 24-hour COD window; a ₹10 rounding tolerance), a "
               "refund formula (reconciliation amount minus order total, SLA-COD-04), precedence rules (structured "
               "evidence over narrative unless there is a recorded reason to doubt it, SLA-PRI-01; specific over "
               "general, SLA-PRI-03), and clauses that leave room for discretion (SLA-DG-05, SLA-DG-08), to see "
               "whether a model forces a decision where a person would escalate. Every clause has a fixed ID that "
               "serves as both retrieval target and citation, and the thresholds are plausible stand-ins.")
delete(67)
fill(ORIG[69], "Rather than writing cases freely, we derived them from a scenario matrix of dispute type × difficulty. "
               "The pilot holds 10 cases, five of each type, with reference decisions 5 APPROVE, 2 REJECT and 3 "
               "ESCALATE. An EASY case has one obvious governing clause and agreeing evidence; a HARD case needs "
               "several sources, thresholds or competing clauses weighed together; an ESCALATION case holds evidence "
               "that cannot support a defensible automatic decision.")
delete(70, 71, 72, 73)  # scenario-matrix table: 8-page limit
fill(ORIG[87], "A reference label stores the decision, the governing clause IDs, the decisive, contradictory and "
               "missing evidence IDs, a rationale, sub-decisions such as the resolution type and refund amount, the "
               "labeler and the SLA version. Labels are kept apart from the model's input, were written without "
               "seeing any prediction, and any later change needs a revision note. The pilot labels name 26 "
               "governing clauses, one to four per case.")
fill(ORIG[76], Paragraph(ORIG[76], D).text.replace(
    "The 44 evidence items are counted by type in Table V.",
    "The 44 evidence items are 10 chat messages, 10 agent statements, 10 PoD records, 4 customer photos, 5 "
    "delivery logs and 5 reconciliation logs."))
assert "Table V" not in Paragraph(ORIG[76], D).text
delete(77, 78, 79, 80)  # evidence-type table: 10-page limit
fill(ORIG[58], "V. SLA Policy and Dataset")
truncate_from(ORIG[60], ", and Appendix A gives every clause.")
append_text(ORIG[60], ".")

# New subsection: counterfactual and held-out sets, before the integrity checks
after(91,
      h2("F. Counterfactual and Held-Out Sets"),
      body("The pilot cases were also used to develop the rules engine and the fact extractor, so scores on them are "
           "in-sample. We therefore built two further sets (Table VIII). The counterfactual set holds 16 cases, each "
           "a copy of a pilot case with one decisive fact changed, for example a damaged PoD photo that opens the "
           "7-day window or a reconciliation log that confirms the customer's amount. A model that follows the "
           "facts that matter should change its decision accordingly. These labels were written by the project "
           "team."),
      body("The held-out set holds 34 new cases, written after the rules engine had been frozen under a version tag "
           "and covering boundary values, missing or conflicting evidence and deliberately ambiguous wording. Two "
           "annotators who are not authors of this paper labelled every case independently, without seeing any "
           "model output, the rules engine or each other's labels, in a spreadsheet that restricted decisions and "
           "clause IDs to valid values. They agreed on 31 of 34 decisions (91%, Cohen's κ = 0.86 [25], almost "
           "perfect on the Landis–Koch scale [27]), and the mean Jaccard overlap of their governing-clause sets was "
           "0.87. A third person resolved the 12 cases with any disagreement, 3 on the decision and 9 on clauses "
           "only. All three decision disagreements trace to ambiguous SLA wording: how earlier claims are counted "
           "under SLA-DG-09, whether a same-day photo satisfies the unboxing requirement, and what makes a log "
           "implausible under SLA-COD-05. The labels were frozen before any system was run on these cases."),
      *table_caption("Table VIII", "Dataset Composition"),
      table(["Set", "Cases", "DG / COD", "A / R / E", "Labelled by"],
            [["Pilot", str(splits["pilot"][0]), splits["pilot"][1], splits["pilot"][2], "One author"],
             ["Counterfactual", str(splits["counterfactual"][0]), splits["counterfactual"][1],
              splits["counterfactual"][2], "Project team"],
             ["Held-out", str(splits["heldout"][0]), splits["heldout"][1], splits["heldout"][2],
              "2 annotators + adjudicator"]],
            [1.15, 0.55, 0.9, 0.95, 1.9]),
      note("A / R / E: reference decisions APPROVE / REJECT / ESCALATE."))
delete(92, 93)  # integrity checks: listed in Section VIII-A instead (10-page limit)
delete(88, 89, 90, 91)  # pilot-label table: 8-page limit (anchor 91 already used above)

fill(ORIG[81], "Two rules govern the case schema: raw evidence is always kept, with derived values such as hours "
               "elapsed added alongside and never overwriting it, and a case never contains its label.")
delete(82, 83, 84, 85)  # case-schema table: 10-page limit

# Architecture
replace(96, figure(HERE / "fig1_pipeline.png"))  # redrawn for hybrid retrieval and the rules engine (fig1_pipeline.py)
fill(ORIG[97], "Fig. 1. The SLA-grounded adjudication pipeline. Steps 1–5 produce the LLM ruling; the rules engine (6) "
               "runs on the same facts as baseline and cross-check; only the evaluation step reads the labels.")
fill(ORIG[98], "**1) Evidence Extraction.** The case view combines the dispute type, the order metadata, the "
               "evidence items grouped by section and the SLA version, and raises an error if any label field is "
               "present. A rule-based extractor then derives typed facts: the hours from the PoD timestamp to the "
               "first report, the parcel condition in the PoD record (with negation handling), how specific the "
               "damage description is, whether unboxing evidence exists, hub exceptions, and the amounts on the "
               "invoice, in the customer's claim and in the reconciliation log. Every fact names the evidence IDs it "
               "came from and never replaces the raw text. Regular expressions proved sufficient, so the spaCy [14] "
               "and NLTK [15] pipelines first planned were not needed.")
fill(ORIG[99], "**2) Clause Retrieval.** Four rankers are available. The lexical ranker forms the query *Q* from "
               "the tokens of the case text after removing stop-words, and scores a clause *c* with token set "
               "*T*~c~ as")
truncate_from(ORIG[101], "Dividing by the square root")
append_text(ORIG[101], "The second ranker is BM25 [11] over the same tokens, and the third embeds the case and the "
                       "clauses with all-MiniLM-L6-v2 [9], [28] and ranks by cosine similarity. The hybrid ranker, "
                       "used in all experiments, fuses the three rankings by reciprocal rank fusion [26] and keeps the "
                       "top *k* = 12. Policy-level additions follow for every case: pinned clauses that are always "
                       "present (the priority rules SLA-PRI-01 to 03, the IST rule SLA-GEN-03 and the eligibility "
                       "gates of the dispute type), clauses whose trigger condition an extracted fact satisfies (for "
                       "instance SLA-COD-09 when both sides of a contested amount are corroborated), and a one-hop "
                       "expansion that adds every clause named by ID inside a selected clause, so that SLA-COD-06 "
                       "brings SLA-COD-07 along.")
after(102, body("Three prompting styles share these constraints. *Zero-shot* gives only the clauses and the case; "
                "*facts* adds the extracted facts with their evidence IDs; and *CoT* (chain of thought [12]) adds the "
                "facts and asks the model to record its analysis of the window, the governing clause and the "
                "evidence before it decides."))
fill(ORIG[103], "**4) LLM Adjudicator.** Vendor-specific details sit behind a single provider interface. The "
                "experiments use three open-weight models served by Groq: gpt-oss-120b and gpt-oss-20b [20] and "
                "qwen3.8-27b, a Qwen3-family model [29]. Every call uses temperature 0 and a limit of 3,000 output "
                "tokens, and is retried with exponential back-off when the service reports rate limiting.")
fill(ORIG[105], "**6) Rules Engine and Evaluation.** A deterministic rules engine implements the SLA as an explicit "
                "decision procedure over the extracted facts and records a step-by-step trace. It is the offline "
                "fallback, a baseline, and a cross-check stored with every LLM ruling. It was written with the pilot "
                "cases visible and frozen before the held-out cases were written. Outputs are scored against the "
                "frozen labels by a separate module; no other part of the system reads the labels.")
fill(ORIG[107], f"The code is written in Python 3.11 and has {V['n_tests']} automated tests. It can be used from the command "
                "line, which adjudicates a single case or a whole dataset and saves every run with its configuration "
                "and per-case outputs as JSON, or through a Streamlit application whose evaluation view is the only "
                "place that reads reference labels.")
delete(108, 109, 111, 112, 113)  # implementation table and application subsection: 10-page limit
ORIG[110].getparent().remove(ORIG[110])

# Worked-examples section removed for 8 pages: COD-005 is the Section VIII-G case study, and the decision flows
# move into Section VI as subsection B, after the implementation paragraph (figure order stays 1, 2, 3)
delete(*range(114, 135))
after(107, *[ORIG[i] for i in range(135, 141)])
fill(ORIG[135], "B. Decision Logic")
fill(ORIG[136], "Figs. 2 and 3 condense the reading of SLA v0.1 that guided the labelling into two decision flows; "
                "together they reproduce all ten pilot decisions, and the rules engine implements them over the "
                "extracted facts. The flows are simplified (they omit, for instance, the order-ID requirement of "
                "SLA-COD-02 and the remedy choice of SLA-DG-07). The LLM gets no flow: it must reach the same "
                "answers from the clause text, and some questions, such as whether a customer's photo supports the "
                "claim, can only be answered by reading narrative evidence.")
fill(ORIG[138], Paragraph(ORIG[138], D).text.replace("Fig. 4.", "Fig. 2."))
fill(ORIG[140], Paragraph(ORIG[140], D).text.replace("Fig. 5.", "Fig. 3."))

# Methodology
fill(ORIG[149], "In the results, clause agreement is reported as precision, recall and F1 of the cited set, which give "
                "partial credit in the same way as the Jaccard score. Latency is measured per case in wall-clock "
                "time and includes any repair round. Accuracies are "
                "given with 95% Wilson intervals [30], and configurations are compared with exact McNemar tests "
                "[31] on paired per-case correctness, Holm-corrected within each family of comparisons [32]. "
                "Explanation quality has not been rated by humans, and overlap scores such as ROUGE [13] or "
                "BERTScore [22] are not reported, because overlap with a reference rationale says nothing about "
                "whether an explanation is right. SLA-PRI-02 is excluded from clause scoring, since the prompt "
                "instructs the model not to cite it.")
fill(ORIG[151], "We compare against a majority-class classifier, a uniform random classifier, and the rules "
                "engine, which shows how much of the task a hand-coded procedure can handle (it implements Figs. 2 "
                "and 3 on the extracted facts). Human judgment enters through the held-out labels of two "
                "independent annotators and an adjudicator. Three open-weight models, gpt-oss-120b, qwen3.8-27b and "
                "gpt-oss-20b, are each run in the three prompting styles of Section VI. Further conditions are a "
                "full-context prompt with all 29 clauses, four repeated runs of one configuration, and two "
                "safeguards simulated from the saved runs: escalating whenever the LLM and the rules engine "
                "disagree, and escalating any ruling below a confidence floor. Few-shot prompting [21] and other "
                "model families such as Mistral [23] and Llama 3 [24] are left to future work.")
_ho_styles = {m: [dict(STYLES)[s] for s, _ in STYLES if (m, s) in _hk] for m, _ in MODELS}
extra = ", ".join(f"{m} " + ("in all three styles" if len(st) == len(STYLES) else "with " + " and ".join(st))
                  for m, st in sorted(_ho_styles.items(), key=lambda kv: -len(kv[1])) if st)
fill(ORIG[153], "Labels never enter a prompt or a retrieval index, and the case view raises an error if a label "
                "field reaches it. The held-out labels were finalised before any system was run on those cases and "
                "were not used to tune prompts, the retriever or the rules engine; where the annotators disagreed, "
                "both labels and the adjudicated decision are kept. Every run stores its model, prompt style, "
                "retrieval settings, dataset, temperature, token use and per-case outputs, and every figure in this "
                "paper is computed from these saved runs. Because the free API tier limits daily tokens, the "
                f"held-out grid is partial: {extra}.")
fill(ORIG[141], "VII. Evaluation Methodology")
# stale future tense from the submission: partial credit is now reported (Jaccard, and clause F1 below)
_r = Paragraph(ORIG[145], D).runs
assert [r.text for r in _r[12:15]] == [", and if partial credit turns out to be ", "necessary,",
                                       " we will use the Jaccard overlap shown next. "]
_r[12].text, _r[13].text, _r[14].text = ", with partial credit given by the Jaccard overlap. ", "", ""
fill(ORIG[155], "Each wrong or unsafe output is tagged by the pipeline stage that failed (evidence reading, retrieval, "
                "grounding, arithmetic or the decision itself). In Section VIII we group decision errors at the "
                "coarsest level: missed escalations, unnecessary escalations, and reversals of approve and reject.")
delete(156, 157, 158, 159)  # error-taxonomy table: 8-page limit
delete(160, 161)  # research targets: 10-page limit

# Results: replace the preliminary-results section (162–191)
RETR_ROWS = []
for name in ("lexical", "bm25", "dense", "hybrid"):
    for k in ("4", "12"):
        p, c = retr[("pilot", name, k)], retr[("counterfactual", name, k)]
        RETR_ROWS.append([{"bm25": "BM25", "dense": "Dense", "lexical": "Lexical", "hybrid": "Hybrid"}[name], k,
                          p[0], p[1], c[0], c[1], p[2]])


def grid_cell(ds, rs):
    return f"{pct(mean(rs, 'decision_accuracy'))} / {pct(mean(rs, 'escalation_recall'))}" if rs else "«pending»"


GRID_ROWS = []
for m, mname in MODELS:
    for s, sname in STYLES:
        rows = [grid["pilot"][(m, s)], grid["counterfactual"][(m, s)]]
        label = f"{mname}, {sname}" + (f" ({len(rows[0])} runs)" if len(rows[0]) > 1 else "")
        GRID_ROWS.append([label, grid_cell("pilot", rows[0]), grid_cell("counterfactual", rows[1])])
GRID_ROWS.append(["gpt-oss-120b, CoT, full context", grid_cell("pilot", fc["pilot"]),
                  grid_cell("counterfactual", fc["counterfactual"])])
GRID_ROWS.append(["Rules engine", grid_cell("pilot", sel("pilot", engine="rules")),
                  grid_cell("counterfactual", sel("counterfactual", engine="rules"))])
maj = {ds: sel(ds, engine="rules")[0]["baselines"]["majority_class"] for ds in ("pilot", "counterfactual")}
GRID_ROWS.append(["Majority class"] + [f"{pct(maj[ds]['decision_accuracy'])} / 0%" for ds in ("pilot", "counterfactual")])

# Held-out runs the user will launch by hand (no timer); until their result files exist they show as «pending»
HO_PLANNED = (("gpt-oss-120b", "facts"), ("qwen3.8-27b", "zero_shot"))
_ho_key = lambda mdl, sty: ([m for m, _ in MODELS].index(mdl), [s for s, _ in STYLES].index(sty))
_ho_have = {(r["config"]["model"].split("/")[-1], r["config"]["prompt_style"]): r for r in ho_llm}
ho_missing = [k for k in HO_PLANNED if k not in _ho_have]
HO_ROWS = []
for mdl, sty in sorted(set(_ho_have) | set(ho_missing), key=lambda k: _ho_key(*k)):
    label = f"{mdl}, {dict(STYLES)[sty]}"
    if (mdl, sty) not in _ho_have:
        HO_ROWS.append([label, "«pending»", "«—»", "«—»", "«—»", "«—»"])
        continue
    r = _ho_have[(mdl, sty)]
    m = r["metrics"]
    HO_ROWS.append([label, f"{pct(m['decision_accuracy'], 1)} ({ci([r])})", f"{m['macro_f1']:.2f}",
                    f'{pct(m["escalation_precision"])} / {pct(m["escalation_recall"])}', pct(m["clause_f1"]),
                    pct(m["refund_accuracy"])])
m = ho_rules["metrics"]
HO_ROWS.append(["Rules engine", f"{pct(m['decision_accuracy'], 1)} ({ci([ho_rules])})", f"{m['macro_f1']:.2f}",
                f'{pct(m["escalation_precision"])} / {pct(m["escalation_recall"])}', pct(m["clause_f1"]),
                pct(m["refund_accuracy"])])
HO_ROWS.append(["Majority class", pct(ho_rules["baselines"]["majority_class"]["decision_accuracy"], 1), "—",
                "— / 0%", "—", "—"])

_names = [f"{m} with {dict(STYLES)[st]} prompting" for m, st in ho_missing]
pending_ho = (f" «{' and '.join(_names)} {'are' if len(_names) > 1 else 'is'} still being run on the held-out set "
              "and will be added to Table XIII.»" if ho_missing else "")

RESULTS = [
    h1("VIII. Results"),
    h2("A. Dataset Integrity and Grounding"),
    body("The validator passes all checks on the 60 cases and their labels: no label reaches the model's input, "
         f"every evidence and clause reference resolves, and case and label IDs agree. All {V['n_tests']} automated tests pass. "
         f"Of {V['all_n']} LLM rulings, {V['viol'] or 'none'} kept an unresolved citation; the first answer needed one repair "
         f"round in {V['all_rep']} rulings ({V['all_rep_pc']})."),
    h2("B. Clause Retrieval"),
    body("Table XI compares the four rankers. *Ranker recall* is the share of governing clauses in the ranker's "
         "own top-*k*; *context recall* is the share that reaches the prompt once pinned clauses, gates, fact "
         "triggers and cross-references are added. Lexical ranking, the retriever of the submitted prototype, "
         "misses SLA-COD-09 in COD-005 even at *k* = 12, because a customer's account of an overcharge shares few "
         "words with a fraud clause. Dense ranking finds more clauses at larger *k*, and the hybrid ranker with fact "
         "triggers puts every governing clause of both sets into the prompt at every *k* tested, at a cost of about "
         f"{float(retr[('pilot', 'hybrid', '12')][2]):.0f} of the 29 clauses at *k* = 12."),
    *table_caption("Table XI", "Recall of Governing Clauses (%)"),
    table(["Ranker", "k", "Pilot rank.", "Pilot ctx.", "CF rank.", "CF ctx.", "Clauses"],
          [[a, b, c[:-1], d[:-1], e[:-1], f[:-1], g] for a, b, c, d, e, f, g in RETR_ROWS],
          [1.0, 0.4, 0.8, 0.8, 0.8, 0.8, 0.8]),
    note("rank.: the ranker's own top-k. ctx.: what reaches the prompt. CF: counterfactual. Clauses: mean number "
         "in the pilot prompts, out of 29. SLA-PRI-02 excluded."),
    body("Following cross-references has a side effect. The pinned priority rules mention damaged-goods clauses as "
         "examples, so expansion adds two or three of them to every COD prompt, and SLA-COD-06 brings SLA-COD-07 "
         f"into damaged-goods prompts. In all {V['aud_n']} LLM rulings made with retrieval a clause of the other "
         f"dispute family was in the prompt, and {V['aud_cited'] or 'not one'} ruling cited it. The distractors did "
         "no harm with these models. Restricting expansion to the case's own family would remove them; we did not "
         "apply it, so that all runs share one retriever."),
    h2("C. End-to-End Adjudication"),
    body("Table XII gives decision accuracy and escalation recall on the pilot and counterfactual sets. Every LLM "
         f"configuration beats the majority baseline, with {V['pilot_lo']}–{V['pilot_hi']} on the pilot set and "
         f"{V['counterfactual_lo']}–{V['counterfactual_hi']} on the counterfactual set; the best is qwen3.8-27b with "
         f"extracted facts ({V['qwen_facts_p']} and {V['qwen_facts_cf']}). The rules engine scores 100% on both, but "
         "it was written with the pilot cases visible and the counterfactual cases are one-fact edits of them, so "
         f"these scores are in-sample. Refund amounts were right in {V['refund_lo']}–{V['refund_hi']} of the cases "
         f"that call for one. Clause F1 is lower, {V['clf1_lo']}–{V['clf1_hi']}, mainly because models cite more "
         "supporting clauses than the labels list."),
    body("Putting all 29 clauses into the prompt changed little. gpt-oss-120b with CoT scored "
         f"{V['fc_p']} on the pilot set and {V['fc_cf']} on the counterfactual set with the full SLA, against "
         f"{V['k12_p']} (mean of {V['rep_runs']} runs) and {V['k12_cf']} with retrieval, while reading "
         f"{V['tok_ratio']} times as many tokens per case. For a policy this short, retrieval is not needed for "
         "accuracy. It remains useful because policies grow and because a smaller context gives the validator a "
         "tighter boundary for citations."),
    *table_caption("Table XII", "Pilot and Counterfactual Results"),
    table(["Configuration", "Pilot (n = 10)", "Counterfactual (n = 16)"], GRID_ROWS, [2.1, 1.1, 1.8]),
    note("Each cell: decision accuracy / escalation recall. Repeated runs are averaged. Hybrid retrieval, k = 12, "
         "unless marked full context."),
    h2("D. Held-Out Results"),
    body("Table XIII and Fig. 4 report the held-out set, the only set that neither the rules engine nor the prompts "
         f"were developed on. The rules engine falls from 100% to {V['ho_rules']}: it escalates "
         f"{V['ho_rules_a2e']} of the {V['ho_n_app']} cases the annotators approve, so most of its errors are "
         f"unnecessary referrals. The best configuration is {V['ho_best_name']}, at {V['ho_best']} "
         f"(95% CI {V['ho_best_ci']}%); "
         + ("with 34 cases its gain over the rules engine is not significant" if float(V["ho_best_p"]) >= 0.05
            else "its gain over the rules engine is significant")
         + f" (exact McNemar, Holm-adjusted over {len(ho_llm)} comparisons, p = {V['ho_best_p']}). Prompt style "
         f"mattered for qwen3.8-27b: with extracted facts it reached {V['qf_acc']}, against {V['qz_acc']} "
         f"zero-shot (paired exact McNemar, unadjusted p = {V['p_qfz']}) and {V['qc_acc']} with CoT "
         f"(p = {V['p_qfc']}), and it caught {V['qf_esc']} of the {V['ho_n_esc']} cases the annotators escalate "
         f"with facts and {V['qz_esc']} zero-shot, but only {V['qc_esc']} with CoT. Facts did not help "
         f"gpt-oss-120b, which scored {V['gf_acc']} with them against {V['gc_acc']} with CoT "
         f"(p = {V['p_gfc']})." + pending_ho),
    *table_caption("Table XIII", "Held-Out Results (n = 34)"),
    table(["Configuration", "Accuracy (95% CI)", "mF1", "Esc. P / R", "Cl. F1", "Ref."], HO_ROWS,
          [1450, 1150, 500, 800, 550, 550]),
    note("mF1: macro-F1. Esc. P / R: precision / recall of ESCALATE. Cl. F1: clause F1. Ref.: share of refund "
         "cases with the exact amount. "
         "Hybrid retrieval, k = 12."),
    h2("E. Significance and Consistency"),
    body("With 26 pilot and counterfactual cases the intervals are wide and overlap. Exact McNemar tests find no "
         f"significant difference between prompt styles within a model (smallest Holm-adjusted p = {V['p_styles']}), "
         f"between models within a style ({V['p_models']}), or between any LLM configuration and the rules engine "
         f"({V['p_rules']}). {WORDS[V['rep_runs']]} repeated runs of gpt-oss-120b with CoT on the pilot set gave "
         f"{V['rep_mean']} ± {V['rep_sd']} accuracy with {V['rep_agree']} pairwise decision agreement; only "
         f"{V['rep_cases']} changed between runs, despite temperature 0."),
    figure(REPO / "results" / "figures" / "heldout_ci.png"),
    clone(97, "Fig. 4. Decision accuracy on the 34 held-out cases with 95% Wilson intervals. The dashed line is the "
              "majority-class baseline (always approve)."),
    h2("F. Errors and Safeguards"),
    body(f"Across the pilot and counterfactual runs, {V['err_n']} of {V['rul_n']} LLM rulings were wrong: "
         f"{V['missed_escalation']} ({V['missed_escalation_pc']}) decided a case the reference escalates, "
         f"{V['over_escalation']} ({V['over_escalation_pc']}) escalated a case the reference decides, and "
         f"{V['polarity']} ({V['polarity_pc']}) reversed approve and reject. On the held-out set the {V['err_ho']} "
         f"LLM errors split {V['missed_escalation_ho']} / {V['over_escalation_ho']} / {V['polarity_ho']} in the same "
         "order: forced decisions are still the largest group, while unnecessary escalations and reversals grow on "
         "unfamiliar cases."),
    body("Escalating whenever the LLM and the rules engine disagree improved accuracy in "
         f"{V['guard_better']} of {V['guard_runs']} pilot and counterfactual runs, where the rules engine is "
         "in-sample. On the held-out set the same guard lowered accuracy for gpt-oss-120b from "
         f"{pct(g120['accuracy_before'], 1)} to {pct(g120['accuracy_after'], 1)} and for qwen3.8-27b from "
         f"{pct(gq['accuracy_before'], 1)} to {pct(gq['accuracy_after'], 1)}, sending "
         f"{g120['correct_sent_to_review']} and {gq['correct_sent_to_review']} correct rulings to review, although "
         f"it raised escalation recall for gpt-oss-20b from {pct(g20['escalation_recall_before'], 1)} to "
         f"{pct(g20['escalation_recall_after'], 1)}. A confidence floor fares no better. Correct and wrong rulings "
         f"report similar confidence (means {V['conf_c']} and {V['conf_w']}), so on the pilot and counterfactual "
         f"runs a floor of 0.95 fixes {V['fl_fixed']} errors but sends {V['fl_sent']} correct rulings to review "
         f"({V['fl_before']} to {V['fl_after']}), and on the held-out set "
         + ("no floor improves accuracy." if ho_floor_gain <= 0 else "the best floor gains little.")),
    h2("G. Case Study: COD-005"),
    body("COD-005 shows the dominant failure. The customer says ₹3,500 was taken for a ₹3,200 order and attaches an "
         "unverifiable photograph of banknotes, while the rider's statement and the reconciliation log both record "
         "₹3,200. The customer offers more than an assertion, but not the two independent sources that a fraud "
         f"finding under SLA-COD-09 requires, so the reference is ESCALATE. {V['cod5_rej']} of {V['cod5_n']} pilot "
         "rulings rejected the claim, siding with the structured log under SLA-PRI-01 with a median confidence of "
         f"{V['cod5_conf']}. The {'one ruling' if V['cod5_esc'] == 1 else str(V['cod5_esc']) + ' rulings'} that "
         "escalated did so by reading the case as suspected fraud rather than as an unresolved conflict. "
         f"SLA-COD-09 was in the prompt for {V['cod5_seen']} of the {V['cod5_n']} rulings, so the failure lies in "
         "reasoning rather than retrieval: the models read the clause and still prefer a confident decision."),
]
after(191, *RESULTS)
delete(*range(162, 192))

# Discussion
fill(ORIG[194], "The results suggest three lessons for systems that adjudicate against a written policy. First, a "
                f"closed list of citable IDs works: across {V['all_n']} rulings no citation to a non-existent clause "
                "or evidence item survived the single repair round. Second, a hand-written rules engine is a poor "
                f"guide to generalisation. It is perfect on the cases it was written for and drops to "
                f"{V['ho_rules']} on new ones, where the best LLM holds up better, so the LLM's value lies in coping "
                "with evidence its designers did not foresee. Third, escalation needs its own mechanism. Prompt "
                "instructions alone left most configurations deciding cases a person would refer; prompt style "
                "shifted this for one model, while rules-engine disagreement and self-reported confidence did not. A "
                "dedicated, calibrated abstention component is the most promising next step.")
fill(ORIG[196], "**Internal validity.** The project team wrote the SLA and all cases, so policy and case wording "
                "may match more closely than in real disputes. The held-out cases were written after the rules "
                "engine was frozen and were labelled by two independent annotators, but the counterfactual labels "
                "have not had a second annotator. The pilot label of COD-005 lists SLA-PRI-02, which the prompt "
                "tells models not to cite, so that clause is excluded from clause scoring.")
fill(ORIG[197], "**External validity.** Sixty synthetic cases expose failure modes but give wide intervals and do "
                "not capture the variety of real disputes; independently sourced operational cases are the next "
                "requirement. Photographs are given as text descriptions, whereas a deployment would have to "
                "interpret images. The SLA thresholds are plausible placeholders, and the held-out grid is partial "
                "because of API limits.")
fill(ORIG[198], "**Construct validity.** Matching a reference label measures agreement with one adjudicated "
                "reading of the SLA; where the policy allows discretion, a reasonable different decision counts as "
                "an error, as the three annotator disagreements show. Explanation quality was not rated by humans, "
                "and the model's confidence is self-reported and poorly calibrated.")
delete(199, 200)  # extending the dataset: 8-page limit
fill(ORIG[201], "C. Responsible Use")
fill(ORIG[192], "IX. Discussion")
delete(203, 204, 205, 206, 207)
fill(ORIG[208], "X. Conclusion and Future Work")
fill(ORIG[209], "We have presented and evaluated a pipeline in which an LLM adjudicates D2C damaged-goods and "
                "COD-mismatch disputes under an SLA, with every ruling tied to real clauses and evidence and "
                "escalation treated as a valid answer. On 60 cases, including 34 held-out cases labelled blind by "
                f"two annotators, the best open-weight LLM reached {V['ho_best']} held-out accuracy against "
                f"{V['ho_rules']} for a rules engine that scores 100% on the cases it was written for, and no ruling "
                "kept an invented citation. Extracted facts gave the best configuration, but not a consistent gain "
                "across models. The main weakness is "
                "escalation: most configurations decide cases that a person would refer, and neither rules-engine "
                "disagreement nor self-reported confidence corrects this.")
fill(ORIG[210], "Future work will address escalation directly, with a trained abstention component and calibrated "
                "confidence, and will add human ratings of explanation quality, independently sourced cases, image "
                "evidence, few-shot prompting and further model families.")

NEW_REFS = [
    "[26]\tG. V. Cormack, C. L. A. Clarke, and S. Büttcher, “Reciprocal rank fusion outperforms Condorcet and "
    "individual rank learning methods,” in Proc. 32nd Int. ACM SIGIR Conf. Research and Development in Information "
    "Retrieval, 2009, pp. 758–759.",
    "[27]\tJ. R. Landis and G. G. Koch, “The measurement of observer agreement for categorical data,” Biometrics, "
    "vol. 33, no. 1, pp. 159–174, 1977.",
    "[28]\tW. Wang, F. Wei, L. Dong, H. Bao, N. Yang, and M. Zhou, “MiniLM: Deep self-attention distillation for "
    "task-agnostic compression of pre-trained transformers,” in Advances in Neural Information Processing Systems, "
    "vol. 33, 2020, pp. 5776–5788.",
    "[29]\tA. Yang et al., “Qwen3 technical report,” arXiv:2505.09388, 2025.",
    "[30]\tE. B. Wilson, “Probable inference, the law of succession, and statistical inference,” Journal of the "
    "American Statistical Association, vol. 22, no. 158, pp. 209–212, 1927.",
    "[31]\tQ. McNemar, “Note on the sampling error of the difference between correlated proportions or "
    "percentages,” Psychometrika, vol. 12, no. 2, pp. 153–157, 1947.",
    "[32]\tS. Holm, “A simple sequentially rejective multiple test procedure,” Scandinavian Journal of Statistics, "
    "vol. 6, no. 2, pp. 65–70, 1979.",
]
after(236, *[clone(236, ref) for ref in NEW_REFS])
delete(*range(237, 243))  # Appendix A clause table: dropped for the 10-page limit

# Renumber tables in reading order and fix every in-text reference
ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII", "XIII", "XIV", "XV", "XVI"]
paras = [Paragraph(el, D) for el in D.element.body.iter(qn("w:p"))]
labels = [p for p in paras if re.fullmatch(r"Table [IVX]+", p.text.strip())]
mapping = {p.text.strip().split()[1]: ROMAN[k] for k, p in enumerate(labels)}
assert len(mapping) == len(labels), "duplicate table label"
ref = re.compile(r"Table (" + "|".join(sorted(mapping, key=len, reverse=True)) + r")(?![IVX])")
def _sub_across_runs(p):
    """Apply the renumbering even when 'Table' and its numeral sit in different runs."""
    runs = p.runs
    text = "".join(r.text for r in runs)
    for m in reversed(list(ref.finditer(text))):
        new = "Table " + mapping[m.group(1)]
        pos, first = 0, True
        for r in runs:
            a, b = pos, pos + len(r.text)
            pos = b
            lo, hi = max(a, m.start()), min(b, m.end())
            if lo >= hi:
                continue
            r.text = r.text[:lo - a] + (new if first else "") + r.text[hi - a:]
            first = False
        text = "".join(r.text for r in runs)


for p in paras:
    if ref.search(p.text):
        _sub_across_runs(p)
print("tables:", " ".join(f"{a}->{b}" for a, b in mapping.items() if a != b))

# PIC asks for the IEEE US-letter template: 8.5 x 11 in, top 0.75, bottom 1, sides 0.625, 3.5 in columns, 0.25 gap
for sec in D.sections:
    sec.page_width, sec.page_height = Inches(8.5), Inches(11)
    sec.top_margin, sec.bottom_margin = Inches(0.75), Inches(1.0)
    sec.left_margin = sec.right_margin = Inches(0.625)
    cols = sec._sectPr.find(qn("w:cols"))
    if cols is not None and cols.get(qn("w:num")) == "2":
        cols.set(qn("w:space"), "360")

# file metadata (the PDF inherits it): full accepted title and the CMT author list
D.core_properties.title = ("AI-Assisted Dispute Adjudication for D2C Delivery Operations: An SLA-Grounded LLM "
                           "Pipeline")
D.core_properties.author = ("Arnav Mundra; Pallavi Hiwarkar; Kartikey Bisen; Piyush Pariwakam; Ishwar Paradkar; "
                            "Krunal Narad")
D.core_properties.subject = "IEEE PIC 2026, Paper 325 (camera-ready)"
D.save(str(OUT))
print("wrote", OUT)
for k in ("pilot_lo", "pilot_hi", "counterfactual_lo", "counterfactual_hi", "fc_p", "fc_cf", "ho_best", "ho_rules",
          "guard_better", "guard_runs", "cod5_rej", "cod5_n", "err_n", "rul_n"):
    print(f"  {k} = {V[k]}")
