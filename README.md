# blooper-skills

[![validate](https://github.com/blooper-ai/blooper-skills/actions/workflows/validate.yml/badge.svg)](https://github.com/blooper-ai/blooper-skills/actions/workflows/validate.yml)
[![build-registry](https://github.com/blooper-ai/blooper-skills/actions/workflows/build-registry.yml/badge.svg)](https://github.com/blooper-ai/blooper-skills/actions/workflows/build-registry.yml)

Community skill registry for the [Blooper](https://blooper.ai) creative workspace. Each subdirectory under `skills/<publisher>/<slug>/` describes one installable skill the Blooper app can offer users in chat.

A skill is a single declarative `manifest.yaml` (plus an optional README, icon, and small tool stubs) that wires together built-in runtime tools to do something useful — trim a video, generate ten variants of a character, summarize a PDF, etc. Skills are pure configuration: no servers to deploy, no SDK to install.

## How it works

1. You write a `manifest.yaml` in this repo describing inputs, the prompt template, the tools the skill calls, and the expected output.
2. You open a pull request. CI validates the manifest against the JSON Schema, runs structural checks, and verifies `registry.json` was regenerated.
3. After review and merge, the skill appears in the Blooper marketplace within 24h. The Blooper app pulls `registry.json` from this repo and shows your skill to users whose chat context matches your skill's `applies_to` filter.
4. Users install the skill into their project with one click. Updates land the next time they pull the marketplace.

## Adding a skill

1. Fork this repo.
2. Copy `templates/starter-skill/` to `skills/<your-publisher>/<your-skill-slug>/`.
3. Edit `manifest.yaml`, write the README, drop in a 64x64 SVG icon.
4. Validate locally:
   ```sh
   pip install -r scripts/requirements.txt
   python scripts/validate.py --all
   python scripts/build_registry.py --out registry.json
   ```
5. Commit the regenerated `registry.json` alongside your skill.
6. Open a pull request using the PR template.

Full step-by-step in [`CONTRIBUTING.md`](./CONTRIBUTING.md).

## Repository layout

```
blooper-skills/
├── schema/                  JSON Schema for one manifest.yaml
├── scripts/                 validate, build_registry, export_schema
├── skills/<publisher>/<slug>/   one directory per skill
├── templates/starter-skill/ copy-paste starting point
├── docs/                    authoring guides
└── registry.json            auto-generated index of every skill
```

## Reference skills

Five end-to-end examples live under `skills/blooper/`. Each demonstrates a different pattern. A narrated tour is in [`docs/examples-tour.md`](./docs/examples-tour.md).

| Skill | Pattern |
| --- | --- |
| `blooper/trim-video` | Minimal deterministic single-tool skill. |
| `blooper/crop-video` | Same shape with a `select` parameter for aspect presets. |
| `blooper/character-emotions` | Self-verify retry loop using a vision check tool. |
| `blooper/generate-room-from-refs` | Folder-scoped skill with `file_versions` ref input. |
| `blooper/generate-in-all-providers` | Provider fan-out and human-in-the-loop pick. |

## Docs

- [`docs/authoring.md`](./docs/authoring.md) - narrative authoring guide.
- [`docs/schema-reference.md`](./docs/schema-reference.md) - field-by-field manifest reference.
- [`docs/tool-development.md`](./docs/tool-development.md) - when and how to ship a custom tool.
- [`docs/examples-tour.md`](./docs/examples-tour.md) - guided tour of the reference skills.
- App-side docs: <https://dev.blooper.ai/docs/>.

## FAQ

**Do I need to know Python?** No, unless you are shipping a custom tool. Pure manifest skills are YAML only.

**Can I publish a private skill?** Skills in this repo are public. For private/internal skills, use the in-app "Inline agent" feature; nothing in this repo is required.

**How long until my skill is live?** After merge, the marketplace re-indexes within 24h. Users see updates the next time their app pulls the marketplace.

**What runs my skill code?** The Blooper runtime executes the manifest. Built-in tools are part of the runtime; custom tools you ship under `tools/` are loaded by the runtime sandbox.

**Can I include a paid model in my budget?** Yes - declare it in `budget.max_provider_calls`. Reviewers will push back on bloated budgets; start tight.

**What license?** MIT - see [`LICENSE`](./LICENSE). By contributing a skill, you license your contribution under MIT.

## Security

Found a problem in a skill's tool code or in the registry pipeline? See [`SECURITY.md`](./SECURITY.md) for the private disclosure process.

## Code of conduct

This project follows the Contributor Covenant 2.1 - see [`CODE_OF_CONDUCT.md`](./CODE_OF_CONDUCT.md). Report concerns to conduct@blooper.ai.
