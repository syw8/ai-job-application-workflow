import json
import re
import subprocess
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
FRONTMATTER = re.compile(r"\A---\n(?P<header>.*?)\n---\n", re.DOTALL)


class WorkflowStructureTests(unittest.TestCase):
    def test_expected_skills_exist(self):
        expected = {
            "write-cover-letter",
            "tailor-cv",
            "find-and-track-jobs",
        }
        actual = {path.name for path in (ROOT / "skills").iterdir() if path.is_dir()}
        self.assertEqual(expected, actual)

    def test_skill_names_match_folders(self):
        for folder in (ROOT / "skills").iterdir():
            if not folder.is_dir():
                continue
            text = (folder / "SKILL.md").read_text(encoding="utf-8")
            match = FRONTMATTER.match(text)
            self.assertIsNotNone(match)
            header = yaml.safe_load(match.group("header"))
            self.assertEqual(folder.name, header["name"])

    def test_cover_letter_researches_official_guidance(self):
        text = (ROOT / "skills" / "write-cover-letter" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("official", text.lower())
        self.assertIn("requirement-to-evidence", text)
        self.assertIn("existing letter is optional", text.lower())

    def test_scheduled_search_is_external(self):
        config = yaml.safe_load((ROOT / "config.example.yaml").read_text(encoding="utf-8"))
        self.assertEqual("external", config["scheduled_search"]["component"])
        self.assertFalse(config["scheduled_search"]["repository_executes_schedule"])

    def test_plugin_has_no_server_configuration(self):
        manifest = json.loads((ROOT / "plugin.json").read_text(encoding="utf-8"))
        self.assertNotIn("mcpServers", manifest)
        self.assertFalse((ROOT / "mcp.json").exists())

    def test_human_review_is_required(self):
        config = yaml.safe_load((ROOT / "config.example.yaml").read_text(encoding="utf-8"))
        self.assertTrue(config["human_review_required"])
        self.assertTrue(config["documents"]["versioning"]["require_decided_change_set"])

    def test_required_fictional_fixtures_exist(self):
        for relative in [
            "examples/fictional-demo/README.md",
            "examples/fictional-demo/application-record.json",
            "examples/fictional-demo/candidate-profile.example.yaml",
            "examples/fictional-demo/document-input.json",
            "examples/fictional-demo/generated/fictional-change-review.md",
            "examples/fictional-demo/generated/fictional-cover-letter.md",
            "examples/fictional-demo/generated/fictional-cv.md",
            "examples/fictional-demo/job-lead.json",
        ]:
            self.assertTrue((ROOT / relative).is_file(), relative)

    def test_cv_allows_broad_tailoring_while_protecting_facts(self):
        config = yaml.safe_load((ROOT / "config.example.yaml").read_text(encoding="utf-8"))
        cv = config["documents"]["cv"]
        self.assertTrue({"profile", "experience", "education", "projects", "skills"}.issubset(cv["editable_sections"]))
        self.assertTrue({"organizations", "titles", "dates", "credentials"}.issubset(cv["protected_fact_types"]))
        self.assertTrue(cv["fact_changes_require_confirmation"])

    def test_job_search_has_private_criteria_and_primary_page_gate(self):
        config = yaml.safe_load((ROOT / "config.example.yaml").read_text(encoding="utf-8"))
        search = config["job_search"]
        self.assertTrue(search["roles"])
        self.assertTrue(search["locations"])
        self.assertTrue(search["official_detail_page_required"])

    def test_package_folder_pattern_has_required_fields(self):
        config = yaml.safe_load((ROOT / "config.example.yaml").read_text(encoding="utf-8"))
        pattern = config["documents"]["cover_letter"]["package"]["folder_pattern"]
        self.assertIn("{organization}", pattern)
        self.assertIn("{role}", pattern)

    def test_skill_sources_are_current_research_contracts(self):
        cover = (ROOT / "skills" / "write-cover-letter" / "references" / "source-and-writing-policy.md").read_text(encoding="utf-8")
        cv = (ROOT / "skills" / "tailor-cv" / "references" / "source-and-tailoring-policy.md").read_text(encoding="utf-8")
        jobs = (ROOT / "skills" / "find-and-track-jobs" / "references" / "search-policy.md").read_text(encoding="utf-8")
        self.assertIn("Bundesagentur", cover)
        self.assertIn("Europass", cv)
        self.assertIn("primary detail page", jobs.lower())

    def test_fictional_fixtures_are_not_ignored(self):
        for relative in [
            "examples/fictional-demo/README.md",
            "examples/fictional-demo/application-record.json",
            "examples/fictional-demo/candidate-profile.example.yaml",
            "examples/fictional-demo/document-input.json",
            "examples/fictional-demo/generated/fictional-change-review.md",
            "examples/fictional-demo/generated/fictional-cover-letter.md",
            "examples/fictional-demo/generated/fictional-cv.md",
            "examples/fictional-demo/job-lead.json",
        ]:
            result = subprocess.run(
                ["git", "check-ignore", "--no-index", "--quiet", relative],
                cwd=ROOT,
                check=False,
            )
            self.assertNotEqual(0, result.returncode, relative)

    def test_private_paths_are_ignored(self):
        private_record = "records" + ".json"
        for relative in [
            "config.local.yaml",
            "candidate-profile.yaml",
            ".env",
            "private-data/example.json",
            private_record,
            "private-document.pdf",
            ".venv/bin/python",
        ]:
            result = subprocess.run(
                ["git", "check-ignore", "--no-index", "--quiet", relative],
                cwd=ROOT,
                check=False,
            )
            self.assertEqual(0, result.returncode, relative)

    def test_ci_has_read_only_checkout_and_no_artifact_upload(self):
        workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
        self.assertIn("contents: read", workflow)
        self.assertIn("persist-credentials: false", workflow)
        self.assertNotIn("upload-artifact", workflow)


if __name__ == "__main__":
    unittest.main()
