"""Run LLM configs one at a time; stop before a run could exceed the daily budget.

Usage, from the repo root:
    python scripts/run_configs.py <model> <dataset>:<style>:<expected tokens> ...
"""
import json
import os
import subprocess
import sys
from pathlib import Path

PY = sys.executable
MODEL = sys.argv[1]
MARGIN = 1.15
PLAN = [tuple(item.split(":")) for item in sys.argv[2:]]
sys.path.insert(0, os.getcwd())
from src.llm.quota import snapshot  # noqa: E402


def child(*args):
    return subprocess.run([PY, *args], env={**os.environ, "PYTHONIOENCODING": "utf-8"})


for dataset, style, expected in PLAN:
    need = int(int(expected) * MARGIN)
    if child("scripts/groq_quota.py", MODEL).returncode != 0:
        print(f"STOP: probe says rate limited before {dataset}/{style}", flush=True)
        sys.exit(3)
    left = snapshot(MODEL).meter("tpd").remaining
    print(f"BUDGET: {left} tokens left (local log); {dataset}/{style} needs ~{need}", flush=True)
    if left < need:
        print(f"STOP: not enough budget for {dataset}/{style}", flush=True)
        sys.exit(4)
    pattern = f"*{MODEL.split('/')[-1]}*.json"  # lets two models run side by side
    before = set(Path("results/runs").glob(pattern))
    code = child("-m", "src.evaluation.experiment", "--engine", "llm", "--model", MODEL,
                 "--prompt-style", style, "--dataset", dataset, "--delay", "15").returncode
    new = set(Path("results/runs").glob(pattern)) - before
    if code or len(new) != 1:
        print(f"STOP: run failed, exit {code}, new files {new}", flush=True)
        sys.exit(5)
    run = json.loads(new.pop().read_text(encoding="utf-8"))
    tokens = sum(sum((p.get("usage") or {}).values()) for p in run["predictions"])
    print(f"DONE: {run['run_id']} tokens={tokens} failures={len(run['failures'])} dense={run['config'].get('dense')}",
          flush=True)
    if run["failures"]:
        print("STOP: run had failed cases", flush=True)
        sys.exit(6)
print("ALL PLANNED RUNS DONE", flush=True)
