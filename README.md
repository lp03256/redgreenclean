# Red Green Clean

**Keep your changes true.**

Red Green Clean is a small set of Claude Code skills that hold an AI coding agent to the
discipline a careful engineer already uses: write the test first, change
behaviour and structure in separate commits, and name every refactoring you
apply so it can be checked.

It is not a framework and it does not run your build. It is a set of rules the
agent reads before it touches your code.

## Why

Coding agents are fast and agreeable. Left alone they will write the production
code before the test, mix a rename into a bug fix, and tell you it all went
well. None of that shows up in the diff review, because the diff looks fine.
What is missing is the order things happened in.

Red Green Clean makes the order explicit and checkable.

## The idea in one page

Two kinds of change exist, and they must never share a commit:

| Kind | What it does | How you check it |
|------|--------------|------------------|
| **Structural** | Moves code around. Renames, extracts, reorders. | Tests pass before and after, unchanged. |
| **Behavioural** | Changes what the program does. | A test that failed now passes. |

Mixing them is what makes a diff unreviewable. A reviewer cannot tell whether
the 200 moved lines are the same 200 lines, so they skim, and the one changed
line slips through. Separating them is the whole trick, and it is Kent Beck's,
not ours.

Red Green Clean adds one thing on top: a **named move**. Every structural change you make
has to be one of the moves in the catalog, stated by name before it is applied.
"Clean this up" is not a move. "Extract Function" is.

## Install

```bash
git clone https://github.com/lp03256/redgreenclean.git
cd redgreenclean && ./install.sh
```

This symlinks the skills into `~/.claude/skills/`. Nothing else is touched.
Uninstall with `./install.sh --remove`.

If you have bought Pro, clone it into `pro/` inside this directory and run
`./install.sh --pro`. The two are separate repositories; this one is MIT and
Pro is not.

## Use

| Command | What it does |
|---------|--------------|
| `/rgc` | Picks the right mode for what you are doing |
| `/rgc-rhythm` | Red → green → clean loop for a behaviour change |
| `/rgc-tidy` | Structural change only, no behaviour |
| `/rgc-move` | Look up a named refactoring and its mechanics |
| `/rgc-ledger` | Show what was applied this session |

Start with `/rgc`. It will ask you one question and route from there.

The project is Red Green Clean; the commands are `rgc` because you will type
them a hundred times a week.

## Pro

The free core above is complete and standalone. Pro adds the parts that need
tooling rather than advice:

| | |
|---|---|
| `/rgc-weigh` | Grade the change first, so a typo fix does not get the full ceremony |
| `/rgc-net` | Build characterisation tests around code that has none |
| `/rgc-audit` | Record what the agent did, in order, as it happens |
| `rgc-drift` | Read any repo's git history and report where discipline slipped |

`rgc-drift` works on repos that never used this tool. Point it at something you
already have:

```
rgc-drift --since origin/main
```

See `pro/README.md`. Pro is licensed separately; it is not MIT.

## What Red Green Clean will not do

- It will not run your tests for you. It tells the agent when to run them; your
  project's own commands do the work.
- It will not stop you overriding it. Every gate can be waived by saying so.
  The point is that waiving it is a decision you make out loud.
- It does not know your architecture. Red Green Clean is about how you change code, not
  about what your code should be.

## Reading

The methods here are not new. They come from:

- Kent Beck, *Test-Driven Development by Example* — the red/green/refactor loop
- Kent Beck, *Tidy First?* — separating structural from behavioural change
- Martin Fowler, *Refactoring* (2nd ed.) — the move catalog and its mechanics
- Robert C. Martin, *Clean Code* — naming and function size

If you only read one, read *Tidy First?*. It is short and it is the core of
this tool.

## Licence

MIT. See LICENSE.
