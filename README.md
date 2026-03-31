# AI-native development

Guides and best practices for building software with LLMs, from the team at [Codelitt](https://codelitt.com).

These aren't theoretical. They come from shipping production software where Claude Code, codemode-x, and other LLM tools do a significant share of the implementation work. When something wastes tokens, breaks the feedback loop, or confuses the model, we write it down.

## Guides

| Guide | What it covers |
|-------|---------------|
| [AI-native architecture](guides/ai-native-architecture.md) | 9 principles for structuring codebases so LLMs can work in them effectively. Contracts, error handling, idempotency, file structure, and more. |
| [Claude Code workflows](guides/claude-code-workflows.md) | Practical setup and habits: planning mode, context-mode plugin, /documents/ folder, CLAUDE.md wiring, subagents, task tracking, and workflow orchestration rules. |
| [The AI quality paradox](guides/ai-quality-paradox.md) | Why AI-assisted development needs more QA, not less. The math behind rework spirals, the speed limit on generation velocity, and what to do about it. Based on Mennillo 2026. |

## Skills

Claude Code skills you can install as a plugin or copy individually.

### Install as plugin (recommended)

```
claude plugin install ai-native-development@codelittinc
```

This installs all skills and keeps them updated.

### Or copy individually

Copy any skill folder to `~/.claude/skills/` to use.

| Skill | Command | What it does |
|-------|---------|-------------|
| [qa-check](skills/qa-check/) | `/qa-check` | Reviews code changes for rework risk, missing tests, AI-specific defect patterns, and validation gaps. Based on the AI Quality Paradox research. |
| [supply-chain-check](skills/supply-chain-check/) | `/supply-chain-check` | Single-command supply chain security audit. Scans for compromised packages, dangerous version ranges, lock file issues, CVEs, typosquatting, and local IOC artifacts. |

## Related projects

- [codemode-x](https://github.com/codelitt/codemode-x) -- MCP plugin that compresses N APIs, databases, and doc sets into 2 tools (search + execute) for Claude Code

## Contributing

Open an issue or PR. We're especially interested in:
- Patterns you've found that make LLM-assisted development faster or more reliable
- Anti-patterns that waste tokens or break feedback loops
- Real examples from production codebases (anonymized if needed)

## License

MIT
