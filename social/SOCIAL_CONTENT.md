# Social Media Content Package
## "The Power of 15" Launch — Pramod Misra

---

# LINKEDIN ARTICLE (Long-form)

**Title**: NASA Built 10 Rules for Code That Controls Spaceships. I Added 5 More for Code That Controls AI.

**Subtitle**: I audited real InsurTech ML repos and AI agent code against these rules. The results were alarming.

---

In 2006, Gerard Holzmann at NASA's Jet Propulsion Laboratory published "The Power of Ten" — 10 strict coding rules for software where your life depends on correctness. Code for the airplane you fly on. The nuclear plant near your house. The spacecraft carrying astronauts to orbit.

I've spent the last two years building production AI systems in the insurance industry — from carrier accounting automation to AI-powered claims agents. And I've come to a conclusion:

**The AI code we're writing today needs rules just as strict.**

Not because an AI model will crash an airplane. But because a model trained on leaked data will misprice insurance premiums for thousands of families. An agent loop without a bound will burn $500 in API tokens in 20 minutes. A hardcoded API key in a GitHub repo will get exploited before you wake up tomorrow.

So I took Holzmann's original 10 rules and adapted them for the AI era. Then I added 5 new rules that NASA never needed — because they weren't dealing with training loops, GPU memory, data leakage, or LLM agent chains.

**Then I tested them against real code.**

### What I Found

I audited publicly available code across three categories:

**1. Insurance ML Projects on GitHub** (5 repos, claim prediction and fraud detection)
- 4 out of 5 had data leakage — fitting scalers on the entire dataset before splitting train/test
- 5 out of 5 had zero random seeds — the "95% accuracy" in their README is non-reproducible
- 2 had API keys committed to source control

**2. Popular ML Tutorials** (PyTorch, scikit-learn, HuggingFace)
- GPU memory leak patterns taught as the default in beginner tutorials
- Training loops with no early stopping and no convergence checks
- Models saved as `model.pt` with zero metadata about what produced them

**3. AI Agent Frameworks** (LangChain, CrewAI)
- Multiple documented GitHub issues of agents stuck in infinite loops
- One framework function silently ignored the `max_iterations` parameter
- `PythonREPLTool` gives LLMs unrestricted code execution — any prompt injection becomes arbitrary code

The average project violated **9 out of 15 rules**.

### The 5 Rules NASA Didn't Need (But You Do)

The original Power of Ten rules handle control flow, memory, function size, assertions, scope, error handling, metaprogramming, pointer safety, and static analysis. All of these still apply — with modifications for ML patterns.

But AI code has 5 failure modes that didn't exist in 2006:

**Rule 11: Reproducibility by Default** — Every ML experiment must be reproducible from a single command. All sources of randomness must be explicitly seeded and logged. Environments must be pinned. Data must be versioned.

**Rule 12: No Data Leakage** — Training data and evaluation data must be strictly separated. Split first, transform later. No exceptions.

**Rule 13: Experiment Tracking and Model Lineage** — Every model artifact must be traceable to the exact code, data, config, and environment that produced it.

**Rule 14: Security, Secrets, and Sensitive Data Hygiene** — No secrets in code. No PII in logs. AI agents must have explicit permission boundaries.

**Rule 15: Dependency Pinning and Environment Determinism** — Every project must have a fully pinned, reproducible dependency specification.

### Why This Matters for Insurance

I work in insurance, where a model's prediction directly impacts someone's premium, their claim settlement, their financial security. When an insurance ML model is trained on leaked data, it's not just a technical bug — it's a pricing error that affects real people.

The insurance industry is adopting AI faster than it's adopting the engineering discipline to support it. These 15 rules are my attempt to close that gap.

### Get the Full Document

I've published the complete "Power of 15" coding standard as a markdown file that you can drop directly into any project. It includes:

- All 15 rules with language-specific patterns (Python, TypeScript, SQL)
- ML-specific modifications to the original NASA rules
- Code examples for every rule
- A summary reference card

Built to work as a `CLAUDE.md` import for Claude Code, a system prompt for Claude.ai, or a team coding standard for any AI-assisted development workflow.

Comment "RULES" and I'll share the link.

---

**Pramod Misra**
Director of Data Analytics | Snellings Walters Insurance, Atlanta, GA
Georgia Institute of Technology

*Adapted from "The Power of Ten — Rules for Developing Safety Critical Code" by Gerard J. Holzmann, NASA/JPL Laboratory for Reliable Software.*

---
---

# TWITTER/X THREAD (15 tweets)

**Tweet 1 (Hook)**
NASA wrote 10 rules for code that controls spaceships.

I added 5 more for code that controls AI.

Then I audited real insurance ML repos and AI agent code against all 15.

The results? A thread 🧵

**Tweet 2**
In 2006, Gerard Holzmann at NASA/JPL published "The Power of Ten" — 10 strict coding rules for safety-critical software.

Code for airplanes. Nuclear plants. Spacecraft.

I adapted them for AI/ML code. Here's why they needed updating ↓

**Tweet 3**
I audited 5 open-source insurance ML projects on GitHub.

4 out of 5 had DATA LEAKAGE — fitting scalers on the entire dataset before splitting train/test.

That "95% accuracy" in the README? Meaningless. It would collapse in production.

(Rule 12: Split first, transform later.)

**Tweet 4**
5 out of 5 repos had ZERO random seeds set.

No `random.seed()`. No `np.random.seed()`. No `torch.manual_seed()`.

The results can never be reproduced — not even by the author.

(Rule 11: Reproducibility by default.)

**Tweet 5**
2 repos had API keys hardcoded in source code.

One was an actual OpenAI key committed to GitHub.

In insurance, where we handle PII daily, this is a compliance nightmare waiting to happen.

(Rule 14: No secrets in code. Ever.)

**Tweet 6**
Then I looked at AI agent frameworks.

LangChain's GitHub has MULTIPLE issues filed about agents stuck in infinite loops — burning API tokens endlessly.

One function (create_json_agent) silently ignored the max_iterations parameter.

(Rule 2: All loops must have a bounded upper limit.)

**Tweet 7**
LangChain's PythonREPLTool gives the LLM unrestricted code execution.

Any prompt injection = arbitrary Python on your machine.

In a production insurance system? That's a breach.

(Rule 14: AI agents must have explicit permission boundaries.)

**Tweet 8**
The original NASA rules I kept (with ML modifications):

Rule 1: Simple control flow only
Rule 2: Bounded loops (+ early stopping for training)
Rule 3: No unbounded allocation (+ GPU tensor cleanup)
Rule 4: Short functions (≤60 lines)
Rule 5: High assertion density (+ data shape/NaN checks)

**Tweet 9**
More original rules, adapted:

Rule 6: Minimal variable scope (hyperparams in dataclasses)
Rule 7: Check every return value (+ LLM API retry logic)
Rule 8: No metaprogramming tricks
Rule 9: Limit indirection (no `any` types)
Rule 10: Zero linter warnings

**Tweet 10**
The 5 NEW rules I added for the AI era:

Rule 11: Reproducibility by default — seed everything, log everything
Rule 12: No data leakage — split first, transform later
Rule 13: Experiment tracking — every model traceable to code+data+config
Rule 14: Security hygiene — no secrets, no PII in logs, bounded agents
Rule 15: Dependency pinning — exact versions, lock files

**Tweet 11**
The most dangerous finding from the audit:

Data leakage doesn't crash your code.
It doesn't throw an error.
It doesn't show a warning.

It just makes your model look better than it is.

In insurance, that means underpriced premiums and underestimated reserves.

**Tweet 12**
The average project I audited violated 9 out of 15 rules.

These aren't obscure edge cases.
These are:
- No seeds
- No validation
- No error handling
- No dependency pinning
- Keys in code

Basic engineering discipline. Missing everywhere.

**Tweet 13**
I built the full "Power of 15" as a markdown file you can:

✓ Drop into CLAUDE.md for Claude Code
✓ Use as a system prompt
✓ Adopt as a team coding standard

Every rule has code examples in Python, TypeScript, and SQL.

**Tweet 14**
Why I care about this:

I build production AI systems in insurance. A bad model doesn't just fail a benchmark — it misprices someone's coverage.

Engineering discipline for AI isn't optional. It's the floor.

**Tweet 15 (CTA)**
NASA's 10 rules weren't built for the AI era. So I updated them.

The full "Power of 15" document + audit report:
→ Comment "RULES" and I'll DM you the link

Pramod Misra
Director of Data Analytics | Snellings Walters Insurance
Georgia Institute of Technology

---
---

# LINKEDIN CAROUSEL CONTENT (10 slides)

Slide 1 — Title
"The Power of 15"
NASA's Coding Rules, Rewritten for the AI Era
Pramod Misra | Director of Data Analytics | Snellings Walters Insurance | Georgia Tech

Slide 2 — The Problem
"I audited real InsurTech ML repos and AI agent code."
"The average project violated 9 out of 15 rules."

Slide 3 — Top Finding: Data Leakage
"4 out of 5 insurance ML repos had data leakage."
"They fit scalers BEFORE splitting train/test."
"That '95% accuracy'? Meaningless in production."
→ Rule 12: Split first, transform later.

Slide 4 — No Reproducibility
"5 out of 5 repos had ZERO random seeds."
"No one — including the author — can reproduce the results."
→ Rule 11: Seed everything. Log everything.

Slide 5 — Agent Loops
"AI agents stuck in infinite loops — burning tokens."
"One framework silently ignored max_iterations."
→ Rule 2: All loops must have a bounded upper limit.

Slide 6 — Security Gaps
"API keys hardcoded in source code."
"LLMs with unrestricted code execution."
→ Rule 14: No secrets. Bounded agent permissions.

Slide 7 — The Original 10 (NASA/JPL)
1. Simple control flow
2. Bounded loops
3. No unbounded allocation
4. Short functions
5. High assertion density
6. Minimal scope
7. Check every return value
8. No metaprogramming
9. Limit indirection
10. Zero warnings

Slide 8 — The 5 New Rules for AI
11. Reproducibility by default
12. No data leakage
13. Experiment tracking
14. Security & secrets hygiene
15. Dependency pinning

Slide 9 — Why It Matters
"A bad model doesn't just fail a benchmark."
"In insurance, it misprices someone's coverage."
"Engineering discipline for AI isn't optional."

Slide 10 — CTA
"The Power of 15"
Full document + audit report available.
Comment "RULES" for the link.

Pramod Misra
Director of Data Analytics
Snellings Walters Insurance | Georgia Tech
