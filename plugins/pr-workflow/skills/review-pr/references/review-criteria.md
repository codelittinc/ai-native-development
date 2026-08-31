# Review criteria

This file is the one definition of **what to judge**, **how severe a finding is**, and **what a
finding must contain**.

Two callers read this file, and neither one repeats it:

- The `review-pr` skill, which examines a pull request and delivers the result to the terminal or
  to GitHub comments.
- The `pr-create-reviewed` skill, which runs the same judgement in subagents that have no session
  context.

Change this file when a criterion must change.

## Read these files first, in this order

The rules of the repository outrank the general rules in this file. Read the rules of the
repository before you judge anything:

1. **`REVIEW.md`** at the root of the repository, if it exists. It holds the severity rules of
   this repository, the list of items to always check, the list of items to skip, and the
   verification bar. **It outranks each rule below.**
2. **`CLAUDE.md`, `AGENTS.md`, and `CONTRIBUTING.md`** at the root, and the `CLAUDE.md` file at
   each directory level that the diff touches. A root file is frequently a router to more files.
   Never decide that a rule does not exist because the root file does not hold it.
3. **The `.claude/rules/*.md` files whose `paths:` frontmatter agrees with the diff**, if the
   repository uses them.

If the repository has none of these files, say so in one line in the review. Then judge the
change against the three lenses below and against the patterns that the surrounding code uses.

## The three lenses

**A. Code quality.** Look for clear names, small functions, no dead code, no duplicated code, and
correct error handling with no error that the code swallows. Hold the change to the file size
rule of the repository. Hold the tests to this bar: a test states the intent, a public function
has a unit test, an endpoint has an integration test against a real dependency, and **no test is
made weaker, skipped, or deleted to make the change pass**.

**B. Security.** Each endpoint checks the correct authentication level and the correct data
scope. A schema validates the input before the input reaches the database. Look for SQL
injection, a secret in the code, personal data in a log, and a value that is correct in only one
environment. Authorization must be a permission check and a scope check. A role name alone is not
an authorization check.

**C. The rules of this repository.** These carry the most weight, because a general reviewer
cannot infer them. When the diff touches the load-bearing domain of the repository — money
movement, authentication, personal data, data migration, or physical control — hold the change to
the full rule file for that domain. Do not check a shortened list. Hold each pull request to the
boundary rules between packages, and to the documentation rule, if the repository has one: many
repositories require that a change which a user can observe updates its documentation page in the
same pull request.

## Severity

Rank each finding **Critical**, then **High**, then **Medium**, then **Low**, then **Nit**.

- A correctness defect, a security hole, or a broken domain invariant is always **High** or above.
- Each item that `REVIEW.md` lists as always important is **High** or above. It is never a Nit,
  and the size of the diff does not change this.

## The bar for a finding

**Each finding needs a `file:line` citation and a concrete failure scenario.** The scenario gives
the input or the state, and the incorrect output or the crash that the input produces. If you
cannot write that sentence, you do not have a finding.

Never infer the behavior of a function from its name. The name `validateCharge()` is not evidence
that the function validates anything. Open the function. Read the source around the diff when the
diff alone is not enough. A finding must be true in the real file, not only in the patch.

Report only a finding that you can defend against the real code. Do not add filler. If an area is
clean, say so in one sentence. Do not invent a nit. A review with filler costs the author more
time than it saves.

## The merge verdict

Give the verdict **first**, so that the author knows immediately if a change is mandatory.

- **🚫 Blocking. Do not merge until you fix this.** The review found a Critical or a High finding. Name it.
- **⚠️ Merge, then fix soon.** The most severe finding is Medium. Say what to fix.
- **✅ Safe to merge as it is.** The review found only Low findings or Nits, or found nothing.

Map the verdict to the severities that you found. Do not call a High finding optional. Do not
block a merge for a Nit.

## Scope: the diff, and only the diff

Report only on the lines that the diff adds or changes. A problem that exists outside the diff is
out of scope. Name it in one `Out of scope:` line and do not propose a fix. A reviewer who
examines unrelated code makes a reviewable pull request unreviewable, and the author must then
argue about code that they did not touch.

There is one exception. A file that this pull request touches is in scope when the pull request
makes its existing state worse, or when the changes of the pull request push the file past a size
rule of the repository.

## Fan out by lens

One general pass misses the failure modes of a domain. Before you review, find the specialist
reviewers that the repository defines:

```bash
ls .claude/agents/ 2>/dev/null
```

Read the description of each agent. For each agent whose scope the diff touches, run that agent
and merge its findings. Remove a finding that repeats another one at the same file and line.

If the repository defines no agents, use these lenses. Run one subagent for each lens that the
diff touches, and give it the lens name and the criteria in this file:

| The diff touches | The lens |
|---|---|
| The load-bearing domain of the repository, such as money, authentication, or personal data | The domain invariants |
| A database schema, a migration, or a database constraint | Deployment safety of the migration |
| A CI workflow, a Dockerfile, or an environment variable | Deployment safety |
| The frontend | The design system, accessibility, and the state that reaches the browser |
| A package boundary or a shared type | The contract between packages |
| Behavior that a user can observe | The documentation obligation |

Always run one general reviewer as well. It covers what no lens above claims. A subagent cannot
start another subagent, so the caller owns the fan out.

## How this review divides work with the other checks

- `/code-review` in Claude Code finds correctness defects in the diff.
- `/qa-check` finds AI-specific quality decay and architecture defects.
- This review finds defects in code quality, in security, and against the rules of the repository,
  and it delivers the result to a person or to GitHub.

Run them together. Do not do the same work two times in one review.
