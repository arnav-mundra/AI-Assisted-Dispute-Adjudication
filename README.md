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
copy .env.example .env                # then add at least one provider key

python -m src.config.validate_env     # which providers are configured
python -m streamlit run app/main.py   # the application
```

Command-line equivalents of the same pipeline:

```bash
python -m src.evaluation.run_adjudication --case DG-001
python -m src.evaluation.run_adjudication --all --out runs/pilot_run.json
python -m src.validation.validate_pilot
python -m pytest
```

## Repo Structure

```
├── app/                          # Streamlit application
│   ├── main.py                   #   entry point: sidebar, navigation, status
│   └── ui/                       #   theme + adjudication and evaluation views
├── src/
│   ├── config/                   # paths, environment smoke test
│   ├── evidence_extraction/      # Phase 2 slot — case + evidence access
│   ├── clause_matching/          # Phase 3 slot — SLA clause parsing + retrieval
│   ├── reasoning_engine/         # Phase 4 slot — prompt, LLM call, validation
│   ├── llm/                      # provider abstraction (Groq active; Anthropic off)
│   ├── evaluation/               # Phase 6 slot — dataset runs, ground-truth comparison
│   └── validation/               # dataset structural validator
├── data/
│   ├── raw/pilot/                # pilot_cases.json — model input
│   ├── labeled/pilot/            # pilot_ground_truth.json — frozen reference labels
│   └── synthetic/                # generated cases (later phases)
├── docs/
│   ├── sla_policy.md             # the SLA the system adjudicates against
│   ├── phase0/                   # schemas, evaluation protocol, reproducibility
│   └── phase1/                   # scenario matrix, pilot schema, checklist
├── scripts/                      # ad-hoc provider connection checks
├── tests/
└── runs/                         # adjudication run outputs (gitignored)
```

## Pipeline

```
pilot case ──► evidence preparation ──► SLA clause retrieval ──► LLM adjudication
           ──► structured JSON ──► validation ──► UI result
```

Each stage is a package boundary, so later phases replace one component without
rewriting the application:

| Stage | Today | Later |
|---|---|---|
| `src/evidence_extraction/` | loads pre-structured pilot cases | Phase 2: extraction from chat/email/log documents |
| `src/clause_matching/` | lexical clause ranking + eligibility gates + cross-references | Phase 3: sentence-transformer embeddings + FAISS/Chroma |
| `src/reasoning_engine/` + `src/llm/` | one model per run, validated JSON contract | Phase 4: 3 prompting styles × 3 models |
| `src/evaluation/` | decision accuracy vs. frozen labels | Phase 6: F1, ROUGE/BERTScore, human comparison |

Guarantees that hold today:

- **No hard-coded outcomes.** No case ID maps to a decision anywhere; the model adjudicates.
- **No ground-truth leakage.** `build_case_view` raises if a label reaches a prompt, the
  adjudication view never imports the labels, and tests assert both.
- **Grounded citations.** Clause and evidence IDs returned by the model are checked against
  the SLA and the case. Unverifiable citations trigger one repair round-trip and are then
  surfaced as validation notes, never silently accepted.

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
| 2 | Evidence extraction module | Not started |
| 3 | Clause matching via embeddings | Lexical placeholder in place |
| 4 | Reasoning engine: 3 prompting styles × 3 models | Single-model slice working |
| 5 | Pipeline integration (FastAPI) | Not started |
| 6 | Evaluation vs. baselines + human comparison | Decision accuracy only |
| 7 | Error analysis, bias/consistency testing | Not started |
| 8 | Demo + report/poster finalization | Application working |

## Tech Stack

- **Reasoning models:** Groq-hosted open models (active), Claude (implemented, switched off)
- **Clause matching:** lexical today; Sentence-Transformers + FAISS/Chroma in Phase 3
- **Evaluation:** Pandas, scikit-learn, ROUGE/BERTScore
- **Application:** Streamlit

## Status

**Phase 0 — complete.** SLA v0.1, case/ground-truth schemas, evaluation protocol,
reproducibility rules.

**Phase 1 — pilot dataset complete.** 10 cases (5 damaged-goods, 5 COD-mismatch) generated
from `docs/phase1/SCENARIO_MATRIX.md`, with independent labels in
`data/labeled/pilot/pilot_ground_truth.json`. Structural consistency — schema conformance,
evidence/clause reference integrity, no leakage — is enforced by
`python -m src.validation.validate_pilot`. Remaining work (second-labeler review, scaling
beyond the pilot) is tracked in `docs/phase1/PHASE1_CHECKLIST.md`.

**Vertical slice — working.** The application runs the full pipeline end-to-end over the
pilot cases and reports decision, primary and supporting clauses, evidence relied upon,
rationale, resolution and confidence. The evaluation view scores a full pilot run against
the frozen labels.
