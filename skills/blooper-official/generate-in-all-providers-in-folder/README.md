# Generate one file per provider (in folder)

Run the same prompt through every from-scratch image provider and create
one new image **File** in the current folder for each. This is the
folder-anchored companion to `generate-in-all-providers` (which appends
new VERSIONS to a single existing file).

Use this when you want every model's render kept side-by-side as
independent files — for a moodboard, an exploration sweep, or a "show me
all the options" pass that the user picks from later.

## When to use it

- You're in a folder chat (e.g. *References*, *Moodboard*, *Inspiration*)
  and want the same prompt rendered by every available image provider.
- You want the results as separate Files, not as competing versions of
  one File.

## Parameters

| Param    | Type | Required | Notes                                     |
| -------- | ---- | -------- | ----------------------------------------- |
| `prompt` | text | yes      | The prompt to run through every provider. |

## Example chat invocation

> Open a folder, then type:
>
> *"Generate one file per provider: a misty pine forest at golden hour."*

The skill calls `get_run_context` to learn the folder, then fans out
one `generate_image` call per from-scratch image provider. Each call
creates a new File in that folder.

## Expected output

- One new image File per from-scratch provider (today: FLUX.2 Max,
  Nano Banana, OpenAI Image).
- Each file is named after its provider so you can tell them apart at a
  glance in the folder grid.
- No picker step — every result is kept.

## Budget

- `max_provider_calls`: 6 — covers 3 providers plus retry slack.
- `max_minutes`: 10.

## Limits and known issues

- Must be run from a folder chat. Running from a file chat stops with a
  message pointing you at the on-file companion skill.
- One call per provider. The skill does not loop, retry, or regenerate.
- If one provider fails the others still proceed; the failure is
  reported but does not abort the run.
