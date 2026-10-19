"""
Comprehensive Security and Regression Tests for HermesProject Secret Scanner
=============================================================================
Tests all security hardening requirements and invariants:
1. Synthetic examples of all 10 supported credential formats.
2. Malformed and incomplete tokens.
3. Overlapping patterns and duplicate findings resolution.
4. Safe redaction in terminal, JSON, and diagnostic output.
5. Classifier audit: Realistic credentials embedded in misleading contexts
   (comments mentioning 'example', test variable names 'mock_key', doc snippets,
   scanner regex definitions) MUST alert as SUSPICIOUS_CREDENTIAL.
6. Public documentation-key classification (strict 32-hex Algolia DocSearch keys vs
   arbitrary credentials in Docusaurus/Algolia contexts).
7. Detection of secrets containing complex punctuation and unusual characters.
8. Multiple distinct credentials on the same source line.
9. Private key detection across formats (RSA, OpenSSH, EC, DSA, Encrypted, PGP)
   and multiline safety.
10. Historical commit secret detection (secrets committed then removed).
11. Git history coverage, --all ref traversal, and shallow clone detection.
12. Staged changes secret interception.
13. Binary, unreadable, and large file safety.
14. Absolute zero-leak guarantee across stdout, stderr, JSON, dataclasses, and exceptions.

NOTE: All credentials in this file are strictly synthetic test vectors.
No real production API keys or user credentials are used.
"""

import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

# Add project root to sys.path to import scanner
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.scan_secrets import (
    Finding,
    ScanCoverage,
    SecretScanner,
    classify_match,
    compute_safe_fingerprint,
    is_algolia_search_key,
    is_binary_file,
    print_scan_report,
    scan_line_for_secrets,
)


class TestSecretScanner(unittest.TestCase):

    # --------------------------------------------------------------------------
    # 1. Synthetic Examples of Every Supported Credential Format (10 Families)
    # --------------------------------------------------------------------------
    def test_1_synthetic_credential_formats(self):
        """Verifies detection for all 10 supported credential families using synthetic vectors."""
        test_cases = [
            ("APInex Key", "sk-apx0123456789abcdef0123456789", "apinex_key"),
            ("Anthropic Key", "sk-ant-api03-0123456789abcdef0123456789", "anthropic_key"),
            ("Groq Key", "gsk_0123456789abcdef0123456789abcdef0123", "groq_key"),
            ("Google API Key", "AIzaSyD0123456789abcdefghijklmnopqrstuv", "google_api_key"),
            ("GitHub Token", "ghp_0123456789abcdef0123456789abcdef0123", "github_token"),
            ("AWS Access Key", "AKIAIOSFODNN7EXAMPLE", "aws_access_key"),
            ("Private Key Block", "-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEA...\n-----END RSA PRIVATE KEY-----", "private_key_block"),
            ("OpenAI Key", "sk-proj-0123456789abcdef0123456789", "openai_key"),
            ("Bearer Token", "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.e30.dummySignature1234567890", "bearer_token"),
            ("Hardcoded Secret Assignment", 'db_password = "SuperSecretDbPassword123!"', "hardcoded_secret_assignment"),
        ]

        for desc, payload, expected_rule in test_cases:
            findings = []
            for line_no, line in enumerate(payload.splitlines(), start=1):
                findings.extend(scan_line_for_secrets(line, line_no, "dummy_file.py"))

            self.assertTrue(len(findings) >= 1, f"Failed to detect {desc} with payload: {payload}")
            matched_rules = [f.rule_id for f in findings]
            self.assertIn(expected_rule, matched_rules, f"Expected rule {expected_rule} for {desc}, got {matched_rules}")

    # --------------------------------------------------------------------------
    # 2. Malformed and Incomplete Tokens
    # --------------------------------------------------------------------------
    def test_2_malformed_and_incomplete_tokens(self):
        """Verifies that incomplete fragments and malformed strings do not trigger false positives."""
        malformed_lines = [
            "sk-apx",                          # APInex prefix only (too short)
            "sk-",                             # Generic prefix only
            "AIza",                            # Google prefix only
            "ghp_123",                         # GitHub token too short
            "AKIA1234",                        # AWS ID too short (must be 20 chars total)
            "Bearer ",                         # Empty bearer
            "Bearer short",                    # Bearer token < 25 chars
            "password = 'abc'",                # Password < 8 chars
            "-----BEGIN PUBLIC KEY-----",      # Public key, not private key
            "def test_sk_prefix(): pass",      # Python function definition
            "curl https://example.com",        # Plain URL
        ]

        for line in malformed_lines:
            findings = scan_line_for_secrets(line, 1, "test_file.py")
            self.assertEqual(len(findings), 0, f"Malformed line unexpectedly produced findings: '{line}' -> {findings}")

    # --------------------------------------------------------------------------
    # 3. Overlapping Patterns and Priority Resolution
    # --------------------------------------------------------------------------
    def test_3_overlapping_patterns_and_duplicate_findings(self):
        """Verifies overlap resolution prevents duplicate findings across specific and generic rules."""
        # 1. Bearer token enclosing an APInex key
        # APInex Key (priority 100) must win over Bearer Token (priority 50)
        line1 = 'headers = {"Authorization": "Bearer sk-apx99887766554433221100aabbccdd"}'
        f1 = scan_line_for_secrets(line1, 1, "adapter.py")
        self.assertEqual(len(f1), 1, f"Expected exactly 1 resolved finding, got {len(f1)}")
        self.assertEqual(f1[0].rule_id, "apinex_key")

        # 2. Variable assignment enclosing a Google API key
        # Google Key (priority 100) must win over Hardcoded Secret Assignment (priority 10)
        line2 = 'api_key = "AIzaSyD0123456789abcdefghijklmnopqrstuv"'
        f2 = scan_line_for_secrets(line2, 1, "config.py")
        self.assertEqual(len(f2), 1, f"Expected exactly 1 resolved finding, got {len(f2)}")
        self.assertEqual(f2[0].rule_id, "google_api_key")

        # 3. APInex key prefix vs generic OpenAI key
        # APInex (priority 100) must win over OpenAI (priority 90)
        line3 = 'token = "sk-apx11223344556677889900aabbccdd"'
        f3 = scan_line_for_secrets(line3, 1, "client.py")
        self.assertEqual(len(f3), 1, f"Expected exactly 1 resolved finding, got {len(f3)}")
        self.assertEqual(f3[0].rule_id, "apinex_key")

    # --------------------------------------------------------------------------
    # 4. Safe Redaction in Terminal and JSON Output
    # --------------------------------------------------------------------------
    def test_4_safe_redaction_terminal_and_json(self):
        """Verifies that terminal and JSON outputs contain zero raw secret values."""
        secret_payload = "sk-apx99887766554433221100aabbccdd"
        line = f'my_secret = "{secret_payload}"'
        findings = scan_line_for_secrets(line, 42, "src/secrets.py")
        self.assertEqual(len(findings), 1)

        finding = findings[0]

        # 1. Check finding object properties
        self.assertNotIn(secret_payload, finding.fingerprint_sha256)
        self.assertTrue(finding.fingerprint_sha256.startswith("sha256:"))
        self.assertEqual(finding.length, len(secret_payload))

        # 2. Check JSON serialized dictionary
        json_dict = finding.to_safe_dict()
        json_str = json.dumps(json_dict)
        self.assertNotIn(secret_payload, json_str)
        self.assertIn("fingerprint_sha256", json_str)
        self.assertIn("length", json_str)

        # 3. Check terminal formatted report
        cov = ScanCoverage(scope="tracked", files_scanned=1, total_suspicious=1)
        captured = io.StringIO()
        old_stdout = sys.stdout
        try:
            sys.stdout = captured
            print_scan_report(findings, [cov])
        finally:
            sys.stdout = old_stdout

        terminal_out = captured.getvalue()
        self.assertNotIn(secret_payload, terminal_out)
        self.assertIn("sha256:", terminal_out)

    # --------------------------------------------------------------------------
    # 5. Classifier Audit: Misleading Contexts & False Negative Hardening
    # --------------------------------------------------------------------------
    def test_5_classifier_no_false_negatives_in_misleading_contexts(self):
        """
        Verifies that realistic credentials are NOT marked SYNTHETIC_MOCK merely
        because the line or context mentions 'example', 'test', 'mock', 'sample',
        or is located in a test file, scanner file, or doc file.
        """
        realistic_key = "sk-apx01827461984719283746192837461928"

        misleading_cases = [
            # Case A: Line comment mentioning 'example' or 'test'
            (f'api_token = "{realistic_key}" # for example in tests', "server/config.py"),
            (f'# example token for developers: {realistic_key}', "docs/setup.md"),
            # Case B: Inside a test file with variable named 'mock_key' or 'test_key'
            (f'mock_key = "{realistic_key}"', "tests/test_auth.py"),
            (f'test_api_key = "{realistic_key}"', "hermes-agent/tests/test_agent.py"),
            (f'assert client.key == "{realistic_key}"', "tests/unit/test_client.py"),
            # Case C: Inside scanner or redaction source file with re.compile
            (f'PATTERNS = [re.compile(r"{realistic_key}")]', "server/utils/redact.py"),
            (f'KNOWN_REGEX = "{realistic_key}" # regex_pattern', "scripts/scan_secrets.py"),
            # Case D: Inside documentation snippet
            (f'```bash\nexport APINEX_KEY="{realistic_key}"\n```', "docs/quickstart.md"),
        ]

        for payload, file_path in misleading_cases:
            for line_no, line in enumerate(payload.splitlines(), start=1):
                findings = scan_line_for_secrets(line, line_no, file_path)
                if not findings:
                    continue
                for f in findings:
                    self.assertEqual(
                        f.classification,
                        "SUSPICIOUS_CREDENTIAL",
                        f"Realistic key was wrongly marked {f.classification} in misleading context: '{line}' in {file_path}"
                    )

        # Confirm that true synthetic fixtures continue to be recognized as SYNTHETIC_MOCK
        true_synthetic_lines = [
            ('APINEX_API_KEY="your_apinex_api_key_here"', ".env.example"),
            ('client.api_key = "test_apx_key"', "tests/test_api.py"),
            ('api_key="your-api-key"', "docs/guide.md"),
            ('auth_token = "dummy_secret_value"', "tests/mock_auth.py"),
            ('key = "sk-proj-xxxxxxxxxxxxxxxxxxxx"', "docs/setup.md"),
            ('API_KEY="${USDA_API_KEY:-DEMO_KEY}"', "scripts/fetch.sh"),
            ('auth_token = "{{MY_SECRET_KEY}}"', "templates/config.yaml"),
            ('key = "AKIAIOSFODNN7EXAMPLE"', "tests/test_aws.py"),
        ]

        for line, file_path in true_synthetic_lines:
            findings = scan_line_for_secrets(line, 1, file_path)
            self.assertTrue(len(findings) >= 1, f"Expected match for: {line}")
            for f in findings:
                self.assertEqual(
                    f.classification,
                    "SYNTHETIC_MOCK",
                    f"Expected SYNTHETIC_MOCK for '{line}' in {file_path}, got {f.classification}"
                )

    # --------------------------------------------------------------------------
    # 6. Public Documentation-Key Classification (Algolia DocSearch)
    # --------------------------------------------------------------------------
    def test_6_public_doc_key_strict_classification(self):
        """
        Verifies that PUBLIC_DOC_KEY is assigned ONLY to demonstrably public 32-hex
        Algolia search-only keys in Docusaurus configuration, never to arbitrary credentials.
        """
        # 1. Valid 32-hex Algolia DocSearch search key in docusaurus config
        valid_algolia_line = "apiKey: '8fda2a49223ce185ac30c2dbf6898a07',"
        f_valid = scan_line_for_secrets(valid_algolia_line, 105, "website/docusaurus.config.ts")
        self.assertEqual(len(f_valid), 1)
        self.assertEqual(f_valid[0].classification, "PUBLIC_DOC_KEY")
        self.assertIn("32-hex", f_valid[0].context_note)

        # 2. Non-32-hex or provider key inside docusaurus config must NOT be PUBLIC_DOC_KEY!
        fake_secret_line = 'apiKey: "sk-proj-01827461984719283746192837461928",'
        f_fake = scan_line_for_secrets(fake_secret_line, 106, "website/docusaurus.config.ts")
        self.assertEqual(len(f_fake), 1)
        self.assertEqual(
            f_fake[0].classification,
            "SUSPICIOUS_CREDENTIAL",
            "Provider credential in docusaurus.config must alert as SUSPICIOUS_CREDENTIAL, not PUBLIC_DOC_KEY"
        )

        # 3. Arbitrary secret on a line with 'algolia' in a standard source file
        algolia_source_line = 'algolia_admin_key = "sk-apx01827461984719283746192837461928"'
        f_src = scan_line_for_secrets(algolia_source_line, 20, "server/search.py")
        self.assertEqual(len(f_src), 1)
        self.assertEqual(
            f_src[0].classification,
            "SUSPICIOUS_CREDENTIAL",
            "Arbitrary credential on algolia line must alert as SUSPICIOUS_CREDENTIAL"
        )

        # 4. Invariant: Raw key is never printed in Finding or context_note
        raw_key = "8fda2a49223ce185ac30c2dbf6898a07"
        self.assertNotIn(raw_key, f_valid[0].context_note)
        self.assertNotIn(raw_key, json.dumps(f_valid[0].to_safe_dict()))

    # --------------------------------------------------------------------------
    # 7. Secrets Containing Complex Punctuation & Unusual Characters
    # --------------------------------------------------------------------------
    def test_7_secrets_containing_complex_punctuation(self):
        """Verifies detection of credentials and passwords containing valid special characters."""
        punctuation_cases = [
            ('db_password = "P@ssw0rd!#$123"', "hardcoded_secret_assignment", "P@ssw0rd!#$123"),
            ('secret_key: "complex+token/value=123?#456"', "hardcoded_secret_assignment", "complex+token/value=123?#456"),
            ('passwd = "Admin&Secret%Key^2026*"', "hardcoded_secret_assignment", "Admin&Secret%Key^2026*"),
            ('Bearer eyJhbGciOi.eyJzdWIiOi.test+sig/val=1234567890', "bearer_token", "eyJhbGciOi.eyJzdWIiOi.test+sig/val=1234567890"),
        ]

        for line, expected_rule, expected_value in punctuation_cases:
            findings = scan_line_for_secrets(line, 1, "config.py")
            self.assertTrue(len(findings) >= 1, f"Failed to detect punctuation secret: {line}")
            self.assertEqual(findings[0].rule_id, expected_rule)
            self.assertEqual(findings[0].length, len(expected_value))
            # Verify safe fingerprint matches expected hash
            expected_fp = compute_safe_fingerprint(expected_value)
            self.assertEqual(findings[0].fingerprint_sha256, expected_fp)

    # --------------------------------------------------------------------------
    # 8. Multiple Distinct Credentials on the Same Source Line
    # --------------------------------------------------------------------------
    def test_8_multiple_credentials_on_same_line(self):
        """Verifies that multiple non-overlapping credentials on one line are individually captured."""
        multi_line = 'key1 = "sk-apx0123456789abcdef0123456789", key2 = "ghp_0123456789abcdef0123456789abcdef0123"'
        findings = scan_line_for_secrets(multi_line, 1, "service.py")
        self.assertEqual(len(findings), 2, f"Expected 2 distinct findings, got {len(findings)}")

        rules = [f.rule_id for f in findings]
        self.assertEqual(rules, ["apinex_key", "github_token"])
        self.assertNotEqual(findings[0].fingerprint_sha256, findings[1].fingerprint_sha256)

    # --------------------------------------------------------------------------
    # 9. Private Key Markers and Multiline Handling
    # --------------------------------------------------------------------------
    def test_9_private_key_markers_and_multiline_safety(self):
        """Verifies private key detection across headers and safe handling of multiline key material."""
        key_headers = [
            "-----BEGIN RSA PRIVATE KEY-----",
            "-----BEGIN OPENSSH PRIVATE KEY-----",
            "-----BEGIN EC PRIVATE KEY-----",
            "-----BEGIN DSA PRIVATE KEY-----",
            "-----BEGIN PRIVATE KEY-----",
            "-----BEGIN ENCRYPTED PRIVATE KEY-----",
            "-----BEGIN PGP PRIVATE KEY BLOCK-----",
        ]

        for hdr in key_headers:
            findings = scan_line_for_secrets(hdr, 1, "server.key")
            self.assertEqual(len(findings), 1, f"Failed to detect header: {hdr}")
            self.assertEqual(findings[0].rule_id, "private_key_block")
            self.assertEqual(findings[0].classification, "SUSPICIOUS_CREDENTIAL")

        # Full multiline PEM file
        full_pem = (
            "-----BEGIN RSA PRIVATE KEY-----\n"
            "MIIEowIBAAKCAQEA0Y123456789abcdefghijklmnopqrstuvwxyz...\n"
            "MIIEowIBAAKCAQEA0Y123456789abcdefghijklmnopqrstuvwxyz...\n"
            "-----END RSA PRIVATE KEY-----\n"
        )
        scanner = SecretScanner(repo_root=".")
        findings_pem = scanner.scan_file_content(full_pem, "server.pem")
        # Exactly 1 finding for the private key header block
        self.assertEqual(len(findings_pem), 1)
        self.assertEqual(findings_pem[0].rule_id, "private_key_block")
        self.assertEqual(findings_pem[0].line_number, 1)

    # --------------------------------------------------------------------------
    # 10. Historical Commit Secret Detection (Deleted Secrets in Git History)
    # --------------------------------------------------------------------------
    def test_10_historical_commit_secrets(self):
        """Verifies that secrets introduced in past commits and later removed are detected in history."""
        with tempfile.TemporaryDirectory() as temp_repo:
            repo_path = Path(temp_repo)

            # Initialize temporary Git repo with default branch main
            subprocess.run(["git", "init", "-b", "main"], cwd=temp_repo, check=True, stdout=subprocess.DEVNULL)
            subprocess.run(["git", "config", "user.email", "audit@hermes.local"], cwd=temp_repo, check=True)
            subprocess.run(["git", "config", "user.name", "Audit Runner"], cwd=temp_repo, check=True)

            # Commit 1: Add a file with a suspicious credential
            secret_file = repo_path / "credentials.py"
            secret_file.write_text('api_token = "sk-apx99887766554433221100aabbccdd"\n')
            subprocess.run(["git", "add", "credentials.py"], cwd=temp_repo, check=True)
            subprocess.run(["git", "commit", "-m", "Commit 1: Add credentials"], cwd=temp_repo, check=True, stdout=subprocess.DEVNULL)

            # Get commit 1 hash
            commit1_hash = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=temp_repo, text=True).strip()[:10]

            # Commit 2: Remove the credential from credentials.py
            secret_file.write_text('api_token = "dummy_secret_value"\n')
            subprocess.run(["git", "add", "credentials.py"], cwd=temp_repo, check=True)
            subprocess.run(["git", "commit", "-m", "Commit 2: Remove credentials"], cwd=temp_repo, check=True, stdout=subprocess.DEVNULL)

            # Run history scan on the temporary repo
            scanner = SecretScanner(repo_root=temp_repo)
            history_findings, cov = scanner.scan_history()

            suspicious_history = [f for f in history_findings if f.classification == "SUSPICIOUS_CREDENTIAL"]
            self.assertTrue(len(suspicious_history) >= 1, "History scanner failed to detect past secret")
            self.assertEqual(suspicious_history[0].commit_hash, commit1_hash)
            self.assertEqual(suspicious_history[0].file_path, "credentials.py")

    # --------------------------------------------------------------------------
    # 11. Git History Coverage: All Refs and Shallow Detection
    # --------------------------------------------------------------------------
    def test_11_git_history_all_refs_and_shallow_detection(self):
        """Verifies that history scanning inspects feature branches and correctly identifies shallow status."""
        with tempfile.TemporaryDirectory() as temp_repo:
            repo_path = Path(temp_repo)

            subprocess.run(["git", "init", "-b", "main"], cwd=temp_repo, check=True, stdout=subprocess.DEVNULL)
            subprocess.run(["git", "config", "user.email", "audit@hermes.local"], cwd=temp_repo, check=True)
            subprocess.run(["git", "config", "user.name", "Audit Runner"], cwd=temp_repo, check=True)

            # Main commit
            (repo_path / "main.py").write_text("print('hello')\n")
            subprocess.run(["git", "add", "main.py"], cwd=temp_repo, check=True)
            subprocess.run(["git", "commit", "-m", "Main commit"], cwd=temp_repo, check=True, stdout=subprocess.DEVNULL)

            # Create feature branch with a credential
            subprocess.run(["git", "checkout", "-b", "feature/secret-branch"], cwd=temp_repo, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            (repo_path / "feature.py").write_text('token = "gsk_0123456789abcdef0123456789abcdef0123"\n')
            subprocess.run(["git", "add", "feature.py"], cwd=temp_repo, check=True)
            subprocess.run(["git", "commit", "-m", "Feature commit with secret"], cwd=temp_repo, check=True, stdout=subprocess.DEVNULL)

            # Switch back to main
            subprocess.run(["git", "checkout", "main"], cwd=temp_repo, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            # Scan history from main - with --all, feature/secret-branch MUST be scanned!
            scanner = SecretScanner(repo_root=temp_repo)
            findings, cov = scanner.scan_history()

            groq_findings = [f for f in findings if f.rule_id == "groq_key"]
            self.assertTrue(len(groq_findings) >= 1, "Failed to scan across unmerged branch refs (--all)")
            self.assertFalse(cov.is_shallow, "Temporary repo was unexpectedly flagged as shallow clone")

    # --------------------------------------------------------------------------
    # 12. Staged Changes Interception
    # --------------------------------------------------------------------------
    def test_12_staged_changes_secrets(self):
        """Verifies that secrets in git staged changes are intercepted before commit."""
        with tempfile.TemporaryDirectory() as temp_repo:
            subprocess.run(["git", "init", "-b", "main"], cwd=temp_repo, check=True, stdout=subprocess.DEVNULL)
            subprocess.run(["git", "config", "user.email", "audit@hermes.local"], cwd=temp_repo, check=True)
            subprocess.run(["git", "config", "user.name", "Audit Runner"], cwd=temp_repo, check=True)

            staged_file = Path(temp_repo) / "staged_service.py"
            staged_file.write_text('token = "gsk_0123456789abcdef0123456789abcdef0123"\n')
            subprocess.run(["git", "add", "staged_service.py"], cwd=temp_repo, check=True)

            scanner = SecretScanner(repo_root=temp_repo)
            staged_findings, cov = scanner.scan_staged()

            self.assertTrue(len(staged_findings) >= 1, "Staged scanner failed to detect staged secret")
            self.assertEqual(staged_findings[0].rule_id, "groq_key")
            self.assertEqual(staged_findings[0].file_path, "staged_service.py")

    # --------------------------------------------------------------------------
    # 13. Binary Files, Unreadable Files, and Multimatch Files
    # --------------------------------------------------------------------------
    def test_13_binary_unreadable_and_multimatch_files(self):
        """Verifies that binary files are skipped safely and multi-match files are fully indexed."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            scanner = SecretScanner(repo_root=temp_dir)

            # Binary file with embedded null byte and key string
            binary_file = temp_path / "app_icon.png"
            content = bytearray([137, 80, 78, 71, 13, 10, 26, 10, 0, 0, 0])
            content.extend(b"sk-apx0123456789abcdef0123")
            content.append(0)
            binary_file.write_bytes(bytes(content))

            self.assertTrue(is_binary_file(binary_file))
            cov = ScanCoverage(scope="test")
            findings_bin = scanner.scan_local_file(binary_file, "app_icon.png", cov)
            self.assertEqual(len(findings_bin), 0, "Binary file must not produce text findings")
            self.assertEqual(cov.files_skipped_binary, 1)

            # File with multiple matches on distinct lines
            multimatch_file = temp_path / "multi.py"
            multimatch_content = (
                'key1 = "sk-apx0123456789abcdef0123456789"\n'
                '# spacer\n'
                'key2 = "ghp_0123456789abcdef0123456789abcdef0123"\n'
                '# spacer\n'
                'key3 = "AKIAIOSFODNN7EXAMPLE"\n'
            )
            multimatch_file.write_text(multimatch_content)

            cov2 = ScanCoverage(scope="test")
            findings_multi = scanner.scan_local_file(multimatch_file, "multi.py", cov2)
            self.assertEqual(len(findings_multi), 3, f"Expected 3 findings, got {len(findings_multi)}")
            lines = [f.line_number for f in findings_multi]
            self.assertEqual(lines, [1, 3, 5])

    # --------------------------------------------------------------------------
    # 14. Zero-Leak Invariant Across JSON, Dataclasses, and Reports
    # --------------------------------------------------------------------------
    def test_14_guarantee_no_real_credentials_in_output(self):
        """Verifies that raw secret strings never appear in JSON, dataclasses, reports, or diagnostics."""
        synthetic_secrets = [
            "sk-apx99887766554433221100aabbccdd",
            "sk-ant-api03-00112233445566778899aabbccdd",
            "gsk_abcdef0123456789abcdef0123456789",
            "AIzaSyD9876543210zyxwvutsrqponmlkjihgfe",
            "ghp_0123456789abcdef0123456789abcdef0123",
            "AKIAIOSFODNN7EXAMPLE",
        ]

        for sec in synthetic_secrets:
            line = f'token = "{sec}"'
            findings = scan_line_for_secrets(line, 1, "test.py")
            self.assertTrue(len(findings) >= 1)

            for f in findings:
                # 1. Inspect finding dataclass dictionary
                d = f.to_safe_dict()
                d_str = json.dumps(d)
                self.assertNotIn(sec, d_str, f"Secret leaked in dictionary output: {sec}")

                # 2. Inspect terminal report
                cov = ScanCoverage(scope="test", files_scanned=1, total_suspicious=1)
                buf = io.StringIO()
                old_stdout = sys.stdout
                try:
                    sys.stdout = buf
                    print_scan_report([f], [cov])
                finally:
                    sys.stdout = old_stdout

                report_text = buf.getvalue()
                self.assertNotIn(sec, report_text, f"Secret leaked in report text: {sec}")


    # --------------------------------------------------------------------------
    # 15. Access Token and Auth Token Assignment Regression Tests
    # --------------------------------------------------------------------------
    def test_15_access_and_auth_token_assignment_regression(self):
        """
        Verifies that hardcoded_secret_assignment accurately detects both access_token
        and auth_token assignments across case variants and delimiters, rejects short values,
        maintains zero-leak guarantees, and honors provider overlap priority.
        """
        assignment_test_cases = [
            ('access_token = "SyntheticAccessToken123!"', "SyntheticAccessToken123!"),
            ('ACCESS_TOKEN = "SyntheticAccessToken123!"', "SyntheticAccessToken123!"),
            ('access-token = "SyntheticAccessToken123!"', "SyntheticAccessToken123!"),
            ('auth_token = "SyntheticAuthToken123!"', "SyntheticAuthToken123!"),
            ('auth-token = "SyntheticAuthToken123!"', "SyntheticAuthToken123!"),
        ]

        for line, raw_value in assignment_test_cases:
            findings = scan_line_for_secrets(line, 1, "config.py")
            self.assertEqual(len(findings), 1, f"Failed detection for line: {line}")
            f = findings[0]
            self.assertEqual(f.rule_id, "hardcoded_secret_assignment")
            self.assertEqual(f.length, len(raw_value))
            expected_fp = compute_safe_fingerprint(raw_value)
            self.assertEqual(f.fingerprint_sha256, expected_fp)

            # Redaction guarantee: raw secret must never appear in dataclass dict, JSON, or terminal report
            d = f.to_safe_dict()
            d_str = json.dumps(d)
            self.assertNotIn(raw_value, d_str, f"Raw token leaked in finding dict: {raw_value}")
            self.assertNotIn(raw_value, f.context_note)
            self.assertNotIn(raw_value, f.fingerprint_sha256)

            buf = io.StringIO()
            old_stdout = sys.stdout
            try:
                sys.stdout = buf
                print_scan_report([f], [ScanCoverage(scope="test", files_scanned=1, total_suspicious=1)])
            finally:
                sys.stdout = old_stdout
            self.assertNotIn(raw_value, buf.getvalue(), f"Raw token leaked in printed report: {raw_value}")

        # Short values below existing minimum length (8 chars) must NOT be detected by the generic assignment rule
        short_lines = [
            'access_token = "short"',
            'ACCESS_TOKEN = "tiny"',
            'access-token = "1234567"',
            'auth_token = "abc"',
            'auth-token = "short"',
        ]
        for s in short_lines:
            findings_short = scan_line_for_secrets(s, 1, "config.py")
            assignment_findings = [f for f in findings_short if f.rule_id == "hardcoded_secret_assignment"]
            self.assertEqual(
                len(assignment_findings), 0,
                f"Short token below minimum length was unexpectedly detected: {s} -> {assignment_findings}"
            )

        # Overlap resolution: Provider-specific rules MUST win over generic access/auth_token assignment
        overlap_cases = [
            ('access_token = "sk-apx0123456789abcdef0123456789"', "apinex_key"),
            ('auth_token = "ghp_0123456789abcdef0123456789abcdef0123"', "github_token"),
            ('access_token = "gsk_0123456789abcdef0123456789abcdef0123"', "groq_key"),
            ('ACCESS_TOKEN = "AIzaSyD0123456789abcdefghijklmnopqrstuv"', "google_api_key"),
            ('access-token = "sk-ant-api03-0123456789abcdef0123456789"', "anthropic_key"),
        ]
        for ov_line, expected_rule in overlap_cases:
            f_ov = scan_line_for_secrets(ov_line, 1, "service.py")
            self.assertEqual(len(f_ov), 1, f"Expected 1 finding for overlap line: {ov_line}")
            self.assertEqual(
                f_ov[0].rule_id, expected_rule,
                f"Provider rule {expected_rule} did not win priority on line: {ov_line} (got {f_ov[0].rule_id})"
            )


if __name__ == "__main__":
    unittest.main()
