"""The rules engine must stay exactly as tagged `rules-engine-frozen-v1`.

The held-out cases were written against that version; any change to the engine after
the freeze would let it be tuned on the held-out set. Bugs go in
docs/phase2/RULES_ENGINE_ISSUES.md instead of being fixed in place.
"""

import hashlib
import shutil
import subprocess

import pytest

from src.config.paths import ROOT

FROZEN_TAG = "rules-engine-frozen-v1"
ENGINE = "src/reasoning_engine/rules_engine.py"
# Git blob id of rules_engine.py at the tag (LF line endings), so the check also runs
# without git or without the tag fetched.
FROZEN_BLOB_SHA = "9016d663472ea9f24b5420afdbdde4cd1791dbf0"


def _git_blob_sha(data: bytes) -> str:
    data = data.replace(b"\r\n", b"\n")
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def test_rules_engine_matches_frozen_blob():
    assert _git_blob_sha((ROOT / ENGINE).read_bytes()) == FROZEN_BLOB_SHA, (
        f"{ENGINE} differs from {FROZEN_TAG}; record suspected bugs in "
        "docs/phase2/RULES_ENGINE_ISSUES.md instead of editing the engine")


def _git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)


def test_rules_engine_matches_frozen_tag():
    if shutil.which("git") is None or _git("rev-parse", "--is-inside-work-tree").returncode != 0:
        pytest.skip("not a git checkout")
    tag = _git("rev-parse", "--verify", "--quiet", f"{FROZEN_TAG}^{{commit}}")
    assert tag.returncode == 0, f"tag {FROZEN_TAG} missing — run `git fetch --tags`"
    assert _git("rev-parse", f"{FROZEN_TAG}:{ENGINE}").stdout.strip() == FROZEN_BLOB_SHA
    diff = _git("diff", "--quiet", FROZEN_TAG, "--", ENGINE)
    assert diff.returncode == 0, f"{ENGINE} differs from {FROZEN_TAG} (working tree or commits)"
