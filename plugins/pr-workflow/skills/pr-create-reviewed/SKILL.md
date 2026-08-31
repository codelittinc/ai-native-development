---
name: pr-create-reviewed
version: 1.0.0
description: |
  Open a pull request as a draft, examine it with subagents that have no
  session context, triage the findings with the author, then mark the pull
  request ready. The subagents get the pull request number, the diff, and their
  lens, and nothing else: the session that wrote the code holds its own
  reasons, and a reviewer that inherits those reasons agrees with them. The
  skill uses /pr-create for the title and the description, opens the pull
  request as a draft, fans out to the specialist reviewer agents of the
  repository, presents one findings table for you to triage, applies the fixes
  that you accept, limits the loop to three rounds, and marks the pull request
  ready.
  Use this skill for a change that a reviewer must think about. Use /pr-create
  for a documentation fix or a one-line configuration change.
  Triggers: "open a reviewed PR", "PR with review", "draft PR and review it",
  "review before I open the PR", "self-review this branch".
# No allowed-tools list. This skill starts subagents, and a tool allowlist that omits the
# subagent tool would silently stop the review loop, which is the purpose of the skill.
---

# PR Create with a review

```
title and description  →  qa-check  →  draft PR  →  subagent review  →  you triage  →  QA comment  →  ready
```

The review runs in **separate agent context windows**. That is the purpose of the skill. The session that wrote the code holds its own reasons for the code, and a reviewer that inherits those reasons agrees with them. The reviewers get the pull request number and the diff, and nothing else.

Use `/pr-create` when the change does not need this loop, such as a documentation fix or a one-line configuration change. Use this skill for a change that a reviewer must think about.

## Technical names in this document

This document uses Simplified Technical English (ASD-STE100). These technical names have no approved equivalent:

| Technical name | Meaning |
|---|---|
| Subagent | A separate agent run that has its own context window |
| Lens | One area of judgement, such as security or migration safety |
| Fan out | To start one subagent for each lens that the diff touches |
| Round | One cycle of review, fix, and push |

## Usage

```bash
/pr-create-reviewed                # the current branch
/pr-create-reviewed BRANCH_NAME
```

---

## Step 1: Write the title and the description with `/pr-create`

Follow **steps 0 to 4 of the `pr-create` skill**: the mode, the description structure from the repository template, the check that the branch is not behind, the split proposal for more than 20 files, the analysis of the diff, the title format, and the description rules of end state and budget.

Do not repeat or reinterpret those rules here. The `pr-create` skill owns the definition of a good title and description. This skill owns what happens around them.

Stop at the end of step 4 of that skill, with a title, a description, and the approval of the user.

## Step 2: Run the quality check, then open the draft

**Run `/qa-check` before the push, not after.** If the `qa-check` plugin is installed and the repository has a `.qa-check-required` file, a PreToolUse hook stops `git push` until a report exists for HEAD. A push before the check fails. Keep the report, because Step 6 posts it, and Step 6 uses this report again if HEAD does not move.

```bash
git push -u origin <branch>
gh pr create --draft --title "<title>" --body-file <path-to-body>
```

**A draft is the default.** The pull request is not ready for a person until the loop below runs and the report is posted. Open a pull request that is not a draft only when the user asks for that.

## Step 3: Review in isolated contexts, limited to the diff

Write the diff to a file one time, so that each reviewer reads a file instead of getting the diff again:

```bash
gh pr diff <N> > /tmp/pr-<N>.diff
```

Find the specialist reviewers that this repository defines:

```bash
ls .claude/agents/ 2>/dev/null
```

Start the reviewers with the Agent tool. Put them **all in one message, so that they run at the same time**:

- **Always** run one general reviewer.
- **Also run each specialist lens whose scope the diff touches.** The routing table is in the `review-pr` skill, in `../review-pr/references/review-criteria.md`, under "Fan out by lens". Read the table there. Do not keep a second copy of it here.

Give each agent **only** the pull request number, the path of the diff file, its lens, and the scope rule. Give it no session context, no summary of your intention, and no list of the parts that you believe are correct. An explanation of your reasoning to the reviewer is how you make the reviewer agree with you.

The scope rule has one definition, in `../review-pr/references/review-criteria.md`, under "Scope: the diff, and only the diff". Copy that section into each agent prompt exactly. Do not put it in different words, and do not write a competing version here.

## Step 4: Triage. The author decides.

Merge the findings. Remove a finding that repeats another one at the same file and line. Present one table:

| Severity | file:line | Finding | Proposed action |
|---|---|---|---|

Then **ask the user** which findings to fix, which to defer to an issue with `/issue-create`, and which to reject. Do not start a fix before the user answers.

Two rules limit the triage:

- **Never defer a Critical finding.**
- If the code of the finding is already inside the scope of this pull request, fix it here. Do not open an issue for it.

Say plainly when one of these rules applies.

Check each finding yourself before you present it. A reviewer that runs blind is sometimes incorrect about context of the repository that it could not see. Verify that the citation points to real code, and that the failure scenario is real. Do not put an incorrect finding in the table because an agent wrote it. Do not remove a correct finding because it is inconvenient.

## Step 5: Loop

After the fixes, push and run Step 3 again. Use **3 rounds maximum**. From round 2, report only the findings that are Medium or above. A one-line fix must not reach round seven because of style. If round 3 still has a finding that blocks the merge, stop and tell the user. Do not loop again.

**A fix never changes the pull request description.** A round changes the code, not the description. The description still states only the end state, as step 4 of `/pr-create` requires. This is the most frequent place where that rule fails.

## Step 6: Post the report, then mark the pull request ready

Use the report from Step 2 if HEAD did not move. If the loop pushed a fix, HEAD moved, and the report no longer describes this commit. Run `/qa-check` again. Never invent a report. Never post a report from a different commit.

Post the report and mark the pull request ready. Follow **Step 6 of `/pr-create`** for the comment format:

```bash
gh pr comment <N> --body-file <path-to-report>   # the heading must be exactly: ## QA Check Report
gh pr ready <N>
```

Report the pull request URL, the number of rounds that ran, the fixes that you made, and each item that you deferred to an issue. If you skipped a round, or if a finding is unresolved, say so. A loop that you report as complete when it is not is worse than no loop.

## Quality checklist

- [ ] `/pr-create` steps 0 to 4 wrote the title and the description. This skill did not write its own
- [ ] You ran `/qa-check` **before** the push, if the plugin is installed
- [ ] You created the pull request with `--draft`
- [ ] One general reviewer and each matching lens ran as subagents, in one message
- [ ] Each agent got only the pull request number, the diff path, its lens, and the scope rule word for word
- [ ] No session context reached any reviewer prompt
- [ ] You verified each finding before you presented it
- [ ] **The user triaged the findings.** No Critical finding is deferred
- [ ] The loop used 3 rounds maximum, and reported only Medium and above from round 2
- [ ] The review rounds did not change the pull request description
- [ ] You posted `## QA Check Report` as a comment against the current HEAD
- [ ] You ran `gh pr ready` last
- [ ] You reported the outcome honestly, and named each item that stays open
