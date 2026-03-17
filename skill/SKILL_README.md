# Power of 15 Skill for Claude Code

## Installation

The skill file (`power-of-15.skill`) can be installed in Claude Code to automatically enforce all 15 rules during code generation.

### Manual Setup (Alternative)

If you don't have the .skill file, you can achieve the same effect by:

1. Copy `docs/CODING_RULES.md` to your project root
2. Add this line to your `CLAUDE.md`:

```markdown
import: CODING_RULES.md
```

This will ensure Claude Code follows all 15 rules when generating code in your project.

## What the Skill Does

When installed, the skill:
- Triggers on every code generation task
- Self-checks generated code against all 15 rules
- Automatically adds required ML boilerplate (seeds, assertions, structured checkpoints)
- Flags any intentional rule exceptions with `# RULE-N-EXCEPTION` comments

## Building the Skill

To create a `.skill` file:

1. Package `SKILL.md` (the rule definitions) into a zip archive
2. Rename from `.zip` to `.skill`
3. Place in your Claude Code skills directory

The skill content is identical to `docs/CODING_RULES.md`.
