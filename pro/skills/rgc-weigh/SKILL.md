---
name: rgc-weigh
description: Decide how much ceremony a change deserves before starting it. Use at the start of any change, when the user says "is this worth a test", "quick fix", "how much process", or when a change feels too small for the full loop.
---

# Weigh

Not every change deserves the full loop. A discipline that treats a typo fix
like a new payment flow gets abandoned inside a week, and then you have no
discipline at all.

Weigh the change first. Say which weight you picked and why, in one line.

## The three weights

**Light** — the change cannot be wrong in an interesting way.
Typo in a string. A comment. A log message. Formatting. Bumping a version
number nothing reads conditionally.
→ Make the change. Commit. No test. Say "light" and move on.

**Standard** — the change alters behaviour that something depends on.
A bug fix. A new branch in a condition. A new field. A changed default.
→ Full `rgc-rhythm`: red, green, clean. Three commits.

**Heavy** — the change is hard to reverse, or you do not yet understand the
code you are about to change.
Data migration. Auth or permission logic. Money. Concurrency. Anything in code
with no tests that you did not write. Anything where being wrong is expensive
and silent.
→ `rgc-net` first to build a safety net, then `rgc-rhythm`, then a second pair
of eyes before merge. Say out loud that this is heavy.

## How to decide

Ask these in order. The first "yes" sets the weight.

1. Could this be wrong in a way that no one notices for a month? → **heavy**
2. Does it touch money, identity, permissions, or stored data? → **heavy**
3. Am I changing code I do not understand and cannot test? → **heavy**
4. Does the program behave differently for any input? → **standard**
5. Otherwise → **light**

## The honest failure mode

The temptation is always to grade down — to call a standard change light
because you are confident. Confidence is not evidence, and it is highest
exactly when you are working fast in familiar code, which is where most
defects come from.

**When you are unsure between two weights, take the heavier one.** The cost of
over-testing is minutes. The cost of under-testing is a defect you find in
production in six weeks with no test to characterise it.

## When the user grades it down

They may. If the user says "it's just a one-liner, skip the test", do what they
ask, record it, and say the risk once:

```
rgc-audit step --kind waive --ref "one-line default change, no test (user call)"
```

Say it once. Do not bring it up again later in the session.

## Output

One line before you start:

```
Weight: standard — changes the rejection branch for zero stock, one input
class behaves differently.
```
