#!/usr/bin/env bash
# Scaffolds a fixture with a KNOWN observability gap: an external call whose
# failure branch emits no log/metric/trace, plus a scratch-mode config so the
# run never writes and never interviews.
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

cat > src/fetcher.py <<'PY'
import logging

import requests

log = logging.getLogger(__name__)


def fetch(url):
    try:
        resp = requests.get(url, timeout=5)
        return resp.json()
    except requests.RequestException:
        # external call failed here — no log, no metric, no trace: a silent blind spot
        return None
PY
