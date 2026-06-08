# Crop video

Crop a VIDEO file version to one of three aspect-ratio presets with a
centered crop. Produces a new READY file version on the same file. Like
`trim-video`, this is a deterministic ffmpeg pass — no LLM-side decisions.

## When to use it

- You need a 9:16 vertical version of a 16:9 source for social, or vice
  versa.
- You want a quick `1:1` square crop for a thumbnail.

## Parameters

| Param             | Type   | Required | Default | Notes                                       |
| ----------------- | ------ | -------- | ------- | ------------------------------------------- |
| `file_version_id` | text   | yes      | -       | UUID of the source video version.           |
| `aspect`          | select | yes      | -       | One of `1:1`, `9:16`, `16:9`.               |

## Example chat invocation

> Open a video file, then type:
>
> *"Crop-video to 9:16."*

## Expected output

- One new READY FileVersion containing the centered crop.
- The skill reports the new version's UUID.

## Budget

- `max_provider_calls`: 1
- `max_minutes`: 5

## Limits and known issues

- Centered crop only; no off-center / panned-crop option in this skill.
- Cropping an already-vertical source to `16:9` will produce heavy
  letterbox-equivalent loss in subject coverage — pick a target close to
  the source ratio.
