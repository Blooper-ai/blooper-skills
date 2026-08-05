# Copyright Check

Scan images and video for third-party IP — trademarks, branded designs,
characters, celebrities, and artwork — powered by
[Copysight](https://app.copysight.ai).

## What it does

- **On an image or video file:** scans that file and reports detections in
  chat.
- **On a folder:** scans every image and video inside, then saves a markdown
  **IP Report** file into the folder — one table row per detection with the
  IP name, category, rights holder, confidence, and (for video) the
  timecodes where it appears.
- Detections at or above your **Flag threshold** are marked ⚠ FLAGGED.
- With **Attach annotated versions** on (default):
  - an **image** with detections gets a new version with labeled bounding
    boxes drawn on it;
  - a **video** gets one annotated still per detected IP, captured at the
    moment that IP appears most strongly and labeled with its timecode.

  The original stays the current version either way.
- Files containing real faces are listed as **likeness cautions** even when
  no IP is detected.

## When to use it

Before shipping a campaign, check that generated or sourced assets don't
carry someone else's IP — a logo in the background of a hero shot, a
recognizable character in a b-roll clip, a celebrity likeness in a
storyboard frame.

## Params

| Param | Type | Default | Meaning |
| --- | --- | --- | --- |
| Flag threshold (0–1) | number | `0.5` | Detections with confidence at or above this are flagged |
| Attach annotated versions | boolean | `true` | Draw bounding boxes on a copy, attached as a new version |
| Deep analysis on images | boolean | `false` | Run the slower, higher-recall model on images too. Video always uses it |

## Example output

```
# IP Report — Hero Shots

| File | Type | IP | Category | Rights holder | Confidence | Timecodes | Flagged |
| --- | --- | --- | --- | --- | --- | --- | --- |
| hero-3.png | image | Grace Hopper | Celebrities and famous people | Estate of Grace Hopper | 0.99 | — | ⚠ |
| teaser.mp4 | video | Big Buck Bunny | Trademarks | Blender Foundation | 1.00 | 0:00, 0:44, 0:48 (+2 more) | ⚠ |
| clean.png | image | — | — | — | — | — | |

Likeness cautions: hero-3.png

Scanned 3 files (2 images, 1 video); 2 with detections; 2 flagged (>= 0.5).

Automated scan; not legal advice.
```

## Cost

One Copysight call per file, whatever its type — so a 20-image folder is 20
calls. The run budget allows ~50 files per run before the budget-extension
prompt appears.

Wall clock differs a lot by media type: an image scan is seconds, a video
scan is a large upload plus a deep multi-frame analysis and can take
minutes. The skill's 30-minute budget is sized for a folder holding a few
clips; a folder of many long videos may need a budget extension.

## Notes

- Video is capped at **500 MB** per file and must have finished processing
  (`READY`). Files that fail either check are recorded in the report and the
  sweep continues.
- Results are an automated scan, **not legal advice**.
