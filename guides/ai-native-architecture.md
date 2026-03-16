# AI-native architecture: principles for building with LLMs

## The core constraint

The context window is the CPU of AI-assisted development. Everything an LLM can reason about must fit inside it. A human developer builds a mental model over months. An LLM gets ~120K tokens and starts fresh every session.

This is a design constraint, like memory limits in embedded systems or latency budgets in real-time audio. The architecture must make sure any given task requires loading minimal code while maintaining full understanding of the system.

These principles have real tradeoffs. More contracts means more maintenance. More files means more navigation cost. More abstraction means more indirection to debug. I'll try to be clear about when the tradeoff is worth it.

---

## Principle 1: Contracts over implementation

The most important file in your codebase is the one the LLM doesn't have to open.

Separate *what things do* from *how they do it*. When an LLM needs to modify a route handler, it shouldn't have to read the database adapter's internals. Just the interface. When it needs to change a React component, it doesn't need the API server, just the response shape.

What this looks like:
- Document API response shapes, database schemas, and component props in dedicated reference files
- Use explicit type signatures or contract files that define boundaries between modules
- An LLM modifying module A should never need to read module B's implementation, only B's contract
- Prefer executable contracts over documentation contracts. A Zod schema or TypeScript interface that throws at runtime beats a markdown file that can go stale. `Error: Expected number at orders[3].total_amount` is worth more than any docs page.

Anti-pattern: a 900-line `server.js` where the only way to know what `/api/orders/:id` returns is to trace through 6 SQL queries and 3 helper functions.

Better: a `data-reference.md` that says "GET /api/orders/:id returns `{ order: Order, items: LineItem[], payments: Payment[] }`" so the LLM modifying a frontend component reads 10 lines instead of 900. Even better: a TypeScript type definition that the compiler enforces.

The doc drift problem is real. Contracts only work if they're accurate, and the further a contract lives from the implementation, the faster it rots. Mitigations:
- Co-locate contracts with the code they describe when possible (TypeScript types > separate markdown)
- Generate docs from code (OpenAPI from route handlers, type exports as contracts)
- If using markdown contracts, treat them as code: update them in the same PR that changes the implementation

This is principle #1 because every other principle is a specific application of it. Contracts are the compression algorithm for context windows.

---

## Principle 2: Fail loud, fail fast

Every error should be immediately visible, specific, and actionable.

An LLM's workflow is: make change, run, read output, iterate. If errors are swallowed, vague, or delayed, the feedback loop breaks completely. After contracts, this has the highest return of any principle on this list. Silent failures waste more LLM time than any file structure issue.

**Throw, don't return null.** A function that returns `null` on bad input means the LLM generates code that "works" (no error) but produces wrong results. The LLM can debug a stack trace in seconds. It can spend an entire session chasing a `null` propagating through 5 functions.

**Specific error messages.** `Error: something went wrong` sends the LLM on a fishing expedition. `Error: sku "BLK-LG-001" not found in inventory table (warehouse_id: 12, size: "L", color: "black")` lets it fix the issue in one shot.

**Runtime validation at boundaries.** Zod schemas, JSON Schema validation, or simple assertions at the edges of your system (API input, database results, external API responses). These catch hallucinated data shapes before they propagate.

**Fail at startup, not at request time.** If a config value or env var is missing, crash immediately. Don't let the LLM spend 20 minutes building features before discovering the database connection string is wrong.

**Make test failures obvious.** A test that prints `FAIL: expected 3, got null at pricing.js:47` is more useful than one that silently exits with code 1.

Why this matters so much: Claude Code can debug a clear error message in one iteration. A silent failure or vague error can waste 10+ minutes and $5+ in API calls while the LLM investigates dead ends.

---

## Principle 3: Idempotent everything

Every operation should be safely re-runnable. LLMs make mistakes and retry.

If your import script creates duplicates on retry, your deployment script fails on second run, or your migration crashes if the column already exists, you're building a system that punishes the way LLMs naturally work: iteratively, with trial and error.

- Database operations: upsert over insert, `CREATE TABLE IF NOT EXISTS`, `ADD COLUMN IF NOT EXISTS`
- API imports: match-and-update, not blind insert (upsert endpoints that create-or-update based on a natural key)
- Scripts: check preconditions before acting (`if column exists, skip`)
- File operations: overwrite semantics over append semantics
- Deploys: running the same deploy twice should produce the same result

When Claude Code runs a script, sees an error, fixes the script, and runs it again, the first (partial) run must not have left dirty state. If it did, the second run fails for a completely different reason, and the LLM spirals into debugging a state problem instead of the original issue. Idempotency failures cause more wasted LLM time than almost any other single issue.

---

## Principle 4: Explicit dependencies, no magic

Everything the LLM needs to understand a file should be discoverable from that file.

No globals, no implicit configuration, no "you just have to know" conventions. The import section should tell the full story of a file's dependencies. Environment variables should be documented where they're used.

- Explicit imports over dependency injection magic
- Environment variables documented in a single `.env.example` or reference doc
- State passed explicitly (props, function arguments) not accessed through closures or globals
- Configuration in explicit config files, not scattered across shell profiles

One nuance: this does NOT mean "never use Rails/Next.js/Django." LLMs already know these frameworks' conventions from training data. A standard Next.js `app/` router directory structure is more explicit to an LLM than a custom routing system, because the LLM can predict where things are. The principle targets *custom* magic: the bespoke middleware chain, the in-house plugin system, the "we always name our validators with a `$` prefix" convention that exists nowhere except tribal knowledge.

The test: can a developer (or LLM) who has never seen this codebase understand what a file does by reading only that file and its imports? If the answer requires knowledge that isn't in the code or standard framework conventions, something is too implicit.

---

## Principle 5: File structure for navigability

Files should be sized and named so an LLM can find the right code in 1-2 tool calls.

This is about navigability, not arbitrary line counts. The goal: `Grep("createOrUpdateUser")` finds one file, you read the relevant 40 lines, make the change. If finding the right code requires opening 5 files to trace a call chain, the architecture is fighting the tool.

Name files for their single responsibility: `db-init.js`, `pricing.js`, `Dashboard.jsx`. Directory structure should mirror domain concepts: `pipeline/`, `hooks/`, `components/`. If you can't name a file in 2-3 words that describe its sole purpose, it probably has more than one purpose.

What matters is internal structure, not line count. A 800-line `server.js` where every route handler is a clean, self-contained 30-line block is easier for an LLM to work with than 40 separate route files where understanding the middleware chain requires opening 6 files. The LLM uses `Grep` to find the route, reads 40 lines around it, makes the change, moves on.

The real danger zone is files where you can't understand line 400 without reading lines 50-150. That's entanglement, and it's the actual problem that line count is a weak proxy for.

There's a U-curve here. Too few files is bad (entangled megafiles where everything depends on everything). Too many files is also bad (navigation hell where the LLM spends 3-4 tool calls just *finding* the right file). The sweet spot is domain-grouped files of moderate size.

And a tradeoff worth naming: every file split adds one more thing to navigate. Don't split a file "for the AI" if you wouldn't split it for a human developer joining the team.

---

## Principle 6: Adapter pattern at every boundary

Isolate external systems behind thin wrappers with stable interfaces.

When the implementation behind a boundary changes (PostgreSQL to SQLite, REST to GraphQL, Stripe v2 to v3), only the adapter file changes. Every consumer stays untouched. This limits the blast radius of any change to a single file, which matters for AI development where you want the LLM to modify one thing without understanding everything.

- Database: `db.js` exposes `all()`, `run()`. Callers never write dialect-specific SQL.
- External APIs: wrap in a service file that returns domain objects, not raw HTTP responses.
- LLM providers: adapter that normalizes OpenAI/Anthropic/Kimi behind `extract(text) → StructuredData`.
- File storage: abstract local filesystem vs S3 vs R2 behind `read(key)`, `write(key, data)`.

On a recent project, introducing a `db.js` adapter reduced 1,785 lines of duplicated server code to 730 lines. Every future API route change happens in one file.

When NOT to do this: don't wrap a library you'll never swap. An adapter around `lodash` or `dayjs` adds indirection for zero benefit. Adapters earn their keep at boundaries where the other side might change: databases, cloud services, third-party APIs, LLM providers. If you're wrapping something that will never change, you're over-engineering.

---

## Principle 7: Tests as guardrails

Tests should verify behavior at boundaries so LLMs can refactor freely.

An LLM refactoring a module's internals needs confidence that it hasn't broken consumers. Tests that assert implementation details (mock call counts, internal state) break on every refactor and provide no signal. Tests that assert inputs → outputs at module boundaries let the LLM change anything inside.

- Test API endpoints (input request → output response), not internal helper functions
- Test the public interface of a module, not its private methods
- Integration tests for critical paths AND unit tests for complex logic. You need both.
- Validation tests for data contracts (e.g., 200+ tests for input validation and data extraction rules)
- Keep test files focused so an LLM can read the relevant test suite for a module

One thing that bites people: module B often has an undocumented dependency on module A's internal behavior. Claude refactors A perfectly, all tests pass, and B breaks in production three days later. The defense is integration tests that exercise the full dependency graph, not just unit tests at individual module boundaries. CI pipelines that run the complete test suite are non-negotiable here.

The ideal workflow: LLM reads contract, makes changes, runs tests, all pass, done. If tests are flaky, slow, or test the wrong things, this loop breaks.

---

## Principle 8: Search over scan

Structure information so LLMs can find it in O(1), not O(n).

When an LLM has 100 tools, 50 API endpoints, and 30 database tables available, listing them all consumes the entire context window. Let it search for what's relevant and load only that.

- Use structured documentation with clear headings (LLMs search by heading)
- CLAUDE.md files are the entry-point index. They tell the LLM where to look, not everything it needs to know.
- Well-named files are searchable; line 847 of a megafile is not
- For large systems: MCP plugins like [codemode-x](https://github.com/codelitt/codemode-x) compress N APIs, databases, and doc sets into 2 tools (search + execute), so the LLM loads only the signatures it needs instead of the full tool catalog

Design your project so that `Glob("**/user*.ts")` or `Grep("createOrUpdateUser")` immediately finds what the LLM needs. If finding something requires reading 5 files to understand the call chain, the architecture is working against the tooling.

---

## Principle 9: Structured documentation as system memory

Documentation is not for humans who already know the system. It's for the LLM that starts fresh every session.

An LLM loses everything when the context window resets. Documentation must serve as the persistent memory layer: structured enough to search, concise enough to load, and authoritative enough to trust without reading the implementation.

The documentation stack, ordered by load priority:

| Layer | Purpose | Token budget | Example |
|-------|---------|-------------|---------|
| CLAUDE.md | Entry-point index. What's where, how to run things, key commands. | ~2K tokens | "Backend is Express + PG, run `npm start`, routes in server.js" |
| Executable contracts | TypeScript types, Zod schemas, OpenAPI specs. | Varies | `type OrderResponse = { order: Order, items: LineItem[] }` |
| Data contracts | API shapes, DB schemas, domain terminology (if not using executable contracts). | ~1K tokens per domain | "GET /api/orders/:id → { order, items[], payments[] }" |
| Architecture docs | Why decisions were made, system boundaries, data flow. | Load on demand | "We use upsert imports because idempotency matters for automated pipelines" |
| Product docs | Feature descriptions, user personas, business logic. | Load on demand | "List price vs net price toggling affects all dashboard charts" |
| Inline comments | Non-obvious logic only. | Zero budget, already in the file | "// PG needs ::jsonb cast, SQLite doesn't" |

The cold-start problem: what happens when an LLM enters a codebase with no CLAUDE.md, no contracts, no documentation? The first session should generate bootstrapping docs. Have the LLM explore the codebase and write the initial CLAUDE.md and contract docs. This is the most common real-world scenario and the single best use of your first session.

Session handoff between sequential LLM sessions needs context passing. Patterns that work:
- A `tasks/` directory with current state ("auth module is half-migrated, don't touch user.js")
- CLAUDE.md memory sections that persist across sessions
- Git commit messages that explain *why*, not just *what*. The next session reads `git log`.

---

## How these principles connect

The first four principles (Contracts, Fail Fast, Idempotency, Explicit Dependencies) are defensive. They prevent disasters. The rest (File Structure, Adapters, Tests, Search, Documentation) are optimizations that make the LLM more efficient. Get the defensive ones right first.

Contracts get enforced by fail-fast validation. Idempotent operations get validated by tests. Explicit dependencies enable search. File structure gets isolated by adapters. Documentation persists it all across sessions.

---

## Checklist for new projects

1. Before writing code: create CLAUDE.md (entry-point index) and define data contracts (TypeScript types or Zod schemas preferred over markdown)
2. First file: the adapter/abstraction layer for your primary external dependency
3. At every boundary: validate inputs with schemas that throw specific errors on failure
4. Every function: does it take explicit inputs and return explicit outputs? Does it throw on bad input instead of returning null?
5. Every script: is it idempotent? What happens if it runs twice?
6. Every API: is the request/response shape defined in an executable contract?
7. Every test: does it test behavior at a boundary? Would it still pass if the internals were completely rewritten?
8. Every PR: update contracts and docs in the same PR as the implementation change

---

## Checklist for existing projects (AI-buildability audit)

1. Find the silent failures. Functions that return null/undefined instead of throwing. Add error messages with enough context for an LLM to fix the issue in one shot.
2. Find the fragile scripts. Anything that fails on second run. Make them idempotent.
3. Find the duplicated logic. Two files doing the same thing. Unify behind an adapter.
4. Find the missing contracts. If an LLM has to read the implementation to know the data shape, add a contract. Prefer executable (TypeScript/Zod) over documentation (markdown).
5. Find the magic. Custom implicit configuration, convention-based behavior, globals. Make them explicit. (Standard framework conventions like Next.js routing are fine.)
6. Find the entangled files. Files where you can't understand one section without reading three others. These need internal restructuring or splitting along natural seams.
7. Bootstrap the cold start. If there's no CLAUDE.md, write one. Single highest-leverage task for an existing codebase.

---

## Why this matters beyond AI

These principles also make code better for human developers, but let's be honest about the tradeoff. More contracts means more maintenance. More files means more navigation. More validation means more boilerplate. For a solo developer on a small project, some of these aren't worth the overhead.

The AI context window is a forcing function. It makes the cost of poor architecture immediate instead of gradual. Load a 2,000-line entangled file and you've burned your token budget. Miss a contract and the LLM hallucinates the data shape. Swallow an error and the LLM wastes 10 minutes debugging silence.

The question isn't whether these tradeoffs exist. It's whether the AI-assisted development velocity gain justifies them. For any codebase where you're regularly using LLM tools, it does.
