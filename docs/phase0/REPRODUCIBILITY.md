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

## Dataset and test checks

From the repository root, after installing the requirements:

```bash
python -m src.validation.validate_pilot   # structural validation of the pilot dataset
python -m pytest -v                       # Phase 0 + Phase 1 checks
```

`pytest.ini` pins the rootdir and puts the repository root on `sys.path`, so the
suite runs identically from any working directory.

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
