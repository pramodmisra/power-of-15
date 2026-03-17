# The Power of 15

### NASA/JPL's Coding Rules, Rewritten for the AI Era

[![License: MIT](https://img.shields.io/badge/License-MIT-teal.svg)](LICENSE)
[![Claude Code Skill](https://img.shields.io/badge/Claude_Code-Skill_Available-14B8A6)](skill/power-of-15.skill)
[![Rules](https://img.shields.io/badge/Rules-15-0F172A)](docs/CODING_RULES.md)

---

In 2006, Gerard Holzmann at NASA's Jet Propulsion Laboratory published **"The Power of Ten"** — 10 strict coding rules for safety-critical software. Code for spacecraft, airplanes, and nuclear systems.

**The Power of 15** adapts those rules for the AI era: machine learning pipelines, LLM agent loops, GPU memory management, and modern multi-language development. It adds 5 new rules for failure modes NASA never needed to consider — data leakage, reproducibility, experiment tracking, AI security, and dependency determinism.

Then it was **tested against real code**. The [audit report](audit/AUDIT_REPORT.md) documents violations found across InsurTech ML repos, popular framework tutorials, and AI agent implementations.

---

## Quick Install

### Claude Code (Recommended)

Download and install the skill — it auto-triggers on every code generation task:

```bash
# Download the skill file
curl -LO https://github.com/pramodmisra/power-of-15/raw/main/skill/power-of-15.skill

# Install in Claude Code (drag into project or place in skills directory)
```

Once installed, Claude Code will automatically enforce all 15 rules whenever it writes code in any language.

### CLAUDE.md (Per-Repository)

Copy `docs/CODING_RULES.md` into your project root, then add to your `CLAUDE.md`:

```markdown
import: CODING_RULES.md
```

### Claude.ai Project

See [docs/CLAUDE_PROJECT_INSTRUCTIONS.md](docs/CLAUDE_PROJECT_INSTRUCTIONS.md) for ready-to-paste Project custom instructions.

### Manual Reference

Read the full rules: **[docs/CODING_RULES.md](docs/CODING_RULES.md)**

---

## The 15 Rules at a Glance

### Part I — Core Rules (NASA/JPL Adapted)

| # | Rule | AI/ML Modification |
|---|------|--------------------||
| 1 | Simple control flow | Bounded tree traversal exception for ML |
| 2 | Bounded loops | Training → early stopping; Agents → max_steps |
| 3 | No unbounded allocation | GPU tensor cleanup, `torch.no_grad()` |
| 4 | Short functions (≤60 lines) | Pipeline orchestrators up to 80 with justification |
| 5 | High assertion density | Shape, NaN/Inf, schema checks on data transforms |
| 6 | Minimal variable scope | Hyperparameters in config dataclass |
| 7 | Check every return value | LLM API retry + backoff |
| 8 | No metaprogramming tricks | Approved: `@torch.no_grad`, Hydra, `AutoModel` |
| 9 | Limit indirection | No `any` types; extract nested configs |
| 10 | Zero linter warnings | `nbqa` for notebooks; no `.ipynb` in prod |

### Part II — New Rules for the AI Era

| # | Rule | Why NASA Didn't Need It |
|---|------|------------------------|
| 11 | Reproducibility by default | Seed randomness, log configs, version data |
| 12 | No data leakage | Split first, transform later — always |
| 13 | Experiment tracking | Every model → code + data + config lineage |
| 14 | Security & secrets hygiene | No hardcoded keys, bounded agent permissions |
| 15 | Dependency pinning | Exact versions, lock files, pinned CUDA |

---

## Audit Results

The rules were validated against real publicly available code. Key findings:

| Category | Repos Audited | Avg Rules Violated |
|----------|:------------:|:-----------------:|
| InsurTech ML Projects | 5 | 11 / 15 |
| ML Framework Tutorials | 4 sources | 8 / 15 |
| AI Agent Frameworks | 3 sources | 7 / 15 |

**Most dangerous finding**: 4 out of 5 insurance ML repos had **data leakage** — fitting scalers on the full dataset before train/test split. Reported accuracy metrics were inflated and non-reproducible.

Full report: **[audit/AUDIT_REPORT.md](audit/AUDIT_REPORT.md)**

---

## Repository Structure

```
power-of-15/
├── README.md                           ← You are here
├── LICENSE                             ← MIT License
├── skill/
│   └── power-of-15.skill              ← Claude Code installable skill
├── docs/
│   ├── CODING_RULES.md                ← Full 15 rules with code examples
│   ├── CLAUDE_PROJECT_INSTRUCTIONS.md ← Ready-to-paste Claude.ai Project setup
│   └── ORIGINAL_NASA_P10.md           ← Reference: Holzmann's original paper notes
├── audit/
│   └── AUDIT_REPORT.md                ← Findings from real code audits
├── social/
│   ├── SOCIAL_CONTENT.md              ← LinkedIn article + Twitter thread
│   └── Power_of_15_Carousel.pptx      ← LinkedIn carousel (10 slides)
└── examples/
    ├── python-ml/
    │   └── compliant_training.py       ← Training script following all 15 rules
    ├── typescript-agent/
    │   └── compliant_agent.ts          ← Bounded agent loop with error handling
    └── sql-analytics/
        └── compliant_query.sql         ← BigQuery analytics following Rules 5-7, 10
```

---

## Examples

### Python ML — Compliant Training Script

```python
# Rule 11: Seed everything
set_seed(42)

# Rule 12: Split FIRST, transform LATER
X_train, X_test = train_test_split(X_raw, test_size=0.2, random_state=42)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)   # fit on TRAIN only
X_test_scaled = scaler.transform(X_test)          # transform only

# Rule 12: Assert non-overlap
assert len(set(train_idx) & set(test_idx)) == 0, "Data leakage!"

# Rule 2: Bounded training with early stopping
MAX_EPOCHS = 200
PATIENCE = 10
for epoch in range(MAX_EPOCHS):
    val_loss = train_one_epoch(model, train_loader)
    if val_loss < best_loss:
        best_loss = val_loss
        patience_counter = 0
        save_checkpoint(model, epoch, config)  # Rule 13
    else:
        patience_counter += 1
        if patience_counter >= PATIENCE:
            break
```

### TypeScript Agent — Bounded Loop

```typescript
// Rule 2: Agent loop with hard bound
const MAX_STEPS = 15;
for (let step = 0; step < MAX_STEPS; step++) {
  const action = await agent.decide(state);
  if (action.type === "final_answer") return action.result;

  // Rule 7: Check tool return values
  const result = await executeTool(action);
  if (!result.success) {
    logger.error(`Tool ${action.tool} failed: ${result.error}`);
    state = { ...state, lastError: result.error };
    continue;
  }
  state = updateState(state, result);
}
throw new AgentLoopExhausted(`No answer after ${MAX_STEPS} steps`);
```

See the [examples/](examples/) directory for complete, runnable files.

---

## Contributing

Found a rule that needs refinement? Have a language-specific pattern to add? PRs welcome.

1. Fork the repo
2. Create a branch (`git checkout -b improve-rule-5`)
3. Add your improvement with a code example
4. Submit a PR with a brief rationale

---

## Citation

If you reference The Power of 15 in your work:

```
Misra, P. (2026). "The Power of 15 — Rules for Developing Safety-Critical AI Code."
Adapted from Holzmann, G.J. (2006). "The Power of Ten — Rules for Developing
Safety Critical Code." NASA/JPL Laboratory for Reliable Software.
```

---

## Author

**Pramod Misra**
Director of Data Analytics | Snellings Walters Insurance, Atlanta, GA
Georgia Institute of Technology

- Built production AI systems for insurance: carrier accounting automation, claims processing agents, retention analytics
- Runner-up, ACORD Student Challenge 2025 (AI agent for pet insurance underwriting)
- AI panelist, Kinfos Conference Atlanta (alongside First Citizens Bank, UBS, JPMorgan Chase)
- Active AI/ML hackathon competitor (Nova Hackathon, Elasticsearch Agent Builder)

---

## License

MIT — freely use, modify, and distribute with attribution.

---

*"The rules act like the seat-belt in your car: initially they are perhaps a little uncomfortable, but after a while their use becomes second-nature and not using them becomes unimaginable." — Gerard J. Holzmann, NASA/JPL*
