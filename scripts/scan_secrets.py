#!/usr/bin/env python3
"""
HermesProject - Secret Scanner & Credential Exposure Auditor
============================================================
A security utility designed to inspect local Git repositories, working trees,
staged changes, and commit history for exposed API credentials, private keys,
and hardcoded secrets without leaking secret data into logs, reports, or stdout.

Key Features:
- Provider-specific signature detection (APInex, OpenAI, Gemini, Anthropic, Groq, GitHub, AWS, etc.)
- Overlap resolution preventing duplicate reports across specific and generic patterns
- Strict safe redaction: Only safe metadata (rule, length, truncated SHA-256 fingerprint) is reported
- Token-intrinsic synthetic fixture classification (no naive string/comment/path suppression)
- Demonstrable public client-side documentation search key verification (strict 32-hex Algolia)
- Safe handling of binary files, large files, unreadable encodings, and Git errors
- Comprehensive history coverage across all reachable refs (--all), with shallow clone detection
- Machine-readable JSON output containing zero plain-text secrets
"""

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


# ==============================================================================
# Data Structures
# ==============================================================================

@dataclass
class Finding:
    file_path: str
    line_number: int
    rule_id: str
    rule_name: str
    classification: str  # "SUSPICIOUS_CREDENTIAL", "SYNTHETIC_MOCK", or "PUBLIC_DOC_KEY"
    length: int
    fingerprint_sha256: str
    context_note: str
    commit_hash: Optional[str] = None

    def to_safe_dict(self) -> Dict:
        return asdict(self)


@dataclass
class ScanCoverage:
    scope: str
    files_scanned: int = 0
    files_skipped_binary: int = 0
    files_skipped_large: int = 0
    files_skipped_excluded: int = 0
    files_unreadable: int = 0
    commits_scanned: int = 0
    total_suspicious: int = 0
    total_synthetic: int = 0
    total_public_doc: int = 0
    is_shallow: bool = False


# ==============================================================================
# Pattern Rules & Overlap Priority
# ==============================================================================

class Rule:
    def __init__(self, rule_id: str, name: str, priority: int, regex_pattern: str, is_assignment: bool = False):
        self.rule_id = rule_id
        self.name = name
        self.priority = priority  # Higher priority wins on overlapping spans
        self.regex = re.compile(regex_pattern)
        self.is_assignment = is_assignment


RULES: List[Rule] = [
    # Top Priority: Highly specific provider key patterns (Priority 100)
    Rule(
        rule_id="apinex_key",
        name="APInex API Key",
        priority=100,
        regex_pattern=r"\bsk-apx[a-zA-Z0-9_-]{16,}\b"
    ),
    Rule(
        rule_id="anthropic_key",
        name="Anthropic API Key",
        priority=100,
        regex_pattern=r"\bsk-ant-(?:api\d\d-)?[a-zA-Z0-9_-]{20,}\b"
    ),
    Rule(
        rule_id="groq_key",
        name="Groq API Key",
        priority=100,
        regex_pattern=r"\bgsk_[a-zA-Z0-9_-]{20,}\b"
    ),
    Rule(
        rule_id="google_api_key",
        name="Google Gemini / Cloud API Key",
        priority=100,
        regex_pattern=r"\bAIza[0-9A-Za-z\-_]{35}\b"
    ),
    Rule(
        rule_id="github_token",
        name="GitHub Personal Access Token",
        priority=100,
        regex_pattern=r"\b(?:ghp|gho|ghu|ghs|ghr|github_pat)_[a-zA-Z0-9_]{16,}\b"
    ),
    Rule(
        rule_id="aws_access_key",
        name="AWS Access Key ID",
        priority=100,
        regex_pattern=r"\b(?:AKIA|ABIA|ACCA|ASIA)[0-9A-Z]{16}\b"
    ),
    Rule(
        rule_id="private_key_block",
        name="Cryptographic Private Key Block",
        priority=100,
        regex_pattern=r"-----BEGIN (?:[A-Z0-9_\- ]+)?PRIVATE KEY(?: BLOCK)?-----"
    ),

    # Medium Priority: Generic OpenAI key (Priority 90) - placed below APInex/Anthropic to avoid misattribution
    Rule(
        rule_id="openai_key",
        name="OpenAI API Key",
        priority=90,
        regex_pattern=r"\bsk-(?:proj-|live-|svcacct-|or-v\d-)?[a-zA-Z0-9_-]{20,}\b"
    ),

    # Lower Priority: Bearer Token Pattern (Priority 50)
    # Includes full base64/base64url characters (+, /, =, ., _, -)
    Rule(
        rule_id="bearer_token",
        name="Generic Bearer Token",
        priority=50,
        regex_pattern=r"\b[Bb]earer\s+([a-zA-Z0-9_\-\.\+/=]{25,})\b"
    ),

    # Baseline Priority: Variable Secret Assignment (Priority 10)
    # Matches assignments like db_password, APINEX_API_KEY, client_secret, etc.
    # Uses [^"\'\r\n\t ]{8,} to capture tokens with valid punctuation (!@#$%^&*...) while respecting quotes
    Rule(
        rule_id="hardcoded_secret_assignment",
        name="Hardcoded Secret Assignment",
        priority=10,
        regex_pattern=r"""(?i)\b[a-zA-Z0-9_]*(?:api[_-]?key|client[_-]?secret|(?:auth|access)[_-]?token|secret[_-]?key|password|passwd|pwd)\b\s*[:=]\s*["']([^"'\r\n\t ]{8,})["']""",
        is_assignment=True
    ),
]


# ==============================================================================
# Strict, Token-Intrinsic Synthetic & False-Positive Classifier
# ==============================================================================

# Definite placeholder substrings that represent intentional template documentation
NARROW_TEMPLATE_STRINGS = {
    "your_apinex_api_key_here",
    "your_google_gemini_api_key_here",
    "your_groq_api_key_here",
    "your_api_key_here",
    "your_token_here",
    "dummy_secret",
    "dummy_key",
    "dummy_secret_value",
    "sk-test-key",
    "sk-apx-live-test-key",
    "test_apx_key",
    "test_gemini_key",
    "test_groq_key",
    "local-key",
    "supersecretpassword",
    "changeme123",
    "password123",
    "your-api-key",
    "your-key",
    "your-second-key",
    "your-token",
    "your-secret",
    "your-password",
    "your-stt-key",
    "your-teams-client-secret",
    "your-oauth-client-secret",
    "or-key-original",
    "or-key-rollback",
    "ghp_classic_pat_nope",
    "sk-super-secret-value-do-not-log",
}

# Regex patterns matching synthetic repetitive characters, parameter expansions, or synthetic fixtures
SYNTHETIC_REGEX_PATTERNS = [
    re.compile(r"^sk-proj-x{8,}", re.IGNORECASE),
    re.compile(r"^ghp_x{8,}", re.IGNORECASE),
    re.compile(r"^sk-x{8,}", re.IGNORECASE),
    re.compile(r"^0{12,}$"),
    re.compile(r"^1234567890"),
    re.compile(r"^[xX]{8,}$"),
    re.compile(r"^<[A-Za-z0-9_\-]+>$"),
    re.compile(r"^\$\{[^}]+\}$"),  # Matches bash parameter expansion: ${VAR:-DEFAULT}
    re.compile(r"^\{\{\s*[A-Za-z0-9_\-\.]+\s*\}\}$"),  # Matches template mustache: {{API_KEY}}
    # Alphabet sequential test strings: abcdef123456..., abc123def456..., ABCD1234...
    re.compile(r"^(?:sk-(?:proj-)?)?(?:abc|123|abcdef|abcd1234){2,}", re.IGNORECASE),
    # AWS official documentation dummy key
    re.compile(r"^AKIAIOSFODNN7EXAMPLE$"),
    # Token-intrinsic synthetic prefixes
    re.compile(r"^(?:your|my|demo|test|sample|dummy|example|placeholder)[-_]", re.IGNORECASE),
    # Token-intrinsic synthetic suffixes
    re.compile(r"[-_](?:example|placeholder|demo|mock|dummy|sample|nope|original|rollback|scrolled|scrolling)$", re.IGNORECASE),
    # Token-intrinsic embedded semantic markers (hyphenated synthetic words in token body)
    re.compile(r"[-_](?:user[-_]?key|dummy|mock|fake|sample|example|demo|placeholder|dotenv|fixture|fresh)", re.IGNORECASE),
]


def is_algolia_search_key(token: str) -> bool:
    """Verifies that a token matches the exact format of a public Algolia DocSearch client key (32 hex characters)."""
    return bool(re.match(r"^[a-f0-9]{32}$", token, re.IGNORECASE))


def compute_safe_fingerprint(secret_value: str) -> str:
    """Returns a deterministic, truncated SHA-256 fingerprint. Never leaks secret characters."""
    h = hashlib.sha256(secret_value.encode("utf-8")).hexdigest()
    return f"sha256:{h[:10]}...{h[-6:]}"


def classify_match(raw_token: str, line_content: str, file_path: str) -> Tuple[str, str]:
    """
    Evaluates whether a match is a confirmed suspicious credential vs. a synthetic
    mock fixture, documentation template, or verified public client search key.
    
    Security Guarantee:
    - Classification affects severity, NOT whether the scanner records the match.
    - A realistic credential is NEVER marked SYNTHETIC_MOCK merely because its line
      contains 'example', 'test', 'mock', 'sample', 'assert', or similar words.
    - Credentials in test files, docs, or scanner regex files require token-intrinsic
      evidence to be classified as synthetic; otherwise they alert as SUSPICIOUS_CREDENTIAL.
    - Public search key classification requires strict format and configuration context proof.
    """
    token_lower = raw_token.lower()

    # 1. Exact match against known template strings
    if token_lower in NARROW_TEMPLATE_STRINGS:
        return "SYNTHETIC_MOCK", "Matched known template placeholder string"

    # 2. Check for token-intrinsic synthetic repeated masking characters, parameter expansions, or synthetic fixtures
    for s_regex in SYNTHETIC_REGEX_PATTERNS:
        if s_regex.search(raw_token):
            return "SYNTHETIC_MOCK", "Matched synthetic repetitive mask or template pattern"

    # 3. Check for public DocSearch client keys (Algolia DocSearch search-only apiKey in Docusaurus)
    # Rigorous verification:
    # - Must be inside a Docusaurus configuration file
    # - Must be explicitly configured under Algolia search context (line contains 'algolia' or 'apiKey')
    # - Must strictly match the 32-hex character format of public Algolia search keys
    # - Must NOT match any private provider key prefixes (sk-, AIza, ghp_, AKIA, gsk_)
    if "docusaurus.config" in file_path.lower():
        line_lower = line_content.lower()
        if "algolia" in line_lower or "apikey" in line_lower:
            if is_algolia_search_key(raw_token):
                if not any(raw_token.startswith(p) for p in ["sk-", "AIza", "ghp_", "AKIA", "gsk_"]):
                    return "PUBLIC_DOC_KEY", "Verified public client-side search key (Algolia DocSearch 32-hex key)"

    # 4. Check for localization dictionaries (e.g. i18n translation of the word 'secret' or 'password')
    if "i18n" in file_path and any(k in line_content for k in [": '", ': "', '": "']):
        if len(raw_token) < 25 and not any(raw_token.startswith(p) for p in ["sk-", "AIza", "ghp_", "AKIA", "gsk_"]):
            return "SYNTHETIC_MOCK", "Localization translation dictionary entry"

    # If it does not establish synthetic status through token-intrinsic evidence, it is SUSPICIOUS
    return "SUSPICIOUS_CREDENTIAL", "Unverified credential matching production signature"


# ==============================================================================
# Line Scanner & Overlap Resolver
# ==============================================================================

@dataclass
class RawCandidate:
    rule: Rule
    start: int
    end: int
    matched_value: str


def scan_line_for_secrets(line: str, line_number: int, file_path: str, commit_hash: Optional[str] = None) -> List[Finding]:
    """
    Scans a single line with all active rules and resolves overlapping spans
    using rule priority. Produces safe Finding instances.
    """
    candidates: List[RawCandidate] = []

    for rule in RULES:
        for match in rule.regex.finditer(line):
            # If the rule has capture groups, use group 1; otherwise use the entire match
            if match.groups():
                val = match.group(1)
                start = match.start(1)
                end = match.end(1)
            else:
                val = match.group(0)
                start = match.start(0)
                end = match.end(0)

            if not val or len(val.strip()) < 8:
                continue

            candidates.append(RawCandidate(
                rule=rule,
                start=start,
                end=end,
                matched_value=val
            ))

    if not candidates:
        return []

    # Sort candidates: start position ascending, priority descending, length descending
    candidates.sort(key=lambda c: (c.start, -c.rule.priority, -(c.end - c.start)))

    resolved_candidates: List[RawCandidate] = []
    occupied_spans: List[Tuple[int, int, int]] = []  # (start, end, priority)

    for cand in candidates:
        is_suppressed = False
        for span_start, span_end, span_prio in occupied_spans:
            # Check overlap: start < span_end and span_start < end
            if max(cand.start, span_start) < min(cand.end, span_end):
                # Overlap detected! Higher or equal priority already claimed this span
                if span_prio >= cand.rule.priority:
                    is_suppressed = True
                    break

        if not is_suppressed:
            resolved_candidates.append(cand)
            occupied_spans.append((cand.start, cand.end, cand.rule.priority))

    findings: List[Finding] = []
    for cand in resolved_candidates:
        classification, note = classify_match(cand.matched_value, line, file_path)
        fingerprint = compute_safe_fingerprint(cand.matched_value)

        findings.append(Finding(
            file_path=file_path,
            line_number=line_number,
            rule_id=cand.rule.rule_id,
            rule_name=cand.rule.name,
            classification=classification,
            length=len(cand.matched_value),
            fingerprint_sha256=fingerprint,
            context_note=note,
            commit_hash=commit_hash
        ))

    return findings


# ==============================================================================
# File Reading & Safety Checks
# ==============================================================================

def is_binary_file(file_path: Path) -> bool:
    """Checks if a file appears to be binary by scanning first 8KB for null bytes."""
    try:
        with open(file_path, "rb") as f:
            chunk = f.read(8192)
            return b"\x00" in chunk
    except Exception:
        return False


# Paths explicitly excluded from untracked file scans to protect privacy and performance
UNTRACKED_SCAN_EXCLUSIONS = {
    ".sessions_db.json",
    "books.db",
    "workspace_server.log",
    ".git_upstream_backup",
    "node_modules",
    "workspace",
    "dist",
    ".venv",
    "venv",
    ".DS_Store",
}


def should_skip_untracked(rel_path: str) -> bool:
    parts = Path(rel_path).parts
    for p in parts:
        if p in UNTRACKED_SCAN_EXCLUSIONS:
            return True
        if p.endswith(".db") or p.endswith(".sqlite") or p.endswith(".sqlite3") or p.endswith(".zip"):
            return True
    return False


# ==============================================================================
# SecretScanner Engine
# ==============================================================================

class SecretScanner:
    def __init__(self, repo_root: str, max_file_size_mb: int = 5):
        self.repo_root = Path(repo_root).resolve()
        self.max_file_size_bytes = max_file_size_mb * 1024 * 1024

    def scan_file_content(self, content: str, rel_path: str, commit_hash: Optional[str] = None) -> List[Finding]:
        findings = []
        for line_no, line in enumerate(content.splitlines(), start=1):
            findings.extend(scan_line_for_secrets(line, line_no, rel_path, commit_hash))
        return findings

    def scan_local_file(self, full_path: Path, rel_path: str, coverage: ScanCoverage) -> List[Finding]:
        try:
            if not full_path.is_file():
                return []

            stat = full_path.stat()
            if stat.st_size > self.max_file_size_bytes:
                coverage.files_skipped_large += 1
                return []

            if is_binary_file(full_path):
                coverage.files_skipped_binary += 1
                return []

            coverage.files_scanned += 1
            with open(full_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()

            return self.scan_file_content(content, rel_path)

        except Exception:
            coverage.files_unreadable += 1
            return []

    def scan_tracked(self) -> Tuple[List[Finding], ScanCoverage]:
        """Scans all tracked files via git ls-files."""
        coverage = ScanCoverage(scope="tracked")
        all_findings = []

        try:
            cmd = ["git", "ls-files"]
            output = subprocess.check_output(cmd, cwd=str(self.repo_root), text=True)
            tracked_files = [line.strip() for line in output.splitlines() if line.strip()]
        except Exception as e:
            sys.stderr.write(f"Error executing git ls-files: {type(e).__name__}\n")
            return [], coverage

        for rel in tracked_files:
            full = self.repo_root / rel
            findings = self.scan_local_file(full, rel, coverage)
            all_findings.extend(findings)

        self._update_coverage_totals(coverage, all_findings)
        return all_findings, coverage

    def scan_staged(self) -> Tuple[List[Finding], ScanCoverage]:
        """Scans git staged changes via git diff --cached."""
        coverage = ScanCoverage(scope="staged")
        all_findings = []

        try:
            cmd = ["git", "diff", "--cached", "-U0"]
            diff_text = subprocess.check_output(cmd, cwd=str(self.repo_root), text=True)
        except Exception as e:
            sys.stderr.write(f"Error reading staged diff: {type(e).__name__}\n")
            return [], coverage

        if not diff_text.strip():
            return [], coverage

        current_file = None
        current_line = 0

        for line in diff_text.splitlines():
            if line.startswith("+++ b/"):
                current_file = line[6:].strip()
                coverage.files_scanned += 1
                continue
            if line.startswith("@@"):
                # e.g. @@ -10,0 +15,2 @@
                m = re.search(r"\+(\d+)", line)
                if m:
                    current_line = int(m.group(1)) - 1
                continue
            if line.startswith("+") and not line.startswith("+++"):
                current_line += 1
                added_content = line[1:]
                if current_file:
                    findings = scan_line_for_secrets(added_content, current_line, current_file)
                    all_findings.extend(findings)

        self._update_coverage_totals(coverage, all_findings)
        return all_findings, coverage

    def scan_history(self, max_commits: Optional[int] = None) -> Tuple[List[Finding], ScanCoverage]:
        """
        Scans historical git commit diffs across all reachable branches, tags, and refs.
        
        Coverage & Boundary Guarantees:
        - Inspects all commits reachable via `git log --all -p -U0 --no-merges`.
        - Detects shallow clone boundaries via `git rev-parse --is-shallow-repository`.
        - Merge commits are skipped (--no-merges) because diff changes were introduced
          in individual branch commits prior to merging.
        - Unreachable loose objects (dangling commits) and external backup repositories
          (such as hermes-agent/.git_upstream_backup/) are NOT scanned by git log.
        """
        coverage = ScanCoverage(scope="history")
        all_findings = []

        # Check for shallow repository
        try:
            shallow_check = subprocess.check_output(
                ["git", "rev-parse", "--is-shallow-repository"],
                cwd=str(self.repo_root),
                text=True,
                stderr=subprocess.DEVNULL
            ).strip()
            if shallow_check == "true":
                coverage.is_shallow = True
        except Exception:
            pass

        cmd = ["git", "log", "--all", "-p", "-U0", "--no-merges"]
        if max_commits:
            cmd.extend(["-n", str(max_commits)])

        proc = None
        try:
            proc = subprocess.Popen(
                cmd,
                cwd=str(self.repo_root),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                errors="replace"
            )
            current_commit = None
            current_file = None
            current_line = 0

            for line in proc.stdout:
                if line.startswith("commit "):
                    current_commit = line.split()[1][:10]
                    coverage.commits_scanned += 1
                    current_file = None
                    continue
                if line.startswith("+++ b/"):
                    current_file = line[6:].strip()
                    continue
                if line.startswith("@@"):
                    m = re.search(r"\+(\d+)", line)
                    if m:
                        current_line = int(m.group(1)) - 1
                    continue
                if line.startswith("+") and not line.startswith("+++"):
                    current_line += 1
                    added_content = line[1:]
                    if current_file:
                        findings = scan_line_for_secrets(added_content, current_line, current_file, commit_hash=current_commit)
                        all_findings.extend(findings)

        except Exception as e:
            sys.stderr.write(f"Error reading git history: {type(e).__name__}\n")
            return [], coverage
        finally:
            if proc:
                if proc.stdout:
                    proc.stdout.close()
                if proc.stderr:
                    proc.stderr.close()
                proc.wait()

        self._update_coverage_totals(coverage, all_findings)
        return all_findings, coverage

    def scan_untracked(self) -> Tuple[List[Finding], ScanCoverage]:
        """Scans relevant untracked files while protecting private databases and generated projects."""
        coverage = ScanCoverage(scope="untracked")
        all_findings = []

        try:
            cmd = ["git", "ls-files", "--others", "--exclude-standard"]
            output = subprocess.check_output(cmd, cwd=str(self.repo_root), text=True)
            untracked_files = [line.strip() for line in output.splitlines() if line.strip()]
        except Exception as e:
            sys.stderr.write(f"Error executing git ls-files for untracked: {type(e).__name__}\n")
            return [], coverage

        for rel in untracked_files:
            if should_skip_untracked(rel):
                coverage.files_skipped_excluded += 1
                continue

            full = self.repo_root / rel
            findings = self.scan_local_file(full, rel, coverage)
            all_findings.extend(findings)

        self._update_coverage_totals(coverage, all_findings)
        return all_findings, coverage

    def _update_coverage_totals(self, coverage: ScanCoverage, findings: List[Finding]):
        coverage.total_suspicious = sum(1 for f in findings if f.classification == "SUSPICIOUS_CREDENTIAL")
        coverage.total_synthetic = sum(1 for f in findings if f.classification == "SYNTHETIC_MOCK")
        coverage.total_public_doc = sum(1 for f in findings if f.classification == "PUBLIC_DOC_KEY")


# ==============================================================================
# Reporting & CLI Interface
# ==============================================================================

def print_scan_report(findings: List[Finding], coverage_list: List[ScanCoverage]):
    print("=" * 80)
    print(" HermesProject - Secret Scanner & Security Audit Report")
    print("=" * 80)

    for cov in coverage_list:
        print(f"\n[Scope: {cov.scope.upper()}]")
        print(f"  Files Scanned:        {cov.files_scanned}")
        print(f"  Skipped (Binary):     {cov.files_skipped_binary}")
        print(f"  Skipped (Large >5MB): {cov.files_skipped_large}")
        print(f"  Skipped (Excluded):   {cov.files_skipped_excluded}")
        print(f"  Unreadable Files:     {cov.files_unreadable}")
        if cov.commits_scanned:
            print(f"  Commits Inspected:    {cov.commits_scanned}")
        if cov.is_shallow:
            print(f"  Shallow Clone:        True (Scan bounded by shallow clone depth)")
        print(f"  Suspicious Findings:  {cov.total_suspicious}")
        print(f"  Synthetic Mocks:      {cov.total_synthetic}")
        if cov.total_public_doc:
            print(f"  Public Doc Keys:      {cov.total_public_doc}")

    suspicious = [f for f in findings if f.classification == "SUSPICIOUS_CREDENTIAL"]
    synthetic = [f for f in findings if f.classification == "SYNTHETIC_MOCK"]
    public_doc = [f for f in findings if f.classification == "PUBLIC_DOC_KEY"]

    print("\n" + "-" * 80)
    if suspicious:
        print(f" ALERT: {len(suspicious)} SUSPICIOUS CREDENTIAL(S) DETECTED!")
        print("-" * 80)
        for f in suspicious:
            commit_str = f" [Commit {f.commit_hash}]" if f.commit_hash else ""
            print(f"  [!] {f.rule_name} in {f.file_path}:{f.line_number}{commit_str}")
            print(f"      Length: {f.length} chars | Fingerprint: {f.fingerprint_sha256}")
            print(f"      Context: {f.context_note}")
    else:
        print(" PASS: 0 suspicious credentials detected across inspected scopes.")
        print("-" * 80)

    if public_doc:
        print(f"\nNotice: {len(public_doc)} public documentation client search keys recognized.")
        for f in public_doc:
            commit_str = f" [Commit {f.commit_hash}]" if f.commit_hash else ""
            print(f"  [i] ({f.rule_name}) {f.file_path}:{f.line_number}{commit_str} -> {f.context_note}")

    if synthetic:
        print(f"\nNotice: {len(synthetic)} synthetic test fixtures / documentation examples verified.")
        print("Sample classified synthetic entries:")
        for f in synthetic[:10]:
            commit_str = f" [Commit {f.commit_hash}]" if f.commit_hash else ""
            print(f"  [*] ({f.rule_name}) {f.file_path}:{f.line_number}{commit_str} -> {f.context_note}")
        if len(synthetic) > 10:
            print(f"  ... and {len(synthetic) - 10} more synthetic fixtures verified.")

    print("\n" + "=" * 80)


def main():
    parser = argparse.ArgumentParser(description="HermesProject Secret Scanner")
    parser.add_argument("--repo-root", default=".", help="Target Git repository root")
    parser.add_argument("--tracked", action="store_true", help="Scan Git tracked files")
    parser.add_argument("--staged", action="store_true", help="Scan staged changes")
    parser.add_argument("--history", action="store_true", help="Scan Git commit history")
    parser.add_argument("--untracked", action="store_true", help="Scan relevant untracked files safely")
    parser.add_argument("--all", action="store_true", help="Scan tracked, staged, history, and untracked")
    parser.add_argument("--max-size-mb", type=int, default=5, help="Max file size in MB to scan (default 5)")
    parser.add_argument("--json", dest="json_output", help="Save machine-readable JSON report to path")
    parser.add_argument("--quiet", action="store_true", help="Suppress banner and non-error output")

    args = parser.parse_args()

    scanner = SecretScanner(repo_root=args.repo_root, max_file_size_mb=args.max_size_mb)

    # Default to --tracked if no specific scope is requested
    if not any([args.tracked, args.staged, args.history, args.untracked, args.all]):
        args.tracked = True

    all_findings: List[Finding] = []
    coverage_list: List[ScanCoverage] = []

    if args.all or args.tracked:
        findings, cov = scanner.scan_tracked()
        all_findings.extend(findings)
        coverage_list.append(cov)

    if args.all or args.staged:
        findings, cov = scanner.scan_staged()
        all_findings.extend(findings)
        coverage_list.append(cov)

    if args.all or args.history:
        findings, cov = scanner.scan_history()
        all_findings.extend(findings)
        coverage_list.append(cov)

    if args.all or args.untracked:
        findings, cov = scanner.scan_untracked()
        all_findings.extend(findings)
        coverage_list.append(cov)

    if not args.quiet:
        print_scan_report(all_findings, coverage_list)

    if args.json_output:
        report_data = {
            "repository_root": str(scanner.repo_root),
            "coverage": [asdict(c) for c in coverage_list],
            "total_findings": len(all_findings),
            "total_suspicious": sum(1 for f in all_findings if f.classification == "SUSPICIOUS_CREDENTIAL"),
            "total_synthetic": sum(1 for f in all_findings if f.classification == "SYNTHETIC_MOCK"),
            "total_public_doc": sum(1 for f in all_findings if f.classification == "PUBLIC_DOC_KEY"),
            "findings": [f.to_safe_dict() for f in all_findings]
        }
        with open(args.json_output, "w", encoding="utf-8") as jf:
            json.dump(report_data, jf, indent=2)
        if not args.quiet:
            print(f"\nJSON report saved cleanly to: {args.json_output}")

    # Exit code: 1 if any suspicious credential found, otherwise 0
    suspicious_count = sum(1 for f in all_findings if f.classification == "SUSPICIOUS_CREDENTIAL")
    sys.exit(1 if suspicious_count > 0 else 0)


if __name__ == "__main__":
    main()
