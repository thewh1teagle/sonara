# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "httpx==0.28.1",
# ]
# ///

"""Fetch whisper.h and ggml headers from GitHub into third_party/whisper.cpp/include/. Each file is stamped with the fetch date and source commit."""

import httpx, datetime
from pathlib import Path

WHISPER_REPO = "ggml-org/whisper.cpp"
GGML_REPO = "ggml-org/llama.cpp"  # ggml headers live here
WHISPER_COMMIT = "aa1bc0d1a6dfd70dbb9f60c11df12441e03a9075"

HEADERS = [
    (WHISPER_REPO, WHISPER_COMMIT, "include/whisper.h"),
    (GGML_REPO, WHISPER_COMMIT, "ggml/include/ggml.h"),
    (GGML_REPO, WHISPER_COMMIT, "ggml/include/ggml-cpu.h"),
    (GGML_REPO, WHISPER_COMMIT, "ggml/include/ggml-alloc.h"),
    (GGML_REPO, WHISPER_COMMIT, "ggml/include/ggml-backend.h"),
]

out_dir = Path(__file__).resolve().parent.parent / "third_party/whisper.cpp/include"
out_dir.mkdir(parents=True, exist_ok=True)
now = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%d %H:%M:%S UTC")

for repo, commit, path in HEADERS:
    name = Path(path).name
    content = httpx.get(f"https://raw.githubusercontent.com/{repo}/{commit}/{path}").text
    (out_dir / name).write_text(
        f"// Fetched: {now}\n"
        f"// Source: https://github.com/{repo}/blob/{commit}/{path}\n"
        f"// Commit: {commit}\n\n"
        + content
    )
    print(f"wrote {name} (commit {commit})")
