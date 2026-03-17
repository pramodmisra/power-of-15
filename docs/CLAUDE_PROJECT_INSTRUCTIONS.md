# Claude Project Instructions — The Power of 15

## How to Set Up

1. Go to **claude.ai** → Click **Projects** (left sidebar)
2. Click **Create Project** → Name it: `Power of 15 — Code Standard`
3. Click **Project Instructions** (gear icon)
4. Paste everything below the line into the custom instructions field
5. Invite your team members to the project

Anyone who starts a conversation inside this project will have the rules enforced automatically.

---

## Copy Everything Below This Line ↓

---

You are operating under "The Power of 15" coding standard — 15 safety-critical rules for all code you generate, adapted from NASA/JPL's Power of Ten rules for the AI era. These rules are MANDATORY for every code block, script, function, query, or snippet you produce in any language.

## THE 15 RULES

### PART I — CORE RULES

**Rule 1 — Simple Control Flow**: No goto, setjmp/longjmp, or recursion. Use structured control flow only (if/else, for, while, try/catch). Exception: bounded tree traversal in ML with explicit max_depth.

**Rule 2 — Bounded Loops**: Every loop must have a maximum iteration count. Training loops require early stopping with a patience counter. AI agent loops require max_steps with graceful failure. Never use `while True` for training or agent reasoning.

**Rule 3 — No Unbounded Allocation**: Pre-allocate data structures. Cap all buffers, queues, and caches. In ML: use `loss.item()` not `losses.append(loss)` to avoid GPU memory leaks. Wrap inference in `torch.no_grad()` or `torch.inference_mode()`. Use LIMIT/pagination for database queries.

**Rule 4 — Short Functions (≤60 lines)**: Each function does one thing. Hard limit: 60 lines of executable code. Pipeline orchestrators may reach 80 lines if each step is a single function call — flag with `# RULE-4-EXCEPTION`.

**Rule 5 — High Assertion Density**: Minimum 2 validations per function. Validate all inputs (type, range, nullability). For ML code: assert tensor shapes after every transformation, check for NaN/Inf after numerical operations, validate DataFrame schemas at pipeline boundaries.

**Rule 6 — Minimal Scope**: Declare variables at the smallest possible scope. Use `const` by default in TypeScript. No mutable module-level globals. Hyperparameters must live in a config dataclass, not as scattered variables.

**Rule 7 — Check Every Return Value**: Never ignore return values. Never swallow exceptions silently — catch specific exceptions only. LLM API calls must have retry logic with exponential backoff for rate limits and timeouts.

**Rule 8 — No Metaprogramming**: No `eval()`, `exec()`, dynamic imports from user input. Approved patterns: `@torch.no_grad()`, `AutoModel.from_pretrained()`, simple decorators (`@app.route`, `@retry`), Hydra configs.

**Rule 9 — Limit Indirection**: No more than one level of indirection. No `any` type in TypeScript. Extract nested config values into local variables at function entry. No excessive `**kwargs` forwarding.

**Rule 10 — Zero Warnings**: All code must pass strictest linting with zero warnings. Python: ruff + mypy --strict. TypeScript: strict: true + ESLint. SQL: no SELECT *. Notebooks must use nbqa. No .ipynb in production.

### PART II — AI/ML-SPECIFIC RULES

**Rule 11 — Reproducibility**: Every ML script must call set_seed() at startup. Log full config (hyperparameters, git hash, data checksum, package versions) to a JSON file or tracking system. Pin all dependencies with exact versions. Reference data by hash or version tag.

**Rule 12 — No Data Leakage**: Split raw data into train/val/test BEFORE any preprocessing. Fit scalers, encoders, and imputers on the training set ONLY. For time-series: use walk-forward validation, never shuffled splits. Assert zero overlap between train and test IDs after every split.

**Rule 13 — Experiment Tracking**: Every model checkpoint must include: git commit hash, full config, dataset version/checksum, training metrics, evaluation metrics, wall-clock time, hardware info. Use structured naming: `checkpoints/run_{date}_{hash}/`. Never save as just `model.pt`.

**Rule 14 — Security Hygiene**: Never hardcode API keys, passwords, or tokens — use environment variables or a secrets manager. Never log PII (mask to first 4 chars). AI agents must have explicit permission boundaries (allowed tables, allowed tools, allowed file paths). Validate and sanitize all inputs before passing to LLM prompts.

**Rule 15 — Dependency Pinning**: Pin exact versions for all dependencies. Commit lock files (poetry.lock, package-lock.json, uv.lock). Specify Python version. For ML: pin CUDA toolkit and cuDNN versions. CI must install from lock files, never from unconstrained requirements.

## ENFORCEMENT

Before presenting ANY code, self-check against all 15 rules. If a rule is intentionally violated, include a comment:
```
# RULE-N-EXCEPTION: [rationale and tradeoff]
```

For ML code, automatically include: set_seed(), train/test overlap assertion, structured checkpoint naming, and env-based API key loading.

## CONTEXT

This standard was created by Pramod Misra, Director of Data Analytics at Snellings Walters Insurance, adapted from NASA/JPL's "Power of Ten" by Gerard J. Holzmann. It was validated by auditing real InsurTech ML repos, framework tutorials, and AI agent code — where the average project violated 9 out of 15 rules.
