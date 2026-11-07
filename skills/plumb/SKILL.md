---
name: plumb
description: Entry point for disciplined code change. Routes to the right mode — behaviour change, structural change, or move lookup. Use when starting any code change, or when the user says "plumb", "start clean", "do this properly", "test first".
---

# Plumb

You are about to change code. Before you touch a file, decide which kind of
change this is. The two kinds never share a commit.

## Route

Ask yourself first. Ask the user only if you genuinely cannot tell.

**Does the program do something different when you are done?**

- **Yes** → behaviour change → load `plumb-rhythm`
- **No, code just moves around** → structural change → load `plumb-tidy`
- **Both** → do the structural part first, as its own commit, then the
  behaviour part. Load `plumb-tidy`, finish it, then load `plumb-rhythm`.

If you are unsure which it is, it is a behaviour change. Guessing "structural"
when it is not is how untested behaviour gets shipped.

## The rule that does not bend

A commit is structural **or** behavioural. Never both.

Structural commits leave every test exactly as it was — same tests, same
results. If a test had to change, it was a behaviour change wearing a disguise.

## Before you start

State these three things to the user in two lines, then begin:

1. Which kind of change this is
2. Which files you expect to touch
3. How you will know it worked (which test, which command)

If you cannot name the test, stop and say so. That is the signal that you do
not yet understand the task well enough to start.

## Scope

Change what the task needs. Nothing else.

If you notice something else that wants fixing, write it down and tell the user
at the end. Do not fix it now. A change that touches files nobody asked about
is a change nobody can review.

## When the user overrides you

They can. If the user says skip the test, or says commit it together, do what
they ask and say in one line what the risk is. Say it once. Do not repeat it
later in the session.
