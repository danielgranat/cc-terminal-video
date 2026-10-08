# terminal-video

A Claude Code plugin that turns a terminal run into a narrated demo video.

Claude runs your commands in a recorded tmux session. Then it reads back what the screen showed and when, writes narration tied to those moments, voices it with a local [VoiceStudio](https://github.com/debpalash/VoiceStudio) backend, and assembles the final MP4. Long silent stretches are fast-forwarded.

```
record ──► readout ──► narrate ──► voice ──► assemble
tmux +     screen text   lines anchored   one WAV per   MP4 + narration WAV
asciinema  with times    to readout times line (VoiceStudio)  + SRT + report
```

The plugin doesn't run your demo for you. The agent in your session knows the domain and decides what to run. The plugin gives it the tools, the order of work, and a definition of done for each stage.

## Skills

| Skill | How it's invoked | What it does |
|---|---|---|
| `terminal-video` | `/terminal-video`, or by the agent when you ask for a narrated terminal video | The whole pipeline, after one round of intake questions. Also routes a single-stage request to the right stage. |
| `record-terminal` | `/record-terminal` | Plans the takes, does setup off camera, records each take with a caption, renders to MP4 at real speed. |
| `narrate-recording` | `/narrate-recording` | Explains what narration is for, how to read the readout, and the `narration.json` format. The session's own model writes the lines. |
| `voice-narration` | `/voice-narration` | Generates one clip per line with VoiceStudio in one consistent voice, and flags clips whose pace looks wrong. |
| `assemble-video` | `/assemble-video` | Places the clips, fast-forwards unnarrated stretches, handles lines that overrun, and writes the outputs. |

### Intake questions (`/terminal-video`)

| Question | Default |
|---|---|
| Fast-forward speed for unnarrated stretches | 2× (1× turns it off) |
| How long a stretch without narration must be before it's fast-forwarded | 10 s |
| Voice | designed: `male, middle-aged, moderate pitch, american accent`, seed 42; or a WAV to clone |
| Narration source | the screen readout; optionally also a log file the program writes |

## Install

Requirements: macOS with zsh, plus `brew install tmux asciinema agg ffmpeg uv`. You also need a [VoiceStudio](https://github.com/debpalash/VoiceStudio) checkout with its backend dependencies and model already installed. `tvid` looks for it in `~/dev/oss/VoiceStudio`; set `VOICESTUDIO_DIR` if yours is elsewhere.

```
claude plugin marketplace add danielgranat/cc-terminal-video
claude plugin install terminal-video@tmux-recording
```

You can also run the same steps inside Claude Code with `/plugin marketplace add danielgranat/cc-terminal-video` and `/plugin install terminal-video@tmux-recording`. Start a new session afterwards to load the skills.

To update to the latest version:

```
claude plugin marketplace update tmux-recording
claude plugin update terminal-video@tmux-recording
```

## Usage

In any project, after a session has done some work worth showing:

```
/terminal-video
```

Or ask for it directly: "record the migration script running twice and make a narrated video of it". Each stage also works on its own. For example, `/voice-narration` with a different voice, then `/assemble-video --ff-speed 3`.

Each video gets one working folder (default `~/Movies/tvid/<slug>/`):

```
recording.cast      asciinema recording: the source of truth for time and screen text
recording.mp4       the cast rendered at real speed
readout.txt         what appeared on screen, and when
narration.json      the lines to speak, each anchored to a source-video time
narration.md        the same lines as a table for people
voice/              <id>.wav per line, voice-ref.wav, clips.json (durations, pace check)
final/              narrated.mp4, narration.wav, narration.srt, report.json
showcase/           hand-off bundle for other tools (optional, see below)
```

## The `tvid` CLI

All the mechanics live in one script, [`scripts/tvid`](scripts/tvid). It's a `uv` script, and its only dependency is `pyte`, installed on first run. The skills call it; you can call it yourself too:

```
tvid rec start DIR --cwd <project>             open a recorded zsh in a detached tmux session
tvid rec run DIR "<cmd>" --caption "<text>"    type a command, wait for the prompt, print exit code + screen tail
tvid rec send|key|screen|wait|pause|clear DIR  answer prompts, send keys, inspect, hold the screen
tvid rec stop DIR                              end the shell and save the cast
tvid render DIR                                cast → MP4 at real speed (agg + ffmpeg)
tvid readout DIR [--at SECONDS]                screen text over time, or the full screen at one moment
tvid voice DIR [--instruct … --seed N | --ref WAV --ref-text …] [--keep-backend]
tvid voice-stop DIR                            stop a backend tvid started and kept
tvid assemble DIR [--ff-speed 2 --ff-gap 10 --overrun spill|freeze] [--lufs -16 | --no-normalize]
tvid redact DIR [--urls] [--home] [--pattern REGEX]...   mask private values in the cast (off unless run)
tvid bundle DIR [--urls] [--home] [--pattern REGEX]...   write DIR/showcase/ for other tools
```

Run `tvid <command> --help` for every option.

## How it works

- **Exact timing without changing your program.** The recorded shell prints invisible markers into the recording for each command, caption and exit code. The readout replays the cast through a terminal emulator and stamps every screen line with the moment it first appeared. No guessing from video frames.
- **The video and the narration always describe the same run,** because both come from the same `recording.cast`.
- **Captions** are typed as `# comment` lines before each take, so the video explains itself even on mute.
- **One voice for every line.** Every line is cloned from a single reference clip, which is designed once from the description and seed, or supplied by you. Only lines whose text changed are regenerated.
- **The VoiceStudio backend is left as `tvid` found it.** A running backend is used and never stopped. If none is running, `tvid` starts one, generates the clips and stops it again (`--keep-backend` leaves it running).
- **The timeline is built from measured clip lengths,** not word-count estimates. A line that overruns either pushes the next line later (`spill`) or holds the frame (`freeze`). Stretches with no narration longer than the trigger play faster, with one second at real speed on each side.

## Hand-off to other tools

`tvid bundle DIR` packages one run for another tool to build from, such as an animated explainer made with [anidoodle](https://github.com/alexgreensh/anidoodle), slides or a teaser. It writes `DIR/showcase/`:

```
manifest.json     what the other tool reads (format "tvid-showcase/1")
recording.cast    the terminal recording, as timed data
recording.mp4     rendered from that cast
readout.txt       what appeared on screen, and when
clips/<id>.wav    one clip per line, all with the same gain, at -16 LUFS
```

Every time in the manifest is in recording seconds, the same clock as the cast and `recording.mp4`. Each line looks like this:

```json
{"id": "03", "text": "Export. For each object…", "on_screen": "Export starts",
 "anchor": 15.2, "slot_end": 35.0, "duration": 18.6, "speech_end": 33.8, "file": "clips/03.wav"}
```

- `anchor`: when the line's subject appears on screen.
- `slot_end`: the next line's anchor (or the end of the recording).
- `speech_end`: `anchor` + clip `duration`.

Another tool can either fit the picture to the voice (speed through waits so a result appears as it's spoken) or fit the voice to the picture, as `tvid assemble` does.

The bundle takes the same redaction flags as `tvid redact` and applies them to its own copies only. The cast, video, readout and line text are all masked, so a tool that embeds the cast as data doesn't carry the private values along.

### anidoodle (optional)

This marketplace also lists [anidoodle](https://github.com/alexgreensh/anidoodle) by Alex Greenshpun (Apache-2.0), pinned to v0.6.4, the release tested with this bundle format. It isn't installed with terminal-video. Install it only if you want animated explainers:

```
claude plugin install anidoodle@tmux-recording
```

- **Its first film is slower.** It downloads Node packages into the film's project and a headless Chromium (once per machine). anidoodle's skill runs those steps itself, and needs Node 20 or newer.
- **Install it from one marketplace only.** If you already have anidoodle from its own marketplace (`alexgreensh/anidoodle`), keep that one rather than installing it here too, or you'll get two copies of the same skill.

## Development

The installed plugin is a copy made at install time. To try edits from a clone of this repo without reinstalling, load it directly:

```
claude --plugin-dir <path-to-clone>
```

To release a change, bump `version` in `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` and push. Installed copies pick it up with the update commands above.

## Limitations

- The recorded shell is zsh, and the plugin has only been tested on macOS.
- Voice comes only from VoiceStudio, at `http://localhost:3900` by default (`--url`, `VOICESTUDIO_URL`).
- Clips are checked by pace (seconds per word), not by speech-to-text, so a mispronounced word isn't caught.
- Redaction matches what the terminal printed. A value drawn one character at a time with cursor moves in between can slip past a regex, so check the readout after redacting.
