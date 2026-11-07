---
name: rgc-report
description: Produce and interpret the team report — history, trend, defect correlation, per-author view, coaching. Use when asked how a team is doing, for adoption metrics, or when the user says "team report", "are we improving", "does this discipline actually help".
---

# Report

A team-level read of a repository: what the history looks like, which way it is
moving, whether skipped discipline actually tracks with later fixes, and what
is worth teaching.

```bash
rgc-report                      # last 400 commits
rgc-report --since 2026-01-01   # a date window
rgc-report --path src/payments  # one area
rgc-report --json               # machine-readable
```

## Reading it out loud

**HISTORY** — the verdict mix. See `rgc-drift` for what each verdict means.

**TREND** — problem rate by month. Read the direction, not any single month. A
month with six graded commits will swing wildly and means almost nothing.

**DEFECT CORRELATION** — the one that is easy to oversell. It finds commits
whose message reads like a fix, uses `git blame` to find what last touched the
lines each fix changed, and compares the verdict mix of those origin commits
against the repo's base rate.

A lift above about 1.3 means commits that skipped discipline are
over-represented among the ones later fixed. **A lift near or below 1.0 means
no link is visible, and you must say that plainly.** Do not explain the
absence away, do not re-slice the data until it agrees with you, and do not
present a lift computed from under about 30 traced origins as a finding.

**BY AUTHOR** — only people with at least 10 graded commits in the window.
Smaller samples are suppressed on purpose.

**WHAT TO TEACH** — derived from each person's verdict mix, same threshold.

## Rules when you present this to anyone

**Never rank people with it.** Problem rate tracks deadline pressure far more
reliably than it tracks care. The person with the worst number is often the
one who was handed the incident.

**Always give the sample size** next to any percentage. "38% of 55" is a
statement; "38%" alone is an invitation to misread.

**If the correlation shows nothing, lead with that.** The honest answer is more
useful than the one that sells the tool, and a manager who later discovers you
shaded it will not trust any of the rest.

**Identities split.** One person often commits under two git names. The report
shows them separately unless `.rgc/authors.map` maps the aliases. Check for
duplicates before quoting anyone's number.

## What it cannot tell you

Whether the tests are any good. Whether the fixes were caused by the commits
blame points at. Whether a problem commit was a deliberate, sensible call under
pressure. It reads file paths, line counts and commit messages — nothing else.
