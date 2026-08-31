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

Claude Code skills you can install as plugins or copy individually.

### Install as plugins (recommended)

First add the marketplace. Inside Claude Code:

```
/plugin marketplace add codelittinc/ai-native-development
```

Or from the CLI:

```
claude plugin marketplace add codelittinc/ai-native-development
```

Then install the plugins you want:

```
claude plugin install qa-check@ai-native-development
claude plugin install supply-chain-check@ai-native-development
claude plugin install pr-workflow@ai-native-development
```

Installed plugins receive updates when new versions are published.

### Or copy individually

Copy a skill folder from `plugins/<plugin>/skills/<skill>/` to `~/.claude/skills/` to use it without the plugin system. The five pull request skills live in one plugin, `pr-workflow`, because they call each other; copy the whole set if you copy any of them.

| Skill | Command | What it does |
|-------|---------|-------------|
| [qa-check](plugins/qa-check/skills/qa-check/) | `/qa-check` | Reviews code changes for rework risk, weakened or missing tests, dependency provenance, missing specs, AI slop, and validation gaps. Complements the built-in /code-review, which hunts correctness bugs. Based on the AI Quality Paradox research. |
| [supply-chain-check](plugins/supply-chain-check/skills/supply-chain-check/) | `/supply-chain-check` | Single-command supply chain security audit. Queries live advisory sources (npm audit, OSV.dev, GitHub Advisory Database) and scans for dangerous version ranges, lock file issues, typosquatting, slopsquatting, and local IOC artifacts. |
| [pr-create](plugins/pr-workflow/skills/pr-create/) | `/pr-create` | Reads the branch diff, writes a title and a description, and opens the pull request. The description states the end state of the diff, inside a sentence and bullet budget. It never narrates the session. |
| [pr-create-reviewed](plugins/pr-workflow/skills/pr-create-reviewed/) | `/pr-create-reviewed` | Opens the pull request as a draft, reviews it with subagents that get only the diff, and marks it ready after you triage the findings. The reviewers get no session context, so they do not inherit the reasoning of the author. |
| [review-pr](plugins/pr-workflow/skills/review-pr/) | `/review-pr` | Reviews a pull request for code quality, security, and the rules of the repository. Writes every finding in Simplified Technical English. Prints the review for your own pull request; posts comments on someone else's, after you approve them. |
| [pr-address-comments](plugins/pr-workflow/skills/pr-address-comments/) | `/pr-address-comments` | Collects every unresolved comment from all three GitHub comment APIs, triages each one with you, applies the accepted fixes, and answers each thread. |
| [issue-create](plugins/pr-workflow/skills/issue-create/) | `/issue-create` | Files an issue that matches the conventions of the repository. Searches for a duplicate, names the mechanism and the files, and separates a confirmed fact from a hypothesis. |

## Related projects

- [codemode-x](https://github.com/codelitt/codemode-x) -- MCP plugin that compresses N APIs, databases, and doc sets into 2 tools (search + execute) for Claude Code

## Contributing

Open an issue or PR. We're especially interested in:
- Patterns you've found that make LLM-assisted development faster or more reliable
- Anti-patterns that waste tokens or break feedback loops
- Real examples from production codebases (anonymized if needed)

## License

MIT
