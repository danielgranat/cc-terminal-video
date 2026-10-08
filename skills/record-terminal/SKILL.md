---
name: record-terminal
description: Record a terminal run in tmux with asciinema and render it to MP4 at real speed.
disable-model-invocation: true
---

# Record a terminal run

You run the commands; `tvid` records them. `tvid` means `<this skill's base directory>/../../scripts/tvid`.

`tvid rec start` opens a zsh inside a detached tmux session, recorded by asciinema to `DIR/recording.cast`. The shell loads the user's own startup files (PATH, version managers) and then a plain `$` prompt. Its hooks mark every command, caption and exit code in the cast with timestamps, and tell `tvid` the moment the prompt returns. So every command you want on camera goes through `tvid rec run`. Commands you want off camera go through your normal shell tool.

The cast is the source of truth for the later stages: the video is rendered from it, and the readout the narration is written from comes from it. A video and a narration source from two different runs can't be paired by mistake.

## Steps

1. **Rehearse the story.** Decide what each take must show, as a fact you can check on screen ("the export pulls 461 rows from scratch", "the second run exports 0 rows"). Find out what state makes that true (a reset, an empty table, a fresh checkout), and how long each take runs. A take that runs against the wrong state records a demo of nothing. Done when you can name, for every take, its command, its precondition and the on-screen fact that proves it worked.
2. **Prepare off camera.** Run setup, resets and slow warm-ups through your normal shell tool, outside the recording. Then check each precondition with a read-only command. Done when every precondition from step 1 checks true.
3. **Start recording.** `tvid rec start DIR --cwd <project dir>`. The default terminal is 140×45. Make it wider (`--cols`) if the rehearsal showed tables or bars wrapping. Pass `--no-user-rc` if the user's startup files print noise. Tell the user they can watch live with the `tmux attach -r -t <name>` line it prints.
4. **Film each take.** `tvid rec run DIR "<command>" --caption "<what this take shows>"`.
   - The caption is typed first as a `# comment` line. Write it for the viewer: "Run 2: same sync again, nothing changed upstream".
   - `run` types the command at a human pace and returns when the prompt is back, printing the exit code and the end of the screen.
   - **Long take**: `run` waits up to `--timeout` seconds (default 540, inside a 10-minute tool limit). For longer takes, use `--no-wait`, then repeat `tvid rec wait DIR --timeout 540` until it reports the exit code.
   - **The program asks for input**: use `--no-wait`, then `tvid rec screen DIR` to read the question, `tvid rec send DIR "<answer>" --enter`, then `tvid rec wait DIR`. `tvid rec key DIR C-c` sends control keys.
   - **Between takes**: `tvid rec pause 3` holds the result on screen so the viewer can read it. `tvid rec clear DIR` starts the next take on a clean screen.

   Done with a take when its exit code and screen tail show the on-screen fact from step 1. If they don't, the take failed: stop, fix the state off camera, and record again from step 3 (a new `rec start` overwrites the cast).
5. **Stop and render.** `tvid rec stop DIR`, then `tvid render DIR` (options: `--font-size`, `--theme`, `--fps`). Rendering keeps real time, so cast seconds and video seconds match.
6. **Verify the video.** Run `tvid readout DIR`, then read `DIR/readout.txt`. Extract one frame per take with `ffmpeg -ss <t> -i DIR/recording.mp4 -frames:v 1 <png>` and look at it. Done when the readout shows every take's on-screen fact from step 1, and the frames show readable text with nothing wrapped or cut off.
7. **Check for private values.** Look through the readout for anything the viewer shouldn't see: instance URLs, hostnames, account or record IDs, tokens, your home path. If you find any, list them for the user and ask whether to redact. Redaction is off unless they say yes. To redact, run `tvid redact DIR` with `--urls`, `--home` and/or `--pattern '<regex>'` (repeatable), then `tvid render DIR` and `tvid readout DIR` again, so the video and the readout both show the mask. The unredacted cast stays in `DIR/.tvid/`. Done when the user has decided, and any redaction they chose shows in a fresh readout.

## Gotchas

- Everything typed or printed is in the video. Keep secrets, tokens and private paths off screen: set them in the environment off camera before `rec start`, or pass them through files.
- The recorded shell starts in `--cwd`, not your tool's working directory. Per-project version managers (`fnm`, `nvm`, `asdf`) only switch if the user's startup files hook `cd`. If a take needs a specific runtime, put it in the command (`fnm exec --using=22 npm run …`).
- Keep each take under a few minutes where you can. Assembly fast-forwards silent stretches, but a 10-minute wait still costs the viewer time.
