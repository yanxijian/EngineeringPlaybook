"""Tests for the cross-platform review document checker."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPTS_DIRECTORY = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS_DIRECTORY))

from check_review_documents import validate_documents


FIXTURES_DIRECTORY = Path(__file__).resolve().parent / "fixtures"
CHECKER_PATH = SCRIPTS_DIRECTORY / "check_review_documents.py"


class ReviewDocumentValidationTests(unittest.TestCase):
    def assert_validation(
        self,
        design_name: str,
        review_name: str | None,
        expected_errors: list[str],
        expected_warnings: list[str] | None = None,
        expected_summary: str | None = None,
        require_design_responses: bool = False,
    ) -> None:
        review_path = FIXTURES_DIRECTORY / review_name if review_name else None
        result = validate_documents(
            FIXTURES_DIRECTORY / design_name,
            review_path,
            require_design_responses,
        )
        self.assertEqual(expected_errors, result.errors)
        self.assertEqual(expected_warnings or [], result.warnings)
        self.assertEqual(expected_summary, result.summary)

    def test_existing_fixtures(self) -> None:
        cases = [
            (
                "preflight",
                "feature-plan.md",
                None,
                [],
                [],
                "Design preflight passed. No review report was supplied.",
            ),
            (
                "review",
                "feature-plan.md",
                "feature-plan-review.md",
                [],
                [],
                "Review document structure passed. Findings checked: 1.",
            ),
            (
                "design suggestion warning",
                "unanswered-design-suggestion-plan.md",
                "unanswered-design-suggestion-plan-review.md",
                [],
                ["Design feedback section does not respond to design suggestion: D-01"],
                "Review document structure passed. Findings checked: 1.",
            ),
            (
                "missing feedback section",
                "missing-feedback-plan.md",
                "missing-feedback-plan-review.md",
                ["Design document is missing the review feedback and adoption section."],
                [],
                None,
            ),
            (
                "unanswered finding",
                "unanswered-finding-plan.md",
                "unanswered-finding-plan-review.md",
                ["Design feedback section does not respond to finding: P2-01"],
                [],
                None,
            ),
            (
                "duplicate ID",
                "duplicate-id-plan.md",
                "duplicate-id-plan-review.md",
                ["Review report contains a duplicate ID: P2-01"],
                [],
                None,
            ),
            (
                "wrong review name",
                "feature-plan.md",
                "wrong-name-review.md",
                ["Review report name must be feature-plan-review.md for this design document."],
                [],
                None,
            ),
            (
                "multiple diagnostics",
                "feature-plan.md",
                "multiple-errors-review.md",
                [
                    "Review report name must be feature-plan-review.md for this design document.",
                    "Review report has no P1-01, P2-01, or P3-01 finding IDs.",
                ],
                [],
                None,
            ),
        ]
        for name, design, review, errors, warnings, summary in cases:
            with self.subTest(name=name):
                self.assert_validation(design, review, errors, warnings, summary)

    def test_existing_fixture_strict_design_suggestion(self) -> None:
        self.assert_validation(
            "unanswered-design-suggestion-plan.md",
            "unanswered-design-suggestion-plan-review.md",
            ["Design feedback section does not respond to design suggestion: D-01"],
            expected_summary=None,
            require_design_responses=True,
        )

    def test_missing_review_report(self) -> None:
        result = validate_documents(
            FIXTURES_DIRECTORY / "feature-plan.md",
            FIXTURES_DIRECTORY / "missing-review.md",
        )
        self.assertEqual(1, len(result.errors))
        self.assertTrue(result.errors[0].startswith("Review report not found: "))

    def test_missing_design_document(self) -> None:
        result = validate_documents(FIXTURES_DIRECTORY / "missing-plan.md")
        self.assertEqual(1, len(result.errors))
        self.assertTrue(result.errors[0].startswith("Design document not found: "))

    def test_invalid_utf8_documents(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            invalid_design = root / "invalid-plan.md"
            invalid_design.write_bytes(b"\x80")
            result = validate_documents(invalid_design)
            self.assertEqual([f"{invalid_design.resolve()} is not valid UTF-8"], result.errors)

            design = root / "valid-plan.md"
            design.write_text(
                "## \u8bc4\u5ba1\u4f9d\u636e\u5bfc\u822a\n\n## \u8bc4\u5ba1\u53cd\u9988\u4e0e\u91c7\u7eb3\u8bf4\u660e\n",
                encoding="utf-8",
            )
            invalid_review = root / "valid-plan-review.md"
            invalid_review.write_bytes(b"\x80")
            result = validate_documents(design, invalid_review)
            self.assertEqual([f"{invalid_review.resolve()} is not valid UTF-8"], result.errors)

    def run_cli(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        environment = os.environ.copy()
        environment["PYTHONUTF8"] = "1"
        return subprocess.run(
            [sys.executable, str(CHECKER_PATH), *arguments],
            check=False,
            text=True,
            encoding="utf-8",
            env=environment,
            capture_output=True,
        )

    def test_cli_success_and_argument_contract(self) -> None:
        success = self.run_cli("--design-path", str(FIXTURES_DIRECTORY / "feature-plan.md"))
        self.assertEqual(0, success.returncode)
        self.assertIn("Design preflight passed.", success.stdout)

        review_success = self.run_cli(
            "--design-path",
            str(FIXTURES_DIRECTORY / "feature-plan.md"),
            "--review-path",
            str(FIXTURES_DIRECTORY / "feature-plan-review.md"),
        )
        self.assertEqual(0, review_success.returncode)
        self.assertIn(
            "Review document structure passed. Findings checked: 1.", review_success.stdout
        )

        help_result = self.run_cli("--help")
        self.assertEqual(0, help_result.returncode)
        self.assertIn("--design-path", help_result.stdout)

        missing_argument = self.run_cli()
        self.assertEqual(2, missing_argument.returncode)
        self.assertEqual("", missing_argument.stdout)
        self.assertTrue(missing_argument.stderr.startswith("usage:"))

    def test_cli_utf8_output_with_non_ascii_path(self) -> None:
        with tempfile.TemporaryDirectory(prefix="review-\u6d4b\u8bd5-") as temporary_directory:
            root = Path(temporary_directory)
            invalid_design = root / "invalid-design.md"
            invalid_design.write_bytes(b"\x80")
            design_result = self.run_cli("--design-path", str(invalid_design))
            self.assertEqual(1, design_result.returncode)
            self.assertIn("ERROR:", design_result.stdout)
            self.assertIn("is not valid UTF-8", design_result.stdout)
            self.assertEqual("", design_result.stderr)

            valid_design = root / "valid-plan.md"
            valid_design.write_text(
                "## \u8bc4\u5ba1\u4f9d\u636e\u5bfc\u822a\n\n## \u8bc4\u5ba1\u53cd\u9988\u4e0e\u91c7\u7eb3\u8bf4\u660e\n",
                encoding="utf-8",
            )
            invalid_review = root / "valid-plan-review.md"
            invalid_review.write_bytes(b"\x80")
            review_result = self.run_cli(
                "--design-path", str(valid_design), "--review-path", str(invalid_review)
            )
            self.assertEqual(1, review_result.returncode)
            self.assertIn("ERROR:", review_result.stdout)
            self.assertIn("is not valid UTF-8", review_result.stdout)
            self.assertEqual("", review_result.stderr)


if __name__ == "__main__":
    unittest.main()