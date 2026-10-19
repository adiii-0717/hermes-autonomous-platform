# HermesProject — Secret Scanning and Credential Exposure Guide

> **Document Version:** 1.1.0  
> **Last Updated:** October 14, 2026  
> **Tool Location:** [`scripts/scan_secrets.py`](scripts/scan_secrets.py)  
> **Test Suite:** [`tests/test_secret_scanner.py`](tests/test_secret_scanner.py) (15/15 Unit Tests Passing)

---

## 1. Overview & Security Philosophy

The **HermesProject Secret Scanner** (`scripts/scan_secrets.py`) is an autonomous security auditing utility engineered to detect exposed API keys, access tokens, cryptographic private keys, and hardcoded secrets across local Git repositories, working trees, staged commits, and historical revisions.

### Core Architectural Guarantees
1. **Zero Secret Disclosure:** The scanner **never** prints, logs, or exports plain-text credentials, key fragments, or authorization headers. Findings are reported exclusively using safe metadata: rule category, file path, line number, token character length, and a truncated SHA-256 fingerprint (`sha256:7f83b1...c4b1`).
2. **Deterministic Overlap Resolution:** Specific provider signatures (e.g. APInex, Anthropic, Groq, Google, GitHub, AWS, Cryptographic Private Keys) are prioritized over generic wrappers (e.g. `Bearer <token>` or `api_key = "..."`), eliminating duplicate or misattributed alerts.
3. **Token-Intrinsic Synthetic Classification:** The scanner strictly rejects naive line-level or filename-level whitelisting. A realistic, high-entropy credential is **never** classified as `SYNTHETIC_MOCK` merely because its line or context contains words such as `example`, `test`, `mock`, `sample`, or `assert`, or because it resides in a test file, documentation snippet, or scanner/redaction regex file. Only token-intrinsic evidence (explicit template strings, repetitive character masks, parameter expansions `${...}`, template variables `{{...}}`) can establish synthetic status.
4. **Demonstrable Public Documentation Key Verification:** The classification `PUBLIC_DOC_KEY` is reserved strictly for verifiable public client-side documentation search keys (specifically Algolia DocSearch 32-character hexadecimal search keys inside Docusaurus configuration files). Arbitrary credentials or provider keys occurring in documentation configurations continue to alert as `SUSPICIOUS_CREDENTIAL`.
5. **Comprehensive Git History Coverage:** Historical scans inspect all reachable branches, tags, and commits using `git log --all -p -U0 --no-merges`, with automatic shallow clone detection.
6. **Data Isolation & Privacy Protection:** Untracked private session databases (`.sessions_db.json`), test databases (`books.db`), generated user applications (`workspace/`), and upstream Git backups (`hermes-agent/.git_upstream_backup/`) are strictly protected from read operations during untracked scans.

---

## 2. Supported Detection Patterns & Priority Hierarchy

The scanner evaluates content using a prioritized rule engine. When multiple rules match overlapping character spans on a single line, the higher-priority rule claims the span:

| Priority | Rule ID | Category Name | Target Pattern & Signature |
| :---: | :--- | :--- | :--- |
| **100** | `apinex_key` | APInex API Key | `\bsk-apx[a-zA-Z0-9_-]{16,}\b` |
| **100** | `anthropic_key` | Anthropic API Key | `\bsk-ant-(?:api\d\d-)?[a-zA-Z0-9_-]{20,}\b` |
| **100** | `groq_key` | Groq API Key | `\bgsk_[a-zA-Z0-9_-]{20,}\b` |
| **100** | `google_api_key` | Google Cloud / Gemini API Key | `\bAIza[0-9A-Za-z\-_]{35}\b` |
| **100** | `github_token` | GitHub Personal Access Token | `\b(?:ghp\|gho\|ghu\|ghs\|ghr\|github_pat)_[a-zA-Z0-9_]{16,}\b` |
| **100** | `aws_access_key` | AWS Access Key ID | `\b(?:AKIA\|ABIA\|ACCA\|ASIA)[0-9A-Z]{16}\b` |
| **100** | `private_key_block` | Cryptographic Private Key | `-----BEGIN (?:[A-Z0-9_\- ]+)?PRIVATE KEY(?: BLOCK)?-----` |
| **90** | `openai_key` | OpenAI API Key | `\bsk-(?:proj-\|live-\|svcacct-\|or-v\d-)?[a-zA-Z0-9_-]{20,}\b` |
| **50** | `bearer_token` | Generic Bearer Token | `\b[Bb]earer\s+([a-zA-Z0-9_\-\.\+/=]{25,})\b` |
| **10** | `hardcoded_secret_assignment` | Hardcoded Secret Assignment | `(?i)\b[a-zA-Z0-9_]*(?:api[_-]?key\|client[_-]?secret\|(?:auth\|access)[_-]?token\|secret[_-]?key\|password\|passwd\|pwd)\b\s*[:=]\s*["']([^"'\r\n\t ]{8,})["']` |

### Special Pattern Capabilities
- **Private Key Blocks:** Captures all PEM and PGP private key headers (`RSA`, `OPENSSH`, `EC`, `DSA`, `ENCRYPTED`, `PGP PRIVATE KEY BLOCK`). Only the header marker is recorded; private key body material is never printed or exported.
- **Complex Passwords & Tokens:** The assignment rule allows complex passwords containing symbols and punctuation (`!@#$%^&*()_+-=[]{}|;:,.<>?`) while strictly bounding tokens by quotes and excluding whitespace and newlines.
- **Full Base64 Bearer Tokens:** Supports standard JWT and base64url/base64 characters including `+`, `/`, `=`, `.`, `_`, `-`.

---

## 3. Finding Classifications & Decision Tree

Findings are categorized into three distinct classifications based on token-intrinsic evidence:

```
[Match Detected]
       │
       ├── Matches exact known template string (e.g. 'your_apinex_api_key_here')? ────► [SYNTHETIC_MOCK]
       ├── Matches synthetic mask / sequential pattern (e.g. 'xxxx...', '${VAR}')? ──► [SYNTHETIC_MOCK]
       ├── Matches token-intrinsic synthetic prefix/suffix (e.g. 'your-*', '*-dummy')? ─► [SYNTHETIC_MOCK]
       ├── In Docusaurus config AND strict 32-hex format AND under Algolia context? ───► [PUBLIC_DOC_KEY]
       ├── Short dictionary translation string inside i18n directory? ─────────────────► [SYNTHETIC_MOCK]
       └── All other matches (including realistic keys in test or doc files)? ─────────► [SUSPICIOUS_CREDENTIAL] (Exit 1)
```

1. **`SUSPICIOUS_CREDENTIAL` (Severity: Critical Alert):**
   - High-entropy, production-like token matching an active credential format without token-intrinsic synthetic markers.
   - Triggers an alert and causes the scanner CLI to exit with code `1`.
   - **Crucial Rule:** Realistic credentials embedded in test files (`tests/`), documentation snippets (`docs/`), or redaction source files (`server/utils/redact.py`) are classified as `SUSPICIOUS_CREDENTIAL` unless specific token-intrinsic synthetic evidence is established.
2. **`SYNTHETIC_MOCK` (Severity: Low / Informational):**
   - Recognized template variables (`your_api_key_here`, `dummy_secret`), bash parameter expansions (`${APINEX_KEY:-DEMO}`), repetitive character masks (`sk-proj-xxxxxxxx`), sequential alphabet/numeric test vectors (`1234567890`), or tokens containing hyphenated synthetic markers (`*-test-key`, `*-mock-token`).
3. **`PUBLIC_DOC_KEY` (Severity: Informational):**
   - Strict client-side search key verification:
     * File path must be a Docusaurus configuration (`docusaurus.config.ts` or `docusaurus.config.js`).
     * Context must be explicitly within an Algolia DocSearch block (`algolia:` or `apiKey:`).
     * Token must strictly match the 32-character hexadecimal format of public Algolia search-only keys (`^[a-f0-9]{32}$`).
     * Token must not match any private provider prefix (`sk-`, `AIza`, `ghp_`, `AKIA`, `gsk_`).
     * If these conditions are not met, the finding falls back to `SUSPICIOUS_CREDENTIAL`.

---

## 4. Operational Scopes & Command Line Interface

The scanner provides granular scope control:

```bash
# Scan all tracked files in Git index
python3 scripts/scan_secrets.py --tracked

# Scan uncommitted staged changes (pre-commit inspection)
python3 scripts/scan_secrets.py --staged

# Scan historical Git commit diffs across all reachable refs
python3 scripts/scan_secrets.py --history

# Scan safe untracked files (excluding databases, workspace, and backups)
python3 scripts/scan_secrets.py --untracked

# Comprehensive scan of all 4 scopes
python3 scripts/scan_secrets.py --all

# Export machine-readable report with zero plain-text secrets
python3 scripts/scan_secrets.py --all --json audit_report.json
```

---

## 5. Scope Coverage & Boundary Limitations

| Scope | Underlying Git Mechanism | Included Targets | Excluded Targets & Boundaries |
| :--- | :--- | :--- | :--- |
| **Tracked** | `git ls-files` | All 10,397 tracked files in repository index | Files > 5MB, binary files (null-byte detected) |
| **Staged** | `git diff --cached -U0` | All newly added lines (`+`) in index | Unstaged working tree edits |
| **History** | `git log --all -p -U0 --no-merges` | All commits reachable across all refs/branches | Unreachable dangling Git objects, merge commits (redundant diffs), external repos (`hermes-agent/.git_upstream_backup/`) |
| **Untracked** | `git ls-files --others --exclude-standard` | Uncommitted source, tests, and documentation | `.env`, `.sessions_db.json`, `books.db`, `workspace/`, `node_modules/`, `.git_upstream_backup/` |

---

## 6. Test Suite & Regression Verification

The test suite in [`tests/test_secret_scanner.py`](tests/test_secret_scanner.py) exercises 15 comprehensive test cases:

1. **`test_1_synthetic_credential_formats`**: Verifies detection across all 10 supported credential families.
2. **`test_2_malformed_and_incomplete_tokens`**: Verifies that truncated tokens, empty headers, and public keys do not alert.
3. **`test_3_overlapping_patterns_and_duplicate_findings`**: Verifies priority ordering across overlapping matches.
4. **`test_4_safe_redaction_terminal_and_json`**: Verifies zero disclosure in terminal and JSON outputs.
5. **`test_5_classifier_no_false_negatives_in_misleading_contexts`**: Verifies that realistic keys in misleading contexts (comments mentioning "example", test variable names `mock_key`, doc snippets, scanner regex definitions) alert as `SUSPICIOUS_CREDENTIAL`.
6. **`test_6_public_doc_key_strict_classification`**: Verifies 32-hex Algolia DocSearch key classification and rejection of provider keys in Docusaurus configs.
7. **`test_7_secrets_containing_complex_punctuation`**: Verifies detection of passwords and tokens with punctuation (`!@#$%^&*()_+-=[]{}|;:,.<>?`).
8. **`test_8_multiple_credentials_on_same_line`**: Verifies that multiple distinct credentials on one line are individually captured.
9. **`test_9_private_key_markers_and_multiline_safety`**: Verifies detection of RSA, OpenSSH, EC, DSA, Encrypted, and PGP private key headers without leaking key body.
10. **`test_10_historical_commit_secrets`**: Verifies detection of credentials committed in past revisions and later removed.
11. **`test_11_git_history_all_refs_and_shallow_detection`**: Verifies `--all` branch traversal and shallow clone status checking.
12. **`test_12_staged_changes_secrets`**: Verifies pre-commit interception of staged credentials.
13. **`test_13_binary_unreadable_and_multimatch_files`**: Verifies safe skipping of binary assets and complete indexing of multi-match files.
14. **`test_14_guarantee_no_real_credentials_in_output`**: Verifies the strict zero-leak invariant across all data structures and reports.
15. **`test_15_access_and_auth_token_assignment_regression`**: Verifies detection of both `access_token` and `auth_token` assignments across case variants (`ACCESS_TOKEN`, `access_token`) and delimiters (`access-token`, `auth-token`), rejects short tokens below 8 characters, enforces safe zero-leak output, and guarantees provider overlap priority.
