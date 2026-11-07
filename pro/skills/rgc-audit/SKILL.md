---
name: rgc-audit
description: Record what happened during a session as it happens, in order, to a machine-readable file. Use when starting work that should leave evidence, or when the user says "record this", "audit", "track the session".
---

# Audit

Writes what you actually did, in order, while you do it. Not a summary written
afterwards — those are reconstructions, and reconstructions are kind to
themselves.

Records go to `.rgc/sessions/` in the repo.

## When to use it

Turn it on when the change is **standard** or **heavy** weight (see
`rgc-weigh`). Light changes do not need a record.

Also turn it on whenever the user asks for evidence of how something was built,
or when working on code that has caused defects before.

## Commands

```bash
rgc-audit start --task "add backorder support"
rgc-audit step  --kind red   --ref "test_reject_allows_backorder"
rgc-audit step  --kind green --ref "orders.reject allow_backorder"
rgc-audit step  --kind move  --ref "Extract Function: is_backorder_allowed"
rgc-audit step  --kind waive --ref "skipped test on user instruction"
rgc-audit close
```

`rgc-audit show` prints the open session.

## Rules

**Record the step when you take it, not at the end.** The ordering is the whole
value. A record written at close time is a story about the session, not the
session.

**Record `waive` every time discipline is skipped**, whoever decided it. A
record that only contains successes tells the reader nothing, and the waive
entries are the most useful lines in the file when someone reads it later.

**Never edit a past line.** If something was wrong, add a `note` step saying so.
The file is append-only; that is what makes it worth reading.

**One session per task.** If the task changes, close and start a new one.

## What the record is for

Two things, and neither is performance management.

1. **Review.** A reviewer can see that the test came before the code, which the
   diff cannot show.
2. **Comparison.** `rgc-report` puts the record next to what `rgc-drift` finds
   in git. When they disagree, the git history is right.

Say this to the user if they ask what the records are for. Be direct about it:
these files make it visible when discipline was skipped, including when the
user told you to skip it.

## Committing the records

Either commit `.rgc/sessions/` or add it to `.gitignore`. Both are defensible.
Committing makes the record reviewable alongside the change; ignoring keeps the
history clean. Ask once, follow whatever they pick, do not raise it again.
