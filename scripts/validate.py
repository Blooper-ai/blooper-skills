#!/usr/bin/env python3
"""Validate skill manifests against the JSON Schema and structural rules.

Usage:
    python scripts/validate.py                 # validate every manifest
    python scripts/validate.py --strict        # fail on warnings too
    python scripts/validate.py --manifest PATH # validate one manifest

The canonical manifest filename is ``skill.yaml``. ``skill.yml`` and
``skill.json`` are accepted as alternates per skill — pick one. Mixing
two in the same skill directory is an error (we won't guess which wins).

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
TOOL_COSTS_PATH = REPO_ROOT / "tool_costs.json"
# Reflection-turn headroom we add when computing the minimum sensible
# max_provider_calls budget for a manifest. The BE counter ticks per LLM
# tool-use turn, not per real provider call — so a skill that calls one
# cost-5 tool also burns ~1-2 thinking turns. Authors keep guessing low;
# this lint catches the misconfiguration before publish. Set on 2026-06-09
# after observing every test run of crop-video / trim-video / render-timeline
# pause on a budget_extension approval on its first useful turn.
_BUDGET_REFLECTION_HEADROOM = 2

SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")

# Canonical filename first, then accepted alternates. The same filename set
# is honoured by the backend zip parser (``backend/app/skills/sources/zip.py``)
# and the community fetcher (``backend/app/skills/sources/community.py``) so
# that the same authoring artifact works in every install path.
MANIFEST_FILENAMES: tuple[str, ...] = ("skill.yaml", "skill.yml", "skill.json")

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


def _load_tool_costs() -> dict[str, int]:
    """Read the snapshot of backend tool costs.

    The snapshot is regenerated from the live BE registry whenever the
    cost numbers change (see README — there's a ``make snapshot-tool-costs``
    convention). If the file is missing we return an empty dict and
    silently skip the budget lint; CI will surface the missing snapshot
    via a separate guard if we want to make it required later.
    """
    if not TOOL_COSTS_PATH.exists():
        return {}
    try:
        with TOOL_COSTS_PATH.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, json.JSONDecodeError):
        return {}
    if not isinstance(data, dict):
        return {}
    out: dict[str, int] = {}
    for slug, cost in data.items():
        if isinstance(slug, str) and isinstance(cost, int):
            out[slug] = cost
    return out


def _budget_check(
    data: dict, tool_costs: dict[str, int]
) -> tuple[list[str], list[str]]:
    """Lint manifest.budget.max_provider_calls against the sum of tool
    costs.

    Why this matters: the backend budget counter ticks per LLM tool-use
    turn, not per real provider call. A manifest that lists a single
    cost-5 tool (e.g. ``render_timeline``) but sets
    ``max_provider_calls: 1`` pauses on a ``budget_extension`` approval
    before the skill can finish even its happy path. The fix is to set
    a budget that covers ``sum(tool.cost) + ~2 reflection turns``.

    Returns ``(errors, warnings)``. We treat any tool not in the
    snapshot permissively (cost 0) — better than blocking on a stale
    snapshot during a registry change.
    """
    errors: list[str] = []
    warnings: list[str] = []
    if not tool_costs:
        return errors, warnings  # no snapshot → skip lint

    tools = data.get("tools") or []
    if not isinstance(tools, list):
        return errors, warnings  # schema validation will flag this

    budget = data.get("budget") or {}
    if not isinstance(budget, dict):
        return errors, warnings

    cap_raw = budget.get("max_provider_calls")
    if not isinstance(cap_raw, int):
        return errors, warnings  # schema covers the type error

    sum_known = 0
    unknown: list[str] = []
    for t in tools:
        if not isinstance(t, str):
            continue
        if t in tool_costs:
            sum_known += tool_costs[t]
        else:
            unknown.append(t)

    # Deterministic skills skip the LLM entirely — only the one declared
    # tool is billed, no reflection-turn headroom needed. The schema
    # guarantees deterministic.tool is in tools[], so sum_known already
    # accounts for it. See backend/app/skills/manifest.py:DeterministicSpec.
    is_deterministic = data.get("runtime") == "deterministic"
    headroom = 0 if is_deterministic else _BUDGET_REFLECTION_HEADROOM
    minimum_recommended = sum_known + headroom
    if cap_raw < minimum_recommended:
        suffix = (
            "Bump the budget or remove unused tools."
            if not is_deterministic
            else "Bump the budget or remove unused tools (deterministic runtime — no reflection-turn headroom is added)."
        )
        warnings.append(
            f"budget.max_provider_calls={cap_raw} is below recommended "
            f"minimum {minimum_recommended} (sum of tool costs "
            f"{sum_known}{'' if is_deterministic else f' + {_BUDGET_REFLECTION_HEADROOM} reflection-turn headroom'}). "
            f"Every run will pause on a budget_extension approval. {suffix}"
        )

    if unknown:
        warnings.append(
            f"tools {sorted(unknown)} are not in tool_costs.json "
            f"(treated as cost 0 for the budget lint). Regenerate the "
            f"snapshot or check the tool name."
        )

    return errors, warnings


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
    # Walk every skill directory and accept any one of the canonical
    # filenames. If a skill ships more than one (skill.yaml AND skill.json)
    # we surface every match — validate_one will fail it as ambiguous so
    # CI catches the conflict instead of silently picking one.
    found: list[Path] = []
    for path in sorted(SKILLS_ROOT.rglob("*")):
        if path.is_file() and path.name in MANIFEST_FILENAMES:
            found.append(path)
    return found


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
    manifest_path: Path,
    validator: Draft202012Validator,
    tool_costs: dict[str, int] | None = None,
) -> ManifestReport:
    report = ManifestReport(path=manifest_path)
    try:
        raw_text = manifest_path.read_text(encoding="utf-8")
    except OSError as exc:
        report.errors.append(f"unreadable: {exc}")
        return report

    if manifest_path.name.endswith(".json"):
        try:
            data = json.loads(raw_text)
        except json.JSONDecodeError as exc:
            report.errors.append(
                f"json parse error:{exc.lineno}: {exc.msg}"
            )
            return report
    else:
        try:
            data = yaml.safe_load(raw_text)
        except yaml.YAMLError as exc:
            mark = getattr(exc, "problem_mark", None)
            loc = f":{mark.line + 1}" if mark is not None else ""
            report.errors.append(f"yaml parse error{loc}: {exc}")
            return report

    if not isinstance(data, dict):
        report.errors.append("manifest root must be a mapping (YAML or JSON object)")
        return report

    # Reject ambiguous skill directories that ship more than one of
    # skill.yaml / skill.yml / skill.json. Pick one — the install path
    # cannot guess which to honour.
    siblings = [
        p.name for p in manifest_path.parent.iterdir()
        if p.is_file() and p.name in MANIFEST_FILENAMES
    ]
    if len(siblings) > 1:
        report.errors.append(
            f"{manifest_path.parent}: skill directory contains multiple manifest "
            f"files ({', '.join(sorted(siblings))}); keep exactly one of "
            f"{', '.join(MANIFEST_FILENAMES)}"
        )

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
                    f"{manifest_path}: expected path skills/<publisher>/<slug>/{manifest_path.name}, "
                    f"got skills/{'/'.join(parts)}/{manifest_path.name}"
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

    # Budget-vs-tool-cost lint: catch manifests whose
    # ``budget.max_provider_calls`` is below the sum of the costs of the
    # tools they declare. The backend counter ticks per LLM tool-use
    # turn, so a too-tight budget causes every run to pause on a
    # ``budget_extension`` approval before useful work is done.
    if tool_costs:
        budget_errors, budget_warnings = _budget_check(data, tool_costs)
        report.errors.extend(budget_errors)
        report.warnings.extend(budget_warnings)

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
        help="Validate a single skill.yaml/yml/json (default: walk skills/).",
    )
    args = parser.parse_args(argv)

    schema = load_schema()
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)

    manifests = discover_manifests(args.manifest)
    if not manifests:
        print("no manifests found under skills/")
        return 0

    tool_costs = _load_tool_costs()
    reports = [validate_one(m, validator, tool_costs) for m in manifests]
    return emit(reports, strict=args.strict)


if __name__ == "__main__":
    sys.exit(main())
