# context-forge — config protocol

Load this only when `.agents/context-forge.json` is absent (first run in a repo) or unreadable.

## The config file

`.agents/context-forge.json` at the host repo root — committable, so a team shares one setting. It is the
**single config for both context-forge skills**: `/context-constitution` reads `constitutionPath`/`citeIds`,
and `/context-scrubber` reads `constitutionPath` (to locate the generated constitution among its audit targets)
plus its own optional `scrubberFindingsPath`. Whichever skill runs first in a repo creates the file; the other
reads it and never re-interviews. Whether to gitignore it is the host repo's call. Schema (version 1):

```json
{
  "version": 1,
  "constitutionPath": "docs/context-constitution.md",
  "citeIds": true,
  "scrubberFindingsPath": "context-scrubber-findings.md",
  "created": "<ISO date>"
}
```

- `constitutionPath` — string, **relative to each target directory**. At the repo root it resolves
  against the root (e.g. `docs/context-constitution.md`); for a module at `services/foo/` it resolves against
  that module (e.g. `services/foo/docs/context-constitution.md`). Keep it a repo-relative *tail* so the same
  setting applies uniformly to every target. `null` = scratch mode (see below).
- `citeIds` — boolean. When `true`, each behavior in the prepended contract cites the generated
  constitution IDs that enforce it (e.g. "*ask before assuming* — CF-2, and the design gate"). When
  `false`, the contract uses the generic four-behavior phrasing with no IDs — the right choice when
  you want a maximally portable contract, or aren't generating a constitution at all.
- `scrubberFindingsPath` — string, **optional**, used only by `/context-scrubber`. Unlike `constitutionPath`
  it is **root-anchored** (one audit report for the whole run, since its rows are per-file). Default
  `context-scrubber-findings.md` at the repo root. Absent → the scrubber falls back to that default and does
  **not** rewrite the config in `scan` mode; a config written by an older context-constitution run (with no
  such key) is fully valid. `null` follows `constitutionPath: null` into scratch mode (findings emitted inline).

### No stored baseline — `refresh` reads git

The config deliberately stores **no** "last forged" commit. `refresh` derives each target's baseline
from git — the last commit that wrote that target's `context-constitution.md`
(`git log -1 --format=%H -- <target>/<constitutionPath>`; see `refresh-protocol.md`). That is
per-target for free (each file has its own history), so a write scoped to one module can never throw
off another target's baseline, and — the reason this matters — a **manual edit** to a constitution is
just a commit, indistinguishable from a forge to the next refresh. Persisting a ref here would only
duplicate state git already holds and desync the moment someone hand-edits a constitution without
also updating this file. So the baseline lives in git, not here.

## First-run interview

Ask once — a single structured multiple-choice prompt (the `AskUserQuestion` tool in Claude Code;
where it's unavailable, e.g. under Cursor, ask the same thing in plain chat) — with two questions:

1. **Where should each `context-constitution.md` be written?** (relative to its target dir)
   - `docs/context-constitution.md` (recommended) — a durable, reviewable governance doc beside the code.
   - `context-constitution.md` (repo/module root) — top-level, maximally visible.
   - Custom path — the user names a repo-relative tail.
   - Scratch only — write no constitution files; present every artifact inline in chat.
2. **Should the behavioral contract cite the generated constitution IDs?**
   - Yes (recommended) — behaviors point at the local rules that enforce them; best when generating
     a constitution.
   - No — keep the contract to the generic four lines, no IDs (most portable).

Then, with the Write tool (never a script), write `.agents/context-forge.json` (create
`.agents/` if missing) with the chosen values and today's date. Announce the choices in one line and
continue the boot sequence.

> Date handling: if no clock/date tool is available in the session, ask the user for today's date or
> leave `created` as `"unknown"` — never fabricate a date (**CF-1** applies to dates too).

## Scratch mode semantics

`constitutionPath: null` means **no files are written anywhere** — not the constitution, not the
`CLAUDE.md` contract, not the findings log, not even temp files. Every artifact (each module
constitution, the root constitution, each contract block, and each `context-constitution-findings.md`) is
emitted inline in the conversation as a complete fenced markdown block, so the user can place them
wherever they want. Scratch mode is implied by the `scan` argument regardless of config, and is the
safe way to preview what the skill would produce before letting it write. The first-run interview
labels a real path as recommended because scratch mode has no durable output.

> The findings log is not separately configured: it is always written as `context-constitution-findings.md`
> beside the constitution (same directory as `constitutionPath`), per target, and only when that
> target has at least one defect.
