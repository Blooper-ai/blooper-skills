# Trim video

Trim a single VIDEO file version to a given `[start_sec, end_sec)` range.
Produces a new READY file version on the same file. Deterministic
(`max_provider_calls=1`) — this is a pure ffmpeg pass, no LLM-side
decisions.

## When to use it

- You have a finished or generated clip and need a tighter cut without
  re-generating.

## Parameters

| Param             | Type   | Required | Default | Notes                                                                      |
| ----------------- | ------ | -------- | ------- | -------------------------------------------------------------------------- |
| `file_version_id` | text   | yes      | -       | UUID of the source video version.                                          |
| `start_sec`       | number | yes      | -       | Start of the kept range, inclusive.                                        |
| `end_sec`         | number | yes      | -       | End of the kept range, exclusive. Must be strictly greater than `start_sec`. |

## Example chat invocation

> Open a video file, then type:
>
> *"Trim-video on the current version from 1.2 to 4.0."*

## Expected output

- One new READY FileVersion on the same file containing only the requested
  range.
- The skill reports the new version's UUID.

## Budget

- `max_provider_calls`: 1 — a single tool call.
- `max_minutes`: 5 — bounded by source length and ffmpeg.

## Limits and known issues

- Source must be a VIDEO file version.
- The trim is frame-accurate to the granularity ffmpeg supports for the
  source codec; expect tiny rounding on inter-frame seeks.
