# Red Green Clean Pro

The free tier tells the agent what discipline looks like. Pro checks whether it
actually happened, and helps in the two places the free tier leaves you stuck.

| Skill | The gap it fills |
|-------|------------------|
| `/rgc-weigh` | Not every change deserves the full loop. Decides how much ceremony this one needs, so the discipline survives contact with a one-line fix. |
| `/rgc-net` | "I want to tidy but there are no tests." Builds characterisation tests around code you do not understand yet. |
| `/rgc-audit` | Writes a machine-readable record of what the agent actually did, in order. |
| `/rgc-drift` | Reads your git history and reports where discipline slipped. Works on any repo, including ones that never used this tool. |

`rgc-drift` is the one to run first. Point it at a repo you already have and it
will tell you something true within ten seconds.

## Install

Pro installs alongside the free core:

```bash
./install.sh --pro
```

This links the Pro skills into `~/.claude/skills/` and puts `rgc-drift`,
`rgc-audit` and `rgc-report` on your PATH via `~/.local/bin`.

## Command-line tools

```bash
rgc-drift                      # last 50 commits on the current branch
rgc-drift --since origin/main  # everything since you branched
rgc-drift --json               # machine-readable, for CI
rgc-drift --fail-over 30       # exit 1 if more than 30% of commits are mixed
```

```bash
rgc-audit start  --task "add stock check"
rgc-audit step   --kind red   --ref "createOrder_whenStockIsZero_rejects"
rgc-audit step   --kind green --ref "OrderService.createOrder"
rgc-audit step   --kind move  --ref "Extract Function: checkStockAvailable"
rgc-audit close
```

Records land in `.rgc/sessions/` in the repo. Commit them or gitignore them;
both work.

## Team licence

`rgc-report` aggregates audit records across a repo and reports adoption:

```bash
rgc-report --since 2026-01-01
```

Five sections: history, trend by month, defect correlation, per-author view,
and what to teach.

**Defect correlation** is the one worth the licence. It finds commits that look
like fixes, traces with `git blame` to whatever last touched the lines each fix
changed, and compares those origin commits against the repo's base rate. When
skipped discipline really does track with later fixes, this shows it in your
own history rather than in someone else's study. When it does not, the report
says so.

Per-author figures need at least 10 graded commits in the window; smaller
samples are suppressed. One person often commits under two git names — map the
aliases in `.rgc/authors.map`:

```
lpatil = Lalit Patil
sbhatkande = Sandeep Bhatkande
```

It does not rank people, and you should not use it to.

## Tests

```bash
python3 pro/tests/test_drift.py
```

Builds throwaway git repositories with one planted commit per verdict and
checks `rgc-drift` grades each correctly. No dependencies beyond the standard
library and `git`.

## Licence

See LICENSE-PRO. This directory is not MIT.
