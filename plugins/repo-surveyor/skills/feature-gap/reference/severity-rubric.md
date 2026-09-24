# repo-surveyor — severity rubric

Shared by all three skills; **byte-identical** in every skill's `reference/` directory (the
plugin's `validate.py` fails on drift). Load it at boot, run **detection first**, and announce
which system is in force (**RS-N1**). Every finding's severity must name the level's *trigger* it
meets — never a bare adjective.

## Step 1 — Detect the repo's own priority system (prefer it)

A repo that already speaks a priority language should be surveyed in that language, so its
findings drop straight into its existing triage. Look, read-only, for an established convention
before falling back. In rough order of authority:

1. **Issue/PR label taxonomy** — label names in `.github/` issue templates
   (`.github/ISSUE_TEMPLATE/*`), a `labels.yml`/`.github/labels.yml`, or labels referenced in
   `CONTRIBUTING*`/`docs/`. Common shapes: `P0..P3`/`P1..P4`, `sev1..sev4`/`S1..S4`,
   `priority/critical|high|medium|low`, `severity: *`, `blocker/critical/major/minor/trivial`.
2. **A written triage/severity policy** — a `SECURITY.md`, `CONTRIBUTING*`, `SUPPORT.md`, or a
   `docs/` page that *defines* severity levels and what each means.
3. **In-code convention** — a consistently used `# TODO(P1):` / `// FIXME(sev2):` style, or an
   enum/constant set (`Severity.CRITICAL`, `LogLevel`) the codebase itself standardizes on.

**When one is found:** adopt its levels and its ordering verbatim, map each finding onto it, and
record in the report header: *"Severity system: detected — `<name>` (source: `<path>`)."* Cite the
path where the system is defined (**RS-1**). If two systems conflict, prefer the one closest to
triage authority (labels/policy over an ad-hoc code comment) and note the other.

**Detection must be grounded, not guessed.** A single stray `P1` in one comment is not a system;
adopt a scheme only when it is used consistently or defined in one of the sources above. Otherwise
fall back.

## Step 2 — Fallback: Eisenhower (urgent × important) → P0–P3

Absent a detected system, place every finding on the Eisenhower matrix — its two axes are exactly
the two inputs the leverage ordering (**RS-N2**) already needs — and express the quadrant on a
P0–P3 scale. Record in the header: *"Severity system: Eisenhower → P0–P3 (no repo system
detected)."*

- **Important** = the finding bears on correctness, security, data integrity, or a load-bearing
  user-facing capability (high impact if left).
- **Urgent** = it is already causing harm, is on a path about to be built on, or its cost
  compounds the longer it waits (time-sensitive).

| | **Urgent** | **Not urgent** |
|---|---|---|
| **Important** | **P0 — do now.** Actively harmful or imminently so: a swallowed error on a correctness/security path, a data-losing branch, a broken user-facing contract, a blind spot over a live incident class. | **P1 — schedule.** High impact, not yet biting: brittle architecture in a churning area, a missing metric on a key feature, a discoverability gap on a flagship capability. |
| **Not important** | **P2 — quick win / delegate.** Low impact but cheap and time-adjacent: a local smell in code being touched anyway, a small inconsistency, a redundant log worth pruning while nearby. | **P3 — backlog.** Low impact, no urgency: cosmetic dead code in a quiet corner, a nice-to-have signal, a minor naming drift. Recorded (**RS-N6**), not urged. |

**Mapping rule:** a finding's quadrant is set by its own two axes, then leverage (**RS-N2**) orders
findings *within* a P-level. P0 is reserved for genuinely important **and** urgent — do not inflate;
a report where everything is P0 has no rubric at all (**RS-N1**). Equally, do not bury an important
finding at P3 because it is cheap: cheap-and-important is P1/P2, not P3.

## Per-lens calibration (same scale, lens-specific triggers)

The scale is one; what trips each level is lens-specific. Illustrative P0 triggers:

- **debt-radar** — a swallowed/silenced error on a correctness or security path; dead code masking
  a live bug; an invariant the code no longer upholds.
- **feature-gap** — a user-facing contract that is inconsistent or broken across sibling surfaces
  in a way that misleads users; a security-relevant surface with no guardrail.
- **signal-map** — no signal whatsoever over an error class that would page someone; a feature
  whose failure is currently invisible in logs and metrics.

Lower levels scale down accordingly. Each skill's own `reference/*-protocol.md` gives its full
category-to-severity calibration; this file owns the **scale and the detection rule** they share.
