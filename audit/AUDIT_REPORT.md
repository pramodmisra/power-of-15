# Code Audit Report: 15 Rules vs. Real-World Code

**Audited by**: Pramod Misra, Director of Data Analytics, Snellings Walters Insurance | Georgia Tech
**Framework**: The Power of 15 — Rules for Developing Safety-Critical AI Code
**Date**: March 2026

---

## Executive Summary

I audited publicly available code across three categories — **InsurTech ML projects**, **popular ML frameworks/tutorials**, and **AI agent frameworks** — against my 15-rule coding standard adapted from NASA/JPL's Power of Ten rules. The results are sobering: the average project violated **9 out of 15 rules**. The most dangerous violations were silent, producing code that runs without errors but generates untrustworthy results.

### Violation Heat Map

| Rule | InsurTech ML Repos | ML Tutorials/Examples | AI Agent Code |
|------|:------------------:|:--------------------:|:-------------:|
| 1. Simple control flow | PASS | PASS | PASS |
| 2. Bounded loops | PASS | WARN | **FAIL** |
| 3. No unbounded allocation | WARN | **FAIL** | **FAIL** |
| 4. Short functions | **FAIL** | **FAIL** | WARN |
| 5. Assertions/validation | **FAIL** | **FAIL** | **FAIL** |
| 6. Minimal scope | **FAIL** | **FAIL** | WARN |
| 7. Check every return value | **FAIL** | **FAIL** | **FAIL** |
| 8. No metaprogramming | PASS | PASS | PASS |
| 9. Limit indirection | WARN | WARN | WARN |
| 10. Zero warnings/linting | **FAIL** | **FAIL** | **FAIL** |
| 11. Reproducibility | **FAIL** | **FAIL** | N/A |
| 12. No data leakage | **FAIL** | **FAIL** | N/A |
| 13. Experiment tracking | **FAIL** | **FAIL** | N/A |
| 14. Security/secrets | **FAIL** | WARN | **FAIL** |
| 15. Dependency pinning | **FAIL** | **FAIL** | **FAIL** |

**FAIL** = Clear violation found | **WARN** = Partial compliance | **PASS** = Compliant

---

## Category 1: InsurTech ML Projects

**Repos audited**: Insurance-Claim-Prediction (sharmaroshan), Predicting-Insurance-Claim (Muhammad-Sheraz-ds), Auto-Claim-Prediction (GirrajMaheshwari), Vehicle-Insurance-Claim-Prediction (Sarah-2510), Denial-Reason-Prediction-Model (MacHu-GWU)

### Critical Findings

**Rule 12 VIOLATED — Data Leakage (found in 4 of 5 repos)**

The most dangerous and most common pattern. Multiple insurance ML repos fit scalers and encoders on the entire dataset before splitting:

```python
# ACTUAL PATTERN FOUND — fits on ALL data including test
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_all)    # LEAKAGE: test distribution leaks into training
X_train, X_test = train_test_split(X_scaled, test_size=0.2)
```

This means reported accuracy metrics are inflated. A model claiming 95% accuracy on insurance claim prediction may drop to 78% on genuinely unseen data. In an insurance context, this directly translates to mispriced premiums and underestimated reserves.

**Rule 11 VIOLATED — No Reproducibility (found in 5 of 5 repos)**

Zero repos set random seeds. Zero repos log the environment. Zero repos version their training data.

```python
# ACTUAL PATTERN — no seed set anywhere
X_train, X_test = train_test_split(X, y, test_size=0.2)  # Different split every run
model = RandomForestClassifier()                           # Different results every run
model.fit(X_train, y_train)
print(f"Accuracy: {model.score(X_test, y_test)}")         # Non-reproducible number
```

The reported accuracy number in the README is a snapshot of one lucky (or unlucky) run. No one — including the author — can reproduce it.

**Rule 14 VIOLATED — Hardcoded Secrets (found in 2 of 5 repos)**

```python
# ACTUAL PATTERN FOUND in Streamlit insurance apps
os.environ["OPENAI_API_KEY"] = "sk-xxxxxxxx"  # Hardcoded in source
```

One repo had an actual API key committed to version control (since revoked by GitHub's secret scanning). Streamlit insurance prediction apps that ship with `insurance.pkl` model files have no documentation of what data trained them — a model lineage gap (Rule 13).

**Rule 5 VIOLATED — Zero Data Validation (found in 5 of 5 repos)**

No repo validates input data shape, type, range, or null counts before training. No assertions on model output ranges.

```python
# ACTUAL PATTERN — no validation anywhere
df = pd.read_csv("insurance.csv")
X = df.drop("insuranceclaim", axis=1)
y = df["insuranceclaim"]
# What if a column is missing? What if BMI is negative? What if nulls exist?
# Silence. The code just runs.
```

**Rule 15 VIOLATED — No Dependency Pinning (found in 4 of 5 repos)**

Most repos either have no `requirements.txt` at all or list unpinned dependencies:

```
pandas
sklearn
matplotlib
numpy
```

One repo specifies `Python 2.7` (end-of-life since January 2020).

---

## Category 2: Popular ML Tutorials & Examples

**Sources audited**: Official PyTorch tutorials (pytorch.org/tutorials), HuggingFace example scripts, scikit-learn documentation examples, top Kaggle notebooks

### Critical Findings

**Rule 3 VIOLATED — GPU Memory Leaks (PyTorch tutorials)**

Official PyTorch tutorials sometimes demonstrate patterns that leak GPU memory in production:

```python
# PATTERN FROM TUTORIALS — accumulates attached tensors
losses = []
for batch in dataloader:
    loss = criterion(model(inputs), targets)
    losses.append(loss)          # Holds entire computation graph in memory
    loss.backward()
```

The correct pattern (`losses.append(loss.item())`) is mentioned in advanced docs but not in beginner tutorials — where most people learn the pattern they'll carry forward.

**Rule 2 VIOLATED — Training Loops Without Early Stopping**

Many tutorial training loops use a fixed epoch count with no convergence check:

```python
# COMMON TUTORIAL PATTERN
for epoch in range(100):
    for batch in train_loader:
        # train...
    print(f"Epoch {epoch}: loss = {running_loss}")
# No early stopping, no validation monitoring, no checkpoint of best model
```

The loop terminates (it's bounded by epoch count), but it burns compute after convergence and has no mechanism to detect divergence. This gets a WARN rather than FAIL because it technically terminates.

**Rule 12 VIOLATED — Leakage in scikit-learn Examples**

Even scikit-learn's own documentation has historically demonstrated fit-before-split patterns for transformers, though this has improved in recent versions. Third-party tutorials overwhelmingly still show the dangerous pattern.

**Rule 13 VIOLATED — No Experiment Tracking**

Tutorial code saves models as `model.pt`, `best_model.pkl`, or `checkpoint.pth` with zero metadata. No config logging, no git hash, no data version.

---

## Category 3: AI Agent Frameworks

**Sources audited**: LangChain examples, CrewAI quickstarts, AutoGen samples, documented GitHub issues

### Critical Findings

**Rule 2 VIOLATED — Agent Loops Without Bounds**

LangChain's `AgentExecutor` defaults to `max_iterations=15`, but many examples and user implementations override this or don't set it at all. Multiple filed GitHub issues (#6025, #8493, #12157, #2495, #3429) document agents getting stuck in infinite reasoning loops, burning API tokens.

```python
# PATTERN FROM LANGCHAIN ISSUES — agent loops indefinitely
agent_chain = initialize_agent(
    tools, llm,
    agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
    verbose=True,
    memory=memory
    # No max_iterations set — relies on framework default
)
while(True):                    # OUTER loop has NO exit condition
    user_message = input("User: ")
    if user_message == 'exit':  # Only exits on exact string match
        break
    response = agent_chain(user_message)
```

The `create_json_agent` function was documented as silently ignoring `max_iterations` — the parameter was accepted but not passed through to the executor (GitHub issue #3429).

**Rule 14 VIOLATED — API Keys in Agent Code**

Agent example code routinely hardcodes API keys:

```python
# ACTUAL PATTERN FROM LANGCHAIN ISSUES
os.environ["OPENAI_API_KEY"] = "sk-xxxxxxxx"
os.environ["AZURE_OPENAI_API_KEY"] = AZURE_OPENAI_API_KEY  # Module-level constant
```

Agent frameworks that use `PythonREPLTool` give the LLM unrestricted code execution — a severe security boundary violation (Rule 14). Any prompt injection can execute arbitrary Python on the host machine.

**Rule 7 VIOLATED — Error Handling in Tool Calls**

Agent tool calls frequently lack proper error handling. When a tool returns an unexpected format, the agent retries the same failing action until hitting the iteration limit:

```
> Agent stopped due to iteration limit or time limit.
```

This is the most commonly reported error in LangChain's GitHub issues. The root cause: tool errors aren't caught and translated into informative feedback for the agent's next reasoning step.

**Rule 5 VIOLATED — No Input Validation on Tool Parameters**

Agent tools typically accept string inputs without validation. A misconfigured agent can pass SQL injection through a database tool, malformed JSON to an API tool, or path traversal strings to a file tool.

---

## Top 5 Most Dangerous Violations (Ranked by Real-World Impact)

| Rank | Rule | Violation | Real-World Impact |
|------|------|-----------|-------------------|
| 1 | Rule 12 | Data leakage (fit before split) | Inflated model metrics → mispriced insurance premiums, failed production models |
| 2 | Rule 14 | Hardcoded API keys + unrestricted agent tools | Financial exposure, compliance violation (HIPAA/GDPR), prompt injection attacks |
| 3 | Rule 11 | No reproducibility (no seeds, no versioning) | Cannot audit, debug, or validate any reported result |
| 4 | Rule 2 | Agent loops without bounds | Runaway API costs ($100s+ per incident), stuck production systems |
| 5 | Rule 7 | Silent error swallowing | Partial data training, corrupt model artifacts, cascading failures |

---

## Conclusion

The current state of publicly available insurance ML code and AI agent implementations is not production-ready by any rigorous standard. The violations are not obscure edge cases — they are fundamental gaps in data discipline, reproducibility, security, and error handling that directly impact the trustworthiness of every model built with these patterns.

The 15 rules are not theoretical. They catch the exact violations that are shipping in real code today.

---

*This audit was conducted as part of "The Power of 15" coding standard publication by Pramod Misra.*
