# blooper-skills

Community skill registry for the [Blooper](https://blooper.ai) creative workspace. Each subdirectory under `skills/<publisher>/<slug>/` describes one installable skill the Blooper app can offer users in chat.

This repository is **data only** — skill manifests and docs, nothing else. The Blooper backend is the single source of truth: it discovers the manifests here, validates them, and builds its own catalog. There is no `registry.json`, schema, or validation script to maintain in this repo.

A skill is a single declarative `skill.yaml` (plus an optional README, icon, and small tool stubs) that wires together built-in runtime tools to do something useful — trim a video, generate ten variants of a character, summarize a PDF, etc. Skills are pure configuration: no servers to deploy, no SDK to install.

## How it works

1. You write a `skill.yaml` in this repo describing inputs, the prompt template, the tools the skill calls, and the expected output.
2. You open a pull request; a maintainer reviews it.
3. After merge, the Blooper backend discovers your manifest (it enumerates `skills/<publisher>/<slug>/skill.yaml` directly), validates it against the canonical manifest model, and surfaces it in the marketplace to users whose chat context matches your skill's `applies_to` filter. A manifest that fails validation simply isn't shown.
4. Users install the skill into their project with one click. Updates land the next time they pull the marketplace.

## Adding a skill

1. Fork this repo.
2. Create `skills/<your-publisher>/<your-skill-slug>/` and add a `skill.yaml` (use any existing skill under `skills/blooper-official/` as a starting point).
3. Write the README, drop in an optional 64x64 SVG icon.
4. Make sure the manifest `slug` matches the folder path (`skills/<publisher>/<slug>/` → `slug: <publisher>/<slug>`).
5. Open a pull request using the PR template. There is nothing to build or commit beyond your skill's files — the backend validates the manifest on ingest. To try it first, zip the skill and upload it privately into a scratch project via **Skills → Upload .zip** in the app (see the [docs](https://blooper.ai/docs/)).

Full step-by-step in [`CONTRIBUTING.md`](./CONTRIBUTING.md).

## Repository layout

```
blooper-skills/
├── skills/<publisher>/<slug>/    one directory per skill (skill.yaml + README + optional icon)
├── CONTRIBUTING.md  LICENSING.md  SECURITY.md
└── README.md
```

Data only — the manifest schema, validation rules, and the marketplace index all live in the Blooper backend (the single source of truth), not here.

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
| `blooper-official/timeline-generate-all`       | Batch fan-out of video generations with frame-accurate clip refs.         |
| `blooper-official/export-file-history-pdf`     | One-tool provenance/history PDF export for the anchored file.             |

## Docs

App-side docs, SDK reference, and authoring tutorials live at <https://blooper.ai/docs/>.

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
