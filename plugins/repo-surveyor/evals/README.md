# repo-surveyor — eval suite

Behavioral regression tests for the three repo-surveyor skills, run with
[`claude plugin eval`](https://code.claude.com/docs/en/plugin-evals). Each case scaffolds a tiny
fixture repo with a *known* defect, invokes one skill in **scratch/inline mode** (so the run stays
read-only — nothing is written), and grades three things:

1. **The right skill fired** (`tool_used` on `Skill` with an `input_match` on the skill name).
2. **The run was read-only** (`tool_used` on `Write` with `min: 0, max: 0` — the skill must not
   mutate source or write a file when told to present inline).
3. **The report meets the Floor** (`llm` grader): it cites a concrete `path:line`, assigns a
   severity, and — for `debt-radar` — states a do-vs-not-do trade-off; it flags the planted defect
   and invents nothing.

These are the guardrails that let the skills be changed safely: reword a description, refactor a
protocol, or adjust a template, then re-run the suite to confirm triggering, read-only posture, and
report quality still hold.

## Cases

| Case | Skill under test | Planted defect the report must catch |
|---|---|---|
| `debt-radar-scan/` | `debt-radar` | A swallowed exception + a dead function in `src/sample.py` |
| `feature-gap-scan/` | `feature-gap` | An asymmetric CRUD surface (create/list, no delete) + an undocumented command |
| `signal-map-scan/` | `signal-map` | An error branch on an external call with no logging |

## Running

Every run is a **real, billed model call** (network + credentials required); there is no offline
mode. So this suite is run **on demand**, not in the zero-dependency CI that gates every PR — the
`scripts/validate.py` structural check keeps the eval *files* well-formed for free; running them
proves *behavior*.

```shell
# from the plugin root
cd plugins/repo-surveyor

# cheap iteration: one run per case, with-arm only
claude plugin eval . --runs 1 --ablation none --scaffold

# fuller signal: default runs, measure the plugin's delta vs. no-plugin
claude plugin eval . --scaffold --json results.json --threshold 0.8

# a single case
claude plugin eval evals/debt-radar-scan/prompt.md --scaffold
```

`--scaffold` runs each case's `setup.sh` to build its fixture repo first. Results land in
`evals/results/<timestamp>/` (git-ignored). Exit code 0 = all cases ≥ threshold; 1 = below
threshold; 2 = partial (cost/auth).

### Optional CI (opt-in, needs a secret)

Because a run costs money and needs `ANTHROPIC_API_KEY`, this is **not** wired into the default
pipeline. To gate a dedicated workflow on it, add a job that runs only when the secret is present:

```yaml
# .github/workflows/repo-surveyor-evals.yml (opt-in; not part of the free validate pipeline)
jobs:
  evals:
    if: ${{ secrets.ANTHROPIC_API_KEY != '' }}
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: |
          cd plugins/repo-surveyor
          claude plugin eval . --scaffold --trust-plugin \
            --json results.json --threshold 0.8 --no-publish --max-cost-usd 10
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
```
