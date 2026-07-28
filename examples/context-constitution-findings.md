# agent-plugins — Constitution Findings

Defects surfaced by `/context-constitution` (context-forge) on 2026-07-28 while forging
`context-constitution.md`. These are **things to fix**, not invariants to respect, so they are
recorded here rather than frozen into governance rules (**CF-N9**). Each is cited; none is acted
on automatically — this file is for triage.

## Documentation that lies

| Claim | What the code does | Evidence | Suggested action |
|---|---|---|---|
| `CLAUDE.md` §Architecture: the two catalogs "are deliberately kept structurally identical". | They are identical in their `plugins` entries — which is the part that matters and the part CI enforces — but **not** at the top level: Claude's catalog-level `description` is a top-level key, Cursor's is nested under a `metadata` object. Nothing validates catalog-level shape beyond `name` and `plugins`. | `.claude-plugin/marketplace.json:7` vs `.cursor-plugin/marketplace.json:7-9`; checks at `scripts/validate_manifests.py:123,126` | Narrow the claim to what is true and enforced ("same `plugins` entries, same `./plugins/<name>` sources"), **or** add a catalog-level shape check and make the sentence true. Do not delete the line — the invariant it points at is real. |

## Latent bugs

| Defect | Why it's a bug | Evidence | Suggested action |
|---|---|---|---|
| The README-listing check is a bare **substring** test: `name not in readme`. | A plugin whose name is a substring of another registered plugin's name — or of any prose in the README — passes without having its own entry. `forge` alongside `context-forge`, or `lab` alongside `strat-lab`, would be silently "documented". The check exists precisely because a plugin once shipped undocumented (`a0bcafa`), so a false pass defeats its whole purpose. Not currently triggered: no current plugin name is a substring of another. | `scripts/validate_manifests.py:229-233` | Match a stronger signal than raw substring — the plugin's link (`plugins/<name>/`) or a word-boundary regex. |
| A missing `README.md` **disables** the README check instead of failing it. | `check_readme_mentions` returns `[]` early when the file is absent. The comment explains this as a fixture-repo convenience, and it is — but the same escape hatch applies to the real repository: delete `README.md` and every plugin instantly "passes" the check that exists to keep them documented. | `scripts/validate_manifests.py:225-228` | Keep the fixture allowance explicit rather than implicit — e.g. skip only when the repo has no catalogs either, or have `validate_repo` pass a flag for fixture mode. |

## Unenforced invariants (no check exists)

| Invariant | Why it drifts | Evidence | Suggested action |
|---|---|---|---|
| A plugin's `description` must agree across its three copies (both catalogs + its own `plugin.json`). | Nothing reads `description` in any validator, so drift is free. Two of three plugins have already drifted — design-buddy's `plugin.json` carries parenthetical detail the catalogs lack; context-forge's differ in opening phrase and category list. | `.claude-plugin/marketplace.json:14` vs `plugins/design-buddy/.claude-plugin/plugin.json:5`; `.claude-plugin/marketplace.json:26` vs `plugins/context-forge/.claude-plugin/plugin.json:5` | Either add a description-parity check to `validate_manifests.py` (cheap — the data is already parsed), or state deliberately that the catalog copy is a short marketing blurb and `plugin.json` is authoritative, and make the two consistently *different* rather than accidentally so. |
| A remote (`github`/`git`) plugin source gets **no** validation at all. | The skip is deliberate for the on-disk-tree check but silently extends to version parity, membership parity, and the README check, because the entry never joins `tool_members`. Today no remote sources exist, so nothing is broken yet. | `scripts/validate_manifests.py:90-91`, `:150-155` | If a remote plugin is ever registered, either add it to `tool_members` before the `continue` (so membership/README checks still apply) or fail loudly on remote sources until they're supported. |

---
_Surfaced by [context-forge](https://github.com/davcs86/agent-plugins). Recorded for triage, never
enshrined as rules — re-run `/context-constitution` to refresh._
