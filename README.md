# blooper-skills

[![validate](https://github.com/blooper-ai/blooper-skills/actions/workflows/validate.yml/badge.svg)](https://github.com/blooper-ai/blooper-skills/actions/workflows/validate.yml)
[![build-registry](https://github.com/blooper-ai/blooper-skills/actions/workflows/build-registry.yml/badge.svg)](https://github.com/blooper-ai/blooper-skills/actions/workflows/build-registry.yml)

Community skill registry for the [Blooper](https://blooper.ai) creative workspace. Each subdirectory under `skills/<publisher>/<slug>/` describes one installable skill the Blooper app can offer users in chat.

A skill is a single declarative `skill.yaml` (plus an optional README, icon, and small tool stubs) that wires together built-in runtime tools to do something useful — trim a video, generate ten variants of a character, summarize a PDF, etc. Skills are pure configuration: no servers to deploy, no SDK to install.

## How it works

1. You write a `skill.yaml` in this repo describing inputs, the prompt template, the tools the skill calls, and the expected output.
2. You open a pull request. CI validates the manifest against the JSON Schema, runs structural checks, and verifies `registry.json` was regenerated.
3. After review and merge, the skill appears in the Blooper marketplace within 24h. The Blooper app pulls `registry.json` from this repo and shows your skill to users whose chat context matches your skill's `applies_to` filter.
4. Users install the skill into their project with one click. Updates land the next time they pull the marketplace.

## Adding a skill

1. Fork this repo.
2. Create `skills/<your-publisher>/<your-skill-slug>/` and add a `skill.yaml` (use any existing skill under `skills/blooper-official/` as a starting point).
3. Write the README, drop in an optional 64x64 SVG icon.
4. Validate locally:
   ```sh
   pip install pyyaml jsonschema
   python scripts/validate.py
   python scripts/build_registry.py
   ```
5. Commit the regenerated `registry.json` alongside your skill.
6. Open a pull request using the PR template.

Full step-by-step in [`CONTRIBUTING.md`](./CONTRIBUTING.md).

## Repository layout

```
blooper-skills/
├── schema/                       JSON Schema for one skill.yaml
├── scripts/                      validate, build_registry
├── skills/<publisher>/<slug>/    one directory per skill
└── registry.json                 auto-generated index of every skill
```

## Reference skills

The reference skills live under `skills/blooper-official/`. Each one is a real, production skill from the Blooper app — they're the canonical examples of what a Blooper skill looks like end-to-end.

| Skill                                          | Pattern                                                                  |
| ---------------------------------------------- | ------------------------------------------------------------------------ |
| `blooper-official/trim-video`                  | Minimal deterministic single-tool skill.                                  |
| `blooper-official/crop-video`                  | Same shape with a `select` parameter for aspect presets.                  |
| `blooper-official/render-timeline`             | Single-tool skill scoped to a folder kind.                                |
| `blooper-official/character-emotions`          | Self-verify retry loop using a vision check tool, version-tree lineage.   |
| `blooper-official/generate-room-from-refs`     | Folder-scoped skill with `file_versions` ref input.                       |
| `blooper-official/generate-in-all-providers`   | Provider fan-out and human-in-the-loop pick.                              |
| `blooper-official/storyboard-from-script`      | Heavy LLM-pipeline skill wrapped behind a single runtime tool.            |
| `blooper-official/storyboard-generate-all`     | Batch fan-out across a folder of placeholders with per-shot ref filtering. |
| `blooper-official/timeline-from-storyboard`    | Structural / metadata-only seeding skill.                                 |
| `blooper-official/timeline-generate-all`       | Batch fan-out of video generations with project-wide character refs.      |

## Docs

App-side docs, SDK reference, and authoring tutorials live at <https://dev.blooper.ai/docs/>.

## FAQ

**Do I need to know Python?** No, unless you are shipping a custom tool. Pure manifest skills are YAML only.

**Can I publish a private skill?** Skills in this repo are public. For private/internal skills, use the in-app "Inline agent" feature; nothing in this repo is required.

**How long until my skill is live?** After merge, the marketplace re-indexes within 24h. Users see updates the next time their app pulls the marketplace.

**What runs my skill code?** The Blooper runtime executes the manifest. Built-in tools are part of the runtime; custom tools you ship under `tools/` are loaded by the runtime sandbox.

**Can I include a paid model in my budget?** Yes - declare it in `budget.max_provider_calls`. Reviewers will push back on bloated budgets; start tight.

**What license?** Apache-2.0 - see [`LICENSE`](./LICENSE). By contributing a skill, you license your contribution under Apache-2.0 unless your manifest declares a different (permissive) SPDX identifier.

**Plugin licensing**: each skill manifest may declare a `license` field with one of the accepted SPDX identifiers (Apache-2.0 — the default, MIT, BSD-2-Clause, BSD-3-Clause, ISC). Copyleft and source-available licenses are rejected by PR validation. Full policy and rationale in [`LICENSING.md`](./LICENSING.md).

## Security

Found a problem in a skill's tool code or in the registry pipeline? See [`SECURITY.md`](./SECURITY.md) for the private disclosure process.
