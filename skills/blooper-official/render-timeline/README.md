# Render timeline

Render a Timeline to a single MP4 file via ffmpeg. Each call produces a new
READY FileVersion on the Timeline's backing file. Pick the output preset
to match where you're delivering — horizontal, vertical, or square.

## When to use it

- Every clip in the timeline is in good shape and you want a single
  watchable MP4.
- You want a quick proxy render at `720p` before a final `4k` pass.

## Parameters

| Param                | Type   | Required | Default | Notes                                                                                  |
| -------------------- | ------ | -------- | ------- | -------------------------------------------------------------------------------------- |
| `timeline_folder_id` | text   | yes      | -       | UUID of the Timeline folder.                                                            |
| `aspect`             | select | yes      | -       | One of `720p`, `1080p`, `4k`, `720p_vertical`, `1080p_vertical`, `4k_vertical`, `square_1080p`. |

## Example chat invocation

> Open the timeline folder, then type:
>
> *"Render-timeline at 1080p."*

## Expected output

- One new READY FileVersion on the Timeline's backing MP4 file.
- The skill reports the new version's UUID.

## Budget

- `max_provider_calls`: 1
- `max_minutes`: 20 — long timelines at 4k can push this; bump locally if
  you fork the skill.

## Limits and known issues

- Renders the timeline as-is. Clips without backing video are rendered as
  their start-image freeze frame for the clip's duration.
- The preset list is fixed in v1.0.0. Custom resolutions require a forked
  skill or a future minor bump.
