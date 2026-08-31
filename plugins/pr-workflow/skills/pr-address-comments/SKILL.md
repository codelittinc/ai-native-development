---
name: pr-address-comments
version: 1.0.0
description: |
  Collect every unresolved review comment on a pull request, triage each one
  into fix, defer, decline, or already fixed with the author, apply the fixes
  that the author accepts, and answer each thread. The skill reads all three
  GitHub comment surfaces, because inline comments, top-level comments, and
  review summaries are three different APIs and one of them is easy to miss. It
  uses GraphQL to skip the threads that a reviewer resolved. It reads each
  comment against the code as it is now, not as the comment describes it. It
  never changes the pull request description, because the description states
  the end state and not the history of the review.
  Use this skill after a person or a review command leaves feedback on a pull
  request.
  Triggers: "address the review comments", "respond to PR feedback", "fix the
  review comments", "reply to the reviewer", "handle PR comments".
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Grep
  - Glob
---

# Address the review comments on a pull request

A reviewer produces findings. This skill closes the loop: collect what is open, decide each finding **with the user**, fix what the user accepts, and answer each thread, so that no comment stays unanswered.

## Technical names in this document

This document uses Simplified Technical English (ASD-STE100). These technical names have no approved equivalent:

| Technical name | Meaning |
|---|---|
| Thread | One review comment and the replies below it |
| Resolved thread | A thread that a person marked as complete in the GitHub interface |
| Outdated thread | A thread whose line moved, because a later commit changed the file |
| Surface | One of the three GitHub APIs that hold review feedback |

## Usage

```bash
/pr-address-comments              # the pull request of the current branch
/pr-address-comments <PR_NUMBER>
/pr-address-comments <PR_URL>
```

---

## Step 1: Find the pull request and the branch

```bash
gh pr view <PR> --json number,url,title,headRefName,author,isDraft
```

With no argument, find the pull request from the current branch. If the branch has no pull request, ask the user for the number and stop.

**Check out the head branch** if you are not on it. You are going to edit code, and the comments describe the state of that branch. If the branch is behind its remote, pull first. A fix on an old tree gets lost on the next push.

## Step 2: Collect every comment surface

Review feedback lives in three places, and they are three different APIs. Read all three. A surface that you miss is how a comment gets lost.

```bash
# Inline comments on specific lines, with their diff context
gh api repos/{owner}/{repo}/pulls/<PR>/comments --paginate

# Top-level comments
gh api repos/{owner}/{repo}/issues/<PR>/comments --paginate

# Review summaries
gh api repos/{owner}/{repo}/pulls/<PR>/reviews --paginate
```

**Skip each thread that a reviewer resolved.** Only GraphQL gives you that state:

```bash
gh api graphql -f query='
  query($owner:String!, $repo:String!, $pr:Int!) {
    repository(owner:$owner, name:$repo) {
      pullRequest(number:$pr) {
        reviewThreads(first:100) {
          nodes {
            id isResolved isOutdated
            comments(first:50) { nodes { id databaseId author{login} body path line } }
          }
        }
      }
    }
  }' -F owner=<owner> -F repo=<repo> -F pr=<PR>
```

Remove each thread where `isResolved` is true. Keep each thread where `isOutdated` is true, and mark it. The line moved, so a later commit can have fixed the problem already. Verify the current file. Do not assume either answer.

Also remove these items:

- A comment that you wrote on your own pull request. Your earlier reply is not new feedback.
- Bot output that asks for nothing, such as a coverage table or a deployment link.
- A comment that you answered in a thread reply in this session.

## Step 3: Read each comment against the code as it is now

A review comment describes the code as it was when the reviewer wrote the comment. Before you judge the comment, open the file at the path in the comment and read the code that is there **now**. A later push can have fixed the problem, or moved it to a place that the comment does not name.

Put comments that make the same point on different lines into one group. A group gets one decision and one fix, and then a reply on each thread.

## Step 4: Triage with the user. Do not start a fix.

Present one table, then stop:

| # | Thread | file:line | What the reviewer asks | Your assessment | Proposed |
|---|---|---|---|---|---|

`Proposed` is one of these four values:

- **Fix.** The comment is correct, and the change belongs in this pull request.
- **Defer.** The finding is real, but it is outside the scope of this pull request. Open a GitHub issue with `/issue-create`, and put the issue link in the reply.
- **Decline.** The comment rests on an incorrect reading, or the current behavior is deliberate. Give the reason and the `file:line` that shows it.
- **Already fixed.** A later commit resolved it. Give the commit or the current line.

Your assessment is your honest opinion. It includes "the reviewer is correct and I was wrong". Do not choose Fix to agree with the reviewer. Do not choose Decline to avoid work. An incorrect Decline costs the reviewer a second round.

**The user decides.** Apply nothing until the user answers. Two rules limit the triage:

- **Never defer a Critical finding.**
- If the code of the finding is already inside the scope of this pull request, fix it here. Do not open an issue for it.

## Step 5: Apply the fixes that the user accepts

Make one commit for each logical fix. Use the commit message convention of the repository, usually `type(scope): description`. **Never name the review round in a commit message.** State what the code now does.

Run the checks that cover what you touched before you push. Read `package.json`, the `Makefile`, or the CI workflow to find the commands of the repository. Run the full suite if the change reaches the load-bearing domain, the schema, or a shared package.

If a fix touches the load-bearing domain of the repository, run the specialist reviewer for that domain again on the new diff. A fix that a person makes under review pressure is exactly where a new defect enters.

```bash
git push
```

## Step 6: Answer each thread

Each comment that you collected gets an answer, and this includes each comment that you declined. Silence reads as "ignored", and it costs the reviewer a second read to find out.

Write each reply body to a JSON file with the Write tool, because the tool escapes each string
for you. A reply that contains a backtick or a single quotation mark breaks an inline
`-f body='...'` argument.

```json
{ "body": "Fixed in a1b2c3d. The null check moved into `isLateFeeEligible()`." }
```

```bash
# Reply inside the thread, so that the reply stays threaded
gh api repos/{owner}/{repo}/pulls/<PR>/comments/<comment_databaseId>/replies \
  --input <path-to-reply-json>
```

Keep each reply to one or two sentences:

- **Fixed.** Give what changed and where: "Fixed in a1b2c3d. The null check moved into `isLateFeeEligible()` (`src/late-fees.ts:44`)."
- **Deferred.** Give the issue link and the reason that the fix is not in this pull request.
- **Declined.** Give the reason and the `file:line` that supports it.
- **Already fixed.** Give the commit that fixed it.

**Do not resolve a thread that you replied to**, unless the user asks you to. The reviewer resolves their own comment. If you resolve it, you remove their opportunity to disagree.

## Step 7: Do not change the pull request description

**The description states the end state of the diff. It does not state the history of the review.** The `pr-create` skill applies this rule when it opens the pull request, and this skill is the most frequent place where the rule fails.

Never add an "Addressed review comments" section, a changelog for each round, a list of what round two changed, or a note that a reviewer asked for something.

If a fix changed what the pull request does, such as a new endpoint, a behavior that you removed, or a different migration, write the description again from the current diff with `/pr-create <PR_URL>`. That command writes the description as if the branch were the first commit. If the fix did not change what the pull request does, do not touch the description.

The same rule applies to the QA Check Report comment. If HEAD moved, run `/qa-check` again and post a new comment. Never edit the old comment to look like it covered the new code.

## Step 8: Report

Print the pull request URL, one line for each comment with its decision and its outcome, each issue that you opened, and the push state of the branch. If anything stays open, such as a comment that the user did not decide or a check that fails, say so plainly. Do not imply that the loop is complete.

## Quality checklist

- [ ] You read all three comment surfaces: inline, top-level, and review summaries
- [ ] You skipped each resolved thread, and verified each outdated thread against the current file
- [ ] You read each comment against the code as it is **now**
- [ ] You presented the triage table, and **the user decided** before you made any edit
- [ ] No Critical finding is deferred. In-scope code is fixed here
- [ ] You ran the checks for what you touched
- [ ] You ran the domain reviewer again if a fix touched the load-bearing domain
- [ ] Each comment that you collected has a reply, and this includes each decline
- [ ] You wrote each reply to a file, and did not put it in the shell command
- [ ] You left the threads unresolved, for the reviewer to close
- [ ] **The pull request description did not change.** It has no review narration and no changelog
- [ ] You posted a new `/qa-check` comment if HEAD moved
