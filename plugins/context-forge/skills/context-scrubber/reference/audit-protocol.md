# context-forge — audit protocol (Phase 0 + Phase 1)

Load this at the start of Phase 0. It covers discovering the context targets, running the read-only auditor,
confirming its verdicts, and routing every confirmed verdict into the findings file. Nothing here trims a file —
that is Phase 2 (`apply-protocol.md`), gated and `apply`-only.

## What you are hunting (and what you are NOT)

The scrubber is the litmus test (**CF-N4**) run in reverse. `/context-constitution` keeps only what an agent
would **miss**; you flag what an agent would **find for free**, what no longer holds, or what is mis-placed —
all of it dead weight or attention drag in an auto-loaded context file. Seven line-level categories, each
grounded in real evidence (**CF-1**):

| Category | What it is | Grounded by |
|---|---|---|
| **Stale citation** | a `path:line` the context file cites that no longer resolves | the citation fails to resolve (Read/Grep/ls found nothing there) |
| **Restated (fails CF-N4)** | a fact plain in the one file an agent would edit, a manifest, or a doc/CI file it already loads | the free-to-read `path:line` that makes it redundant |
| **Cross-file duplication (CF-N3)** | the same rule/fact in ≥2 context files | every duplicate location + which copy is highest in the tree |
| **Contradicted by code** | a context claim the code now disproves | the contradicting `path:line` |
| **Should be just-in-time** | accurate but *pre-loaded* content that belongs behind a pointer to an on-demand doc — task-specific/rarely-needed detail that costs tokens on every load | the content is narrow/rarely-needed and an on-demand home exists or should; **not** a duplicate (that's cross-file) — it's *misplaced*, not redundant |
| **Brittle / over-specified (anti-altitude)** | a long if-else / step-by-step instruction block that should be a heuristic — it shapes behavior but too rigidly, and rots as the code moves | the block enumerates cases/steps a strong one-line heuristic would cover; **not** filler (that's bloat) — it *does* steer the agent, just brittly |
| **Bloat / low-value prose** | verbose filler that shapes no agent action | — (judgment; mark lower-confidence, never assert removal without a clear reason) |

Suggested actions map to the category: `remove` (stale/restated/duplication), **`route to findings / fix the code
or the claim`** (contradicted — a defect, **never** an `apply` delete; see below), `move-to-<on-demand doc>` +
leave a pointer (just-in-time), `trim to a heuristic` (brittle), or `trim` (bloat). Anything you *suspect* but
cannot ground is **`keep-but-verify`**, phrased as a question — never asserted as removable (**CF-1**).
Severity/confidence ranks a finding within the report; it never deletes one (**CF-N8**).

**Contradicted-by-code is a defect, not a scrub target (CF-N9).** A context line the code disproves is
*documentation that lies* — the same class `/context-constitution` routes to its findings log for human triage.
Whether the fix is to *implement the missing behavior* or *remove the doc* is a decision the scrubber does not
get to make silently: a dead config key or an unimplemented event may be an intended-but-unbuilt control (a risk
limit, an approval flow), and deleting the row buries the spec. So a contradicted verdict is **reported and
deferred to `/context-constitution`** (its findings log owns the fix-vs-remove call), carried as
`keep-but-verify` in this report — it is **excluded from the removable total and is never an `apply` candidate**.
The only line-level correction the scrubber suggests here is a pure *re-ground* (a drifted `path:line`), and even
that is a `/context-constitution` refresh job, not a scrubber trim.

Plus one **file-level** signal (not a per-line row): **context budget / rot risk** — a whole context file whose
**measured** size is large enough to strain attention (context rot) even when no single line fails. Report the
biggest files with their measured lines/characters against a soft budget; it is advisory (points at what to
review), never an automatic removal.

## Step 1 — Discover the context targets

Under the analysis root (arg `path` or repo root), enumerate the auto-loaded instruction files (the set in
`SKILL.md` → `## What counts as a context target`):

- `find <root> -name CLAUDE.md` and `-name AGENTS.md` (root + nested, every depth).
- Resolve `constitutionPath` per target to add each `context-constitution.md` / `context-constitution-findings.md`.
- `.cursor/rules/*`, `.cursorrules`, `.github/copilot-instructions.md`, `.windsurfrules` when present.

**Exclude** application source, tests, and read-on-demand docs. If discovery finds nothing, say so and stop —
there is nothing to scrub. Report the target list; cap a very large fan-out and name anything you deferred
(**CF-1** honesty — never silently audit a subset).

## Step 2 — Run the auditor (read-only, advisory)

Spawn the **`context-auditor`** subagent (Agent tool; reference it as `context-forge:context-auditor`, falling
back to the bare name if the namespaced type isn't found). Hand it the target list and the repo root. For a large
repo or a monorepo with many context files, spawn **one auditor per file cluster in parallel** (one message,
multiple Task calls) — each returns a scoped digest keyed to its files. The auditor has `Glob, Grep, Read` only;
it classifies each substantive line and cites its evidence, and it **never writes**. See its output format in the
agent file.

**Protected blocks are off-limits to the audit.** Tell the auditor (and enforce yourself) that any span between
`context-forge:*:start` / `:end` sentinels — and the legacy `constitution-forge:*` form — is **not audited**: it
is the behavioral-contract or constitution-pointer block that `/context-constitution` owns. The auditor lists the
blocks it found (so the report can note them) but never classifies a line inside one.

## Step 3 — Confirm every verdict yourself (CF-1, CF-3)

The auditor is advisory; **you** are the only writer, and no verdict enters the findings file on the auditor's
word alone. For each returned verdict, do the cheap confirmation:

- **Stale citation** — try to resolve the cited `path:line` yourself (Read the file at that line, or Grep for the
  referenced symbol). Confirmed only if it genuinely doesn't resolve. If the code merely *moved*, note the new
  location so the suggested action can be "re-ground to `path:line`" rather than "remove."
- **Restated** — open the free-to-read source the auditor named and confirm it truly makes the context line
  redundant for an agent editing that file.
- **Duplication** — read both sites and confirm they state the same thing; pick the keeper (highest in the tree —
  **CF-N3**).
- **Contradicted by code** — read the contradicting site and confirm the disagreement is real (not a version skew
  or a case the context line already excepts). Mark **⚠ security** if it touches an authz/authn/secret/tenant
  boundary. Confirmed → it is a **defect** (**CF-N9**): record it, note whether the honest fix is *implement* or
  *remove-the-doc*, and route it to the findings log / a `/context-constitution` refresh — carried here as
  `keep-but-verify`, **never** a `remove` row and **never** an `apply` candidate. Do not resolve the
  implement-vs-remove question yourself.
- **Bloat** — sanity-check that the line really shapes no action; when in doubt, downgrade to `keep-but-verify`.

A verdict that fails confirmation is dropped from the "fails" set and, if still suspicious, recorded under
`keep-but-verify` — never asserted.

## Step 4 — Route into the findings file (Phase 1; no drops — CF-N8)

Fill `templates/scrubber-findings.md`. Every confirmed verdict lands in exactly one category section; each
`keep-but-verify` lands in that section. Nothing grounded is discarded — the report is the durable home for
everything the audit paid to find. One row per failing context line, cited on **both** sides (the context
`file:line` and the evidence it fails), with the category, a one-line why, and a suggested action
(`remove` / `trim` / `move-to-<file>` / `keep-but-verify`).

**Protected blocks** get their own transparency section (`## Protected blocks (reported, never trimmed)`) listing
the sentinel blocks found — never a removal row. A constitution-pointer that looks stale is `keep-but-verify` with
"re-run `/context-constitution`," because that block is the constitution skill's to maintain (**CF-N11**).

**Measure savings, don't estimate them (CF-1).** You hold the exact bytes of every flagged line, so quantify the
report's `## Summary` from **measured** lines and characters — real counts, per category and as a "removable
total" (rows actioned `remove`/`trim`/confirmed `move`; `keep-but-verify` excluded). A **token** count is honest
only from a real tokenizer: if a token-counting tool is available in the session, use it and label the column
measured; otherwise report lines/characters and, at most, an explicit `≈ chars ÷ 4` approximation — never a bare
token number that reads as exact. Do not invent a savings figure of any kind.

**Measure the file-level budget too.** For every audited context file, record its **measured** total lines and
characters (you already hold its bytes). Flag any file over a soft budget — default **~2,000 characters** for a
single auto-loaded context file, adjustable — as a context-rot risk in the report's `## Context budget
(file-level)` section, biggest first. This is advisory: a large file is a prompt to review, not an automatic
removal, and the number is measured, never invented (**CF-1**). It catches the case where every individual line
looks defensible but the file as a whole is too big to keep sharp attention on.

Then present the Phase 1 gate (target list, failing counts by category, `keep-but-verify` count, findings
destination) and route by the user's choice — write the findings file on approval, or present it inline in scratch
mode. In `apply` mode, on **Approve findings & proceed to Apply**, continue to `apply-protocol.md`.

## Guardrails

- **Read-only until the gate.** Phase 0 spawns read-only auditors and does read/inspect confirmation only; nothing
  is written before the Phase 1 gate, nothing trimmed before the Phase 2 gate.
- **Distill, don't dump.** Digests and rows are `file:line` + a one-line reason + a citation, never pasted file
  bodies.
- **Grounded beats plausible.** A "stale"/"restated"/"contradicted" verdict requires the confirming evidence in
  hand; a hunch is `keep-but-verify`, phrased as a question.
- **Never audit or trim a protected sentinel block.** It is `/context-constitution`'s territory.
