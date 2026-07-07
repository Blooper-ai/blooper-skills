# Copyright Check

Scan images for third-party IP — trademarks, branded designs, characters,
celebrities, and artwork — powered by [Copysight](https://app.copysight.ai).

## What it does

- **On an image file:** scans that image and reports detections in chat.
- **On a folder:** scans every image inside, then saves a markdown
  **IP Report** file into the folder — one table row per detection with the
  IP name, category, rights holder, and confidence.
- Detections at or above your **Flag threshold** are marked ⚠ FLAGGED.
- With **Attach annotated versions** on (default), each image with
  detections gets a new version with labeled bounding boxes drawn on it —
  the original stays the current version.
- Images containing real faces are listed as **likeness cautions** even
  when no IP is detected.

## Params

| Param | Default | Meaning |
| --- | --- | --- |
| Flag threshold (0–1) | 0.5 | Detections with confidence at or above this are flagged |
| Attach annotated versions | true | Draw bounding boxes on a copy, attached as a new version |

## Notes

- Images and GIFs only. Video is not supported yet.
- One Copysight call per image; the run budget allows ~50 images per run
  (budget extension kicks in beyond that).
- Results are an automated scan, **not legal advice**.
