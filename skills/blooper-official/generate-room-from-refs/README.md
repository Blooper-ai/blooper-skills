# Generate Room from References

Generate a series of consistent room images using the reference photos
already in the current `Locations/` folder as style + content anchors. The
references are passed alongside the prompt so each generated room reads as
"more of the same world" rather than four unrelated environments.

## When to use it

- You have one or two location references in the `Locations/` folder and you
  want a quick fill of related rooms — same style, same world.
- You want each generated room saved as a brand-new file in the folder
  (so they can each get their own version tree, character refs, etc.) rather
  than as more versions of one file.

## Parameters

| Param         | Type          | Required | Default | Notes                                                              |
| ------------- | ------------- | -------- | ------- | ------------------------------------------------------------------ |
| `room_count`  | integer       | yes      | `4`     | Number of rooms to generate (`1`–`8`).                              |
| `style`       | text          | no       | -       | Free-form style direction, e.g. `"warm wood, painterly, dusk"`.    |
| `references`  | file_versions | yes      | -       | One or more IMAGE versions from the current folder used as refs.    |

## Example chat invocation

> Open the `Locations/` folder, then type:
>
> *"Generate-room-from-refs: give me 4 more rooms in the same warm-wood
> painterly style as `kitchen.png`."*

## Expected output

- `room_count` new files in the current `Locations/` folder, each with one
  initial READY version produced by the generator and the supplied references
  baked into the conditioning.

## Budget

- `max_provider_calls`: 12 — leaves room for one retry per room.
- `max_minutes`: 8 — generations run sequentially.

## Limits and known issues

- The skill assumes the references are spatially consistent (single
  location). If you pass refs from three different worlds the output will
  drift.
- `style` is appended to the prompt — keep it short. Long style prose dilutes
  the reference influence.
