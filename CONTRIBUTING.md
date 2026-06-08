# Contributing to blooper-skills

Thanks for adding a skill to the Blooper marketplace. This repo follows a Raycast-style inline monorepo: one pull request carries the manifest, optional tool code, README, and icon together so reviewers can see the whole skill in one place.

## TL;DR

1. Fork and clone the repo.
2. Create `skills/<your-publisher>/<your-skill-slug>/` and drop in a `manifest.yaml` + `README.md` (use any skill under `skills/blooper-official/` as a starting point).
3. Run `python scripts/validate.py` and `python scripts/build_registry.py` locally.
4. Commit, push, open a PR using the template and fill in the checklist.

## Step 1 - Pick a slug

Slugs are `<publisher>/<skill-name>`, both kebab-case, both matching `[a-z0-9_-]+`.

- `publisher` is your handle or org. By convention it matches the directory name under `skills/` and your GitHub username/org. First-time contributors: pick something you can live with - this becomes part of every install id.
- `skill-name` describes what the skill does in 1-3 words: `trim-video`, `summarize-pdf`, `caption-image`.

The slug MUST match the folder path. A manifest with `slug: alice/caption-image` must live at `skills/alice/caption-image/manifest.yaml`. CI enforces this.

## Step 2 - Scaffold from an existing skill

Copy any skill from `skills/blooper-official/` as a starting point:

```sh
cp -R skills/blooper-official/trim-video skills/<publisher>/<skill-slug>
```

A skill directory holds:

```
skills/<publisher>/<skill-slug>/
├── manifest.yaml      # edit this
├── README.md          # edit this
├── icon.svg           # optional, drop in a 64x64 svg
└── tools/             # optional; delete if you only use built-in tools
    └── example_tool.py
```

## Step 3 - Write the manifest

`manifest.yaml` follows the SkillManifest schema. Authoritative reference is [`schema/skill-manifest.schema.json`](./schema/skill-manifest.schema.json). The non-obvious fields:

- `applies_to` - when the skill should be offered to the user. AND across keys, OR within lists. Leave empty to apply everywhere.
- `params` - typed inputs presented to the user before run.
- `output.count` - `"dynamic"`, an integer, or `"from_param.<param_name>"`.
- `tools` - list every tool the skill calls. Tool names not provided by the runtime AND not shipped under `tools/` will fail at install.
- `budget` - cap provider calls and minutes. Reviewers will push back on bloated budgets; start tight.

## Step 4 - Optional: ship a custom tool

Most skills should compose existing built-in tools. If you genuinely need a new tool:

1. Put one or more `*.py` files under `skills/<publisher>/<skill-slug>/tools/`.
2. Each tool file must export a `register(registry)` function.
3. List the tool's exported name in `manifest.yaml` `tools:`.
4. A platform-runtime reviewer must sign off before the PR can merge. Custom tools become part of the runtime; they are reviewed for safety, cost, and API stability. Expect a longer review cycle and be ready to iterate.

If you do NOT need a new tool, omit the `tools/` directory.

## Step 5 - Write the README

Every skill must include `README.md` with at minimum:

- One-paragraph description (same content as `manifest.description` is fine).
- "When to use it" - concrete user intent the skill serves.
- "Parameters" - table of every param with type and example.
- "Example output" - one screenshot or pasted result.
- "Cost" - rough provider-call count for a typical run.

## Step 6 - Validate locally

```sh
pip install pyyaml jsonschema

# Validate just your skill:
python scripts/validate.py --manifest skills/<publisher>/<skill-slug>/manifest.yaml

# Run full structural checks across every manifest:
python scripts/validate.py

# Regenerate the registry and commit it:
python scripts/build_registry.py
git add registry.json
```

CI runs the same commands.

## Step 7 - Open the PR

Use the auto-loaded PULL_REQUEST_TEMPLATE.md and complete every checkbox. A typical PR looks like:

- Title: `Add skill <publisher>/<slug>` or `Update <publisher>/<slug> to vX.Y.Z`.
- Body: filled-in checklist; link to a screenshot or short video of the skill running.
- Files: `skills/<publisher>/<slug>/...` plus the regenerated `registry.json`.

## Reviews

- Manifest-only PRs are reviewed by the maintainer team. CODEOWNERS routes by `skills/<publisher>/`.
- PRs touching `tools/` are additionally reviewed by `@blooper-ai/platform-runtime` for runtime safety.
- Two-business-day SLA on first review; longer for custom tools.

## Versioning

- Follow semver. Bump `version` in `manifest.yaml` for every change that ships.
- Patch (`1.0.X`) for prompt tweaks, README fixes, icon swaps.
- Minor (`1.X.0`) for new params with safe defaults, new tools, expanded applicability.
- Major (`X.0.0`) for breaking param changes, removed tools, narrowed applicability.

## Removing a skill

Open a PR that deletes `skills/<publisher>/<slug>/` and regenerates `registry.json`. The marketplace marks the slug as removed on the next index pull. Installed copies continue to work locally until the user uninstalls.

## Questions

- Authoring questions: open a discussion under `Authoring`.
- Bug reports for an existing skill: use `.github/ISSUE_TEMPLATE/bug.md`.
- Wishlist: `.github/ISSUE_TEMPLATE/skill-request.md`.

For app-side documentation, SDK reference, and tutorials see <https://dev.blooper.ai/docs/>.
