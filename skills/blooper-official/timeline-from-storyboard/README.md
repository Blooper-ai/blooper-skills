# Create timeline from storyboard

Create a new Timeline that mirrors the structure of an existing Storyboard:
one TimelineScene per Storyboard Scene, one TimelineClip per Shot, with
each shot's current image carried over as the clip's start image when one
exists.

The skill is structural only — it does NOT generate any video. After it
runs, you can hand-pick start/end frames per clip, then call
`blooper-official/timeline-generate-all` to fan out video generation.

## When to use it

- You finished a storyboard (every shot has an image) and you want to move
  into video. The timeline structure mirroring saves you from re-listing
  every scene and shot manually.

## Parameters

| Param                  | Type | Required | Default                   | Notes                                                       |
| ---------------------- | ---- | -------- | ------------------------- | ----------------------------------------------------------- |
| `storyboard_folder_id` | text | yes      | -                         | UUID of the source Storyboard folder.                       |
| `name`                 | text | no       | `"<storyboard> timeline"` | Override the auto-derived timeline name.                    |

## Example chat invocation

> Open the storyboard folder, then type:
>
> *"Timeline-from-storyboard — call it `Heist v1 timeline`."*

## Expected output

- A new Timeline folder inside the project's Videos folder.
- One TimelineScene per source Storyboard scene; one TimelineClip per shot.
- Each clip's start image set to the shot's current image when the shot has
  one (clips for empty shots are created with no start image).
- The skill reports the new `timeline_folder_id` in chat.

## Budget

- `max_provider_calls`: 2 — one find call + one create call.
- `max_minutes`: 2 — structural only.

## Limits and known issues

- Does NOT generate video. Run `timeline-generate-all` afterwards.
- Shots without a current image become clips without a start image. Fill the
  shot or set the clip's start image manually before generating video.
- Re-running on the same storyboard produces a second timeline; the skill
  does not deduplicate.
