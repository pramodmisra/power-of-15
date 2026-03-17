# Original NASA/JPL Power of Ten — Reference Notes

This document summarizes Gerard J. Holzmann's original 10 rules for context. The full paper is available at: [spinroot.com/gerard/pdf/P10.pdf](https://spinroot.com/gerard/pdf/P10.pdf)

## The Original 10 Rules (2006, targeting C)

1. **Simple control flow** — No goto, setjmp/longjmp, or recursion
2. **Bounded loops** — All loops must have a statically provable upper bound
3. **No dynamic memory after init** — No malloc/free after initialization
4. **Short functions** — No more than 60 lines per function (one printed page)
5. **High assertion density** — Minimum 2 assertions per function
6. **Minimal scope** — Declare data at the smallest possible scope
7. **Check return values** — Every non-void return must be checked
8. **Limited preprocessor** — Only includes and simple macros
9. **Restricted pointers** — Max one level of dereference; no function pointers
10. **Zero warnings** — Compile and analyze with strictest settings, zero warnings

## What Changed in The Power of 15

| Original Rule | Modification for AI/ML |
|---------------|----------------------|
| Rule 2 (Bounded loops) | Added: early stopping for training, max_steps for agents |
| Rule 3 (No dynamic alloc) | Added: GPU tensor cleanup, `torch.no_grad()`, bounded DataFrames |
| Rule 4 (Short functions) | Added: pipeline orchestrator exception (up to 80 lines) |
| Rule 5 (Assertions) | Added: tensor shape, NaN/Inf, DataFrame schema assertions |
| Rule 6 (Minimal scope) | Added: hyperparameters in config dataclass |
| Rule 7 (Check returns) | Added: LLM API retry with backoff |
| Rule 8 (Limited preprocessor) | Mapped to: no eval/exec, approved framework decorators |
| Rule 9 (Restricted pointers) | Mapped to: no `any` types, flat config access |

## 5 New Rules (No NASA Equivalent)

| Rule | Why It's New |
|------|-------------|
| 11. Reproducibility | NASA code is deterministic by nature; ML has randomness |
| 12. No data leakage | NASA doesn't have train/test splits |
| 13. Experiment tracking | NASA tracks hardware configs, not model lineage |
| 14. Security hygiene | NASA code runs on isolated systems, not public APIs |
| 15. Dependency pinning | NASA locks toolchains; ML ecosystems change weekly |

## Holzmann's Philosophy

The original paper concludes with an analogy that still holds:

*"The rules act like the seat-belt in your car: initially they are perhaps a little uncomfortable, but after a while their use becomes second-nature and not using them becomes unimaginable."*

The Power of 15 extends this philosophy: when a model prices someone's insurance premium, when an agent accesses customer data, when a training pipeline feeds production — the rules exist to make the code worthy of trust.
