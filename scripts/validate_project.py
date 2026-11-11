#!/usr/bin/env python3
"""Validate the manifest, configuration, examples, and Skill structure."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

import yaml
from jsonschema import Draft202012Validator, FormatChecker

from record_rules import config_review_reasons, review_reasons


FRONTMATTER = re.compile(r"\A---\n(?P<header>.*?)\n---\n", re.DOTALL)


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def is_git_tracked(root: Path, relative: str) -> bool:
    result = subprocess.run(
        ["git", "ls-files", "--error-unmatch", relative],
        cwd=root,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return result.returncode == 0


def validate_instance(instance, schema, label: str) -> list[str]:
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    return [f"{label}: {error.message}" for error in sorted(validator.iter_errors(instance), key=lambda item: list(item.path))]


def validate_skills(root: Path) -> list[str]:
    errors: list[str] = []
    for folder in sorted((root / "skills").iterdir()):
        if not folder.is_dir():
            continue
        skill_file = folder / "SKILL.md"
        metadata_file = folder / "agents" / "openai.yaml"
        if not skill_file.is_file():
            errors.append(f"{folder.name}: missing SKILL.md")
            continue
        match = FRONTMATTER.match(skill_file.read_text(encoding="utf-8"))
        if not match:
            errors.append(f"{folder.name}: invalid YAML frontmatter boundary")
            continue
        header = yaml.safe_load(match.group("header"))
        if header.get("name") != folder.name:
            errors.append(f"{folder.name}: frontmatter name does not match folder")
        if not isinstance(header.get("description"), str) or len(header["description"].strip()) < 20:
            errors.append(f"{folder.name}: description is missing or too short")
        if not metadata_file.is_file():
            errors.append(f"{folder.name}: missing agents/openai.yaml")
        else:
            metadata = yaml.safe_load(metadata_file.read_text(encoding="utf-8"))
            prompt = metadata.get("interface", {}).get("default_prompt", "")
            if f"${folder.name}" not in prompt:
                errors.append(f"{folder.name}: default_prompt must mention ${folder.name}")
    return errors


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    required_fixtures = [
        "examples/fictional-demo/README.md",
        "examples/fictional-demo/application-record.json",
        "examples/fictional-demo/candidate-profile.example.yaml",
        "examples/fictional-demo/document-input.json",
        "examples/fictional-demo/generated/fictional-change-review.md",
        "examples/fictional-demo/generated/fictional-cover-letter.md",
        "examples/fictional-demo/generated/fictional-cv.md",
        "examples/fictional-demo/job-lead.json",
    ]
    for relative in required_fixtures:
        if not (root / relative).is_file():
            errors.append(f"missing required fictional fixture: {relative}")
    if errors:
        return errors

    manifest = load_json(root / "plugin.json")
    if manifest.get("name") != "ai-job-application-workflow":
        errors.append("plugin.json: unexpected plugin name")
    if not re.fullmatch(r"\d+\.\d+\.\d+", str(manifest.get("version", ""))):
        errors.append("plugin.json: version must use semantic version format")

    config = yaml.safe_load((root / "config.example.yaml").read_text(encoding="utf-8"))
    config_schema = load_json(root / "schemas" / "config.schema.json")
    errors.extend(validate_instance(config, config_schema, "config.example.yaml"))
    errors.extend(f"config business rule: {reason}" for reason in config_review_reasons(config))

    record = load_json(root / "examples" / "fictional-demo" / "application-record.json")
    record_schema = load_json(root / "schemas" / "application-record.schema.json")
    errors.extend(validate_instance(record, record_schema, "fictional application record"))
    errors.extend(f"fictional application record: {reason}" for reason in review_reasons(record))

    lead = load_json(root / "examples" / "fictional-demo" / "job-lead.json")
    document_input = load_json(root / "examples" / "fictional-demo" / "document-input.json")
    candidate_profile = yaml.safe_load(
        (root / "examples" / "fictional-demo" / "candidate-profile.example.yaml").read_text(encoding="utf-8")
    )
    public_demo_inputs = [lead, record, document_input, candidate_profile]
    if any(item.get("fictional") is not True for item in public_demo_inputs):
        errors.append("fictional fixtures must declare fictional: true")
    for relative in [
        "examples/fictional-demo/generated/fictional-change-review.md",
        "examples/fictional-demo/generated/fictional-cover-letter.md",
        "examples/fictional-demo/generated/fictional-cv.md",
    ]:
        if "Fictional example." not in (root / relative).read_text(encoding="utf-8"):
            errors.append(f"generated public fixture is missing its fictional banner: {relative}")
    for label, value in [("job lead", lead.get("url", "")), ("application record", record.get("source_url", ""))]:
        if urlparse(value).hostname != "example.com":
            errors.append(f"{label}: public fixture URLs must use example.com")

    if (root / ".git").exists():
        for relative in required_fixtures:
            if not is_git_tracked(root, relative):
                errors.append(f"required fictional fixture is not Git-tracked: {relative}")

    errors.extend(validate_skills(root))
    return errors


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    errors = validate(root)
    if errors:
        print("Project validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Project validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
