# Generate all timeline clips

Fan out one `generate_video` job per empty or image-only clip in a timeline,
carrying the clip's stored prompt plus optional start/end image references.
Clips whose backing video is already READY are skipped unless
`force=true`.

The skill also includes every character reference image from the project's
`Characters/` folder as a `ref_version_ids` entry on every clip — that's
what keeps each generated clip on-model with the chosen characters across
the whole sequence.

## When to use it

- You created a timeline (typically with
  `blooper-official/timeline-from-storyboard`) and you want to render every
  clip to video without clicking each one individually.

## Parameters

| Param                | Type    | Required | Default | Notes                                                                                  |
| -------------------- | ------- | -------- | ------- | -------------------------------------------------------------------------------------- |
| `timeline_folder_id` | text    | yes      | -       | UUID of the Timeline folder.                                                            |
| `force`              | boolean | no       | `false` | When true, re-generate clips whose state is already `has_video`.                        |

## Example chat invocation

> Open the timeline folder, then type:
>
> *"Timeline-generate-all — render everything that's still empty."*

## Expected output

- One new video file version per processed clip, attached to the clip's
  backing file.
- A one-line per-clip summary in chat (which clip, what state, what was
  done).

## Budget

- `max_provider_calls`: 60 — one per clip for a 60-clip timeline.
- `max_minutes`: 45 — video generation is slow; the runtime parallelises.
- `max_sub_runs`: 60 — each clip generation counts as one sub-run.

## Limits and known issues

- Clips with state `empty` get a text-only generation. To get image-anchored
  clips, set the start (or start+end) image first — the skill picks them up
  automatically.
- The Characters folder lookup is by literal name; the folder must be named
  `Characters` and live at the project root.
- If the Characters folder is empty or absent, clips render without
  character refs. Narration in chat warns about this.
