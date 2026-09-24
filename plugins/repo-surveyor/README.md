# repo-surveyor

Three staff-level **survey** lenses that scout a codebase and emit **evidence-cited findings
reports** — never a vague "you should refactor," always a `path:line` + severity + a labeled
estimate. Read-only by default; each skill writes only its own findings artifact. Published to
**Claude Code**, **Cursor**, and **Codex** from one shared component tree.

```shell
/plugin marketplace add davcs86/agent-plugins
/plugin install repo-surveyor@davcs86-agent-plugins
```

## The three lenses

| Skill | Persona | Use it when |
|---|---|---|
| **`debt-radar`** | Staff software architect | You want the real technical debt found and *triaged* — code smells, dead code, swallowed/silenced errors, brittle patterns — each confirmed with a `path:line`, a severity, a benefit, a T-shirt LOE, and an explicit **do-vs-not-do** trade-off. A `verify` mode re-checks whether a past finding (or a free-text issue) is now resolved against the current code. |
| **`feature-gap`** | Product-manager × engineer hybrid | You want the **user-facing surface** (UI routes, MCP tool schemas, CLI commands, public/exported API) analyzed for feature gaps, cross-surface inconsistencies, low-discoverability features, additive feature ideas, and the **product metrics** worth tracking per feature. Static and recommendation-only — it maps the surface, it does not measure live traffic. |
| **`signal-map`** | Observability × data-science hybrid | You want **surgical** instrumentation guidance — the minimum logs/metrics/traces at the maximum-leverage points (error branches, hot paths, feature boundaries) so failures are visible and feature performance is measurable. Cites the exact `path:line`, the signal type, and the question each signal answers. |

## What every finding guarantees

Every report is governed by a shared **Floor / Norms** discipline (`RS-*` / `RS-N*`):

- **Nothing is invented (RS-1).** The *existence* of a defect, gap, or blind spot cites concrete
  evidence — a `path:line`, a symbol, a config key, or a commit. An ungrounded suspicion lands
  under `## Needs confirmation`, phrased as a question, never asserted.
- **Estimates are labeled, not disguised (RS-4).** LOE, benefit, and impact are ordinal T-shirt
  estimates with stated assumptions — the defect is cited, the estimate is flagged as a
  projection.
- **Trade-offs run both ways (RS-N3).** Every recommendation states the cost of doing it *and* the
  cost of not doing it.
- **Ranked by leverage (RS-N2).** Within a severity, findings sort by impact ÷ LOE, so you act
  top-down.
- **Read-only by default (RS-2).** A survey writes only its findings artifact under the configured
  output dir; it never mutates your source.

## Severity

Each finding carries a severity. On the first run in a repo the skill **detects the repo's own
priority system** (issue-template labels, `CONTRIBUTING`, existing `P0`/`S1`/`sev*` conventions)
and uses it. Absent one, it falls back to an **Eisenhower (urgent × important) → P0–P3** mapping —
see `skills/*/reference/severity-rubric.md`.

## Config

All three skills share one committable config, `.agents/repo-surveyor.json` at the repo root.
On the first run (when it is absent) the skill asks where findings should be written —
`.repo-surveyor/`, `./docs/repo-surveyor/`, or an existing docs directory it detects — and stores
the choice. `outputDir: null` is scratch mode: findings are presented inline and nothing is
written.

## Development

```shell
# structural integrity of this plugin (manifests, frontmatter, shared-copy parity, subagents)
python3 plugins/repo-surveyor/scripts/validate.py
python3 plugins/repo-surveyor/scripts/validate.py --self-test
```
