"""Draw the paper's result figures from saved runs.

    python scripts/plot_figures.py    # writes results/figures/{accuracy_ci,confidence}.{png,pdf}

accuracy_ci: decision accuracy with 95% Wilson intervals per configuration, repeats pooled
as in the report tables. confidence: self-reported confidence of correct vs wrong LLM
rulings. Every point comes from results/runs/*.json; held-out runs are never read.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from src.config.paths import RESULTS_DIR  # noqa: E402
from src.evaluation.analysis import _unguarded, consistency, error_kind  # noqa: E402
from src.evaluation.datasets import load_dataset  # noqa: E402
from src.evaluation.experiment import list_runs  # noqa: E402

DATASETS = (("pilot", "Pilot (n = 10)"), ("counterfactual", "Counterfactual (n = 16)"))
MODELS = (("gpt-oss-120b", "120b"), ("qwen3.8-27b", "qwen"), ("gpt-oss-20b", "20b"))
STYLES = ("zero_shot", "facts", "cot")
ROWS = [(f"{short}, {style}", f"{model} · {style} · hybrid k=12") for model, short in MODELS for style in STYLES]
ROWS.append(("Rules engine", "rules engine"))


def panel_data(dataset):
    runs = list_runs(dataset)
    by_config = {s["config"].split(" · ", 1)[1]: s for s in consistency(runs)}
    majority = next(r["baselines"]["majority_class"] for r in runs if r.get("baselines"))
    return by_config, majority


def save(fig, name):
    out = RESULTS_DIR / "figures"
    out.mkdir(parents=True, exist_ok=True)
    for ext in ("png", "pdf"):
        fig.savefig(out / f"{name}.{ext}", dpi=300)
    print("wrote", out / f"{name}.png")


def confidence_figure():
    """Histogram of LLM confidence, correct rulings above and wrong ones below."""
    correct, wrong = [], []
    for dataset, _ in DATASETS:
        labels = {l["case_id"]: l["decision"] for l in load_dataset(dataset)[1]}
        for run in list_runs(dataset):
            if not _unguarded(run):
                continue
            for pred in run["predictions"]:
                if pred["case_id"] in labels:
                    bucket = wrong if error_kind(pred.get("decision", "UNPARSED"), labels[pred["case_id"]]) else correct
                    bucket.append(float(pred.get("confidence") or 0.0))
    bins = [0.7 + 0.025 * i for i in range(13)]  # 0.95 falls on a bin edge
    fig, axes = plt.subplots(2, 1, figsize=(3.4, 2.3), sharex=True)
    for ax, values, name, shade in ((axes[0], correct, "Correct", "0.6"), (axes[1], wrong, "Wrong", "0.15")):
        ax.hist(values, bins=bins, color=shade, edgecolor="white", linewidth=0.6)
        ax.axvline(0.95, color="0.35", lw=0.9, ls="--")
        ax.text(0.02, 0.95, f"{name} (n = {len(values)})", transform=ax.transAxes, va="top", fontsize=7.5)
        ax.set_ylabel("Rulings")
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
    axes[1].text(0.945, axes[1].get_ylim()[1] * 0.95, "floor 0.95", ha="right", va="top", fontsize=6.5, color="0.3")
    axes[1].set_xlabel("Self-reported confidence")
    axes[1].set_xlim(0.7, 1.0)
    fig.tight_layout()
    save(fig, "confidence")


def main():
    plt.rcParams.update({"font.family": "serif", "font.size": 8})
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 2.9), sharey=True)
    labels = [label for label, _ in ROWS]
    for ax, (dataset, title) in zip(axes, DATASETS):
        by_config, majority = panel_data(dataset)
        for y, (_, key) in enumerate(ROWS):
            s = by_config.get(key)
            if s is None:
                ax.text(0.02, y, "not yet run", va="center", fontsize=7, color="0.45")
                continue
            low, high = s["accuracy_ci"]
            rules = key == "rules engine"
            ax.plot([low, high], [y, y], color="0.55", lw=1.6, solid_capstyle="round")
            ax.plot(s["accuracy_mean"], y, marker="s" if rules else "o", ms=4.5,
                    color="black", mfc="white" if rules else "black", mew=1.1, clip_on=False)
            if s["runs"] > 1:
                ax.text(high + 0.02, y, f"{s['runs']} runs pooled", va="center", fontsize=6.5, color="0.3")
        ax.axvline(majority["decision_accuracy"], color="0.35", lw=0.9, ls="--")
        ax.text(majority["decision_accuracy"] - 0.015, len(ROWS) - 0.35,
                f"majority ({majority['label'].lower()})", ha="right", va="bottom", fontsize=6.5, color="0.3")
        ax.set_title(title, fontsize=8.5)
        ax.set_xlim(0, 1.0)
        ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0], ["0%", "25%", "50%", "75%", "100%"])
        ax.set_xlabel("Decision accuracy (95% Wilson CI)")
        ax.grid(axis="x", color="0.9", lw=0.6)
        ax.set_axisbelow(True)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
    axes[0].set_yticks(range(len(ROWS)), labels)
    axes[0].set_ylim(len(ROWS) + 0.2, -0.7)
    fig.tight_layout()
    save(fig, "accuracy_ci")
    confidence_figure()


if __name__ == "__main__":
    main()
