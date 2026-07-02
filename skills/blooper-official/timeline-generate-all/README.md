# Generate all timeline clips

Fan out one `generate_video` job per empty or image-only clip in a timeline,
carrying each clip's stored start/end frames as `ref_version_ids`. Clips
whose backing video is already READY are skipped unless `force=true`.

**Reference semantics** (why this skill is careful with refs): for video
generation the reference images are FRAMES, not identity hints — slot 0 is
the start frame, and if more than one id is passed the LAST one becomes the
end frame and the provider MORPHS between them. So each clip gets its own
start image (plus its end image only when the editor authored one), and a
clip with no start image gets AT MOST one character reference. Passing every
character into every clip — what v1.1.0 did — both collapsed casts to one
dominant face and accidentally created start→character morphs.

## When to use it

- You have a timeline and want to render every clip to video without
  clicking each one individually.

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

- Clips with state `empty` get at most ONE reference (the most relevant
  character for that clip's prompt). For frame-accurate clips, set the start
  (or start+end) image first — the skill picks them up automatically.
- The Characters folder lookup (for empty clips) is by literal name; the
  folder must be named `Characters` and live at the project root.
- Motion-only prompts: the skill never re-describes the character/scene in
  its video prompts — the reference frames carry the look.
