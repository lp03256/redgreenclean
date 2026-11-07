---
name: rgc-drift
description: Read git history and report where test-first discipline slipped — unprotected changes, mixed commits, weakened tests. Use when asked how healthy a repo is, before starting work in unfamiliar code, or when the user says "drift", "how bad is it", "audit the history".
---

# Drift

Reads git history and reports where discipline slipped. Works on any repo,
including ones that never used this tool — which makes it the fastest way to
learn what you are walking into.

```bash
rgc-drift                        # last 50 commits
rgc-drift --since origin/main    # everything on this branch
rgc-drift --path src/payments    # one area
rgc-drift --json                 # for CI or further processing
rgc-drift --fail-over 30         # exit 1 if over 30% problem commits
```

## What each verdict means

| Verdict | What it saw |
|---|---|
| `RED` | Test files only, lines added. A test written before the code. |
| `GREEN` | Production and test changed together. |
| `STRUCTURAL` | Files moved or renamed, near-zero edits. Behaviour unchanged. |
| `SCAFFOLD` | Config, docs, dependencies. Not graded. |
| `MIXED` | Code moved **and** changed in one commit. |
| `UNPROTECT` | Production code changed with no test touched. |
| `TEST-CUT` | Tests shrank while production code changed. |

A commit with no parent is graded `SCAFFOLD`. There was nothing behind it to
protect, so grading it tells you nothing about discipline.

A production-only commit directly after a test-only commit is graded `GREEN`,
not `UNPROTECT`. Splitting red and green across two commits is correct
practice, and the tool must not punish it.

The last three are the problems. Of those, `UNPROTECT` and `MIXED` matter most:
the first is behaviour nobody pinned down, the second is a diff nobody can
actually review.

## How to use the number

A problem rate under about 20% is normal and healthy. Above 40% means the
discipline is not really in place, whatever anyone says.

**Do not present the number as a score for a person.** It is a property of a
codebase and the pressure it was written under. Deadlines produce
`UNPROTECT` commits far more reliably than carelessness does.

## Before starting work in unfamiliar code

Run it scoped to the area you are about to touch:

```bash
rgc-drift --path src/payments -n 200
```

A high `UNPROTECT` rate there tells you to reach for `rgc-net` before changing
anything, and to grade the change **heavy** in `rgc-weigh`.

## In CI

```bash
rgc-drift --since origin/main --fail-over 25 --quiet
```

Checks only the branch, not the whole history. Start the threshold above your
current rate and tighten it over time — a gate that fails on day one gets
switched off on day two.

## Limits — state these when you report results

The tool reads file paths and line counts. It cannot read intent.

- It guesses which files are tests from path and filename patterns. Unusual
  layouts will be misread.
- A refactor large enough that git stops recognising the file as a rename may
  be reported as `UNPROTECT` rather than `MIXED`. Both are problems, so the
  headline rate stays right; the label may not.
- A commit can be `GREEN` and still be bad work. Presence of a test is not
  quality of a test.
- Squash-merge histories compress many steps into one commit and will read
  worse than the work actually was. Say so if the repo squashes.
- Red/green pairing only works when both commits are inside the range you
  asked for. A `--since` that starts between them will show the green half as
  `UNPROTECT`. Widen the range before believing a sudden jump.

Report the number with its limits attached. A precise-looking percentage
presented without them will be believed more than it deserves.
