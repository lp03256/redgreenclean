---
name: rgc-net
description: Build characterisation tests around code that has none, so it can be changed safely. Use before touching untested legacy code, or when the user says "there are no tests", "I don't know what this does", "legacy", "afraid to touch this".
---

# Net

For code you need to change and cannot currently test. The goal is not to
prove the code is right. The goal is to **pin down what it does today**, right
or wrong, so that if you change it by accident you find out immediately.

These are characterisation tests. They describe, they do not judge.

## The rule that makes this work

**Do not fix anything you find.** You will find bugs. Write a test that asserts
the buggy behaviour, note it, and move on. Fixing it now means you are changing
behaviour with no net, which is the exact thing you came here to avoid.

A test asserting wrong behaviour is not a lie. It is a record, and it is how
you will later prove your fix changed only what you meant.

## Steps

**1. Find the seam.**
Locate the smallest place you can call the code from a test. A public function
is ideal. If everything is tangled, look for the outermost thing you can call
with inputs you control.

If there is genuinely no seam, say so. Introducing one is itself a structural
change and belongs in `rgc-tidy` first, as its own commit.

**2. Call it and see what happens.**
Write a test that calls the code with ordinary input and asserts something you
know is wrong, for example `assert result == "PLACEHOLDER"`. Run it. The
failure message tells you the actual value. Put that value in the assertion.

This feels backwards and is the fastest way to learn what untested code does.

**3. Widen until the shape is covered.**
Add cases until you have, at minimum:
- the ordinary path
- empty or zero input
- null or missing input
- one boundary value
- one input that makes it throw, if anything does

Stop when you can describe the behaviour in a sentence. You are not aiming for
coverage targets; you are aiming for confidence to change it.

**4. Name them for what they record, not what is right.**

```
reject_whenStockIsNegative_currentlyReturnsFalse
```

The word "currently" is doing real work. It tells the next reader this was
observed, not designed.

**5. Commit the net on its own.**
Tests only, no production change. This commit is valuable by itself, and it is
reviewable in isolation.

**6. Note what looked wrong.**
List anything you pinned down that seems like a bug. Do not fix it. Hand the
list to the user.

## Then what

With the net in place, go to `rgc-rhythm`. When your change makes a
characterisation test fail, that is information: either you changed something
you did not mean to, or you deliberately fixed the bug and should now update
that test and say so in the commit.

## What this is not

This is not a substitute for real tests of intended behaviour. It is
scaffolding that makes change survivable. Once you understand the code, replace
the characterisation tests with tests that state what the code *should* do.
