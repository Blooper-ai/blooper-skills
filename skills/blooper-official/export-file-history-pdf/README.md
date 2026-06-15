# Export file history (PDF)

Export a file's complete version history as a **PDF** that lands in the
project's **Exports** folder. The document lists every version from the first
to the current one — for each: created time, status, model/provider, mode,
the prompt, the references it consumed, and a thumbnail. When you're done,
you get an "export ready" notification that links straight to the PDF.

Deterministic (`max_provider_calls=0`) — pure data + PDF render, no LLM and no
provider calls.

## When to use it

- You want a shareable, archival record of how a file evolved across versions.
- You need to show a client/reviewer the prompts and references behind each
  iteration.
- You want the full provenance of a final asset — not just this file's
  versions, but how every reference that fed it was made, recursively.

## Parameters

| Param                | Type    | Required | Default | Notes                                                                                          |
| -------------------- | ------- | -------- | ------- | ---------------------------------------------------------------------------------------------- |
| `file_id`            | text    | no       | anchored file | UUID of the file to export. Pre-filled from the open file; omit to use it.               |
| `include_provenance` | boolean | no       | false        | Also append the **recursive cross-file provenance** of the current version.                                              |
| `max_depth`          | integer | no       | entire tree  | Optional cap on how deep to follow the provenance graph. Omit to walk the **whole tree** — cycles and shared inputs are cut automatically, so it always terminates. |

## Example chat invocation

> Open any file, then type:
>
> *"Export file history on this file."*
>
> …or, with full lineage:
>
> *"Export file history with provenance, depth 4."*

## Expected output

- One new `PDF` FileVersion in the project's **Exports** folder named
  `<file> — history.pdf`.
- An `EXPORT_READY` notification (only for you) that deep-links to the PDF and
  offers a Download button.
