# Storyboard from script

Take a plain-text script (a `.txt` / TEXT file version sitting anywhere in
the project) and produce a fully populated storyboard in one shot. A single
runtime tool — `generate_storyboard_from_script` — fans out five LLM stages
internally:

1. **Scene partition** — split the script into scenes.
2. **Director shot list** — per scene, produce a shot list with camera
   movement, duration, and which characters are present in each shot.
3. **Character detection** — list every character that appears.
4. **Character dedup** — collapse aliases / role-mentions to canonical names
   with appearance, clothing, and role notes.
5. **Photorealistic image prompts** — one prompt per shot, suitable for
   downstream `generate_image` calls.

The single tool call then persists the storyboard structure: a Storyboard
folder with one sub-folder per scene and one shot file per shot (with
`cam_mvmnt`, `duration_sec`, per-shot character list, and the image prompt).

**Structure only, by design** (`structure_only=true`, the tool's default):
the pipeline creates **no** character or location image files. Your existing
`Characters/` and `Locations/` assets stay the single source of truth — the
per-shot character lists reference them by name, and they get attached as
image references when the shots are rendered. This is what keeps every shot
showing *your* exact cast instead of minting a duplicate cast of lookalikes.

## When to use it

- You have a written script and you want a structured storyboard scaffold
  without hand-listing every shot.
- You already have (or plan to generate) your cast in `Characters/` and want
  the shot plan wired to those exact assets.

## Parameters

| Param                  | Type         | Required | Default | Notes                                                          |
| ---------------------- | ------------ | -------- | ------- | -------------------------------------------------------------- |
| `text_file_version_id` | file_version | yes      | -       | The TEXT file version of the script. Pick from anywhere in the project. |
| `storyboard_name`      | text         | no       | derived | Leave blank to derive from the script's title.                  |

## Example chat invocation

> *"Storyboard-from-script: run on `Heist – draft 4.txt`, name it
> `Heist v1 board`."*

## Expected output

- One new Storyboard folder with one sub-folder per scene.
- One empty shot file per shot, populated with metadata (`cam_mvmnt`,
  `duration_sec`, per-shot character list, image prompt).
- No new files in `Characters/` or `Locations/` — deliberate; see above.
- The skill reports the new `storyboard_folder_id` and scene / shot counts
  when it finishes.

## Recommended follow-up

1. Make sure every character in the cast has an image in `Characters/`
   (generate any that are missing).
2. Render the shots from the chat: generate each shot into its card with
   your character (and location) images attached as references, so every
   shot shows your exact cast.

## Budget

- `max_provider_calls`: 8 — the pipeline tool (cost 5) plus reflection/retry
  headroom.
- `max_minutes`: 45 — long scripts can take a while.

## Limits and known issues

- Source file must be a TEXT file version. Other formats (PDF, .fountain, …)
  must be converted to plain text first.
- Long scripts hit token limits inside individual LLM stages; the runtime
  tool degrades gracefully but very long features should be split into reels
  and run one reel per call.
