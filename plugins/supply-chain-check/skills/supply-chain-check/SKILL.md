---
name: supply-chain-check
version: 1.1.0
description: |
  Single-command supply chain security audit. Queries live advisory sources
  (npm audit, OSV.dev, GitHub Advisory Database) and scans for dangerous
  version ranges, lock file issues, typosquatting, slopsquatting/hallucinated
  dependencies, and local IOC artifacts. Wraps npm audit + active threat
  heuristics.
  Triggers: "supply chain check", "dependency audit", "security scan",
  "check dependencies", "scan for vulnerabilities".
allowed-tools:
  - Read
  - Bash
  - Grep
  - Glob
---

# Supply Chain Security Check

You are a supply chain security auditor. Run all 10 checks below in order against the current project, then produce the structured report at the end.

Do NOT rely on any memorized or baked-in list of compromised packages. Static lists go stale within days and invite fabricated entries. Every compromised-package determination in this skill must come from a live advisory source queried at runtime (Check 1).

---

## Check 1: Live Advisory Check

**1a. npm audit.** If a `package.json` exists in the project root:

```bash
npm audit --json 2>/dev/null || echo '{"error": "npm audit failed or no package-lock.json"}'
```

Parse the JSON. Report total vulnerabilities by severity (low/moderate/high/critical). For HIGH and CRITICAL: package name, version, vulnerability title, advisory URL. If npm audit fails (no lock file, no node_modules), note this as a gap.

**1b. OSV.dev API.** For direct dependencies (and any package flagged by later checks), query OSV:

```bash
curl -s -X POST https://api.osv.dev/v1/querybatch \
  -d '{"queries": [{"package": {"name": "<pkg>", "ecosystem": "npm"}, "version": "<installed-version>"}]}'
# detail on any hit: POST the same shape to https://api.osv.dev/v1/query
```

**1c. GitHub Advisory Database.** For anything suspicious:

```bash
gh api "/advisories?ecosystem=npm&affects=<pkg>@<version>" 2>/dev/null
```

If ANY live source flags an installed package@version as malware or compromised, set risk level to **COMPROMISED** and stop — this is an active incident.

For attack-shape pattern recognition, see the table of documented past incidents in `references/incidents.md` — historical examples only, NOT current IOCs.

---

## Check 2: Dangerous Version Ranges

Read `package.json` and check every dependency in `dependencies` and `devDependencies`:
- Flag any dependency using caret (`^`) or tilde (`~`) ranges — these auto-resolve to newer versions, which is exactly how advisory-flagged releases spread
- Especially flag ranges that would resolve to a version flagged in Check 1
- Recommend pinning exact versions for all direct dependencies
- Note: `*`, `latest`, or empty version strings are CRITICAL flags

---

## Check 3: Lock File Integrity

Check:
1. Does a lock file exist? (`package-lock.json`, `yarn.lock`, or `pnpm-lock.yaml`)
2. Is it committed to git? Run: `git ls-files package-lock.json yarn.lock pnpm-lock.yaml 2>/dev/null`
3. Is it in `.gitignore`? Run: `grep -E 'package-lock|yarn.lock|pnpm-lock' .gitignore 2>/dev/null`

Flag:
- No lock file = **CRITICAL** (fresh installs resolve to latest, potentially compromised versions)
- Lock file exists but not committed = **HIGH** (each developer gets different versions)
- Lock file in .gitignore = **CRITICAL** (intentionally bypassing version pinning)

---

## Check 4: Typosquatting Detection

Read all dependency names from `package.json` (both `dependencies` and `devDependencies`). For each, check if the name is suspiciously similar to a well-known package. Common patterns:

- Character substitution: `axois` vs `axios`, digit-for-letter swaps like `1odash` vs `lodash`
- Extra/missing hyphens: `cryptojs` vs `crypto-js`
- Scope impersonation: `@types/reacct` vs `@types/react`
- Prefix/suffix additions: `express-helper-utils` mimicking `express`

Flag any dependency you don't recognize as a well-known package. When in doubt, check download volume via the npm downloads API:
```bash
curl -s https://api.npmjs.org/downloads/point/last-week/<package-name>
```

---

## Check 5: Slopsquatting / Hallucinated Dependencies

LLMs hallucinate plausible package names; attackers register those names and wait. This moved from theoretical to actively exploited (Cloud Security Alliance research note, 2026-04-19): the malicious npm package `unused-imports` was registered to catch hallucinations of `eslint-plugin-unused-imports` (~233 weekly downloads while security-held, Feb 2026), and `react-codeshift` (Jan 2026) followed the same playbook. The same note reproduced 127 hallucinated package names across 5 frontier models.

Identify recently added dependencies. When invoked from qa-check's dependency tripwire, use the new dependencies in the current diff; otherwise:

```bash
git log --since="30 days ago" -p -- package.json | grep '^\+ *"' | sort -u
```

For each new or recently added dependency, verify ALL of:

1. **Existence**: `npm view <pkg> name version --json`. A package imported in code but absent from the registry is a live registration opportunity for attackers — **CRITICAL**.
2. **Age**: `npm view <pkg> time.created`. Younger than 6 months → flag.
3. **Maintainer plausibility**: `npm view <pkg> maintainers repository.url`. Single unknown maintainer, no repository, empty README → flag.
4. **Download history**: `curl -s https://api.npmjs.org/downloads/point/last-month/<pkg>`. Downloads far below what the name's plausibility suggests → flag.
5. **Lockfile pinning**: resolved to an exact version in the lock file.
6. **Name proximity**: is the name a near-miss of a more popular package (`unused-imports` vs `eslint-plugin-unused-imports`)? Cross-reference Check 4.

Any new dependency that is unverifiable or newborn (fails 1 or 2) → **CRITICAL**. Failures of 3–6 → HIGH; escalate when several stack up.

---

## Check 6: Phantom Dependencies

Compare dependencies declared in `package.json` against what's resolved in the lock file:
1. Read `package.json` — extract all declared dependency names
2. Read lock file — extract all top-level resolved packages
3. Flag any resolved package that:
   - Doesn't trace back to a declared dependency's dependency tree
   - Was added to the lock file without a corresponding `package.json` change (check `git diff` if available)
   - Has a name that appears typosquatted (cross-reference with Checks 4 and 5)

---

## Check 7: Suspicious Install Scripts

Check for lifecycle scripts in direct dependencies that could execute malicious code:

```bash
# Project's own package.json
grep -E '"(preinstall|postinstall|preuninstall|postuninstall)"' package.json 2>/dev/null

# Installed dependencies (if node_modules exists) — list packages declaring install hooks
grep -lE '"(preinstall|postinstall)"' node_modules/*/package.json node_modules/@*/*/package.json 2>/dev/null
```

Flag scripts that contain:
- `curl`, `wget`, `powershell`, `osascript` (network downloads or system scripting)
- `base64`, `Buffer.from`, `atob` (encoding/obfuscation)
- `eval`, `Function(` (dynamic code execution)
- `child_process`, `exec`, `spawn` (shell execution)
- References to `/tmp/`, `/private/tmp/`, `%TEMP%`, `%PROGRAMDATA%` (temp file staging)
- `nohup`, `background`, `detach` (persistence)

---

## Check 8: Registry Anomalies

```bash
# Check for .npmrc files
cat .npmrc 2>/dev/null
cat ~/.npmrc 2>/dev/null

# Check for yarn config
cat .yarnrc 2>/dev/null
cat .yarnrc.yml 2>/dev/null
```

Flag:
- Any `registry=` pointing to something other than `https://registry.npmjs.org/`
- Any `@scope:registry=` entries (may be legitimate — note but don't auto-flag)
- Any `_authToken` or credentials in committed `.npmrc` files

---

## Check 9: Publication Pattern Checks

For any dependency flagged in checks 1–8, verify it has a legitimate release:

```bash
# Check if version has a corresponding GitHub tag
npm view <package>@<version> repository.url --json 2>/dev/null
# Then check: does a git tag exist for this version?
```

Flag if:
- The installed version has no corresponding GitHub release/tag
- The version was published very recently (within 48 hours) — check `npm view <package> time --json`
- The version was published by a different maintainer than usual — check `npm view <package> maintainers --json`

---

## Check 10: Local IOC Scan

Check the local machine for indicators of compromise. Do NOT use a memorized IOC list. Take concrete IOCs (file paths, process names, C2 domains) from the live advisories surfaced in Check 1 and search for those specifically. If no advisory names concrete IOCs, run only the generic heuristics below:

```bash
# Hidden executables staged in temp directories
find /tmp /private/tmp -maxdepth 1 -name ".*" -perm -u+x -type f 2>/dev/null

# Unexpected persistence (macOS)
ls -la ~/Library/LaunchAgents /Library/LaunchAgents /Library/LaunchDaemons 2>/dev/null

# Unexpected cron entries
crontab -l 2>/dev/null

# Recently modified shell startup files (rc-file persistence)
ls -la ~/.zshrc ~/.bashrc ~/.bash_profile ~/.profile 2>/dev/null
```

Flag anything you cannot explain. Any artifact matching a live advisory's IOCs = **COMPROMISED** — the payload has already run.

---

## Output

After running all 10 checks, produce this report:

```
## Supply Chain Security Report

### Risk Level: [CLEAN / WARNING / CRITICAL / COMPROMISED]

### Live Advisory Findings (npm audit + OSV.dev + GitHub Advisory)
- [results from Check 1]

### Version Range Risks
- [results from Check 2]

### Lock File Status
- [results from Check 3]

### Suspicious Patterns
- Typosquatting: [Check 4 results]
- Slopsquatting / hallucinated dependencies: [Check 5 results]
- Phantom dependencies: [Check 6 results]
- Install scripts: [Check 7 results]
- Registry: [Check 8 results]

### Publication Verification
- [results from Check 9]

### Local IOC Check
- [results from Check 10]

### Recommended Actions
1. [specific, actionable items ranked by severity]
```

### Risk Level Criteria

- **CLEAN**: All checks pass, no flags
- **WARNING**: Minor issues (some unpinned ranges, missing lock file for dev-only project)
- **CRITICAL**: Advisory-flagged version resolvable via caret range, no lock file on production project, typosquatted dependency detected, new dependency failing provenance checks (nonexistent, newborn, or name-proximate to a popular package), suspicious install scripts
- **COMPROMISED**: Live-advisory-flagged package installed, IOC artifacts found on machine

### Important Notes

- Be specific. "Pin your dependencies" is useless. "Pin `axios` from `^1.7.9` to `1.7.9` in package.json line 14" is actionable.
- If risk level is CRITICAL or COMPROMISED, lead with the emergency action items.
- For COMPROMISED findings: recommend immediately disconnecting from network, rotating all credentials accessible from the machine, and auditing recent git commits for unauthorized changes.
- Never report a package as compromised from memory or from the historical incidents in `references/incidents.md` — only from a live advisory queried during this run.
- This skill complements Trail of Bits' `supply-chain-risk-auditor` which handles strategic dependency risk profiling (maintainer count, abandonment risk, CVE history). This skill focuses on active threats and hygiene.
