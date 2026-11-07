---
name: plumb-rhythm
description: The red-green-clean loop for a behaviour change. Write a failing test, make it pass with the least code, then tidy. Use when adding a feature, fixing a bug, or changing what the program does.
---

# Rhythm

Three steps, in order, every time. Each one is a separate commit.

## Red — write the failing test

Write one test for the behaviour you want. Run it. Watch it fail.

A test that fails to compile counts as failing. A test that passes the first
time you run it is not a test of new behaviour — either the behaviour already
exists, or the test does not check what you think it checks. Find out which
before going on.

Write the smallest test that can fail for the right reason. One behaviour per
test. If you need two asserts to describe one outcome, that is fine. If you
need two asserts for two outcomes, that is two tests.

**Name the test so the failure explains itself.** When this test fails in CI
eighteen months from now, its name is the only thing the person on call has.

```
createOrder_whenStockIsZero_rejectsWithOutOfStock
```

not

```
testCreateOrder
```

Do not write production code in this step. Not one line.

**Commit:** the test alone, failing. Yes, really. A red commit is a record of
what you set out to do.

## Green — make it pass with the least code

Write the smallest amount of production code that turns the test green. Nothing
more.

Ugly is fine here. Hardcoding is fine here if it genuinely is the smallest step
and you have another test coming that will force the real thing. Duplication is
fine here. You are buying one thing only: a passing test.

Resist every urge to improve what you are writing. Improvement is the next
step, and it is much safer with a green test behind you.

Run the whole suite, not just your test. A new behaviour that breaks an old one
is not done.

**Commit:** the production code that makes it pass.

## Clean — tidy what you just wrote

Now improve it, with the tests green and staying green.

Run the tests after every single change, not at the end of a batch. The value
of this step comes from the tight loop; if you make six changes and then run
the tests, you have given up the thing that makes refactoring safe.

Use named moves. Load `plumb-move` if you want the catalog. Say the name of the
move before you apply it.

Stop when the code is clear, not when it is clever.

**Commit:** structural only. No behaviour change. Tests identical before and
after.

## If you get stuck in green

If making the test pass is turning into a large, tangled piece of work, the
test was too big. Throw the production code away, make the test smaller, and
start again. This feels like losing ground and is almost always faster.

## What to report

At the end, in four lines:

- The test you wrote
- The behaviour it pins down
- What you tidied, by move name
- Anything you noticed and deliberately left alone
