"""Build the README results table and results/icaaic_summary.md from saved runs.

    python scripts/results_tables.py

Every figure comes from results/runs/*.json; re-run this after any new experiment.
Runs from before the escalation-prompt fix are kept in results/runs/pre_rule5_fix/,
which is not read here. Held-out runs are never included.
"""

import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.config.paths import RESULTS_DIR  # noqa: E402
from src.evaluation.analysis import consistency, wilson_interval  # noqa: E402
from src.evaluation.experiment import list_runs  # noqa: E402

DATASETS = ("pilot", "counterfactual")
MODELS = ("openai/gpt-oss-120b", "qwen/qwen3.8-27b", "openai/gpt-oss-20b")
STYLES = ("zero_shot", "facts", "cot")
README = ROOT / "README.md"
README_START, README_END = "<!-- results:start -->", "<!-- results:end -->"
PILOT_REPEATS_NEEDED = 3
SPREAD_FLAG = 0.10  # accuracy sd across repeats worth pointing out


def _pct(value: Optional[float]) -> str:
    return "—" if value is None else f"{value:.0%}"


def _ci(run: Dict[str, Any]) -> str:
    n = run["metrics"]["n"]
    low, high = wilson_interval(round(run["metrics"]["decision_accuracy"] * n), n)
    return f"{low:.0%}–{high:.0%}"


def _grounding(run: Dict[str, Any]) -> int:
    return sum(1 for row in run["metrics"]["per_case"] if row["grounding_issue"])


def _config_name(run: Dict[str, Any]) -> str:
    config = run["config"]
    if config["engine"] == "rules":
        return "Rules engine"
    name = f"{config['model'].split('/')[-1]} · {config['prompt_style']}"
    return name + (f" · repeat {config['repeat']}" if config.get("repeat") else "")


def _sort_key(run: Dict[str, Any]) -> tuple:
    config = run["config"]
    model = config.get("model", "")
    style = config.get("prompt_style", "")
    return (config["engine"] != "rules",
            MODELS.index(model) if model in MODELS else len(MODELS),
            STYLES.index(style) if style in STYLES else len(STYLES),
            config.get("repeat", 0))


def usable_runs(runs: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Plain runs on the paper's datasets: safeguards off, scored, never held-out."""
    kept = [r for r in runs if r.get("config", {}).get("dataset") in DATASETS and r.get("metrics", {}).get("n")
            and not r["config"].get("guard") and not r["config"].get("min_confidence")]
    return sorted(kept, key=_sort_key)


def _row(run: Dict[str, Any], with_id: bool) -> str:
    m = run["metrics"]
    cells = [_config_name(run), str(m["n"]), _pct(m["decision_accuracy"]), _ci(run), _pct(m["escalation_recall"]),
             _pct(m["clause_f1"]), _pct(m.get("refund_accuracy")), str(_grounding(run))]
    if with_id:
        cells.append(f"`{run['run_id']}`")
    return "| " + " | ".join(cells) + " |"


def dataset_table(runs: Sequence[Dict[str, Any]], with_id: bool) -> List[str]:
    head = "| Configuration | n | Decision acc. | 95% Wilson CI | Escalation recall | Clause F1 | Refund acc. | Grounding violations |"
    rule = "|---|---|---|---|---|---|---|---|"
    if with_id:
        head, rule = head + " Run ID |", rule + "---|"
    lines = [head, rule] + [_row(run, with_id) for run in runs]
    if runs:
        majority = runs[0]["baselines"]["majority_class"]
        blanks = " — | — |" + (" — |" if with_id else "")
        lines.append(f"| Majority class (always {majority['label'].lower()}) | {runs[0]['metrics']['n']} "
                     f"| {_pct(majority['decision_accuracy'])} | — | {_pct(majority['escalation_recall'])} |"
                     f" — |{blanks}")
    return lines


def missing_configs(runs: Sequence[Dict[str, Any]]) -> List[tuple]:
    done = {(r["config"].get("dataset"), r["config"].get("model"), r["config"].get("prompt_style")) for r in runs}
    return [(d, m, s) for m in MODELS for d in DATASETS for s in STYLES if (d, m, s) not in done]


def flags(runs: Sequence[Dict[str, Any]], stability: Sequence[Dict[str, Any]]) -> List[str]:
    """Things a reader should check, worked out from the runs."""
    notes = []
    for run in runs:
        majority = run["baselines"]["majority_class"]["decision_accuracy"]
        where = f"{run['config']['dataset']} · {_config_name(run)}"
        if run["metrics"]["decision_accuracy"] <= majority:
            notes.append(f"**At or below the majority-class baseline:** {where} scored "
                         f"{_pct(run['metrics']['decision_accuracy'])} against {_pct(majority)}.")
        if run["config"]["engine"] == "llm" and run["config"].get("dense") is None:
            notes.append(f"**Retrieval setup not recorded:** {where} has no `dense` field in its config.")
        if run.get("failures"):
            notes.append(f"**Failed cases:** {where} lost {len(run['failures'])} case(s) to errors; "
                         "they are scored as wrong. Re-run this configuration.")
        if _grounding(run):
            notes.append(f"**Grounding violations:** {where} has {_grounding(run)} case(s) with an unresolved "
                         "citation after repair.")
    for dataset in DATASETS:
        scoped = [r for r in runs if r["config"]["dataset"] == dataset]
        rules = next((r for r in scoped if r["config"]["engine"] == "rules"), None)
        recalls = [r["metrics"]["escalation_recall"] for r in scoped if r["config"]["engine"] == "llm"]
        if rules and recalls and max(recalls) < rules["metrics"]["escalation_recall"]:
            support = rules["metrics"]["per_class"]["ESCALATE"]["support"]
            notes.append(f"**Escalation recall is the weak spot on {dataset}:** LLM runs reach "
                         f"{_pct(min(recalls))}–{_pct(max(recalls))} against {_pct(rules['metrics']['escalation_recall'])} "
                         f"for the rules engine. Only {support} reference cases escalate, so each one moves this a lot.")
    for group in stability:
        if group["runs"] > 1 and group["accuracy_sd"] >= SPREAD_FLAG:
            notes.append(f"**Large run-to-run spread:** {group['config']} has accuracy sd "
                         f"{_pct(group['accuracy_sd'])} over {group['runs']} runs.")
    return notes


def render_summary(runs: Sequence[Dict[str, Any]]) -> str:
    runs = usable_runs(runs)
    llm = [r for r in runs if r["config"]["engine"] == "llm"]
    stability = consistency(llm)
    lines = ["# ICAAIC results summary", "",
             "Generated by `scripts/results_tables.py` from `results/runs/`; do not edit by hand. "
             "All LLM runs use hybrid retrieval and the default `top_k`. Intervals are 95% Wilson intervals, "
             "which are wide at these sample sizes. Grounding violations count cases with a citation still "
             "unresolved after repair.", ""]
    for dataset in DATASETS:
        lines += [f"## {dataset.capitalize()}", ""]
        lines += dataset_table([r for r in runs if r["config"]["dataset"] == dataset], with_id=True) + [""]

    lines += ["## Consistency across repeat runs", ""]
    repeated = [g for g in stability if g["runs"] > 1]
    if repeated:
        lines += ["| Configuration | Runs | Accuracy (mean ± sd) | 95% CI (pooled) | Escalation recall (mean) "
                  "| Pairwise agreement | Cases that changed |", "|---|---|---|---|---|---|---|"]
        for g in repeated:
            low, high = g["accuracy_ci"]
            lines.append(f"| {g['config']} | {g['runs']} | {g['accuracy_mean']:.0%} ± {g['accuracy_sd']:.0%} "
                         f"| {low:.0%}–{high:.0%} | {_pct(g['escalation_recall_mean'])} "
                         f"| {_pct(g['pairwise_agreement'])} | {', '.join(sorted(g['unstable_cases'])) or 'none'} |")
    else:
        lines.append("No repeat runs yet, so there are no consistency figures to cite.")
    lines.append("")

    lines += ["## Worth checking", ""]
    lines += [f"- {note}" for note in flags(runs, stability)] or ["- Nothing was flagged automatically."]
    lines += ["- The rules engine and fact triggers were written with the pilot cases visible, so its pilot "
              "scores are in-sample.",
              "- Counterfactual labels were written by the project team and have not had second-annotator review.",
              "- Differences between prompt styles rest on very few cases; compare the intervals before "
              "claiming one style beats another.",
              "- Runs from before the escalation-prompt fix (`results/runs/pre_rule5_fix/`) and runs that lost a "
              "case to an API error (`results/runs/failed_api_error/`) are kept but left out of these tables.", ""]

    lines += ["## Not run yet", ""]
    missing = missing_configs(llm)
    lines += [f"- {dataset} · {model.split('/')[-1]} · {style}" for dataset, model, style in missing] or ["- Every grid cell has a run."]
    lines.append("")
    return "\n".join(lines)


def update_readme(runs: Sequence[Dict[str, Any]], path: Path = README) -> None:
    runs = usable_runs(runs)
    block = [README_START, ""]
    for dataset in DATASETS:
        block += [f"**{dataset.capitalize()}**", ""]
        block += dataset_table([r for r in runs if r["config"]["dataset"] == dataset], with_id=False) + [""]
    block.append(README_END)
    text = path.read_text(encoding="utf-8")
    pattern = re.compile(re.escape(README_START) + ".*?" + re.escape(README_END), re.DOTALL)
    if not pattern.search(text):
        raise SystemExit(f"{path} has no {README_START} marker")
    path.write_text(pattern.sub(lambda _: "\n".join(block), text), encoding="utf-8")


def main() -> None:
    runs = list_runs()
    (RESULTS_DIR / "icaaic_summary.md").write_text(render_summary(runs), encoding="utf-8")
    update_readme(runs)
    print("wrote results/icaaic_summary.md and the README results table")


if __name__ == "__main__":
    main()
