# Regenerate shot

Make a new version of a single shot with a focused tweak (style nudge, camera
move, prompt edit) while keeping the rest of the storyboard locked. The skill
reuses the original provider, seed, and metadata so the new version sits cleanly
next to its siblings.

## When to use it

- One frame in an otherwise-good storyboard is off and you want to fix just
  that frame.
- You want to A/B a small variation (wider lens, warmer lighting) without
  rerunning the whole scene.
- You want to keep a clear parent-child trail of versions on a single shot.

## Args

| Param         | Type         | Required | Default | Notes                                                          |
| ------------- | ------------ | -------- | ------- | -------------------------------------------------------------- |
| `source_shot` | file_version | yes      | -       | The shot file version to refine. Pick from the current folder. |
| `tweak`       | text         | yes      | -       | Plain-language description of the change (max 1000 chars).     |
| `keep_seed`   | boolean      | no       | `true`  | Reuse the source seed when the provider supports it.           |
| `strength`    | number       | no       | `0.45`  | 0.0 = stay close, 1.0 = full reroll. Provider-dependent.       |
| `variants`    | integer      | no       | `1`     | How many versions to make (1-4).                               |

## Example chat invocation

> Open a shot file inside a `storyboard` folder, then type:
>
> *"Run regenerate-shot on this frame: 'push the camera lower and add a small
> reflection in the puddle', keep seed, strength 0.35, two variants."*

The skill loads the shot's metadata, applies the tweak on top of the original
prompt, and submits two new jobs to the same provider with the original seed.
Both results are saved as new versions of the same shot.

## Output

- One to four new file versions saved under the same shot as the source.
- Each new version carries metadata `{provider, prompt, seed, aspect, tweak,
  strength, parent_version_id}` so the version history is traceable end to end.
- Chat reply summarizes provider, seed handling, variant count, and any
  warnings.

## Notes and limits

- The skill only calls the provider that produced the source version. If you
  want to switch providers, use the generate-in-all-providers skill instead.
- `strength` is a hint, not a guarantee. Different providers interpret it
  differently; 0.4 is a reasonable starting point for a focused tweak.
- `variants` is capped at 4 to stay inside the 6-call budget with headroom for
  one retry per variant.
- Provider seed reuse depends on the provider; if unsupported, the new version
  gets a fresh seed and the metadata records it.
