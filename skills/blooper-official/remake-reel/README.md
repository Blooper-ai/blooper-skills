# Remake a reel in another world

Takes a short video — an Instagram Reel link, or a video already in the
project — breaks it into its shots, and rebuilds it shot by shot in a
different visual world. The source is treated as a blueprint: shot list,
durations, cut points, framing, camera movement, the performers and their
blocking carry over. The setting, wardrobe, props and grade are replaced.

## What it does

1. Imports the link (`import_video_from_url`) or takes the given video.
2. Reads the shots (`analyze_reference_video`) and **shows the list for
   correction** before anything is generated.
3. Cuts one clip per shot into a "Shots" tag (`trim_video_version` +
   `save_as_new_file`).
4. Per shot: pulls a frame, restyles it into the world with the project's
   References attached (`generate_image`), then has that still perform the
   shot's moves (`copy_moves`). After the first shot it stops once to let you
   pick the lane.
5. Assembles the rebuilt shots on a timeline at the source shots' exact
   lengths, renders (9:16 by default), and puts the original's sound back
   under the picture (`add_soundtrack`).

## The world

The world is what the project already holds: its brief, decisions and the
images in the References tag. Put two or three stills of the look there
first; describe it in the "world" parameter.

## Cost

One restyled still and one `copy_moves` render per shot. A 12-shot reel is
roughly 24 paid calls; the skill's budget allows a retry per shot.
