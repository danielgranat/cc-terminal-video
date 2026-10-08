---
name: assemble-video
description: Lay voice clips over a terminal recording, fast-forward unnarrated stretches, and write the narrated MP4.
disable-model-invocation: true
---

# Assemble the narrated video

`tvid assemble DIR` places each clip from `DIR/voice/` at its line's anchor on `DIR/recording.mp4`, then writes `DIR/final/`. `tvid` means `<this skill's base directory>/../../scripts/tvid`.

## How the timeline is built

Lines play in anchor order, with at least `--min-gap` (0.3 s) of silence between them.

- **Overrun.** When a line is still playing at the next line's anchor:
  - `--overrun spill` (default): the next line starts when this one ends, while the video keeps playing.
  - `--overrun freeze`: the video holds the frame at the next anchor until this line ends, so every line starts exactly on its anchor.
- **Fast-forward.** A stretch with no narration longer than `--ff-gap` seconds (default 10) plays at `--ff-speed` (default 2; 1 turns it off). `--ff-margin` (1 s) at each end of the stretch stays at real speed, so the jump never starts mid-word.
- **The end.** If the narration outlasts the video, the last frame holds until it ends. The final frame then holds for `--tail` seconds (1.5).

## Steps

1. **Assemble.** Run `tvid assemble DIR` with the user's settings, e.g. `--ff-speed 3 --ff-gap 8 --overrun freeze`. Use `--name` for a different output file name. Done when it prints the output paths.
2. **Check it.** Compare the audio and video lengths in `final/narrated.mp4`: `ffprobe -v error -show_entries stream=codec_type,duration -of compact <file>`. Extract a frame at one or two line starts from `final/report.json` (`ffmpeg -ss <output_start> -i <file> -frames:v 1 <png>`), and confirm the screen shows what that line talks about. Done when the lengths match within 0.1 s and the frames match their lines.
3. **Report.** Tell the user:
   - the final length next to the source length;
   - each fast-forwarded stretch (source range, speed, new length);
   - each line that started late or held the frame, and by how much;
   - the outputs: `narrated.mp4`, `narration.wav` (the narration alone, timed to the final video), `narration.srt` (subtitles), `report.json`.

   Nobody has listened to it yet, so say so.
