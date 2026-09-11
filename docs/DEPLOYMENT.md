# Deploying to Streamlit Community Cloud

Entry point: `app/main.py`. Dependency file: `requirements.txt` (repo root).

## The failure this fixes

Community Cloud currently provisions **Python 3.14**. Two pins in the old
`requirements.txt` had no cp314 wheels, so pip fell back to compiling from
source inside a container without build headers:

| Pin | Problem on Python 3.14 |
|---|---|
| `streamlit==1.39.0` | requires `pillow<11`; the first Pillow with a cp314 wheel is **11.3.0**, so Pillow was compiled from source and failed with `RequiredDependencyException: zlib` |
| `pandas==2.2.3` | first pandas with a cp314 wheel is **2.3.3**; 2.2.3 offers only an sdist, so the build stalled at `Preparing metadata (pyproject.toml)` |

Both are now floored at versions that publish cp314 wheels. Verified with a
wheels-only resolution for both interpreters:

```bash
pip install --dry-run --python-version 3.14 --only-binary=:all: --target /tmp/x -r requirements.txt
pip install --dry-run --python-version 3.11 --only-binary=:all: --target /tmp/x -r requirements.txt
```

Both resolve with no source builds.

## Choosing the Python version

`.python-version` in the repo root declares **3.11**, the version this project
is developed and tested against.

Be aware of how Community Cloud actually decides:

- The authoritative control is the **"Advanced settings" dialog at deploy
  time**. Pick the Python version there.
- **Python cannot be changed after deployment.** To change it you must delete
  the app and redeploy it, then re-enter your secrets.
- `runtime.txt` is **not** honoured — multiple 2026 reports show Cloud ignoring
  it and provisioning its own default (e.g.
  [streamlit#15326](https://github.com/streamlit/streamlit/issues/15326)). Do
  not rely on it.

Because the version pin cannot be guaranteed from inside the repo, the
requirements are written to install cleanly on **3.11 through 3.14**. Pinning
3.11 in Advanced settings is preferred, but the deploy no longer depends on it.

## Secrets

Set `GROQ_API_KEY` in the app's **Secrets** (Settings → Secrets), in TOML form:

```toml
GROQ_API_KEY = "gsk_..."
```

`ANTHROPIC_API_KEY` is optional — Anthropic is implemented but listed in
`DISABLED_PROVIDERS` in `src/llm/provider.py`, so it will not run until that
entry is removed.

Never commit `.env`; it is gitignored.

## Only one dependency file

Community Cloud searches `uv.lock`, `Pipfile`, `environment.yml`,
`requirements.txt`, `pyproject.toml` in that order and uses the first it finds.
This repo intentionally ships only `requirements.txt`. Do not add another.
