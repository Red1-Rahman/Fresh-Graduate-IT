#!/usr/bin/env python3
# .github/scripts/validate_latex.py
"""Validation script for LaTeX documents in CI/CD pipeline."""

import json
import re
import sys
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class LaTeXDocumentConfig(BaseModel):
    """Configuration and validation rules for LaTeX documents."""

    min_chapters: int = Field(default=5, ge=1)
    max_line_length: int = Field(default=100, ge=50)
    require_toc: bool = Field(default=True)
    require_bibliography: bool = Field(default=True)
    forbidden_em_dashes: bool = Field(default=True)
    max_em_dash_count: int = Field(default=0)


class LaTeXValidationResult(BaseModel):
    """Result of LaTeX document validation."""

    file_path: str
    is_valid: bool
    chapter_count: int
    section_count: int
    em_dash_count: int = Field(default=0, ge=0)
    long_lines: int = Field(default=0, ge=0)
    has_toc: bool = False
    has_bibliography: bool = False
    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)

    @field_validator("is_valid")
    @classmethod
    def validate_status(cls, v, info):
        """Ensure is_valid is True only when no errors present."""
        if v and info.data.get("errors"):
            return False
        return v


class LaTeXDocumentValidator:
    """Validates LaTeX documents against quality standards."""

    def __init__(self, config: Optional[LaTeXDocumentConfig] = None):
        self.config = config or LaTeXDocumentConfig()

    def validate_file(self, file_path: str) -> LaTeXValidationResult:
        """Validate a single LaTeX file."""
        path = Path(file_path)

        if not path.exists():
            return LaTeXValidationResult(
                file_path=file_path,
                is_valid=False,
                chapter_count=0,
                section_count=0,
                errors=[f"File not found: {file_path}"],
            )

        try:
            content = path.read_text(encoding="utf-8")
        except Exception as e:
            return LaTeXValidationResult(
                file_path=file_path,
                is_valid=False,
                chapter_count=0,
                section_count=0,
                errors=[f"Failed to read file: {str(e)}"],
            )

        result = LaTeXValidationResult(
            file_path=file_path,
            is_valid=True,
            chapter_count=len(re.findall(r"^\\chapter", content, re.MULTILINE)),
            section_count=len(re.findall(r"^\\section", content, re.MULTILINE)),
        )

        self._check_em_dashes(content, result)
        self._check_line_length(content, result)
        self._check_toc(content, result)
        self._check_bibliography(content, result)
        self._check_chapter_count(result)

        result.is_valid = len(result.errors) == 0

        return result

    def _check_em_dashes(self, content: str, result: LaTeXValidationResult) -> None:
        """Check for improperly formatted em dashes."""
        em_dash_pattern = r"(?<![\\-])\-{3}(?!-)"
        matches = list(re.finditer(em_dash_pattern, content))
        result.em_dash_count = len(matches)

        if self.config.forbidden_em_dashes and result.em_dash_count > 0:
            result.errors.append(
                f"Found {result.em_dash_count} em dashes (---). "
                "Use appropriate LaTeX commands or rephrase with parentheses."
            )

    def _check_line_length(self, content: str, result: LaTeXValidationResult) -> None:
        """Check for lines exceeding maximum length."""
        lines = content.split("\n")
        result.long_lines = sum(1 for line in lines if len(line) > self.config.max_line_length)

        if result.long_lines > 10:
            result.warnings.append(
                f"{result.long_lines} lines exceed {self.config.max_line_length} "
                "characters (consider line wrapping for readability)."
            )

    def _check_toc(self, content: str, result: LaTeXValidationResult) -> None:
        """Check for table of contents."""
        result.has_toc = "\\tableofcontents" in content

        if self.config.require_toc and not result.has_toc:
            result.errors.append("Missing \\tableofcontents command.")

    def _check_bibliography(self, content: str, result: LaTeXValidationResult) -> None:
        """Check for bibliography."""
        result.has_bibliography = (
            "\\begin{thebibliography}" in content or "\\bibliography{" in content
        )

        if self.config.require_bibliography and not result.has_bibliography:
            result.errors.append("Missing bibliography section.")

    def _check_chapter_count(self, result: LaTeXValidationResult) -> None:
        """Check minimum chapter count."""
        if result.chapter_count < self.config.min_chapters:
            result.warnings.append(
                f"Only {result.chapter_count} chapters found "
                f"(recommended minimum: {self.config.min_chapters})."
            )


def main() -> int:
    """Entry point for validation script."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Validate LaTeX documents for quality and structure."
    )
    parser.add_argument(
        "files",
        nargs="+",
        type=str,
        help="LaTeX files to validate",
    )
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="JSON file with validation config",
    )
    parser.add_argument(
        "--json-output",
        type=str,
        default=None,
        help="Output results as JSON to this file",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as errors",
    )

    args = parser.parse_args()

    config = LaTeXDocumentConfig()
    if args.config:
        config_path = Path(args.config)
        if config_path.exists():
            config_data = json.loads(config_path.read_text())
            config = LaTeXDocumentConfig(**config_data)

    validator = LaTeXDocumentValidator(config)
    results = []
    all_valid = True

    for file_path in args.files:
        result = validator.validate_file(file_path)
        results.append(result)

        print(f"\n{'='*70}")
        print(f"File: {result.file_path}")
        print(f"{'='*70}")
        print(f"Chapters: {result.chapter_count}")
        print(f"Sections: {result.section_count}")
        print(f"Em dashes found: {result.em_dash_count}")
        print(f"Long lines: {result.long_lines}")
        print(f"Has TOC: {result.has_toc}")
        print(f"Has bibliography: {result.has_bibliography}")

        if result.errors:
            print(f"\n✗ ERRORS ({len(result.errors)}):")
            for error in result.errors:
                print(f"  - {error}")
            all_valid = False

        if result.warnings:
            print(f"\n⚠ WARNINGS ({len(result.warnings)}):")
            for warning in result.warnings:
                print(f"  - {warning}")
            if args.strict:
                all_valid = False

        if result.is_valid and not result.warnings:
            print("\n✓ Valid")

    if args.json_output:
        output_path = Path(args.json_output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_data = {
            "timestamp": __import__("datetime").datetime.now().isoformat(),
            "all_valid": all_valid,
            "results": [r.model_dump() for r in results],
        }
        output_path.write_text(json.dumps(output_data, indent=2))
        print(f"\nResults written to: {output_path}")

    print(f"\n{'='*70}")
    if all_valid:
        print("✓ All files passed validation")
        return 0
    else:
        print("✗ Validation failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
