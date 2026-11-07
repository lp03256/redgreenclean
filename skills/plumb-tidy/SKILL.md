---
name: plumb-tidy
description: Structural change only — the code moves, the behaviour does not. Use when renaming, extracting, reordering, or cleaning up without changing what the program does.
---

# Tidy

Structural change. The program does exactly the same thing when you are done.

## The test is the proof

Before you start, run the tests and note the result. After you finish, run them
again. Same tests, same result, no test file edited.

If you had to change a test, you changed behaviour. Stop, undo, and go to
`plumb-rhythm` instead.

**If there are no tests covering what you are about to move**, say so to the
user before touching anything. Two honest options:

1. Write characterisation tests first — tests that pin down what the code does
   today, right or wrong. Then tidy safely.
2. Tidy without a net, in very small steps, and say plainly that this is what
   you are doing.

Pick option 1 unless the user says otherwise. Do not quietly pick option 2 and
describe it as safe.

## Size

One move per commit. Not one session per commit.

This feels slow and is the entire point. A commit containing one named move is
reviewable in ten seconds. A commit containing nine is reviewable in no amount
of time, so it gets approved unread.

## Order

When several tidyings are available, do them in this order:

1. **Dead code** — delete it. Nothing else gets easier until it is gone.
2. **Names** — rename before you move. Moving badly named things just spreads
   the confusion.
3. **Extract** — pull out the pieces that now have obvious names.
4. **Reorder** — put things that change together next to each other.

Deleting first is not a style preference. Every later step costs more if you
carry dead code through it.

## What counts as structural

Renaming. Extracting a function, variable, or class. Inlining one. Moving a
function between files. Reordering members. Replacing a comment with a better
name. Turning a nested conditional into guard clauses. Removing code nothing
calls.

## What does not

Changing a default value. Adding a null check. Widening or narrowing a type in
a way that accepts different input. Changing the order of two calls that have
side effects. Any of these can change behaviour. They belong in `plumb-rhythm`.

## Before each move

Say it in one line:

```
Extract Function: lines 40-58 of OrderValidator.java -> checkStockAvailable()
```

Then make the change and run the tests.

## Stop condition

Stop when the thing you came to do is done. Tidying has no natural end, and
"while I'm in here" is how a two-file change becomes a twenty-file change that
nobody will review.
