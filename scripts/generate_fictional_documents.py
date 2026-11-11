#!/usr/bin/env python3
"""Generate deterministic Markdown documents from an explicitly fictional fixture."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


REQUIRED_FIELDS = {"fictional", "candidate", "job", "guidance", "variant", "change_review", "matches"}


def load_input(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    missing = sorted(REQUIRED_FIELDS - data.keys())
    if missing:
        raise ValueError(f"missing required fields: {', '.join(missing)}")
    if data["fictional"] is not True:
        raise ValueError("document generation is limited to explicitly fictional fixtures")
    if not data["guidance"].get("sources"):
        raise ValueError("at least one guidance source is required")
    if len(data["matches"]) < 2:
        raise ValueError("at least two requirement-to-evidence matches are required")
    match_ids = [item.get("id") for item in data["matches"]]
    if None in match_ids or len(match_ids) != len(set(match_ids)):
        raise ValueError("requirement-to-evidence matches need unique IDs")
    for change in data["change_review"]:
        if change.get("decision") not in {"accepted", "rejected", "pending"}:
            raise ValueError("change decisions must be accepted, rejected, or pending")
        if not set(change.get("evidence_ids", [])).issubset(match_ids):
            raise ValueError("change review references an unknown evidence ID")
    if data["variant"].get("status") == "reviewed" and any(
        change["decision"] == "pending" for change in data["change_review"]
    ):
        raise ValueError("a reviewed variant cannot contain pending decisions")
    return data


def bullet_list(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def render_cv(data: dict) -> str:
    candidate = data["candidate"]
    job = data["job"]
    education = "\n\n".join(
        f"### {item['credential']} — {item['institution']}\n{item['period']}\n\n{item['details']}"
        for item in candidate["education"]
    )
    experience = "\n\n".join(
        f"### {item['title']} — {item['organization']}\n{item['period']}\n\n{bullet_list(item['bullets'])}"
        for item in candidate["experience"]
    )
    projects = "\n\n".join(
        f"### {item['name']}\n{bullet_list(item['bullets'])}" for item in candidate["projects"]
    )
    version_id = data["variant"]["outputs"]["cv"]
    return f"""# {candidate['name']}

> Fictional example. Version: {version_id}.

{candidate['headline']}

## Profile

{candidate['targeted_summary']}

## Experience

{experience}

## Selected project

{projects}

## Education

{education}

## Skills

{bullet_list(candidate['skills'])}

## Languages

{bullet_list(candidate['languages'])}
"""


def render_cover_letter(data: dict) -> str:
    candidate = data["candidate"]
    job = data["job"]
    first, second = data["matches"][:2]
    version_id = data["variant"]["outputs"]["cover_letter"]
    return f"""# Cover letter

> Fictional example. Version: {version_id}.

Dear {job['contact']},

I am applying for the {job['role']} position at {job['organization']}. {job['motivation']}

In my work as {first['context']}, {first['evidence']} This experience would help me {first['contribution']} In addition, {second['evidence']} I would bring the same care to {second['contribution']}

I am drawn to the role's combination of {job['focus']}. I would welcome the opportunity to discuss how my experience could support your team.

Sincerely,

{candidate['name']}
"""


def render_change_review(data: dict) -> str:
    def cell(value: str) -> str:
        return value.replace("|", "\\|").replace("\n", " ")

    rows = []
    for change in data["change_review"]:
        rows.append(
            "| {decision} | {document} | {section} | {proposal} | {rationale} | {evidence} |".format(
                decision=cell(change["decision"]),
                document=cell(change["document"]),
                section=cell(change["section"]),
                proposal=cell(change["proposal"]),
                rationale=cell(change["rationale"]),
                evidence=cell(", ".join(change["evidence_ids"])),
            )
        )
    return "\n".join(
        [
            "# Document change review",
            "",
            f"> Fictional example. Variant: {data['variant']['id']}.",
            "",
            "| Decision | Document | Section | Proposed change | Rationale | Evidence |",
            "| --- | --- | --- | --- | --- | --- |",
            *rows,
            "",
        ]
    )


def generate(input_path: Path, output_dir: Path) -> list[Path]:
    data = load_input(input_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    outputs = {
        output_dir / "fictional-cv.md": render_cv(data),
        output_dir / "fictional-cover-letter.md": render_cover_letter(data),
        output_dir / "fictional-change-review.md": render_change_review(data),
    }
    for path, content in outputs.items():
        path.write_text(content, encoding="utf-8")
    return sorted(outputs)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    for path in generate(args.input, args.output_dir):
        print(path.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
