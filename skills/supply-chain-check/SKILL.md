---
name: supply-chain-check
version: 1.0.0
description: |
  Single-command supply chain security audit. Scans for compromised packages,
  dangerous version ranges, lock file issues, CVEs, typosquatting, and local
  IOC artifacts. Wraps npm audit + active threat heuristics.
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

---

## Check 1: Known Compromised Packages

Search `package.json`, `package-lock.json`, `yarn.lock`, and `pnpm-lock.yaml` for any of these known-compromised package@version pairs:

| Package | Compromised Versions | Date | Advisory |
|---------|---------------------|------|----------|
| axios | 1.14.1, 0.30.4 | 2026-03-31 | RAT via plain-crypto-js dependency |
| plain-crypto-js | 4.2.0, 4.2.1 | 2026-03-30 | Typosquat of crypto-js, deploys multi-stage RAT |
| event-stream | 3.3.6 | 2018-11-26 | Cryptocurrency wallet theft via flatmap-stream |
| ua-parser-js | 0.7.29, 0.8.0, 1.0.0 | 2021-10-22 | Cryptominer + password stealer |
| coa | 2.0.3, 2.0.4, 2.1.1, 2.1.3, 3.0.1, 3.1.3 | 2021-11-04 | Credential harvester |
| rc | 1.2.9, 1.3.9, 2.3.9 | 2021-11-04 | Credential harvester |
| colors | 1.4.1, 1.4.2 | 2022-01-08 | Infinite loop protest-ware |
| faker | 6.6.6 | 2022-01-05 | Infinite loop protest-ware |
| node-ipc | 10.1.1, 10.1.2, 10.1.3, 11.0.0, 9.2.2 | 2022-03-15 | Peacenotwar — overwrites files on Russian/Belarusian IPs |
| es5-ext | 0.10.63 | 2024-03-09 | Protest-ware with network beacon |

Use `grep` to search lock files and package.json for exact package name + version matches. If ANY match is found, set risk level to **COMPROMISED** and stop — this is an active incident.

---

## Check 2: npm audit

If a `package.json` exists in the project root, run:

```bash
npm audit --json 2>/dev/null || echo '{"error": "npm audit failed or no package-lock.json"}'
```

Parse the JSON output. Report:
- Total vulnerabilities by severity (low/moderate/high/critical)
- For HIGH and CRITICAL: package name, version, vulnerability title, advisory URL
- If npm audit fails (no lock file, no node_modules), note this as a gap

---

## Check 3: Dangerous Version Ranges

Read `package.json` and check every dependency in `dependencies` and `devDependencies`:
- Flag any dependency using caret (`^`) or tilde (`~`) ranges — these auto-resolve to newer versions which may be compromised
- Especially flag ranges where the current latest on npm could be a compromised version
- Recommend pinning exact versions for all direct dependencies
- Note: `*`, `latest`, or empty version strings are CRITICAL flags

---

## Check 4: Lock File Integrity

Check:
1. Does a lock file exist? (`package-lock.json`, `yarn.lock`, or `pnpm-lock.yaml`)
2. Is it committed to git? Run: `git ls-files package-lock.json yarn.lock pnpm-lock.yaml 2>/dev/null`
3. Is it in `.gitignore`? Run: `grep -E 'package-lock|yarn.lock|pnpm-lock' .gitignore 2>/dev/null`

Flag:
- No lock file = **CRITICAL** (fresh installs resolve to latest, potentially compromised versions)
- Lock file exists but not committed = **HIGH** (each developer gets different versions)
- Lock file in .gitignore = **CRITICAL** (intentionally bypassing version pinning)

---

## Check 5: Typosquatting Detection

Read all dependency names from `package.json` (both `dependencies` and `devDependencies`). For each, check if the name is suspiciously similar to a well-known package. Common patterns:

- Extra/missing hyphens: `plain-crypto-js` vs `crypto-js`
- Character substitution: `axois` vs `axios`, `lodash-es` vs `1odash-es`
- Scope impersonation: `@types/reacct` vs `@types/react`
- Prefix/suffix additions: `express-helper-utils` mimicking `express`

Flag any dependency you don't recognize as a well-known package. When in doubt, check if the package has >1000 weekly downloads on npm by running:
```bash
npm view <package-name> --json 2>/dev/null | grep -A1 '"weekly"'
```

---

## Check 6: Phantom Dependencies

Compare dependencies declared in `package.json` against what's resolved in the lock file:
1. Read `package.json` — extract all declared dependency names
2. Read lock file — extract all top-level resolved packages
3. Flag any resolved package that:
   - Doesn't trace back to a declared dependency's dependency tree
   - Was added to the lock file without a corresponding `package.json` change (check `git diff` if available)
   - Has a name that appears typosquatted (cross-reference with Check 5)

---

## Check 7: Suspicious Install Scripts

Check for lifecycle scripts in direct dependencies that could execute malicious code:

```bash
# Check project's own package.json
grep -E '"(preinstall|postinstall|preuninstall|postuninstall)"' package.json 2>/dev/null

# Check direct dependencies in node_modules (if they exist)
for dep in $(cat package.json | grep -oP '"[^"]+"\s*:' | head -50 | tr -d '":'); do
  if [ -f "node_modules/$dep/package.json" ]; then
    scripts=$(grep -E '"(preinstall|postinstall)"' "node_modules/$dep/package.json" 2>/dev/null)
    if [ -n "$scripts" ]; then
      echo "FOUND in $dep: $scripts"
    fi
  fi
done
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

For any dependency flagged in checks 1-8, verify it has a legitimate release:

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

Check the local machine for known indicators of compromise from recent supply chain attacks:

**macOS:**
```bash
# Axios RAT dropper path
ls -la /Library/Caches/com.apple.act.mond 2>/dev/null

# Suspicious hidden files in tmp
ls -la /private/tmp/.* 2>/dev/null | grep -v '^\.\.$' | grep -v '^\.$'

# Check for ad-hoc signed binaries in tmp
find /private/tmp -name ".*" -perm +111 2>/dev/null
```

**Cross-platform:**
```bash
# Check for suspicious processes (axios RAT beacons every 60s)
ps aux | grep -i 'com.apple.act' 2>/dev/null
ps aux | grep -i 'ld.py' 2>/dev/null

# Check for the distinctive fake User-Agent in recent network activity
grep -r 'msie 8.0.*windows nt 5.1.*trident/4.0' /var/log/ 2>/dev/null | head -5
```

Flag any artifacts found as **COMPROMISED** — this means the RAT has already been deployed.

---

## Output

After running all 10 checks, produce this report:

```
## Supply Chain Security Report

### Risk Level: [CLEAN / WARNING / CRITICAL / COMPROMISED]

### Known Compromised Packages
- [results from Check 1]

### npm audit
- [results from Check 2]

### Version Range Risks
- [results from Check 3]

### Lock File Status
- [results from Check 4]

### Suspicious Patterns
- Typosquatting: [Check 5 results]
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
- **CRITICAL**: Known-compromised version resolvable via caret range, no lock file on production project, typosquatted dependency detected, suspicious install scripts
- **COMPROMISED**: Known-compromised package installed, IOC artifacts found on machine

### Important Notes

- Be specific. "Pin your dependencies" is useless. "Pin `axios` from `^1.7.9` to `1.7.9` in package.json line 14" is actionable.
- If risk level is CRITICAL or COMPROMISED, lead with the emergency action items.
- For COMPROMISED findings: recommend immediately disconnecting from network, rotating all credentials accessible from the machine, and auditing recent git commits for unauthorized changes.
- This skill complements Trail of Bits' `supply-chain-risk-auditor` which handles strategic dependency risk profiling (maintainer count, abandonment risk, CVE history). This skill focuses on active threats and hygiene.
