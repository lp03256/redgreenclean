---
name: rgc-ledger
description: Show what was changed this session and in what order — tests written, moves applied, commits made. Use at the end of a work session, or when the user asks "what did you do", "summarise this session", "show the ledger".
---

# Ledger

A short record of what happened, in order. Written for the person reviewing
tomorrow, not for the person who was here today.

## What to produce

```
## Session ledger

### Behaviour
- RED   createOrder_whenStockIsZero_rejectsWithOutOfStock   (commit a1b2c3d)
- GREEN OrderService.createOrder — stock check before persist (commit e4f5g6h)

### Structure
- Extract Function: OrderValidator:40-58 -> checkStockAvailable  (commit i7j8k9l)
- Rename: tmp -> remainingStock                                   (commit i7j8k9l)

### Left alone deliberately
- OrderRepository.findAll has no test coverage. Out of scope for this card.
- PricingService has the same nested-conditional shape. Separate change.

### Test state
- Suite green. 412 passed, 0 failed. Command: ./gradlew test
```

## Rules for writing it

**Order matters more than completeness.** The thing a reviewer cannot get from
the diff is the sequence. Preserve it.

**Say what you did not do.** The "left alone deliberately" section is the most
useful part of this record, because it is the only place where a deliberate
decision to leave something is distinguishable from not having noticed it.

**Report the test state honestly.** If the suite is red, say it is red and
paste the failure. If you did not run it, say you did not run it. A ledger
claiming green when nobody ran the tests is worse than no ledger.

**Keep it short.** If the ledger is longer than a screen, the session did too
much and should have been several sessions.

## Where it goes

Print it. Do not write it to a file unless the user asks.

If the user wants it kept, write it to a path they name. Do not invent a
directory structure and start filling it. That is their decision, not yours.
