---
name: issue-create
version: 1.0.0
description: |
  File a GitHub issue that obeys the title, label, and body conventions of the
  repository. The skill learns those conventions from the issues that exist,
  and it does not use a fixed template. It works from a short description or
  from the current conversation, such as a defect that you just found or a
  finding that a review deferred. It searches for a duplicate before it files,
  it grounds the issue in the code by naming the file and the mechanism, it
  separates a confirmed fact from a hypothesis, it records where the issue came
  from, and it reads the label list of the repository instead of inventing a
  label.
  Use this skill to file a defect, a feature request, or work that a pull
  request review deferred.
  Triggers: "create an issue", "file a bug", "open a GitHub issue", "track this
  as an issue", "file a follow-up".
allowed-tools:
  - Read
  - Write
  - Bash
  - Grep
  - Glob
---

# Create a GitHub issue

File an issue that agrees with the conventions of this repository. The conventions are in the issues that exist, not in a fixed template. Read them first.

The skill works from the context that is available: the current conversation, such as a defect that you found, a review follow-up, or an edge case that a triage deferred; or a short description in the argument.

## Technical names in this document

This document uses Simplified Technical English (ASD-STE100). These technical names have no approved equivalent:

| Technical name | Meaning |
|---|---|
| Provenance | The place that the issue came from, such as a pull request review or an investigation |
| Mechanism | The code path that causes the problem, not the symptom that a user sees |
| Taxonomy | The set of labels that the repository uses |
| Load-bearing domain | The part of a repository where a defect is most expensive |

## Usage

```bash
/issue-create <a short description of the defect, feature, or follow-up>
/issue-create                    # take the issue from the current conversation
```

---

## Step 1: Collect the context

**Find the subject of the issue.**

- From the conversation: use the defect, the finding, or the follow-up that you discussed most recently. If there is more than one candidate, ask the user which one. You can also offer to file more than one issue.
- From the argument: use the description as the start, then add what you find in the code.

**Ground the issue in the code.** A good issue names the mechanism, not only the symptom:

- Find the files and the functions, and put each path in backticks, for example `src/charges/candidates.ts`.
- Separate what you confirmed from what you suspect. Write "Confirmed:" for a fact that you verified. Write "Suspected, not yet reproduced" for a hypothesis.
- Record the provenance: the pull request review, the investigation, or the conversation that found this. For example: "Follow-up from the review of PR #121".

## Step 2: Learn the conventions of this repository

Read the issues that exist. Do not assume a format.

```bash
gh issue list --state all --limit 30 --json number,title,labels \
  --jq '.[] | [(.number|tostring), .title, ([.labels[].name] | join(","))] | @tsv'
gh issue view <a recent issue number>   # read two or three bodies in full
```

Record these items:

- The title format. Many repositories use `scope: a specific description`. Some use a `BUG:` prefix. Some use plain prose.
- The weight of a body. Some repositories write dense prose. Some use headings.
- If the repository has an issue template in `.github/ISSUE_TEMPLATE/`. If a template exists, **the template controls the structure**.

## Step 3: Search for a duplicate

Search before you file:

```bash
gh issue list --state all --search "<key terms>" --limit 10
gh issue list --state open --limit 30      # read the titles if the search terms are unclear
```

- If an **open** issue agrees, stop and report it. Offer to add the new context as a comment with `gh issue comment <N> --body-file <path>`.
- If a **closed** issue agrees, name it in the new body, for example "This is a regression of #N".

## Step 4: Classify the issue

**The type controls the shape of the body:**

- **Defect.** The behavior is wrong today. The body starts with the defect and the evidence.
- **Feature.** This is a new capability. The body starts with the scope bullets. Name the specification file if one exists.
- **Follow-up.** This is a known gap that a review deferred and that is safe today. The body starts with the provenance and the reason for the deferral.

**Propose a priority. Do not choose one silently.** Use the priority scale of the repository, which is frequently `P0` for a blocker, then `P1`, `P2`, and `P3`. If the issue touches the load-bearing domain of the repository, say so, and propose a high priority.

## Step 5: Choose the labels

Read the label list on each run. Never use a list from memory, because the taxonomy changes:

```bash
gh label list --limit 50 --json name,description --jq '.[] | [.name, .description] | @tsv'
```

Choose one label from each group that the repository uses, such as the area, the priority, the timeline, and the type. Use a label only if it fits. A small follow-up with no label is better than a label that is wrong. **Never create a new label without approval from the user.**

## Step 6: Write the title

Use the format of the repository. If the repository has no clear format, use `scope: a specific description`. The scope is the component name that a person searches by.

- State the real defect or the real work. Do not state a vague area.
- Add the consequence in parentheses when that helps: `(this avoids many alerts on a backdate of more than one year)`.
- Give the phase for a feature that has more than one phase: `Lease renewal — Phase 1: …`.

Correct: `move-out: a non-rent monthly charge is not prorated on a mid-month move-out`

Correct: `reconciliation: block a reopen when the period is closed`

Incorrect: `Fix proration bug` — this has no scope and no specifics

Incorrect: `feat(leases): add proration` — the conventional commit format is for a pull request title, not for an issue

## Step 7: Write the body

Follow `references/issue-bodies.md` for the guidance for each type. The necessary parts:

- **The provenance first**, when a review or an investigation found the issue.
- **The problem with its mechanism**: what is wrong, *where*, with the file paths in backticks, and *why it happens*.
- **The evidence**: what you confirmed, and what you suspect.
- **The recommended fix**: the approach, and where it belongs. Name the alternative in one line if there is a real choice.
- **The acceptance**: what "done" looks like. For a defect, this always includes a regression test that fails today.
- **The cross-references**: related issues as `#N`, and the specification files.

Match the weight of the body to the weight of the issue. A follow-up of two sentences is two sentences. A small issue needs no heading.

## Step 8: Show the issue, then create it

Show the issue for approval before you create it:

```markdown
## Proposed issue

**Title**: <title>
**Labels**: <label>, <label>

**Body**:
<body>

---
Do you want me to create this issue?
```

After the user approves, write the body to a file with the Write tool and create the issue:

```bash
gh issue create --title "<title>" --label "<label1>" --label "<label2>" --body-file <path-to-body>
```

Use `--body-file`. A body that contains a backtick or a single quotation mark breaks an inline `--body` argument.

Then report the issue URL. If the user asked you to file the issue without a review, skip the approval step, but still show what you created.

## Quality checklist

- [ ] You read the issues that exist, and matched their title and body conventions
- [ ] You read `.github/ISSUE_TEMPLATE/` and used the template if one exists
- [ ] You searched for a duplicate in the open issues and the closed issues, and reported a match instead of filing again
- [ ] The title states the real defect or the real work, with its scope
- [ ] You read the label list on this run. The labels fit, and you invented none
- [ ] The body gives the provenance when a review or an investigation found the issue
- [ ] The problem statement names the files in backticks and explains the mechanism
- [ ] The body separates a confirmed fact from a hypothesis
- [ ] The body gives the recommended fix and the acceptance criteria. For a defect, it names the regression test that fails today
- [ ] An issue in the load-bearing domain names the invariant at risk, and proposes a high priority
- [ ] The body cross-references the related issues and the specification files
- [ ] You wrote the body to a file and used `--body-file`
- [ ] The user approved before you created the issue, unless the user asked you to file it directly

## Reference

`references/issue-bodies.md` gives the body shape for a defect, a follow-up, and a feature, plus the universal rules and the anti-patterns.
