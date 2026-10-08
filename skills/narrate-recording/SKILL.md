---
name: narrate-recording
description: Write the narration for a terminal recording, anchored to what the screen showed and when.
disable-model-invocation: true
---

# Narrate a terminal recording

You write the narration. You know what the run means: the session that built or ran it is the domain expert. This file tells you what narration is for, where to read what the viewer saw, and the format the voice and assemble stages need. `tvid` means `<this skill's base directory>/../../scripts/tvid`.

## What narration is

The viewer watches the screen and hears you. The screen already shows *what* is happening. Your lines give the *meaning*: what this step is for, what the number that just appeared tells them, what to notice. Write for the viewer the video is for, someone who wasn't in the session. Speak the way a colleague walks someone through a demo: short spoken sentences, one idea each, concrete. Skip internal jargon, ticket IDs and file paths unless the viewer needs them.

Every line is **anchored**: it starts at the second the thing it talks about appears on screen, and only states what is on screen by then or what the session itself knows. A line never announces a result before the screen shows it.

Silence is allowed. Stretches with no narration longer than the fast-forward trigger (default 10 s) play faster in the final video, so a long wait needs a line only if something worth saying is happening.

## Sources

- **`DIR/readout.txt`** (default). Make it with `tvid readout DIR`. It shows what appeared on screen and when, in source-video seconds: `+` new line, `~` a line rewritten in place (a spinner turning into a ✔), `▸` captions and commands, `✓`/`✗` the prompt coming back with its exit code. Each line is stamped with the moment it first appeared.
- **`tvid readout DIR --at <seconds>`** prints the whole screen at one moment. Use it when a table or layout matters.
- **What you know from the session**: why the run exists, what the numbers mean, what is normal and what is a warning.
- **A log the program writes** (when the user named one). Readout times are seconds since the recording started, and its header gives that start as a wall-clock time in whole seconds. To place a log line in the video, match its text to the same text in the readout and use the readout's time. Use the clock difference only for log lines that never reach the screen.

The readout and the video come from the same cast, so they always describe the same run. Write only from a readout made from the DIR whose video you are narrating.

## Steps

1. **Map the video.** Read the whole readout. List the beats: each caption, each step or phase the program announces, each result a viewer should notice, and each long stretch with nothing new. Done when every take in the readout has its beats listed with their times.
2. **Write the lines.** One line per beat that needs words, anchored at that beat's readout time. Open with one line saying what the video shows, and close with what it proved. Done when every beat that needs words has a line.
3. **Fit the time.** A line's budget runs from its anchor to the next line's anchor, at about 2.5 spoken words per second. Trim a line that runs over. If it can't be trimmed, it may spill: the next line starts late, and the stretch is reported. Done when every line fits its budget or you know which ones spill and why.
4. **Write the files.** Write `DIR/narration.json` (the format is below). Then write `DIR/narration.md`, a table for people: video time · what's on screen · line. Done when both files exist and every `at` in `narration.json` is a time from the readout.

## narration.json

```json
{
  "lines": [
    {"id": "01", "at": 3.52, "on_screen": "Export starts", "text": "First, export. …"},
    {"id": "02", "at": 8.09, "on_screen": "Load asks to confirm", "text": "…"}
  ]
}
```

- `id`: a stable, zero-padded string. It names the clip file (`voice/01.wav`), so keep a line's id when you edit its text.
- `at`: source-video seconds, copied from the readout.
- `on_screen`: what the anchor shows, for people reading the file.
- `text`: exactly what gets spoken. Write it the way it should sound: spell out abbreviations the voice would misread ("S-Q-L" or "sequel", not "SQL"; "Kubernetes", not "k8s"), and leave out paths and IDs.
