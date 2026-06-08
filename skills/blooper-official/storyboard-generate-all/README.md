# Generate all storyboard shots

Batch-fill every empty shot file in a storyboard with a generated image,
using each shot's stored prompt and the right per-shot character +
location references. Non-empty shots are skipped unless `force=true`.

This skill is the natural follow-up to `blooper-official/storyboard-from-script`:
the script→storyboard pipeline leaves you with shot placeholders that have
prompts, durations, and `chars` lists; this skill turns those placeholders
into actual images.

## Why per-shot character filtering matters

Earlier versions passed *every* character reference to every shot.
Predictable failure mode: the model collapsed to one dominant face across
the whole storyboard. v1.2.0 reads each shot's `chars` array (set by the
storyboard pipeline's stage-4 dedup, with names matching Character
placeholder file names exactly) and only injects references for the
characters that are actually on screen in that beat.

## When to use it

- You have a storyboard folder produced by the script→storyboard pipeline
  (or hand-authored with the same shape: scene folders, shot files with
  `prompt` + `chars` metadata).
- The character placeholders in `Characters/` have been filled with chosen
  designs.
- You now want every empty shot rendered without clicking through them
  one-by-one.

## Parameters

| Param                  | Type    | Required | Default | Notes                                                                       |
| ---------------------- | ------- | -------- | ------- | --------------------------------------------------------------------------- |
| `storyboard_folder_id` | text    | yes      | -       | UUID of the Storyboard folder to fan out across.                            |
| `force`                | boolean | no       | `false` | When true, re-generate shots that already have an image (uses `regenerate_shot`). |

## Example chat invocation

> Open the storyboard folder, then type:
>
> *"Storyboard-generate-all — fill every empty shot."*
>
> Or, to re-roll a finished board with a new look:
>
> *"Storyboard-generate-all, force=true."*

## Expected output

- One new file version per empty shot (or per shot, when `force=true`), each
  parented under the shot's existing file.
- A one-line per-shot summary in chat that includes the character names
  actually injected: `"Shot 003: filled, chars=[Mara, Doc]"`.

## Budget

- `max_provider_calls`: 50 — one per shot for typical boards.
- `max_minutes`: 30 — shots dispatch in parallel inside the runtime.
- `max_sub_runs`: 50 — each shot generation counts as one sub-run.

## Limits and known issues

- Empty placeholders use `generate_image` with `target_file_id`. Non-empty
  placeholders MUST use `regenerate_shot` — `generate_image` rejects
  non-empty targets with `"target_file is not empty"`.
- The skill does NOT alter `shot.prompt`. Append descriptors via the
  character/location references, not by editing the stored prompt.
- If a shot lists a character name that has no filled-in placeholder, that
  name is silently skipped (the rest of the shot's characters still
  contribute references). No substitute is invented.
- If the project has no `Characters/` folder the skill still runs with only
  location refs; chat narration warns the user.
