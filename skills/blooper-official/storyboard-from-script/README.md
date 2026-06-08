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

The single tool call then persists everything: a Storyboard folder with one
sub-folder per scene, one shot file per shot (with `cam_mvmnt`,
`duration_sec`, per-shot character list, and the image prompt), plus a
character placeholder file per detected character in the project's
`Characters/` folder.

## When to use it

- You have a written script and you want a structured storyboard scaffold
  without hand-listing every shot.
- You want character placeholders auto-created so you can hand-pick the
  character look later before filling the shots with images.

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
- One Character placeholder file per detected character in the
  `Characters/` folder, ready to be filled with a generated portrait.
- The skill reports the new `storyboard_folder_id` and scene / shot /
  character counts when it finishes.

## Recommended follow-up

1. Open the `Characters/` folder and generate an image for each placeholder.
2. Run `blooper-official/storyboard-generate-all` against the new storyboard
   to fill the empty shot placeholders with images, using your now-filled
   character refs.

## Budget

- `max_provider_calls`: 6 — five LLM stages plus slack.
- `max_minutes`: 45 — long scripts can take a while.

## Limits and known issues

- Source file must be a TEXT file version. Other formats (PDF, .fountain, …)
  must be converted to plain text first.
- Long scripts hit token limits inside individual LLM stages; the runtime
  tool degrades gracefully but very long features should be split into reels
  and run one reel per call.
