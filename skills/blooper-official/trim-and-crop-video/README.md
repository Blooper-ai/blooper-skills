# Trim and crop video

Trim a video file version to a `[start_sec, end_sec)` window, then crop the trimmed result to a target aspect ratio — in a single skill invocation, no LLM involved.

This is the canonical worked example for the [**deterministic pipeline**](https://blooper.ai/docs/patterns/deterministic) authoring mode. It composes two existing tools (`trim_video_version` and `crop_video_version`) with the second step reading the first step's `new_version_id` via the `{{ steps.<id>.<field> }}` template syntax.

## How it works

The manifest declares two ordered steps:

```yaml
runtime: deterministic
deterministic:
  pipeline:
    - id: trim
      tool: trim_video_version
      args:
        file_version_id: "{{ params.file_version_id }}"
        start_sec: "{{ params.start_sec }}"
        end_sec: "{{ params.end_sec }}"
    - id: crop
      tool: crop_video_version
      args:
        file_version_id: "{{ steps.trim.new_version_id }}"
        aspect: "{{ params.aspect }}"
```

At run start the runtime:

1. Resolves every `{{ params.X }}` against the validated `run.params` dict.
2. Invokes the first step, records its result in an internal `steps.trim` slot.
3. Resolves `{{ steps.trim.new_version_id }}` against that slot before calling step 2.
4. Charges each step's tool `cost` against `spent_provider_calls` (here: `1 + 1 = 2`).
5. Publishes `skill_run_output` for each step that returned a `version_id` / `new_version_id`, so the FE updates live after both the trim AND the crop land.

If any step fails — bad params, the source version is `PENDING`, ffmpeg errors — the run terminates `FAILED` with a `step '<id>': <reason>` message on `run.error`. Earlier steps' side effects (the trim's `FileVersion` row) stay in place; we do not roll back.

## Why a pipeline instead of two separate invocations

You could install `crop-video` and `trim-video` separately and run them one after the other. The reasons to compose them into a single skill:

- **One Configure click.** The user picks start/end/aspect once, not twice.
- **One run id.** Cost, logs, cancellation, and the run card all join on a single key.
- **Atomic intent.** "I want this clip, cropped to a target aspect" is one thought; surfacing it as one skill keeps the Skills tab readable.
- **No LLM in the seam.** A naive composition routed through the chat agent would burn an LLM turn between the two tool calls; the deterministic pipeline runs both back-to-back with zero token cost.

## Params

| Name | Type | Notes |
|---|---|---|
| `file_version_id` | text (uuid) | Source video version. Optional — the Configure modal auto-fills it from the current selection via `prefill_from: context.current_version_id`. |
| `start_sec` | number | Trim window start. Must satisfy `0 ≤ start_sec < end_sec ≤ source_duration`. |
| `end_sec` | number | Trim window end (exclusive). |
| `aspect` | select | `1:1`, `9:16`, or `16:9`. Centred crop is applied to the trimmed result. |

## Cost and budget

- `trim_video_version`: cost 1
- `crop_video_version`: cost 1
- `budget.max_provider_calls`: 2

Budget-vs-tool-cost validation runs backend-side on ingest (the old in-repo `scripts/validate.py` is retired): it sums step tool costs in a deterministic pipeline and warns when `max_provider_calls` is below that sum.

## See also

- [`crop-video`](../crop-video/README.md) — the single-step deterministic skill the second pipeline step delegates to.
- [`trim-video`](../trim-video/README.md) — the single-step deterministic skill the first pipeline step delegates to.
- [Deterministic skills](https://blooper.ai/docs/patterns/deterministic) — the reference doc for `runtime: deterministic`, including the full template-syntax grammar and the failure model.
