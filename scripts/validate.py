#!/usr/bin/env python3
"""Validate skill manifests against the JSON Schema and structural rules.

Usage:
    python scripts/validate.py                 # validate every manifest
    python scripts/validate.py --strict        # fail on warnings too
    python scripts/validate.py --manifest PATH # validate one manifest

Exit code is 0 when every manifest passes, 1 otherwise.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

try:
    import yaml
except ImportError:  # pragma: no cover - exercised on a bare interpreter
    sys.stderr.write(
        "error: pyyaml is required. Install with: pip install pyyaml jsonschema\n"
    )
    sys.exit(2)

try:
    from jsonschema import Draft202012Validator
except ImportError:  # pragma: no cover
    sys.stderr.write(
        "error: jsonschema is required. Install with: pip install pyyaml jsonschema\n"
    )
    sys.exit(2)


REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = REPO_ROOT / "schema" / "skill-manifest.schema.json"
SKILLS_ROOT = REPO_ROOT / "skills"

SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")

# License policy: see LICENSING.md.
DEFAULT_LICENSE = "Apache-2.0"
ACCEPTED_LICENSES = frozenset(
    {"Apache-2.0", "MIT", "BSD-2-Clause", "BSD-3-Clause", "ISC"}
)
# Patterns for SPDX identifiers we explicitly reject so we can emit a
# policy-aware error rather than the generic "not in enum" message.
REJECTED_LICENSE_PATTERNS = (
    re.compile(r"^GPL(-.*)?$", re.IGNORECASE),
    re.compile(r"^LGPL(-.*)?$", re.IGNORECASE),
    re.compile(r"^AGPL(-.*)?$", re.IGNORECASE),
    re.compile(r"^SSPL(-.*)?$", re.IGNORECASE),
    re.compile(r"^BUSL(-.*)?$", re.IGNORECASE),  # Business Source License
    re.compile(r"^BSL(-.*)?$", re.IGNORECASE),
    re.compile(r"^Elastic(-.*)?$", re.IGNORECASE),
    re.compile(r"^CC-BY-NC(-.*)?$", re.IGNORECASE),
    re.compile(r"^Commons-Clause$", re.IGNORECASE),
    re.compile(r"^Proprietary$", re.IGNORECASE),
    re.compile(r"^.*-NC(-.*)?$", re.IGNORECASE),  # any non-commercial CC variant
)


def _check_license(value) -> str | None:
    """Return an error string when ``value`` violates the license policy.

    ``value`` is the raw ``license`` field from the manifest (may be ``None``
    or missing — both fall back to :data:`DEFAULT_LICENSE`). Schema validation
    has already rejected non-string/non-null values, so here we only enforce
    the additional policy text from ``LICENSING.md``.
    """
    if value is None:
        return None
    if not isinstance(value, str):
        return None  # caught by JSON Schema already
    if value in ACCEPTED_LICENSES:
        return None
    for pattern in REJECTED_LICENSE_PATTERNS:
        if pattern.match(value):
            return (
                f"license '{value}' is on the rejected list. See LICENSING.md."
            )
    accepted = ", ".join(sorted(ACCEPTED_LICENSES))
    return (
        f"license '{value}' is not in the accepted SPDX list ({accepted})."
    )


@dataclass
class ManifestReport:
    path: Path
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


def load_schema() -> dict:
    if not SCHEMA_PATH.exists():
        raise SystemExit(f"error: schema not found at {SCHEMA_PATH}")
    with SCHEMA_PATH.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def discover_manifests(explicit: Path | None) -> list[Path]:
    if explicit is not None:
        if not explicit.exists():
            raise SystemExit(f"error: manifest not found: {explicit}")
        return [explicit.resolve()]
    if not SKILLS_ROOT.exists():
        return []
    return sorted(SKILLS_ROOT.rglob("manifest.yaml"))


def _line_for_key(text: str, key: str) -> int | None:
    """Best-effort line lookup for a top-level YAML key."""
    pattern = re.compile(rf"^{re.escape(key)}\s*:", re.MULTILINE)
    match = pattern.search(text)
    if not match:
        return None
    return text.count("\n", 0, match.start()) + 1


def _format_pointer(error) -> str:
    if not error.absolute_path:
        return "<root>"
    parts: list[str] = []
    for piece in error.absolute_path:
        if isinstance(piece, int):
            parts.append(f"[{piece}]")
        else:
            if parts:
                parts.append(f".{piece}")
            else:
                parts.append(str(piece))
    return "".join(parts)


def validate_one(
    manifest_path: Path, validator: Draft202012Validator
) -> ManifestReport:
    report = ManifestReport(path=manifest_path)
    try:
        raw_text = manifest_path.read_text(encoding="utf-8")
    except OSError as exc:
        report.errors.append(f"unreadable: {exc}")
        return report

    try:
        data = yaml.safe_load(raw_text)
    except yaml.YAMLError as exc:
        mark = getattr(exc, "problem_mark", None)
        loc = f":{mark.line + 1}" if mark is not None else ""
        report.errors.append(f"yaml parse error{loc}: {exc}")
        return report

    if not isinstance(data, dict):
        report.errors.append("manifest root must be a YAML mapping")
        return report

    # JSON Schema validation.
    schema_errors = sorted(validator.iter_errors(data), key=lambda e: list(e.absolute_path))
    for err in schema_errors:
        pointer = _format_pointer(err)
        top_key = next(iter(err.absolute_path), None)
        line = _line_for_key(raw_text, str(top_key)) if top_key else None
        loc = f"{manifest_path}:{line}" if line else str(manifest_path)
        report.errors.append(f"{loc} [{pointer}]: {err.message}")

    # Structural checks beyond the schema.
    slug = data.get("slug")
    version = data.get("version")

    if isinstance(slug, str):
        try:
            rel = manifest_path.parent.relative_to(SKILLS_ROOT)
        except ValueError:
            report.errors.append(
                f"{manifest_path}: manifest is not under skills/ root ({SKILLS_ROOT})"
            )
        else:
            parts = rel.parts
            if len(parts) != 2:
                report.errors.append(
                    f"{manifest_path}: expected path skills/<publisher>/<slug>/manifest.yaml, "
                    f"got skills/{'/'.join(parts)}/manifest.yaml"
                )
            else:
                expected_slug = f"{parts[0]}/{parts[1]}"
                if slug != expected_slug:
                    line = _line_for_key(raw_text, "slug")
                    loc = f"{manifest_path}:{line}" if line else str(manifest_path)
                    report.errors.append(
                        f"{loc}: slug '{slug}' does not match directory path "
                        f"(expected '{expected_slug}')"
                    )

    if isinstance(version, str) and not SEMVER_RE.match(version):
        line = _line_for_key(raw_text, "version")
        loc = f"{manifest_path}:{line}" if line else str(manifest_path)
        report.errors.append(
            f"{loc}: version '{version}' is not semver (X.Y.Z)"
        )

    # License policy: omitted/null is treated as the repo default; explicit
    # values must be on the accepted SPDX list, and known-rejected SPDX IDs
    # get a policy-specific error.
    license_err = _check_license(data.get("license"))
    if license_err:
        line = _line_for_key(raw_text, "license")
        loc = f"{manifest_path}:{line}" if line else str(manifest_path)
        report.errors.append(f"{loc}: {license_err}")

    readme = manifest_path.parent / "README.md"
    if not readme.exists():
        report.errors.append(
            f"{manifest_path.parent}: README.md missing (every skill needs a public README)"
        )

    # Soft warnings.
    if "description" not in data or not (data.get("description") or "").strip():
        report.warnings.append(f"{manifest_path}: description is empty")
    if "publisher" not in data or not (data.get("publisher") or "").strip():
        report.warnings.append(f"{manifest_path}: publisher is empty")

    return report


def emit(reports: Iterable[ManifestReport], strict: bool) -> int:
    n_total = 0
    n_failed = 0
    n_warned = 0
    for report in reports:
        n_total += 1
        if report.errors:
            n_failed += 1
            print(f"FAIL  {report.path.relative_to(REPO_ROOT)}")
            for line in report.errors:
                print(f"  - {line}")
        else:
            print(f"OK    {report.path.relative_to(REPO_ROOT)}")
        for warn in report.warnings:
            n_warned += 1
            print(f"  warn: {warn}")

    print(
        f"\n{n_total} manifest(s); {n_failed} failed; {n_warned} warning(s)"
    )
    if n_failed:
        return 1
    if strict and n_warned:
        return 1
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate skill manifests.")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit non-zero if there are any warnings.",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=None,
        help="Validate a single manifest.yaml (default: walk skills/).",
    )
    args = parser.parse_args(argv)

    schema = load_schema()
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)

    manifests = discover_manifests(args.manifest)
    if not manifests:
        print("no manifests found under skills/")
        return 0

    reports = [validate_one(m, validator) for m in manifests]
    return emit(reports, strict=args.strict)


if __name__ == "__main__":
    sys.exit(main())
