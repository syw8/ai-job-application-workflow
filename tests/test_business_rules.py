import copy
import importlib.util
import json
import sys
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("record_rules", ROOT / "scripts" / "record_rules.py")
RECORD_RULES = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = RECORD_RULES
SPEC.loader.exec_module(RECORD_RULES)


def fictional_record():
    return json.loads((ROOT / "examples" / "fictional-demo" / "application-record.json").read_text(encoding="utf-8"))


class BusinessRuleTests(unittest.TestCase):
    def test_fictional_record_needs_no_additional_review_reason(self):
        self.assertEqual([], RECORD_RULES.review_reasons(fictional_record()))

    def test_unsupported_submission_claim_is_detected(self):
        record = fictional_record()
        record["application_status"] = "submitted"
        record["event_date"] = {"value": "2030-04-14", "precision": "day"}
        record["evidence"] = [record["evidence"][0]]
        self.assertIn("unsupported-consequential-status", RECORD_RULES.review_reasons(record))

    def test_missing_submission_date_is_sent_for_review(self):
        record = fictional_record()
        record["application_status"] = "submitted"
        self.assertIn("consequential-status-date-needs-review", RECORD_RULES.review_reasons(record))

    def test_declined_without_direct_evidence_is_detected(self):
        record = fictional_record()
        record["application_status"] = "declined"
        record["event_date"] = {"value": "2030-04-14", "precision": "day"}
        record["evidence"] = [record["evidence"][0]]
        self.assertIn("unsupported-consequential-status", RECORD_RULES.review_reasons(record))

    def test_declined_with_consistent_evidence_and_adapters_passes(self):
        record = fictional_record()
        record["application_status"] = "declined"
        record["event_date"] = {"value": "2030-04-14", "precision": "day"}
        for state in record["adapter_states"].values():
            state["application_status"] = "declined"
        self.assertEqual([], RECORD_RULES.review_reasons(record))

    def test_uploaded_material_without_direct_evidence_is_detected(self):
        record = fictional_record()
        record["materials"]["confirmed_uploaded"] = ["CL-CFL-2030-17-V1"]
        record["evidence"] = [record["evidence"][0]]
        self.assertIn("unsupported-upload-claim", RECORD_RULES.review_reasons(record))

    def test_unknown_document_version_reference_is_detected(self):
        record = fictional_record()
        record["materials"]["available_locally"].append("CV-UNKNOWN-V1")
        self.assertIn("unknown-document-version-reference", RECORD_RULES.review_reasons(record))

    def test_duplicate_document_version_id_is_detected(self):
        record = fictional_record()
        record["materials"]["document_versions"].append(
            copy.deepcopy(record["materials"]["document_versions"][0])
        )
        self.assertIn("duplicate-document-version-id", RECORD_RULES.review_reasons(record))

    def test_unreviewed_confirmed_document_is_detected(self):
        record = fictional_record()
        record["materials"]["document_versions"][0]["review_state"] = "draft"
        record["materials"]["confirmed_submitted"] = ["CV-CFL-2030-17-V1"]
        self.assertIn("unreviewed-confirmed-document-version", RECORD_RULES.review_reasons(record))

    def test_document_version_for_another_requisition_is_detected(self):
        record = fictional_record()
        record["materials"]["document_versions"][0]["target_requisition_id"] = "OTHER-99"
        self.assertIn("document-version-target-mismatch", RECORD_RULES.review_reasons(record))

    def test_duplicate_requisition_is_sent_for_review(self):
        record = fictional_record()
        peer = copy.deepcopy(record)
        peer["id"] = "APP-002"
        reasons = RECORD_RULES.review_reasons(record, [peer])
        self.assertIn("duplicate-requisition-needs-review", reasons)
        self.assertIn("duplicate-requisition-not-flagged", reasons)

    def test_inconsistent_adapter_status_is_detected(self):
        record = fictional_record()
        record["adapter_states"]["markdown"]["application_status"] = "submitted"
        self.assertIn("inconsistent-adapter-status", RECORD_RULES.review_reasons(record))

    def test_failed_adapter_is_sent_for_review(self):
        record = fictional_record()
        record["adapter_states"]["markdown"]["state"] = "failed"
        self.assertIn("adapter-state-needs-review", RECORD_RULES.review_reasons(record))

    def test_month_precision_accepts_month_only(self):
        event = {"value": "2030-04", "precision": "month"}
        self.assertIsNone(RECORD_RULES.date_precision_issue(event))

    def test_month_precision_rejects_full_day(self):
        event = {"value": "2030-04-12", "precision": "month"}
        self.assertEqual("invalid-month-precision", RECORD_RULES.date_precision_issue(event))

    def test_invalid_calendar_day_is_detected(self):
        event = {"value": "2030-02-30", "precision": "day"}
        self.assertEqual("invalid-day-precision", RECORD_RULES.date_precision_issue(event))

    def test_invalid_calendar_day_in_range_is_detected(self):
        event = {"value": "2030-02-30/2030-03-02", "precision": "range", "original": "late February to early March"}
        self.assertEqual("invalid-range-precision", RECORD_RULES.date_precision_issue(event))

    def test_reversed_range_is_detected(self):
        event = {"value": "2030-05/2030-04", "precision": "range", "original": "May to April"}
        self.assertEqual("reversed-date-range", RECORD_RULES.date_precision_issue(event))

    def test_example_config_has_consistent_adapter_states(self):
        config = yaml.safe_load((ROOT / "config.example.yaml").read_text(encoding="utf-8"))
        self.assertEqual([], RECORD_RULES.config_review_reasons(config))

    def test_narrow_cv_scope_is_detected(self):
        config = yaml.safe_load((ROOT / "config.example.yaml").read_text(encoding="utf-8"))
        config["documents"]["cv"]["editable_sections"] = ["research_interests"]
        self.assertIn("cv-tailoring-scope-too-narrow", RECORD_RULES.config_review_reasons(config))

    def test_unprotected_cv_facts_are_detected(self):
        config = yaml.safe_load((ROOT / "config.example.yaml").read_text(encoding="utf-8"))
        config["documents"]["cv"]["fact_changes_require_confirmation"] = False
        self.assertIn("cv-fact-changes-not-protected", RECORD_RULES.config_review_reasons(config))

    def test_missing_job_search_criteria_are_detected(self):
        config = yaml.safe_load((ROOT / "config.example.yaml").read_text(encoding="utf-8"))
        config["job_search"]["roles"] = []
        self.assertIn("job-search-criteria-incomplete", RECORD_RULES.config_review_reasons(config))

    def test_nonofficial_research_policy_is_detected(self):
        config = yaml.safe_load((ROOT / "config.example.yaml").read_text(encoding="utf-8"))
        config["research"]["source_policy"] = "anything"
        self.assertIn("official-guidance-not-prioritized", RECORD_RULES.config_review_reasons(config))


if __name__ == "__main__":
    unittest.main()
