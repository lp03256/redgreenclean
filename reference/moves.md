# Move catalog

Named structural changes. Each one leaves behaviour unchanged.

Descriptions are deliberately short — enough to pick the right move and apply
it, not a substitute for Fowler's *Refactoring*, which has the full mechanics
and the edge cases.

---

## Composing functions

### Extract Function
**When:** a block inside a longer function has a job you can name.
**Do:** move the block into a new function named after *what it achieves*, not
how. Pass what it needs, return what it produces.
**Watch for:** variables modified by the block. If more than one is written and
used afterwards, extract a smaller block or return an object.

### Inline Function
**When:** the body is as clear as the name and adds nothing.
**Do:** replace every call with the body, delete the function.
**Watch for:** callers you missed. Search the whole repo, not the open file.

### Extract Variable
**When:** an expression is long enough that you have to parse it.
**Do:** assign the sub-expression to a named local, use the name.
**Watch for:** side effects. If the expression calls something that mutates
state, extracting it changes when that happens.

### Inline Variable
**When:** the name says no more than the expression did.
**Do:** replace the name with the expression, delete the assignment.

### Change Function Declaration
**When:** the name is wrong, or the parameters are.
**Do:** for a small codebase, change it and fix the callers. For a large one,
add the new version alongside, migrate callers, then delete the old.

### Remove Flag Argument
**When:** a boolean parameter picks between two behaviours.
**Do:** split into two functions with names that say which is which.
**Why:** `setLocked(true)` tells the reader nothing at the call site. `lock()`
does.

---

## Moving things

### Move Function
**When:** a function uses another class's data more than its own.
**Do:** move it to the class whose data it uses. Leave a delegating call behind
if callers are many, then migrate and delete.

### Move Field
**When:** a field is always used together with data on another class.
**Do:** move it, update accessors, migrate callers.

### Slide Statements
**When:** related lines are separated by unrelated ones.
**Do:** move them together. Nothing else.
**Watch for:** order dependence. Only slide past statements that do not touch
the same state.

### Split Loop
**When:** one loop does two unrelated things.
**Do:** two loops over the same collection. Yes, this iterates twice. Measure
before worrying about it; clarity first, and extraction usually follows.

---

## Simplifying conditionals

### Replace Nested Conditional with Guard Clauses
**When:** nesting hides the normal path.
**Do:** turn each exceptional case into an early return at the top. The main
path ends up flat at the bottom of the function.

### Decompose Conditional
**When:** the condition and the branches are both complicated.
**Do:** extract the condition into a well-named predicate, and each branch into
its own function.

### Consolidate Conditional Expression
**When:** several conditions in a row produce the same result.
**Do:** combine with `and`/`or`, then extract into one named predicate.

### Replace Conditional with Polymorphism
**When:** the same `switch` on a type code appears in several places.
**Do:** one subclass or strategy per case, move each branch into it.
**Watch for:** doing this too early. One switch is fine. Three is the signal.

---

## Data

### Encapsulate Variable
**When:** data is reachable and modifiable from everywhere.
**Do:** route access through functions so you can see and control the writes.

### Introduce Parameter Object
**When:** the same group of parameters travels together through several
functions.
**Do:** make a small type holding them. Often this type then attracts behaviour
of its own, which is the real win.

### Replace Primitive with Object
**When:** a string or number has rules attached that live elsewhere.
**Do:** give it a type that holds the rules.
**Example:** an email that gets validated in four places wants to be an `Email`.

### Split Variable
**When:** one variable is assigned twice for two different purposes.
**Do:** two variables, each named for its purpose. A variable that means two
things is a bug waiting for a maintainer.

---

## Organising larger pieces

### Extract Class
**When:** a class has a subset of fields and methods that only talk to each
other.
**Do:** move that subset into its own class.

### Inline Class
**When:** a class no longer does enough to justify existing.
**Do:** fold it into its only caller.

### Hide Delegate
**When:** callers chain through one object to reach another (`a.getB().getC()`).
**Do:** add a method on the first object that does the hop.

### Remove Middle Man
**When:** a class does nothing but forward calls.
**Do:** let callers talk to the real object directly.
**Note:** this is the opposite of Hide Delegate. Both are right sometimes. The
balance shifts as code changes; revisit rather than picking a side forever.

---

## Smell to move

| Smell | Likely move |
|---|---|
| Long function | Extract Function |
| Long parameter list | Introduce Parameter Object, Remove Flag Argument |
| Duplicated code | Extract Function, then move it somewhere shared |
| Large class | Extract Class |
| Feature envy — method uses another object's data more than its own | Move Function |
| Data clump — same fields travel together | Introduce Parameter Object |
| Primitive obsession | Replace Primitive with Object |
| Repeated switch on a type | Replace Conditional with Polymorphism |
| Message chain — `a.getB().getC().getD()` | Hide Delegate |
| Comment explaining the next block | Extract Function named after the comment |
| Dead code | Delete |
| Speculative generality — built for a case that never came | Inline, Remove Middle Man, Delete |

---

## Two rules that override everything here

**Tests green throughout.** Run them after each move, not after a batch. A
refactoring with no tests is just editing, and editing has a defect rate.

**One move per commit.** The reviewer's ability to check your work drops to
roughly zero the moment two moves share a diff.
