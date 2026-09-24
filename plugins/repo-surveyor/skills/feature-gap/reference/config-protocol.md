# repo-surveyor — config protocol

Load this only when `.agents/repo-surveyor.json` is absent (first run in a repo) or unreadable.
Shared by all three skills; **byte-identical** in every skill's `reference/` directory (the
plugin's `validate.py` fails on drift).

## The config file

`.agents/repo-surveyor.json` at the host repo root — committable, so a team shares one setting.
It is the **single config for all three repo-surveyor skills**. Whichever skill runs first in a
repo creates it via the first-run interview below; the others read it and never re-interview.
Whether to gitignore it is the host repo's call. Schema (version 1):

```json
{
  "version": 1,
  "outputDir": ".repo-surveyor",
  "findings": {
    "debt-radar": "debt-radar-findings.md",
    "feature-gap": "feature-gap-findings.md",
    "signal-map": "signal-map-findings.md"
  },
  "userFacingGlobs": [],
  "created": "<ISO date>"
}
```

- **`outputDir`** — string, repo-root-relative, or `null`. The directory each skill writes its
  findings file into. `null` = **scratch mode** (see below): nothing is written anywhere, every
  report is emitted inline. A survey never writes *outside* this directory (**RS-2**).
- **`findings`** — object, optional. Per-skill findings filename (basename only), resolved inside
  `outputDir`. Absent or a missing key → the default shown above for that skill. Kept per-skill so
  the three reports sit side by side without colliding.
- **`userFacingGlobs`** — array of strings, optional, used only by `feature-gap`. Repo-relative
  globs the host explicitly designates as the user-facing surface (routes dir, MCP server module,
  public API package, CLI entrypoints). Absent or `[]` → `feature-gap` auto-discovers the surface
  and, if it cannot confidently delimit it, asks once. Opt in here to pin the surface for a repo
  whose entry points are non-obvious.
- **`created`** — ISO date the file was written. Never fabricated (**RS-1**): read a clock/git if
  available, else `"unknown"`.

### No stored severity system, no stored baseline

The config deliberately stores **neither** the detected severity system **nor** any "last
surveyed" commit. Both are derived per run: severity by re-detecting the repo's own convention
(`reference/severity-rubric.md`), and `verify`-mode baselines from git and from the prior findings
file itself. Persisting either would only duplicate state the repo already holds and desync the
moment someone changes a label taxonomy or hand-edits a findings file — exactly the drift these
skills exist to catch. State lives where it is authoritative, not here.

## First-run interview

Ask once — a single structured multiple-choice prompt (the `AskUserQuestion` tool in Claude Code;
where it is unavailable, e.g. under Cursor/Codex, ask the same thing in plain chat and wait for the
answer). Before asking, **detect** candidate docs directories read-only (`docs/`, `documentation/`,
`doc/`, `website/docs/`) so the offered options fit the repo.

**Where should findings reports be written?**

- **`.repo-surveyor/`** (recommended when no docs dir is detected) — a dedicated, low-noise
  directory at the repo root; keeps three generated reports out of the way of hand-written docs.
- **`docs/repo-surveyor/`** (recommended when a `docs/` dir *is* detected) — reports live beside
  the repo's existing documentation, reviewable in the same place. Offer the actual detected docs
  path(s).
- **Custom path** — the user names a repo-relative directory.
- **Scratch only** — write nothing; present every report inline in chat.

Then, with the **Write tool** (never a script), create `.agents/repo-surveyor.json` (creating
`.agents/` if missing) with the chosen `outputDir`, the default `findings` map, an empty
`userFacingGlobs`, and today's date. Announce the choice in one line and continue the boot
sequence.

> Date handling: if no clock/date tool is available in the session, ask the user for today's date
> or leave `created` as `"unknown"` — never fabricate a date (**RS-1** applies to dates too).

## Scratch mode semantics

`outputDir: null` (or the `scan`/preview invocation, regardless of config) means **no file is
written anywhere** — not the findings report, not the config, not a temp file. The full report is
emitted inline in the conversation as one complete fenced-markdown block, so the user can place it
wherever they want. Scratch mode is the safe way to preview what a survey produces before letting
it write. The interview labels a real directory as recommended because scratch mode leaves no
durable, re-runnable artifact — and `debt-radar`'s `verify` mode needs a durable prior findings
file to check against.
