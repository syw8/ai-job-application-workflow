import json
import unittest
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]


class SchemaTests(unittest.TestCase):
    def assert_valid(self, instance, schema_path):
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        validator = Draft202012Validator(schema, format_checker=FormatChecker())
        errors = list(validator.iter_errors(instance))
        self.assertEqual([], errors, "\n".join(error.message for error in errors))

    def test_example_config(self):
        config = yaml.safe_load((ROOT / "config.example.yaml").read_text(encoding="utf-8"))
        self.assert_valid(config, ROOT / "schemas" / "config.schema.json")

    def test_fictional_application_record(self):
        record = json.loads((ROOT / "examples" / "fictional-demo" / "application-record.json").read_text(encoding="utf-8"))
        self.assert_valid(record, ROOT / "schemas" / "application-record.schema.json")

    def test_generic_record_does_not_require_fictional_marker(self):
        record = json.loads((ROOT / "examples" / "fictional-demo" / "application-record.json").read_text(encoding="utf-8"))
        record.pop("fictional")
        self.assert_valid(record, ROOT / "schemas" / "application-record.schema.json")

    def test_generic_record_allows_false_fictional_marker(self):
        record = json.loads((ROOT / "examples" / "fictional-demo" / "application-record.json").read_text(encoding="utf-8"))
        record["fictional"] = False
        self.assert_valid(record, ROOT / "schemas" / "application-record.schema.json")

    def test_month_precision_rejects_day_value(self):
        record = json.loads((ROOT / "examples" / "fictional-demo" / "application-record.json").read_text(encoding="utf-8"))
        record["event_date"] = {"value": "2030-04-12", "precision": "month"}
        schema = json.loads((ROOT / "schemas" / "application-record.schema.json").read_text(encoding="utf-8"))
        validator = Draft202012Validator(schema, format_checker=FormatChecker())
        self.assertTrue(list(validator.iter_errors(record)))

    def test_submitted_status_requires_direct_evidence(self):
        record = json.loads((ROOT / "examples" / "fictional-demo" / "application-record.json").read_text(encoding="utf-8"))
        record["application_status"] = "submitted"
        record["event_date"] = {"value": "2030-04-14", "precision": "day"}
        record["evidence"] = [record["evidence"][0]]
        schema = json.loads((ROOT / "schemas" / "application-record.schema.json").read_text(encoding="utf-8"))
        validator = Draft202012Validator(schema, format_checker=FormatChecker())
        self.assertTrue(list(validator.iter_errors(record)))

    def test_declined_status_requires_direct_evidence(self):
        record = json.loads((ROOT / "examples" / "fictional-demo" / "application-record.json").read_text(encoding="utf-8"))
        record["application_status"] = "declined"
        record["event_date"] = {"value": "2030-04-14", "precision": "day"}
        record["evidence"] = [record["evidence"][0]]
        schema = json.loads((ROOT / "schemas" / "application-record.schema.json").read_text(encoding="utf-8"))
        validator = Draft202012Validator(schema, format_checker=FormatChecker())
        self.assertTrue(list(validator.iter_errors(record)))


if __name__ == "__main__":
    unittest.main()
