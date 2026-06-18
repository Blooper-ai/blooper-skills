<!--
Thanks for contributing a skill! Fill in the checklist below and the short
summary. PRs missing the checklist are usually sent back without review.
-->

## Summary

<!-- One or two sentences: what does this skill do and why does it belong in the
marketplace? Link to a screenshot or short clip of it running if you have one. -->

## Type of change

- [ ] New skill
- [ ] Update to an existing skill (bump version)
- [ ] Remove a skill
- [ ] Tooling, docs, or schema change (no skill content)

## Checklist

- [ ] Slug follows `publisher/name` pattern (lowercase, kebab-case, matches `^[a-z0-9_-]+/[a-z0-9_-]+$`).
- [ ] Slug matches the directory path under `skills/`.
- [ ] Version is semver (`X.Y.Z`); bumped for any user-visible change.
- [ ] `applies_to` fields filled correctly (file_type / folder_kind / folder_name / parent_folder_name).
- [ ] `README.md` present in the skill directory with: description, args, example chat invocation, output, cost note.
- [ ] `tools:` lists only built-in runtime tools (or tools shipped under this skill's `tools/`). Unknown tools are rejected by the backend on ingest.
- [ ] No internal infrastructure references in manifest or README (no internal hostnames, queue names, repo paths, vendor secrets).
- [ ] (If new tool code:) `tools/` directory follows the public SDK contract — see <https://dev.blooper.ai/docs/>.
- [ ] Budget (`max_provider_calls`, `max_minutes`) is tight and justified.
- [ ] `license` is one of: Apache-2.0 (default), MIT, BSD-2-Clause, BSD-3-Clause, ISC — OR the field is omitted (defaults to Apache-2.0). See [`LICENSING.md`](../LICENSING.md).

## Notes for reviewers

<!-- Anything worth flagging: tricky params, expected failure modes, follow-up
PRs you plan to send. -->
