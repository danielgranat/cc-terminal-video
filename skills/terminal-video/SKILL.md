---
name: terminal-video
description: Narrated video of a terminal run. Records the run in tmux, reads back what the screen showed, writes and voices the narration with VoiceStudio, and assembles the video with idle stretches fast-forwarded. Use when asked to record, film or demo a terminal or CLI run, to narrate a terminal recording, or to voice a narration over one; also for any single stage of that.
---

# Terminal video

Turns a terminal run into a narrated video in five stages. Each stage has its own skill file next to this one; read the file when you reach its stage. `tvid` in every stage means `<this skill's base directory>/../../scripts/tvid` (a `uv` script; first run installs its one dependency).

| Stage | File | Produces in DIR |
|---|---|---|
| Record | `../record-terminal/SKILL.md` | `recording.cast`, `recording.mp4` |
| Narrate | `../narrate-recording/SKILL.md` | `readout.txt`, `narration.json`, `narration.md` |
| Voice | `../voice-narration/SKILL.md` | `voice/*.wav`, `voice/clips.json` |
| Assemble | `../assemble-video/SKILL.md` | `final/narrated.mp4`, `final/narration.wav`, `final/narration.srt`, `final/report.json` |

A request for one stage (e.g. "narrate this recording", "redo the voice") goes straight to that stage's file; the end-to-end steps below are for the whole video.

DIR is one working folder per video. Default: `~/Movies/tvid/<short-slug>/`. The stages find each other's files there by name, so keep every artifact of one video in one DIR.

## End to end

1. **Intake.** Ask once, in a single question round, before recording anything. Ask only what the conversation hasn't already answered, and offer the default as the first option:
   - **Fast-forward**: speed for unnarrated stretches (default 2×; 1× turns it off).
   - **Trigger**: how long a stretch without narration must be before it is fast-forwarded (default 10 s).
   - **Voice**: the designed default (`male, middle-aged, moderate pitch, american accent`, seed 42), another description, or a WAV to clone (with the words spoken in it).
   - **Narration source**: the screen readout (default), plus a log file the program writes, if it has one.

   Settle these yourself unless the user raises them: who the video is for and what they should come away with (infer it from the conversation), a line longer than its slot spills into the next slot, the final frame holds until the narration ends. Done when every setting is either answered or defaulted, and you have stated the defaults you took.
2. **Record**, following the record stage file.
3. **Narrate**, following the narrate stage file. Go straight on to voice; pause for the user to review the script only if they asked to.
4. **Voice**, following the voice stage file.
5. **Assemble**, following the assemble stage file, with the intake settings.
6. **Hand over.** Report the final video's path and length, the fast-forwarded stretches and any spilled lines (from `final/report.json`), the take(s) it shows, and that nobody has listened to it yet. Done when the user has the paths and those facts in one message.

## Hand-off to other tools

When the user wants to build something else from the run, such as an animated explainer, slides or a teaser, run `tvid bundle DIR`. It writes `DIR/showcase/`: the cast, a video rendered from it, the readout, clips normalized to −16 LUFS with one shared gain, and `manifest.json`. The manifest gives each line's `anchor`, `slot_end` and `speech_end` in recording seconds, plus its text and clip file. The bundle takes the same `--urls`, `--home` and `--pattern` flags as `tvid redact`, and applies them to its own copies only. Point the other tool at `manifest.json`.

For an animated explainer, use the anidoodle plugin. It's an optional plugin, listed in this plugin's marketplace. If its skill isn't available in the session, give the user the install command, `claude plugin install anidoodle@tmux-recording`, and tell them to start a new session; this session doesn't install it. Its first film downloads Node packages and a headless Chromium, which anidoodle's own skill sets up.
