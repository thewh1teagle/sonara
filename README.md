# Sona

Like [Ollama](https://github.com/ollama/ollama) but for speech transcription. Powered by [whisper.cpp](https://github.com/ggml-org/whisper.cpp) with GPU acceleration (Metal on macOS, Vulkan on Linux/Windows).

## Features

- Cross-platform binaries: Windows (x86_64), Linux (x86_64/arm64), and macOS (Apple Silicon/Intel).
- GPU acceleration by platform: Vulkan on Windows/Linux and CoreML/Metal on macOS.
- OpenAI-compatible REST API server for transcription workflows.
- CLI for local transcription and serving.
- Bundled ffmpeg in release archives for convenience.
- Supports virtually any audio/video input format via automatic ffmpeg conversion.

## Usage

1. Download the binary for your platform from:
   - https://github.com/thewh1teagle/sona/releases
2. Download a Whisper model:
   - Model list: https://huggingface.co/ggerganov/whisper.cpp/tree/main
   - With Sona:

```bash
./sona pull https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.bin
```

3. Start the server:

```bash
./sona serve ./ggml-base.bin
```

Sona is OpenAI-compatible, so you can use the official OpenAI Python client against `base_url`.

```bash
wget https://github.com/ggml-org/whisper.cpp/raw/refs/heads/master/samples/jfk.wav -O sample.wav
```

```bash
pip install openai
```

```python
from openai import OpenAI

client = OpenAI(base_url="http://localhost:11531/v1", api_key="sona")
with open("sample.wav", "rb") as f:
    out = client.audio.transcriptions.create(model="ggml-base.bin", file=f)
print(out.text)
```
