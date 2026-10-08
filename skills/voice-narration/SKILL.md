---
name: voice-narration
description: Generate one voice clip per narration line with a local VoiceStudio backend.
disable-model-invocation: true
---

# Voice the narration

`tvid voice DIR` reads `DIR/narration.json` (format: `../narrate-recording/SKILL.md`) and writes `DIR/voice/<id>.wav` plus `DIR/voice/clips.json` with each clip's measured duration. `tvid` means `<this skill's base directory>/../../scripts/tvid`.

The engine is the user's VoiceStudio install, reached at `http://localhost:3900` (override with `--url` or `VOICESTUDIO_URL`). Use VoiceStudio. If it can't run here, tell the user what's missing, and switch engines only if they say so.

## One voice for every line

Every line is cloned from a single reference clip, so the whole narration sounds like one person.

- **Designed voice** (default): `--instruct "male, middle-aged, moderate pitch, american accent" --seed 42`. `tvid` generates one reference sentence in that voice, keeps it as `voice/voice-ref.wav`, and clones every line from it. VoiceStudio understands only these terms: gender (male, female), age (child, teenager, young adult, middle-aged, elderly), pitch (very low, low, moderate, high or very high pitch), whisper, and an accent (american, british, australian, canadian, indian, japanese, korean, chinese, russian, portuguese). Other words are ignored. For a narration that isn't in English, also pass `--language <name>` and `--ref-sentence "<one or two sentences in that language>"`, so the reference voice speaks the same language as the lines.
- **Cloned voice**: `--ref <wav> --ref-text "<exact words spoken in it>"`. Use a clean 5–15 second clip.

The reference stays in `voice/`, so a line regenerated later still matches the rest. Changing `--instruct`, `--seed`, `--language` or `--engine` regenerates the reference and every clip.

## The backend: leave it as you found it

`tvid voice` manages the backend's lifecycle, so you never start or stop it by hand:

- **Already running** (the desktop app, or a backend the user started): `tvid` uses it and never stops it.
- **Not running**: `tvid` starts it from the user's VoiceStudio checkout on the first clip that needs generating, and stops it when the command ends. The checkout comes from `--voicestudio-dir` or `VOICESTUDIO_DIR`. Startup and model load add about half a minute. A run with nothing to regenerate never starts it.
- **Not running, and no checkout given**: `tvid` stops and says so. Ask the user either to start VoiceStudio themselves, or for the path to their checkout. Pass that path with `--voicestudio-dir`, and mention that `export VOICESTUDIO_DIR=<path>` in their shell profile saves them answering again.
- **`--keep-backend`**: leaves a backend `tvid` started running. Use it while you're redoing lines. `tvid voice-stop DIR` stops it later, and only ever stops a backend `tvid` started. If you keep one, stop it before you hand over.

## Steps

1. **Generate.** `tvid voice DIR [voice options]`. Only lines whose text or voice changed are regenerated. To redo a line, edit its `text` (keep its `id`) and run again. Done when the command prints its table with a clip for every line.
2. **Check the pace.** The table lists each clip's seconds per word. A clip outside 0.22–0.7 s per word is marked: it was probably cut off, or it repeats or garbles words. Rephrase the line and regenerate. Done when no clip is marked, or you have told the user which marked clips remain and why.
