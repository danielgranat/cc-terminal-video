#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["kokoro-onnx>=0.4", "soundfile>=0.12"]
# ///
"""Speak lines with Kokoro, for `tvid voice --engine kokoro`.

Reads a JSON job on stdin: {"voice", "speed", "lang", "items": [{"text", "out"}]}, writes each item as
16-bit mono WAV, and prints one JSON result line per item. `--list` prints the voice names instead.
The model files (~350 MB) download once into the cache folder and are checked against pinned hashes.
"""

import hashlib
import json
import os
import sys
import time
import urllib.request
from pathlib import Path

RELEASE = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0"
FILES = {
    "kokoro-v1.0.onnx": "7d5df8ecf7d4b1878015a32686053fd0eebe2bc377234608764cc0ef3636a6c5",
    "voices-v1.0.bin": "bca610b8308e8d99f32e6fe4197e7ec01679264efed0cac9140fe9c29f1fbf7d",
}


def cache_dir() -> Path:
    base = os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache"
    return Path(os.environ.get("TVID_KOKORO_DIR") or Path(base) / "tvid" / "kokoro")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def model_files() -> tuple[Path, Path]:
    d = cache_dir()
    d.mkdir(parents=True, exist_ok=True)
    for name, digest in FILES.items():
        path = d / name
        if path.exists() and path.stat().st_size > 0:
            continue
        print(f"downloading Kokoro {name} to {d} (once)", file=sys.stderr)
        part = path.with_suffix(path.suffix + ".part")
        urllib.request.urlretrieve(f"{RELEASE}/{name}", part)
        if sha256(part) != digest:
            part.unlink()
            sys.exit(f"kokoro: {name} failed its checksum; download it again")
        part.rename(path)
    return d / "kokoro-v1.0.onnx", d / "voices-v1.0.bin"


def main() -> None:
    from kokoro_onnx import Kokoro
    import soundfile as sf

    model, voices = model_files()
    k = Kokoro(str(model), str(voices))
    if "--list" in sys.argv:
        print("\n".join(sorted(k.get_voices())))
        return
    job = json.load(sys.stdin)
    if job["voice"] not in k.get_voices():
        sys.exit(f"kokoro: no voice {job['voice']!r}; list them with: tvid voice --list-voices")
    for item in job["items"]:
        t0 = time.time()
        audio, rate = k.create(item["text"], voice=job["voice"], speed=job["speed"], lang=job["lang"])
        sf.write(item["out"], audio, rate, subtype="PCM_16")
        print(json.dumps({"out": item["out"], "seconds": round(time.time() - t0, 1)}), flush=True)


if __name__ == "__main__":
    main()
