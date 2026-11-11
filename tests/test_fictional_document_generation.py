import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "generate_fictional_documents", ROOT / "scripts" / "generate_fictional_documents.py"
)
GENERATOR = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = GENERATOR
SPEC.loader.exec_module(GENERATOR)


class FictionalDocumentGenerationTests(unittest.TestCase):
    def test_generated_documents_match_checked_in_fixtures(self):
        source = ROOT / "examples" / "fictional-demo" / "document-input.json"
        expected_dir = ROOT / "examples" / "fictional-demo" / "generated"
        with tempfile.TemporaryDirectory() as directory:
            outputs = GENERATOR.generate(source, Path(directory))
            self.assertEqual(
                ["fictional-change-review.md", "fictional-cover-letter.md", "fictional-cv.md"],
                [path.name for path in outputs],
            )
            for output in outputs:
                expected = (expected_dir / output.name).read_text(encoding="utf-8")
                self.assertEqual(expected, output.read_text(encoding="utf-8"))

    def test_generated_documents_have_fictional_banner(self):
        data = json.loads((ROOT / "examples" / "fictional-demo" / "document-input.json").read_text(encoding="utf-8"))
        self.assertIn("Fictional example.", GENERATOR.render_cv(data))
        self.assertIn("Fictional example.", GENERATOR.render_cover_letter(data))

    def test_cv_contains_multiple_candidate_sections(self):
        data = json.loads((ROOT / "examples" / "fictional-demo" / "document-input.json").read_text(encoding="utf-8"))
        rendered = GENERATOR.render_cv(data)
        for heading in ["## Experience", "## Selected project", "## Education", "## Skills", "## Languages"]:
            self.assertIn(heading, rendered)

    def test_cover_letter_uses_reviewed_evidence(self):
        data = json.loads((ROOT / "examples" / "fictional-demo" / "document-input.json").read_text(encoding="utf-8"))
        rendered = GENERATOR.render_cover_letter(data)
        for match in data["matches"][:2]:
            self.assertIn(match["evidence"], rendered)

    def test_change_review_links_decisions_to_evidence(self):
        data = json.loads((ROOT / "examples" / "fictional-demo" / "document-input.json").read_text(encoding="utf-8"))
        rendered = GENERATOR.render_change_review(data)
        self.assertIn(data["variant"]["id"], rendered)
        for change in data["change_review"]:
            self.assertIn(change["decision"], rendered)
            for evidence_id in change["evidence_ids"]:
                self.assertIn(evidence_id, rendered)

    def test_reviewed_variant_rejects_pending_decisions(self):
        source = ROOT / "examples" / "fictional-demo" / "document-input.json"
        data = json.loads(source.read_text(encoding="utf-8"))
        data["change_review"][0]["decision"] = "pending"
        with tempfile.TemporaryDirectory() as directory:
            input_path = Path(directory) / "input.json"
            input_path.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "pending decisions"):
                GENERATOR.generate(input_path, Path(directory) / "out")

    def test_generator_requires_guidance_sources(self):
        source = ROOT / "examples" / "fictional-demo" / "document-input.json"
        data = json.loads(source.read_text(encoding="utf-8"))
        data["guidance"]["sources"] = []
        with tempfile.TemporaryDirectory() as directory:
            input_path = Path(directory) / "input.json"
            input_path.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "guidance source"):
                GENERATOR.generate(input_path, Path(directory) / "out")

    def test_generator_rejects_nonfictional_input(self):
        source = ROOT / "examples" / "fictional-demo" / "document-input.json"
        data = json.loads(source.read_text(encoding="utf-8"))
        data["fictional"] = False
        with tempfile.TemporaryDirectory() as directory:
            input_path = Path(directory) / "input.json"
            input_path.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "explicitly fictional"):
                GENERATOR.generate(input_path, Path(directory) / "out")


if __name__ == "__main__":
    unittest.main()
