# Phase 0 — Reproducibility and Environment

## Environment

Recommended Python version: **3.11**.

Create an isolated environment:

```bash
python -m venv .venv
source .venv/bin/activate       # macOS/Linux
# .venv\\Scripts\\activate    # Windows PowerShell
pip install --upgrade pip
pip install -r requirements.txt
```

## Environment variables

Copy `.env.example` to `.env` and provide only the API keys required by the experiment.
Never commit `.env`.

## Configuration recording

Each experiment should record:
- Git commit hash
- SLA version
- model/provider and model identifier
- prompt version
- retrieval model/index version
- dataset version
- random seed where applicable
- temperature and other inference settings

## Data policy

Real customer PII must not be placed in the synthetic research dataset.
Synthetic cases should use fictional names, order IDs, phone numbers and addresses.
