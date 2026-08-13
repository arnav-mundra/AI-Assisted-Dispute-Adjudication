# AI-Assisted Dispute Adjudication for D2C Delivery Operations

Academic research project investigating whether an LLM-based reasoning system can
resolve **damaged-goods** and **COD (cash-on-delivery) mismatch** disputes in D2C
e-commerce — using unstructured evidence (chat/email), structured evidence
(pickup/delivery timestamps, logs), and SLA policy text — as accurately and
consistently as a human support agent.

This is a research project, not a product build. See `docs/` for the research
brief, literature survey, SLA document, and evaluation methodology.

## Research Question

Can an LLM-based reasoning system resolve D2C damaged-goods and COD-mismatch
disputes — grounded in SLA clauses and multi-source evidence — as accurately and
consistently as a human adjudicator, and where does it succeed/fail?

## Repo Structure

```
d2c-dispute-adjudication/
├── data/
│   ├── raw/          # reference datasets (Olist, Twitter CS, CFPB, UNFAIR-ToS, LEDGAR)
│   ├── synthetic/     # GPT-4-generated synthetic dispute cases
│   └── labeled/        # manually labeled ground-truth cases
├── docs/
│   ├── sla_policy.md          # draft SLA document (Phase 0 deliverable)
│   ├── research_brief.md      # (to be added)
│   └── literature_review.md   # (to be added)
├── src/
│   ├── evidence_extraction/    # chat/email/log -> structured JSON
│   ├── clause_matching/        # embeddings + FAISS/ChromaDB retrieval
│   ├── reasoning_engine/       # LLM reasoning (3 prompting styles x 3 models)
│   └── evaluation/             # accuracy, F1, ROUGE/BERTScore, bias analysis
├── notebooks/          # exploratory analysis
├── demo/                # Streamlit demo app
└── tests/
```

## Build Roadmap

| Phase | Focus | Timeline |
|---|---|---|
| 0 | Setup + schema + ground truth + evaluation protocol + reproducibility | Immediate |
| 1 | Dataset construction: synthetic cases + manual ground-truth labeling | Aug'26 (Wks 1-3) |
| 2 | Evidence extraction module | Aug'26 (Wk 4) |
| 3 | Clause-matching module | Aug-Sept'26 (Wk 5) |
| 4 | LLM reasoning engine (3 prompting styles x 3 models) | Sept'26 (Wks 6-7) |
| 5 | Pipeline integration (FastAPI end-to-end) | Sept'26 (Wk 7-8) |
| 6 | Evaluation vs. baselines + human comparison | Sept-Oct'26 (Wks 8-9) |
| 7 | Error analysis + bias/consistency testing | Oct'26 (Wk 9-10) |
| 8 | Demo (Streamlit) + report/poster finalization | Oct-Nov'26 (Wks 10-12) |

## Tech Stack

- **Reasoning models:** GPT-4o-mini/GPT-4 (primary), Claude API, Mistral-7B/Llama-3-8B
- **Evidence extraction:** Python, spaCy/NLTK, structured prompt templates
- **Clause matching (RAG):** Sentence-Transformers (all-mpnet-base-v2) + FAISS/ChromaDB
- **Backend:** FastAPI + SQLite/PostgreSQL
- **Evaluation:** Pandas, scikit-learn, ROUGE/BERTScore
- **Demo:** Streamlit

## Setup

```bash
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env           # then fill in your API keys
```

## Bare-Bones Demo (early, for progress checks)

A minimal working Streamlit demo exists at `demo/app.py`, built early (out of
roadmap order) for progress-check purposes. It skips the not-yet-built Evidence
Extraction (Phase 2) and Clause Matching (Phase 3) modules by passing the full
SLA document directly into the reasoning prompt — so it's a real, working
end-to-end call to an LLM, not a mockup, but not the final architecture.

```bash
streamlit run demo/app.py
```

It will be superseded by the full pipeline (Evidence Extraction -> Clause
Matching -> Reasoning Engine -> Evaluation) in Phase 8.

## Status

Phase 0 in progress — repository scaffolded, SLA v0.1 drafted, case/ground-truth
schemas and evaluation protocol defined, and reproducibility checks added.
The bare-bones demo remains a progress-check prototype and is not the research pipeline.
