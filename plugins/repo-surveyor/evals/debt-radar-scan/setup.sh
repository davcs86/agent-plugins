#!/usr/bin/env bash
# Scaffolds a tiny fixture repo with a KNOWN swallowed error and a dead function,
# plus a scratch-mode repo-surveyor config so the run never writes and never
# hits the first-run interview.
set -euo pipefail

mkdir -p src .agents

cat > .agents/repo-surveyor.json <<'JSON'
{
  "version": 1,
  "outputDir": null,
  "findings": {
    "debt-radar": "debt-radar-findings.md",
    "feature-gap": "feature-gap-findings.md",
    "signal-map": "signal-map-findings.md"
  },
  "userFacingGlobs": [],
  "created": "unknown"
}
JSON

cat > src/sample.py <<'PY'
import logging

log = logging.getLogger(__name__)


def load_config(path):
    try:
        with open(path) as fh:
            return fh.read()
    except Exception:
        pass  # swallowed: a missing/unreadable config is silently ignored


def _unused_legacy_helper(x):
    # dead: nothing references this helper
    return x * 2


def run(path):
    return load_config(path)
PY
