# context-forge — apply protocol (Phase 2)

Load this only on an `apply` run, after the Phase 1 findings gate. Apply turns approved findings rows into
**in-place, non-destructive** trims of the context files. It only ever *subtracts* approved lines; it never
rewrites a file, never adds content, and never touches a protected sentinel block. `scan` mode never reaches this
protocol.

## Precondition

You are here only because the user chose **Approve findings & proceed to Apply** at the Phase 1 gate. The findings
file has been written (or presented inline). Only rows whose suggested action is `remove`, `trim`, or a confirmed
`move-to-<file>` are apply candidates — `keep-but-verify` rows are never applied (they are unproven, **CF-1**).

## Step 1 — Build the edit set

From the approved rows, assemble a per-file edit set: for each target file, the exact lines to remove or shorten,
located by **content** (quote the current line), not by a bare line number — line numbers drift as edits land, and
content-anchored edits stay correct. Group by file so each file is opened once. Exclude, up front:

- any line inside a `context-forge:*` / `constitution-forge:*` sentinel span (**CF-N11** — off-limits);
- any `move-to-<file>` whose destination has not been confirmed to already hold the content;
- anything the user deselected.

## Step 2 — Second gate (CF-5)

Present the concrete edit set — per file, each line to remove/trim and the one-line reason — at a **second**
`AskUserQuestion` gate (plain chat under Cursor). This is the last stop before any byte changes. Options:
**Apply the trims** / **Adjust** (drop/edit specific items and re-present) / **Cancel** (write nothing). No file is
edited until the user picks *Apply the trims*.

## Step 3 — Trim in place (CF-4), sentinel-safe

Per approved item, using Edit (a targeted string replacement), on the file's current bytes:

1. **Remove** — delete exactly the quoted line (and a now-orphaned blank line it leaves behind, if any); leave
   every surrounding byte untouched.
2. **Trim** — replace the quoted line with its shortened form exactly as shown/approved in the edit set; change
   nothing else on the line's neighbors.
3. **Sentinel check before each edit.** Re-confirm the target span contains no `…:start` / `…:end` marker. If an
   approved item turns out to fall inside a sentinel block, **skip it** and record the skip — never edit inside the
   block (**CF-N11**).
4. **`move-to-<file>` is advisory.** Only remove the source line; do **not** write the destination. If the
   destination doesn't yet hold the content, leave the source in place and note it as deferred.
5. **Apply only subtracts.** Never add a line, a heading, or a new sentinel. If removing a line would leave a
   heading with no body, prefer to leave a one-line placeholder or defer — never invent replacement prose.

## Step 4 — Idempotency & report

- A line removed on one run stays removed; a re-run of the audit simply won't surface it again — apply performs no
  bookkeeping of its own.
- Per file, record what was **trimmed** vs. **deferred/skipped** (sentinel-guarded, unconfirmed move, user-dropped)
  and surface those counts at COMPLETION so the user sees exactly what changed and what was intentionally left.
- Stage nothing beyond the edited context files (and the findings file already written in Phase 1).

## Guardrails

- **Non-destructive (CF-4).** In-place subtraction only; the file's untouched content is byte-for-byte preserved.
- **Approve before write (CF-5).** The Step-2 gate is mandatory; there is no "apply without confirming the edit
  set."
- **Never trim a protected block (CF-N11).** Behavioral-contract and constitution-pointer spans are always skipped.
- **Never invent (CF-1).** Apply removes and shortens what was approved; it never writes new context prose.
