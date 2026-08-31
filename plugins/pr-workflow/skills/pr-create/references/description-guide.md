# How to write a pull request description

> **A note about structure.** If the repository has a `.github/PULL_REQUEST_TEMPLATE.md` file,
> the `pr-create` skill reads it at run time, and **that template controls** the headings, the
> order, and the checkboxes. The structure below is the fallback when the repository has no
> template. For each of the two conditions, this file gives the content guidance: how to write
> clear text inside the sections.

## Two rules that outrank the remainder of this file

**1. State the end state. Do not narrate the journey.** The description states the diff as it is
now, as if it were the first and only commit. Do not write "initially I…", "after review
feedback…", "changed X then went back to Y", an "Addressed comments" section, or a reference to
an earlier revision. A reviewer examines the code in front of them. The path to that code
competes with it for their attention. A decision is necessary only when a reviewer who reads the
final code asks "why this way?". Then give the decision and its reason, not the deliberation.

**2. Stay inside the budget.** Length is not thoroughness. A description that a reviewer skims is
worse than a short description that they read.

| Section | Budget |
|---|---|
| Summary | The issue link and 3 sentences or fewer |
| Changes | 12 bullets or fewer, in groups by area |
| Implementation Details | 3 bullets or fewer, or omit the section |
| **Summary and Changes together** | 600 words or fewer — a limit, not a target |

The Test Plan and the Notes are additional to the 600 words. A necessary section must not compete
with the prose for space.

**The sentence limit and the bullet limit do the work.** Three sentences and twelve bullets keep
a description easy to scan. The word count only finds a description that started to narrate. A
change in one area is usually near 250 words. A change across many areas is usually near 450
words. If you reach 600 words with twelve necessary bullets, the pull request is usually too
large. That is the true finding. Making good prose worse to meet a number helps no one.

**The bullet test:** a bullet is necessary only if a reviewer examines the code differently
because of it. Do not repeat what the diff shows, such as "renamed X" or "added a test", unless
the bullet sends the reviewer to a different place. Remove a section instead of adding filler.

## The default structure

```markdown
## Summary

Closes #NNN <!-- or "Refs #NNN". Omit the line if no issue exists. -->

[One or two sentences. State WHAT this pull request does and WHY it is necessary.]

## Changes

### [area — for example: api, server, or a route domain]

- [A key change, with its context]
- [A key change, with its context]

### [area — for example: a shared package, the database layer, or the types]

- [A key change, with its context]

### [area — for example: web or the background worker]

- [A description of the change]

## Implementation Details (optional)

[Add this section only for an architecture decision, an approach that is not obvious,
or a trade-off that a reviewer must understand.]

- **[Decision]**: [The explanation]
- **[The alternative that you examined]**: [The reason that you did not use it]

## Test Plan

- [ ] [A specific command or verification step]
- [ ] [A specific command or verification step]
- [ ] [A manual verification step, if one is necessary]

## Notes (optional)

- **Risks**: [A known risk, or an area that needs more review]
- **Follow-ups**: [Related work that lands separately]
- **Dependencies**: [A pull request, a migration, or an environment variable that must land first]
- **Breaking changes**: [If the change breaks a consumer]
```

## The Summary section

- **Put the issue line first.** Use `Closes #NNN` when the pull request resolves the issue, because GitHub closes the issue on merge. Use `Refs #NNN` when the pull request is only related. Omit the line if no issue exists. Never invent an issue number.
- **The first sentence** states the main change.
- **The second sentence** states the problem that the change solves.
- Stay at a high level. Do not give implementation details.

Correct:

```markdown
Adds a manual "ignore" state to bank reconciliation, so that staff can clear book entries
that will never match a statement line, such as a voided check.
```

Incorrect:

```markdown
This PR updates reconciliation. We changed some handlers and added a status.
```

## The Changes section

- Put the bullets in groups by area, with the most significant group first. Use the boundaries of the repository: the API layer, the shared logic, the data layer, the shared types, the frontend, and the background jobs.
- Keep the boundary story visible. Say when logic moved from one layer to a different layer.
- Use parallel structure. Start each bullet with a verb.
- Give the file path for a complex change.
- Show a behavior change, a schema change, and a new or changed endpoint.

Correct:

```markdown
### api — reconciliation

- Added `POST /v1/bank-reconciliations/:id/ignore-entry` to mark a book entry as NOT_A_BANK_ITEM
- Reopen now checks that the period is still OPEN before it changes the status (`handlers.ts:112`)

### db

- Added a `ReconciliationEntryStatus` enum value and its migration. A partial unique index keeps
  one reconciliation in progress for each bank account
```

Incorrect:

```markdown
### api

- Updated reconciliation
- Made some changes to the handlers
- Fixed stuff
```

## The Implementation Details section

Add this section for these items:

- A technical decision that is not obvious
- A trade-off between two approaches
- A decision about concurrency or transactions, such as the isolation level, a row lock, or a retry
- A decision in the load-bearing domain of the repository
- An effect on performance or on security

```markdown
## Implementation Details

- **Serializable transaction**: The ignore operation uses the same SELECT FOR UPDATE lock as the
  reconciliation, so that two staff members cannot change the same entry at the same time. It
  retries three times on a serialization failure.

- **No effect on the ledger**: The ignore state exists only in the reconciliation workspace. The
  journal entry does not change, because a posted journal entry is immutable.
```

Omit this section for a simple change, for a standard pattern that the repository documents
already, and for code that explains itself.

## The Test Plan section

- Use a checkbox for each verification step.
- Give the exact command. Read `package.json`, the `Makefile`, or the CI workflow to find the commands of this repository.
- Limit a test run when that helps: give the path of the suite, not only the full run.
- Add a manual verification step when a person must look at a screen.
- **For a change in the load-bearing domain, name the invariants that you verified.**

Correct:

```markdown
- [ ] `npm test` — the unit tests and the integration tests pass
- [ ] `npm run typecheck` and `npm run lint`
- [ ] An integration test posts a payment and asserts that the debits equal the credits
- [ ] Reconciled the seeded CSV by hand and verified the totals
```

Incorrect:

```markdown
- [ ] Test it
- [ ] Make sure it works
- [ ] Run tests
```

## The Notes section

```markdown
**Risks**:

- This change needs a database migration on deployment. It touches a table that holds money.
- This change alters the order of charge application. Monitor the receivables report after deployment.

**Follow-ups**:

- The vendor payout part lands in a separate pull request.

**Dependencies**:

- Set `STRIPE_WEBHOOK_SECRET` in the deployment environment before you deploy.
- Blocked on #102, which must merge first.

**Breaking changes**:

- `GET /v1/reports/ar-aging` renames the `bucket30` field to `bucket_30`.
- Removed the deprecated `legacyLedger` query parameter.
```

## Anti-patterns

**Session narration.** This is the most frequent failure, and the most expensive one. It puts the
attention of the reviewer on your process instead of on the code.

```markdown
## Summary

I first tried to filter in the query, but that broke the aging report. After the review
feedback I moved the check into the shared package instead. As discussed, I added the
partial index later, to fix the performance problem that this caused.

## Changes

- Addressed a review comment about null handling
- Went back from the approach in the first commit
```

State the end state instead:

```markdown
## Summary

Excludes uncoded charges from late fee eligibility, so that a customer never gets a fee on a
charge that staff have not classified.

## Changes

- `isLateFeeEligible()` returns false for a null charge code (shared package)
- A partial index on open uncoded charges keeps the eligibility query fast (data layer)
```

**Text that is too vague:**

```markdown
## Summary

Updates some services and fixes bugs.
```

**Technical text with no context:**

```markdown
## Changes

- Refactored AbstractFactoryBuilder to use the composite pattern
- Extracted the interface IChargePoster<T> with covariant type parameters
```

**No structure:**

```markdown
Changed the charges handler and also updated the core package. Also made some changes to the
schema and fixed a bug in the web app. Tests are also updated.
```

**A Test Plan with no content:**

```markdown
## Test Plan

- [ ] Run tests
```

**Implementation details that are not necessary:**

```markdown
## Implementation Details

- Used TypeScript 5.8 syntax
- Imported Decimal from decimal.js
- Created a new function with the name handleRequest()
- Used if/else instead of switch
```
