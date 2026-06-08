# Generate in all providers

Fan out the same image or video prompt across every provider you have
connected, then present the results side by side so you can pick the best one.
Useful when you do not yet have a favorite engine for a given style and want a
quick A/B/C/D before committing.

## When to use it

- You are exploring style options for a new project and want a same-prompt
  shoot-out across providers.
- You are debugging why one provider keeps misreading a prompt and want to see
  whether others handle it.
- You want a single chat command that turns "try this everywhere" into a
  picker UI.

## Args

| Param              | Type    | Required | Default        | Notes                                              |
| ------------------ | ------- | -------- | -------------- | -------------------------------------------------- |
| `prompt_text`      | text    | yes      | -              | Free-form prompt, up to 2000 characters.           |
| `mode`             | select  | no       | `image`        | `image` or `video`.                                |
| `aspect`           | select  | no       | `16:9`         | `16:9`, `9:16`, `1:1`, `4:3`.                      |
| `duration_seconds` | integer | no       | `5`            | Only used when `mode = video`. Range 2-12.         |
| `seed`             | integer | no       | -              | Shared across providers when they support seeding. |

## Example chat invocation

> In an image folder, type:
>
> *"Run generate-in-all-providers: 'a foggy harbor at dawn, painterly, warm
> light', 16:9, seed 42."*

The skill fans the prompt out to every connected image provider, saves one
version per provider into the folder, and pops up a picker so you can crown a
winner.

## Output

- One file version per provider that succeeded, named `compare_<provider_id>`.
- Metadata on each version records the provider, prompt, aspect, seed, and
  duration so you can re-run a single provider later without rebuilding the
  fan-out.
- The picked version is marked canonical; the others remain as alternates in
  the same folder.

## Notes and limits

- Requires at least two connected providers. If only one is connected, the
  skill stops early with a message.
- This skill never retries a failed provider. Use the regenerate-shot skill for
  per-provider retries with tweaks.
- Video mode multiplies cost. The 12-call budget covers up to ~6 image
  providers or ~4 video providers; trim with a lower mode or skip providers in
  Settings if you need to save spend.
