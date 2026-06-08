# Character Emotions

Generate four expressive emotion variants of a single character and attach
each one as a **new version of the same file** — not as four separate files.
Each version is labelled with the emotion (Happy, Sad, Angry, Surprised) so
the file's version tree reads like a mood pass on one design.

The skill self-verifies every variant with a vision check: if the model
regresses to a six-up character-sheet / grid layout, the skill retries
once and parents the retry under the failed attempt, preserving lineage in
the version tree.

## When to use it

- You finalised a character image in `Characters/` and now want a quick mood
  pass to see how the design holds up in alternate expressions.
- You want every emotion to live as a sibling version of the original so you
  can A/B-swap them without polluting the folder with new files.
- You need the retry-on-grid-regression behaviour without writing your own
  vision check.

## Parameters

| Param           | Type    | Required | Default                             | Notes                                                                 |
| --------------- | ------- | -------- | ----------------------------------- | --------------------------------------------------------------------- |
| `emotion_count` | integer | yes      | `4`                                 | How many variants to emit (`2`–`8`).                                  |
| `emotions`      | text    | no       | `happy, sad, angry, surprised`      | Comma-separated emotion list. Override to e.g. `proud, scared, tired`. |

## Example chat invocation

> Open a character file inside the `Characters/` folder, then type:
>
> *"Run character-emotions on this — give me happy, sad, surprised, proud."*

The skill reads the current version of the file as the source, then emits
one new version per emotion as a child of the original.

## Expected output

- `emotion_count` new versions on the **current file**, labelled with each
  emotion in TitleCase (`Happy`, `Sad`, …).
- Any retry attempt is parented under the failed version, labelled
  `<Emotion> (retry)`, so you can see exactly which generation regressed.

## Budget

- `max_provider_calls`: 50 — generous to cover retries on every variant.
- `max_minutes`: 12 — generations are sequential (active-generation lock).

## Limits and known issues

- Designed for character-shaped subjects. On heavily abstract designs the
  vision check's regression heuristics can over-trigger.
- Sequential by design: the active-generation lock on the file means each
  emotion waits for the previous one to finish before kicking off.
- Retry is one-shot. If both attempts regress to a grid the skill accepts
  the second result and moves on rather than looping forever.
