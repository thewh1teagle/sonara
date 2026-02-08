# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "httpx==0.28.1",
#     "py7zr==0.22.0",
# ]
# ///

"""Package a Sona release archive with a bundled ffmpeg binary."""

import argparse
import io
import shutil
import tarfile
import tempfile
import zipfile
from pathlib import Path

import httpx
import py7zr


FFMPEG_URLS = {
    ("darwin", "amd64"): "https://www.osxexperts.net/ffmpeg80intel.zip",
    ("darwin", "arm64"): "https://www.osxexperts.net/ffmpeg80arm.zip",
    ("windows", "amd64"): "https://www.gyan.dev/ffmpeg/builds/ffmpeg-git-essentials.7z",
}


def download_bytes(url: str) -> bytes:
    print(f"downloading {url}")
    resp = httpx.get(url, follow_redirects=True, timeout=180)
    resp.raise_for_status()
    return resp.content


def resolve_ffmpeg_url(goos: str, goarch: str) -> str:
    key = (goos, goarch)
    if key not in FFMPEG_URLS:
        raise KeyError(f"unsupported target for ffmpeg URL: {goos}/{goarch}")
    return FFMPEG_URLS[key]


def copy_ffmpeg(stage_dir: Path, goos: str, goarch: str):
    url = resolve_ffmpeg_url(goos, goarch)
    data = download_bytes(url)

    if goos == "windows":
        ffmpeg_path = stage_dir / "ffmpeg.exe"
        with py7zr.SevenZipFile(io.BytesIO(data), "r") as archive:
            for fname, bio in archive.read().items():
                if Path(fname).name == "ffmpeg.exe":
                    ffmpeg_path.write_bytes(bio.read())
                    break
            else:
                raise FileNotFoundError("ffmpeg.exe not found in 7z archive")
    else:
        ffmpeg_path = stage_dir / "ffmpeg"
        with zipfile.ZipFile(io.BytesIO(data)) as zf:
            for name in zf.namelist():
                if Path(name).name == "ffmpeg":
                    ffmpeg_path.write_bytes(zf.read(name))
                    break
            else:
                raise FileNotFoundError("ffmpeg not found in zip archive")

    ffmpeg_path.chmod(0o755)


def package(binary_path: Path, out_path: Path, goos: str, goarch: str):
    if not binary_path.exists():
        raise FileNotFoundError(binary_path)

    with tempfile.TemporaryDirectory(prefix="sona-package-") as td:
        stage_dir = Path(td) / "bundle"
        stage_dir.mkdir(parents=True, exist_ok=True)

        binary_name = "sona.exe" if goos == "windows" else "sona"
        target_binary = stage_dir / binary_name
        shutil.copy2(binary_path, target_binary)
        target_binary.chmod(0o755)

        copy_ffmpeg(stage_dir, goos, goarch)

        out_path.parent.mkdir(parents=True, exist_ok=True)
        if goos == "windows":
            with zipfile.ZipFile(out_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
                for item in sorted(stage_dir.iterdir()):
                    zf.write(item, arcname=item.name)
        else:
            with tarfile.open(out_path, "w:gz") as tar:
                for item in sorted(stage_dir.iterdir()):
                    tar.add(item, arcname=item.name)

    print(f"packaged {out_path} ({out_path.stat().st_size // 1024} KB)")


def main():
    parser = argparse.ArgumentParser(description="Package Sona release archive")
    parser.add_argument("--binary", required=True, help="Built sona binary path")
    parser.add_argument("--goos", required=True, choices=["darwin", "windows"])
    parser.add_argument("--goarch", required=True, choices=["amd64", "arm64"])
    parser.add_argument(
        "--out", required=True, help="Output archive path (.tar.gz or .zip)"
    )
    args = parser.parse_args()

    package(Path(args.binary), Path(args.out), args.goos, args.goarch)


if __name__ == "__main__":
    main()
