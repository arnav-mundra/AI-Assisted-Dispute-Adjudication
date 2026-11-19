"""Fig. 1 of the PIC camera-ready: the current pipeline, drawn for one IEEE column (3.35 in).

    <repo>/venv/Scripts/python fig1_pipeline.py      -> fig1_pipeline.png (600 dpi)

Steps are numbered as in Section VI of the paper. Same content and palette as the journal figure
(SN Computer Science submission/figures/fig1_pipeline.png), laid out vertically.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch  # noqa: E402

OUT = Path(__file__).resolve().parent / "fig1_pipeline.png"
EDGE, LINE, TITLE, BODY = "#c3c1b8", "#a9a79e", "#1f1f1f", "#55534e"
HI_EDGE, HI_FILL = "#2f6fd0", "#e6eef9"
X0, X1 = -8, 100
TS, BS = 6.4, 5.5                                   # title / body font sizes (pt)
LH = BS * 1.25 / 72 * (X1 - X0) / 3.35              # body line height in data units
GAP = 3.2


def height(body):
    return 5.4 + LH * (body.count("\n") + 1) + 1.6


MAIN = [("Dispute case", "Order metadata and 4–5 evidence items"),
        ("1. Evidence extraction", "Typed facts (windows, PoD condition,\namounts), each naming its evidence IDs;\n"
                                   "label-leak check"),
        ("2. Clause retrieval", "Lexical + BM25 + dense fused by RRF,\nk = 12; then pinned rules, gates, fact\n"
                                "triggers and one-hop cross-references"),
        ("3. Prompt construction", "Zero-shot, facts or CoT; closed lists\nof citable clause and evidence IDs"),
        ("4. LLM adjudicator", "One call per case, T = 0, JSON ruling"),
        ("5. Grounding validation", "Clause and evidence IDs exist; schema\nvalid; leftover problems kept as warnings"),
        ("Ruling", "APPROVE / REJECT / ESCALATE\nwith clause and evidence citations"),
        ("Evaluation", "Scored against the labels; the only\nstep that reads them")]
Y = [0.0]
for _, b in MAIN:
    Y.append(Y[-1] + height(b) + GAP)
Y1 = Y[-1] - GAP + 0.6

fig = plt.figure(figsize=(3.35, 3.35 * Y1 / (X1 - X0)))
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(X0, X1)
ax.set_ylim(Y1, 0)
ax.axis("off")


def box(x, y, w, title, body, hi=False, dashed=False):
    h = height(body)
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=1.6",
                                fc=HI_FILL if hi else "white", ec=HI_EDGE if hi else EDGE,
                                lw=0.9 if hi else 0.6, ls="--" if dashed else "-"))
    ax.text(x + 2, y + 1.5, title, ha="left", va="top", fontsize=TS, weight="bold", color=TITLE)
    ax.text(x + 2, y + 5.4, body, ha="left", va="top", fontsize=BS, color=BODY, linespacing=1.25)
    return h


def arrow(*pts, dashed=False, label=None, at=None, rot=0):
    xs, ys = zip(*pts)
    ax.plot(xs, ys, color=LINE, lw=0.6, ls="--" if dashed else "-", solid_capstyle="butt")
    ax.annotate("", xy=pts[-1], xytext=pts[-2],
                arrowprops=dict(arrowstyle="-|>", color=LINE, lw=0.6, mutation_scale=5, shrinkA=0, shrinkB=0))
    if label:
        ax.text(*at, label, fontsize=BS - 0.2, color=BODY, ha="center", va="center", style="italic",
                rotation=rot, bbox=dict(fc="white", ec="none", pad=0.4))


H = [box(2, y, 61, t, b, hi=t.startswith("5.")) for (t, b), y in zip(MAIN, Y)]


def mid(i):
    return Y[i] + H[i] / 2


for i in range(len(MAIN) - 1):
    arrow((32.5, Y[i] + H[i]), (32.5, Y[i + 1]))

# side column: SLA beside retrieval, rules engine beside steps 4-5, labels beside evaluation
sla_h = box(67, Y[2], 23, "SLA v0.1", "29 clauses,\nfixed IDs")  # narrow: the facts line passes at x = 94
arrow((67, Y[2] + sla_h / 2), (63, Y[2] + sla_h / 2))
re_y = Y[4]
re_h = box(67, re_y, 31, "6. Rules engine", "The SLA as an\nexplicit procedure\nover the facts;\nno model call")
arrow((63, mid(1)), (94, mid(1)), (94, re_y), label="facts", at=(94, (Y[3] + re_y) / 2))
arrow((82.5, re_y + re_h), (82.5, mid(6)), (63, mid(6)), label="cross-check",
      at=(82.5, (re_y + re_h + mid(6)) / 2))
box(67, Y[7], 31, "Reference labels", "Frozen; never in\na prompt", dashed=True)
arrow((67, mid(7)), (63, mid(7)), dashed=True)
arrow((2, mid(5)), (-4, mid(5)), (-4, mid(4)), (2, mid(4)), label="1 repair",
      at=(-4, (mid(4) + mid(5)) / 2), rot=90)

fig.savefig(OUT, dpi=600)
print("wrote", OUT, f"{3.35:.2f} x {3.35 * Y1 / (X1 - X0):.2f} in")
