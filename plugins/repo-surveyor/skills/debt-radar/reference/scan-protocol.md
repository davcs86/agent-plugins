# debt-radar — scan protocol

Loaded at the start of Phase 0 in `scan` mode. You are the orchestrator; you dispatch the
read-only `debt-scout` and then **confirm every verdict yourself** before it becomes a finding.

## Step 1 — Frame the survey

From the boot sketch (B1), you know the analysis root, the languages/frameworks, and the repo's
real test/lint/build commands. Decide the clustering:

- **Small repo / single module** → one `debt-scout`.
- **Large repo or monorepo** → one `debt-scout` **per module or coherent file-cluster**, spawned
  **in parallel** (one message, multiple Task calls). Give each a disjoint scope so findings do
  not double-count, and name the shared categories so digests compose.

Do **not** try to read the whole tree yourself first — that is what the scout is for, and your
context is the resource to protect (**RS-N8**).

## Step 2 — Dispatch `debt-scout`

Hand each scout: its scope (paths), the detected stack, and the seven categories
(`reference/` calibration in `severity-rubric.md`). It returns a compact digest — one line per
suspected item: `path:line`, category, the quoted/anchored evidence, and a proposed severity.
It never returns file bodies and never writes.

## Step 3 — Confirm every verdict (the orchestrator's job — RS-1, RS-3)

A scout's line is a **lead**, not a finding. Promote it only after you check it:

- **Dead code** — re-grep the symbol across the **whole** tree (not just the scout's scope).
  Rule out: dynamic dispatch / reflection / string-keyed registries, framework entry points
  discovered by convention, public API / exported surface, and test-only use. Zero inbound
  references *after* those exclusions → confirmed dead; otherwise → `needs-confirmation` naming the
  possible dynamic use.
- **Swallowed / silenced error** — open the handler and read it. An empty/comment-only catch, a
  discarded `err`, an unjustified suppression on real logic → confirmed. A handler that logs,
  re-raises, or is a deliberate, documented ignore → not a finding (say nothing).
- **Duplication** — open all cited sites and confirm they actually encode the same logic (not
  merely similar shape). Note whether they must change together.
- **Contradiction with intent** — read the comment/docstring/type **and** the code it describes;
  confirm a real disagreement (not a case the comment already excepts, nor version skew). Mark
  ⚠ security if it touches an authz/authn/secret/tenant boundary.
- **Smells / brittle / latent risk** — confirm the shape is really present at the cited span
  (the god function's real length, the enumeration's real branches). Lower-confidence judgment
  calls with no hard anchor go to `needs-confirmation`, not the category tables.

Anything you cannot ground this way is a **question**, never a verdict (**RS-N6**).

## Step 4 — Score each confirmed finding

For every promoted finding, fill the four estimate fields — each labeled as an estimate
(**RS-4**), each auditable:

- **Severity** — the `severity-rubric.md` level (detected system, else P0–P3) and the **trigger**
  it meets. Do not inflate; reserve the top level for genuinely important-and-urgent.
- **Benefit** — what fixing it buys (a closed incident class, a unit that can now change safely,
  reclaimed budget). Concrete, tied to the cited site.
- **LOE** — a T-shirt size `XS/S/M/L/XL` with a one-line assumption (blast radius: call-sites
  touched, tests to add, interfaces changed). Use the **measured** call-site count where you have
  it; label the size an estimate.
- **Trade-off both ways (RS-N3)** — cost of **not** fixing (what the debt keeps costing) *and*
  cost of **fixing** (new error paths to handle, churn, risk of the change itself).

## Step 5 — Capture the survey baseline

Record the branch and commit the survey reflects: `git rev-parse --abbrev-ref HEAD` and
`git rev-parse HEAD`. These go in the report header so a later `verify` run knows what the findings
were measured against. If git is unavailable, say so in the header rather than inventing a ref.

## Step 6 — Compose

Order findings by leverage within each severity band (**RS-N2**), stating impact and LOE so the
order is auditable. Keep it to the findings that earn their place (**RS-N8**) — a hundred trivia
buries the three that matter. Then return to Phase 1 to render the template and gate the write.
