---
name: rgc-move
description: Look up a named refactoring — when to use it, the steps, and what to watch for. Use when deciding how to restructure code, or when the user asks "what refactoring is this", "how do I extract", "is this a code smell".
---

# Move

Every structural change you make has a name. Use it.

Naming the move before you apply it does three things: it forces you to decide
what you are doing before you do it, it gives the reviewer a one-line summary,
and it makes the change checkable — either the code afterwards matches the
shape that move produces, or you did something else.

"Clean this up" is not a move. "Replace Nested Conditional with Guard Clauses"
is.

## Using the catalog

The full catalog is in `reference/moves.md`. Read it when you need a move you
do not already know cold.

Pick a move by starting from what bothers you about the code, not from the list
of moves. The catalog is indexed both ways.

## The four that cover most cases

If you learn only four, learn these.

**Extract Function** — a block of code inside a longer function has a job you
can name. Pull it out and call it by that name. This is the move you will
reach for most. The test of whether it worked: the calling code now reads like
a description of what happens.

**Rename** — the name does not say what the thing is. Change it. Cheapest move
there is, and the one with the largest effect on how readable the code is. Do
this before any move that relocates code.

**Replace Nested Conditional with Guard Clauses** — a function is three levels
of `if` deep. Turn the exceptional cases into early returns at the top, leaving
the main path flat at the bottom. Deep nesting hides the normal case; this move
puts it back in plain sight.

**Inline** — a function, variable, or class whose body is as clear as its name,
and which adds a hop for no gain. Put the body back where it was called and
delete it. Abstractions that earn nothing cost something.

## Choosing

| What bothers you | Move to reach for |
|---|---|
| Function is too long to hold in your head | Extract Function |
| You cannot tell what a name refers to | Rename |
| Three levels of nesting | Replace Nested Conditional with Guard Clauses |
| An expression is doing too much in one line | Extract Variable |
| The same shape of code in three places | Extract Function, then Pull Up |
| A function takes six parameters | Introduce Parameter Object |
| A class knows too much about another class | Move Function |
| A comment explains what the next line does | Extract Function, name it after the comment, delete the comment |
| A flag parameter switches between two behaviours | Remove Flag Argument — split into two functions |
| Dead code | Delete it. No move needed. |

## Before applying

State it:

```
Move: Extract Variable
Where: PricingService.java:88
Why: the discount expression is three operations deep and unnamed
```

Then do it, then run the tests.

## When no move fits

Sometimes the right answer is that the design is wrong, not that the code is
untidy. Refactoring moves will not rescue a wrong model; they will just make
the wrong model tidier and harder to replace.

If you find yourself applying move after move and the code is not getting
clearer, stop and say so. That is a design conversation, not a tidying task.
