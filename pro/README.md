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

It answers one question honestly: on changes where a test was possible, how
often did one get written first? It reports per-repo and per-author totals. It
does not rank people, and you should not use it to.

## Licence

See LICENSE-PRO. This directory is not MIT.
