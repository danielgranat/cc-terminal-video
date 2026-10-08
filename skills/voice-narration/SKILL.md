---
name: voice-narration
description: Generate one voice clip per narration line, with Kokoro by default or VoiceStudio.
disable-model-invocation: true
---

# Voice the narration

`tvid voice DIR` reads `DIR/narration.json` (format: `../narrate-recording/SKILL.md`) and writes `DIR/voice/<id>.wav` plus `DIR/voice/clips.json` with each clip's measured duration. `tvid` means `<this skill's base directory>/../../scripts/tvid`.

## Engines

- **Kokoro** (default): a small local model with fixed voices. It needs no setup: the first run downloads it (about 350 MB, once) into the user's cache and checks it against pinned hashes. It runs on a normal CPU, at about a second per line.
  - Choose a voice with `--voice <name>` (default `am_michael`, an American male); `tvid voice --list-voices` lists them all. The first letter of the name sets the language (`a` American English, `b` British English, `e` Spanish, `f` French, `h` Hindi, `i` Italian, `j` Japanese, `p` Brazilian Portuguese, `z` Mandarin), and the second the gender (`f`, `m`). `--lang` overrides the language.
  - A fixed voice sounds the same on every line, so the narration is one consistent voice.
- **VoiceStudio** (`--engine voicestudio`): for users who already run [VoiceStudio](https://github.com/debpalash/VoiceStudio) and want a designed or cloned voice. Use it only when the user asks for it. The details, including its backend, are in [VoiceStudio](#voicestudio) below.

`--speed` (default 1.0) applies to both engines.

## Steps

1. **Generate.** Run `tvid voice DIR [--voice <name>]`. Only lines whose text or voice changed are regenerated. To redo a line, edit its `text` (keep its `id`) and run again. Done when the command prints its table with a clip for every line.
2. **Check the pace.** The table lists each clip's seconds per word. A clip outside 0.22–0.7 s per word is marked: it was probably cut off, or it repeats or garbles words. Rephrase the line and regenerate. Done when no clip is marked, or you have told the user which marked clips remain and why.

## VoiceStudio

Every line is cloned from a single reference clip, so the whole narration sounds like one person.

- **Designed voice** (default with this engine): `--instruct "male, middle-aged, moderate pitch, american accent" --seed 42`. `tvid` generates one reference sentence in that voice, keeps it as `voice/voice-ref.wav`, and clones every line from it. VoiceStudio understands only these terms: gender (male, female), age (child, teenager, young adult, middle-aged, elderly), pitch (very low, low, moderate, high or very high pitch), whisper, and an accent (american, british, australian, canadian, indian, japanese, korean, chinese, russian, portuguese). For a narration that isn't in English, also pass `--language <name>` and `--ref-sentence "<one or two sentences in that language>"`.
- **Cloned voice**: `--ref <wav> --ref-text "<exact words spoken in it>"`. Use a clean 5–15 second clip.

The backend is left as `tvid` found it:

- **Already running** (the desktop app, or a backend the user started): `tvid` uses it at `http://localhost:3900` (`--url`, `VOICESTUDIO_URL`) and never stops it.
- **Not running**: `tvid` starts it from the user's VoiceStudio checkout (`--voicestudio-dir` or `VOICESTUDIO_DIR`) on the first clip that needs generating, and stops it when the command ends.
- **Not running, and no checkout given**: `tvid` stops and says so. Ask the user either to start VoiceStudio, or for the path to their checkout.
- **`--keep-backend`**: leaves a backend `tvid` started running while you redo lines. `tvid voice-stop DIR` stops it. Stop it before you hand over.
