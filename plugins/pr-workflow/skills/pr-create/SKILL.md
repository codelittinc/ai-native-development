---
name: pr-create
version: 1.0.0
description: |
  Read the branch diff, write a pull request title and description, and open
  the pull request with the GitHub CLI. The description states the end state of
  the diff. It does not narrate the session: no "initially I", no "after review
  feedback", no changelog of earlier revisions. The skill reads the repository
  pull request template, checks that the branch is not behind the default
  branch, counts the changed files and proposes a split when the pull request
  is too large to review, and holds the description to a sentence and bullet
  budget. It also regenerates the title and description of a pull request that
  is already open.
  Use this skill for a straightforward pull request. Use /pr-create-reviewed
  when you want a review loop before a person sees the pull request.
  Triggers: "open a PR", "create a pull request", "write the PR description",
  "PR title and body", "update the PR description".
allowed-tools:
  - Read
  - Write
  - Bash
  - Grep
  - Glob
---

# PR Create

Read the branch diff. Write a title and a description. Open the pull request.

**Do you want the review loop?** `/pr-create-reviewed` opens the pull request as a draft, examines it with subagents that get only the diff, and marks it ready after you triage the findings. That skill uses steps 0 to 4 below for the title and the description, so the two skills always agree about a good description.

## Technical names in this document

This document uses Simplified Technical English (ASD-STE100). These technical names have no approved equivalent:

| Technical name | Meaning |
|---|---|
| Default branch | The branch that pull requests merge into, usually `main` or `master` |
| Diff | The set of lines that the branch adds, changes, and removes |
| Stacked pull requests | Two or more small pull requests, where each one starts from the branch of the previous one |
| Trailer | A line at the end of a description that records the tool that wrote it |

## Usage

```bash
/pr-create                 # the current branch
/pr-create BRANCH_NAME
/pr-create <PR_URL>        # write the title and description of a pull request that is open
```

---

## Step 0: Find the mode

If the argument agrees with `github.com/*/pull/*`, the mode is **UPDATE**. Read the pull request and examine its head branch:

```bash
gh pr view <PR_URL> --json number,headRefName,baseRefName,title,body,isDraft
```

If the argument is different, the mode is **CREATE**. Use the named branch, or the current branch.

## Step 0.5: Find the description structure

```bash
cat .github/PULL_REQUEST_TEMPLATE.md 2>/dev/null   # read this again on each run
```

If the repository has a template, its headings, its order, and its checkbox blocks **are** the necessary structure. The `gh pr create --body` command does not apply the template for you. If the repository has no template, use the Summary, Changes, Implementation Details, Test Plan, and Notes structure from `references/description-guide.md`.

For each of the two conditions, `references/description-guide.md` controls the content **inside** the sections.

## Step 1: Examine the branch state and the size

Find the default branch first. Do not assume the name `main`:

```bash
BASE=$(gh repo view --json defaultBranchRef --jq .defaultBranchRef.name)
git fetch origin "$BASE"
git merge-base --is-ancestor "origin/$BASE" HEAD   # exit code 1 shows that the branch is behind
git log "$BASE..HEAD" --oneline
git diff "$BASE...HEAD" --stat
git diff "$BASE...HEAD"
```

**If the branch is behind** (exit code 1), show `git log HEAD..origin/$BASE --oneline`. Recommend `git rebase origin/$BASE`. Ask the user before you continue. Stop if the answer is no.

**Examine the size.** A reviewer approves a pull request that is too large to hold in the mind:

```bash
git diff --name-only "$BASE...HEAD" \
  | grep -vE '(package-lock\.json|pnpm-lock\.yaml|yarn\.lock|go\.sum|Cargo\.lock|/generated/|\.snap$)' \
  | wc -l
```

For more than **20** files, list them in groups by boundary: schema and migration, backend, frontend, background jobs, shared packages, documentation. Propose a split into stacked pull requests along the seam that needs the least rework. Ask the user to split or to continue.

This proposal is **advice**. The user decides. A split is usually correct when the groups merge independently. A split is usually incorrect when a schema change and its only consumer land in different pull requests.

**Find the issue number** from the branch name (`123-desc`, `issue-123`) or from the commits (`#123`, `closes #123`). If you find one, read it with `gh issue view <N> --json title,body,labels`. If you find none, continue without one.

## Step 2: Examine the diff

- Put the change in a category: feature, fix, refactor, infrastructure, test, or documentation.
- Record the directories and packages that the change touches, and if the change stays in one area.
- Record the **reason**: the problem, the behavior that changes, and the cause of the work.
- **Record the domain risk.** Each repository has a load-bearing domain where a defect is expensive: money movement, authentication and authorization, personal data, data migration, or physical control. Read the root `CLAUDE.md`, `AGENTS.md`, `CONTRIBUTING.md`, or `REVIEW.md` to find which domain this repository protects. If the diff touches it, say so in the description, and name the rules that the change must obey.
- **Examine the dependencies.** If a manifest or a lock file changed, run `/supply-chain-check` if that plugin is installed, and state the result in the description. A test suite that passes gives no evidence about the source of a dependency.

## Step 3: Write the title

Use `type(scope): description`. The types are `feat`, `fix`, `refactor`, `test`, `chore`, and `docs`. The scope is the domain or the package. Omit the scope when the change is truly cross-cutting. Use the imperative. Keep the title below 70 characters. Add the `(#123)` suffix when an issue exists.

Correct: `fix(billing): uncoded charges are not eligible for a late fee (#34)`

Incorrect: `Update late fees`

Incorrect: `fix(billing): updated the late fee handler and the charge code validation so that…`

## Step 4: Write the description

### State the end state. Do not narrate the journey.

**The description states the diff as it is now, as if it were the first and only commit.** A reviewer examines the code in front of them. The path that you took competes with the change for their attention. This is the most frequent defect in a generated description. Obey it as a rule, not as a preference.

Never write these items:

- "Initially I …", "after review feedback …", "as discussed …", "per the QA report …"
- "changed X, then went back to Y" — state Y, because X does not exist
- An "Addressed review comments" section, a per-round changelog, or a reference to an earlier revision of this pull request
- A defense of a decision that no reviewer questioned
- A record of *your* process: the files that you searched, the options that you rejected

A decision belongs in the description only when a reviewer who reads the final code asks "why this way?". Then give the decision and its reason in one line. Do not give the deliberation.

### Budgets

| Section | Budget |
|---|---|
| Summary | The issue link and **3 sentences or fewer**: what changes, and why |
| Changes | **12 bullets or fewer**, in groups by area |
| Implementation Details | Only a decision that is not obvious. **3 bullets or fewer.** Omit the section if there is none |
| Test Plan | The commands that you ran, and the manual steps |
| **Summary and Changes together** | **600 words or fewer** — a limit, not a target |

The Test Plan and the Notes are additional to the 600 words. A necessary section must not compete with the prose for space.

**The sentence limit and the bullet limit do the work.** Three sentences and twelve bullets keep a description easy to scan. The word count only finds a description that started to narrate. A change in one area is usually near 250 words. A change across many areas is usually near 450 words. If you reach 600 words with twelve necessary bullets, the pull request is probably too large for one review. That is the true finding. See the size check in Step 1. Never make good prose worse to meet a number.

**The bullet test: a bullet is necessary only if a reviewer examines the code differently because of it.** Do not repeat what the diff shows, such as "renamed X" or "added a test for Y", unless the bullet sends the reviewer to a different place. Remove a section instead of adding filler.

### Necessary content

- **The issue link** on the first line of the Summary: `Closes #123` closes the issue on merge, and `Refs #123` does not. Omit the line when no issue exists. Never invent an issue number.
- **The Test Plan**: the commands that you ran. Use the commands of this repository, and read `package.json`, `Makefile`, or the CI workflow to find them. For a change in the load-bearing domain, name the invariant checks.
- **The trailer**: put `🤖 Generated with [Claude Code](https://claude.com/claude-code)` last.

## Step 5: Run the quality checks, then open the pull request

Show the title and the description. Ask for approval. After the user approves:

**Run `/qa-check` before the push, not after.** If the `qa-check` plugin is installed and the repository has a `.qa-check-required` file, a PreToolUse hook stops `git push` until a report exists for HEAD. A push before the check fails. Keep the report, because Step 6 posts it.

```bash
git push -u origin <branch>
gh pr create --title "<title>" --body-file <path-to-body>
```

Write the description to a file with the Write tool, then use `--body-file`. A description that contains a backtick or a single quotation mark breaks an inline `--body` argument.

For the **UPDATE** mode, read the section below.

## Step 6: Post the QA Check Report as a comment

Post the report as a **comment**, not in the description. The report is long, and a description that starts with it hides the change:

```bash
gh pr comment <N> --body-file <path-to-report>   # the heading must be exactly: ## QA Check Report
```

Never invent a report. Never post a report from a commit that is different from HEAD.

Report the pull request URL when you are done.

### The UPDATE mode

**Write the description again from the current diff. Never add to the description that exists.** Text that you add is how a description collects a changelog of the session. Steps 1 to 4 make a new description of the branch as it is now.

Keep only the content that this skill did not write: bot sections such as coverage tables and deployment links, and reviewer notes that a person added. Copy them exactly, after the generated content, with two empty lines between them.

```bash
gh pr edit <N> --title "<title>" --body-file <path-to-body>
```

## Quality checklist

- [ ] You read `.github/PULL_REQUEST_TEMPLATE.md` again on this run, and used its structure
- [ ] You found the default branch with `gh repo view`, and did not assume the name `main`
- [ ] The issue link is present (`Closes #N` or `Refs #N`) when an issue exists, and absent when none exists
- [ ] You compared the branch against the default branch, and asked the user if the branch is behind
- [ ] You counted the files, and proposed a split for more than 20 files
- [ ] The title uses `type(scope): description`, the imperative, and fewer than 70 characters
- [ ] **The description has no session narration**: no "initially", no "after feedback", no changelog
- [ ] The Summary has 3 sentences or fewer. The Changes section has 12 bullets or fewer. Each bullet passes the bullet test
- [ ] The description states the load-bearing domain when the diff touches it
- [ ] The Test Plan lists the commands that you ran
- [ ] You ran `/qa-check` **before** the push, if the plugin is installed
- [ ] You ran `/supply-chain-check` and stated the result, if a manifest or a lock file changed
- [ ] You posted `## QA Check Report` as a comment
- [ ] You wrote the description to a file and used `--body-file`
- [ ] The Claude Code trailer is last

## Reference

`references/description-guide.md` gives the section-by-section writing guidance, the default structure, the anti-patterns, and worked examples.
