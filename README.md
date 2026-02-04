# 🎙️ Sona

Like **Ollama**, but for **speech transcription**.  
Built on top of **whisper.cpp** with fast **GPU acceleration** (Metal on macOS, Vulkan on Linux and Windows).

---

## ✨ Features

- **Cross-platform binaries**  
  Windows (x86_64), Linux (x86_64 / arm64), macOS (Apple Silicon and Intel)

- **GPU acceleration out of the box**  
  Vulkan on Windows/Linux, CoreML/Metal on macOS

- **OpenAI-compatible REST API**  
  Drop-in replacement for existing transcription workflows

- **CLI + Server mode**  
  Transcribe locally or run a long-lived service

- **Bundled ffmpeg**  
  No extra installs, works with almost any audio or video format

- **Automatic format handling**  
  Audio is converted transparently via ffmpeg

---

## Quick Start

### 1. Download Sona
Grab the binary for your platform:  
https://github.com/thewh1teagle/sona/releases

---

### 2. Download a Whisper model

Model list:  
https://huggingface.co/ggerganov/whisper.cpp/tree/main

Using Sona:
```shell
./sona pull https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.bin
```

---

### 3. Start the server
```shell
./sona serve ./ggml-base.bin
```

---

## 🔌 OpenAI-Compatible API

Sona speaks the OpenAI API, so existing clients just work.

```shell
wget https://github.com/ggml-org/whisper.cpp/raw/refs/heads/master/samples/jfk.wav -O sample.wav
pip install openai
```

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:11531/v1",
    api_key="sona",
)

with open("sample.wav", "rb") as f:
    result = client.audio.transcriptions.create(
        model="ggml-base.bin",
        file=f,
    )

print(result.text)
```

📚 API Docs

Interactive docs (Swagger UI):
http://localhost:11531/docs

OpenAPI spec:
http://localhost:11531/openapi.json

