from __future__ import annotations

import json
import os
import shutil
import signal
import subprocess
import sys
from pathlib import Path


class SonaError(Exception):
    pass


def _find_binary() -> str | None:
    """Look for ``sona`` in cwd, next to the script, in venv bin, then PATH."""
    name = "sona.exe" if sys.platform == "win32" else "sona"

    candidates = [
        # 1. Current working directory
        Path.cwd() / name,
        # 2. Next to the running script
        *(
            [Path(m.__file__).resolve().parent / name]
            if (m := sys.modules.get("__main__")) and getattr(m, "__file__", None)
            else []
        ),
        # 3. Next to the Python interpreter (venv bin/)
        Path(sys.executable).resolve().parent / name,
    ]

    for c in candidates:
        if c.is_file() and os.access(c, os.X_OK):
            return str(c)

    # 4. PATH
    return shutil.which("sona")


class Runner:
    """Manages the ``sona`` child process lifecycle."""

    def __init__(self, port: int = 0) -> None:
        binary = _find_binary()
        if binary is None:
            raise SonaError(
                "'sona' binary not found. Place it next to your script, "
                "in your virtualenv bin/, or on PATH."
            )

        self._process = subprocess.Popen(
            [binary, "serve", "--port", str(port)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        try:
            line = self._process.stdout.readline()  # type: ignore[union-attr]
            if not line:
                stderr = self._process.stderr.read().decode() if self._process.stderr else ""  # type: ignore[union-attr]
                raise SonaError(f"sona exited before ready signal: {stderr}")
            info = json.loads(line)
            if info.get("status") != "ready":
                raise SonaError(f"unexpected ready signal: {info}")
            self.port: int = info["port"]
        except Exception:
            self._process.kill()
            raise

    @property
    def alive(self) -> bool:
        return self._process.poll() is None

    def stop(self) -> None:
        """Send SIGTERM and wait for clean shutdown."""
        if self._process.poll() is not None:
            return
        if sys.platform == "win32":
            self._process.terminate()
        else:
            self._process.send_signal(signal.SIGTERM)
        try:
            self._process.wait(timeout=30)
        except subprocess.TimeoutExpired:
            self._process.kill()
