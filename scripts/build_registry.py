#!/usr/bin/env python3
"""Build the top-level registry.json index from every manifest under skills/.

The registry is the single artifact the marketplace consumer pulls from this
repo. Each entry is a denormalized slice of the manifest with everything the
client needs to render and filter the skill list, plus a pointer back to the
source directory.

Usage:
    python scripts/build_registry.py
    python scripts/build_registry.py --out path/to/registry.json
    python scripts/build_registry.py --check     # exit 1 if the file would change

Exit 0 on success, 1 if any manifest fails validation or --check sees a diff.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
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

# Reuse the validator from validate.py so structural rules stay in one place.
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from validate import (  # type: ignore  # noqa: E402
    DEFAULT_LICENSE,
    REPO_ROOT,
    SCHEMA_PATH,
    SKILLS_ROOT,
    discover_manifests,
    load_schema,
    validate_one,
)


def manifest_to_entry(manifest_path: Path, data: dict[str, Any]) -> dict[str, Any]:
    """Project a manifest to its registry shape."""
    repo_path = manifest_path.parent.relative_to(REPO_ROOT).as_posix()
    icon_name = data.get("icon")
    icon_url: str | None = None
    if isinstance(icon_name, str) and icon_name.strip():
        # Resolve relative to the manifest dir; the marketplace consumer can
        # turn this into a raw.githubusercontent.com URL.
        icon_url = f"{repo_path}/{icon_name}"
    elif (manifest_path.parent / "icon.svg").exists():
        icon_url = f"{repo_path}/icon.svg"

    # License: published entry always carries the resolved value (never null);
    # an omitted/null manifest field falls back to the repo default per
    # LICENSING.md.
    raw_license = data.get("license")
    license_value = (
        raw_license if isinstance(raw_license, str) and raw_license else DEFAULT_LICENSE
    )

    return {
        "slug": data.get("slug"),
        "version": data.get("version"),
        "name": data.get("name"),
        "description": data.get("description", ""),
        "publisher": data.get("publisher", ""),
        "applies_to": data.get("applies_to") or {},
        "tools": list(data.get("tools") or []),
        "output_kind": (data.get("output") or {}).get("produces"),
        "license": license_value,
        "repo_path": repo_path,
        "icon_url": icon_url,
    }


def build(strict: bool = True) -> list[dict[str, Any]]:
    schema = load_schema()
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)

    manifests = discover_manifests(None)
    if not manifests:
        return []

    entries: list[dict[str, Any]] = []
    failed: list[Path] = []
    for path in manifests:
        report = validate_one(path, validator)
        if not report.ok:
            failed.append(path)
            for err in report.errors:
                print(f"  - {err}", file=sys.stderr)
            continue
        with path.open("r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
        entries.append(manifest_to_entry(path, data))

    if failed and strict:
        print(
            f"error: {len(failed)} manifest(s) failed validation; aborting build",
            file=sys.stderr,
        )
        sys.exit(1)

    entries.sort(key=lambda e: str(e.get("slug") or ""))
    return entries


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build registry.json from manifests.")
    parser.add_argument(
        "--out",
        type=Path,
        default=REPO_ROOT / "registry.json",
        help="Output path (default: <repo>/registry.json).",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Do not write; exit 1 if the file on disk differs from the build.",
    )
    args = parser.parse_args(argv)

    if not SCHEMA_PATH.exists():
        print(f"error: schema not found at {SCHEMA_PATH}", file=sys.stderr)
        return 1
    if not SKILLS_ROOT.exists():
        print(f"error: skills/ not found at {SKILLS_ROOT}", file=sys.stderr)
        return 1

    entries = build(strict=True)
    serialized = json.dumps(entries, indent=2, ensure_ascii=True, sort_keys=True) + "\n"

    if args.check:
        current = args.out.read_text(encoding="utf-8") if args.out.exists() else ""
        if current != serialized:
            print(
                f"registry mismatch at {args.out}: regenerate with "
                f"`python scripts/build_registry.py`",
                file=sys.stderr,
            )
            return 1
        print(f"registry.json is up to date ({len(entries)} entries)")
        return 0

    args.out.write_text(serialized, encoding="utf-8")
    print(f"wrote {args.out.relative_to(REPO_ROOT)} ({len(entries)} entries)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
