import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("privacy_scan", ROOT / "scripts" / "privacy_scan.py")
PRIVACY_SCAN = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = PRIVACY_SCAN
SPEC.loader.exec_module(PRIVACY_SCAN)


class PrivacyScanTests(unittest.TestCase):
    def test_safe_fictional_content_passes(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            (path / "safe.md").write_text("Fictional candidate at Example Institute.", encoding="utf-8")
            self.assertEqual([], PRIVACY_SCAN.scan(path))

    def test_local_home_path_is_detected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            private_path = "/" + "Users" + "/private-person/secret.txt"
            (path / "unsafe.md").write_text(private_path, encoding="utf-8")
            rules = {finding.rule for finding in PRIVACY_SCAN.scan(path)}
            self.assertIn("macos-home-path", rules)

    def test_token_is_detected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            token = "sk-" + "a" * 32
            (path / "unsafe.txt").write_text(token, encoding="utf-8")
            rules = {finding.rule for finding in PRIVACY_SCAN.scan(path)}
            self.assertIn("openai-style-token", rules)

    def test_external_denylist_is_detected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            value = "Private" + " Identifier"
            (path / "unsafe.txt").write_text(f"Contains {value} here.", encoding="utf-8")
            rules = {finding.rule for finding in PRIVACY_SCAN.scan(path, [value])}
            self.assertIn("private-denylist", rules)

    def test_ordinary_name_from_private_denylist_is_detected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            ordinary_name = "Taylor" + " Morgan"
            (path / "notes.md").write_text(f"Reviewed by {ordinary_name}.", encoding="utf-8")
            findings = PRIVACY_SCAN.scan(path, [ordinary_name])
            self.assertIn("private-denylist", {finding.rule for finding in findings})

    def test_renamed_private_record_is_detected_by_content(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            private_name = "Jordan" + " Ellis"
            (path / "renamed-archive.txt").write_text(
                f'{{"candidate": "{private_name}", "status": "submitted"}}',
                encoding="utf-8",
            )
            findings = PRIVACY_SCAN.scan(path, [private_name])
            self.assertIn("private-denylist", {finding.rule for finding in findings})

    def test_local_phone_number_is_detected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            phone = "030" + " 12345678"
            (path / "contact.txt").write_text(phone, encoding="utf-8")
            rules = {finding.rule for finding in PRIVACY_SCAN.scan(path)}
            self.assertIn("local-phone-number", rules)

    def test_common_credential_patterns_are_detected(self):
        credential_cases = {
            "github-token": "gh" + "p_" + "a" * 24,
            "aws-access-key": "AK" + "IA" + "A" * 16,
            "slack-token": "xox" + "b-" + "1" * 24,
            "google-api-key": "AI" + "za" + "A" * 35,
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            for index, value in enumerate(credential_cases.values()):
                (path / f"credential-{index}.txt").write_text(value, encoding="utf-8")
            rules = {finding.rule for finding in PRIVACY_SCAN.scan(path)}
            self.assertTrue(set(credential_cases).issubset(rules))

    def test_formatted_findings_do_not_reveal_path_or_match(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            private_name = "Morgan" + " Taylor"
            private_filename = "private-person-name.txt"
            (path / private_filename).write_text(private_name, encoding="utf-8")
            finding = PRIVACY_SCAN.scan(path, [private_name])[0]
            rendered = PRIVACY_SCAN.format_finding(finding, 1)
            self.assertNotIn(private_name, rendered)
            self.assertNotIn(private_filename, rendered)
            self.assertIn("private-denylist", rendered)

    def test_binary_application_artifact_is_detected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            suffix = "." + "docx"
            (path / f"private{suffix}").write_bytes(b"not a real document")
            rules = {finding.rule for finding in PRIVACY_SCAN.scan(path)}
            self.assertIn("blocked-binary-artifact", rules)


if __name__ == "__main__":
    unittest.main()
