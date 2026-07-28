# agent-plugins — Constitution

Derived by `/context-constitution` (context-forge) on 2026-07-28. This file captures the
**non-obvious** — patterns this repo follows but never wrote down, the places that break those
patterns, the contracts between its parts, and the scars behind them — the things an agent would
otherwise miss and get wrong. It does **not** restate what the docs already say or CI already
enforces (see `## Pointers`). Refresh by re-running `/context-constitution refresh`.

## Floor (`AP-*`) — never-do, non-overridable

| ID | Rule | Why | Evidence |
|---|---|---|---|
| **AP-01** | Every `SKILL.md` frontmatter value containing `: ` (colon-space) must be **quoted**. | An unquoted YAML scalar containing `: ` parses as a nested mapping, so the *whole* frontmatter block fails to parse and every field — `name`, `description`, `allowed-tools` — is silently dropped at load time. The skill appears to install and then behaves as if it has no metadata at all. Inherited from the upstream plugin and invisible to the then-regex-only validator, which checked key *presence* only. | commit `482f565`; guard at `plugins/design-buddy/scripts/validate.py:97-99`, self-test at `:213` |
| **AP-02** | Never add a `version` field to a plugin entry inside a marketplace catalog. `plugin.json` is the sole authority. | A catalog copy is a second source of truth that nothing validates — `validate_manifests.py:176` reads `version` only from the plugin manifest, so a stale catalog copy would drift silently and forever. Removed from both catalogs in `482f565` per the marketplace docs. | commit `482f565`; `scripts/validate_manifests.py:176` |

## Rules (`AP-*`) — binding, easy-to-miss conventions

The **Example** column points at the one site that best demonstrates the rule.

| ID | Rule | Why | Evidence | Example (canonical `path:line`) |
|---|---|---|---|---|
| **AP-10** | A **remote** (`github`/`git`) plugin source bypasses *every* check in the marketplace validator — version parity, membership parity, and the README-listing check alike. Treat a remote entry as unvalidated. | `_plugin_dir_name` returns `None` for a non-string source, and the entry loop `continue`s **before** `tool_members[label].add(name)` — so the plugin never enters the membership set that all three cross-repo checks are computed from. The skip is deliberate for the on-disk tree check; that it also silently disables the other three is not obvious from reading any one of them. | `scripts/validate_manifests.py:90-91`, `:150-155` | `scripts/validate_manifests.py:151` |
| **AP-11** | The two catalogs are **not** byte-parallel at the top level: Claude's catalog-level `description` is a top-level key; Cursor's is nested under `metadata`. Follow each catalog's existing shape — do not "fix" one to match the other. | The validator checks only `name` and `plugins` at catalog level, so this asymmetry is invisible to the build and survives every green run. It originates in the scaffold: `16ca7ea` created both with a `metadata` object, and only the Claude catalog was later flattened. | `.claude-plugin/marketplace.json:7` vs `.cursor-plugin/marketplace.json:7-9`; checks at `scripts/validate_manifests.py:123,126` | `.cursor-plugin/marketplace.json:7-9` |
| **AP-12** | A plugin's `description` exists in **three** files — both catalogs and its own `plugin.json` — and nothing keeps them in sync. Edit all three together. | Two of the three current plugins have already drifted: design-buddy's `plugin.json` description carries detail the catalogs lack, and context-forge's differ in both opening phrase and category list. No check covers `description` anywhere. | `.claude-plugin/marketplace.json:14` vs `plugins/design-buddy/.claude-plugin/plugin.json:5` | `plugins/strat-lab/.claude-plugin/plugin.json:5` (the one still in sync) |
| **AP-13** | The PostToolUse validation hook fires **only** for manifest paths. Editing a `SKILL.md`, a shared `reference/` copy, `README.md`, or the validator itself triggers nothing — run the validators by hand after those edits. | `RELEVANT_RE` matches `*-plugin/(marketplace\|plugin).json` and returns 0 for everything else. The repo's own description of the hook ("after any `Edit`/`Write` to a `*-plugin/…json` file") is accurate but easy to read as "edits are validated", which is the trap: the per-plugin validator only auto-runs when a *manifest inside that plugin* changes, never when its skill tree changes. | `scripts/hooks/validate_on_edit.py:19`, `:37-38`, `:41-44` | `scripts/hooks/validate_on_edit.py:19` |
| **AP-14** | The hook's configured command is **repo-root-relative**, so it only resolves when the session's working directory is the repo root. A `cd` into a subdirectory breaks every subsequent edit. | Observed live while forging this constitution: after a `cd` into `plugins/design-buddy/skills`, three consecutive edits failed with `python3: can't open file '…/plugins/design-buddy/skills/scripts/hooks/validate_on_edit.py'`. The edits themselves had already been written, so the failure is noisy but not corrupting — still, it reads like a broken hook rather than a wrong cwd. | `.claude/settings.json:9` | `.claude/settings.json:9` |

## Norms (`AP-*`) — defaults & asymmetry guidance

| ID | Norm | Why | Evidence | Example (canonical `path:line`) |
|---|---|---|---|---|
| **AP-20** | Every validator ships a `--self-test` suite built on throwaway fixture repos, **including a positive clean-fixture case**, and CI runs `--self-test` *before* the validator itself. | Running the self-test first means a broken check fails loudly rather than passing vacuously; the clean fixture is what catches a check that fires on everything. Follow this shape for any new script. | `.github/workflows/validate.yml:21-22`, `:29-30`; `scripts/validate_manifests.py:322-332` | `scripts/validate_manifests.py:324-332` |
| **AP-21** | Plugins version **independently** of each other and of the catalogs. The catalogs' own `version` tracks nothing and is not bumped when a plugin ships. | It has read `1.0.0` since the first plugin was imported (`449d884`) and has never changed across every plugin addition and version bump since — including this one. Bumping it would imply a coupling that does not exist. | `.claude-plugin/marketplace.json:8`; `git log -- .claude-plugin/marketplace.json` | `.claude-plugin/marketplace.json:8` |
| **AP-22** | CI's per-plugin validator loop uses `shopt -s nullglob`, so a plugin that ships **no** `scripts/validate.py` is silently skipped rather than failing. Shipping one is a convention, not a gate. | Without `nullglob` the loop would run against the literal unexpanded glob and fail; with it, a plugin can ship no validator and CI stays green. All three current plugins ship one — keep that up by convention, since nothing enforces it. | `.github/workflows/validate.yml:26-31` | `plugins/strat-lab/scripts/validate.py` |
| **AP-23** | `disable-model-invocation: true` is decided **per skill**, not applied by default. Set it when a skill writes outside its own artifact directory or mutates external state; omit it otherwise. | A skill the model can never trigger is reachable only by someone who already knows its name — that is a real discoverability cost, and paying it is only justified by real side effects. `context-constitution` (prepends to the host's `CLAUDE.md`) and `backtest` (mutates strategies on a live backend) keep it; the other four dropped it in design-buddy 2.0.0 / context-forge 0.5.0. | `docs/adding-a-plugin.md` §"Deciding `disable-model-invocation`"; `plugins/context-forge/skills/context-constitution/SKILL.md:6` | `plugins/context-forge/skills/context-scrubber/SKILL.md` (dropped, with an implicit-invocation guard in the body) |

## Gotchas & scars

- **A plugin can pass every manifest check and still ship invisible.** `strat-lab` was registered
  in both catalogs, carried valid matching semver, and had a complete plugin tree — and was absent
  from the README, so nobody reading the front page knew it existed. The README-listing check
  (`check_readme_mentions`) exists *because* of that miss, and caught it on the very next run.
  Evidence: `scripts/validate_manifests.py:219-233` + commit `a0bcafa`.
- **`removeprefix`, not `lstrip`, when stripping `"./"`.** `lstrip` strips a character *set*, so
  `lstrip("./")` on `./.hidden-plugin` eats the leading dot of the directory name too. Fixed in
  `a0bcafa` with an inline comment and a dedicated self-test case that would catch a regression.
  Evidence: `scripts/validate_manifests.py:84-88` + self-test case at `:393-395`.
- **Skill names are a global namespace under Cursor.** Cursor invokes commands flat, with no
  `plugin:` prefix to disambiguate, so a skill named `review` collides with the host tool's own
  `/review`. design-buddy 2.0.0 renamed `design`/`plan`/`review` →
  `design-debate`/`impl-plan`/`plan-review` for exactly this reason. Evidence:
  `docs/adding-a-plugin.md` §"One tree, two tools"; `plugins/design-buddy/README.md` (2.0.0 note).

## Candidate rules (unverified)

| Candidate | Why suspected | What would confirm it |
|---|---|---|
| `disable-model-invocation` is read only by Cursor and ignored by Claude Code. | The repo consistently documents it as "Cursor's" key, and Claude Code's own skill loading is description-driven. But no test or citation in this repo demonstrates Claude Code's behavior either way. | Claude Code's published skill-frontmatter reference, or an observed run where a skill carrying the key is/isn't model-invoked. |
| The catalogs' top-level `version` is inert (consumed by no tool). | It has never been bumped (**AP-21**) and no code in this repo reads it. | The Claude Code / Cursor marketplace schema docs stating whether a client reads it. |

## Pointers (already documented or CI-enforced — not restated here)

| What | Where |
|---|---|
| All tooling is Python 3 stdlib only — no `pip install`, no dependencies | `CLAUDE.md` §Commands |
| Both catalogs register the same plugin set; versions byte-identical across a plugin's manifests | enforced: `scripts/validate_manifests.py` (`check_membership_parity`, `check_version_parity`) |
| Every registered plugin must be mentioned in the top-level `README.md` | enforced: `scripts/validate_manifests.py` (`check_readme_mentions`) |
| Shared `reference/` copies (`principles.md`, `config-protocol.md`) must be byte-identical across a plugin's skills | enforced: each `plugins/*/scripts/validate.py` (`check_shared_copies`) |
| Adding a new agent tool = one entry in the `TOOLS` list | `CLAUDE.md` §Architecture; `scripts/validate_manifests.py` |
| Full procedure for adding a plugin | `docs/adding-a-plugin.md` |

---
_Forged by [context-forge](https://github.com/davcs86/agent-plugins). It captures the
non-obvious — nothing here is invented; re-run `/context-constitution` to refresh after the code changes._
