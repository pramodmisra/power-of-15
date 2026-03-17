# The Power of 15 — Rules for Developing Safety-Critical AI Code

**Author**: Pramod Misra, Director of Data Analytics, Snellings Walters Insurance, Atlanta, GA | Georgia Institute of Technology

> Adapted from Gerard J. Holzmann's "The Power of Ten — Rules for Developing Safety Critical Code" (NASA/JPL).
> Enhanced with rules for machine learning, AI agent development, and modern AI-assisted workflows.
> Purpose: Enforce as a mandatory standard for all code produced by Claude Code, Claude.ai artifacts, and any AI-assisted development workflow.

---

## Foreword

In 2006, Gerard Holzmann at NASA's Jet Propulsion Laboratory wrote 10 rules for code where your life depends on its correctness — code for spacecraft, airplanes, and nuclear systems. Those rules were deliberately strict, deliberately small in number, and deliberately verifiable by tools.

I work in insurance, where a model's prediction directly impacts someone's premium, their claim settlement, their financial security. I also build AI systems — carrier accounting automation, claims processing agents, retention analytics — and compete in AI hackathons where speed often wins over discipline.

After auditing publicly available InsurTech ML code, popular framework tutorials, and AI agent implementations against Holzmann's original rules, I found that the average project violated 9 out of 15 rules. The most dangerous violations were silent: data leakage that inflates accuracy without throwing an error, agent loops that burn API tokens without crashing, API keys committed to public repos without a warning.

Holzmann's original 10 rules still hold. But the AI era introduced failure modes he never needed to consider: GPU memory leaks from unreleased tensors, data leakage from fitting before splitting, non-reproducible experiments from unseeded randomness, and AI agents with unrestricted execution privileges.

So I adapted the original 10 for modern multi-language AI development, and added 5 new rules for the gaps that only exist in ML and agent systems. The result is this document — 15 rules, each with code examples, each mechanically checkable, each battle-tested against real production code.

The rules are strict. That's the point. When it counts — when a model prices someone's insurance, when an agent accesses customer data, when a training pipeline feeds a production system — it's worth going the extra mile.

— Pramod Misra, March 2026

---

## How to Use This File

- **Claude Code**: Add `import: CODING_RULES.md` to your project's `CLAUDE.md`, or paste these rules directly into `CLAUDE.md`.
- **Claude.ai**: Reference this document in your system prompt or user preferences with: *"Follow the coding rules in CODING_RULES.md for all code you generate."*
- **Scope**: These rules apply to every language (Python, TypeScript, SQL, Bash, React/JSX, etc.) unless a rule explicitly states a language-specific exception.
- **ML/AI Scope**: Rules 11–15 specifically target machine learning pipelines, model training, AI agent code, and data-intensive applications. They apply whenever the code touches training data, model weights, inference endpoints, or experiment workflows.

---

## PART I — CORE RULES (NASA/JPL Adapted)

### Rule 1: Simple Control Flow Only

**Do not use `goto`, `setjmp`/`longjmp`, or direct/indirect recursion.**

- Use only structured control flow: `if/else`, `for`, `while`, `switch/match`, `try/catch`.
- Replace recursion with iterative alternatives (loops + explicit stacks).
- **Exception**: Tail-recursive patterns are acceptable ONLY in languages with guaranteed tail-call optimization (e.g., Scheme, Elixir). In Python, TypeScript, and C — use iteration.
- **ML Exception**: Tree-traversal utilities in decision tree/random forest inspection code may use bounded recursion with an explicit `max_depth` parameter. The recursion depth must never exceed the known tree depth.

**Why**: Acyclic call graphs are statically analyzable. Recursion introduces unbounded stack growth and makes termination proofs impossible without manual analysis.

---

### Rule 2: All Loops Must Have a Bounded Upper Limit

**Every loop must have a clear, provable termination condition and a maximum iteration count.**

- For fixed collections: iterate over the collection directly (`for item in list`, `array.forEach`).
- For dynamic/conditional loops (`while`): include a hard upper-bound counter and fail explicitly if exceeded.
- **Pattern** (Python):
  ```python
  MAX_RETRIES = 100
  for attempt in range(MAX_RETRIES):
      if done_condition():
          break
  else:
      raise RuntimeError("Loop exceeded maximum iterations")
  ```
- **Pattern** (TypeScript):
  ```typescript
  const MAX_ITER = 1000;
  let i = 0;
  while (!done && i < MAX_ITER) {
      // ... work ...
      i++;
  }
  if (i >= MAX_ITER) throw new Error("Loop exceeded maximum iterations");
  ```

#### ML/AI Modification

Training loops and agent reasoning loops get special treatment because they are intentionally long-running, but they must still be bounded:

- **Training loops**: Must define `max_epochs` upfront. Implement early stopping with a `patience` counter (e.g., stop after N epochs with no validation improvement). Never use `while True` for training.
  ```python
  # GOOD — bounded training loop with early stopping
  MAX_EPOCHS = 200
  PATIENCE = 10
  best_loss = float("inf")
  patience_counter = 0

  for epoch in range(MAX_EPOCHS):
      val_loss = train_one_epoch(model, data)
      if val_loss < best_loss:
          best_loss = val_loss
          patience_counter = 0
          save_checkpoint(model)
      else:
          patience_counter += 1
          if patience_counter >= PATIENCE:
              logger.info(f"Early stopping at epoch {epoch}")
              break
  ```
- **AI Agent loops** (ReAct, tool-use, chain-of-thought): Must define `max_steps` or `max_tool_calls`. Log each step. Fail gracefully if the bound is hit.
  ```python
  MAX_AGENT_STEPS = 15
  for step in range(MAX_AGENT_STEPS):
      action = agent.decide(state)
      if action.type == "final_answer":
          return action.result
      state = execute_tool(action)
  raise AgentLoopExhausted(f"No answer after {MAX_AGENT_STEPS} steps")
  ```
- **Data processing loops** (batch iteration, streaming): Must track total records processed and enforce a ceiling or checkpoint interval.

**Why**: Runaway training burns GPU hours and money. Runaway agent loops burn API tokens and can trigger rate limits or infinite tool-call chains. Bounding these loops is both a safety and a cost-control measure.

---

### Rule 3: No Unbounded Dynamic Memory Allocation at Runtime

**Pre-allocate data structures during initialization. Avoid unbounded growth during execution.**

- Do not append to lists/arrays/maps indefinitely inside loops or event handlers without a size cap.
- For queues, caches, and buffers: enforce a maximum size and evict or reject on overflow.
- **Pattern** (Python):
  ```python
  from collections import deque
  buffer = deque(maxlen=10_000)  # bounded
  ```
- For database result sets: always use `LIMIT` clauses or pagination.
- **Exception**: One-time data loading during application startup (e.g., reading a config file, hydrating a cache from a database) is permitted.

#### ML/AI Modification

GPU and tensor memory require explicit discipline beyond what the original rule covers:

- **Tensor cleanup**: In PyTorch, detach tensors from the computation graph before logging or storing: `loss_value = loss.item()`, not `losses.append(loss)`. Accumulated attached tensors prevent garbage collection of the entire graph.
  ```python
  # BAD — leaks GPU memory every iteration
  all_losses = []
  for batch in dataloader:
      loss = model(batch)
      all_losses.append(loss)  # holds entire computation graph

  # GOOD — detach scalar value
  all_losses = []
  for batch in dataloader:
      loss = model(batch)
      all_losses.append(loss.item())  # float, no graph reference
  ```
- **Gradient accumulation**: When using gradient accumulation for large effective batch sizes, call `optimizer.zero_grad()` at the correct interval, not every step and not never.
- **Inference context**: Always wrap inference in `torch.no_grad()` or `torch.inference_mode()` to prevent unnecessary gradient storage.
  ```python
  @torch.inference_mode()
  def predict(model, inputs):
      return model(inputs)
  ```
- **Model loading**: When loading large models (LLMs, vision transformers), use memory-mapped loading, quantization, or device placement strategies. Never load a 7B+ parameter model fully into CPU RAM first and then move to GPU.
- **DataFrame operations**: In pandas/polars, avoid chained `.copy()` of large DataFrames. Use in-place operations or method chaining that avoids intermediate copies. For datasets larger than 1GB, prefer streaming/chunked loading.

**Why**: GPU OOM crashes are the most common failure mode in ML development. A single leaked tensor reference can hold gigabytes of GPU memory hostage. Explicit memory discipline prevents silent accumulation that only manifests at scale.

---

### Rule 4: Functions Must Be Short and Single-Purpose

**No function should exceed 60 lines of logic (excluding docstrings, comments, and blank lines).**

- Each function does one thing and does it completely.
- If a function requires scrolling to read, split it.
- Name functions descriptively: `calculate_retention_rate()`, not `process()`.
- **Hard limit**: 60 lines of executable code per function/method.

#### ML/AI Modification

ML pipelines have legitimate patterns that can push against the 60-line limit. The rule applies, but with these structured exceptions:

- **Pipeline orchestration functions** (functions that call `load_data → preprocess → split → train → evaluate → log` in sequence) may reach 80 lines if each step is a separate function call and the orchestrator is purely sequential wiring. Each step itself must obey the 60-line rule.
- **Feature engineering functions** that apply many transformations to a DataFrame are permitted up to 80 lines only if each transformation is a single, readable line (e.g., `.assign(...)` chains). If any single transformation requires logic, extract it.
- **Model definition classes** (PyTorch `nn.Module`, Keras models): The `__init__` method may exceed 60 lines for models with many layers, but `forward()` must not. If `forward()` exceeds 60 lines, the model needs submodules.
- All exceptions must be flagged:
  ```python
  # RULE-4-EXCEPTION: Pipeline orchestrator — 73 lines.
  # Each step is a single function call. Splitting this further
  # would obscure the linear pipeline flow.
  ```

**Why**: Short functions remain the gold standard. The ML exceptions exist because splitting certain sequential pipeline code across files can actually reduce readability — but the bar for claiming an exception is high.

---

### Rule 5: Assertions and Validation at High Density

**Every function must validate its inputs and assert its invariants. Target a minimum of two validation checks per function.**

- Validate all function parameters at entry (type, range, nullability).
- Assert post-conditions before returning results.
- Use framework-appropriate mechanisms:
  - **Python**: `assert`, `raise ValueError/TypeError`, Pydantic validators
  - **TypeScript**: Zod schemas, type guards, explicit `if (!x) throw`
  - **SQL**: `WHERE` clauses that filter impossible states; `CHECK` constraints
- Assertions must be meaningful — `assert True` or `if (true)` violations do not count.

#### ML/AI Modification — Data Validation as Assertions

In ML code, the most critical assertions are about **data shape, type, and distribution**, not just function parameters:

- **Shape assertions**: After every tensor/array transformation, assert the expected shape.
  ```python
  def preprocess_batch(images: torch.Tensor) -> torch.Tensor:
      assert images.ndim == 4, f"Expected 4D tensor [B,C,H,W], got {images.ndim}D"
      normalized = (images - MEAN) / STD
      assert normalized.shape == images.shape, "Shape changed during normalization"
      return normalized
  ```
- **Range assertions**: Model outputs should be range-checked (e.g., probabilities between 0 and 1, regression outputs within expected bounds).
  ```python
  probs = model.predict_proba(X)
  assert (probs >= 0).all() and (probs <= 1).all(), "Probabilities out of range"
  assert np.allclose(probs.sum(axis=1), 1.0, atol=1e-5), "Probabilities don't sum to 1"
  ```
- **NaN/Inf checks**: Assert absence of NaN and Inf after every numerical transformation, especially after division, log, and softmax operations.
  ```python
  assert not torch.isnan(loss), "NaN loss detected — check learning rate or data"
  assert not torch.isinf(logits).any(), "Inf in logits — check for numerical overflow"
  ```
- **Schema validation for DataFrames**: Validate column names, dtypes, and non-null constraints at pipeline boundaries.
  ```python
  REQUIRED_COLUMNS = {"policy_id", "premium", "effective_date", "lob"}
  assert REQUIRED_COLUMNS.issubset(df.columns), f"Missing: {REQUIRED_COLUMNS - set(df.columns)}"
  assert df["premium"].dtype in (np.float64, np.float32), "Premium must be numeric"
  assert df["premium"].notna().all(), "Null premiums found"
  ```
- **Minimum of two data-level assertions** in any function that transforms data (in addition to parameter validation).

**Why**: In ML, bugs don't crash — they silently produce wrong predictions. A model trained on NaN-contaminated features or wrongly-shaped tensors will converge to garbage without ever raising an error. Data assertions are the ML equivalent of memory safety checks.

---

### Rule 6: Minimize Variable Scope

**Declare every variable at the smallest possible scope. Never reuse variables for unrelated purposes.**

- No file-level / module-level mutable globals unless absolutely required (e.g., singleton config).
- Declare loop variables inside the loop.
- In TypeScript/JavaScript: always use `const` by default; use `let` only when mutation is required; never use `var`.
- In Python: avoid module-level mutable state; pass dependencies explicitly.
- In SQL: use CTEs instead of temp tables when possible to contain scope.
- **ML addition**: Hyperparameters, model configs, and training settings must be isolated in a config object/dataclass — never scattered as loose module-level variables.
  ```python
  # BAD — scattered globals
  LEARNING_RATE = 0.001
  BATCH_SIZE = 32
  EPOCHS = 100
  DROPOUT = 0.3

  # GOOD — contained config
  @dataclass
  class TrainingConfig:
      learning_rate: float = 0.001
      batch_size: int = 32
      max_epochs: int = 100
      dropout: float = 0.3
  ```

**Why**: Smaller scope means fewer places a variable can be corrupted, and faster diagnosis when it is. For ML, scattered hyperparameters make experiment comparison impossible.

---

### Rule 7: Check Every Return Value and Handle Every Error

**Never ignore return values. Never swallow exceptions silently.**

- Every function call that can fail must have its error/return value checked.
- `try/except` blocks must catch specific exceptions — never bare `except:` or `catch (e) {}` that silently continues.
- If a return value is intentionally ignored, document why with an explicit comment.
- **Forbidden patterns**:
  ```python
  # BAD — silent swallow
  try:
      risky_operation()
  except:
      pass
  ```
- **Required patterns**:
  ```python
  # GOOD — specific handling
  try:
      response = requests.post(url, data=payload)
      response.raise_for_status()
  except requests.HTTPError as e:
      logger.error(f"API call failed: {e}")
      raise
  ```
- **ML addition**: API calls to LLM providers (Anthropic, OpenAI, etc.) must handle rate limits, token limits, and timeout errors explicitly with retry logic and backoff.
  ```python
  # GOOD — LLM API call with structured error handling
  from tenacity import retry, stop_after_attempt, wait_exponential

  @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=30))
  def call_claude(prompt: str) -> str:
      try:
          response = client.messages.create(model="claude-sonnet-4-20250514", ...)
          return response.content[0].text
      except anthropic.RateLimitError:
          logger.warning("Rate limited, retrying...")
          raise  # let tenacity handle retry
      except anthropic.APIError as e:
          logger.error(f"Anthropic API error: {e}")
          raise
  ```

**Why**: Unchecked errors are the #1 source of silent data corruption. In ML/AI systems, a silently failed API call or data load can produce a model trained on partial data without anyone noticing.

---

### Rule 8: Minimize Metaprogramming and Code Generation Tricks

**Limit use of macros, decorators, dynamic code evaluation, and meta-classes to simple, well-understood patterns.**

- **Forbidden**: `eval()`, `exec()`, dynamic `import` from user input, runtime class generation from strings.
- **Permitted with caution**: Simple decorators (`@app.route`, `@retry`), straightforward generics, standard ORM metaclasses.
- Configuration should be data (JSON, YAML, env vars), not executable code.
- In TypeScript: avoid complex mapped/conditional types that obscure intent. Prefer explicit interfaces.
- In Python: avoid `__getattr__` magic and dynamic `setattr` chains — prefer explicit attributes.

#### ML/AI Modification — Approved ML Framework Patterns

ML frameworks use decorators and dynamic patterns extensively by design. These specific patterns are permitted:

- **Approved decorators**: `@torch.no_grad()`, `@torch.inference_mode()`, `@tf.function`, `@jit`, `@pytest.mark.parametrize`, `@app.tool()` (MCP), `@retry`
- **Approved dynamic patterns**: HuggingFace `AutoModel.from_pretrained()`, `model.to(device)`, config-driven model building from YAML/JSON (e.g., Hydra configs)
- **Still forbidden**: Building model architectures by `eval()`-ing config strings, dynamic layer creation from unvalidated user input, monkey-patching model methods at runtime

**Why**: Metaprogramming defeats static analysis. The ML exceptions exist because frameworks like PyTorch and TensorFlow have designed their APIs around these patterns — fighting the framework creates worse code than using the approved idioms.

---

### Rule 9: Restrict Indirection and Pointer-Like Patterns

**Limit levels of indirection. Keep data access direct and traceable.**

- No more than one level of indirection in data access chains. Avoid `obj.a.b.c.d` — extract intermediate values with descriptive names.
- Avoid deeply nested callbacks or promise chains — use `async/await`.
- In TypeScript: avoid `any` type — it is the equivalent of a void pointer. Use `unknown` with type guards.
- In Python: avoid excessive `**kwargs` forwarding through multiple layers — be explicit about parameters.
- **Pattern** — flatten deep access:
  ```python
  # BAD
  city = response.data.results[0].address.city

  # GOOD
  first_result = response.data.results[0]
  address = first_result.address
  city = address.city
  ```
- **ML addition**: Config-driven ML pipelines (Hydra, OmegaConf) can create deep nested access like `cfg.model.encoder.attention.num_heads`. Extract into local variables at the function boundary:
  ```python
  # GOOD — extract at entry
  def build_attention(cfg: DictConfig):
      attn_cfg = cfg.model.encoder.attention
      num_heads = attn_cfg.num_heads
      hidden_dim = attn_cfg.hidden_dim
      # ... use flat variables from here
  ```

**Why**: Deep indirection chains are fragile and obscure data flow for both humans and static analyzers.

---

### Rule 10: Zero Warnings, Maximum Static Analysis

**All code must pass linting and type-checking with zero warnings at the strictest available setting.**

- **Python**: `ruff` (all rules enabled) + `mypy --strict` (or `pyright` strict mode). Zero warnings.
- **TypeScript**: `"strict": true` in `tsconfig.json` + ESLint with recommended rules. Zero warnings.
- **SQL**: Validate with `sqlfluff` or equivalent. No `SELECT *` in production queries.
- **React/JSX**: ESLint + `react-hooks/exhaustive-deps` enforced.
- **General**: If a linter warning seems like a false positive, rewrite the code to eliminate the warning — do not suppress it without a documented justification.
- Run formatters (`black`, `prettier`, `sqlfluff fix`) before finalizing any output.
- **ML addition**: For Jupyter notebooks, use `nbqa` to run ruff/mypy on notebook cells. Notebooks in production pipelines must be converted to `.py` scripts — no `.ipynb` in production.

**Why**: Static analysis catches entire categories of bugs before runtime. Zero-warning policies eliminate the "warning fatigue" that causes real issues to be ignored.

---

## PART II — ML/AI-SPECIFIC RULES (New)

These rules address failure modes unique to machine learning, AI agent development, and data-intensive systems that the original NASA/JPL rules could not anticipate.

---

### Rule 11: Reproducibility by Default

**Every ML experiment must be reproducible from a single command. All sources of randomness must be explicitly seeded and logged.**

- **Seed everything**: Set and log random seeds for Python (`random`), NumPy (`np.random`), PyTorch (`torch.manual_seed`, `torch.cuda.manual_seed_all`), and TensorFlow (`tf.random.set_seed`) at the start of every script.
  ```python
  import random, numpy as np, torch

  def set_seed(seed: int = 42) -> None:
      random.seed(seed)
      np.random.seed(seed)
      torch.manual_seed(seed)
      torch.cuda.manual_seed_all(seed)
      torch.backends.cudnn.deterministic = True
      torch.backends.cudnn.benchmark = False
  ```
- **Log the full config**: Every training run must log its complete configuration (hyperparameters, data paths, model architecture, seed, git commit hash) to a tracking system (MLflow, W&B, or at minimum a JSON file alongside the checkpoint).
  ```python
  run_metadata = {
      "seed": SEED,
      "git_sha": subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip(),
      "config": asdict(training_config),
      "python_version": sys.version,
      "torch_version": torch.__version__,
      "timestamp": datetime.utcnow().isoformat(),
  }
  with open(checkpoint_dir / "run_metadata.json", "w") as f:
      json.dump(run_metadata, f, indent=2)
  ```
- **Environment pinning**: Generate `requirements.txt` with pinned versions (`pip freeze`) or use `pyproject.toml` with exact pins. For critical projects, use Docker with a locked base image.
- **Data versioning**: Reference datasets by hash, version tag, or immutable URI — never by mutable file paths that can change between runs. Use DVC, lakeFS, or at minimum store checksums.
  ```python
  import hashlib
  data_hash = hashlib.sha256(Path("training_data.parquet").read_bytes()).hexdigest()[:12]
  logger.info(f"Training data checksum: {data_hash}")
  ```

**Why**: ML research has a well-documented reproducibility crisis. Without explicit seeding, environment pinning, and data versioning, re-running the same code produces different results — making debugging, comparison, and auditing impossible. As industry research consistently shows, teams that cannot reproduce results cannot trust their models in production.

---

### Rule 12: Data-Code Boundary Discipline (No Data Leakage)

**Training data and evaluation data must be strictly separated. No information from the test set may influence any training decision.**

- **Split first, transform later**: Always split raw data into train/validation/test before any preprocessing, feature engineering, or normalization. Fit scalers, encoders, and imputers on the training set only, then transform validation/test sets.
  ```python
  # BAD — leaks test distribution into training
  scaler = StandardScaler()
  X_scaled = scaler.fit_transform(X_all)  # fits on ALL data including test
  X_train, X_test = train_test_split(X_scaled)

  # GOOD — strict separation
  X_train, X_test = train_test_split(X_raw)
  scaler = StandardScaler()
  X_train_scaled = scaler.fit_transform(X_train)  # fit on train only
  X_test_scaled = scaler.transform(X_test)         # transform only
  ```
- **Time-series discipline**: For temporal data, never use future data to predict the past. Use expanding-window or walk-forward validation — never random shuffled splits.
  ```python
  # BAD for time-series
  train_test_split(df, shuffle=True)  # randomly mixes future into past

  # GOOD for time-series
  cutoff = df["date"].quantile(0.8)
  train = df[df["date"] <= cutoff]
  test = df[df["date"] > cutoff]
  ```
- **Feature leakage checks**: Never include target-derived features (e.g., "claim_amount" when predicting "will_claim"), future-leaked features (e.g., "cancellation_date" when predicting churn), or unique identifiers that correlate with the target.
- **Cross-validation**: When using k-fold CV, ensure preprocessing is re-fit inside each fold — not once on the whole dataset.
- **Assertion**: After any split, assert zero overlap:
  ```python
  assert len(set(train_ids) & set(test_ids)) == 0, "Data leakage: overlapping IDs"
  ```

**Why**: Data leakage is the single most common and most damaging bug in ML. It produces models that look excellent in evaluation but fail completely in production. Unlike code bugs, leakage doesn't crash — it produces silently inflated metrics that only surface after deployment.

---

### Rule 13: Experiment Tracking and Model Lineage

**Every model artifact must be traceable to the exact code, data, config, and environment that produced it.**

- **Minimum logged metadata per training run**:
  - Git commit hash (or code snapshot)
  - Full hyperparameter config
  - Dataset identifier + checksum/version
  - Training metrics per epoch (loss, accuracy, etc.)
  - Evaluation metrics on held-out test set
  - Wall-clock training time and hardware info (GPU type, memory)
  - Final model checkpoint path
- **Model registry**: Production models must be registered with a version number, linked to their training run, and tagged with deployment status (staging/production/retired).
- **No unnamed checkpoints**: Never save a model as `model.pt` or `best_model.pkl` without a run ID. Use structured naming:
  ```
  checkpoints/
    run_2025-03-17_abc123/
      config.json
      model_epoch_042.pt
      metrics.json
      run_metadata.json
  ```
- **Comparison discipline**: Before deploying a new model, log a side-by-side comparison of the new model vs. the current production model on the same evaluation set.

**Why**: Without lineage tracking, production incidents become undiagnosable. When a model starts producing bad predictions, you need to answer: "What data was it trained on? What code version? What hyperparameters?" If you can't answer these in 5 minutes, the tracking system has failed.

---

### Rule 14: Security, Secrets, and Sensitive Data Hygiene

**No secrets, credentials, PII, or sensitive data may exist in source code, notebooks, logs, or model artifacts.**

- **Secrets**:
  - Never hardcode API keys, database passwords, tokens, or credentials in code. Use environment variables, `.env` files (gitignored), or a secrets manager (AWS Secrets Manager, GCP Secret Manager, HashiCorp Vault).
  - Scan for leaked secrets in CI with tools like `trufflehog`, `gitleaks`, or `detect-secrets`.
  ```python
  # BAD
  client = anthropic.Anthropic(api_key="sk-ant-api03-...")

  # GOOD
  client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env
  ```
- **PII in training data and logs**:
  - Never log full customer names, SSNs, policy numbers, or medical records in training logs, metrics outputs, or error messages.
  - If training on data containing PII, document the data handling policy and ensure access controls.
  - Mask PII in error messages: `logger.error(f"Failed for policy {policy_id[:4]}****")`.
- **Model artifacts**:
  - Embedding layers and attention weights can memorize training data. For models trained on sensitive data, evaluate memorization risk before deployment.
  - Never ship model checkpoints that contain training data samples in their metadata.
- **AI Agent safety**:
  - Agents that execute tools (file access, web requests, database queries) must have explicit permission boundaries. Never give an agent unrestricted filesystem or database write access.
  - Validate and sanitize all user inputs before passing them to LLM prompts to prevent prompt injection.
  ```python
  # GOOD — constrained agent tool access
  ALLOWED_TABLES = {"policies", "claims", "producers"}
  def query_tool(table: str, query: str) -> str:
      if table not in ALLOWED_TABLES:
          raise PermissionError(f"Access denied for table: {table}")
      # ... execute validated query
  ```

**Why**: A single leaked API key can cost thousands of dollars in minutes. PII in logs creates compliance liability (HIPAA, GDPR, state privacy laws). AI agents with unrestricted access are a security incident waiting to happen. Security discipline must be baked into the code, not bolted on.

---

### Rule 15: Dependency Pinning and Environment Determinism

**Every project must have a fully pinned, reproducible dependency specification. "It works on my machine" is not acceptable.**

- **Pin exact versions** for all direct and transitive dependencies:
  ```
  # BAD
  torch>=2.0
  pandas

  # GOOD
  torch==2.4.1
  pandas==2.2.3
  numpy==1.26.4
  ```
- **Lock files**: Use `pip-compile` (pip-tools), `poetry.lock`, `uv.lock`, `package-lock.json`, or `yarn.lock`. Commit lock files to version control.
- **Python version**: Specify the exact Python version in `pyproject.toml`, `.python-version`, or Dockerfile.
- **CUDA/GPU dependencies**: For ML projects, pin CUDA toolkit version, cuDNN version, and GPU driver compatibility in documentation and Docker images.
  ```dockerfile
  FROM nvidia/cuda:12.4.1-runtime-ubuntu22.04
  # Pin everything from the base image up
  ```
- **No floating installs in CI/CD**: CI pipelines must install from lock files, never from unconstrained `requirements.txt`.
- **Periodic updates**: Pinned dependencies must be reviewed and updated at least monthly. Use `dependabot`, `renovate`, or manual audits to catch security vulnerabilities in pinned versions.

**Why**: A single unpinned dependency can silently change behavior between runs. NumPy 1.x to 2.x changed default dtypes; PyTorch point releases have altered numerical behavior. In ML, even small floating-point differences cascade through training to produce different models. Reproducibility (Rule 11) is impossible without environment determinism.

---

## Summary Reference Card

| # | Rule | Key Check | ML/AI Impact |
|---|------|-----------|--------------|
| 1 | Simple control flow | No goto, no recursion | Bounded tree traversal exception |
| 2 | Bounded loops | Every loop has a max iteration count | Training loops need early stopping; agent loops need max_steps |
| 3 | No unbounded allocation | All buffers/collections are size-capped | GPU tensor cleanup, `torch.no_grad()`, detach before logging |
| 4 | Short functions | ≤ 60 lines of logic per function | Pipeline orchestrators up to 80 lines with justification |
| 5 | High assertion density | ≥ 2 validations per function | Shape, range, NaN/Inf, and schema assertions on all data transforms |
| 6 | Minimal scope | `const` by default, no mutable globals | Hyperparameters in config dataclass, not scattered globals |
| 7 | Check every return value | No silent exception swallowing | LLM API calls need retry + backoff for rate limits |
| 8 | No metaprogramming tricks | No `eval`, no dynamic code gen | Approved: `@torch.no_grad`, `AutoModel.from_pretrained`, Hydra configs |
| 9 | Limit indirection | Max 1 level deep, no `any` types | Extract nested config values at function boundary |
| 10 | Zero warnings | Strictest linting + type checking, 0 warnings | `nbqa` for notebooks; no `.ipynb` in production |
| 11 | **Reproducibility by default** | Seed all randomness, log full config | Pin seeds, hash data, snapshot environment |
| 12 | **No data leakage** | Split first, transform later | Fit on train only; time-series walk-forward; assert zero overlap |
| 13 | **Experiment tracking** | Every model traceable to code+data+config | Structured checkpoints, model registry, comparison logs |
| 14 | **Security & secrets hygiene** | No hardcoded secrets, no PII in logs | Agent permission boundaries, prompt injection prevention |
| 15 | **Dependency pinning** | Exact versions, lock files, pinned CUDA | Lock files committed; no floating installs in CI |

---

## Enforcement Note

When generating code, Claude must self-check against all 15 rules before presenting the final output. If a rule is intentionally violated, Claude must flag the violation explicitly with a comment in the code explaining the rationale and the tradeoff.

```
# RULE-4-EXCEPTION: Pipeline orchestrator — 73 lines.
# Each step is a single function call. Splitting this further
# would obscure the linear pipeline flow.
```

```
# RULE-2-ML: Training loop uses max_epochs=500 with early stopping (patience=20).
# Bounded by both epoch count and convergence criterion.
```

For the 5 new ML/AI rules (11–15), Claude must include relevant boilerplate when generating ML code:
- Rule 11: Include `set_seed()` and metadata logging in any training script.
- Rule 12: Assert train/test non-overlap after any data split.
- Rule 13: Generate structured checkpoint naming in any model-saving code.
- Rule 14: Use `os.environ` for API keys in any client initialization code.
- Rule 15: Generate pinned dependency specifications when creating new projects.

---

---

## About the Author

**Pramod Misra** is the Director of Data Analytics at Snellings Walters Insurance in Atlanta, GA, where he builds production AI and analytics systems for the insurance industry. He serves on the agency's internal AI executive committee and has deep hands-on expertise with Applied Epic AMS, Google BigQuery, Power BI, and the Anthropic Claude ecosystem. He is affiliated with the Georgia Institute of Technology and was recognized as a runner-up in the ACORD Student Challenge 2025 for AI-driven insurance underwriting. He is an active participant in the AI/ML hackathon community and has spoken on agentic AI at the Kinfos conference alongside executives from First Citizens Bank, UBS, and JPMorgan Chase.

---

*Core rules adapted from "The Power of Ten — Rules for Developing Safety Critical Code" by Gerard J. Holzmann, NASA/JPL Laboratory for Reliable Software. ML/AI extensions informed by MLOps reproducibility research, OWASP AI security guidelines, and production ML engineering practices as of 2026.*

*© 2026 Pramod Misra. This document may be freely shared with attribution.*
