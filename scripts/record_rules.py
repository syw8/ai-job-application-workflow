#!/usr/bin/env python3
"""Business-rule checks that complement the application-record JSON Schema."""

from __future__ import annotations

from datetime import date
import re


CONSEQUENTIAL_STATUSES = {"submitted", "interviewing", "offer", "rejected", "withdrawn", "declined"}
DIRECT_EVIDENCE = {"user_confirmation", "direct_communication"}


def has_direct_evidence(record: dict) -> bool:
    return any(item.get("kind") in DIRECT_EVIDENCE for item in record.get("evidence", []))


def date_precision_issue(event_date: dict | None) -> str | None:
    if event_date is None:
        return None
    precision = event_date.get("precision")
    value = event_date.get("value", "")
    if precision == "day":
        try:
            date.fromisoformat(value)
        except (TypeError, ValueError):
            return "invalid-day-precision"
    elif precision == "month" and not re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])", value):
        return "invalid-month-precision"
    elif precision == "year" and not re.fullmatch(r"\d{4}", value):
        return "invalid-year-precision"
    elif precision == "range":
        parts = value.split("/")
        if len(parts) != 2:
            return "invalid-range-precision"
        bounds = []
        for part in parts:
            if re.fullmatch(r"\d{4}", part):
                bounds.append((int(part), 1, 1))
            elif re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])", part):
                year, month = part.split("-")
                bounds.append((int(year), int(month), 1))
            else:
                try:
                    parsed = date.fromisoformat(part)
                except (TypeError, ValueError):
                    return "invalid-range-precision"
                bounds.append((parsed.year, parsed.month, parsed.day))
        if bounds[0] > bounds[1]:
            return "reversed-date-range"
    elif precision == "unknown" and value != "unknown":
        return "invalid-unknown-precision"
    elif precision not in {"day", "month", "year", "range", "unknown"}:
        return "unsupported-date-precision"
    return None


def review_reasons(record: dict, peers: list[dict] | None = None) -> list[str]:
    reasons: list[str] = []
    peers = peers or []
    status = record.get("application_status")

    if status in CONSEQUENTIAL_STATUSES:
        if not has_direct_evidence(record):
            reasons.append("unsupported-consequential-status")
        if record.get("review_required") is not True:
            reasons.append("consequential-status-requires-human-review")
        if record.get("event_date") is None:
            reasons.append("consequential-status-date-needs-review")

    materials = record.get("materials", {})
    if materials.get("confirmed_uploaded") and not has_direct_evidence(record):
        reasons.append("unsupported-upload-claim")
    if materials.get("confirmed_submitted") and not has_direct_evidence(record):
        reasons.append("unsupported-submitted-material-claim")

    versions = materials.get("document_versions", [])
    version_ids = [item.get("id") for item in versions]
    known_versions = set(version_ids)
    if len(version_ids) != len(known_versions):
        reasons.append("duplicate-document-version-id")
    referenced_versions = set(materials.get("available_locally", []))
    referenced_versions.update(materials.get("confirmed_uploaded", []))
    referenced_versions.update(materials.get("confirmed_submitted", []))
    if referenced_versions - known_versions:
        reasons.append("unknown-document-version-reference")
    reviewed_versions = {item.get("id") for item in versions if item.get("review_state") == "reviewed"}
    confirmed_versions = set(materials.get("confirmed_uploaded", [])) | set(materials.get("confirmed_submitted", []))
    if confirmed_versions - reviewed_versions:
        reasons.append("unreviewed-confirmed-document-version")
    requisition = record.get("requisition_id")
    if requisition and any(
        item.get("target_requisition_id") not in {None, requisition}
        for item in versions
    ):
        reasons.append("document-version-target-mismatch")

    date_issue = date_precision_issue(record.get("event_date"))
    if date_issue:
        reasons.append(date_issue)

    organization = str(record.get("organization", "")).casefold()
    if requisition:
        duplicates = [
            peer for peer in peers
            if peer.get("id") != record.get("id")
            and peer.get("requisition_id") == requisition
            and str(peer.get("organization", "")).casefold() == organization
        ]
        if duplicates:
            reasons.append("duplicate-requisition-needs-review")
            if record.get("possible_duplicate") is not True:
                reasons.append("duplicate-requisition-not-flagged")

    adapter_states = record.get("adapter_states", {})
    active_statuses = set()
    for state in adapter_states.values():
        adapter_state = state.get("state")
        adapter_status = state.get("application_status")
        if adapter_state in {"needs_review", "failed"}:
            reasons.append("adapter-state-needs-review")
        if adapter_state == "disabled" and adapter_status is not None:
            reasons.append("disabled-adapter-has-status")
        if adapter_state != "disabled" and adapter_status is not None:
            active_statuses.add(adapter_status)
    if len(active_statuses) > 1 or (active_statuses and status not in active_statuses):
        reasons.append("inconsistent-adapter-status")

    return sorted(set(reasons))


def config_review_reasons(config: dict) -> list[str]:
    reasons: list[str] = []
    versioning = config.get("documents", {}).get("versioning", {})
    if versioning.get("require_decided_change_set") is not True:
        reasons.append("document-change-decisions-not-required")
    cv = config.get("documents", {}).get("cv", {})
    editable = set(cv.get("editable_sections", []))
    if len(editable) < 3 or "experience" not in editable:
        reasons.append("cv-tailoring-scope-too-narrow")
    if cv.get("fact_changes_require_confirmation") is not True:
        reasons.append("cv-fact-changes-not-protected")
    protected_facts = set(cv.get("protected_fact_types", []))
    if not {"dates", "credentials", "organizations"}.issubset(protected_facts):
        reasons.append("cv-core-facts-not-protected")

    search = config.get("job_search", {})
    if not search.get("roles") or not search.get("locations"):
        reasons.append("job-search-criteria-incomplete")
    if search.get("official_detail_page_required") is not True:
        reasons.append("primary-job-page-not-required")

    research = config.get("research", {})
    if research.get("source_policy") != "official_first":
        reasons.append("official-guidance-not-prioritized")
    if research.get("require_primary_vacancy") is not True:
        reasons.append("primary-vacancy-not-required")

    adapters = config.get("tracker", {}).get("adapters", {})
    if not any(adapter.get("enabled") for adapter in adapters.values()):
        reasons.append("no-tracker-adapter-enabled")
    for name, adapter in adapters.items():
        expected = {"configured", "needs_review"} if adapter.get("enabled") else {"disabled"}
        if adapter.get("state") not in expected:
            reasons.append(f"inconsistent-adapter-config:{name}")
    return sorted(set(reasons))
