"""Run an adjudication configuration over a dataset, score it, and save the run.

    python -m src.evaluation.experiment --engine rules
    python -m src.evaluation.experiment --engine llm --prompt-style facts
    python -m src.evaluation.experiment --engine llm --all-styles          # Phase 4 grid
    python -m src.evaluation.experiment --engine rules --dataset counterfactual

Each run is written to results/runs/<run_id>.json with its configuration, every
prediction, and the metrics, so the Evaluation view can compare runs side by side.
Ground truth is loaded only after all predictions are made.
"""

from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from src.config.paths import EXPERIMENT_RUNS_DIR
from src.evaluation.datasets import DATASETS, load_dataset
from src.evaluation.metrics import baselines, format_summary, score_run
from src.reasoning_engine.adjudicator import PROMPT_STYLES, adjudicate, default_model
from src.reasoning_engine.rules_engine import RULES_MODEL

IST = timezone(timedelta(hours=5, minutes=30))


def run_label(config: Dict[str, Any]) -> str:
    if config["engine"] == "rules":
        return "Rules engine (deterministic SLA)"
    return f"{config['model']} · {config['prompt_style']}"


def run_experiment(
    engine: str = "rules",
    model: Optional[str] = None,
    prompt_style: str = "facts",
    retrieval: str = "hybrid",
    top_k: int = 12,
    dataset: str = "pilot",
    delay: float = 0.0,
    progress: Optional[Callable[[int, int, str], None]] = None,
    save: bool = True,
) -> Dict[str, Any]:
    cases, labels = load_dataset(dataset)
    model = RULES_MODEL if engine == "rules" else (model or default_model())

    predictions: List[Dict[str, Any]] = []
    failures: List[Dict[str, str]] = []
    started = time.perf_counter()

    for index, case in enumerate(cases):
        if progress:
            progress(index, len(cases), case["case_id"])
        if index and delay and engine != "rules":
            time.sleep(delay)
        try:
            result = adjudicate(case, model=model, top_k=top_k, prompt_style=prompt_style,
                                retrieval=retrieval, engine=engine)
            predictions.append(result.to_dict())
        except Exception as exc:  # one failed case must not lose the run
            failures.append({"case_id": case["case_id"], "error": str(exc)[:300]})

    # Labels joined only now, after every prediction is made.
    metrics = score_run(predictions, labels)
    created = datetime.now(IST)
    config = {
        "engine": engine,
        "model": model,
        "prompt_style": prompt_style if engine != "rules" else "",
        "retrieval": retrieval,
        "top_k": top_k,
        "dataset": dataset,
    }
    run = {
        "run_id": f"{created.strftime('%Y%m%d-%H%M%S')}_{dataset}_{engine}"
                  + (f"_{model.split('/')[-1]}_{prompt_style}" if engine != "rules" else ""),
        "label": run_label(config),
        "created_at": created.isoformat(timespec="seconds"),
        "config": config,
        "wall_seconds": round(time.perf_counter() - started, 2),
        "predictions": predictions,
        "failures": failures,
        "metrics": metrics,
        "baselines": baselines(labels),
    }
    if save:
        save_run(run)
    return run


def save_run(run: Dict[str, Any]) -> Path:
    EXPERIMENT_RUNS_DIR.mkdir(parents=True, exist_ok=True)
    path = EXPERIMENT_RUNS_DIR / f"{run['run_id']}.json"
    path.write_text(json.dumps(run, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    return path


def list_runs(dataset: Optional[str] = None) -> List[Dict[str, Any]]:
    """Saved runs, newest first. Corrupt files are skipped."""
    runs = []
    if EXPERIMENT_RUNS_DIR.exists():
        for path in EXPERIMENT_RUNS_DIR.glob("*.json"):
            try:
                run = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if dataset and run.get("config", {}).get("dataset") != dataset:
                continue
            run["_path"] = str(path)
            runs.append(run)
    return sorted(runs, key=lambda r: r.get("created_at", ""), reverse=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run and score an adjudication experiment.")
    parser.add_argument("--engine", choices=["rules", "llm"], default="rules")
    parser.add_argument("--model", default=None)
    parser.add_argument("--prompt-style", choices=sorted(PROMPT_STYLES), default="facts")
    parser.add_argument("--all-styles", action="store_true", help="Run every prompt style (LLM only).")
    parser.add_argument("--retrieval", choices=["lexical", "bm25", "dense", "hybrid"], default="hybrid")
    parser.add_argument("--top-k", type=int, default=12)
    parser.add_argument("--dataset", choices=sorted(DATASETS), default="pilot")
    parser.add_argument("--delay", type=float, default=3.0, help="Seconds between LLM calls (throttling).")
    args = parser.parse_args()

    styles = sorted(PROMPT_STYLES) if args.all_styles and args.engine == "llm" else [args.prompt_style]
    for style in styles:
        def show(i: int, n: int, case_id: str) -> None:
            print(f"  [{i + 1}/{n}] {case_id}", flush=True)

        print(f"\n=== {args.engine} · {args.model or ''} · {style} · {args.dataset} ===")
        run = run_experiment(engine=args.engine, model=args.model, prompt_style=style,
                             retrieval=args.retrieval, top_k=args.top_k, dataset=args.dataset,
                             delay=args.delay, progress=show)
        print(format_summary(run["metrics"]))
        if run["failures"]:
            print(f"failed cases: {[f['case_id'] for f in run['failures']]}")
        print(f"saved: results/runs/{run['run_id']}.json")


if __name__ == "__main__":
    main()
