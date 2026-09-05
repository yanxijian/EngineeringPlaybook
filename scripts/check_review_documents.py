"""Validate the required structure of a design document and its review."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Sequence


FEEDBACK_HEADING = "\u8bc4\u5ba1\u53cd\u9988\u4e0e\u91c7\u7eb3\u8bf4\u660e"
EVIDENCE_HEADING = "\u8bc4\u5ba1\u4f9d\u636e\u5bfc\u822a"
FINDING_ID_PATTERN = re.compile(r"^P[1-3]-\d{2}$")
DESIGN_ID_PATTERN = re.compile(r"^D-\d{2}$")
REPORT_ID_PATTERN = re.compile(r"(?m)^#{2,4}\s+((?:P[1-3]|D)-\d{2})\b")


@dataclass
class ValidationResult:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    summary: Optional[str] = None


def _read_document(path: Path, label: str, result: ValidationResult) -> Optional[str]:
    if not path.is_file():
        result.errors.append(f"{label} not found: {path}")
        return None

    try:
        return path.read_text(encoding="utf-8", errors="strict")
    except UnicodeDecodeError:
        result.errors.append(f"{path} is not valid UTF-8")
    except OSError as error:
        result.errors.append(f"Unable to read {path}: {error}")
    return None


def _has_heading(document: str, heading: str) -> bool:
    pattern = re.compile(r"^##\s+" + re.escape(heading) + r"\s*$", re.MULTILINE)
    return pattern.search(document) is not None


def _feedback_section(document: str) -> str:
    pattern = re.compile(
        r"^##\s+" + re.escape(FEEDBACK_HEADING) + r"\s*$\r?\n(.*?)(?=^##\s|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    match = pattern.search(document)
    return match.group(1) if match else ""


def _has_response(feedback: str, issue_id: str) -> bool:
    pattern = re.compile(r"^\|\s*" + re.escape(issue_id) + r"\s*\|", re.MULTILINE)
    return pattern.search(feedback) is not None


def validate_documents(
    design_path: Path | str,
    review_path: Path | str | None = None,
    require_design_responses: bool = False,
) -> ValidationResult:
    """Return structural errors and warnings without writing to stdout or stderr."""
    result = ValidationResult()
    design = Path(design_path).resolve()
    design_text = _read_document(design, "Design document", result)
    if design_text is None:
        return result

    if not _has_heading(design_text, FEEDBACK_HEADING):
        result.errors.append("Design document is missing the review feedback and adoption section.")
    if not _has_heading(design_text, EVIDENCE_HEADING):
        result.errors.append("Design document is missing the review evidence navigation section.")
    design_structure_is_valid = not result.errors

    if review_path is None:
        if not result.errors:
            result.summary = "Design preflight passed. No review report was supplied."
        return result

    review = Path(review_path).resolve()
    review_text = _read_document(review, "Review report", result)
    if review_text is None or not design_structure_is_valid:
        return result

    expected_name = f"{design.stem}-review.md"
    if design.parent != review.parent:
        result.errors.append("Review report must be in the same directory as the design document.")
    if review.name != expected_name:
        result.errors.append(
            f"Review report name must be {expected_name} for this design document."
        )

    feedback = _feedback_section(design_text)
    report_ids = REPORT_ID_PATTERN.findall(review_text)
    duplicate_ids = sorted({issue_id for issue_id in report_ids if report_ids.count(issue_id) > 1})
    finding_ids = sorted({issue_id for issue_id in report_ids if FINDING_ID_PATTERN.fullmatch(issue_id)})
    design_ids = sorted({issue_id for issue_id in report_ids if DESIGN_ID_PATTERN.fullmatch(issue_id)})

    if not finding_ids:
        result.errors.append("Review report has no P1-01, P2-01, or P3-01 finding IDs.")
    for issue_id in duplicate_ids:
        result.errors.append(f"Review report contains a duplicate ID: {issue_id}")
    for issue_id in finding_ids:
        if not _has_response(feedback, issue_id):
            result.errors.append(
                f"Design feedback section does not respond to finding: {issue_id}"
            )
    for issue_id in design_ids:
        if _has_response(feedback, issue_id):
            continue
        message = f"Design feedback section does not respond to design suggestion: {issue_id}"
        if require_design_responses:
            result.errors.append(message)
        else:
            result.warnings.append(message)

    if not result.errors:
        result.summary = f"Review document structure passed. Findings checked: {len(finding_ids)}."
    return result


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--design-path", required=True, type=Path)
    parser.add_argument("--review-path", type=Path)
    parser.add_argument("--require-design-responses", action="store_true")
    return parser


def main(arguments: Optional[Sequence[str]] = None) -> int:
    options = _build_parser().parse_args(arguments)
    result = validate_documents(
        options.design_path,
        options.review_path,
        options.require_design_responses,
    )
    for warning in result.warnings:
        print(f"WARNING: {warning}")
    for error in result.errors:
        print(f"ERROR: {error}")
    if result.errors:
        return 1
    if result.summary:
        print(result.summary)
    return 0


if __name__ == "__main__":
    sys.exit(main())