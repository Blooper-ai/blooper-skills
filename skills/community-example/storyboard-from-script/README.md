# Storyboard from script

Turn a screenplay or beat sheet into a shot-by-shot storyboard with one image
per shot. The skill drafts a shot list from the script, writes an image prompt
for each shot in a consistent visual style, and saves every shot as a new file
version in the current folder.

## When to use it

- You have a short script, beat sheet, or scene treatment and you want a visual
  preview before committing time to layout or animatics.
- You want a fast, consistent style pass across an entire scene rather than
  hand-drawing each frame.
- You are pitching a sequence and need eight to twenty images that read in
  order.

## Args

| Param       | Type         | Required | Default            | Notes                                                       |
| ----------- | ------------ | -------- | ------------------ | ----------------------------------------------------------- |
| `script`    | file_version | yes      | -                  | A `script` file picked from the current folder.             |
| `style`     | select       | no       | `cinematic`        | `cinematic` / `graphic_novel` / `storyboard_sketch` / `photoreal`. |
| `aspect`    | select       | no       | `16:9`             | `16:9` / `2.39:1` / `4:3` / `1:1`.                          |
| `max_shots` | integer      | no       | `24`               | Caps how many shots the skill will try to draw (1-80).      |

## Example chat invocation

> Open a storyboard folder that contains a script file, then type:
>
> *"Run storyboard-from-script on the latest version of `pilot.script`,
> graphic-novel style, 2.39:1, max 18 shots."*

The skill will pick the file version, draft a numbered shot list, and produce
up to 18 image versions named `shot_001`, `shot_002`, ... in the folder.

## Output

- One file version per shot, saved into the current folder.
- Each file version carries metadata `{shot_id, slug_line, camera, mood}` so
  later skills (re-render, swap style, edit dialogue) can target specific shots.
- The chat reply summarizes shots drawn, shots skipped, and any warnings.

## Notes and limits

- Character consistency is best-effort. For tight character locking, generate a
  reference sheet first and pass it through the `regenerate-shot` skill per
  frame.
- `max_shots` is a cap, not a target. Short scripts produce fewer shots.
- Long features will hit the 40-call budget; split the script into reels and
  run one reel per folder.
- Style names are platform presets; new presets are added in minor versions.
