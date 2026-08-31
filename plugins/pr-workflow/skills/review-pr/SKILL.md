---
name: review-pr
version: 1.0.0
description: |
  Examine a GitHub pull request for code quality, security problems, and the
  rules of the repository. Write every finding in Simplified Technical English
  (ASD-STE100), in the What, Why, Fix shape, with a file and line citation and
  a concrete failure scenario. The delivery depends on the author of the pull
  request: for your own pull request the skill prints the review in the
  terminal and posts nothing to GitHub; for a pull request from a different
  person the skill shows you each comment, waits for your approval, and then
  posts them as one review with inline comments. It gives the merge verdict
  first, limits the review to the diff, and runs the specialist reviewer agents
  of the repository.
  Use this skill to review a pull request that is open, your own or one from a
  teammate.
  Triggers: "review this PR", "review pull request", "code review the PR",
  "look at PR 123", "leave review comments".
allowed-tools:
  - Read
  - Write
  - Bash
  - Grep
  - Glob
---

# PR Review

Examine a GitHub pull request for **code quality**, **security problems**, and **the rules of the repository**. Write all feedback in **ASD-STE100 Simplified Technical English**.

The delivery depends on the author of the pull request:

- **The pull request is yours.** Print the review in the terminal, so that you can act on it. Post nothing to GitHub.
- **The pull request belongs to a different person.** Post the findings as comments on the pull request, after the user approves them.

## Technical names in this document

This document uses Simplified Technical English (ASD-STE100). These technical names have no approved equivalent:

| Technical name | Meaning |
|---|---|
| Inline comment | A comment that GitHub attaches to one line of the diff |
| Lens | One area of judgement, such as security or migration safety |
| Load-bearing domain | The part of a repository where a defect is most expensive, such as money movement or personal data |
| Merge verdict | The one-line answer to "can the author merge this?" |

## Usage

```bash
/review-pr <PR_URL_or_NUMBER>
```

- `PR_URL`: for example `https://github.com/owner/repo/pull/123`
- `PR_NUMBER`: for example `123`. The number resolves against the `origin` remote of the current repository.
- No argument: use the pull request of the current branch. If the current branch has no pull request, ask the user for the number and stop.

---

## Step 0: Read the Simplified Technical English rules

Read `references/asd-ste100.md` before you write any feedback. Each sentence that you write for this review must obey it. This applies to the terminal summary and to each GitHub comment. This is the purpose of the skill. Do not skip this step.

## Step 1: Find the author, because the author controls the delivery

```bash
gh api user --jq .login                                      # your GitHub login
gh pr view <PR> --json number,url,author,title,isDraft       # the pull request and its author
```

- If `author.login` is the same as your login, the mode is **SELF**. Print the review in the terminal.
- If the author is a bot, that is, `author.is_bot` is true or the login ends with `[bot]`, the mode is **SELF**. Do not post a comment on a pull request from a bot.
- If the author is different, the mode is **OTHER**. Post comments on the pull request.

State the mode to the user in one line before you continue. For example: "This pull request is yours. I print the review here." Say in the same line if the pull request is a draft, because a draft can change before it is ready.

## Step 2: Get the diff and the context

Write the diff to a file. A bare `gh pr diff` prints each line and fills the context window on a large pull request. Read the file and search the file instead. The file headers in the diff give you the list of files, so you do not need a second command for the list.

```bash
gh pr diff <PR> > /tmp/review-pr-<PR>.diff

# The comments that exist, so that you do not repeat a point that a reviewer made already
gh pr view <PR> --json comments,reviews
```

Skip the lock files and the generated output when you read the diff, for example `package-lock.json`, `pnpm-lock.yaml`, `yarn.lock`, `go.sum`, and a snapshot file. They are noise in a review.

Understand the change before you judge it:

- Which directories and packages does the change touch?
- Which endpoint or route domain does the change touch, if any?
- **Does the change touch the load-bearing domain of this repository?** Read `REVIEW.md`, `CLAUDE.md`, `AGENTS.md`, or `CONTRIBUTING.md` to find which domain this repository protects.

Read the source around the diff when the diff alone is not enough. A finding must be true in the real file, not only in the patch.

## Step 3: Review across the three lenses

Read **`references/review-criteria.md`** and apply it in full. That file is the shared definition of what to judge and how hard: the order in which to read the rules of the repository, the three lenses of code quality, security, and repository rules, the scope rule, and the table that fans out to specialist reviewers.

Do not repeat the content of that file here. Change the criteria file when a criterion must change.

For each finding, record the file, the line, the severity, and the three-part shape of What, Why, and Fix from the Simplified Technical English reference.

## Step 4: Severity, the merge verdict, and honesty

`references/review-criteria.md` defines the severity scale of Critical, High, Medium, Low, and Nit. It also defines the bar for a finding and the three merge verdicts. Apply them as they are written.

This skill adds one rule about placement. Give the verdict **early**: on the first line of a SELF review, and on the second line of an OTHER summary, directly after the thank-you.

## Step 5: Deliver the review

### Mode SELF: print the review here

Print the review in the terminal in this structure. Post nothing to GitHub.

```markdown
## PR Review — #<number> <title>  (yours — printed here)

**Merge verdict**: <🚫 Blocking / ⚠️ Merge, then fix soon / ✅ Safe to merge as it is> — <one sentence.>

**Scope reviewed**: <the areas that the diff touches> · <load-bearing domain: yes or no>

### Critical
- **<file>:<line> — <a one-line title>.** <What.> <Why.> **Fix:** <an imperative sentence.>

### High
- ...

### Medium
- ...

### Low and Nit
- ...

### Correct areas
- <an area that is clean, in one sentence.>

**Verdict**: <one sentence. For example: "Fix the two Critical findings before you merge.">
```

If the review found nothing, say so plainly and give the verdict.

### Mode OTHER: comment on the pull request

Post the findings to the pull request. Use **inline comments** on the exact lines, in one review, so that the author sees each point in its context.

1. Write each comment in Simplified Technical English. Check each one against the list in `references/asd-ste100.md`.
2. **Start with a thank-you.** Start the summary with a genuine thank-you to the author, for example "Thank you for this pull request, @author." Keep the findings themselves in Simplified Technical English.
3. **Get approval before you post.** This action is outward-facing. Show the user each comment and the target pull request. Post only after the user approves.
4. Post the full review with **one** command. Choose the path by the type of your findings.

**Path 1, inline comments. This is the normal path.** Use the GitHub review API. One request posts the summary and each inline comment as a single review. Do not also run `gh pr review`, because that posts a second review.

Do **not** build the request with inline `-f 'comments[][body]=...'` arguments. A finding can contain a single quotation mark or a backtick, and that character breaks the shell argument. Write the payload to a JSON file instead. Write the file with the Write tool, because the tool escapes each string for you.

```json
{
  "event": "COMMENT",
  "body": "<the summary in Simplified Technical English>",
  "comments": [
    { "path": "<file>", "line": 42, "body": "<the finding: What. Why. Fix.>" }
  ]
}
```

Then post the review from that file:

```bash
gh api repos/{owner}/{repo}/pulls/<number>/reviews --input <path-to-json>
```

**Path 2, no inline comment.** Every finding is cross-cutting. Post the summary alone:

```bash
gh pr review <PR> --comment --body-file <path-to-summary>
```

Rules for each path:

- Use `event=COMMENT`. Do **not** use `APPROVE` or `REQUEST_CHANGES`. This skill comments. It does not gate the merge, unless the user asks for a verdict event.
- Put a finding that has no single line, such as an architecture point, in the summary and not in an inline comment.
- The summary starts with the thank-you, then the merge verdict on its own line, then one sentence of overall assessment, then the findings that have no line.

After you post, print the pull request URL and a short list of what you posted.

## Quality checklist

- [ ] You read `references/asd-ste100.md` before you wrote any feedback
- [ ] You compared `gh api user` with the pull request author, and stated the mode to the user
- [ ] The review covers code quality, security, and the rules of the repository
- [ ] You read the rule files of the repository before you judged the change
- [ ] The merge verdict is first, and it agrees with the severities that you found
- [ ] Each finding has a real file and line, and the What, Why, Fix shape
- [ ] Each finding gives a concrete failure scenario
- [ ] The review stays inside the diff. A problem outside the diff is one `Out of scope:` line
- [ ] Each sentence obeys ASD-STE100: short, active, simple tense, one idea
- [ ] SELF mode printed the review here and posted nothing to GitHub
- [ ] OTHER mode started the summary with a thank-you to the author
- [ ] OTHER mode showed the comments and got approval before it posted
- [ ] You wrote the JSON payload with the Write tool, and did not build it in the shell
- [ ] The review names the clean areas, and invents no finding

## Examples

**Example 1: your own pull request. The review prints here.**

```bash
/review-pr 275
# The author is you, so the skill prints the review in the terminal.
```

**Example 2: a pull request from a teammate. The review posts to GitHub.**

```bash
/review-pr https://github.com/owner/repo/pull/266
# The author is different, so the skill writes the comments, asks you, then posts them.
```
