# Generate in all providers

Run the same prompt through every registered image provider, get one new
version per provider all parented under the file's current version, then
ask the user to pick the winner — and promote that winner to the file's
current version.

Useful when you don't yet know which model handles a particular idea best
(stylised vs. photoreal, character anchoring vs. wild composition, etc.).

## When to use it

- You have an image file and a prompt, and you want a side-by-side
  comparison across every connected image provider before committing to
  one as the canonical version.

## Parameters

| Param    | Type | Required | Default | Notes                                       |
| -------- | ---- | -------- | ------- | ------------------------------------------- |
| `prompt` | text | yes      | -       | The prompt to run through every provider.   |

## Example chat invocation

> Open an image file, then type:
>
> *"Generate in all providers: a misty pine forest at golden hour."*

The skill calls `compare_providers` under the hood. That single tool issues
one `generate_image` per provider with the same prompt + parent version so
seeds, references, and conditioning stay aligned across providers.

## Expected output

- One new version per provider, attached to the current file (all hanging
  off the same parent version).
- A picker UI listing every result by provider display name.
- When the user picks, that version becomes the file's `current_version`.
- If the user cancels, all generated versions stay in the version tree —
  nothing is promoted, nothing is destroyed.

## Budget

- `max_provider_calls`: 100 — this skill declines to set its own ceiling. The
  fan-out is one call per applicable provider, read live from the registry, so
  any snug figure expires the next time a provider is added; and because the
  charge is taken before the fan-out and kept if a provider fails part way, too
  snug a cap makes the first partial failure fatal rather than retryable. 100 is
  the default of your account's own provider-call ceiling, which the runtime
  applies as `min(your ceiling, this)` — so your account setting and your wallet
  are what bound a run. A typical run spends one call per provider (3–5 today).
- `max_minutes`: 30 — generous on purpose: the picker step pauses the run and
  HITL wall-clock counts toward the deadline (anchored at run start), so a
  user who goes off browsing the version tree before picking (the onboarding
  guide even tells them to) must not come back to a timed-out FAILED run.

## Limits and known issues

- The skill is one-shot by design. It does not loop, regenerate failed
  providers, or fan-out a second round.
- Must be run on an image file (`file_id` non-null). Running outside an
  image file stops with an explanatory message.
- The picker step blocks until the user responds. If the user walks away
  the skill times out at `max_minutes`.
