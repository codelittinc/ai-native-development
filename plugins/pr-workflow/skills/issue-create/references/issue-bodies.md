# How to write an issue body

> A good issue body is dense and grounded. It is not a template with empty sections. Match the
> weight of the body to the weight of the issue: a small follow-up is one tight paragraph, and a
> defect that blocks a release gets structure. If the repository has a file in
> `.github/ISSUE_TEMPLATE/`, that template controls the structure, and this file gives the
> content guidance inside it.

## The body of a defect

```markdown
**Defect (blocks the release).** <!-- Use a severity marker only when the defect truly blocks. -->
<What is wrong, in one sentence, with its mechanism: the code path that misbehaves, and the
file paths in backticks.>

**Confirmed:** <The evidence. Give counts, the records that you checked, and what you ran.
Omit this section when you did not verify the problem. Then write "Suspected, not yet
reproduced" instead.>

**Recommended fix:** <The approach, and the place that it belongs. Name the alternative in one
line if there is a real design choice.>

**Acceptance:** <What "done" looks like. For a defect, this always includes a regression test
that fails today. Add the cleanup of the data that is already wrong, if any exists.>

Ref: <The provenance: a pull request review, an investigation, or a related issue #N.>
```

A good example names the exact files, states the confirmed effect with a count, such as "2 active
records have a rate above zero but no recurring charge", gives a recommended fix and its
alternative, and gives acceptance criteria that include the cleanup of the existing data.

## The body of a follow-up

A follow-up is usually one paragraph. Start with the provenance and the severity. Then give the
mechanism. Then give the request.

```markdown
Follow-up from the review of PR #NNN (this problem exists already). <What the gap is, and
where, with `path/to/file.ts` in backticks. Why the gap is safe today, or low impact.> <What
to do about it.> <The priority.>
```

A good example: "From the review of PR #87 (Low). `postChargesInTx` loops from the effective
month to the current month with no upper limit (`src/charges/post.ts:88`). The loop is safe,
because it is idempotent. But a backdate of more than one year exceeds the transaction budget and
sends many alerts. Add a limit of 24 months, or add a bound on `effectiveDate` in the schema."

## The body of a feature

Use scope bullets, not prose. Name the specification file if one exists. Name the phase when the
work is staged.

```markdown
<One line: what this is, and when it starts.> Spec: `<path to the spec file>`.

- **<Capability>:** <What it does, which surface it changes, and the state transitions in
  capital letters, for example Accept → PENDING_SIGNATURE>
- **<Capability>:** <…>
- <The sequence: "this waits for #23", or "this starts after Phase 1">
```

## The universal rules

- **Put each file path in backticks** when you know the mechanism. An issue is a search target for
  the person who picks it up.
- **Cross-reference** a related issue as `#N`, and a specification as its path.
- **Name the domain invariant.** If the issue touches the load-bearing domain of the repository,
  say which invariant is at risk, and say if the data is wrong now or only at risk.
- **State what is not broken**, when that prevents an incorrect triage. For example: "The ledger
  stays correct, but the refund does not appear as cash that the customer is owed."
- **Add no filler.** Do not write an empty section such as "Steps to reproduce: N/A". Do not
  repeat the title. Do not add a heading to an issue of two sentences.

## Anti-patterns

**A symptom with no mechanism:** "Proration is wrong sometimes on move-out."

**A template with empty sections:** "Environment: N/A. Screenshots: none."

**A hypothesis that reads as a confirmed fact.** Write "suspected" until you reproduce the
problem.

**Acceptance criteria that repeat the fix:** "the bug is fixed".

**An issue that you file without a search** for an open issue about the same mechanism.
