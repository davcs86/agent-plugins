# Recon: dedup-context-forge-shared-reference

**Created**: 2026-08-02
**Change**: De-duplicate context-forge's shared `reference/principles.md` and `reference/config-protocol.md` (currently byte-identical copies under `skills/context-constitution/reference/` and `skills/context-scrubber/reference/`) into a single shared copy the plugin ships once, without merging the two skills' differing risk models (context-constitution: write-default, `disable-model-invocation: true`; context-scrubber: scan-default, implicitly triggerable).
**Depth**: full
**Affected areas**: `plugins/context-forge/` (skills, scripts/validate.py, README.md), `docs/adding-a-plugin.md`, `scripts/` (repo-root validator + hook — confirmed out of scope), `plugins/design-buddy/` (sibling precedent, same pattern)

---

## Repo Profile

`agent-plugins` is a multi-tool agent-plugin marketplace repo (Claude Code / Cursor / Codex). No app to build; all integrity is enforced by stdlib-only Python validators — a repo-level `scripts/validate_manifests.py` plus each plugin's own `scripts/validate.py`. `plugins/context-forge` ships two skills (`context-constitution`, `context-scrubber`) that already duplicate two governance files byte-for-byte, guarded by a drift check built specifically around that duplication.

## Codebase Map

- **`plugins/context-forge/`** (Markdown + Python)
  - Skills: `skills/context-constitution/SKILL.md`, `skills/context-scrubber/SKILL.md`
  - Duplicated files: `skills/context-constitution/reference/principles.md` ≡ `skills/context-scrubber/reference/principles.md` (byte-identical, confirmed via diff); `skills/context-constitution/reference/config-protocol.md` ≡ `skills/context-scrubber/reference/config-protocol.md` (byte-identical, confirmed via diff)
  - Validator: `plugins/context-forge/scripts/validate.py`
    - `SHARED_REFERENCE_FILES = ("principles.md", "config-protocol.md")` — `plugins/context-forge/scripts/validate.py:43`
    - `check_shared_copies` (DRIFT guard) — `plugins/context-forge/scripts/validate.py:126-134` — globs `skills/*/reference/<name>`; skips entirely if `len(copies) < 2`; a symlink counts as a "copy" (its `read_text()` follows the link transparently, so it always matches baseline by construction)
    - `check_internal_paths` (existence guard) — `plugins/context-forge/scripts/validate.py:104-111`, regex `INTERNAL_PATH_RE = r"(?:reference|templates)/[A-Za-z0-9_./-]+\.md"` — `plugins/context-forge/scripts/validate.py:32`. Resolves every match as `skill_dir / ref` (skill-directory-relative only). The regex requires the literal text to start with `reference/`/`templates/` — a `../reference/…` or plugin-root path is either not matched at all, or matched-but-resolved-wrong.
  - 8 literal citations of the two filenames inside the skills' own Progressive-disclosure sections — every one written as bare `reference/<name>.md`, none as `../` or plugin-root paths: `skills/context-constitution/SKILL.md:57-58,84,93`; `skills/context-scrubber/SKILL.md:58,60,82,90`
  - `README.md:131,133-134` — one markdown link to `skills/context-constitution/reference/principles.md`, plus prose stating "shared `principles.md` and `config-protocol.md` are byte-identical copies" — itself documents (and would need rewording to reflect) whatever the new structure is

- **`scripts/` (repo root)** — confirmed **out of scope**: `scripts/validate_manifests.py:52-69,109-190` only reads marketplace catalogs + each plugin's manifest JSON, never touches `skills/*/reference/`. `scripts/hooks/validate_on_edit.py:32-36` only fires on `*-plugin/(marketplace|plugin).json` edits — a `reference/*.md` edit does not trigger it (confirmed by the hook's own self-test asserting a `SKILL.md` edit is "out of scope").

- **`docs/adding-a-plugin.md`** — the only "self-contained" statement is at the whole-**plugin** level (`docs/adding-a-plugin.md:5`), not per-skill. Zero occurrences of "symlink" or of the `reference/`+`templates/` convention anywhere in the file — this convention is undocumented at the authoring-guide level; both live only in `context-forge`'s own `scripts/validate.py` docstring/logic.

- **`plugins/design-buddy/`** (sibling plugin, precedent) — three skills (`design-debate`, `impl-plan`, `plan-review`), **identical pattern**: `principles.md` (52 lines) and `config-protocol.md` (67 lines) each duplicated 3x, byte-identical (confirmed via md5sum across all three copies of each). `plugins/design-buddy/scripts/validate.py:124-132` carries the same `check_shared_copies` function body verbatim, same `SHARED_REFERENCE_FILES` constant (`plugins/design-buddy/scripts/validate.py:41`). No README or comment anywhere in either plugin argues for the duplication itself beyond the drift-guard's own docstring line ("the skills are self-contained, so copies must never drift" — `plugins/context-forge/scripts/validate.py:14-15`, `plugins/design-buddy/scripts/validate.py:13-14`, near-identical wording in both). design-buddy does **not** use `disable-model-invocation` on any of its three skills (`grep` returns no matches), so its three skills don't carry context-forge's write-vs-scan asymmetry — it is a weaker analogy for risk-model concerns, but a direct analogy for the file-duplication mechanics.

## Patterns to REUSE

- `check_shared_copies` → the existing DRIFT-guard *pattern* (glob + compare) is the thing already solving "copies must never drift" today; any new design should either keep it passing unmodified or replace it with an equally-enforced guarantee — not simply delete the safety net.
- Per-skill bare `reference/<name>.md` citation style in `SKILL.md`'s Progressive-disclosure section → reuse as-is if the chosen approach can keep every citation resolving at that literal skill-relative path (i.e. a symlink at that path), avoiding 8 site edits.

## Host Conventions & Hard Rules

- **Hard rule**: "all tooling is Python 3 stdlib only (no `pip install`, no dependencies) — preserve that when adding scripts." — `CLAUDE.md:33-34`
- **Hard rule**: "the reference files shared across the two skills (principles.md, config-protocol.md) are byte-identical — the skills are self-contained, so copies must never drift." — `plugins/context-forge/scripts/validate.py:14-15` (module docstring; enforced by `check_shared_copies`)
- **Hard rule**: "every reference/... and templates/... path named in a skill's markdown resolves to a file" — `plugins/context-forge/scripts/validate.py:12` (docstring; enforced by `check_internal_paths`)
- **Hard rule**: "no absolute host path leaks into the plugin (portability guard)" — `plugins/context-forge/scripts/validate.py:13,35-38` (`LEAK_PATTERNS`/`check_leakage`) — evidence the plugin's design already treats cross-machine/cross-install portability as a floor-level concern, relevant to weighing a symlink's portability risk
- **Hard rule** (repo-wide): plugin dir must be "a self-contained directory under `plugins/`" — `docs/adding-a-plugin.md:5` (plugin-level, not stated per-skill)
- Convention: CI runs each plugin's own `scripts/validate.py --self-test` then `scripts/validate.py` — `.github/workflows/validate.yml`; a green local run of the documented commands means a green pipeline — `CLAUDE.md:27-28`

## Dependencies

- Data / schema: none
- External contracts: none — but the *installation/distribution* mechanism by which Claude Code / Cursor / Codex actually materialize this plugin on an end user's machine (raw git clone vs. archive/package download) is **not documented anywhere in this repo** — relevant because it determines whether a symlink physically survives distribution
- Config / environment: none
- Cross-area edges: `plugins/context-forge/skills/*/SKILL.md` (Progressive disclosure section, cites the two filenames) → `plugins/context-forge/skills/*/reference/{principles,config-protocol}.md` (the files themselves) → `plugins/context-forge/scripts/validate.py` (`check_shared_copies`, `check_internal_paths`, both keyed off the current `skills/*/reference/<name>` layout)

## Risks / Not-found

- Not found: any documented policy (repo-wide or per-plugin) on symlinks — allowed, disallowed, or silently supported
- Not found: any `.gitattributes` file in the repo, or a repo/global `core.symlinks` override — git 2.43.0 in use, POSIX-default symlink handling, nothing suggests non-default behavior *in this environment*, but contributor/CI environments (e.g. Windows checkouts) are unverified
- Not found: any description anywhere in the repo of how Claude Code / Cursor / Codex's actual skill loaders resolve `SKILL.md`-relative paths at runtime, or whether plugin installation for end users ever goes through an archive/package step that could silently drop a symlink
- Not found: any `files` allowlist/glob field in any of the three `plugin.json` manifests that would explicitly include or exclude a symlink or a plugin-root-level `reference/` dir
- Ledger: none exists yet (first design-buddy run in this repo) — no prior lessons to carry forward

## Recommended Scope

Advisory only. The debate should weigh, at minimum: (A) a symlink from one skill's copy to the other's (passes both existing validator checks unmodified, zero `SKILL.md`/README prose edits, but introduces an unverified symlink-portability dependency into a repo whose own validator explicitly guards "portability" elsewhere); (B) a plugin-root-level canonical `reference/` dir with updated citation paths and validator logic (removes duplication for real, but touches `check_internal_paths`' regex/resolution, `check_shared_copies`, all 8 `SKILL.md` citation sites, and `README.md`); (C) leave the status quo (duplicated + CI-drift-guarded) — the existing `check_shared_copies` may already fully solve the risk the proposal is aimed at, making further change low-value. Whether `plugins/design-buddy`'s identical 3x duplication should be touched in the same pass, or left as an explicit out-of-scope follow-up, is a scope call the debate should make explicit rather than silently deciding.
