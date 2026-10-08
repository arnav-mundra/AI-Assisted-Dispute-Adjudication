# AI-Assisted Dispute Adjudication for D2C Delivery Operations

Academic research project investigating whether an LLM-based reasoning system can
resolve **damaged-goods** and **COD (cash-on-delivery) mismatch** disputes in D2C
e-commerce — using unstructured evidence (chat/email), structured evidence
(pickup/delivery timestamps, logs), and SLA policy text — as accurately and
consistently as a human support agent.

## Research Question

Can an LLM-based reasoning system resolve D2C damaged-goods and COD-mismatch
disputes — grounded in SLA clauses and multi-source evidence — as accurately and
consistently as a human adjudicator, and where does it succeed/fail?

## Quick Start

```bash
python -m venv venv
venv\Scripts\activate                 # Windows;  source venv/bin/activate elsewhere
pip install -r requirements.txt
copy .env.example .env                # add GROQ_API_KEY to use the LLM (optional)

python -m streamlit run app/main.py   # the application
```

The application works **without any API key**: rulings then come from the deterministic
SLA rules engine, and extraction, retrieval, the what-if explorer and evaluation all run
offline. With `GROQ_API_KEY` set, the LLM decides and the rules engine cross-checks it.

Command line:

```bash
python -m src.evaluation.run_adjudication --case DG-001                    # one case, LLM
python -m src.evaluation.run_adjudication --case DG-001 --engine rules     # one case, offline
python -m src.evaluation.experiment --engine rules                          # score rules engine
python -m src.evaluation.experiment --engine rules --dataset counterfactual
python -m src.evaluation.experiment --engine llm --all-styles              # Phase 4 prompt grid
python -m src.evaluation.counterfactuals                                    # rebuild stress set
python -m src.validation.validate_pilot
python -m src.evaluation.experiment --engine llm --prompt-style facts --repeats 3   # consistency
python -m src.evaluation.analysis                                           # errors, guard, CIs -> results/error_analysis.md
python -m src.validation.agreement export --dataset pilot                   # blind second-labeller CSV
python -m src.validation.agreement compare --dataset pilot --second <filled.csv>   # Cohen's kappa
python -m pytest
```

Scored runs are written to `results/runs/` and appear in the app's Evaluation view.

## Repo Structure

```
├── app/                          # Streamlit application
│   ├── main.py                   #   entry point: sidebar settings + navigation
│   └── ui/                       #   overview, adjudicate, new dispute, what-if,
│                                 #   evaluation, SLA policy, theme
├── src/
│   ├── evidence_extraction/      # Phase 2 — case loading + fact extraction (extractor.py)
│   ├── clause_matching/          # Phase 3 — SLA parsing + lexical/BM25/dense/hybrid retrieval
│   ├── reasoning_engine/         # Phase 4 — LLM adjudicator, 3 prompt styles, rules engine
│   ├── llm/                      # provider abstraction (Groq active; Anthropic off)
│   ├── evaluation/               # Phase 6 — metrics, experiments, datasets, counterfactuals
│   ├── validation/               # dataset structural validator
│   └── config/                   # paths, environment smoke test
├── data/
│   ├── raw/pilot/                # pilot_cases.json — model input
│   ├── labeled/pilot/            # pilot_ground_truth.json — frozen reference labels
│   └── synthetic/counterfactual/ # 16-case counterfactual stress set + its labels
├── results/runs/                 # scored experiment runs (one JSON per run)
├── docs/                         # SLA, phase docs, deployment
└── tests/                        # 58 offline tests (no network calls)
```

## Pipeline

```
case evidence ─► evidence extraction ─► clause retrieval ─► reasoning engine ─► validation ─► ruling
                 (source-linked facts)   (hybrid + fact      (LLM, 3 prompt      (grounding     + rules
                                          triggers)           styles)             checks)        cross-check
```

| Stage | Module | What it does |
|---|---|---|
| Evidence extraction | `src/evidence_extraction/extractor.py` | Reads chat/email, agent statements, PoD photo descriptions, delivery and cash logs into typed facts (reporting window, PoD state with negation handling, damage specificity, unboxing, hub exceptions, COD amounts). Every fact names the evidence IDs it came from. |
| Clause retrieval | `src/clause_matching/clause_retrieval.py` | Lexical, BM25, optional dense embeddings, and a hybrid (reciprocal-rank fusion) that adds clauses whose trigger condition an extracted fact satisfies. Priority rules, eligibility gates and cross-references are always added. |
| Reasoning engine | `src/reasoning_engine/adjudicator.py` | One LLM call per case, in one of three prompting styles: `zero_shot`, `facts` (adds the extracted facts) and `cot` (facts + recorded analysis steps). Output is a validated JSON ruling. |
| Rules engine | `src/reasoning_engine/rules_engine.py` | The SLA as an explicit decision procedure over the extracted facts, with a step-by-step trace. Used as the offline fallback, a research baseline, and a cross-check on every LLM ruling. |
| Evaluation | `src/evaluation/metrics.py`, `experiment.py` | Decision accuracy, macro-F1, escalation recall/precision, clause P/R/F1, primary-clause accuracy, resolution and refund accuracy, decisive-evidence recall, grounding-violation rate, Brier score, rules agreement; majority-class and random baselines. |

Guarantees that hold today:

- **No hard-coded outcomes.** No case ID maps to a decision anywhere — not in the
  extractor, the retriever, the rules engine or the prompts.
- **No ground-truth leakage.** `build_case_view` raises if a label reaches a prompt, the
  adjudication view never imports the labels, and labels are joined to predictions only
  after a run completes. Tests assert all three.
- **Grounded citations.** Clause and evidence IDs returned by the model are checked against
  the SLA and the case. Unverifiable citations trigger one repair round-trip and are then
  surfaced as validation notes, never silently accepted.
- **Procedural clauses are not scored.** `SLA-PRI-02` ("every ruling must cite a clause")
  is excluded from clause scoring on both sides, so COD-005's label no longer penalises a
  model for following the instruction not to cite it. The frozen label file is unchanged.

## Results (offline, reproducible without a key)

| Configuration | Dataset | Decision acc. | Escalation recall | Clause F1 | Refund acc. |
|---|---|---|---|---|---|
| Rules engine | Pilot (10) | 100% | 100% | 82% | 100% |
| Rules engine | Counterfactual (16) | 100% | 100% | 62% | 100% |
| Majority class (always approve) | Pilot | 50% | 0% | — | — |

Governing-clause recall on the pilot set: hybrid retrieval with fact triggers reaches
100% at k=1–4 (≈12–14 clauses in context); lexical ranking alone needs k=12 (≈17 clauses)
for 96%.

**Read these numbers carefully.** The rules engine and the fact triggers were written with
the 10 pilot cases visible, so pilot scores are in-sample. The counterfactual set was built
to be a fairer test (one SLA-relevant fact changed per case, label written from the SLA
text for that change), but its labels were written by the same team — have a second
annotator review them before reporting. LLM numbers come from running
`python -m src.evaluation.experiment --engine llm --all-styles` with a key.

## Providers

Selected by model name; only providers whose key is present can run, and the UI reports
the rest as unavailable rather than failing.

| Provider | Env var | Models | State |
|---|---|---|---|
| Groq | `GROQ_API_KEY` | openai/gpt-oss-120b, qwen/qwen3.8-27b, openai/gpt-oss-20b | Active |
| Anthropic | `ANTHROPIC_API_KEY` | claude-opus-5, claude-sonnet-5, claude-haiku-4-5 | Implemented, switched off |

Anthropic is fully implemented but listed in `DISABLED_PROVIDERS` in
`src/llm/provider.py`: its models are absent from the picker and it refuses to run even
with a key set. Remove `"anthropic"` from that set to re-enable it — that is the only
change required.

Add a provider by subclassing `LLMProvider` in `src/llm/` and calling `register(...)`.
Optional `ADJUDICATION_MODEL` pins the default. Never commit `.env`.

## Build Roadmap

| Phase | Focus | Status |
|---|---|---|
| 0 | Setup, schemas, ground-truth protocol, reproducibility | Complete |
| 1 | Pilot dataset: 10 cases + frozen reference labels | Complete (pilot) |
| 2 | Evidence extraction module | Rule-based extractor complete; spaCy/NER variant optional |
| 3 | Clause matching | Lexical, BM25, hybrid + fact triggers complete; dense embeddings optional (`requirements-ml.txt`) |
| 4 | Reasoning engine: 3 prompting styles × models | 3 styles implemented; multi-model runs pending keys |
| 5 | Pipeline integration | Integrated in the Streamlit app; FastAPI not started |
| 6 | Evaluation vs. baselines + human comparison | Full metric suite, baselines, counterfactual set; human comparison pending |
| 7 | Error analysis, bias/consistency testing | What-if explorer + counterfactual set in place |
| 8 | Demo + report/poster finalization | Demo application complete |

## Tech Stack

- **Reasoning models:** Groq-hosted open models (active), Claude (implemented, switched off)
- **Rules engine:** explicit SLA decision procedure (pure Python)
- **Evidence extraction:** regex + lexicons with negation handling (pure Python)
- **Clause matching:** lexical + BM25 + reciprocal-rank fusion + fact triggers; optional
  Sentence-Transformers (`pip install -r requirements-ml.txt`)
- **Evaluation:** custom metrics module, Pandas, Altair
- **Application:** Streamlit
