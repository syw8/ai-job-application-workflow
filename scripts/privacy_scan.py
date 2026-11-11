#!/usr/bin/env python3
"""Scan a repository for common privacy and credential hazards."""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


SKIP_DIRS = {".git", ".venv", "__pycache__", ".pytest_cache"}
BINARY_SUFFIXES = {
    ".docx", ".xlsx", ".xls", ".pdf", ".odt", ".pages", ".eml", ".msg",
    ".pem", ".key", ".p12", ".pfx",
}


@dataclass(frozen=True)
class Finding:
    path: Path
    line: int
    rule: str


def _patterns() -> list[tuple[str, re.Pattern[str]]]:
    users = "/" + "Users" + "/"
    home = "/" + "home" + "/"
    windows = "C:" + "\\\\" + "Users" + "\\\\"
    private_key = "BEGIN " + "PRIVATE KEY"
    grade_abbreviation = "G" + "PA"
    grade_phrase = "grade point " + "average"
    rank_phrase = "class " + "rank"
    slack_prefix = "xox" + "b-"
    google_prefix = "AI" + "za"
    return [
        ("macos-home-path", re.compile(re.escape(users) + r"[^\s'\"`<>]+")),
        ("linux-home-path", re.compile(re.escape(home) + r"[^\s'\"`<>]+")),
        ("windows-home-path", re.compile(re.escape(windows), re.IGNORECASE)),
        ("private-key", re.compile(private_key)),
        ("openai-style-token", re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b")),
        ("github-token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b")),
        ("aws-access-key", re.compile(r"\bAKIA[A-Z0-9]{16}\b")),
        ("jwt", re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b")),
        ("slack-token", re.compile(rf"\b{slack_prefix}[A-Za-z0-9-]{{20,}}\b")),
        ("google-api-key", re.compile(rf"\b{google_prefix}[A-Za-z0-9_-]{{30,}}\b")),
        ("non-example-email", re.compile(r"\b[A-Z0-9._%+-]+@(?!example\.(?:com|org|net)\b)[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)),
        ("international-phone-number", re.compile(r"(?<!\w)\+[1-9][0-9 ()-]{7,}[0-9]")),
        ("local-phone-number", re.compile(r"(?<!\w)(?:\(?0\d{2,5}\)?[ ./-])(?:\d[ ./-]?){6,10}(?!\w)")),
        ("north-american-phone-number", re.compile(r"(?<!\w)\(?[2-9]\d{2}\)?[ .-]\d{3}[ .-]\d{4}(?!\w)")),
        ("candidate-grade", re.compile(rf"\b(?:{grade_abbreviation}|{grade_phrase}|{rank_phrase}|top\s+\d+(?:\.\d+)?%)\b", re.IGNORECASE)),
        ("private-record-filename", re.compile(r"\b(?:records\.json|application[_ -]?timeline\.docx)\b", re.IGNORECASE)),
    ]


def iter_files(root: Path) -> Iterable[Path]:
    for current, dirs, files in os.walk(root):
        dirs[:] = [name for name in dirs if name not in SKIP_DIRS]
        for name in files:
            yield Path(current) / name


def load_denylist(path: Path | None) -> list[str]:
    if path is None:
        return []
    values = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        value = raw.strip()
        if value and not value.startswith("#"):
            values.append(value)
    return values


def scan(root: Path, denylist: list[str] | None = None) -> list[Finding]:
    root = root.resolve()
    findings: list[Finding] = []
    denylist = denylist or []
    patterns = _patterns()

    for path in iter_files(root):
        relative = path.relative_to(root)
        if path.suffix.lower() in BINARY_SUFFIXES:
            findings.append(Finding(relative, 0, "blocked-binary-artifact"))
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            findings.append(Finding(relative, 0, "unreadable-or-binary"))
            continue

        for line_number, line in enumerate(text.splitlines(), start=1):
            for rule, pattern in patterns:
                if rule == "private-record-filename" and relative == Path(".gitignore"):
                    continue
                if pattern.search(line):
                    findings.append(Finding(relative, line_number, rule))
            lowered = line.casefold()
            for value in denylist:
                if value.casefold() in lowered:
                    findings.append(Finding(relative, line_number, "private-denylist"))
    return findings


def format_finding(finding: Finding, ordinal: int) -> str:
    """Return a useful location without printing filenames or matched content."""
    file_id = hashlib.sha256(finding.path.as_posix().encode("utf-8")).hexdigest()[:12]
    line = f":{finding.line}" if finding.line else ""
    return f"finding-{ordinal}: {finding.rule} in file-{file_id}{line}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".", type=Path)
    parser.add_argument("--denylist", type=Path, help="Private denylist stored outside the repository")
    args = parser.parse_args()

    findings = scan(args.root, load_denylist(args.denylist))
    if findings:
        for ordinal, finding in enumerate(findings, start=1):
            print(format_finding(finding, ordinal))
        print(f"Privacy scan failed with {len(findings)} finding(s).", file=sys.stderr)
        return 1

    print("Privacy scan passed: no blocked patterns or artifacts found.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
