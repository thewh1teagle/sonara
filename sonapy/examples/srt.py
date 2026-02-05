# /// script
# requires-python = ">=3.12"
# dependencies = ["sonapy"]
#
# [tool.uv.sources]
# sonapy = { path = "../" }
# ///
"""
SRT transcription example — request subtitle output and save it.

Setup:
  wget https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-tiny.bin
  wget https://github.com/ggml-org/whisper.cpp/raw/refs/heads/master/samples/jfk.wav

Run:
  uv run examples/srt.py ggml-tiny.bin jfk.wav
  uv run examples/srt.py ggml-tiny.bin jfk.wav my-output.srt
"""

import sys
from pathlib import Path

from sonapy import Sona


def main():
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <model.bin> <audio.wav> [output.srt]")
        sys.exit(1)

    model_path = sys.argv[1]
    audio_path = sys.argv[2]
    output_path = Path(sys.argv[3]) if len(sys.argv) > 3 else Path(audio_path).with_suffix(".srt")

    with Sona() as sona:
        sona.load_model(model_path)

        srt = sona.transcribe(audio_path, response_format="srt")
        output_path.write_text(srt, encoding="utf-8")

    print(f"Wrote SRT to {output_path}")
    print("\nPreview:")
    print("\n".join(srt.splitlines()[:8]))


if __name__ == "__main__":
    main()
