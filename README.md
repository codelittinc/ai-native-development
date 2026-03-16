# AI-native development

Guides and best practices for building software with LLMs, from the team at [Codelitt](https://codelitt.com).

These aren't theoretical. They come from shipping production software where Claude Code, codemode-x, and other LLM tools do a significant share of the implementation work. When something wastes tokens, breaks the feedback loop, or confuses the model, we write it down.

## Guides

| Guide | What it covers |
|-------|---------------|
| [AI-native architecture](guides/ai-native-architecture.md) | 9 principles for structuring codebases so LLMs can work in them effectively. Contracts, error handling, idempotency, file structure, and more. |
| [Claude Code workflows](guides/claude-code-workflows.md) | Practical setup and habits: planning mode, context-mode plugin, /documents/ folder, CLAUDE.md wiring, subagents, task tracking, and workflow orchestration rules. |

## Related projects

- [codemode-x](https://github.com/codelitt/codemode-x) -- MCP plugin that compresses N APIs, databases, and doc sets into 2 tools (search + execute) for Claude Code

## Contributing

Open an issue or PR. We're especially interested in:
- Patterns you've found that make LLM-assisted development faster or more reliable
- Anti-patterns that waste tokens or break feedback loops
- Real examples from production codebases (anonymized if needed)

## License

MIT
