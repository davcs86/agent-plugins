#!/usr/bin/env bash
# Scaffolds a fixture with a KNOWN user-facing surface defect: an asymmetric CRUD
# API (create + list, no delete) and an undocumented CLI command, plus a
# scratch-mode config so the run never writes and never interviews.
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
  "userFacingGlobs": ["src/**"],
  "created": "unknown"
}
JSON

cat > src/routes.js <<'JS'
// HTTP API — item resource
router.post('/items', createItem);   // create
router.get('/items', listItems);     // list
// NOTE: no DELETE /items/:id — an item cannot be removed once created.

// CLI commands
program
  .command('sync')
  .description('Sync items from the remote source')
  .action(sync);

program
  .command('purge')            // no .description() — absent from --help output
  .action(purge);
JS
